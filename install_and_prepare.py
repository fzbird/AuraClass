import os
import subprocess
import sys

# 创建必要目录
def create_directories():
    dirs = ['backend/logs', 'backend/uploads']
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"目录已创建: {dir_path}")

# 安装依赖
def install_dependencies():
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-e", "./backend"], check=True)
        print("依赖安装完成")
    except subprocess.CalledProcessError as e:
        print(f"依赖安装失败: {e}")

# 检查.env文件
def check_env_file():
    env_file = 'backend/.env'
    if os.path.exists(env_file):
        print(".env文件已存在")
    else:
        print("警告: .env文件不存在，请确保配置正确的环境变量")

# 主函数
def main():
    create_directories()
    install_dependencies()
    check_env_file()
    print("\n准备工作完成，请运行数据库迁移命令: cd backend && alembic upgrade head")

if __name__ == "__main__":
    main() 