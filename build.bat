@echo off
chcp 65001 >nul 2>&1
echo.
echo ========================================
echo   桌面宠物 EXE 构建脚本
echo ========================================
echo.

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python
    echo.
    echo 请先安装 Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    echo 安装时请勾选 "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

:: 安装依赖
echo [1/3] 安装依赖...
pip install Pillow pyinstaller --quiet
if errorlevel 1 (
    echo [错误] 依赖安装失败，请检查网络连接
    pause
    exit /b 1
)
echo [OK] 依赖安装完成

:: 构建 EXE
echo.
echo [2/3] 正在打包 EXE (可能需要 1-3 分钟)...
pyinstaller --onefile --windowed ^
    --name "桌面宠物" ^
    --add-data "character_rgba.png;." ^
    --clean --noconfirm ^
    desktop_pet.py

if errorlevel 1 (
    echo.
    echo [错误] 打包失败
    pause
    exit /b 1
)

:: 完成
echo.
echo [3/3] 构建完成！
echo.
echo   EXE 文件: dist\桌面宠物.exe
echo.
echo   双击即可运行桌面宠物！
echo.
pause
