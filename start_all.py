"""
一键启动前后端服务器
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def check_venv():
    """检查虚拟环境是否存在"""
    project_root = Path(__file__).parent
    if os.name == 'nt':  # Windows
        venv_python = project_root / "venv" / "Scripts" / "python.exe"
    else:  # Linux/Mac
        venv_python = project_root / "venv" / "bin" / "python"
    
    return venv_python.exists()

def start_backend(project_root):
    """启动后端服务器"""
    backend_dir = project_root / "backend"
    
    if not backend_dir.exists():
        print(f"[错误] 找不到backend目录: {backend_dir}")
        return None
    
    # 确定Python可执行文件
    if check_venv():
        if os.name == 'nt':  # Windows
            python_exe = project_root / "venv" / "Scripts" / "python.exe"
        else:  # Linux/Mac
            python_exe = project_root / "venv" / "bin" / "python"
    else:
        python_exe = Path(sys.executable)
    
    # 启动后端（在新进程中）
    if os.name == 'nt':  # Windows
        # Windows使用start命令在新窗口启动
        cmd = f'cd /d "{project_root}" && cd backend && "{python_exe}" main.py'
        process = subprocess.Popen(
            f'start "后端服务器" cmd /k "{cmd}"',
            shell=True
        )
    else:  # Linux/Mac
        # Linux/Mac使用gnome-terminal或xterm
        cmd = f'cd "{project_root}/backend" && "{python_exe}" main.py'
        try:
            process = subprocess.Popen(
                ['gnome-terminal', '--', 'bash', '-c', f'{cmd}; exec bash'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        except:
            try:
                process = subprocess.Popen(
                    ['xterm', '-e', f'bash -c "{cmd}; exec bash"'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            except:
                print("[警告] 无法在新窗口启动后端，将在当前终端运行")
                process = subprocess.Popen(
                    [str(python_exe), "main.py"],
                    cwd=backend_dir
                )
    
    return process

def start_frontend(project_root):
    """启动前端服务器"""
    frontend_dir = project_root / "frontend"
    
    if not frontend_dir.exists():
        print(f"[错误] 找不到frontend目录: {frontend_dir}")
        return None
    
    # 启动前端（在新进程中）
    if os.name == 'nt':  # Windows
        cmd = f'cd /d "{project_root}" && cd frontend && npm run dev'
        process = subprocess.Popen(
            f'start "前端开发服务器" cmd /k "{cmd}"',
            shell=True
        )
    else:  # Linux/Mac
        cmd = f'cd "{project_root}/frontend" && npm run dev'
        try:
            process = subprocess.Popen(
                ['gnome-terminal', '--', 'bash', '-c', f'{cmd}; exec bash'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        except:
            try:
                process = subprocess.Popen(
                    ['xterm', '-e', f'bash -c "{cmd}; exec bash"'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            except:
                print("[警告] 无法在新窗口启动前端，将在当前终端运行")
                process = subprocess.Popen(
                    ['npm', 'run', 'dev'],
                    cwd=frontend_dir
                )
    
    return process

def main():
    print("=" * 50)
    print("   A股量化交易系统 - 一键启动")
    print("=" * 50)
    print()
    
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # 检查虚拟环境
    if check_venv():
        print("✓ 检测到虚拟环境")
    else:
        print("[警告] 未找到虚拟环境")
        print("建议先运行 setup_venv.py 创建虚拟环境")
        print()
        choice = input("是否继续？(Y/N): ").strip().upper()
        if choice != 'Y':
            print("已取消")
            input("按Enter键退出...")
            return 1
    
    print()
    print("此脚本将启动后端和前端")
    print("按Enter继续，或按Ctrl+C取消...")
    try:
        input()
    except KeyboardInterrupt:
        print("\n已取消")
        return 0
    
    # 启动后端
    print("\n[1/2] 启动后端服务器...")
    backend_process = start_backend(project_root)
    if backend_process is None:
        print("[错误] 后端启动失败")
        input("按Enter键退出...")
        return 1
    
    print("✓ 后端服务器已启动（新窗口）")
    time.sleep(3)  # 等待后端启动
    
    # 启动前端
    print("\n[2/2] 启动前端开发服务器...")
    frontend_process = start_frontend(project_root)
    if frontend_process is None:
        print("[错误] 前端启动失败")
        input("按Enter键退出...")
        return 1
    
    print("✓ 前端服务器已启动（新窗口）")
    
    print()
    print("=" * 50)
    print("   启动完成！")
    print("=" * 50)
    print()
    print("后端API: http://localhost:8000")
    print("API文档: http://localhost:8000/api/docs")
    print("前端界面: http://localhost:5173")
    print()
    
    if os.name == 'nt':
        print("两个窗口已打开，关闭窗口即可停止服务")
    else:
        print("两个终端窗口已打开，关闭窗口即可停止服务")
    print()
    print("按Ctrl+C可以退出此脚本（不会停止服务器）")
    print()
    
    # 保持脚本运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n脚本已退出，服务器仍在运行")
        print("请关闭相应的窗口来停止服务器")
        return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n[错误] 发生异常: {e}")
        import traceback
        traceback.print_exc()
        input("\n按Enter键退出...")
        sys.exit(1)

