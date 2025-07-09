from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
from pydantic import BaseModel

from app.api.deps import get_db
from app.models.user import User
from app.core.permissions import require_permissions, get_enforcer, reload_policy
from app.schemas.role import Role

router = APIRouter()

class PermissionPolicy(BaseModel):
    role: str
    resource: str
    action: str

class PolicyItem(BaseModel):
    sub: str  # 角色
    obj: str  # 资源路径
    act: str  # 动作，如GET, POST, PUT, DELETE, *

class UpdatePolicyRequest(BaseModel):
    role: str
    policies: List[Dict[str, str]]  # 包含obj和act的列表

@router.get("/policies", response_model=Dict[str, List[Dict[str, str]]])
async def get_policies(
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permissions(path="/api/v1/permissions/policies", method="GET")
):
    """
    获取所有权限策略
    
    返回按角色分组的策略列表
    """
    enforcer = await get_enforcer(db)
    policies = enforcer.get_policy()
    
    # 按角色组织策略
    role_policies = {}
    
    for policy in policies:
        if len(policy) >= 3:
            role = policy[0]
            resource = policy[1]
            action = policy[2]
            
            if role not in role_policies:
                role_policies[role] = []
            
            role_policies[role].append({
                "resource": resource,
                "action": action
            })
    
    return role_policies

@router.get("/role-policies/{role_name}", response_model=List[Dict[str, str]])
async def get_role_policies(
    role_name: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permissions(path="/api/v1/permissions/role-policies/{role_name}", method="GET")
):
    """
    获取指定角色的所有权限策略
    """
    enforcer = await get_enforcer(db)
    policies = enforcer.get_filtered_policy(0, role_name)
    
    result = []
    for policy in policies:
        if len(policy) >= 3:
            result.append({
                "resource": policy[1],
                "action": policy[2]
            })
    
    return result

@router.post("/role-policies/{role_name}", status_code=200)
async def update_role_policies(
    role_name: str,
    policies: List[Dict[str, str]] = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permissions(path="/api/v1/permissions/role-policies/{role_name}", method="POST")
):
    """
    更新指定角色的权限策略
    
    会先清除该角色现有策略，然后添加新策略
    """
    enforcer = await get_enforcer(db)
    
    # 验证角色是否存在
    from app.crud.role import role as role_crud
    role = await role_crud.get_by_name(db, name=role_name)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 清除该角色现有的所有策略
    enforcer.remove_filtered_policy(0, role_name)
    
    # 添加新策略
    for policy in policies:
        resource = policy.get("resource")
        action = policy.get("action")
        if resource and action:
            enforcer.add_policy(role_name, resource, action)
    
    # 保存策略到文件
    enforcer.save_policy()
    
    # 重新加载策略
    await reload_policy()
    
    return {"message": f"角色 '{role_name}' 的权限策略已更新"}

@router.get("/resources", response_model=List[str])
async def get_resources(
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permissions(path="/api/v1/permissions/resources", method="GET")
):
    """
    获取系统中所有可用的资源路径
    """
    enforcer = await get_enforcer(db)
    policies = enforcer.get_policy()
    
    # 提取所有独特的资源路径
    resources = set()
    for policy in policies:
        if len(policy) >= 2:
            resources.add(policy[1])
    
    # 添加一些常见的API路径模式
    api_resources = [
        "/api/v1/users",
        "/api/v1/users/*",
        "/api/v1/roles",
        "/api/v1/roles/*",
        "/api/v1/classes",
        "/api/v1/classes/*",
        "/api/v1/students", 
        "/api/v1/students/*",
        "/api/v1/quant-items",
        "/api/v1/quant-items/*",
        "/api/v1/quant-records",
        "/api/v1/quant-records/*",
        "/api/v1/notifications",
        "/api/v1/notifications/*",
        "/api/v1/ai-assistant",
        "/api/v1/ai-assistant/*",
        "/api/v1/admin/*",
        "/api/v1/auth/*",
        "/api/v1/uploads",
        "/api/v1/uploads/*",
        "/api/v1/permissions/*",
        "/api/v1/statistics/*",
        "/api/v1/exports/*",
        "/api/v1/health",
        "/api/v1/quant-item-categories/*"
    ]
    
    for resource in api_resources:
        resources.add(resource)
    
    return sorted(list(resources))

