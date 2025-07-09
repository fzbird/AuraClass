
# AuraClass 班级量化管理软件项目开发文档

## 1. 项目概述

AuraClass是一款班级量化管理辅助软件，旨在提升教师和班级管理员对班级的管理效率和数据洞察能力。通过便捷的信息录入、清晰的数据展示、智能的统计分析以及AI助手功能，帮助用户更科学、高效地进行班级量化管理。

## 2. 系统架构

### 2.1 整体架构

```
+-------------------+       +------------------+       +-----------------+
|   桌面客户端      | ----> |    Web前端       | <---> |    后端API      |
| (Electron包装)    |       | (Vue3 + NativeUI)|       |   (FastAPI)     |
+-------------------+       +------------------+       +--------+--------+
                            |                                    |
+-------------------+       |                            +-------v--------+
|   移动客户端      | ----> |                            |     MySQL      |
|    (Android)      |                                    |    数据库      |
+-------------------+                                    +----------------+
                                                         |    Casbin      |
                                                         |  (策略存储)    |
                                                         +----------------+
```

### 2.2 后端架构

- **框架**: FastAPI提供高性能异步API接口
- **ORM**: 异步SQLAlchemy用于数据库交互，Alembic用于数据库迁移
- **权限控制**: Casbin实现RBAC权限控制
- **认证**: JWT (JSON Web Tokens)进行用户认证
- **实时通信**: WebSocket实现实时通知和AI助手交互
- **数据库**: MySQL 8.0+

### 2.3 前端架构

- **框架**: Vue 3 (Composition API)
- **UI组件**: Native UI提供现代化组件
- **状态管理**: Pinia管理应用状态
- **路由**: Vue Router管理页面导航
- **数据可视化**: ECharts绘制统计图表
- **API通信**: Axios发送HTTP请求，原生WebSocket处理实时通信

### 2.4 桌面端架构

- **技术框架**: Electron包装Web前端
- **更新机制**: electron-updater实现自动更新
- **系统集成**: 原生通知、系统托盘

### 2.5 移动端架构

- **技术选型**: 使用Capacitor包装Web前端生成Android应用
- **原生功能**: 通知推送、摄像头访问、文件系统访问
- **离线存储**: IndexedDB + 本地SQLite同步

## 3. 详细数据库设计

### 3.1 数据库表结构

#### users (用户表)
| 字段名 | 类型 | 约束 | 说明 |
|-------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 用户ID |
| username | VARCHAR(50) | UNIQUE, NOT NULL | 用户名 |
| password_hash | VARCHAR(255) | NOT NULL | 密码哈希 |
| full_name | VARCHAR(100) | NOT NULL | 真实姓名 |
| role_id | INT | FK, NOT NULL | 角色ID |
| class_id | INT | FK, NULL | 关联班级ID |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | 是否激活 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

#### roles (角色表)
| 字段名 | 类型 | 约束 | 说明 |
|-------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 角色ID |
| name | VARCHAR(50) | UNIQUE, NOT NULL | 角色名称 |
| description | VARCHAR(255) | NULL | 角色描述 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 创建时间 |

#### casbin_rule (Casbin策略表)
| 字段名 | 类型 | 约束 | 说明 |
|-------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 规则ID |
| ptype | VARCHAR(255) | NOT NULL | 策略类型 |
| v0 | VARCHAR(255) | NULL | 主体(角色) |
| v1 | VARCHAR(255) | NULL | 资源 |
| v2 | VARCHAR(255) | NULL | 行为 |
| v3 | VARCHAR(255) | NULL | 扩展1 |
| v4 | VARCHAR(255) | NULL | 扩展2 |
| v5 | VARCHAR(255) | NULL | 扩展3 |

#### classes (班级表)
| 字段名 | 类型 | 约束 | 说明 |
|-------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 班级ID |
| name | VARCHAR(50) | NOT NULL | 班级名称 |
| grade | VARCHAR(20) | NOT NULL | 年级 |
| year | INT | NOT NULL | 学年 |
| head_teacher_id | INT | FK->users, NULL | 班主任ID |
| created_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

#### students (学生表)
| 字段名 | 类型 | 约束 | 说明 |
|-------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 学生ID |
| user_id | INT | FK->users, NULL | 关联用户ID |
| student_id_no | VARCHAR(50) | UNIQUE, NOT NULL | 学号 |
| full_name | VARCHAR(100) | NOT NULL | 姓名 |
| class_id | INT | FK->classes, NOT NULL | 班级ID |
| gender | VARCHAR(10) | NOT NULL | 性别 |
| birth_date | DATE | NULL | 出生日期 |
| contact_info | VARCHAR(255) | NULL | 联系信息 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

