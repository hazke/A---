"""
配置 Docker Desktop 镜像加速（拉取 python/node 等基础镜像）
运行后需重启 Docker Desktop 生效。
"""
import json
import sys
from pathlib import Path

# 2026-07 亲测可用（docker pull node:20-alpine 成功）
REGISTRY_MIRRORS = [
    "https://docker.1ms.run",
    "https://docker.xuanyuan.me",
]

# 已失效或限流的镜像，配置时会自动移除
BROKEN_MIRRORS = {
    "https://docker.m.daocloud.io",
    "https://docker.1panel.live",
    "https://dockerpull.com",
}


def get_daemon_path() -> Path:
    return Path.home() / ".docker" / "daemon.json"


def load_daemon_config(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"[警告] 现有 daemon.json 格式有误，将重新写入: {e}")
    return {}


def configure_registry_mirrors() -> bool:
    daemon_path = get_daemon_path()
    daemon_path.parent.mkdir(parents=True, exist_ok=True)

    config = load_daemon_config(daemon_path)
    existing = [
        m for m in config.get("registry-mirrors", [])
        if m not in BROKEN_MIRRORS and m not in REGISTRY_MIRRORS
    ]
    config["registry-mirrors"] = list(dict.fromkeys(REGISTRY_MIRRORS + existing))

    daemon_path.write_text(
        json.dumps(config, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    removed = [m for m in BROKEN_MIRRORS if m in config.get("registry-mirrors", [])]
    print("=" * 50)
    print("  Docker 镜像加速已配置")
    print("=" * 50)
    print(f"配置文件: {daemon_path}")
    print("registry-mirrors:")
    for mirror in config["registry-mirrors"]:
        print(f"  - {mirror}")
    print()
    print("已移除失效镜像:")
    for mirror in sorted(BROKEN_MIRRORS):
        print(f"  - {mirror}")
    print()
    print("请重启 Docker Desktop 使配置生效：")
    print("  右键托盘图标 -> Restart")
    print()
    return True


def main() -> int:
    try:
        configure_registry_mirrors()
        return 0
    except Exception as e:
        print(f"[错误] 配置失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
