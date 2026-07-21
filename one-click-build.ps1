# 一键构建脚本 (PowerShell) - 自动下载 Python + 打包 EXE
# 右键 -> "使用 PowerShell 运行" 即可

$ErrorActionPreference = "Stop"
$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectDir

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  桌面宠物 EXE 一键构建工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# --- 检查 Python ---
$python = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $ver = & $cmd --version 2>&1
        if ($ver -match "Python 3\.") {
            $python = $cmd
            Write-Host "[OK] 找到 $ver" -ForegroundColor Green
            break
        }
    } catch {}
}

if (-not $python) {
    Write-Host "[!] 未找到 Python 3，正在自动安装..." -ForegroundColor Yellow
    
    # 下载 Python 3.12 嵌入式版本
    $pyUrl = "https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe"
    $pyInstaller = "$env:TEMP\python-installer.exe"
    
    Write-Host "    下载 Python 安装程序..."
    Invoke-WebRequest -Uri $pyUrl -OutFile $pyInstaller -UseBasicParsing
    
    Write-Host "    安装 Python (静默模式)..."
    Start-Process -FilePath $pyInstaller -ArgumentList "/quiet", "InstallAllUsers=0", "PrependPath=1", "Include_pip=1" -Wait
    
    # 刷新 PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
    
    # 验证
    try {
        $ver = python --version 2>&1
        Write-Host "[OK] Python 安装完成: $ver" -ForegroundColor Green
        $python = "python"
    } catch {
        Write-Host "[X] Python 安装失败，请手动安装 Python 3.8+" -ForegroundColor Red
        Write-Host "    下载地址: https://www.python.org/downloads/" -ForegroundColor Yellow
        pause
        exit 1
    }
}

# --- 安装依赖 ---
Write-Host ""
Write-Host "[1/3] 安装依赖包..." -ForegroundColor Cyan
& $python -m pip install --upgrade pip --quiet 2>&1 | Out-Null
& $python -m pip install Pillow pyinstaller --quiet 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[X] 依赖安装失败" -ForegroundColor Red
    pause
    exit 1
}
Write-Host "[OK] 依赖安装完成" -ForegroundColor Green

# --- 打包 EXE ---
Write-Host ""
Write-Host "[2/3] 正在打包 EXE (可能需要 1-3 分钟)..." -ForegroundColor Cyan

# 确保资源文件存在
if (-not (Test-Path "character_rgba.png")) {
    Write-Host "[X] 缺少 character_rgba.png 文件" -ForegroundColor Red
    pause
    exit 1
}

& $python -m PyInstaller --onefile --windowed `
    --name "桌面宠物" `
    --add-data "character_rgba.png;." `
    --clean --noconfirm `
    desktop_pet.py 2>&1 | Where-Object { $_ -match "(ERROR|WARNING|Building|Complete)" }

if ($LASTEXITCODE -ne 0) {
    Write-Host "[X] 打包失败" -ForegroundColor Red
    pause
    exit 1
}

# --- 完成 ---
$exePath = "dist\桌面宠物.exe"
if (Test-Path $exePath) {
    $size = [math]::Round((Get-Item $exePath).Length / 1MB, 1)
    Write-Host ""
    Write-Host "[3/3] 构建完成！" -ForegroundColor Green
    Write-Host ""
    Write-Host "  EXE 路径: $exePath" -ForegroundColor White
    Write-Host "  文件大小: ${size} MB" -ForegroundColor White
    Write-Host ""
    Write-Host "  双击即可运行桌面宠物！" -ForegroundColor Yellow
    
    # 询问是否立即运行
    $run = Read-Host "  是否立即运行? (Y/n)"
    if ($run -ne "n" -and $run -ne "N") {
        Start-Process $exePath
    }
} else {
    Write-Host "[X] EXE 文件未生成" -ForegroundColor Red
}

Write-Host ""
pause
