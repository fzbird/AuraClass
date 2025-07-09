# AuraClass 班级量化管理软件后端设计文档

## 1. 后端架构概述

AuraClass 后端采用 FastAPI 框架构建，实现高性能的异步 API 服务，支持班级量化管理系统的各项功能。系统后端使用分层架构，遵循关注点分离原则，确保代码模块化和可维护性。

### 1.1 架构图

```
+----------------------------------+
|            API 层                |
|  (路由、请求验证、响应格式化)     |
+----------------------------------+
                 |
+----------------------------------+
|            服务层                |
|  (业务逻辑、事务管理、权限验证)   |
+----------------------------------+
                 |
+----------------------------------+
|            数据访问层            |
|  (CRUD 操作、数据库交互)         |
+----------------------------------+
                 |
+----------------------------------+
|            数据库层              |
|  (MySQL 数据库、模型定义)        |
+----------------------------------+
```

### 1.2 核心功能模块

- **用户认证与鉴权** - JWT 认证、Casbin 权限控制
- **系统设置管理** - 班级信息、用户管理、角色管理
- **量化项目管理** - 定义和管理量化考核项目
- **量化信息管理** - 记录和查询量化信息
- **统计分析** - 多维度的数据统计和图表生成
- **WebSocket 服务** - 实时通知和 AI 助手通信
- **异步任务处理** - 处理耗时操作如报表生成、数据导出

## 2. 技术栈详情

### 2.1 核心框架

- **Python 3.10+** - 利用最新的类型注解和异步特性
- **FastAPI 0.100.0+** - 高性能 API 框架，支持异步和类型提示
- **Pydantic v2** - 数据验证和设置管理
- **SQLAlchemy 2.0** - 异步 ORM，提供数据库抽象层
- **Alembic** - 数据库迁移工具
- **Casbin** - 灵活的访问控制框架
- **asyncpg** - 高性能 PostgreSQL 异步驱动

### 2.2 认证与安全

- **python-jose** - JWT 令牌生成和验证
- **passlib** - 密码哈希和验证
- **bcrypt** - 密码加密算法
- **python-multipart** - 处理表单数据和文件上传

### 2.3 通信和异步功能

- **WebSockets** - FastAPI 内置 WebSocket 支持
- **redis** - 缓存和会话存储
- **celery** - 可选的分布式任务队列

### 2.4 测试和文档

- **pytest** - 测试框架
- **pytest-asyncio** - 异步测试支持
- **httpx** - 异步 HTTP 客户端，用于测试
- **Swagger/OpenAPI** - API 文档自动生成

## 3. 详细目录结构

