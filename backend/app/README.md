# AuraClass 班级量化管理软件后端

## 项目描述

AuraClass是一款班级量化管理辅助软件，旨在提升教师和班级管理员对班级的管理效率和数据洞察能力。本仓库包含AuraClass的后端API服务。

## 技术栈

- FastAPI
- SQLAlchemy (异步)
- MySQL
- Casbin (权限控制)
- WebSocket
- JWT认证

## 开发环境设置

### 环境要求

- Python 3.10+
- MySQL 8.0+
- Redis (可选)

### 安装步骤

1. 克隆项目
```bash
git clone https://github.com/yourusername/auraclass-backend.git
cd auraclass-backend
```

2. 创建并激活虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

3. 安装依赖
```bash
pip install -e .
```

4. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件填入你的配置
```

5. 初始化数据库
```bash
alembic upgrade head
```

6. 启动开发服务器
```bash
uvicorn app.main:app --reload
```

## API文档

开发环境下，访问以下URL查看API文档：
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## 运行测试

```bash
pytest
```

## 部署

查看[部署文档](./docs/deployment.md)了解如何部署到生产环境。

## 许可证

[MIT](LICENSE)
