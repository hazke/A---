"""
启动前端开发服务器
"""
import os
import sys
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.console_fix import configure_console

configure_console()


def check_nodejs():
    """检查Node.js是否安装"""
    try:
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            errors="replace",
        )
        node_version = result.stdout.strip()
        print(f"[OK] Node.js version: {node_version}")

        npm_result = subprocess.run(
            ["npm", "--version"],
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            errors="replace",
        )
        npm_version = npm_result.stdout.strip()
        print(f"[OK] npm version: {npm_version}")
        return True
    except FileNotFoundError:
        print("=" * 60)
        print("[ERROR] Node.js / npm not found")
        print("=" * 60)
        print()
        print("Node.js is not installed or not on PATH")
        print()
        print("Install steps:")
        print("1. Visit https://nodejs.org/")
        print("2. Download LTS (18.x or 20.x)")
        print("3. Install and check 'Add to PATH'")
        print("4. Close all terminals, then reopen")
        print("5. Run: node --version")
        print()
        return False
    except subprocess.CalledProcessError as e:
        print("[ERROR] Node.js / npm version check failed")
        print(f"Detail: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Node.js check failed: {e}")
        return False

def check_dependencies(frontend_dir):
    """检查前端依赖是否已安装"""
    node_modules = frontend_dir / "node_modules"
    return node_modules.exists()

def main():
    print("=" * 50)
    print("  A-Stock Quant - Frontend Server")
    print("=" * 50)
    print()

    project_root = Path(__file__).parent
    frontend_dir = project_root / "frontend"

    if not frontend_dir.exists():
        print(f"[ERROR] frontend directory not found: {frontend_dir}")
        input("Press Enter to exit...")
        return 1

    if not check_nodejs():
        input("Press Enter to exit...")
        return 1

    print("\n[1/2] Checking dependencies...")
    if not check_dependencies(frontend_dir):
        print("Dependencies missing, running npm install...")
        print("This may take a few minutes...")
        os.chdir(frontend_dir)
        try:
            subprocess.run(["npm", "install"], check=True)
            print("[OK] Dependencies installed")
        except subprocess.CalledProcessError:
            print("[ERROR] npm install failed")
            input("Press Enter to exit...")
            return 1
        except Exception as e:
            print(f"[ERROR] Install failed: {e}")
            input("Press Enter to exit...")
            return 1
    else:
        print("[OK] Dependencies already installed")

    print("\n[2/2] Starting frontend dev server...")
    os.chdir(frontend_dir)

    try:
        print("Frontend starting...")
        print("UI: http://localhost:5173")
        print("Press Ctrl+C to stop")
        print("=" * 50)
        print()

        subprocess.run(["npm", "run", "dev"], check=True)

    except KeyboardInterrupt:
        print("\n\nStopped by user (Ctrl+C)")
        return 0
    except subprocess.CalledProcessError:
        print("\n[ERROR] Frontend failed to start")
        print("Check:")
        print("1. npm dependencies installed")
        print("2. Port 5173 is free")
        print("3. Error messages above")
        input("\nPress Enter to exit...")
        return 1
    except Exception as e:
        print(f"\n[ERROR] Unexpected exception: {e}")
        import traceback

        traceback.print_exc()
        input("\nPress Enter to exit...")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n[ERROR] Unexpected exception: {e}")
        import traceback

        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)

