#!/bin/bash

# 设置退出时杀死所有子进程
trap 'kill $(jobs -p) 2>/dev/null' EXIT

# 颜色代码
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # 无颜色

# 显示带颜色的消息
echo_color() {
  color=$1
  message=$2
  echo -e "${color}${message}${NC}"
}

# 检查Python环境
if [ ! -d ".venv" ]; then
  echo_color $YELLOW "Python 虚拟环境不存在，正在创建..."
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -e backend
else
  source .venv/bin/activate
fi

# 检查Node.js环境
cd auraclass-frontend
if [ ! -d "node_modules" ]; then
  echo_color $YELLOW "前端依赖不存在，正在安装..."
  npm install
fi
cd ..

# 启动后端服务
echo_color $BLUE "正在启动后端服务..."
cd backend
python run.py &
BACKEND_PID=$!
cd ..

# 等待后端启动
echo_color $YELLOW "等待后端服务启动..."
sleep 5

# 检查后端服务是否正常启动
curl -s http://localhost:8200/health > /dev/null
if [ $? -eq 0 ]; then
  echo_color $GREEN "后端服务已成功启动 (PID: $BACKEND_PID)"
else
  echo_color $RED "后端服务启动失败！"
  kill $BACKEND_PID 2>/dev/null
  exit 1
fi

# 启动前端服务
echo_color $BLUE "正在启动前端服务..."
cd auraclass-frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo_color $GREEN "所有服务启动成功！"
echo_color $BLUE "后端服务运行在: http://localhost:8200"
echo_color $BLUE "前端服务运行在: http://localhost:8201"
echo_color $YELLOW "按 Ctrl+C 停止所有服务"

# 等待用户中断
wait 