@router.get("/actions", response_model=List[str])
async def get_actions(
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permissions(path="/api/v1/permissions/actions", method="GET")
):
    """
    获取系统中所有可用的操作（动作）类型
    """
    return ["GET", "POST", "PUT", "DELETE", "PATCH", "*"]

@router.post("/reload", status_code=200)
async def reload_permission_policy(
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permissions(path="/api/v1/permissions/reload", method="POST")
):
    """
    重新加载权限策略
    """
    success = await reload_policy()
    
    if success:
        return {"message": "权限策略已成功重新加载"}
    else:
        raise HTTPException(
            status_code=500,
            detail="无法重新加载权限策略"
        )

@router.get("/api-paths", response_model=List[str])
async def get_all_api_paths(
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permissions(path="/api/v1/permissions/api-paths", method="GET")
):
    """
    获取系统中所有实际的API路径
    """
    # 基于后端实际API端点创建资源路径列表
    api_endpoints = [
        # 用户管理
        "/api/v1/users",
        "/api/v1/users/{user_id}",
        
        # 角色管理
        "/api/v1/roles",
        "/api/v1/roles/{role_id}",
        "/api/v1/roles/{role_id}/users",
        
        # 权限管理
        "/api/v1/permissions/policies",
        "/api/v1/permissions/role-policies/{role_name}",
        "/api/v1/permissions/resources",
        "/api/v1/permissions/actions",
        "/api/v1/permissions/reload",
        "/api/v1/permissions/api-paths",
        
        # 班级管理
        "/api/v1/classes",
        "/api/v1/classes/{class_id}",
        "/api/v1/classes/{class_id}/students",
        
        # 学生管理
        "/api/v1/students",
        "/api/v1/students/{student_id}",
        "/api/v1/students/{student_id}/records",
        "/api/v1/students/import",
        "/api/v1/students/batch",
        
        # 量化指标
        "/api/v1/quant-items",
        "/api/v1/quant-items/{item_id}",
        "/api/v1/quant-items/categories",
        "/api/v1/quant-items/templates",
        
        # 量化记录
        "/api/v1/quant-records",
        "/api/v1/quant-records/{record_id}",
        "/api/v1/quant-records/batch",
        "/api/v1/quant-records/class/{class_id}",
        "/api/v1/quant-records/import",
        
        # 通知管理
        "/api/v1/notifications",
        "/api/v1/notifications/{notification_id}",
        "/api/v1/notifications/unread",
        "/api/v1/notifications/read-all",
        
        # AI助手
        "/api/v1/ai-assistant/chat",
        "/api/v1/ai-assistant/files",
        "/api/v1/ai-assistant/models",
        
        # 系统管理
        "/api/v1/admin/config",
        "/api/v1/admin/restart",
        "/api/v1/admin/backup",
        "/api/v1/admin/restore",
        
        # 认证
        "/api/v1/auth/login",
        "/api/v1/auth/token",
        "/api/v1/auth/refresh",
        
        # 文件上传
        "/api/v1/uploads",
        "/api/v1/uploads/{file_id}",
        
        # 统计分析
        "/api/v1/statistics/dashboard",
        "/api/v1/statistics/students",
        "/api/v1/statistics/classes",
        "/api/v1/statistics/trends",
        
        # 导出功能
        "/api/v1/exports/records",
        "/api/v1/exports/students",
        
        # 健康检查
        "/api/v1/health"
    ]
    
    return sorted(api_endpoints) 