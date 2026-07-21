#!/bin/bash
# Linux/macOS 构建脚本（跨平台编译需要 Windows 环境）
echo "========================================"
echo "  桌面宠物 EXE 构建脚本"
echo "========================================"

# 安装依赖
pip install Pillow pyinstaller --quiet

# 构建
pyinstaller --onefile --windowed \
    --name "桌面宠物" \
    --add-data "character_rgba.png:." \
    --clean \
    desktop_pet.py

echo ""
echo "构建完成！EXE 文件在 dist/ 目录下"
