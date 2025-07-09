from typing import Dict, Any, List
import os
import subprocess
import sys
import signal
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.core.permissions import require_permissions
from app.models.user import User
from app.core.config import settings
from pathlib import Path
from dotenv import load_dotenv, find_dotenv, set_key

router = APIRouter()


class ConfigSettings(BaseModel):
    """系统配置设置模型"""
    PROJECT_NAME: str
    DATA_BACKUP_DAYS: int
    LOG_RETENTION_DAYS: int
    ENABLE_NOTIFICATIONS: bool
    ENABLE_AUDIT_LOG: bool
    CACHE_TIMEOUT: int
    DATABASE_URL: str
    SECRET_KEY: str
    DEBUG: bool
    FRONTEND_URL: str
    ALLOWED_ORIGINS: str  # 前端使用字符串格式
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int


@router.get("/config", response_model=ConfigSettings)
async def get_system_config(
    current_user: User = require_permissions(path="/api/v1/admin/config", method="GET")
) -> Dict[str, Any]:
    """
    获取系统配置
    
    需要管理员权限访问
    """
    try:
        # 使用Settings实例获取配置
        config = {
            "PROJECT_NAME": settings.PROJECT_NAME,
            "DATA_BACKUP_DAYS": settings.DATA_BACKUP_DAYS,
            "LOG_RETENTION_DAYS": settings.LOG_RETENTION_DAYS,
            "ENABLE_NOTIFICATIONS": settings.ENABLE_NOTIFICATIONS,
            "ENABLE_AUDIT_LOG": settings.ENABLE_AUDIT_LOG,
            "CACHE_TIMEOUT": settings.CACHE_TIMEOUT,
            "DATABASE_URL": settings.DATABASE_URL,
            "SECRET_KEY": settings.SECRET_KEY,
            "DEBUG": settings.DEBUG,
            "FRONTEND_URL": settings.FRONTEND_URL,
            "ALLOWED_ORIGINS": settings.ALLOWED_ORIGINS,
            "ALGORITHM": settings.ALGORITHM,
            "ACCESS_TOKEN_EXPIRE_MINUTES": settings.ACCESS_TOKEN_EXPIRE_MINUTES
        }
        
        return config
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"无法读取系统配置: {str(e)}"
        )


@router.put("/config", response_model=Dict[str, Any])
async def update_system_config(
    config: ConfigSettings,
    current_user: User = require_permissions(path="/api/v1/admin/config", method="PUT")
) -> Dict[str, Any]:
    """
    更新系统配置
    
    需要管理员权限访问。配置更新后会立即重新加载，无需重启服务器。
    """
    try:
        # 获取.env文件路径
        env_path = Path(__file__).parent.parent.parent.parent.parent / ".env"
        
        # 验证并处理ALLOWED_ORIGINS格式
        allowed_origins = config.ALLOWED_ORIGINS
        # 清理无效的通配符格式
        if "*" in allowed_origins and not allowed_origins.endswith("*") and not allowed_origins.startswith("*"):
            origins = []
            for origin in allowed_origins.split(","):
                origin = origin.strip()
                if ":" in origin and "*" in origin.split(":")[-1] and "*" != origin.split(":")[-1]:
                    # 替换非法的端口通配符
                    origin = "http://localhost:8200"  
                origins.append(origin)
            allowed_origins = ",".join(origins)
            
        # 转换为字符串格式的环境变量
        env_vars = {
            "PROJECT_NAME": config.PROJECT_NAME,
            "DATA_BACKUP_DAYS": str(config.DATA_BACKUP_DAYS),
            "LOG_RETENTION_DAYS": str(config.LOG_RETENTION_DAYS),
            "ENABLE_NOTIFICATIONS": str(config.ENABLE_NOTIFICATIONS).lower(),
            "ENABLE_AUDIT_LOG": str(config.ENABLE_AUDIT_LOG).lower(),
            "CACHE_TIMEOUT": str(config.CACHE_TIMEOUT),
            "DATABASE_URL": config.DATABASE_URL,
            "SECRET_KEY": config.SECRET_KEY,
            "DEBUG": str(config.DEBUG).lower(),
            "FRONTEND_URL": config.FRONTEND_URL,
            "ALLOWED_ORIGINS": allowed_origins,
            "ALGORITHM": config.ALGORITHM,
            "ACCESS_TOKEN_EXPIRE_MINUTES": str(config.ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        
        # 使用python-dotenv处理.env文件
        dotenv_path = str(env_path)
        
        # 更新每个环境变量
        for key, value in env_vars.items():
            set_key(dotenv_path, key, value)
        
        # 使用Settings代理类的reload方法重新加载配置
        # 这将会清除环境变量，重新加载.env文件，并创建新的Settings实例
        changes = settings.reload()
        
        # 准备响应
        response = {
            "message": "系统配置已更新并立即生效",
            "updated_at": str(Path(dotenv_path).stat().st_mtime),
            "changes": len(changes),
        }
        
        # 添加配置变更详情
        if changes:
            response["change_details"] = changes
            
        # 添加关键配置的当前值，用于前端验证
        response["current_config"] = {
            "project_name": settings.PROJECT_NAME,
            "debug": settings.DEBUG,
            "data_backup_days": settings.DATA_BACKUP_DAYS,
            "allowed_origins": settings.ALLOWED_ORIGINS,
        }
        
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"无法更新系统配置: {str(e)}"
        )


@router.post("/restart", response_model=Dict[str, str])
async def restart_server(
    current_user: User = require_permissions(path="/api/v1/admin/restart", method="POST")
) -> Dict[str, str]:
    """
    重启服务器
    
    需要管理员权限访问
    """
    try:
        # 如果环境中有GUNICORN_PID，则尝试重启gunicorn
        gunicorn_pid = os.environ.get("GUNICORN_PID")
        if gunicorn_pid:
            try:
                os.kill(int(gunicorn_pid), signal.SIGHUP)
                return {"message": "服务器正在重启"}
            except (ProcessLookupError, ValueError):
                pass

        # 尝试使用systemctl重启服务（如果是systemd服务）
        try:
            subprocess.run(["systemctl", "restart", "auraclass"], 
                          check=True, capture_output=True)
            return {"message": "服务器服务正在重启"}
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
                
        # 尝试通过重新执行当前进程来重启
        # 注意：这是最后的手段，可能会导致异常行为
        pid = os.getpid()
        os.system(f"kill -1 {pid} &")  # 使用SIGHUP信号
        
        return {"message": "服务器正在重启, 请稍后刷新页面"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"无法重启服务器: {str(e)}"
        ) 