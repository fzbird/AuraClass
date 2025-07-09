#!/usr/bin/env python3
"""
AuraClass 项目启动工具
支持启动前端、后端或全部服务，以及优雅的关闭处理
"""

import argparse
import asyncio
import os
import platform
import signal
import subprocess
import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any, Callable

# 颜色代码
COLORS = {
    "red": "\033[0;31m",
    "green": "\033[0;32m",
    "yellow": "\033[0;33m",
    "blue": "\033[0;34m",
    "magenta": "\033[0;35m",
    "cyan": "\033[0;36m",
    "reset": "\033[0m"
}

# 项目路径
BASE_DIR = Path(__file__).parent.absolute()
BACKEND_DIR = BASE_DIR / "backend"
FRONTEND_DIR = BASE_DIR / "auraclass-frontend"
VENV_DIR = BASE_DIR / ".venv"

# 进程和状态管理
running_processes: Dict[str, subprocess.Popen] = {}
service_status: Dict[str, bool] = {"backend": False, "frontend": False}


def color_text(text: str, color: str) -> str:
    """返回带颜色的文本"""
    return f"{COLORS.get(color, COLORS['reset'])}{text}{COLORS['reset']}"


def print_color(text: str, color: str = "reset", end: str = "\n") -> None:
    """打印彩色文本"""
    sys.stdout.write(f"{color_text(text, color)}{end}")
    sys.stdout.flush()


def get_venv_activate_cmd() -> str:
    """返回激活虚拟环境的命令"""
    if platform.system() == "Windows":
        return str(VENV_DIR / "Scripts" / "activate.bat")
    return f"source {VENV_DIR / 'bin' / 'activate'}"


async def run_command(cmd: str, working_dir: Path, env: Optional[Dict[str, str]] = None) -> str:
    """运行命令并返回输出"""
    env = env or os.environ.copy()
    
    if platform.system() == "Windows":
        process = await asyncio.create_subprocess_shell(
            cmd, 
            cwd=str(working_dir),
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            shell=True
        )
    else:
        process = await asyncio.create_subprocess_shell(
            cmd, 
            cwd=str(working_dir),
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            executable="/bin/bash"
        )
        
    stdout, stderr = await process.communicate()
    
    if process.returncode != 0:
        error = stderr.decode("utf-8", errors="replace")
        print_color(f"命令执行失败: {cmd}", "red")
        print_color(error, "red")
        return ""
        
    return stdout.decode("utf-8", errors="replace").strip()


async def check_python_env() -> None:
    """检查或创建Python虚拟环境"""
    if not VENV_DIR.exists():
        print_color("Python 虚拟环境不存在，正在创建...", "yellow")
        
        # 创建虚拟环境
        venv_cmd = f"{sys.executable} -m venv {VENV_DIR}"
        await run_command(venv_cmd, BASE_DIR)
        
        # 安装后端依赖
        if platform.system() == "Windows":
            pip_cmd = f"{VENV_DIR}\\Scripts\\pip install -e {BACKEND_DIR}"
        else:
            pip_cmd = f"{VENV_DIR}/bin/pip install -e {BACKEND_DIR}"
            
        await run_command(pip_cmd, BASE_DIR)
        print_color("Python 虚拟环境已创建并安装了后端依赖", "green")
    else:
        print_color("Python 虚拟环境已存在", "green")


async def check_nodejs_env() -> None:
    """检查或安装前端依赖"""
    node_modules = FRONTEND_DIR / "node_modules"
    
    if not node_modules.exists():
        print_color("前端依赖不存在，正在安装...", "yellow")
        await run_command("npm install", FRONTEND_DIR)
        print_color("前端依赖已安装", "green")
    else:
        print_color("前端依赖已存在", "green")


async def start_backend(reload: bool = True) -> None:
    """启动后端服务"""
    print_color("正在启动后端服务...", "blue")
    
    cmd = ""
    if platform.system() == "Windows":
        python_bin = str(VENV_DIR / "Scripts" / "python")
        cmd = f"{python_bin} run.py"
    else:
        cmd = f"{get_venv_activate_cmd()} && python run.py"
    
    # 使用subprocess启动，以保持进程运行
    if platform.system() == "Windows":
        process = subprocess.Popen(
            cmd,
            cwd=str(BACKEND_DIR),
            shell=True,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )
    else:
        process = subprocess.Popen(
            cmd,
            cwd=str(BACKEND_DIR),
            shell=True,
            executable="/bin/bash",
            preexec_fn=os.setsid
        )
    
    running_processes["backend"] = process
    
    # 等待服务启动
    print_color("等待后端服务启动...", "yellow")
    max_retries = 10
    retries = 0
    backend_started = False
    
    while retries < max_retries and not backend_started:
        retries += 1
        await asyncio.sleep(1)
        
        # 检查进程是否还活着
        if process.poll() is not None:
            print_color(f"后端服务进程已终止，退出码: {process.returncode}", "red")
            return
        
        # 检查健康端点
        health_check_cmd = "curl -s http://localhost:8200/health"
        try:
            result = await run_command(health_check_cmd, BASE_DIR)
            if result:
                backend_started = True
                break
        except Exception:
            pass
    
    if backend_started:
        service_status["backend"] = True
        print_color(f"后端服务已成功启动 (PID: {process.pid})", "green")
    else:
        print_color("后端服务启动超时", "red")
        stop_process("backend")


