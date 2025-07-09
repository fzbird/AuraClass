from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import time
import heapq
from collections import defaultdict, deque
from threading import Lock


class TimeWindowMetrics:
    """
    基于时间窗口的API性能指标收集器
    用于计算指定时间窗口内的API性能指标
    """
    
    def __init__(self, window_size_seconds: int = 3600):
        """
        初始化时间窗口指标收集器
        
        Args:
            window_size_seconds: 时间窗口大小（秒）
        """
        self.window_size = window_size_seconds
        self.metrics = defaultdict(lambda: {
            "response_times": deque(),
            "timestamps": deque(),
            "min_time": float("inf"),
            "max_time": 0,
            "total_time": 0,
            "count": 0
        })
        self.lock = Lock()
        
    def record(self, endpoint: str, response_time: float) -> None:
        """
        记录API端点的响应时间
        
        Args:
            endpoint: API端点名称
            response_time: 响应时间（秒）
        """
        timestamp = time.time()
        
        with self.lock:
            # 更新指标
            metrics = self.metrics[endpoint]
            
            # 添加新数据点
            metrics["response_times"].append(response_time)
            metrics["timestamps"].append(timestamp)
            metrics["total_time"] += response_time
            metrics["count"] += 1
            metrics["min_time"] = min(metrics["min_time"], response_time)
            metrics["max_time"] = max(metrics["max_time"], response_time)
            
            # 清理过期数据点
            self._clean_old_data(endpoint, timestamp)
    
    def _clean_old_data(self, endpoint: str, current_time: float) -> None:
        """
        清理过期的数据点
        
        Args:
            endpoint: API端点名称
            current_time: 当前时间戳
        """
        metrics = self.metrics[endpoint]
        cutoff_time = current_time - self.window_size
        
        # 重新计算指标，去除过期数据点
        while metrics["timestamps"] and metrics["timestamps"][0] < cutoff_time:
            old_timestamp = metrics["timestamps"].popleft()
            old_response_time = metrics["response_times"].popleft()
            
            # 更新计数和总时间
            metrics["total_time"] -= old_response_time
            metrics["count"] -= 1
            
        # 如果需要重新计算最小值和最大值
        if metrics["response_times"]:
            metrics["min_time"] = min(metrics["response_times"])
            metrics["max_time"] = max(metrics["response_times"])
        else:
            # 没有数据点了，重置指标
            metrics["min_time"] = float("inf")
            metrics["max_time"] = 0
            metrics["total_time"] = 0
            metrics["count"] = 0
    
    def get_metrics(self, endpoint: Optional[str] = None) -> Dict[str, Any]:
        """
        获取指定端点或所有端点的性能指标
        
        Args:
            endpoint: API端点名称，若为None则返回所有端点的指标
            
        Returns:
            性能指标字典
        """
        with self.lock:
            current_time = time.time()
            result = {}
            
            if endpoint:
                if endpoint in self.metrics:
                    self._clean_old_data(endpoint, current_time)
                    metrics = self.metrics[endpoint]
                    if metrics["count"] > 0:
                        result[endpoint] = self._calculate_metrics(metrics)
            else:
                for ep, metrics in self.metrics.items():
                    self._clean_old_data(ep, current_time)
                    if metrics["count"] > 0:
                        result[ep] = self._calculate_metrics(metrics)
                    
            return result
    
    def _calculate_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算性能指标
        
        Args:
            metrics: 原始指标数据
            
        Returns:
            计算后的性能指标
        """
        count = metrics["count"]
        if count == 0:
            return {
                "avg_response_time_ms": 0,
                "min_response_time_ms": 0,
                "max_response_time_ms": 0,
                "p90_response_time_ms": 0,
                "p95_response_time_ms": 0,
                "p99_response_time_ms": 0,
                "request_count": 0,
                "requests_per_second": 0
            }
        
        avg_time = metrics["total_time"] / count
        min_time = metrics["min_time"]
        max_time = metrics["max_time"]
        
        # 计算百分位数
        if len(metrics["response_times"]) > 1:
            response_times_sorted = sorted(metrics["response_times"])
            p90 = response_times_sorted[int(count * 0.9)]
            p95 = response_times_sorted[int(count * 0.95)]
            p99 = response_times_sorted[int(count * 0.99)]
        else:
            p90 = p95 = p99 = avg_time
        
        # 计算RPS
        time_span = metrics["timestamps"][-1] - metrics["timestamps"][0]
        requests_per_second = count / max(time_span, 1)
        
        return {
            "avg_response_time_ms": round(avg_time * 1000, 2),
            "min_response_time_ms": round(min_time * 1000, 2),
            "max_response_time_ms": round(max_time * 1000, 2),
            "p90_response_time_ms": round(p90 * 1000, 2),
            "p95_response_time_ms": round(p95 * 1000, 2),
            "p99_response_time_ms": round(p99 * 1000, 2),
            "request_count": count,
            "requests_per_second": round(requests_per_second, 2)
        }
        
    def reset(self, endpoint: Optional[str] = None) -> None:
        """
        重置指标数据
        
        Args:
            endpoint: 要重置的API端点，若为None则重置所有指标
        """
        with self.lock:
            if endpoint:
                if endpoint in self.metrics:
                    self.metrics[endpoint] = {
                        "response_times": deque(),
                        "timestamps": deque(),
                        "min_time": float("inf"),
                        "max_time": 0,
                        "total_time": 0,
                        "count": 0
                    }
            else:
                self.metrics.clear()


# 创建不同时间窗口的指标收集器
minute_metrics = TimeWindowMetrics(60)  # 1分钟窗口
hour_metrics = TimeWindowMetrics(3600)  # 1小时窗口
day_metrics = TimeWindowMetrics(86400)  # 24小时窗口


def record_api_performance(endpoint: str, response_time: float) -> None:
    """
    记录API性能到所有时间窗口
    
    Args:
        endpoint: API端点
        response_time: 响应时间（秒）
    """
    minute_metrics.record(endpoint, response_time)
    hour_metrics.record(endpoint, response_time)
    day_metrics.record(endpoint, response_time)


def get_slow_endpoints(window: str = "hour", limit: int = 5) -> List[Dict[str, Any]]:
    """
    获取最慢的API端点
    
    Args:
        window: 时间窗口 "minute", "hour", "day"
        limit: 返回的端点数量
        
    Returns:
        最慢端点列表，按平均响应时间降序排序
    """
    if window == "minute":
        metrics = minute_metrics.get_metrics()
    elif window == "hour":
        metrics = hour_metrics.get_metrics()
    else:
        metrics = day_metrics.get_metrics()
    
    # 按平均响应时间排序
    sorted_endpoints = sorted(
        [
            {"endpoint": ep, **data}
            for ep, data in metrics.items()
        ],
        key=lambda x: x["avg_response_time_ms"],
        reverse=True
    )
    
    return sorted_endpoints[:limit]


def get_high_traffic_endpoints(window: str = "hour", limit: int = 5) -> List[Dict[str, Any]]:
    """
    获取请求量最高的API端点
    
    Args:
        window: 时间窗口 "minute", "hour", "day"
        limit: 返回的端点数量
        
    Returns:
        高流量端点列表，按请求数降序排序
    """
    if window == "minute":
        metrics = minute_metrics.get_metrics()
    elif window == "hour":
        metrics = hour_metrics.get_metrics()
    else:
        metrics = day_metrics.get_metrics()
    
    # 按请求数排序
    sorted_endpoints = sorted(
        [
            {"endpoint": ep, **data}
            for ep, data in metrics.items()
        ],
        key=lambda x: x["request_count"],
        reverse=True
    )
    
    return sorted_endpoints[:limit] 