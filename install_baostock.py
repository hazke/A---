"""
安装 BaoStock 依赖脚本
"""
import sys
import subprocess
from pathlib import Path

def main():
    print("=" * 50)
    print("   安装 BaoStock 依赖")
    print("=" * 50)
    print()
    
    # 检查是否在虚拟环境中
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    if in_venv:
        print("✓ 检测到虚拟环境")
        python_cmd = sys.executable
    else:
        print("⚠ 未检测到虚拟环境")
        print("建议：先运行 python setup_venv.py 创建虚拟环境")
        print()
        choice = input("是否继续在当前环境安装？(Y/N): ").strip().upper()
        if choice != 'Y':
            print("已取消")
            return 1
        python_cmd = sys.executable
    
    print()
    print(f"使用 Python: {python_cmd}")
    print()
    
    # 安装 baostock
    print("正在安装 baostock...")
    try:
        result = subprocess.run(
            [python_cmd, "-m", "pip", "install", "baostock>=0.8.8"],
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        print("✓ BaoStock 安装成功！")
        print()
        
        # 验证安装
        print("验证安装...")
        import baostock as bs
        print(f"✓ BaoStock 版本: {bs.__version__}")
        print()
        print("=" * 50)
        print("   安装完成！")
        print("=" * 50)
        print()
        print("现在可以：")
        print("1. 重启后端服务")
        print("2. 系统将自动使用 BaoStock 作为数据源")
        print()
        
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"[错误] 安装失败")
        print(f"错误信息: {e.stderr}")
        print()
        print("请尝试：")
        print("1. 检查网络连接")
        print("2. 使用管理员权限运行")
        print("3. 或手动运行: python -m pip install baostock>=0.8.8")
        return 1
    except ImportError as e:
        print(f"[错误] 验证失败: {e}")
        print("BaoStock 可能未正确安装")
        return 1
    except Exception as e:
        print(f"[错误] 发生异常: {e}")
        import traceback
        traceback.print_exc()
        return 1

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

