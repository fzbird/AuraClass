import json
import os
import sys
import importlib
import threading
from typing import Any, Dict, List, Optional, Union, Callable
from pathlib import Path

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource
from pydantic.fields import FieldInfo


# 自定义设置预处理函数，处理环境变量中的特殊情况
def setting_customizer(settings_cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """在settings初始化前自定义处理环境变量值"""
    # 处理ALLOWED_ORIGINS，避免Pydantic尝试解析为JSON
    if "ALLOWED_ORIGINS" in input_data and isinstance(input_data["ALLOWED_ORIGINS"], str):
        # 如果是JSON格式的字符串，尝试解析为普通的逗号分隔格式
        value = input_data["ALLOWED_ORIGINS"]
        if value.startswith('[') and value.endswith(']'):
            try:
                json_value = json.loads(value)
                if isinstance(json_value, list):
                    input_data["ALLOWED_ORIGINS"] = ','.join(json_value)
            except:
                pass
    return input_data


class Settings(BaseSettings):
    # 应用基本配置
    PROJECT_NAME: str = "AuraClass"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "AuraClass班级量化管理系统"
    API_V1_STR: str = "/api/v1"
    APP_ENV: str = "development"
    DEBUG: bool = True
    
    # 新增系统配置字段
    DATA_BACKUP_DAYS: int = 7
    LOG_RETENTION_DAYS: int = 30
    ENABLE_NOTIFICATIONS: bool = True
    ENABLE_AUDIT_LOG: bool = True
    CACHE_TIMEOUT: int = 60
    FRONTEND_URL: str = "http://localhost:8201"
    
    # 安全配置
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # 数据库配置
    DATABASE_URL: str
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_ECHO: bool = False
    
    # CORS配置 - 使用字符串类型存储，避免Pydantic的JSON解析问题
    ALLOWED_ORIGINS: str = "http://localhost:8200,ws://localhost:8200"
    
    # 添加验证器确保ALLOWED_ORIGINS格式正确
    @field_validator("ALLOWED_ORIGINS")
    def validate_allowed_origins(cls, v: str) -> str:
        # 清理ALLOWED_ORIGINS字符串
        if not v:
            return "http://localhost:8200,ws://localhost:8200"
                
        # 分割并处理各个origin
        origins = []
        for origin in v.split(','):
            origin = origin.strip()
            if not origin:
                continue
                
            # 检查无效的通配符格式
            if "*" in origin and not origin.endswith("*") and not origin.startswith("*"):
                # 检查端口中的通配符
                if ":" in origin and "*" in origin.split(":")[-1] and "*" != origin.split(":")[-1]:
                    # 替换非法的端口通配符，例如 'http://localhost:*' 转为 'http://localhost:8200'
                    origin = "http://localhost:8200"
            origins.append(origin)
            
        if not origins:
            return "http://localhost:8200,ws://localhost:8200"
            
        return ','.join(origins)
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    LOG_FORMAT: str = "json"
    
    # 监控配置
    METRICS_UPDATE_INTERVAL: int = 60
    ENABLE_METRICS: bool = True
    SLOW_API_THRESHOLD: float = 1.0  # 慢API阈值（秒）
    
    # Redis配置
    # REDIS_URL: str = "redis://localhost:6379/0"
    
    # 文件上传配置
    UPLOADS_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    # UPLOADS_DIR: str = "uploads/ai-assistant"  # AI助手上传文件目录
    ALLOWED_FILE_TYPES: List[str] = [
        "image/jpeg", "image/png", "image/gif", "image/webp",
        "application/pdf", 
        "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "text/plain", "text/csv"
    ]
    MAX_FILES_PER_REQUEST: int = 5
    
    # Casbin配置
    CASBIN_MODEL_PATH: str = "backend/app/core/rbac_model.conf"
    CASBIN_POLICY_PATH: str = "backend/app/core/rbac_policy.csv"
    
    # Ollama配置
    OLLAMA_BASE_URL: str = "http://192.168.5.117:11434"
    OLLAMA_MODEL_NAME: str = "gemma3:27b"
    OLLAMA_API_KEY: str = "your-ollama-api-key-here"
    OLLAMA_USE_SYSTEM_PARAM: bool = True
    OLLAMA_USE_THINK_MODE: bool = True  # 开启思考模式

    # Open-Webui配置
    OPEN_WEBUI_BASE_URL: str = "http://192.168.5.117:3000"
    OPEN_WEBUI_MODEL_NAME: str = "gemma3:27b"
    OPEN_WEBUI_API_KEY: str = "your-open-webui-api-key-here"
    OPEN_WEBUI_USE_THINK_MODE: bool = True  # 开启思考模式

    # OpenAI配置
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_API_KEY: str = "your-openai-api-key-here"

    # 启动端口
    BACKEND_PORT: int = 8200
    FRONTEND_PORT: int = 8210
    
    # 项目根目录
    @property
    def BASE_DIR(self) -> Path:
        return Path(__file__).parent.parent.parent
    
    # 将ALLOWED_ORIGINS字符串转换为列表，用于应用中的CORS设置
    @property
    def get_allowed_origins(self) -> List[str]:
        if not self.ALLOWED_ORIGINS:
            return ["http://localhost:8200", "ws://localhost:8200"]
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]
    
    # 配置模型，添加自定义预处理器
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        customise_sources=[
            lambda settings_cls, source_settings: PydanticBaseSettingsSource(
                setting_customizer(settings_cls, source_settings._apply_in_env_file())
            ),
        ],
    )


