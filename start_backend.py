"""
启动后端服务器
"""
import os
import sys
import subprocess
from pathlib import Path

# Ensure project root is importable for utils.console_fix
sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.console_fix import configure_console

configure_console()


def check_python():
    """检查Python是否安装"""
    try:
        result = subprocess.run(
            [sys.executable, "--version"],
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            errors="replace",
        )
        print(f"[OK] Python version: {result.stdout.strip()}")
        return True
    except Exception as e:
        print(f"[ERROR] Python check failed: {e}")
        return False


def check_venv():
    """检查虚拟环境是否存在"""
    project_root = Path(__file__).parent
    if os.name == "nt":
        venv_python = project_root / "venv" / "Scripts" / "python.exe"
    else:
        venv_python = project_root / "venv" / "bin" / "python"
    return venv_python.exists()


def get_python_executable():
    """获取Python可执行文件路径"""
    project_root = Path(__file__).parent
    if check_venv():
        if os.name == "nt":
            return project_root / "venv" / "Scripts" / "python.exe"
        return project_root / "venv" / "bin" / "python"
    return Path(sys.executable)


def main():
    print("=" * 50)
    print("  A-Stock Quant - Backend Server")
    print("=" * 50)
    print()

    project_root = Path(__file__).parent
    os.chdir(project_root)

    if check_venv():
        print("[1/2] [OK] Virtual environment detected")
        python_exe = get_python_executable()
    else:
        print("[WARN] Virtual environment not found")
        print("Tip: run setup_venv.py first")
        print()
        choice = input("Continue with system Python? (Y/N): ").strip().upper()
        if choice != "Y":
            print("Cancelled. Please run setup_venv.py first.")
            input("Press Enter to exit...")
            return 1

        if not check_python():
            print("[ERROR] Python not found. Please install Python 3.8+")
            input("Press Enter to exit...")
            return 1

        python_exe = Path(sys.executable)

    print("\n[2/2] Starting backend server...")
    backend_dir = project_root / "backend"

    if not backend_dir.exists():
        print(f"[ERROR] backend directory not found: {backend_dir}")
        input("Press Enter to exit...")
        return 1

    os.chdir(backend_dir)

    try:
        print(f"Python: {python_exe}")
        print("Backend starting...")
        print("API docs: http://localhost:8000/api/docs")
        print("Press Ctrl+C to stop")
        print("=" * 50)
        print()

        # Prefer UTF-8 for child process on Windows
        env = os.environ.copy()
        env.setdefault("PYTHONIOENCODING", "utf-8")
        env.setdefault("PYTHONUTF8", "1")

        subprocess.run(
            [str(python_exe), "main.py"],
            check=True,
            env=env,
        )

    except KeyboardInterrupt:
        print("\n\nStopped by user (Ctrl+C)")
        return 0
    except subprocess.CalledProcessError:
        print("\n[ERROR] Backend failed to start")
        print("Check:")
        print("1. Python dependencies installed")
        print("2. Port 8000 is free")
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
