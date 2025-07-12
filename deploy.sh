#!/bin/bash

# AuraClass 自动部署脚本 - 多环境支持版本
# 支持开发、生产、灵活三种部署模式

echo "🚀 AuraClass 自动部署脚本 v1.0 - 共享MySQL版本"
echo "=============================="

# 检查文件权限
echo "🔧 检查文件权限..."
if [ -f "backend/entrypoint.sh" ]; then
    if [ ! -x "backend/entrypoint.sh" ]; then
        echo "⚠️  修复entrypoint.sh执行权限..."
        chmod +x backend/entrypoint.sh
        echo "✅ entrypoint.sh权限已修复"
    else
        echo "✅ entrypoint.sh权限正常"
    fi
fi

# 修复Windows换行符问题
if command -v dos2unix >/dev/null 2>&1; then
    dos2unix backend/entrypoint.sh 2>/dev/null || true
    echo "✅ 换行符格式已修复"
elif command -v sed >/dev/null 2>&1; then
    sed -i 's/\r$//' backend/entrypoint.sh 2>/dev/null || true
    echo "✅ 换行符格式已修复"
fi

# 获取服务器IP - 多种方法兼容，优先获取内网IP
get_server_ip() {
    local ip=""
    
    # 方法1: Windows系统 - ipconfig (优先检测内网IP)
    if [ -z "$ip" ] && command -v ipconfig >/dev/null 2>&1; then
        # 优先获取192.168网段的IP
        ip=$(ipconfig 2>/dev/null | awk '/192\.168\./ {print $NF}' | head -1 2>/dev/null)
        
        # 如果没有192.168网段，则获取10.x网段的IP
        if [ -z "$ip" ]; then
            ip=$(ipconfig 2>/dev/null | awk '/10\./ {print $NF}' | head -1 2>/dev/null)
        fi
        
        # 如果还是没有，则获取172.16-31网段的IP（排除Docker虚拟网卡）
        if [ -z "$ip" ]; then
            ip=$(ipconfig 2>/dev/null | awk '/172\.1[6-9]\./ || /172\.2[0-9]\./ || /172\.3[0-1]\./ {print $NF}' | head -1 2>/dev/null)
        fi
    fi
    
    # 方法2: 使用 hostname -I (Linux)
    if [ -z "$ip" ] && command -v hostname >/dev/null 2>&1; then
        ip=$(hostname -I 2>/dev/null | awk '{print $1}' 2>/dev/null)
    fi
    
    # 方法3: 使用 ip route (Linux)
    if [ -z "$ip" ] && command -v ip >/dev/null 2>&1; then
        ip=$(ip route get 8.8.8.8 2>/dev/null | awk '{print $7}' | head -1 2>/dev/null)
    fi
    
    # 方法4: 使用 ifconfig (通用)
    if [ -z "$ip" ] && command -v ifconfig >/dev/null 2>&1; then
        ip=$(ifconfig 2>/dev/null | grep -E "inet.*192\.|inet.*10\.|inet.*172\." | head -1 | awk '{print $2}' | cut -d: -f2 2>/dev/null)
    fi
    
    # 方法5: 外部IP检测 (fallback)
    if [ -z "$ip" ]; then
        ip=$(curl -s ifconfig.me 2>/dev/null || curl -s ipinfo.io/ip 2>/dev/null || echo "localhost")
    fi
    
    echo "$ip"
}

SERVER_IP=$(get_server_ip)
echo "📍 检测到服务器IP: $SERVER_IP"

# 让用户确认或手动输入IP
echo ""
read -p "🔍 IP地址是否正确？如不正确请输入实际IP地址（回车确认当前IP）: " user_ip
if [ -n "$user_ip" ]; then
    SERVER_IP="$user_ip"
    echo "✅ 更新服务器IP为: $SERVER_IP"
fi

# 步骤1: 选择运行环境
echo ""
echo "🏗️  步骤1: 选择运行环境"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. 🔧 开发环境    - 前端8201端口，后端8200端口，避免端口冲突"
echo "2. 🌐 生产环境    - 前端80端口，后端8200端口，标准HTTP访问"  
echo "3. 🔄 灵活环境    - 双端口支持，同时提供80和8201端口访问"
echo ""
read -p "请选择环境 (1-3): " env_choice