#### quant_items (量化项目表)
| 字段名 | 类型 | 约束 | 说明 |
|-------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 项目ID |
| name | VARCHAR(100) | NOT NULL | 项目名称 |
| description | TEXT | NULL | 项目描述 |
| default_score | DECIMAL(5,2) | NOT NULL | 默认分值 |
| category | VARCHAR(50) | NOT NULL | 分类(纪律/卫生/学习等) |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | 是否启用 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

#### quant_records (量化记录表)
| 字段名 | 类型 | 约束 | 说明 |
|-------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 记录ID |
| student_id | INT | FK->students, NOT NULL | 学生ID |
| item_id | INT | FK->quant_items, NOT NULL | 量化项目ID |
| score | DECIMAL(5,2) | NOT NULL | 得分 |
| reason | TEXT | NULL | 原因描述 |
| recorder_id | INT | FK->users, NOT NULL | 记录者ID |
| record_date | DATE | NOT NULL | 记录日期 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

#### notifications (通知表)
| 字段名 | 类型 | 约束 | 说明 |
|-------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 通知ID |
| title | VARCHAR(255) | NOT NULL | 标题 |
| content | TEXT | NOT NULL | 内容 |
| recipient_user_id | INT | FK->users, NULL | 接收用户ID |
| recipient_role_id | INT | FK->roles, NULL | 接收角色ID |
| recipient_class_id | INT | FK->classes, NULL | 接收班级ID |
| sender_id | INT | FK->users, NOT NULL | 发送者ID |
| created_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| is_read | BOOLEAN | NOT NULL, DEFAULT FALSE | 是否已读 |

#### ai_queries (AI查询记录表)
| 字段名 | 类型 | 约束 | 说明 |
|-------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 查询ID |
| user_id | INT | FK->users, NOT NULL | 用户ID |
| query_text | TEXT | NOT NULL | 查询文本 |
| response_text | TEXT | NULL | 响应文本 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| status | VARCHAR(20) | NOT NULL | 处理状态 |

### 3.2 索引设计

```sql
-- users表索引
CREATE INDEX idx_users_role_id ON users(role_id);
CREATE INDEX idx_users_class_id ON users(class_id);

-- students表索引
CREATE INDEX idx_students_class_id ON students(class_id);
CREATE INDEX idx_students_user_id ON students(user_id);
CREATE INDEX idx_students_name ON students(full_name);

-- quant_records表索引
CREATE INDEX idx_quant_records_student_id ON quant_records(student_id);
CREATE INDEX idx_quant_records_item_id ON quant_records(item_id);
CREATE INDEX idx_quant_records_recorder_id ON quant_records(recorder_id);
CREATE INDEX idx_quant_records_date ON quant_records(record_date);
CREATE INDEX idx_quant_records_composite ON quant_records(student_id, item_id, record_date);

-- notifications表索引
CREATE INDEX idx_notifications_recipient_user ON notifications(recipient_user_id);
CREATE INDEX idx_notifications_recipient_role ON notifications(recipient_role_id);
CREATE INDEX idx_notifications_recipient_class ON notifications(recipient_class_id);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);
```

### 3.3 数据库关系图

```
roles <---- users ----> classes
  ^          |            ^
  |          |            |
  |          v            |
Casbin     students <-----+
          /    |
         /     |
        v      v
notifications  quant_records
                    ^
                    |
                    |
                quant_items
```

## 4. 项目结构设计

### 4.1 后端目录结构

