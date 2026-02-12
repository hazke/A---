#!/bin/bash
# 后端启动脚本

echo "启动A股量化交易系统后端..."
cd "$(dirname "$0")"
python main.py

