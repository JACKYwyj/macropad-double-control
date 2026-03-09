# MacroPad 双控键盘
[English](./README_EN.md) | [中文](./README.md) | [日本語](./README_JP.md)

---

## 概述

基于 Adafruit MacroPad RP2040 的双控键盘系统，同时支持 **Vibe Coding** 和 **OpenClaw AI 代理**控制。

![MacroPad](https://img.shields.io/badge/Hardware-Adafruit%20MacroPad%20RP2040-blue)
![CircuitPython](https://img.shields.io/badge/Firmware-CircuitPython%2010.x-green)

## 功能特点

- ✅ **12 个可编程按键** - 两种模式各 12 个快捷键
- ✅ **旋钮控制** - Vibe 模式代码 Diff 导航 / OpenClaw 模式消息滚动
- ✅ **LED 状态指示** - 蓝色=Vibe 模式 / 绿色=OpenClaw 模式
- ✅ **跨平台兼容** - Mac/Windows/Linux 即插即用
- ✅ **命令自动执行** - 按键自动发送回车符

## 硬件要求

- Adafruit MacroPad RP2040
- Cherry MX 兼容机械轴 (12个)
- 键帽 (12个)

详见 [HARDWARE.md](./HARDWARE.md)

## 快速开始

### 1. 烧录固件

1. 按住 **BOOT** 按钮 + **RESET** 进入 bootloader
2. 下载 [CircuitPython 固件](https://circuitpython.org/board/adafruit_macropad_rp2040/)
3. 将 `.uf2` 文件拖入 RPI-RP2 驱动器

### 2. 安装库

```bash
pip install circup
circup install adafruit_macropad
```

### 3. 部署固件

将 `firmware/code.py` 复制到 CIRCUITPY 根目录

## 按键功能

### Vibe Coding 模式 (蓝色 LED)

| 按键 | 功能 | 快捷键 |
|------|------|--------|
| 1 | AI Chat | Cmd+L |
| 2 | +Context | Cmd+Shift+L |
| 3 | Submit | Cmd+Return |
| 4 | Edit | Cmd+K |
| 5 | Composer | Cmd+I |
| 6 | FullComp | Cmd+Shift+I |
| 7 | Accept | Tab |
| 8 | AI Fix | Cmd+K |
| 9 | Reject | Esc |
| 10 | New | Cmd+N |
| 11 | Save | Cmd+S |
| 12 | Terminal | Cmd+` |

**旋钮旋转**: 代码 Diff 导航

### OpenClaw 模式 (绿色 LED)

| 按键 | 功能 | 命令 |
|------|------|------|
| 1 | Status | openclaw status |
| 2 | Restart | openclaw gateway restart |
| 3 | Doctor | openclaw doctor |
| 4 | Sync | clawhub sync |
| 5 | Sessions | openclaw sessions list |
| 6 | Test | echo test |
| 7 | Device | openclaw nodes device_status |
| 8 | Run | openclaw exec ls |
| 9 | KILL | pkill -f openclaw |

**旋钮旋转**: 消息历史滚动

### 模式切换

- **旋钮按下**: 切换 Vibe Coding ↔ OpenClaw 模式

## 故障排除

详见 [HARDWARE.md](./HARDWARE.md#故障排除)

## 相关链接

- [Adafruit MacroPad 官方文档](https://learn.adafruit.com/adafruit-macropad-rp2040)
- [CircuitPython](https://circuitpython.org/)
- [OpenClaw](https://github.com/openclaw/openclaw)

## 许可证与使用声明

MIT License

**⚠️ 禁止商用声明**
本项目仅供个人学习交流使用，禁止任何形式的商业用途。包括但不限于：
- 禁止用于商业产品或服务
- 禁止二次销售或授权他人使用
- 禁止在商业项目中引用本代码

如需商用授权，请联系作者。