```
/backend
├── alembic/                 # 数据库迁移配置
│   ├── versions/            # 数据库版本迁移脚本
│   └── env.py               # 迁移环境配置
├── app/                     # 应用主目录
│   ├── api/                 # API 接口层
│   │   ├── deps.py          # API 依赖项(认证、权限)
│   │   └── v1/              # API v1 版本
│   │       ├── endpoints/   # API 端点
│   │       │   ├── auth.py          # 认证相关
│   │       │   ├── users.py         # 用户管理
│   │       │   ├── roles.py         # 角色管理
│   │       │   ├── classes.py       # 班级管理
│   │       │   ├── students.py      # 学生管理
│   │       │   ├── quant_items.py   # 量化项目管理
│   │       │   ├── quant_records.py # 量化记录管理
│   │       │   ├── statistics.py    # 统计分析
│   │       │   ├── notifications.py # 通知管理
│   │       │   └── ai_assistant.py  # AI 助手
│   │       └── router.py    # API 路由注册
│   ├── core/                # 核心模块
│   │   ├── config.py        # 配置管理
│   │   ├── security.py      # 安全相关(JWT)
│   │   ├── events.py        # 应用事件(启动/关闭)
│   │   └── permissions.py   # 权限管理(Casbin)
│   ├── crud/                # 数据库 CRUD 操作
│   │   ├── base.py          # 基础 CRUD
│   │   ├── user.py          # 用户 CRUD
│   │   ├── role.py          # 角色 CRUD
│   │   ├── class_crud.py    # 班级 CRUD
│   │   ├── student.py       # 学生 CRUD
│   │   ├── quant_item.py    # 量化项目 CRUD
│   │   ├── quant_record.py  # 量化记录 CRUD
│   │   └── notification.py  # 通知 CRUD
│   ├── db/                  # 数据库相关
│   │   ├── base.py          # 基础配置
│   │   ├── session.py       # 会话管理
│   │   └── init_db.py       # 数据库初始化
│   ├── models/              # SQLAlchemy 模型
│   │   ├── user.py          # 用户模型
│   │   ├── role.py          # 角色模型
│   │   ├── class_model.py   # 班级模型
│   │   ├── student.py       # 学生模型
│   │   ├── quant_item.py    # 量化项目模型
│   │   ├── quant_record.py  # 量化记录模型
│   │   └── notification.py  # 通知模型
│   ├── schemas/             # Pydantic 模型(验证、序列化)
│   │   ├── auth.py          # 认证 Schema
│   │   ├── user.py          # 用户 Schema
│   │   ├── role.py          # 角色 Schema
│   │   ├── class_schema.py  # 班级 Schema
│   │   ├── student.py       # 学生 Schema
│   │   ├── quant_item.py    # 量化项目 Schema
│   │   ├── quant_record.py  # 量化记录 Schema
│   │   ├── notification.py  # 通知 Schema
│   │   └── common.py        # 通用 Schema
│   ├── services/            # 业务逻辑服务
│   │   ├── auth.py          # 认证服务
│   │   ├── statistics.py    # 统计服务
│   │   ├── ai_service.py    # AI 助手服务
│   │   └── notification.py  # 通知服务
│   ├── utils/               # 工具函数
│   │   ├── logging.py       # 日志工具
│   │   ├── security.py      # 安全工具
│   │   └── statistics.py    # 统计计算工具
│   ├── websockets/          # WebSocket 处理
│   │   ├── connection.py    # 连接管理
│   │   ├── notifications.py # 通知 WebSocket
│   │   └── ai_assistant.py  # AI 助手 WebSocket
│   └── main.py              # 应用入口
├── tests/                   # 测试
│   ├── conftest.py          # 测试配置
│   ├── api/                 # API 测试
│   ├── services/            # 服务测试
│   └── utils/               # 工具测试
├── pyproject.toml           # 项目依赖管理
├── .env.example             # 环境变量示例
├── Dockerfile               # Docker 配置
├── docker-compose.yml       # Docker Compose 配置
└── README.md                # 项目说明
```

## 4. API 设计规范

### 4.1 通用原则

- 使用 RESTful 设计风格
- API 版本控制 (/api/v1/...)
- 一致的 URL 命名：使用复数名词、kebab-case 格式
- 标准 HTTP 状态码和方法语义
- 结构化错误响应
- 分页、排序、过滤支持
- API 文档自动生成 (Swagger/ReDoc)

### 4.2 响应格式

成功响应：
```json
{
  "data": {
    // 实际数据
  },
  "meta": {
    "pagination": {
      "page": 1,
      "size": 10,
      "total": 100
    }
  }
}
```

