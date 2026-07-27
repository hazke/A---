"""
使用 Docker 启动系统
"""
import os
import sys
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.console_fix import configure_console

configure_console()


def check_docker():
    """检查 Docker 是否安装"""
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            errors="replace",
        )
        print(f"[OK] Docker: {result.stdout.strip()}")

        try:
            compose_result = subprocess.run(
                ["docker-compose", "--version"],
                capture_output=True,
                text=True,
                check=True,
                encoding="utf-8",
                errors="replace",
            )
            print(f"[OK] Docker Compose: {compose_result.stdout.strip()}")
        except FileNotFoundError:
            try:
                compose_result = subprocess.run(
                    ["docker", "compose", "version"],
                    capture_output=True,
                    text=True,
                    check=True,
                    encoding="utf-8",
                    errors="replace",
                )
                print(f"[OK] Docker Compose: {compose_result.stdout.strip()}")
            except Exception:
                print("[WARN] docker-compose not found; try: docker compose")

        return True
    except FileNotFoundError:
        print("=" * 60)
        print("[ERROR] Docker not found")
        print("=" * 60)
        print()
        print("Install Docker first:")
        print("1. Windows/Mac: https://www.docker.com/products/docker-desktop/")
        print("2. Linux: sudo apt-get install docker.io docker-compose")
        print()
        print("Then restart the terminal and run this script again.")
        print()
        return False
    except Exception as e:
        print(f"[ERROR] Docker check failed: {e}")
        return False

def get_compose_command():
    """获取 docker-compose 命令"""
    try:
        subprocess.run(["docker-compose", "--version"], 
                      capture_output=True, check=True)
        return "docker-compose"
    except:
        return "docker compose"

BROKEN_REGISTRY_MIRRORS = {
    "https://docker.m.daocloud.io",
    "https://docker.1panel.live",
    "https://dockerpull.com",
}

def ensure_docker_registry_mirrors():
    """确保 Docker Desktop 已配置可用镜像加速（拉取基础镜像）"""
    daemon_path = Path.home() / ".docker" / "daemon.json"
    needs_setup = not daemon_path.exists()
    if daemon_path.exists():
        try:
            import json
            config = json.loads(daemon_path.read_text(encoding="utf-8"))
            mirrors = config.get("registry-mirrors", [])
            has_broken = any(m in BROKEN_REGISTRY_MIRRORS for m in mirrors)
            needs_setup = not mirrors or has_broken
        except Exception:
            needs_setup = True

    if not needs_setup:
        return

    print("正在更新 Docker 镜像加速配置...")
    setup_script = Path(__file__).parent / "setup_docker_mirrors.py"
    if setup_script.exists():
        subprocess.run([sys.executable, str(setup_script)], check=False)
        print("[WARN] Restart Docker Desktop, then continue the build.\n")


def main():
    print("=" * 50)
    print("  A-Stock Quant - Docker Launcher")
    print("=" * 50)
    print()

    project_root = Path(__file__).parent
    os.chdir(project_root)

    if not check_docker():
        input("Press Enter to exit...")
        return 1

    if not (project_root / "docker-compose.yml").exists():
        print("[ERROR] docker-compose.yml not found")
        input("Press Enter to exit...")
        return 1

    print()
    print("=" * 50)
    print("Select an action:")
    print("=" * 50)
    print("1. Build and start (first time, recommended)")
    print("2. Start (already built, detached)")
    print("3. Stop")
    print("4. Logs")
    print("5. Restart")
    print("6. Status")
    print("7. Clean (remove containers and images)")
    print()

    choice = input("Choose (1-7): ").strip()
    
    compose_cmd = get_compose_command()
    
    try:
        if choice == "1":
            ensure_docker_registry_mirrors()
            print("\n[1/3] Cleaning old containers (avoid name conflicts)...")
            # Force-remove leftover named containers if compose down missed them
            subprocess.run([compose_cmd, "down", "--remove-orphans"], check=False)
            subprocess.run(["docker", "rm", "-f", "quant-backend", "quant-frontend"], check=False)
            print("\n[2/3] Building images...")
            print("(CN mirrors enabled for apt/pip/npm; first build may take a few minutes)\n")
            subprocess.run([compose_cmd, "build"], check=True)
            print("\n[3/3] Starting services...")
            print("=" * 50)
            print()
            subprocess.run([compose_cmd, "up"], check=True)

        elif choice == "2":
            print("\nStarting services...")
            print("=" * 50)
            print()
            subprocess.run([compose_cmd, "up", "-d"], check=True)
            print("\n[OK] Services started (detached)")
            print("\nURLs:")
            print("  Frontend: http://localhost:5173")
            print("  Backend:  http://localhost:8000")
            print("  API docs: http://localhost:8000/api/docs")
            print("\nLogs: docker-compose logs -f")

        elif choice == "3":
            print("\nStopping services...")
            subprocess.run([compose_cmd, "down"], check=True)
            print("[OK] Services stopped")

        elif choice == "4":
            print("\nShowing logs (Ctrl+C to exit)...")
            print("=" * 50)
            print()
            subprocess.run([compose_cmd, "logs", "-f"], check=True)

        elif choice == "5":
            print("\nRestarting services...")
            subprocess.run([compose_cmd, "restart"], check=True)
            print("[OK] Services restarted")

        elif choice == "6":
            print("\nService status:")
            print("=" * 50)
            subprocess.run([compose_cmd, "ps"], check=True)

        elif choice == "7":
            print("\n[WARN] This will delete all containers and images")
            confirm = input("Continue? (yes/no): ").strip().lower()
            if confirm == "yes":
                print("\nCleaning...")
                subprocess.run([compose_cmd, "down", "-v", "--rmi", "all"], check=True)
                subprocess.run(["docker", "rm", "-f", "quant-backend", "quant-frontend"], check=False)
                print("[OK] Cleanup done")
            else:
                print("Cancelled")

        else:
            print("[ERROR] Invalid choice")
            return 1

    except KeyboardInterrupt:
        print("\n\nStopped by user (Ctrl+C)")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Command failed: {e}")
        return 1
    except Exception as e:
        print(f"\n[ERROR] Unexpected exception: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n[ERROR] Unexpected exception: {e}")
        import traceback

        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)

