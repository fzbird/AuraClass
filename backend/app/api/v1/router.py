from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    roles,
    classes,
    students,
    quant_items,
    quant_item_categories,
    quant_records,
    statistics,
    notifications,
    ai_assistant,
    files,
    exports,
    health,
    uploads,
    admin,
    permissions
)

api_router = APIRouter()

# 认证相关路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])

# 用户管理路由
api_router.include_router(users.router, prefix="/users", tags=["用户管理"])

# 角色管理路由
api_router.include_router(roles.router, prefix="/roles", tags=["角色管理"])

# 班级管理路由
api_router.include_router(classes.router, prefix="/classes", tags=["班级管理"])

# 学生管理路由
api_router.include_router(students.router, prefix="/students", tags=["学生管理"])

# 量化项目管理路由
api_router.include_router(quant_items.router, prefix="/quant-items", tags=["量化项目"])

# 量化项目分类路由
api_router.include_router(quant_item_categories.router, prefix="/quant-item-categories", tags=["量化项目分类"])

# 量化记录管理路由
api_router.include_router(quant_records.router, prefix="/quant-records", tags=["量化记录"])

# 统计分析路由
api_router.include_router(statistics.router, prefix="/statistics", tags=["统计分析"])

# 通知管理路由
api_router.include_router(notifications.router, prefix="/notifications", tags=["通知管理"])

# AI助手路由
api_router.include_router(ai_assistant.router, prefix="/ai-assistant", tags=["AI助手"])

# 文件管理路由
api_router.include_router(files.router, prefix="/files", tags=["文件管理"])

# 上传文件路由
api_router.include_router(uploads.router, prefix="/uploads", tags=["文件上传"])

# 数据导出路由
api_router.include_router(exports.router, prefix="/exports", tags=["数据导出"])

# 健康检查路由
api_router.include_router(health.router, prefix="/health", tags=["系统健康"])

# 系统管理路由
api_router.include_router(admin.router, prefix="/admin", tags=["系统管理"])

# 权限管理路由
api_router.include_router(permissions.router, prefix="/permissions", tags=["权限管理"])