错误响应：
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": {
      // 错误详情，可选
    }
  }
}
```

### 4.3 核心 API 端点详情

#### 认证 API

| 端点                   | 方法 | 描述                   | 请求体                             | 响应                    | 状态码 |
|------------------------|------|------------------------|-----------------------------------|--------------------------|-------|
| /api/v1/auth/login     | POST | 用户登录               | {username, password}             | {access_token, token_type} | 200   |
| /api/v1/auth/refresh   | POST | 刷新 Token             | {refresh_token}                  | {access_token, token_type} | 200   |

#### 用户管理 API

| 端点                   | 方法   | 描述                  | 请求体                                    | 响应                    | 状态码 |
|------------------------|--------|----------------------|------------------------------------------|--------------------------|-------|
| /api/v1/users          | GET    | 获取用户列表         | -                                        | {data: [用户列表], meta} | 200   |
| /api/v1/users          | POST   | 创建用户             | {username, full_name, password, role_id} | {data: 用户信息}         | 201   |
| /api/v1/users/{id}     | GET    | 获取单个用户         | -                                        | {data: 用户信息}         | 200   |
| /api/v1/users/{id}     | PUT    | 更新用户             | {username?, full_name?, role_id?}       | {data: 用户信息}         | 200   |
| /api/v1/users/{id}     | DELETE | 删除用户             | -                                        | -                        | 204   |

#### 量化记录 API

| 端点                         | 方法   | 描述                    | 请求体                                       | 响应                      | 状态码 |
|------------------------------|--------|------------------------|---------------------------------------------|----------------------------|--------|
| /api/v1/quant-records        | GET    | 获取量化记录列表       | -                                           | {data: [记录列表], meta}   | 200    |
| /api/v1/quant-records        | POST   | 创建量化记录           | {student_id, item_id, score, reason}        | {data: 记录信息}           | 201    |
| /api/v1/quant-records/batch  | POST   | 批量创建量化记录       | [{student_id, item_id, score, reason}, ...] | {data: {created: 数量}}    | 201    |
| /api/v1/quant-records/{id}   | GET    | 获取单个量化记录       | -                                           | {data: 记录信息}           | 200    |
| /api/v1/quant-records/{id}   | PUT    | 更新量化记录           | {score?, reason?}                           | {data: 记录信息}           | 200    |
| /api/v1/quant-records/{id}   | DELETE | 删除量化记录           | -                                           | -                          | 204    |

### 4.4 WebSocket API 设计

#### 通知 WebSocket

- **端点**: /ws/notifications/{user_id}
- **认证**: 通过查询参数 `token` 传递 JWT
- **消息格式**:
  - 服务器 -> 客户端:
    ```json
    {
      "type": "notification",
      "data": {
        "id": "notification_id",
        "title": "通知标题",
        "content": "通知内容",
        "created_at": "2023-07-01T12:34:56Z"
      }
    }
    ```
  - 客户端 -> 服务器 (确认)
    ```json
    {
      "type": "ack",
      "notification_id": "notification_id"
    }
    ```

#### AI 助手 WebSocket

- **端点**: /ws/ai-assistant/{user_id}
- **认证**: 通过查询参数 `token` 传递 JWT
- **消息格式**:
  - 客户端 -> 服务器 (查询):
    ```json
    {
      "type": "query",
      "data": {
        "query_text": "用户查询文本"
      }
    }
    ```
  - 服务器 -> 客户端 (响应):
    ```json
    {
      "type": "response",
      "data": {
        "response_text": "AI响应文本",
        "data": { /* 可选的数据，如图表数据 */ }
      }
    }
    ```

## 5. 数据库模型详细设计

### 5.1 核心模型定义

#### 用户模型 (User)

```python
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, func
from sqlalchemy.orm import relationship

from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # 关系
    role = relationship("Role", back_populates="users")
    class_ = relationship("Class", back_populates="users")
    quant_records_created = relationship("QuantRecord", back_populates="recorder")
    notifications_sent = relationship("Notification", back_populates="sender", foreign_keys="Notification.sender_id")
    notifications_received = relationship("Notification", back_populates="recipient_user", foreign_keys="Notification.recipient_user_id")
    ai_queries = relationship("AIQuery", back_populates="user")
```

#### 量化记录模型 (QuantRecord)

```python
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Date, Numeric, Text, func
from sqlalchemy.orm import relationship

from app.db.base import Base