# 设置docker-compose文件和环境描述
case $env_choice in
    1)
        COMPOSE_FILE="docker-compose.dev.yml"
        ENV_TYPE="开发环境"
        PRIMARY_PORT="8201"
        SECONDARY_PORT=""
        echo "✅ 选择：$ENV_TYPE (前端:$PRIMARY_PORT, 后端:8200)"
        ;;
    2)
        COMPOSE_FILE="docker-compose.prod.yml"
        ENV_TYPE="生产环境"
        PRIMARY_PORT="81"
        SECONDARY_PORT=""
        echo "✅ 选择：$ENV_TYPE (前端:$PRIMARY_PORT, 后端:8200)"
        ;;
    3)
        COMPOSE_FILE="docker-compose.yml"
        ENV_TYPE="灵活环境"
        PRIMARY_PORT="81"
        SECONDARY_PORT="8201"
        echo "✅ 选择：$ENV_TYPE (前端双端口: $PRIMARY_PORT + $SECONDARY_PORT, 后端:8200)"
        ;;
    *)
        echo "❌ 无效选择！"
        exit 1
        ;;
esac

# 步骤2: 选择API配置方式
echo ""
echo "🔗 步骤2: 选择API配置方式"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. 🔄 反向代理模式 - 通过nginx代理，前端无需指定后端地址（推荐）"
echo "2. 🌍 环境变量模式 - 明确指定后端API地址"
echo ""
read -p "请选择API配置方式 (1-2): " api_choice

# 配置前端环境变量
case $api_choice in
    1)
        CONFIG_TYPE="反向代理模式"
        echo "✅ 选择：$CONFIG_TYPE"
        echo "🔧 配置反向代理..."
        
        # 创建生产环境配置（使用相对路径，让nginx处理）
        cat > frontend/.env.production << EOF
# 反向代理模式配置 - API请求通过nginx代理
VITE_API_BASE_URL=
VITE_WS_BASE_URL=
EOF
        
        if [ "$env_choice" = "2" ]; then
            ACCESS_URL="http://$SERVER_IP:81/"
            API_URL="http://$SERVER_IP:81/api/"
        elif [ "$env_choice" = "1" ]; then
            ACCESS_URL="http://$SERVER_IP:8201/"
            API_URL="http://$SERVER_IP:8201/api/"
        else
            ACCESS_URL="http://$SERVER_IP:81/ 或 http://$SERVER_IP:8201/"
            API_URL="http://$SERVER_IP:81/api/ 或 http://$SERVER_IP:8201/api/"
        fi
        ;;
        
    2)
        CONFIG_TYPE="环境变量模式"
        echo "✅ 选择：$CONFIG_TYPE"
        echo "🔧 配置环境变量..."
        
        # 创建环境变量配置
        cat > frontend/.env.production << EOF
# 环境变量模式配置 - 明确指定后端API地址
VITE_API_BASE_URL=http://$SERVER_IP:8200
VITE_WS_BASE_URL=ws://$SERVER_IP:8200
EOF
        
        if [ "$env_choice" = "2" ]; then
            ACCESS_URL="http://$SERVER_IP:81/"
            API_URL="http://$SERVER_IP:8200/"
        elif [ "$env_choice" = "1" ]; then
            ACCESS_URL="http://$SERVER_IP:8201/"
            API_URL="http://$SERVER_IP:8200/"
        else
            ACCESS_URL="http://$SERVER_IP:81/ 或 http://$SERVER_IP:8201/"
            API_URL="http://$SERVER_IP:8200/"
        fi
        ;;
        
    *)
        echo "❌ 无效选择！"
        exit 1
        ;;
esac

echo ""
echo "📋 部署配置总结"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🏗️  运行环境: $ENV_TYPE"
echo "🔗 API配置: $CONFIG_TYPE"
echo "📁 配置文件: $COMPOSE_FILE"
echo "🌐 访问地址: $ACCESS_URL"
echo "🔗 API地址: $API_URL"
echo ""

read -p "确认开始部署？(y/n): " confirm
if [[ ! $confirm =~ ^[Yy]$ ]]; then
    echo "❌ 部署已取消"
    exit 0
fi

echo ""
echo "🏗️  开始构建和部署..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 停止现有容器
echo "⏹️  停止现有容器..."
docker-compose down 2>/dev/null || true
docker-compose -f docker-compose.dev.yml down 2>/dev/null || true
docker-compose -f docker-compose.prod.yml down 2>/dev/null || true

# 更新后端环境配置
echo "🔧 更新后端环境配置..."

# 确保.env文件存在
if [ ! -f "backend/.env" ]; then
    echo "📋 创建默认.env文件..."
    if [ -f "backend/.env.example" ]; then
        cp backend/.env.example backend/.env
    else
        cat > backend/.env << EOF
