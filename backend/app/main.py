from contextlib import asynccontextmanager
import asyncio
import json
import time
from decimal import Decimal
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.api.v1.router import api_router
from app.api.v1.endpoints.health import record_api_metrics
from app.utils.performance import record_api_performance
from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.monitoring import (
    MonitoringMiddleware,
    update_system_metrics
)

# 设置日志
setup_logging(
    log_level=settings.LOG_LEVEL,
    log_file=settings.LOG_FILE,
    log_format="simple"  # 使用简化的日志格式
)

logger = get_logger(__name__)

# 引入监控系统补丁，减少过多的请求日志
try:
    import app.core.monitoring_patch
    logger.info("监控系统补丁已加载，将减少不必要的日志记录")
except ImportError:
    logger.warning("无法加载监控系统补丁，请检查文件是否存在")

# 创建系统指标更新任务
async def metrics_updater():
    while True:
        update_system_metrics()
        await asyncio.sleep(settings.METRICS_UPDATE_INTERVAL)

# 应用启动和关闭事件
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    logger.info("Starting application")
    metrics_task = asyncio.create_task(metrics_updater())
    
    # 初始化AI助手服务
    from app.services.ai_service import ai_assistant
    await ai_assistant.initialize()
    logger.info("AI Assistant service initialized")
    
    # 确保上传目录存在
    uploads_dir = Path(settings.UPLOADS_DIR)
    uploads_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Ensured uploads directory exists: {uploads_dir}")
    
    yield
    
    # 关闭时执行
    logger.info("Shutting down application")
    metrics_task.cancel()
    try:
        await metrics_task
    except asyncio.CancelledError:
        pass

# 创建FastAPI应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    lifespan=lifespan,
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
)

# API性能监控中间件
class APIPerformanceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 排除掉健康检查和性能检查端点，避免递归统计
        path = request.url.path
        # 健康检查相关的端点列表
        health_endpoints = [
            "/health", 
            "/api/v1/health/api-performance", 
            "/api/v1/health/metrics",
            "/api/v1/health/window-performance",
            "/api/v1/health/slow-endpoints",
            "/api/v1/health/high-traffic",
            "/api/v1/health/system-info",
            "/api/v1/health/db-health"
        ]
        
        # 检查路径是否在排除列表中，或者以某个前缀开始
        if path in health_endpoints or any(path.startswith(f"{prefix}/") for prefix in health_endpoints):
            return await call_next(request)
            
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # 记录API性能指标
        method = request.method
        endpoint = f"{method} {path}"
        
        # 记录到全局累计指标
        record_api_metrics(endpoint, process_time)
        
        # 记录到时间窗口指标
        record_api_performance(endpoint, process_time)
        
        # 记录慢请求日志
        if process_time > settings.SLOW_API_THRESHOLD:
            logger.warning(
                f"Slow API request: {endpoint} took {process_time:.4f}s "
                f"(threshold: {settings.SLOW_API_THRESHOLD}s)"
            )
        
        return response

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加API性能监控中间件
app.add_middleware(APIPerformanceMiddleware)

# 添加监控中间件
app.add_middleware(MonitoringMiddleware)

class CustomJSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        def custom_encoder(obj):
            if isinstance(obj, Decimal):
                return float(obj)
            return obj

        return json.dumps(
            jsonable_encoder(content),
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            default=custom_encoder,
        ).encode("utf-8")

# 统一异常处理
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": str(exc.status_code),
                "message": exc.detail
            }
        },
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return CustomJSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "数据验证失败",
                "details": exc.errors()
            }
        },
    )

# 设置默认响应类
app.router.default_response_class = CustomJSONResponse

# 注册API路由
app.include_router(api_router, prefix=settings.API_V1_STR)

# 挂载静态文件目录
uploads_path = Path(settings.UPLOADS_DIR)
if not uploads_path.exists():
    uploads_path.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")
logger.info(f"Mounted static files directory: {uploads_path} at /uploads")

# 注册WebSocket路由
from app.websockets.notifications import router as notification_ws_router
from app.websockets.ai_assistant import router as ai_assistant_ws_router

# WebSocket路由直接注册到主应用，不添加前缀
logger.info("Registering WebSocket routes")
app.include_router(notification_ws_router)
app.include_router(ai_assistant_ws_router)
logger.info(f"Registered WebSocket routes: {[route.path for route in app.routes if hasattr(route, 'endpoint') and 'websocket' in str(route.endpoint)]}")

# 健康检查端点
@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy"}

# 应用信息端点
@app.get("/api/v1/api/info")
async def api_info():
    return {
        "app_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.APP_ENV
    }

@app.get("/api/v1/")
async def root():
    return {
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "running"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8200, reload=settings.DEBUG)
