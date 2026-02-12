# Docker 安装指南

## Windows 安装 Docker

### 方法1：Docker Desktop（推荐）

1. **下载 Docker Desktop**
   - 访问：https://www.docker.com/products/docker-desktop/
   - 点击 "Download for Windows"
   - 下载 `Docker Desktop Installer.exe`

2. **安装 Docker Desktop**
   - 运行安装程序
   - 按照向导完成安装
   - **重要**：安装过程中确保勾选所有选项
   - 安装完成后会要求重启电脑

3. **启动 Docker Desktop**
   - 安装完成后，从开始菜单启动 "Docker Desktop"
   - 等待 Docker 启动完成（系统托盘会显示 Docker 图标）
   - 首次启动可能需要几分钟

4. **验证安装**
   - 打开命令提示符（CMD）或 PowerShell
   - 运行：
     ```bash
     docker --version
     docker-compose --version
     ```
   - 如果显示版本号，说明安装成功

### 方法2：使用 WSL 2（高级用户）

如果已安装 WSL 2，可以在 WSL 2 中安装 Docker：

```bash
# 在 WSL 2 中运行
sudo apt-get update
sudo apt-get install docker.io docker-compose
```

## 安装后操作

### 1. 验证 Docker 是否运行

打开 Docker Desktop，确保状态显示为 "Running"

### 2. 测试 Docker

```bash
# 运行测试容器
docker run hello-world
```

如果看到 "Hello from Docker!" 消息，说明 Docker 正常工作。

### 3. 启动量化交易系统

```bash
# 使用 Python 脚本（推荐）
python start_docker.py

# 或直接使用 docker-compose
docker-compose up --build
```

## 常见问题

### Q1: Docker Desktop 启动失败

**可能原因：**
- WSL 2 未安装或未启用
- 虚拟化未启用

**解决：**
1. 确保已安装 WSL 2
2. 在 BIOS 中启用虚拟化（Virtualization）
3. 在 Windows 功能中启用 "Hyper-V" 或 "Windows Subsystem for Linux"

### Q2: 端口被占用

**错误：** `Bind for 0.0.0.0:8000 failed: port is already allocated`

**解决：**
- 修改 `docker-compose.yml` 中的端口映射
- 或停止占用端口的其他服务

### Q3: 构建速度慢

**原因：** 首次构建需要下载镜像

**解决：**
- 使用国内镜像源（配置 Docker 镜像加速）
- 或耐心等待首次构建完成

### Q4: 权限问题（Linux）

**错误：** `permission denied while trying to connect to the Docker daemon socket`

**解决：**
```bash
sudo usermod -aG docker $USER
# 重新登录或重启
```

## 下一步

安装完成后，查看 [DOCKER_GUIDE.md](DOCKER_GUIDE.md) 了解如何使用 Docker 启动系统。

