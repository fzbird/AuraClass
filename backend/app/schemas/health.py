from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class ServiceHealth(BaseModel):
    status: str = Field(..., description="服务健康状态，可能值：healthy, unhealthy, degraded")


class MemoryUsage(BaseModel):
    total: int = Field(..., description="总内存（字节）")
    available: int = Field(..., description="可用内存（字节）")
    percent: float = Field(..., description="内存使用百分比")


class CPUUsage(BaseModel):
    percent: float = Field(..., description="CPU使用百分比")


class SystemHealth(BaseModel):
    memory_usage: MemoryUsage
    cpu_usage: CPUUsage


class HealthCheckResponse(BaseModel):
    status: str = Field(..., description="整体健康状态，可能值：ok, degraded, error")
    timestamp: datetime = Field(..., description="检查时间")
    services: Dict[str, ServiceHealth] = Field(..., description="各服务健康状态")
    system: SystemHealth = Field(..., description="系统资源使用情况")


class DiskUsage(BaseModel):
    total: int = Field(..., description="总磁盘空间（字节）")
    free: int = Field(..., description="可用磁盘空间（字节）")
    used_percent: float = Field(..., description="磁盘使用百分比")


class SystemInfoResponse(BaseModel):
    memory: MemoryUsage
    cpu: Dict[str, Any] = Field(..., description="CPU使用情况")
    disk: DiskUsage
    timestamp: datetime


class DBConfig(BaseModel):
    url: str = Field(..., description="数据库连接URL（敏感信息已隐藏）")
    pool_size: int = Field(..., description="连接池大小")
    max_overflow: int = Field(..., description="最大溢出连接数")
    echo: bool = Field(..., description="是否启用SQL回显")


class DBHealthResponse(BaseModel):
    status: str = Field(..., description="数据库健康状态")
    check_time_ms: float = Field(..., description="检查耗时（毫秒）")
    timestamp: datetime
    db_config: DBConfig


class EndpointPerformance(BaseModel):
    avg_response_time_ms: float = Field(..., description="平均响应时间（毫秒）")
    min_response_time_ms: float = Field(..., description="最小响应时间（毫秒）")
    max_response_time_ms: float = Field(..., description="最大响应时间（毫秒）")
    request_count: int = Field(..., description="请求数量")


class APIPerformanceResponse(BaseModel):
    api_performance: Dict[str, EndpointPerformance] = Field(..., description="各端点性能指标")
    timestamp: datetime


class TimeWindowPerformance(BaseModel):
    """时间窗口内端点性能指标"""
    avg_response_time_ms: float = Field(..., description="平均响应时间（毫秒）")
    min_response_time_ms: float = Field(..., description="最小响应时间（毫秒）")
    max_response_time_ms: float = Field(..., description="最大响应时间（毫秒）")
    p90_response_time_ms: float = Field(..., description="90%响应时间（毫秒）")
    p95_response_time_ms: float = Field(..., description="95%响应时间（毫秒）")
    p99_response_time_ms: float = Field(..., description="99%响应时间（毫秒）")
    request_count: int = Field(..., description="请求数量")
    requests_per_second: float = Field(..., description="每秒请求数")


class WindowPerformanceResponse(BaseModel):
    """时间窗口性能指标响应"""
    window: str = Field(..., description="时间窗口，可能值：minute, hour, day")
    api_performance: Dict[str, TimeWindowPerformance] = Field(..., description="时间窗口内各端点性能指标")
    timestamp: datetime


class EndpointDetail(BaseModel):
    """端点详细信息"""
    endpoint: str = Field(..., description="API端点")
    avg_response_time_ms: float = Field(..., description="平均响应时间（毫秒）")
    min_response_time_ms: float = Field(..., description="最小响应时间（毫秒）")
    max_response_time_ms: float = Field(..., description="最大响应时间（毫秒）")
    p90_response_time_ms: float = Field(..., description="90%响应时间（毫秒）")
    p95_response_time_ms: float = Field(..., description="95%响应时间（毫秒）")
    p99_response_time_ms: float = Field(..., description="99%响应时间（毫秒）")
    request_count: int = Field(..., description="请求数量")
    requests_per_second: float = Field(..., description="每秒请求数")


class SlowEndpointsResponse(BaseModel):
    """最慢端点列表响应"""
    window: str = Field(..., description="时间窗口，可能值：minute, hour, day")
    slow_endpoints: List[EndpointDetail] = Field(..., description="最慢的API端点列表")
    timestamp: datetime


class HighTrafficResponse(BaseModel):
    """高流量端点列表响应"""
    window: str = Field(..., description="时间窗口，可能值：minute, hour, day")
    high_traffic_endpoints: List[EndpointDetail] = Field(..., description="高流量API端点列表")
    timestamp: datetime 