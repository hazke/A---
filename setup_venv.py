"""
虚拟环境自动设置脚本
"""
import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, check=True):
    """运行命令"""
    print(f"执行: {cmd}")
    result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr and result.returncode != 0:
        print(f"错误: {result.stderr}")
    return result.returncode == 0

def main():
    print("=" * 50)
    print("   A股量化交易系统 - 虚拟环境设置")
    print("=" * 50)
    print()
    
    # 获取项目根目录
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # 检查Python版本
    print("[1/4] 检查Python版本...")
    try:
        version = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
        print(f"✓ {version.stdout.strip()}")
    except Exception as e:
        print(f"[错误] Python检查失败: {e}")
        return 1
    
    # 检查虚拟环境
    venv_path = project_root / "venv"
    if venv_path.exists():
        print("\n虚拟环境已存在")
        choice = input("是否重新创建？(Y/N): ").strip().upper()
        if choice == 'Y':
            print("删除旧虚拟环境...")
            import shutil
            try:
                shutil.rmtree(venv_path)
                print("✓ 旧虚拟环境已删除")
            except Exception as e:
                print(f"[错误] 删除失败: {e}")
                return 1
        else:
            print("使用现有虚拟环境")
            venv_python = venv_path / "Scripts" / "python.exe" if os.name == 'nt' else venv_path / "bin" / "python"
            if not venv_python.exists():
                print("[错误] 虚拟环境损坏，请重新创建")
                return 1
    else:
        # 创建虚拟环境
        print("\n[2/4] 创建虚拟环境...")
        if not run_command(f'{sys.executable} -m venv venv'):
            print("[错误] 虚拟环境创建失败")
            return 1
        print("✓ 虚拟环境创建成功")
    
    # 确定虚拟环境中的Python路径
    if os.name == 'nt':  # Windows
        venv_python = venv_path / "Scripts" / "python.exe"
        venv_pip = venv_path / "Scripts" / "pip.exe"
    else:  # Linux/Mac
        venv_python = venv_path / "bin" / "python"
        venv_pip = venv_path / "bin" / "pip"
    
    # 升级pip
    print("\n[3/4] 升级pip...")
    if not run_command(f'"{venv_python}" -m pip install --upgrade pip', check=False):
        print("[警告] pip升级失败，继续安装依赖...")
    
    # 安装依赖
    print("\n[4/4] 安装所有依赖...")
    print("这可能需要几分钟，请耐心等待...")
    requirements_file = project_root / "requirements-all.txt"
    if not requirements_file.exists():
        print(f"[错误] 找不到依赖文件: {requirements_file}")
        return 1
    
    if not run_command(f'"{venv_pip}" install -r "{requirements_file}"'):
        print("[错误] 依赖安装失败")
        print("请检查网络连接或手动安装")
        return 1
    
    print()
    print("=" * 50)
    print("   ✓ 虚拟环境设置完成！")
    print("=" * 50)
    print()
    print(f"虚拟环境位置: {venv_path.absolute()}")
    print()
    print("下次使用时：")
    print("1. 运行 start_backend.py 或 start_all.py")
    print("2. 或运行 start_backend.bat / start_all.bat")
    if os.name == 'nt':
        print("3. 或手动激活: venv\\Scripts\\activate")
    else:
        print("3. 或手动激活: source venv/bin/activate")
    print()
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n用户取消操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n[错误] 发生异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

