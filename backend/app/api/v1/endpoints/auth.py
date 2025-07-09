from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_active_user
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, verify_token
from app.crud.user import user as user_crud
from app.schemas.auth import Token, Login
from app.core.permissions import require_permissions
from app.models.user import User
from app.schemas.user import User as UserSchema

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    db: AsyncSession = Depends(get_db),
    username: str = Form(...),
    password: str = Form(...),
    grant_type: str = Form(default="password")
) -> Any:
    """
    获取OAuth2兼容的令牌
    """
    if grant_type != "password":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持的授权类型",
        )

    user = await user_crud.authenticate(
        db, username=username, password=password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="用户未激活")
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    
    # 创建刷新令牌
    refresh_token = create_refresh_token(subject=user.id)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token
    }

@router.post("/refresh", response_model=Token)
async def refresh_token_endpoint(
    db: AsyncSession = Depends(get_db),
    refresh_token: str = None
) -> Any:
    """
    刷新访问令牌
    """
    token_data = verify_token(refresh_token)
    if not token_data or token_data.type != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await user_crud.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="用户未激活")
    
    # 创建新的访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    
    # 创建新的刷新令牌
    new_refresh_token = create_refresh_token(subject=user.id)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": new_refresh_token
    }

@router.post("/reload-policy", status_code=200)
async def reload_rbac_policy(
    current_user: User = require_permissions(path="/api/v1/auth/reload-policy", method="POST")
):
    """
    手动重新加载 RBAC 策略文件
    此 API 只能由管理员调用
    """
    from app.core.permissions import reload_policy
    
    success = await reload_policy()
    
    if success:
        return {"message": "RBAC 策略已成功重新加载"}
    else:
        raise HTTPException(
            status_code=500,
            detail="无法重新加载 RBAC 策略"
        )

@router.get("/me", response_model=UserSchema)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    获取当前登录用户的信息
    """
    return current_user
