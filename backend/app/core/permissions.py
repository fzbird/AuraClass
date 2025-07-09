from typing import Optional, Dict
from fastapi import Depends, HTTPException, status
from casbin import Enforcer
from casbin import FileAdapter
import os
from pathlib import Path
import time

from app.core.config import settings
from app.db.session import get_db
from app.api.deps import get_current_active_user
from sqlalchemy.ext.asyncio import AsyncSession

# 创建一个全局缓存来存储enforcer实例
_enforcer_cache: Dict[str, Enforcer] = {}
# 存储策略文件的最后修改时间
_policy_file_last_modified: float = 0

def ensure_policy_file_exists():
    """确保策略文件存在，如果不存在则创建"""
    base_dir = Path(__file__).parent.parent.parent
    policy_file = base_dir / "app" / "core" / "rbac_policy.csv"
    if not policy_file.exists():
        policy_file.parent.mkdir(parents=True, exist_ok=True)
        with open(policy_file, 'w', encoding='utf-8') as f:
            # 管理员权限
            f.write("p, admin, /api/v1/users, *\n")
            f.write("p, admin, /api/v1/users/*, *\n")
            f.write("p, admin, /api/v1/roles, *\n")
            f.write("p, admin, /api/v1/roles/*, *\n")
            f.write("p, admin, /api/v1/classes, *\n")
            f.write("p, admin, /api/v1/classes/*, *\n")
            f.write("p, admin, /api/v1/students, *\n")
            f.write("p, admin, /api/v1/students/*, *\n")
            f.write("p, admin, /api/v1/quant-items, *\n")
            f.write("p, admin, /api/v1/quant-items/*, *\n")
            f.write("p, admin, /api/v1/quant-records, *\n")
            f.write("p, admin, /api/v1/quant-records/*, *\n")
            f.write("p, admin, /api/v1/notifications, *\n")
            f.write("p, admin, /api/v1/notifications/*, *\n")
            f.write("p, admin, /api/v1/ai-queries, *\n")
            f.write("p, admin, /api/v1/ai-queries/*, *\n")
            
            # 教师权限
            f.write("p, teacher, /api/v1/students/*, GET\n")
            f.write("p, teacher, /api/v1/classes/*, GET\n")
            f.write("p, teacher, /api/v1/quant-records, POST\n")
            f.write("p, teacher, /api/v1/quant-records/*, GET\n")
            
            # 学生权限
            f.write("p, student, /api/v1/students/{id}, GET\n")
            f.write("p, student, /api/v1/quant-records/*, GET\n")
            
            # 家长权限
            f.write("p, parent, /api/v1/students/{id}, GET\n")
            f.write("p, parent, /api/v1/quant-records/*, GET\n")

def is_policy_file_modified() -> bool:
    """检查策略文件是否被修改"""
    global _policy_file_last_modified
    base_dir = Path(__file__).parent.parent.parent
    policy_file = base_dir / "app" / "core" / "rbac_policy.csv"
    
    if not policy_file.exists():
        return False
    
    current_mtime = policy_file.stat().st_mtime
    
    # 首次检查
    if _policy_file_last_modified == 0:
        _policy_file_last_modified = current_mtime
        return False
    
    # 检查文件是否被修改
    if current_mtime > _policy_file_last_modified:
        _policy_file_last_modified = current_mtime
        return True
    
    return False

async def reload_policy():
    """重新加载策略文件"""
    global _enforcer_cache
    if "enforcer" in _enforcer_cache:
        enforcer = _enforcer_cache["enforcer"]
        # 清除现有策略
        enforcer.clear_policy()
        # 重新加载策略
        enforcer.load_policy()
        print("RBAC 策略已重新加载")
        return True
    return False

async def get_enforcer(db: AsyncSession = Depends(get_db)):
    """
    获取Casbin强制器，并在策略文件变更时自动重载
    """
    # 使用缓存的enforcer实例如果已经存在
    global _enforcer_cache
    
    # 检查策略文件是否被修改
    if is_policy_file_modified() and "enforcer" in _enforcer_cache:
        await reload_policy()
    
    if "enforcer" in _enforcer_cache:
        return _enforcer_cache["enforcer"]
    
    try:
        # 获取项目根目录
        base_dir = Path(__file__).parent.parent.parent
        model_path = base_dir / "app" / "core" / "rbac_model.conf"
        policy_path = base_dir / "app" / "core" / "rbac_policy.csv"
        
        # 确保配置文件存在
        ensure_policy_file_exists()
        
        # 直接创建一个新的enforcer
        enforcer = Enforcer(str(model_path), str(policy_path))
        
        # 更新最后修改时间
        global _policy_file_last_modified
        _policy_file_last_modified = policy_path.stat().st_mtime
        
        # 缓存enforcer实例
        _enforcer_cache["enforcer"] = enforcer
        return enforcer
    except Exception as e:
        # 如果出错，记录错误并返回一个允许所有操作的enforcer（紧急回退）
        print(f"Error initializing enforcer: {str(e)}")
        model_path = base_dir / "app" / "core" / "rbac_model.conf"
        fallback_enforcer = Enforcer(str(model_path), None)
        fallback_enforcer.add_policy("*", "*", "*")  # 允许所有操作
        return fallback_enforcer

async def check_permission(
    path: str,
    method: str,
    user_role: str,
    enforcer = Depends(get_enforcer),
):
    """
    检查权限
    """
    if enforcer.enforce(user_role, path, method):
        return True
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="权限不足"
    )

def require_permissions(path: str, method: str):
    """
    权限要求装饰器
    """
    async def permission_dependency(
        current_user = Depends(get_current_active_user),  # 确保获取已验证的当前用户
        enforcer = Depends(get_enforcer)
    ):
        # 如果用户未登录，拒绝访问
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户未登录"
            )
        
        # 如果用户没有role属性或role没有name属性，拒绝访问
        if not hasattr(current_user, "role") or not hasattr(current_user.role, "name"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="用户角色未定义"
            )
        
        # 假设用户对象有一个role属性，关联到role对象，后者有一个name属性
        if not enforcer.enforce(current_user.role.name, path, method):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        return current_user  # 返回当前用户，而不仅仅是True
    
    return Depends(permission_dependency)
