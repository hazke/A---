"""
环境检查脚本 - 检查所有依赖是否已安装
"""
import sys
import subprocess
from pathlib import Path

def check_python():
    """检查Python"""
    print("=" * 50)
    print("环境检查")
    print("=" * 50)
    print()
    
    print("[1/4] 检查Python...")
    try:
        version = subprocess.run([sys.executable, "--version"], 
                                capture_output=True, text=True, check=True)
        print(f"  ✓ Python版本: {version.stdout.strip()}")
        
        # 检查版本号
        version_str = version.stdout.strip()
        version_num = float(version_str.split()[1].rsplit('.', 1)[0])
        if version_num < 3.8:
            print(f"  ⚠ 警告: Python版本过低，推荐3.8+")
        return True
    except Exception as e:
        print(f"  ✗ Python检查失败: {e}")
        return False

def check_venv():
    """检查虚拟环境"""
    print("\n[2/4] 检查虚拟环境...")
    project_root = Path(__file__).parent
    venv_path = project_root / "venv"
    
    if sys.platform == 'win32':
        venv_python = venv_path / "Scripts" / "python.exe"
    else:
        venv_python = venv_path / "bin" / "python"
    
    if venv_python.exists():
        print(f"  ✓ 虚拟环境已创建: {venv_path}")
        
        # 检查关键依赖
        print("  检查关键依赖...")
        try:
            result = subprocess.run(
                [str(venv_python), "-m", "pip", "list"],
                capture_output=True, text=True, check=True
            )
            packages = result.stdout.lower()
            
            required = ['pandas', 'fastapi', 'numpy', 'pydantic']
            missing = []
            for pkg in required:
                if pkg not in packages:
                    missing.append(pkg)
            
            if missing:
                print(f"  ⚠ 缺少依赖: {', '.join(missing)}")
                print("  请运行: python setup_venv.py")
                return False
            else:
                print("  ✓ 关键依赖已安装")
                return True
        except Exception as e:
            print(f"  ⚠ 无法检查依赖: {e}")
            return False
    else:
        print(f"  ✗ 虚拟环境未创建: {venv_path}")
        print("  请运行: python setup_venv.py")
        return False

def check_nodejs():
    """检查Node.js和npm"""
    print("\n[3/4] 检查Node.js...")
    try:
        node_result = subprocess.run(["node", "--version"], 
                                    capture_output=True, text=True, check=True)
        print(f"  ✓ Node.js版本: {node_result.stdout.strip()}")
        
        npm_result = subprocess.run(["npm", "--version"], 
                                   capture_output=True, text=True, check=True)
        print(f"  ✓ npm版本: {npm_result.stdout.strip()}")
        return True
    except FileNotFoundError:
        print("  ✗ Node.js或npm未安装")
        print("  请访问 https://nodejs.org/ 下载安装LTS版本")
        print("  详细指南: install_nodejs_guide.md")
        return False
    except Exception as e:
        print(f"  ✗ Node.js检查失败: {e}")
        return False

def check_frontend_deps():
    """检查前端依赖"""
    print("\n[4/4] 检查前端依赖...")
    project_root = Path(__file__).parent
    frontend_dir = project_root / "frontend"
    node_modules = frontend_dir / "node_modules"
    
    if not frontend_dir.exists():
        print(f"  ✗ 前端目录不存在: {frontend_dir}")
        return False
    
    if node_modules.exists():
        print(f"  ✓ 前端依赖已安装")
        return True
    else:
        print(f"  ⚠ 前端依赖未安装")
        print("  请运行: cd frontend && npm install")
        return False

def check_config():
    """检查配置文件"""
    print("\n[5/5] 检查配置文件...")
    project_root = Path(__file__).parent
    config_file = project_root / "config" / "config.yaml"
    
    if config_file.exists():
        print(f"  ✓ 配置文件存在: {config_file}")
        return True
    else:
        print(f"  ⚠ 配置文件不存在: {config_file}")
        print("  系统将使用默认配置")
        return True  # 配置文件可以自动创建，不算错误

def main():
    results = []
    
    results.append(("Python", check_python()))
    results.append(("虚拟环境", check_venv()))
    results.append(("Node.js", check_nodejs()))
    results.append(("前端依赖", check_frontend_deps()))
    results.append(("配置文件", check_config()))
    
    print()
    print("=" * 50)
    print("检查结果")
    print("=" * 50)
    
    all_ok = True
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")
        if not result:
            all_ok = False
    
    print()
    if all_ok:
        print("✓ 所有检查通过！可以启动系统了")
        print()
        print("启动命令：")
        print("  python start_all.py        # 一键启动")
        print("  python start_backend.py   # 仅启动后端")
        print("  python start_frontend.py  # 仅启动前端")
    else:
        print("✗ 部分检查未通过，请先解决上述问题")
        print()
        print("修复建议：")
        if not results[1][1]:  # 虚拟环境
            print("  1. 运行: python setup_venv.py")
        if not results[2][1]:  # Node.js
            print("  2. 安装Node.js: https://nodejs.org/")
        if not results[3][1]:  # 前端依赖
            print("  3. 运行: cd frontend && npm install")
    
    print()
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())

