# AuraClass 班级量化管理系统

<div align="center">

![AuraClass Logo](https://img.shields.io/badge/AuraClass-班级量化管理系统-blue)
![Version](https://img.shields.io/badge/version-v0.1.0-green)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Vue](https://img.shields.io/badge/Vue-3.x-brightgreen)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

</div>

## 📖 项目简介

AuraClass是一款现代化的班级量化管理系统，旨在提升教师和班级管理员对班级的管理效率和数据洞察能力。通过便捷的信息录入、清晰的数据展示、智能的统计分析以及AI助手功能，帮助教育工作者更科学、高效地进行班级量化管理。

### ✨ 核心功能

- 🎯 **学生量化管理** - 全面的学生行为量化记录和评价
- 📊 **数据统计分析** - 多维度数据图表展示和趋势分析
- 🤖 **AI智能助手** - 基于Ollama的智能对话和数据分析助手
- 👥 **多角色权限** - 基于Casbin的RBAC权限控制系统
- 📱 **响应式设计** - 支持桌面端、移动端多平台访问
- 💬 **实时通知** - WebSocket实时消息推送系统
- 📈 **性能监控** - 全面的系统性能监控和告警

## 🏗️ 系统架构

### 整体架构图

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   前端应用      │    │     后端API      │    │    数据库       │
│   Vue 3 +       │◄──►│    FastAPI +     │◄──►│    MySQL 8.0    │
│   Naive UI      │    │   SQLAlchemy     │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                       │
         │              ┌─────────────────┐              │
         │              │   权限控制      │              │
         └──────────────│   Casbin +      │──────────────┘
                        │   RBAC          │
                        └─────────────────┘
                                 │
                      ┌─────────────────┐
                      │   AI助手服务    │
                      │   Ollama +      │
                      │   LLM Models    │
                      └─────────────────┘
```

### 技术栈

#### 后端技术栈
- **框架**: FastAPI 0.100+ (高性能异步Web框架)
- **数据库**: MySQL 8.0 + SQLAlchemy 2.0 (异步ORM)
- **数据库迁移**: Alembic (数据库版本控制)
- **权限控制**: Casbin (RBAC权限管理)
- **认证授权**: JWT (JSON Web Tokens)
- **AI服务**: Ollama (本地LLM推理)
- **实时通信**: WebSocket
- **缓存**: Redis 6.0+
- **监控**: Prometheus + Grafana
- **日志**: 结构化日志 + 文件轮转

#### 前端技术栈
- **框架**: Vue 3 (Composition API)
- **UI组件库**: Naive UI (现代化组件库)
- **状态管理**: Pinia (Vue 3状态管理)
- **路由**: Vue Router 4
- **构建工具**: Vite 6
- **HTTP客户端**: Axios
- **图表库**: ECharts 5
- **样式**: TailwindCSS + Sass
- **TypeScript**: 全面类型支持

#### 开发工具
- **代码规范**: ESLint + Prettier + Black
- **类型检查**: TypeScript + MyPy
- **测试框架**: Pytest + Vue Test Utils
- **容器化**: Docker + Docker Compose
- **CI/CD**: GitHub Actions

## 📁 项目结构

```
AuraClass/
├── backend/                    # 后端应用
│   ├── app/                   # 应用核心代码
│   │   ├── api/              # API路由
│   │   │   └── v1/           # v1版本API
│   │   │       └── endpoints/ # 具体端点实现
│   │   ├── core/             # 核心配置
│   │   ├── crud/             # 数据访问层
│   │   ├── db/               # 数据库连接
│   │   ├── models/           # 数据模型
│   │   ├── schemas/          # Pydantic模式
│   │   ├── services/         # 业务逻辑层
│   │   └── utils/            # 工具函数
│   ├── alembic/              # 数据库迁移
│   ├── tests/                # 测试用例
│   └── pyproject.toml        # Python依赖配置
├── auraclass-frontend/         # 前端应用
│   ├── public/               # 静态资源
│   ├── src/                  # 源代码
│   │   ├── components/       # Vue组件
│   │   ├── pages/           # 页面组件
│   │   ├── stores/          # Pinia状态管理
│   │   ├── services/        # API服务
│   │   ├── router/          # 路由配置
│   │   └── utils/           # 工具函数
│   └── package.json         # Node.js依赖
├── docs/                     # 项目文档
├── scripts/                  # 部署脚本
└── docker-compose.yml        # 容器编排
```

## 🚀 快速开始

### 环境要求

- **Python**: 3.10+
- **Node.js**: 18+
- **MySQL**: 8.0+
- **Redis**: 6.0+
- **Ollama**: 最新版本 (可选，用于AI功能)

### 一键启动

项目提供了一键启动脚本，可以快速启动所有服务：

```bash
# 克隆项目
git clone <repository-url>
cd AuraClass

# 赋予启动脚本执行权限
chmod +x start_all.sh

# 一键启动（会自动安装依赖并启动服务）
./start_all.sh
```

启动成功后：
- 前端服务: http://localhost:8201
- 后端服务: http://localhost:8200
- API文档: http://localhost:8200/api/docs

### 手动安装

#### 1. 后端安装

```bash
# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装后端依赖
cd backend
pip install -e .

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库连接等

# 运行数据库迁移
alembic upgrade head

# 启动后端服务
python run.py
```

#### 2. 前端安装

```bash
# 安装前端依赖
cd auraclass-frontend
npm install

# 启动开发服务器
npm run dev
```

#### 3. 数据库配置

创建MySQL数据库：

```sql
CREATE DATABASE auraclass DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'auraclass'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON auraclass.* TO 'auraclass'@'localhost';
FLUSH PRIVILEGES;
```

### 环境变量配置

在 `backend/.env` 文件中配置以下环境变量：

```env
# 基本配置
PROJECT_NAME=AuraClass
DEBUG=True
APP_ENV=development

# 安全配置
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 数据库配置
DATABASE_URL=mysql+aiomysql://username:password@localhost:3306/auraclass

# Redis配置
REDIS_URL=redis://localhost:6379/0

# CORS配置
ALLOWED_ORIGINS=http://localhost:8201,ws://localhost:8201

# AI服务配置 (可选)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL_NAME=qwen3:32b
OLLAMA_USE_THINK_MODE=true

# 文件上传配置
UPLOADS_DIR=uploads
MAX_UPLOAD_SIZE=10485760
```

## 📋 功能特性

### 🎯 核心功能模块

#### 1. 用户认证与授权
- JWT令牌认证
- 基于Casbin的RBAC权限控制
- 多角色支持（管理员、教师、学生）
- 细粒度权限控制

#### 2. 学生管理
- 学生信息维护
- 批量导入学生数据
- 学生分组管理
- 学生档案管理

#### 3. 量化项目管理
- 自定义量化项目
- 量化项目分类管理
- 分值配置和调整
- 项目启用/停用控制

#### 4. 量化记录管理
- 便捷的量化记录录入
- 批量记录操作
- 记录历史追踪
- 记录统计和查询

#### 5. 数据统计与分析
- 多维度数据统计
- 趋势图表展示
- 排名和对比分析
- 自定义报表生成

#### 6. AI智能助手
- 基于Ollama的本地AI服务
- 自然语言查询数据
- 智能数据分析建议
- 多轮对话支持

#### 7. 通知系统
- 实时WebSocket通知
- 系统消息推送
- 邮件通知(可扩展)
- 通知历史管理

#### 8. 系统监控
- API性能监控
- 系统资源监控
- 错误日志追踪
- 慢查询检测

### 🔧 管理功能

#### 1. 系统配置
- 基础参数配置
- 权限策略管理
- 系统初始化
- 数据备份恢复

#### 2. 用户管理
- 用户账号管理
- 角色权限分配
- 密码策略配置
- 登录日志查看

#### 3. 数据管理
- 数据导入导出
- 数据清理工具
- 数据统计报告
- 数据备份策略

## 🔒 权限系统

系统采用基于Casbin的RBAC权限模型：

### 角色定义
- **超级管理员**: 系统最高权限，可管理所有功能
- **学校管理员**: 管理本校所有班级和用户
- **年级主任**: 管理本年级所有班级
- **班主任**: 管理分配的班级
- **任课教师**: 查看和录入权限
- **学生**: 查看个人数据权限

### 权限策略
```
p, admin, *, *
p, school_admin, /api/v1/classes/*, *
p, grade_director, /api/v1/classes/{grade}/*, *
p, head_teacher, /api/v1/classes/{class_id}/*, *
p, teacher, /api/v1/quant-records/*, create,read
p, student, /api/v1/students/{student_id}, read
```

## 📊 数据库设计

### 核心数据表

#### 用户相关
- `users` - 用户基础信息
- `roles` - 角色定义
- `casbin_rule` - 权限策略存储

#### 业务相关
- `classes` - 班级信息
- `students` - 学生信息
- `quant_items` - 量化项目
- `quant_records` - 量化记录
- `notifications` - 通知消息
- `ai_queries` - AI查询记录

### 数据关系
```sql
-- 用户与角色的关系
users ──→ roles (多对一)

-- 班级与用户的关系
classes ──→ users (班主任，一对一)
users ──→ classes (教师可管理多个班级，多对多)

-- 学生与班级的关系
students ──→ classes (多对一)
students ──→ users (可选关联，一对一)

-- 量化记录关系
quant_records ──→ students (多对一)
quant_records ──→ quant_items (多对一)
quant_records ──→ users (记录者，多对一)
```

## 🔧 API文档

### 主要API端点

#### 认证相关
```
POST /api/v1/auth/login      # 用户登录
POST /api/v1/auth/logout     # 用户登出
POST /api/v1/auth/refresh    # 刷新令牌
GET  /api/v1/auth/me         # 获取当前用户信息
```

#### 用户管理
```
GET    /api/v1/users/               # 获取用户列表
POST   /api/v1/users/               # 创建用户
GET    /api/v1/users/{user_id}      # 获取用户详情
PUT    /api/v1/users/{user_id}      # 更新用户信息
DELETE /api/v1/users/{user_id}      # 删除用户
```

#### 学生管理
```
GET    /api/v1/students/            # 获取学生列表
POST   /api/v1/students/            # 创建学生
GET    /api/v1/students/{id}        # 获取学生详情
PUT    /api/v1/students/{id}        # 更新学生信息
DELETE /api/v1/students/{id}        # 删除学生
POST   /api/v1/students/batch       # 批量导入学生
```

#### 量化管理
```
GET    /api/v1/quant-items/         # 获取量化项目
POST   /api/v1/quant-items/         # 创建量化项目
GET    /api/v1/quant-records/       # 获取量化记录
POST   /api/v1/quant-records/       # 创建量化记录
GET    /api/v1/statistics/          # 获取统计数据
```

#### AI助手
```
POST   /api/v1/ai/chat              # AI对话
GET    /api/v1/ai/history           # 对话历史
POST   /api/v1/ai/upload            # 文件上传
```

#### WebSocket
```
WS     /ws                          # WebSocket连接
```

详细API文档请访问: http://localhost:8200/api/docs

## 🔍 使用说明

### 1. 首次登录

系统默认管理员账号：
- 用户名: `admin`
- 密码: `admin123`

首次登录后请及时修改默认密码。

### 2. 基础配置

1. **创建角色和权限**
   - 进入系统管理 → 角色管理
   - 创建需要的角色并分配权限

2. **创建班级**
   - 进入班级管理 → 新增班级
   - 填写班级基本信息

3. **导入学生**
   - 进入学生管理 → 批量导入
   - 下载模板文件，填写学生信息后上传

4. **配置量化项目**
   - 进入量化管理 → 量化项目
   - 创建各类量化项目和分值

### 3. 日常使用

1. **录入量化记录**
   - 进入量化管理 → 记录管理
   - 选择学生和量化项目录入记录

2. **查看统计分析**
   - 进入数据分析查看各类统计图表
   - 支持按时间、班级、学生等维度筛选

3. **使用AI助手**
   - 进入AI助手页面
   - 通过自然语言查询数据和获取分析建议

## 🐳 Docker部署

### 使用Docker Compose

```yaml
# docker-compose.yml
version: '3.8'
services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: auraclass
      MYSQL_USER: auraclass
      MYSQL_PASSWORD: password
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    ports:
      - "8200:8200"
    depends_on:
      - mysql
      - redis
    environment:
      - DATABASE_URL=mysql+aiomysql://auraclass:password@mysql:3306/auraclass
      - REDIS_URL=redis://redis:6379/0

  frontend:
    build: ./auraclass-frontend
    ports:
      - "8201:80"
    depends_on:
      - backend

volumes:
  mysql_data:
```

启动命令：
```bash
docker-compose up -d
```

## 📈 性能优化

### 后端优化
- 异步数据库操作
- Redis缓存热点数据
- 数据库查询优化
- API响应压缩
- 连接池管理

### 前端优化
- 组件懒加载
- 图片压缩和懒加载
- 虚拟滚动长列表
- HTTP缓存策略
- 代码分割

### 数据库优化
- 索引优化
- 分页查询
- 慢查询监控
- 读写分离支持

## 🛠️ 开发指南

### 后端开发

#### 1. 项目结构规范
```
app/
├── api/v1/endpoints/     # API端点实现
├── core/                 # 核心配置和工具
├── crud/                 # 数据访问层
├── models/               # SQLAlchemy模型
├── schemas/              # Pydantic模式
└── services/             # 业务逻辑层
```

#### 2. 代码规范
- 使用异步函数处理I/O操作
- 遵循Pydantic模型验证
- 使用依赖注入管理资源
- 编写完整的类型提示
- 遵循RESTful API设计

#### 3. 数据库操作
```python
# 使用异步会话
async with get_async_session() as session:
    result = await session.execute(select(User))
    users = result.scalars().all()
```

### 前端开发

#### 1. 组件开发规范
```vue
<template>
  <!-- 使用 Naive UI 组件 -->
  <n-card>
    <n-data-table :columns="columns" :data="data" />
  </n-card>
</template>

<script setup lang="ts">
// 使用 Composition API
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

// 定义响应式数据
const data = ref([])

// 生命周期钩子
onMounted(async () => {
  // 加载数据
})
</script>
```

#### 2. 状态管理
```typescript
// stores/userStore.ts
import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    currentUser: null,
    isAuthenticated: false
  }),
  
  actions: {
    async login(credentials: LoginCredentials) {
      // 登录逻辑
    }
  }
})
```

## 🧪 测试

### 后端测试

```bash
# 运行所有测试
pytest

# 运行带覆盖率的测试
pytest --cov=app tests/

# 运行特定测试文件
pytest tests/test_users.py
```

### 前端测试

```bash
# 单元测试
npm run test:unit

# E2E测试
npm run test:e2e

# 测试覆盖率
npm run test:coverage
```

## 📝 更新日志

### v0.1.0 (2024-01-XX)

#### 新增功能
- ✨ 完整的用户认证和权限管理系统
- ✨ 学生和班级管理功能
- ✨ 量化项目和记录管理
- ✨ 数据统计和图表展示
- ✨ AI智能助手集成
- ✨ 实时通知系统
- ✨ 系统监控和性能分析

#### 技术特性
- 🏗️ 基于FastAPI的高性能后端架构
- 🎨 基于Vue 3和Naive UI的现代化前端
- 🔒 基于Casbin的权限控制系统
- 📊 ECharts数据可视化
- 🤖 Ollama本地AI服务集成
- 📱 响应式设计，支持多端访问

## 🤝 贡献指南

### 提交Issue
- 使用Issue模板
- 提供详细的问题描述
- 包含复现步骤和环境信息

### 提交Pull Request
1. Fork项目仓库
2. 创建功能分支
3. 提交代码更改
4. 编写测试用例
5. 更新文档
6. 提交Pull Request

### 代码规范
- 后端遵循PEP 8和Black格式化
- 前端遵循ESLint和Prettier规范
- 提交信息遵循Conventional Commits

## 📄 许可证

本项目采用 [MIT许可证](LICENSE)

## 📞 联系我们

- 项目主页: [GitHub Repository](https://github.com/your-org/auraclass)
- 问题反馈: [Issues](https://github.com/your-org/auraclass/issues)
- 邮箱: 36178831@qq.com

## 🙏 致谢

感谢以下开源项目的支持：

- [FastAPI](https://fastapi.tiangolo.com/) - 现代、快速的Python Web框架
- [Vue.js](https://vuejs.org/) - 渐进式JavaScript框架
- [Naive UI](https://www.naiveui.com/) - Vue 3 组件库
- [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL工具包
- [Casbin](https://casbin.org/) - 访问控制库
- [ECharts](https://echarts.apache.org/) - 数据可视化图表库
- [Ollama](https://ollama.ai/) - 本地LLM运行工具

---

<div align="center">

**AuraClass** - 让班级管理更智能、更高效 🚀

</div> 