class QuantRecord(Base):
    __tablename__ = "quant_records"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    item_id = Column(Integer, ForeignKey("quant_items.id"), nullable=False, index=True)
    score = Column(Numeric(5, 2), nullable=False)
    reason = Column(Text, nullable=True)
    recorder_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    record_date = Column(Date, nullable=False, index=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # 关系
    student = relationship("Student", back_populates="quant_records")
    item = relationship("QuantItem", back_populates="quant_records")
    recorder = relationship("User", back_populates="quant_records_created")
```

### 5.2 Schema 定义

#### 用户 Schema

```python
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field, SecretStr

# 共享属性
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    full_name: str = Field(..., min_length=1, max_length=100)
    is_active: bool = True

# 创建时的额外属性
class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    role_id: int
    class_id: Optional[int] = None

# 更新时的属性
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    password: Optional[str] = Field(None, min_length=8)
    role_id: Optional[int] = None
    class_id: Optional[int] = None
    is_active: Optional[bool] = None

# 数据库中查询的响应
class UserInDB(UserBase):
    id: int
    role_id: int
    class_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# API 响应
class User(UserInDB):
    pass

# 用户列表
class UserList(BaseModel):
    data: List[User]
    meta: dict
```

## 6. 权限控制方案

### 6.1 Casbin 模型配置

使用基于角色的访问控制 (RBAC) 模型，并结合资源和动作。

```
# rbac_model.conf
[request_definition]
r = sub, obj, act

[policy_definition]
p = sub, obj, act

[role_definition]
g = _, _

[policy_effect]
e = some(where (p.eft == allow))

[matchers]
m = g(r.sub, p.sub) && (r.obj == p.obj || p.obj == '*') && (r.act == p.act || p.act == '*')
```

### 6.2 策略示例

```
# 角色继承
g, teacher, user
g, admin, user

# 管理员权限
p, admin, *, *

# 教师权限
p, teacher, /api/v1/quant-records, GET
p, teacher, /api/v1/quant-records, POST
p, teacher, /api/v1/quant-records/*, GET
p, teacher, /api/v1/quant-records/*, PUT
p, teacher, /api/v1/quant-records/*, DELETE
p, teacher, /api/v1/quant-items, GET
p, teacher, /api/v1/students, GET
p, teacher, /api/v1/students/*, GET
p, teacher, /api/v1/stats/*, GET

# 学生权限
p, student, /api/v1/quant-records, GET
p, student, /api/v1/quant-records/own, GET
p, student, /api/v1/students/own, GET
p, student, /api/v1/stats/own, GET
```

### 6.3 权限验证实现

创建 Casbin 依赖项以验证 API 请求：

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import ALGORITHM
from app.crud.user import get_user_by_id
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import TokenPayload

# 初始化 Casbin 强制器
async def get_enforcer():
    from casbin_sqlalchemy_adapter import Adapter
    from casbin import AsyncEnforcer

    adapter = Adapter(settings.DATABASE_URI)
    enforcer = AsyncEnforcer(settings.CASBIN_MODEL_PATH, adapter)
    await enforcer.load_policy()
    return enforcer

# 验证权限
async def check_permission(user_id: int, path: str, method: str, enforcer = Depends(get_enforcer)):
    # 获取用户角色
    # 此处简化，实际应从数据库获取用户角色
    user_role = "admin"  # 示例
    
    has_permission = await enforcer.enforce(user_role, path, method)
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return True
```

## 7. WebSocket 实现设计

### 7.1 通知 WebSocket 管理器

```python
from fastapi import WebSocket
from typing import Dict, List

class NotificationConnectionManager:
    def __init__(self):
        # 存储活跃连接，按用户 ID 分组
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_notification(self, user_id: int, message: dict):
        if user_id in self.active_connections:
            disconnected_websockets = []
            for websocket in self.active_connections[user_id]:
                try:
                    await websocket.send_json(message)
                except Exception:
                    disconnected_websockets.append(websocket)
            
            # 清理断开的连接
            for websocket in disconnected_websockets:
                self.disconnect(websocket, user_id)

    async def broadcast(self, message: dict):
        for user_id in list(self.active_connections.keys()):
            await self.send_notification(user_id, message)


# 创建全局连接管理器实例
notification_manager = NotificationConnectionManager()
```

### 7.2 通知 WebSocket 路由实现

```python
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from jose import jwt, JWTError

from app.core.config import settings
from app.core.security import ALGORITHM
from app.schemas.auth import TokenPayload
from app.websockets.connection import notification_manager

router = APIRouter()

@router.websocket("/ws/notifications/{user_id}")
async def websocket_notifications(
    websocket: WebSocket,
    user_id: int,
    token: str = Query(...),
):
    try:
        # 验证 token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        
        # 验证用户身份匹配
        if token_data.sub != str(user_id):
            await websocket.close(code=1008)  # Policy violation
            return
        
        # 接受连接
        await notification_manager.connect(websocket, user_id)
        
        try:
            while True:
                # 处理来自客户端的消息
                data = await websocket.receive_json()
                
                # 处理确认消息
                if data.get("type") == "ack" and "notification_id" in data:
                    # 实现逻辑：将通知标记为已读
                    pass
        except WebSocketDisconnect:
            notification_manager.disconnect(websocket, user_id)
    except JWTError:
        await websocket.close(code=1008)  # Policy violation
        return
```

## 8. 开发流程与步骤

### 8.1 技术预研与环境搭建 (1周)

- 设置项目结构
- 安装和配置依赖库
- 设置数据库连接
- 配置 Git 仓库
- 搭建本地开发环境
- 编写配置管理代码

### 8.2 核心框架开发 (2周)

- 用户认证与鉴权
  - JWT 认证实现
  - Casbin 权限控制集成
  - 用户模型和 CRUD 操作
- 数据库模型定义
  - 设计所有数据库模型
  - 编写数据库迁移脚本
  - 实现基础 CRUD 操作
- 项目脚手架搭建
  - 编写 API 依赖项
  - 错误处理中间件
  - 日志和监控配置

### 8.3 核心功能模块开发 (3周)

- 系统设置模块
  - 班级管理 API
  - 用户管理 API
  - 角色管理 API
- 量化管理模块
  - 量化项目 API
  - 量化记录 API
- WebSocket 服务
  - 通知 WebSocket 实现
  - AI 助手 WebSocket 实现
- 统计分析模块
  - 多维度统计实现
  - 数据导出功能

### 8.4 功能测试与优化 (2周)

- 编写单元测试
- 编写集成测试
- 性能测试与优化
- 安全审计与修复
- API 文档完善

### 8.5 部署与发布准备 (1周)

- Docker 构建配置
- CI/CD 流水线设置
- 环境变量和配置管理
- 部署文档编写
- 数据库迁移脚本测试

## 9. 测试计划

### 9.1 单元测试

针对以下模块编写单元测试：
- 业务逻辑服务
- 工具函数
- Pydantic 模型验证
- 权限验证

使用 pytest 和 pytest-asyncio 进行测试，目标代码覆盖率 > 80%。

### 9.2 集成测试

针对 API 端点进行集成测试，验证：
- API 响应格式和状态码
- 数据库交互正确性
- 权限控制有效性
- WebSocket 连接和消息处理

使用测试数据库和测试客户端 (httpx) 进行测试。

### 9.3 性能测试

- API 响应时间测试
- 并发连接测试
- 数据库查询性能测试
- WebSocket 连接稳定性测试

使用 locust 或类似工具进行负载测试。

## 10. 部署计划

### 10.1 Docker 部署

使用 Docker 和 Docker Compose 进行部署：

```yaml
# docker-compose.yml 示例
version: '3.8'

services:
  db:
    image: mysql:8.0
    volumes:
      - db_data:/var/lib/mysql
    env_file:
      - ./.env
    networks:
      - backend-network

  backend:
    build: ./backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
    env_file:
      - ./.env
    networks:
      - backend-network

  nginx:
    image: nginx:1.21
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/conf:/etc/nginx/conf.d
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - backend
    networks:
      - backend-network

networks:
  backend-network:

volumes:
  db_data:
```

### 10.2 可扩展性考虑

- 使用 Gunicorn 作为 ASGI 服务器，提高生产环境性能
- 配置 NGINX 作为反向代理，处理 SSL 和负载均衡
- 考虑使用 Redis 缓存频繁访问的数据
- 考虑使用消息队列处理异步任务和通知发送

### 10.3 监控与日志

- 使用 Prometheus 和 Grafana 监控系统性能
- 集成应用程序日志到 ELK 或类似的日志管理系统
- 实现健康检查端点，用于监控服务状态
- 设置自动报警机制，及时发现问题

## 11. 安全考虑

### 11.1 数据安全

- 所有密码使用 bcrypt 加密存储
- 敏感配置使用环境变量，不硬编码
- 数据库定期备份，确保数据安全
- 实现数据访问控制，防止未授权访问

### 11.2 API 安全

- 使用 HTTPS 加密所有通信
- 实现请求速率限制，防止暴力破解
- 添加 CORS 配置，限制跨域请求
- 实现 SQL 注入和 XSS 攻击防护
- 使用安全的依赖项，定期更新

## 12. 依赖管理

```toml
# pyproject.toml
[project]
name = "auraclass-backend"
version = "0.1.0"
description = "AuraClass 班级量化管理软件后端"
requires-python = ">=3.10"
dependencies = [
    "fastapi>=0.100.0",
    "uvicorn[standard]>=0.22.0",
    "sqlalchemy>=2.0.0",
    "alembic>=1.11.1",
    "asyncpg>=0.27.0",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "casbin>=1.24.0",
    "casbin-sqlalchemy-adapter>=0.4.1",
    "pydantic>=2.0.0",
    "python-multipart>=0.0.6",
    "python-dotenv>=1.0.0",
    "redis>=4.6.0",
    "httpx>=0.24.1"
]

[project.optional-dependencies]
dev = [
    "pytest>=7.3.1",
    "pytest-asyncio>=0.21.0",
    "black>=23.3.0",
    "isort>=5.12.0",
    "mypy>=1.3.0",
    "pylint>=2.17.4"
]

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
asyncio_mode = "auto"

[tool.mypy]
python_version = "3.10"
strict = true
plugins = [
    "pydantic.mypy"
]

[tool.black]
line-length = 88
target-version = ['py310']

[tool.isort]
profile = "black"
line_length = 88
```

## 13. 结语

本文档详细介绍了 AuraClass 班级量化管理软件后端系统的设计和实现方案。后端采用 FastAPI 框架，结合异步 SQLAlchemy、Casbin 权限控制和 WebSocket 通信，构建高性能、可扩展的班级量化管理系统。

开发将按照上述计划分阶段进行，确保系统稳定、安全和高效。随着项目的进展，可能会对本文档进行更新和细化，以适应实际开发需求。




