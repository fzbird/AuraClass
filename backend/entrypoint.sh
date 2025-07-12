#!/bin/bash

# AuraClass Backend Entrypoint Script
echo "🚀 Starting AuraClass Backend..."

# 等待数据库连接
echo "⏳ Waiting for database connection..."
sleep 5

# 运行数据库迁移
echo "🔄 Running database migrations..."
cd /app && python -m alembic upgrade head

# 启动应用
echo "✅ Starting FastAPI application..."
exec "$@" 