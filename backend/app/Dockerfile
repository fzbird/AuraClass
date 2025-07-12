FROM python:3.10-slim

WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Shanghai

# 安装系统依赖
# aiomysql 是纯 Python 实现，通常不需要系统级的-dev依赖包
# 如果您使用如 mysqlclient 这样的库，则需要安装 default-libmysqlclient-dev
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY pyproject.toml .
# poetry install --no-root --no-dev
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8200

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8200"]
