# AuraClass Docker 部署指南

本项目提供了一套完整的 Docker 部署方案，支持多环境部署和自动化配置。

## 🚀 快速开始

### 1. 准备工作

确保您的系统已安装：
- Docker
- Docker Compose
- Git Bash (Windows 用户)

### 2. 数据库配置

项目使用外部 MySQL 数据库（192.168.1.45:3306），请确保：
- 数据库服务器正在运行
- 创建了 `auraclass_db` 数据库
- 用户有足够的权限访问数据库

### 3. 一键部署

运行部署脚本：
```bash
./deploy.sh
```

脚本会引导您完成以下配置：
1. **IP 地址确认**：自动检测或手动输入服务器 IP
2. **环境选择**：
   - 开发环境（8201端口）
   - 生产环境（80端口）
   - 灵活环境（80+8201双端口）
3. **API 配置**：
   - 反向代理模式（推荐）
   - 环境变量模式

## 🏗️ 环境说明

### 开发环境
- 前端端口：8201
- 后端端口：8200
- 配置文件：`docker-compose.dev.yml`
- 适用场景：本地开发，避免端口冲突

### 生产环境
- 前端端口：80
- 后端端口：8200
- 配置文件：`docker-compose.prod.yml`
- 适用场景：生产部署，标准 HTTP 访问

### 灵活环境
- 前端端口：80 + 8201
- 后端端口：8200
- 配置文件：`docker-compose.yml`
- 适用场景：同时支持生产和开发访问

## 🔧 手动部署

如果您不想使用自动化脚本，可以手动部署：

### 1. 创建环境文件
```bash
cp backend/env.template backend/.env
```

### 2. 修改配置
编辑 `backend/.env` 文件，更新数据库连接信息。

### 3. 启动服务
```bash
# 开发环境
docker-compose -f docker-compose.dev.yml up -d --build

# 生产环境
docker-compose -f docker-compose.prod.yml up -d --build

# 灵活环境
docker-compose up -d --build
```

## 🌐 API 配置模式

### 反向代理模式（推荐）
- 前端通过 Nginx 代理访问后端
- API 路径：`/api/*`
- WebSocket 路径：`/ws/*`
- 上传路径：`/uploads/*`

### 环境变量模式
- 前端直接访问后端 IP:8200
- 需要配置 CORS 允许跨域访问

## 📝 常用命令

### 查看服务状态
```bash
docker-compose ps
```

### 查看日志
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 重启服务
```bash
docker-compose restart
```

### 停止服务
```bash
docker-compose down
```

### 重新构建
```bash
docker-compose up -d --build
```

## 🔍 故障排除

### 1. 容器无法启动
- 检查端口是否被占用
- 查看容器日志：`docker-compose logs`
- 确认 Docker 服务正在运行

### 2. 数据库连接失败
- 确认数据库服务器地址和端口
- 检查数据库用户权限
- 确认防火墙设置

### 3. 前端无法访问后端
- 检查 CORS 配置
- 确认后端服务正在运行
- 检查 Nginx 代理配置

### 4. 权限问题
- 确保脚本有执行权限：`chmod +x deploy.sh`
- 检查 Docker 用户权限

## 📋 项目结构

```
AuraClass/
├── backend/                 # 后端代码
│   ├── app/                # FastAPI 应用
│   ├── Dockerfile          # 后端 Docker 配置
│   ├── entrypoint.sh       # 启动脚本
│   ├── requirements.txt    # Python 依赖
│   └── env.template        # 环境变量模板
├── frontend/               # 前端代码
│   ├── src/               # Vue.js 应用
│   ├── Dockerfile         # 前端 Docker 配置
│   └── nginx.conf         # Nginx 配置
├── docker-compose.yml      # 灵活环境配置
├── docker-compose.dev.yml  # 开发环境配置
├── docker-compose.prod.yml # 生产环境配置
└── deploy.sh              # 自动部署脚本
```

## 🔒 安全建议

1. 修改默认密钥：更新 `backend/.env` 中的 `SECRET_KEY`
2. 数据库安全：使用强密码，限制数据库访问权限
3. 防火墙配置：只开放必要的端口
4. HTTPS 配置：生产环境建议使用 HTTPS

## 📞 技术支持

如果遇到问题，请检查：
1. Docker 和 Docker Compose 版本
2. 系统防火墙设置
3. 数据库连接配置
4. 容器日志信息

更多问题请参考项目文档或联系技术支持。 