```
/backend
├── alembic/                 # 数据库迁移配置
│   ├── versions/            # 数据库版本迁移脚本
│   └── env.py               # 迁移环境配置
├── app/                     # 应用主目录
│   ├── api/                 # API接口层
│   │   ├── v1/              # API v1版本
│   │   │   ├── endpoints/   # API端点
│   │   │   │   ├── auth.py          # 认证相关
│   │   │   │   ├── users.py         # 用户管理
│   │   │   │   ├── classes.py       # 班级管理
│   │   │   │   ├── students.py      # 学生管理
│   │   │   │   ├── quant_items.py   # 量化项目管理
│   │   │   │   ├── quant_records.py # 量化记录管理
│   │   │   │   ├── statistics.py    # 统计分析
│   │   │   │   ├── notifications.py # 通知管理
│   │   │   │   └── ai_assistant.py  # AI助手
│   │   │   ├── router.py    # API路由注册
│   │   │   └── dependencies.py # API依赖项
│   │   └── deps.py         # 通用依赖项
│   ├── core/               # 核心模块
│   │   ├── config.py       # 配置管理
│   │   ├── security.py     # 安全相关(JWT等)
│   │   └── permissions.py  # 权限管理(Casbin)
│   ├── crud/               # 数据库CRUD操作
│   │   ├── base.py         # 基础CRUD
│   │   ├── users.py        # 用户CRUD
│   │   ├── classes.py      # 班级CRUD
│   │   └── ...            # 其他实体CRUD
│   ├── db/                 # 数据库相关
│   │   ├── base.py         # 基础配置
│   │   ├── session.py      # 会话管理
│   │   └── init_db.py      # 数据库初始化
│   ├── models/             # SQLAlchemy模型
│   │   ├── user.py         # 用户模型
│   │   ├── role.py         # 角色模型
│   │   ├── class.py        # 班级模型
│   │   └── ...            # 其他模型
│   ├── schemas/            # Pydantic模型(验证、序列化)
│   │   ├── user.py         # 用户Schema
│   │   ├── class.py        # 班级Schema
│   │   └── ...            # 其他Schema
│   ├── services/           # 业务逻辑服务
│   │   ├── auth.py         # 认证服务
│   │   ├── statistics.py   # 统计服务
│   │   ├── ai_service.py   # AI助手服务
│   │   └── ...            # 其他服务
│   ├── utils/              # 工具函数
│   │   ├── logging.py      # 日志工具
│   │   └── ...            # 其他工具
│   ├── websockets/         # WebSocket处理
│   │   ├── connection.py   # 连接管理
│   │   ├── notifications.py # 通知WebSocket
│   │   └── ai_assistant.py # AI助手WebSocket
│   └── main.py             # 应用入口
├── tests/                  # 测试
│   ├── conftest.py         # 测试配置
│   ├── api/                # API测试
│   ├── services/           # 服务测试
│   └── ...                # 其他测试
├── .env                    # 环境变量
├── alembic.ini             # Alembic配置
├── pyproject.toml          # 项目依赖
├── Dockerfile              # Docker配置
├── docker-compose.yml      # Docker Compose配置
└── README.md               # 项目说明
```

### 4.2 前端Web目录结构

```
/frontend
├── public/                # 静态资源
│   ├── favicon.ico        # 网站图标
│   └── ...
├── src/                   # 源代码
│   ├── api/               # API调用
│   │   ├── index.js       # API基础配置
│   │   ├── auth.js        # 认证API
│   │   ├── users.js       # 用户API
│   │   └── ...           # 其他API模块
│   ├── assets/            # 静态资源
│   │   ├── images/        # 图片
│   │   ├── styles/        # 样式
│   │   └── ...
│   ├── components/        # 公共组件
│   │   ├── common/        # 通用组件
│   │   ├── layout/        # 布局组件
│   │   ├── charts/        # 图表组件
│   │   └── ...
│   ├── composables/       # 组合函数
│   │   ├── useAuth.js     # 认证相关
│   │   ├── useWebSocket.js # WebSocket处理
│   │   └── ...
│   ├── router/            # 路由
│   │   ├── index.js       # 路由配置
│   │   ├── routes/        # 路由模块
│   │   └── guards.js      # 路由守卫
│   ├── stores/            # Pinia状态管理
│   │   ├── auth.js        # 认证状态
│   │   ├── user.js        # 用户状态
│   │   └── ...
│   ├── utils/             # 工具函数
│   │   ├── request.js     # HTTP请求封装
│   │   ├── websocket.js   # WebSocket封装
│   │   └── ...
│   ├── views/             # 页面视图
│   │   ├── auth/          # 认证相关页面
│   │   ├── dashboard/     # 仪表盘
│   │   ├── system/        # 系统管理
│   │   ├── quant/         # 量化管理
│   │   ├── statistics/    # 统计分析
│   │   └── ...
│   ├── App.vue            # 根组件
│   ├── main.js            # 入口文件
│   └── env.js             # 环境配置
├── .env.development       # 开发环境变量
├── .env.production        # 生产环境变量
├── index.html             # HTML模板
├── vite.config.js         # Vite配置
├── package.json           # 项目依赖
└── README.md              # 项目说明
```

### 4.3 桌面端目录结构

```
/desktop
├── electron/              # Electron相关
│   ├── main.js            # 主进程
│   ├── preload.js         # 预加载脚本
│   └── menu.js            # 菜单配置
├── build/                 # 构建相关
│   ├── icons/             # 应用图标
│   ├── installer.nsh      # 安装脚本
│   └── entitlements.mac.plist # macOS权限
├── dist/                  # 构建输出目录
├── node_modules/          # 依赖
├── src/                   # 源代码(与前端共享)
├── package.json           # 项目配置
├── .electron-builder.config.js # Electron构建配置
└── README.md              # 项目说明
```

