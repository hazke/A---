"""
使用 Docker 启动系统
"""
import os
import sys
import subprocess
from pathlib import Path

def check_docker():
    """检查 Docker 是否安装"""
    try:
        result = subprocess.run(["docker", "--version"], 
                              capture_output=True, text=True, check=True)
        print(f"✓ Docker版本: {result.stdout.strip()}")
        
        # 检查 docker-compose
        try:
            compose_result = subprocess.run(["docker-compose", "--version"], 
                                          capture_output=True, text=True, check=True)
            print(f"✓ Docker Compose版本: {compose_result.stdout.strip()}")
        except FileNotFoundError:
            # 尝试使用 docker compose (新版本)
            try:
                compose_result = subprocess.run(["docker", "compose", "version"], 
                                              capture_output=True, text=True, check=True)
                print(f"✓ Docker Compose版本: {compose_result.stdout.strip()}")
            except:
                print("⚠ Docker Compose 未找到，但可以使用 docker compose 命令")
        
        return True
    except FileNotFoundError:
        print("=" * 60)
        print("[错误] 未检测到 Docker")
        print("=" * 60)
        print()
        print("请先安装 Docker：")
        print("1. Windows/Mac: https://www.docker.com/products/docker-desktop/")
        print("2. Linux: sudo apt-get install docker.io docker-compose")
        print()
        print("安装完成后，重启终端并重新运行此脚本")
        print()
        return False
    except Exception as e:
        print(f"[错误] Docker检查失败: {e}")
        return False

def get_compose_command():
    """获取 docker-compose 命令"""
    try:
        subprocess.run(["docker-compose", "--version"], 
                      capture_output=True, check=True)
        return "docker-compose"
    except:
        return "docker compose"

def main():
    print("=" * 50)
    print("   A股量化交易系统 - Docker 启动")
    print("=" * 50)
    print()
    
    # 切换到项目根目录
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # 检查 Docker
    if not check_docker():
        input("按Enter键退出...")
        return 1
    
    # 检查必要文件
    if not (project_root / "docker-compose.yml").exists():
        print("[错误] 找不到 docker-compose.yml 文件")
        input("按Enter键退出...")
        return 1
    
    print()
    print("=" * 50)
    print("选择操作：")
    print("=" * 50)
    print("1. 构建并启动（首次使用，推荐）")
    print("2. 启动（已构建，后台运行）")
    print("3. 停止服务")
    print("4. 查看日志")
    print("5. 重启服务")
    print("6. 查看服务状态")
    print("7. 清理（删除容器和镜像）")
    print()
    
    choice = input("请选择 (1-7): ").strip()
    
    compose_cmd = get_compose_command()
    
    try:
        if choice == "1":
            print("\n[1/2] 构建镜像...")
            subprocess.run([compose_cmd, "build"], check=True)
            print("\n[2/2] 启动服务...")
            print("=" * 50)
            print()
            subprocess.run([compose_cmd, "up"], check=True)
            
        elif choice == "2":
            print("\n启动服务...")
            print("=" * 50)
            print()
            subprocess.run([compose_cmd, "up", "-d"], check=True)
            print("\n✓ 服务已启动（后台运行）")
            print("\n访问地址：")
            print("  前端: http://localhost:5173")
            print("  后端: http://localhost:8000")
            print("  API文档: http://localhost:8000/api/docs")
            print("\n查看日志: docker-compose logs -f")
            
        elif choice == "3":
            print("\n停止服务...")
            subprocess.run([compose_cmd, "down"], check=True)
            print("✓ 服务已停止")
            
        elif choice == "4":
            print("\n查看日志（按 Ctrl+C 退出）...")
            print("=" * 50)
            print()
            subprocess.run([compose_cmd, "logs", "-f"], check=True)
            
        elif choice == "5":
            print("\n重启服务...")
            subprocess.run([compose_cmd, "restart"], check=True)
            print("✓ 服务已重启")
            
        elif choice == "6":
            print("\n服务状态：")
            print("=" * 50)
            subprocess.run([compose_cmd, "ps"], check=True)
            
        elif choice == "7":
            print("\n⚠ 警告：这将删除所有容器和镜像")
            confirm = input("确定要继续吗？(yes/no): ").strip().lower()
            if confirm == "yes":
                print("\n清理中...")
                subprocess.run([compose_cmd, "down", "-v", "--rmi", "all"], check=True)
                print("✓ 清理完成")
            else:
                print("已取消")
            
        else:
            print("[错误] 无效的选择")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n用户中断")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\n[错误] 命令执行失败: {e}")
        return 1
    except Exception as e:
        print(f"\n[错误] 发生异常: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
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