# # 设置默认环境变量避免验证问题
# os.environ.setdefault('SECRET_KEY', 'YOUR_DEFAULT_SECRET_KEY_HERE_CHANGE_IN_PRODUCTION')
# os.environ.setdefault('DATABASE_URL', 'sqlite:///./test.db')

# SettingsProxy类 - 创建一个代理对象，通过__getattr__动态转发所有属性访问到内部的settings实例
class SettingsProxy:
    """
    设置代理类，实现单例模式和热重载功能
    
    这个类代理了Settings类的所有属性和方法的访问，
    同时提供重载配置的功能，确保所有引用了settings的地方
    都能看到最新的配置值。
    """
    _instance = None
    _lock = threading.RLock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(SettingsProxy, cls).__new__(cls)
                cls._instance._settings = None
                cls._instance._load_settings()
            return cls._instance
    
    def _load_settings(self):
        """加载设置实例"""
        self._settings = Settings()
        return self._settings
        
    def __getattr__(self, name):
        """转发所有属性访问到内部的settings实例"""
        return getattr(self._settings, name)
    
    def reload(self):
        """
        重新加载配置
        
        这个方法会重新从.env文件加载所有配置，并返回变更的配置项列表
        """
        from dotenv import load_dotenv
        
        try:
            # 记录当前配置，用于比较变化
            old_settings = self._settings
            
            # 重置环境变量
            for key in list(os.environ.keys()):
                if key.isupper() and key not in ('PATH', 'SYSTEMROOT', 'PYTHONPATH'):
                    del os.environ[key]
            
            # 设置默认环境变量避免验证问题
            os.environ.setdefault('SECRET_KEY', 'YOUR_DEFAULT_SECRET_KEY_HERE_CHANGE_IN_PRODUCTION')
            os.environ.setdefault('DATABASE_URL', 'sqlite:///./test.db')
            
            # 重新加载.env文件
            env_path = Path(__file__).parent.parent.parent / ".env"
            print(f"正在重新加载配置文件: {env_path}")
            load_dotenv(str(env_path), override=True)
            
            # 创建新的设置实例
            self._settings = Settings()
            
            # 比较并找出变化的配置项
            changes = []
            for attr in dir(self._settings):
                if attr.startswith('_') or attr.startswith('get_') or callable(getattr(self._settings, attr)):
                    continue
                    
                old_val = getattr(old_settings, attr, None)
                new_val = getattr(self._settings, attr, None)
                
                if old_val != new_val:
                    changes.append(f"{attr}: {old_val} -> {new_val}")
                    
            # 输出变更日志
            if changes:
                print(f"配置已重新加载，检测到{len(changes)}处变更:")
                for change in changes:
                    print(f"  - {change}")
            else:
                print("配置已重新加载，无变更")
                
            # 尝试记录到日志系统
            try:
                from app.core.logging import get_logger
                logger = get_logger(__name__)
                if changes:
                    logger.info(f"配置已重新加载，变更项: {', '.join(changes)}")
                else:
                    logger.info("配置已重新加载，无变更")
            except ImportError:
                pass
                
            return changes
                
        except Exception as e:
            error_msg = f"重载配置时发生错误: {str(e)}"
            print(error_msg)
            try:
                from app.core.logging import get_logger
                logger = get_logger(__name__)
                logger.error(error_msg)
            except:
                pass
            return []


# 创建全局settings实例，使用代理模式
settings = SettingsProxy()

# 兼容旧函数接口
def reload_settings():
    """
    重新加载配置的兼容函数
    
    为了保持向后兼容性，保留此函数
    """
    return settings.reload()