### 4.4 移动端目录结构

```
/mobile
├── android/               # Android原生代码
│   ├── app/               # Android应用
│   │   ├── src/           # 源代码
│   │   └── build.gradle   # 构建配置
│   ├── gradle/            # Gradle配置
│   └── build.gradle       # 项目构建配置
├── capacitor.config.ts    # Capacitor配置
├── resources/             # 资源文件(图标等)
├── src/                   # Web源代码(与前端共享)
├── package.json           # 项目配置
└── README.md              # 项目说明
```

## 5. API设计

### 5.1 认证与授权

```
POST /api/v1/auth/login           # 用户登录
POST /api/v1/auth/refresh         # 刷新Token
POST /api/v1/auth/logout          # 用户登出
GET  /api/v1/auth/me              # 获取当前用户信息
```

### 5.2 用户管理

```
GET    /api/v1/users              # 获取用户列表
POST   /api/v1/users              # 创建用户
GET    /api/v1/users/{id}         # 获取单个用户
PUT    /api/v1/users/{id}         # 更新用户
DELETE /api/v1/users/{id}         # 删除用户
PATCH  /api/v1/users/{id}/active  # 启用/禁用用户
```

### 5.3 角色管理

```
GET    /api/v1/roles              # 获取角色列表
POST   /api/v1/roles              # 创建角色
GET    /api/v1/roles/{id}         # 获取单个角色
PUT    /api/v1/roles/{id}         # 更新角色
DELETE /api/v1/roles/{id}         # 删除角色
GET    /api/v1/roles/{id}/permissions # 获取角色权限
POST   /api/v1/roles/{id}/permissions # 设置角色权限
```

### 5.4 班级管理

```
GET    /api/v1/classes            # 获取班级列表
POST   /api/v1/classes            # 创建班级
GET    /api/v1/classes/{id}       # 获取单个班级
PUT    /api/v1/classes/{id}       # 更新班级
DELETE /api/v1/classes/{id}       # 删除班级
GET    /api/v1/classes/{id}/students # 获取班级学生
```

### 5.5 学生管理

```
GET    /api/v1/students           # 获取学生列表
POST   /api/v1/students           # 创建学生
GET    /api/v1/students/{id}      # 获取单个学生
PUT    /api/v1/students/{id}      # 更新学生
DELETE /api/v1/students/{id}      # 删除学生
GET    /api/v1/students/{id}/records # 获取学生量化记录
```

### 5.6 量化项目管理

```
GET    /api/v1/quant-items        # 获取量化项目列表
POST   /api/v1/quant-items        # 创建量化项目
GET    /api/v1/quant-items/{id}   # 获取单个量化项目
PUT    /api/v1/quant-items/{id}   # 更新量化项目
DELETE /api/v1/quant-items/{id}   # 删除量化项目
PATCH  /api/v1/quant-items/{id}/active # 启用/禁用量化项目
```

### 5.7 量化记录管理

```
GET    /api/v1/quant-records      # 获取量化记录列表
POST   /api/v1/quant-records      # 创建量化记录
POST   /api/v1/quant-records/batch # 批量创建量化记录
GET    /api/v1/quant-records/{id} # 获取单个量化记录
PUT    /api/v1/quant-records/{id} # 更新量化记录
DELETE /api/v1/quant-records/{id} # 删除量化记录
```

### 5.8 统计分析

```
GET    /api/v1/stats/summary      # 获取总体统计概览
GET    /api/v1/stats/by-student   # 按学生统计
GET    /api/v1/stats/by-item      # 按项目统计
GET    /api/v1/stats/by-class     # 按班级统计
GET    /api/v1/stats/timeseries   # 时间序列统计
GET    /api/v1/stats/top-students # 获取学生排名
GET    /api/v1/stats/export       # 导出统计数据
```

### 5.9 通知管理

```
GET    /api/v1/notifications          # 获取通知列表
POST   /api/v1/notifications          # 创建通知
GET    /api/v1/notifications/{id}     # 获取单个通知
PATCH  /api/v1/notifications/{id}/read # 标记通知为已读
DELETE /api/v1/notifications/{id}     # 删除通知
```

### 5.10 WebSocket API

```
WS    /ws/notifications           # 通知WebSocket连接
WS    /ws/ai-assistant           # AI助手WebSocket连接
```

