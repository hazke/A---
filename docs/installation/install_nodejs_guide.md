# Node.js 安装指南

## 问题
如果看到错误：`'npm' is not recognized as an internal or external command`

这表示 Node.js 和 npm 没有安装或未添加到系统 PATH。

## 解决方案

### 方法1：安装 Node.js（推荐）

1. **访问 Node.js 官网**
   - 打开浏览器访问：https://nodejs.org/
   - 或直接访问：https://nodejs.org/zh-cn/

2. **下载 LTS 版本**
   - 点击绿色的 "LTS" 按钮下载
   - LTS（Long Term Support）版本更稳定，推荐使用
   - 推荐版本：Node.js 18.x 或 20.x

3. **安装 Node.js**
   - 运行下载的安装程序（.msi 文件）
   - 按照安装向导操作
   - **重要**：确保勾选 "Add to PATH" 选项（通常默认已勾选）

4. **验证安装**
   - 关闭所有终端窗口
   - 重新打开命令提示符（CMD）或 PowerShell
   - 运行以下命令：
     ```bash
     node --version
     npm --version
     ```
   - 如果显示版本号，说明安装成功

### 方法2：使用包管理器安装（高级用户）

**使用 Chocolatey（Windows）：**
```bash
choco install nodejs-lts
```

**使用 Scoop（Windows）：**
```bash
scoop install nodejs-lts
```

**使用 Homebrew（Mac）：**
```bash
brew install node
```

**使用 apt（Linux）：**
```bash
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
```

## 安装后操作

1. **重启终端**
   - 关闭所有终端窗口
   - 重新打开新的终端

2. **验证安装**
   ```bash
   node --version
   npm --version
   ```

3. **重新运行前端启动脚本**
   ```bash
   python start_frontend.py
   ```

## 常见问题

### Q1: 安装后仍然找不到 npm
**解决：**
- 重启电脑（确保环境变量生效）
- 检查 PATH 环境变量是否包含 Node.js 安装路径
- 通常路径为：`C:\Program Files\nodejs\`

### Q2: 如何检查 PATH 环境变量？
**Windows：**
1. 右键"此电脑" → "属性"
2. 点击"高级系统设置"
3. 点击"环境变量"
4. 在"系统变量"中找到"Path"
5. 检查是否包含 Node.js 路径

### Q3: 安装哪个版本？
**推荐：**
- Node.js 18.x LTS（最稳定）
- Node.js 20.x LTS（最新LTS版本）

### Q4: 安装后需要重启电脑吗？
**建议：**
- 重启终端即可
- 如果仍然不行，重启电脑

## 快速检查脚本

运行以下命令检查 Node.js 是否已安装：

```bash
python check_environment.py
```

这会检查所有依赖，包括 Node.js。

## 安装完成后

安装 Node.js 后，运行：

```bash
# 进入前端目录
cd frontend

# 安装依赖（只需一次）
npm install

# 启动前端
npm run dev
```

或使用启动脚本：

```bash
python start_frontend.py
```

