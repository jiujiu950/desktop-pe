# 🐱 桌面宠物 Desktop Pet

一个可爱的桌面宠物程序，基于你提供的角色图片制作。

## ✨ 功能特性

- 🖼️ **透明背景** - 角色悬浮在桌面上，无白底遮挡
- 📌 **窗口置顶** - 始终在最前面显示
- 🖱️ **拖拽移动** - 鼠标左键拖动角色位置
- 🎭 **8种互动** - 点击角色触发随机动画：
  - 跳跃、压扁回弹、左右抖动
  - 吃蛋糕、卖萌、微笑、生气、哭泣
- 💬 **对话气泡** - 互动时显示随机中文对话
- 🔧 **右键菜单** - 调整大小 / 置顶开关 / 退出
- 📏 **滚轮缩放** - 鼠标滚轮调整角色大小

## 🚀 快速开始

### 方法一：直接运行 EXE（推荐）

双击 `桌面宠物.exe` 即可运行，无需安装任何软件。

### 方法二：从源码运行

```bash
# 安装依赖
pip install Pillow

# 运行
python desktop_pet.py
```

### 方法三：一键自动打包（推荐 Windows 用户）

1. 将整个 `desktop-pet` 文件夹复制到 Windows
2. 右键 `one-click-build.ps1` → "使用 PowerShell 运行"
3. 脚本会自动安装 Python + 依赖 + 打包 EXE

### 方法四：手动打包

```cmd
pip install Pillow pyinstaller
pyinstaller --onefile --windowed --name "桌面宠物" --add-data "character_rgba.png;." desktop_pet.py
```

### 方法五：GitHub Actions 云端构建

1. 将项目推送到 GitHub 仓库
2. Actions 会自动构建 Windows EXE
3. 在 Actions → Artifacts 下载

## 📁 文件说明

| 文件 | 说明 |
|------|------|
| `desktop_pet.py` | 主程序代码 |
| `character_rgba.png` | 处理后的透明背景角色图 |
| `build.bat` | Windows 构建脚本 |
| `build.sh` | Linux/macOS 构建脚本 |
| `README.md` | 本说明文件 |

## 🎮 操作指南

| 操作 | 效果 |
|------|------|
| 左键点击角色 | 触发随机动画+对话 |
| 左键拖拽角色 | 移动位置 |
| 右键点击 | 打开菜单 |
| 鼠标滚轮 | 调整大小 |

## ⚙️ 自定义

### 修改对话内容

在 `desktop_pet.py` 中找到 `BUBBLE_TEXTS` 字典，修改对应动画的对话列表即可。

### 修改动画效果

每种动画都有独立的函数（如 `anim_jump`、`anim_shake` 等），可以调整参数或添加新动画。

### 修改默认大小

修改 `self.base_scale` 的初始值（0.15~0.60）。

## 📋 系统要求

- Windows 7/10/11
- 屏幕分辨率：1024×768 或更高
- 如果从源码运行：Python 3.8+，Pillow 库