async def start_frontend() -> None:
    """启动前端服务"""
    print_color("正在启动前端服务...", "blue")
    
    cmd = "npm run dev"
    
    # 使用subprocess启动，以保持进程运行
    if platform.system() == "Windows":
        process = subprocess.Popen(
            cmd,
            cwd=str(FRONTEND_DIR),
            shell=True,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )
    else:
        process = subprocess.Popen(
            cmd,
            cwd=str(FRONTEND_DIR),
            shell=True,
            executable="/bin/bash",
            preexec_fn=os.setsid
        )
    
    running_processes["frontend"] = process
    service_status["frontend"] = True
    
    print_color(f"前端服务已启动 (PID: {process.pid})", "green")


def stop_process(service_name: str) -> None:
    """停止指定服务的进程"""
    process = running_processes.get(service_name)
    if not process:
        return
    
    try:
        if platform.system() == "Windows":
            process.terminate()
            # 对于Windows，发送CTRL+C信号
            # os.kill(process.pid, signal.CTRL_C_EVENT)
        else:
            # 对于Unix系统，发送SIGTERM信号给进程组
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        
        # 等待进程终止
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            # 如果超时，强制杀死进程
            if platform.system() == "Windows":
                process.kill()
            else:
                os.killpg(os.getpgid(process.pid), signal.SIGKILL)
        
        print_color(f"{service_name.capitalize()} 服务已停止", "yellow")
    except (ProcessLookupError, OSError) as e:
        print_color(f"停止 {service_name} 服务时出错: {e}", "red")
    
    running_processes.pop(service_name, None)
    service_status[service_name] = False


def stop_all_services() -> None:
    """停止所有运行的服务"""
    for service in list(running_processes.keys()):
        stop_process(service)


def signal_handler(sig, frame) -> None:
    """处理中断信号"""
    print_color("\n正在停止所有服务...", "yellow")
    stop_all_services()
    sys.exit(0)


async def main() -> None:
    """主函数"""
    parser = argparse.ArgumentParser(description="AuraClass 项目启动工具")
    parser.add_argument("--backend", action="store_true", help="仅启动后端服务")
    parser.add_argument("--frontend", action="store_true", help="仅启动前端服务")
    
    args = parser.parse_args()
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print_color("=== AuraClass 项目启动工具 ===", "cyan")
    
    try:
        # 检查环境
        await check_python_env()
        
        # 服务启动逻辑
        if args.backend:
            await start_backend()
        elif args.frontend:
            await check_nodejs_env()
            await start_frontend()
        else:
            # 启动所有服务
            await check_nodejs_env()
            await start_backend()
            await asyncio.sleep(2)  # 给后端一点时间启动
            
            # 只有当后端启动成功后才启动前端
            if service_status["backend"]:
                await start_frontend()
        
        if any(service_status.values()):
            print_color("\n服务启动信息:", "cyan")
            if service_status["backend"]:
                print_color("后端服务运行在: http://localhost:8200", "blue")
                print_color("API 文档地址: http://localhost:8200/api/docs", "blue")
            if service_status["frontend"]:
                print_color("前端服务运行在: http://localhost:5173", "blue")
            
            print_color("\n按 Ctrl+C 停止所有服务", "yellow")
            
            # 保持脚本运行
            while any(running_processes.values()):
                await asyncio.sleep(1)
                # 检查进程是否还活着
                for service, process in list(running_processes.items()):
                    if process.poll() is not None:
                        print_color(f"{service.capitalize()} 服务已意外终止", "red")
                        running_processes.pop(service)
                        service_status[service] = False
        
    except KeyboardInterrupt:
        print_color("\n接收到用户中断，正在停止所有服务...", "yellow")
    except Exception as e:
        print_color(f"发生错误: {e}", "red")
    finally:
        stop_all_services()


if __name__ == "__main__":
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass