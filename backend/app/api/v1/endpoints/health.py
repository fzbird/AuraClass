from typing import Any, Dict, List
from datetime import datetime, timezone
import psutil
from fastapi import APIRouter, Depends, Response, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from prometheus_client import generate_latest
import time
from collections import defaultdict

from app.api.deps import get_db
from app.core.monitoring import REGISTRY
from app.db.session import check_db_connection
from app.core.config import settings
from app.utils.performance import (
    minute_metrics, 
    hour_metrics, 
    day_metrics,
    get_slow_endpoints,
    get_high_traffic_endpoints
)
from app.schemas.health import (
    HealthCheckResponse,
    SystemInfoResponse,
    DBHealthResponse,
    APIPerformanceResponse,
    WindowPerformanceResponse,
    SlowEndpointsResponse,
    HighTrafficResponse,
    ServiceHealth,
    MemoryUsage,
    CPUUsage,
    SystemHealth,
    DiskUsage,
    DBConfig,
    EndpointPerformance
)

router = APIRouter()

# Global dict to store API performance metrics
api_metrics = defaultdict(lambda: {"count": 0, "total_time": 0, "min_time": float("inf"), "max_time": 0})

# 应用信息端点
@router.get("/api/info")
async def api_info():
    return {
        "app_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.APP_ENV
    }

@router.get("/health", response_model=HealthCheckResponse)
async def health_check(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    系统健康检查
    
    返回系统整体健康状态，包括数据库连接状态和系统资源使用情况
    """
    # 检查数据库连接
    db_status = "healthy" if await check_db_connection(db) else "unhealthy"
    
    # 获取系统信息
    memory = psutil.virtual_memory()
    cpu_percent = psutil.cpu_percent(interval=1)
    
    overall_status = "ok" if db_status == "healthy" else "degraded"
    
    return {
        "status": overall_status,
        "timestamp": datetime.now(timezone.utc),
        "services": {
            "database": {
                "status": db_status
            }
        },
        "system": {
            "memory_usage": {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent
            },
            "cpu_usage": {
                "percent": cpu_percent
            }
        }
    }

@router.get("/metrics")
async def metrics() -> Any:
    """
    Prometheus 指标导出
    
    返回系统监控指标，可被Prometheus抓取
    """
    return Response(
        content=generate_latest(REGISTRY),
        media_type="text/plain"
    )

@router.get("/system-info", response_model=SystemInfoResponse)
async def system_info():
    """
    获取系统资源信息
    
    返回系统内存、CPU和磁盘使用情况的详细信息
    """
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "memory": {
            "total": memory.total,
            "available": memory.available,
            "percent": memory.percent
        },
        "cpu": {
            "percent": psutil.cpu_percent(interval=1),
            "count": psutil.cpu_count()
        },
        "disk": {
            "total": disk.total,
            "free": disk.free,
            "used_percent": disk.percent
        },
        "timestamp": datetime.now(timezone.utc),
    }

@router.get("/db-health", response_model=DBHealthResponse)
async def db_health_check(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    数据库健康专项检查
    
    检查数据库连接状态并返回数据库配置信息
    """
    start_time = time.time()
    is_healthy = await check_db_connection(db)
    check_time = time.time() - start_time
    
    # 获取更多数据库信息
    db_info = {
        "url": settings.DATABASE_URL.replace(settings.DATABASE_URL.split("@")[0], "***"),
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "echo": settings.DB_ECHO
    }
    
    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "check_time_ms": round(check_time * 1000, 2),
        "timestamp": datetime.now(timezone.utc),
        "db_config": db_info
    }

@router.get("/api-performance", response_model=APIPerformanceResponse)
async def api_performance() -> Dict[str, Any]:
    """
    获取API性能指标
    
    返回各API端点的响应时间统计，包括平均响应时间、
    最小响应时间、最大响应时间和请求计数
    """
    performance_data = {}
    
    for endpoint, metrics in api_metrics.items():
        if metrics["count"] > 0:
            avg_time = metrics["total_time"] / metrics["count"]
            performance_data[endpoint] = {
                "avg_response_time_ms": round(avg_time * 1000, 2),
                "min_response_time_ms": round(metrics["min_time"] * 1000, 2) if metrics["min_time"] != float("inf") else 0,
                "max_response_time_ms": round(metrics["max_time"] * 1000, 2),
                "request_count": metrics["count"]
            }
    
    return {
        "api_performance": performance_data,
        "timestamp": datetime.now(timezone.utc)
    }

@router.get("/window-performance/{window}", response_model=WindowPerformanceResponse)
async def api_window_performance(
    window: str = Path(..., description="时间窗口", regex="^(minute|hour|day)$"),
    endpoint: str = Query(None, description="可选的特定API端点")
) -> Dict[str, Any]:
    """
    获取指定时间窗口内的API性能指标
    
    根据指定的时间窗口（分钟、小时、天）返回API性能指标数据
    
    - **window**: 时间窗口，可选值: minute(1分钟), hour(1小时), day(24小时)
    - **endpoint**: 可选，特定的API端点，如不指定则返回所有端点数据
    """
    if window == "minute":
        metrics = minute_metrics.get_metrics(endpoint)
    elif window == "hour":
        metrics = hour_metrics.get_metrics(endpoint)
    elif window == "day":
        metrics = day_metrics.get_metrics(endpoint)
    else:
        return {"error": "Invalid window parameter. Use 'minute', 'hour', or 'day'"}
    
    return {
        "window": window,
        "api_performance": metrics,
        "timestamp": datetime.now(timezone.utc)
    }

@router.get("/slow-endpoints", response_model=SlowEndpointsResponse)
async def slow_endpoints(
    window: str = Query("hour", description="时间窗口", regex="^(minute|hour|day)$"),
    limit: int = Query(5, description="返回结果数量", ge=1, le=20)
) -> Dict[str, Any]:
    """
    获取最慢的API端点
    
    返回指定时间窗口内响应时间最长的API端点列表
    
    - **window**: 时间窗口，可选值: minute(1分钟), hour(1小时), day(24小时)
    - **limit**: 返回的结果数量，1-20之间
    """
    result = get_slow_endpoints(window, limit)
    
    return {
        "window": window,
        "slow_endpoints": result,
        "timestamp": datetime.now(timezone.utc)
    }

@router.get("/high-traffic", response_model=HighTrafficResponse)
async def high_traffic_endpoints(
    window: str = Query("hour", description="时间窗口", regex="^(minute|hour|day)$"),
    limit: int = Query(5, description="返回结果数量", ge=1, le=20)
) -> Dict[str, Any]:
    """
    获取请求量最高的API端点
    
    返回指定时间窗口内请求量最高的API端点列表
    
    - **window**: 时间窗口，可选值: minute(1分钟), hour(1小时), day(24小时)
    - **limit**: 返回的结果数量，1-20之间
    """
    result = get_high_traffic_endpoints(window, limit)
    
    return {
        "window": window,
        "high_traffic_endpoints": result,
        "timestamp": datetime.now(timezone.utc)
    }

def record_api_metrics(endpoint: str, response_time: float) -> None:
    """
    记录API端点的性能指标
    
    Args:
        endpoint: API端点路径
        response_time: 响应时间（秒）
    """
    api_metrics[endpoint]["count"] += 1
    api_metrics[endpoint]["total_time"] += response_time
    api_metrics[endpoint]["min_time"] = min(api_metrics[endpoint]["min_time"], response_time)
    api_metrics[endpoint]["max_time"] = max(api_metrics[endpoint]["max_time"], response_time)
