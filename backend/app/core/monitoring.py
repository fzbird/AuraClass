from typing import Callable, Dict, Any
import time
from datetime import datetime
import psutil
from fastapi import Request, Response
from prometheus_client import (
    Counter, Histogram, Gauge,
    CollectorRegistry, generate_latest
)
from app.core.logging import get_logger

# 创建指标注册表
REGISTRY = CollectorRegistry()

# 定义监控指标
HTTP_REQUEST_COUNTER = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status'],
    registry=REGISTRY
)

HTTP_REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    registry=REGISTRY
)

ACTIVE_REQUESTS = Gauge(
    'active_requests',
    'Number of active requests',
    registry=REGISTRY
)

SYSTEM_MEMORY_USAGE = Gauge(
    'system_memory_usage_bytes',
    'System memory usage in bytes',
    registry=REGISTRY
)

SYSTEM_CPU_USAGE = Gauge(
    'system_cpu_usage_percent',
    'System CPU usage percentage',
    registry=REGISTRY
)

DB_CONNECTION_POOL_SIZE = Gauge(
    'db_connection_pool_size',
    'Database connection pool size',
    registry=REGISTRY
)

class MonitoringMiddleware:
    def __init__(self, app):
        self.app = app
        self.logger = get_logger(__name__)

    async def __call__(
        self,
        scope: Dict[str, Any], 
        receive: Callable, 
        send: Callable
    ) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope)
        # 记录请求开始时间
        start_time = time.time()
        
        # 增加活跃请求计数
        ACTIVE_REQUESTS.inc()
        
        # 创建发送响应的函数
        response_started = False
        response_body = []
        
        async def send_wrapper(message: Dict[str, Any]):
            nonlocal response_started, response_body
            
            if message["type"] == "http.response.start":
                response_started = True
                # 记录响应状态码
                status_code = message["status"]
                
                # 更新监控指标
                HTTP_REQUEST_COUNTER.labels(
                    method=request.method,
                    endpoint=request.url.path,
                    status=status_code
                ).inc()
                
            elif message["type"] == "http.response.body":
                if message.get("more_body", False) == False:
                    # 最后一个响应体分块
                    duration = time.time() - start_time
                    
                    HTTP_REQUEST_DURATION.labels(
                        method=request.method,
                        endpoint=request.url.path
                    ).observe(duration)
                    
                    # 记录详细日志
                    self.logger.info(
                        "Request processed",
                        extra={
                            'method': request.method,
                            'path': request.url.path,
                            'status_code': message.get("status", 200),
                            'duration': duration,
                            'client_ip': request.client.host if request.client else None,
                            'user_agent': request.headers.get('user-agent')
                        }
                    )
                    
                    # 减少活跃请求计数
                    ACTIVE_REQUESTS.dec()
            
            # 转发消息
            await send(message)
        
        try:
            # 执行ASGI应用
            await self.app(scope, receive, send_wrapper)
            
        except Exception as e:
            # 记录错误日志
            self.logger.error(
                "Request failed",
                exc_info=True,
                extra={
                    'method': request.method,
                    'path': request.url.path,
                    'client_ip': request.client.host if request.client else None,
                    'error': str(e)
                }
            )
            # 确保减少活跃请求计数
            if not response_started:
                ACTIVE_REQUESTS.dec()
            raise

def update_system_metrics():
    """更新系统指标"""
    logger = get_logger(__name__)
    try:
        # 更新内存使用情况
        memory = psutil.virtual_memory()
        SYSTEM_MEMORY_USAGE.set(memory.used)
        
        # 更新CPU使用情况
        cpu_percent = psutil.cpu_percent(interval=1)
        SYSTEM_CPU_USAGE.set(cpu_percent)
        
    except Exception as e:
        logger.error(f"Error updating system metrics: {str(e)}")