# 数据库配置
DATABASE_URL=mysql+aiomysql://root:password@192.168.1.45:3306/auraclass_db?charset=utf8mb4

# 安全密钥
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS配置
BACKEND_CORS_ORIGINS=http://localhost:8201,http://127.0.0.1:8201

# 服务器配置
BACKEND_PORT=8200
FRONTEND_PORT=8201
EOF
    fi
    echo "✅ 已创建.env文件"
fi

# 配置更新函数
update_env_value() {
    local key=$1
    local value=$2
    local file="backend/.env"
    
    # 转义特殊字符
    escaped_value=$(echo "$value" | sed 's/[[\.*^$()+?{|]/\\&/g')
    
    # 如果key存在，更新；否则添加
    if grep -q "^$key=" "$file"; then
        # 使用临时文件避免sed在某些系统上的问题
        sed "s|^$key=.*|$key=$escaped_value|" "$file" > "$file.tmp" && mv "$file.tmp" "$file"
        echo "📝 已更新 $key"
    else
        echo "$key=$value" >> "$file"
        echo "📝 已添加 $key"
    fi
}

# 基础CORS配置（开发环境默认配置）
BASE_CORS_ORIGINS="http://localhost:8201,http://127.0.0.1:8201"

# 根据环境和API配置生成CORS配置
CORS_ORIGINS="$BASE_CORS_ORIGINS"

# 添加服务器IP到CORS配置
if [ "$env_choice" = "1" ] || [ "$env_choice" = "3" ]; then
    # 开发环境和灵活环境需要8201端口
    CORS_ORIGINS="$CORS_ORIGINS,http://$SERVER_IP:8201"
    echo "📍 已添加 http://$SERVER_IP:8201 到CORS配置"
fi

if [ "$env_choice" = "2" ] || [ "$env_choice" = "3" ]; then
    # 生产环境和灵活环境需要81端口
    CORS_ORIGINS="$CORS_ORIGINS,http://$SERVER_IP:81"
    echo "📍 已添加 http://$SERVER_IP:81 到CORS配置"
fi

# 更新数据库配置（使用192.168.1.45的MySQL服务器）
DATABASE_URL="mysql+aiomysql://root:qsdfz20150707@192.168.1.45:3306/auraclass_db?charset=utf8mb4"

# 更新配置文件
echo "🔧 更新配置项..."
update_env_value "BACKEND_CORS_ORIGINS" "$CORS_ORIGINS"
update_env_value "DATABASE_URL" "$DATABASE_URL"
update_env_value "BACKEND_PORT" "8200"
update_env_value "FRONTEND_PORT" "8201"

echo "✅ 后端环境配置已更新：backend/.env"

# 重新构建和启动
echo "🔄 使用 $COMPOSE_FILE 重新构建容器..."
docker-compose -f "$COMPOSE_FILE" up -d --build

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo ""
echo "🔍 检查服务状态..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 检查容器状态
if docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
    echo "✅ 容器状态正常"
else
    echo "❌ 容器启动异常，请检查日志"
    docker-compose -f "$COMPOSE_FILE" logs --tail=20
fi

# 检查端口监听
if netstat -an 2>/dev/null | grep -q ":$PRIMARY_PORT.*LISTEN" || ss -tuln 2>/dev/null | grep -q ":$PRIMARY_PORT"; then
    echo "✅ 前端端口 $PRIMARY_PORT 正在监听"
else
    echo "⚠️  前端端口 $PRIMARY_PORT 未监听，请检查配置"
fi

if netstat -an 2>/dev/null | grep -q ":8200.*LISTEN" || ss -tuln 2>/dev/null | grep -q ":8200"; then
    echo "✅ 后端端口 8200 正在监听"
else
    echo "⚠️  后端端口 8200 未监听，请检查配置"
fi

echo ""
echo "🎉 部署完成！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 前端访问地址: $ACCESS_URL"
echo "🔗 后端API地址: $API_URL"
echo ""
echo "📝 常用命令:"
echo "  查看日志: docker-compose -f $COMPOSE_FILE logs -f"
echo "  重启服务: docker-compose -f $COMPOSE_FILE restart"
echo "  停止服务: docker-compose -f $COMPOSE_FILE down"
echo ""
echo "🔧 如果遇到问题，请检查:"
echo "  1. 数据库连接配置是否正确"
echo "  2. 防火墙是否允许相应端口"
echo "  3. 容器日志是否有错误信息" 