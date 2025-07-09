import logging
import json
from datetime import datetime
from datetime import timezone
from typing import Any, Dict, Literal
from pathlib import Path
from logging.handlers import RotatingFileHandler
import traceback

class SimpleFormatter(logging.Formatter):
    """简单的日志格式化器，只显示必要信息"""
    def __init__(self):
        super().__init__("%(asctime)s: %(levelname)s: %(message)s [%(filename)s/%(module)s/%(funcName)s:%(lineno)d]", "%Y-%m-%d %H:%M:%S")

class CustomJSONFormatter(logging.Formatter):
    """详细的JSON格式化器，包含完整的上下文信息"""
    def __init__(self):
        super().__init__()
        self.default_keys = [
            'timestamp', 'level', 'logger', 'message',
            'module', 'function', 'path', 'line_number',
            'exception', 'stack_trace'
        ]

    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'path': record.pathname,
            'line_number': record.lineno
        }

        # 添加异常信息
        if record.exc_info:
            log_data['exception'] = str(record.exc_info[1])
            log_data['stack_trace'] = traceback.format_exception(*record.exc_info)

        # 添加额外字段
        for key, value in record.__dict__.items():
            if key not in self.default_keys and not key.startswith('_'):
                log_data[key] = value

        return json.dumps(log_data, ensure_ascii=False)

def setup_logging(
    log_level: str = "INFO",
    log_file: str = "logs/app.log",
    max_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    log_format: Literal["simple", "json"] = "simple"
) -> None:
    """
    设置日志配置
    
    Args:
        log_level: 日志级别
        log_file: 日志文件路径
        max_size: 单个日志文件最大大小
        backup_count: 保留的备份文件数量
        log_format: 日志格式，可选 'simple'(简单格式) 或 'json'(详细JSON格式)
    """
    # 创建日志目录
    log_path = Path(log_file).parent
    log_path.mkdir(parents=True, exist_ok=True)

    # 创建根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # 清除现有的处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 选择格式化器
    if log_format == "json":
        formatter = CustomJSONFormatter()
    else:
        formatter = SimpleFormatter()

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 创建文件处理器
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_size,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # 设置第三方库的日志级别
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

# 全局日志获取函数
def get_logger(name: str = None) -> logging.Logger:
    """
    获取应用日志记录器
    
    Args:
        name: 日志记录器名称，默认使用调用模块的名称
        
    Returns:
        配置好的日志记录器实例
    """
    return logging.getLogger(name)
