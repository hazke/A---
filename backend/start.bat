@echo off
REM 后端启动脚本（Windows）

echo 启动A股量化交易系统后端...
cd /d %~dp0
python main.py
pause

