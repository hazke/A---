# Node.js 安装问题解决

## 快速诊断

如果看到错误：`'npm' is not recognized as an internal or external command`

**原因：** Node.js 未安装或未添加到系统 PATH

## 快速解决

### 1. 安装 Node.js

访问：**https://nodejs.org/**

- 下载 **LTS 版本**（推荐 18.x 或 20.x）
- 运行安装程序
- **重要**：确保勾选 "Add to PATH"

### 2. 重启终端

安装完成后：
- 关闭所有终端窗口
- 重新打开终端
- 验证：`node --version` 和 `npm --version`

### 3. 重新启动前端

```bash
python start_frontend.py
```

## 详细指南

查看 `install_nodejs_guide.md` 获取完整安装指南。

## 验证安装

运行环境检查：

```bash
python check_environment.py
```

这会检查所有依赖，包括 Node.js。

