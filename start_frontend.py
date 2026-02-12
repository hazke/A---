"""
启动前端开发服务器
"""
import os
import sys
import subprocess
from pathlib import Path

def check_nodejs():
    """检查Node.js是否安装"""
    try:
        result = subprocess.run(["node", "--version"], 
                              capture_output=True, text=True, check=True)
        node_version = result.stdout.strip()
        print(f"✓ Node.js版本: {node_version}")
        
        # 检查npm
        npm_result = subprocess.run(["npm", "--version"], 
                                   capture_output=True, text=True, check=True)
        npm_version = npm_result.stdout.strip()
        print(f"✓ npm版本: {npm_version}")
        return True
    except FileNotFoundError:
        print("=" * 60)
        print("[错误] 未检测到Node.js或npm")
        print("=" * 60)
        print()
        print("Node.js未安装或未添加到系统PATH环境变量")
        print()
        print("📋 安装步骤：")
        print("1. 访问 Node.js 官网: https://nodejs.org/")
        print("2. 下载 LTS 版本（推荐18.x或20.x）")
        print("3. 运行安装程序，确保勾选 'Add to PATH'")
        print("4. 安装完成后，关闭所有终端窗口")
        print("5. 重新打开终端，运行: node --version")
        print()
        print("📖 详细安装指南请查看: install_nodejs_guide.md")
        print()
        print("💡 提示：")
        print("   - 安装后需要重启终端才能生效")
        print("   - 如果仍然不行，可能需要重启电脑")
        print("   - 确保安装时勾选了 'Add to PATH' 选项")
        print()
        return False
    except subprocess.CalledProcessError as e:
        print("[错误] Node.js或npm版本检查失败")
        print(f"错误信息: {e}")
        return False
    except Exception as e:
        print(f"[错误] Node.js检查失败: {e}")
        return False

def check_dependencies(frontend_dir):
    """检查前端依赖是否已安装"""
    node_modules = frontend_dir / "node_modules"
    return node_modules.exists()

def main():
    print("=" * 50)
    print("   A股量化交易系统 - 前端启动")
    print("=" * 50)
    print()
    
    # 切换到项目根目录
    project_root = Path(__file__).parent
    frontend_dir = project_root / "frontend"
    
    if not frontend_dir.exists():
        print(f"[错误] 找不到frontend目录: {frontend_dir}")
        input("按Enter键退出...")
        return 1
    
    # 检查Node.js
    if not check_nodejs():
        input("按Enter键退出...")
        return 1
    
    # 检查依赖
    print("\n[1/2] 检查依赖...")
    if not check_dependencies(frontend_dir):
        print("检测到未安装依赖，正在安装...")
        print("这可能需要几分钟，请耐心等待...")
        os.chdir(frontend_dir)
        try:
            subprocess.run(["npm", "install"], check=True)
            print("✓ 依赖安装完成")
        except subprocess.CalledProcessError:
            print("[错误] 依赖安装失败")
            input("按Enter键退出...")
            return 1
        except Exception as e:
            print(f"[错误] 安装过程出错: {e}")
            input("按Enter键退出...")
            return 1
    else:
        print("✓ 依赖已安装")
    
    # 启动前端
    print("\n[2/2] 启动前端开发服务器...")
    os.chdir(frontend_dir)
    
    try:
        print("前端服务器启动中...")
        print("=" * 50)
        print()
        
        # 直接运行，不捕获输出（实时显示）
        subprocess.run(["npm", "run", "dev"], check=True)
        
    except KeyboardInterrupt:
        print("\n\n用户中断，前端服务器已停止")
        return 0
    except subprocess.CalledProcessError as e:
        print("\n[错误] 前端启动失败")
        print("请检查：")
        print("1. Node.js依赖是否已安装")
        print("2. 端口5173是否被占用")
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

