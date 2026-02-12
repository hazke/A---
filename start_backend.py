"""
启动后端服务器
"""
import os
import sys
import subprocess
from pathlib import Path

def check_python():
    """检查Python是否安装"""
    try:
        result = subprocess.run([sys.executable, "--version"], 
                              capture_output=True, text=True, check=True)
        print(f"✓ Python版本: {result.stdout.strip()}")
        return True
    except Exception as e:
        print(f"[错误] Python检查失败: {e}")
        return False

def check_venv():
    """检查虚拟环境是否存在"""
    project_root = Path(__file__).parent
    if os.name == 'nt':  # Windows
        venv_python = project_root / "venv" / "Scripts" / "python.exe"
    else:  # Linux/Mac
        venv_python = project_root / "venv" / "bin" / "python"
    
    return venv_python.exists()

def get_python_executable():
    """获取Python可执行文件路径"""
    project_root = Path(__file__).parent
    if check_venv():
        if os.name == 'nt':  # Windows
            return project_root / "venv" / "Scripts" / "python.exe"
        else:  # Linux/Mac
            return project_root / "venv" / "bin" / "python"
    else:
        return Path(sys.executable)

def main():
    print("=" * 50)
    print("   A股量化交易系统 - 后端启动")
    print("=" * 50)
    print()
    
    # 切换到项目根目录
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # 检查虚拟环境
    if check_venv():
        print("[1/2] ✓ 检测到虚拟环境")
        python_exe = get_python_executable()
    else:
        print("[警告] 未找到虚拟环境")
        print("建议先运行 setup_venv.py 创建虚拟环境")
        print()
        choice = input("是否继续使用系统Python？(Y/N): ").strip().upper()
        if choice != 'Y':
            print("已取消，请先运行 setup_venv.py")
            input("按Enter键退出...")
            return 1
        
        if not check_python():
            print("[错误] 未检测到Python，请先安装Python 3.8+")
            input("按Enter键退出...")
            return 1
        
        python_exe = Path(sys.executable)
    
    # 启动后端
    print("\n[2/2] 启动后端服务器...")
    backend_dir = project_root / "backend"
    
    if not backend_dir.exists():
        print(f"[错误] 找不到backend目录: {backend_dir}")
        input("按Enter键退出...")
        return 1
    
    os.chdir(backend_dir)
    
    try:
        # 启动后端服务器
        print(f"使用Python: {python_exe}")
        print("后端服务器启动中...")
        print("=" * 50)
        print()
        
        # 直接运行，不捕获输出（实时显示）
        subprocess.run([str(python_exe), "main.py"], check=True)
        
    except KeyboardInterrupt:
        print("\n\n用户中断，后端服务器已停止")
        return 0
    except subprocess.CalledProcessError as e:
        print("\n[错误] 后端启动失败")
        print("请检查：")
        print("1. Python依赖是否已安装")
        print("2. 端口8000是否被占用")
        print("3. 查看上方错误信息")
        input("\n按Enter键退出...")
        return 1
    except Exception as e:
        print(f"\n[错误] 发生异常: {e}")
        import traceback
        traceback.print_exc()
        input("\n按Enter键退出...")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n[错误] 发生异常: {e}")
        import traceback
        traceback.print_exc()
        input("\n按Enter键退出...")
        sys.exit(1)