## 6. Windows桌面端方案

### 6.1 技术方案

- 使用Electron包装Web前端
- 使用electron-builder进行打包
- Node.js集成提供本地功能

### 6.2 功能特性

- **系统集成**:
  - 系统托盘图标
  - 开机自启动
  - 原生通知集成
  - 快捷键支持

- **本地存储**:
  - SQLite作为本地缓存数据库
  - 断网状态下基本功能可用
  - 数据自动同步

- **性能优化**:
  - 渲染进程和主进程分离
  - 主要计算在主进程中完成
  - 资源占用监控与优化

### 6.3 更新机制

- 基于electron-updater实现自动更新
- 支持增量更新
- 后台静默下载，提示安装

### 6.4 安装包构建

- 使用NSIS创建Windows安装程序
- 支持安装过程自定义
- 提供数字证书签名

## 7. Android移动端方案

### 7.1 技术方案

- 使用Capacitor包装Web前端
- WebView渲染核心界面
- 原生插件提供设备功能访问

### 7.2 功能特性

- **设备集成**:
  - 推送通知
  - 摄像头(扫码录入)
  - 地理位置(考勤)
  - 文件系统访问

- **本地存储**:
  - SQLite本地数据库
  - 离线模式支持
  - 数据同步机制

- **界面适配**:
  - 响应式布局
  - 触控优化
  - 手势操作

### 7.3 性能优化

- 资源预加载
- 图片懒加载
- 本地缓存管理
- WebView性能调优

### 7.4 发布部署

- Google Play Store发布
- 内部测试渠道
- CI/CD自动化构建
- 热更新支持

## 8. 安全策略

### 8.1 认证安全

- 强密码策略
- JWT Token安全
- 会话管理
- 登录限制和锁定

### 8.2 授权安全

- Casbin精细化权限控制
- 数据访问控制
- API权限验证
- 敏感操作审计

### 8.3 数据安全

- 传输加密(HTTPS)
- 敏感数据存储加密
- 数据备份策略
- 日志记录与审计

### 8.4 API安全

- 输入验证
- 防SQL注入
- 防XSS攻击
- 速率限制

## 9. 部署方案

### 9.1 后端部署

```
                       +-----------------+
                       |     负载均衡    |
                       |     (Nginx)     |
                       +--------+--------+
                                |
              +----------------+----------------+
              |                                 |
     +--------v--------+               +--------v--------+
     |    FastAPI      |               |    FastAPI      |
     |    (Docker)     |               |    (Docker)     |
     +--------+--------+               +--------+--------+
              |                                 |
              |                                 |
     +--------v--------+               +--------v--------+
     |    MySQL主      |<------------->|    MySQL从      |
     |    (Docker)     |               |    (Docker)     |
     +-----------------+               +-----------------+
```

### 9.2 前端部署

- 静态资源部署到CDN
- 支持前端缓存策略
- 启用GZIP/Brotli压缩
- 部署流程自动化

### 9.3 CI/CD流水线

- 代码提交触发自动构建
- 单元测试和集成测试自动运行
- 测试通过后自动部署到测试环境
- 手动确认后部署到生产环境
- 自动生成版本发布日志

## 10. 开发时间线

### 10.1 阶段一：基础架构与认证(1-2周)

- 环境搭建
- 项目初始化
- 数据库设计与迁移
- 认证与权限框架

### 10.2 阶段二：核心模块开发(3-6周)

- 系统设置模块
- 量化项目管理
- 量化信息管理
- 基本统计功能

### 10.3 阶段三：前端界面与统计(6-8周)

- 核心界面开发
- 高级统计与图表
- WebSocket通信
- 前端数据可视化

### 10.4 阶段四：客户端与AI助手(8-10周)

- 桌面客户端适配
- 移动客户端适配
- AI助手基础功能
- 通知系统

### 10.5 阶段五：测试与优化(11-12周)

- 集成测试
- 性能优化
- 文档完善
- 部署上线

## 11. 总结

AuraClass班级量化管理软件采用前后端分离架构，后端使用FastAPI+MySQL+异步SQLAlchemy+Casbin+WebSocket，前端使用Vue 3+Native UI+Pinia+Vue Router+ECharts，桌面端采用Electron包装，移动端采用Capacitor包装。系统功能模块包括系统设置、量化项目管理、量化信息管理、量化统计和各平台客户端。数据库设计包含8个核心表，涵盖用户、角色、班级、学生、量化项目、量化记录、通知和AI查询等实体。前后端目录结构清晰，API设计遵循RESTful风格，并提供了详细的桌面端和移动端技术方案。
