# MacroPad Dual-Control Keyboard
[English](./README_EN.md) | [中文](./README.md) | [日本語](./README_JP.md)

---

## Overview

A dual-mode keyboard system based on **Adafruit MacroPad RP2040**, supporting both **Vibe Coding** and **OpenClaw AI Agent** control.

## Features

- ✅ **12 Programmable Keys** - 12 shortcuts for each mode
- ✅ **Rotary Encoder** - Vibe: Diff navigation / OpenClaw: Message scroll
- ✅ **LED Status** - Blue=Vibe mode / Green=OpenClaw mode
- ✅ **Cross-Platform** - Mac/Windows/Linux plug-and-play
- ✅ **Auto-Execute** - Keys auto-send Enter

## Hardware

- Adafruit MacroPad RP2040
- Cherry MX compatible switches (12)
- Keycaps (12)

See [HARDWARE.md](./HARDWARE.md)

## Quick Start

### 1. Flash Firmware

1. Hold **BOOT** + **RESET** to enter bootloader
2. Download [CircuitPython firmware](https://circuitpython.org/board/adafruit_macropad_rp2040/)
3. Drag `.uf2` to RPI-RP2 drive

### 2. Install Libraries

```bash
pip install circup
circup install adafruit_macropad
```

### 3. Deploy

Copy `firmware/code.py` to CIRCUITPY root

## Key Functions

### Vibe Coding Mode (Blue LED)

| Key | Function | Shortcut |
|-----|----------|----------|
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

**Encoder**: Diff navigation

### OpenClaw Mode (Green LED)

| Key | Function | Command |
|-----|----------|---------|
| 1 | Status | openclaw status |
| 2 | Restart | openclaw gateway restart |
| 3 | Doctor | openclaw doctor |
| 4 | Sync | clawhub sync |
| 5 | Sessions | openclaw sessions list |
| 6 | Test | echo test |
| 7 | Device | openclaw nodes device_status |
| 8 | Run | openclaw exec ls |
| 9 | KILL | pkill -f openclaw |

**Encoder**: Message scroll

### Mode Switch

- **Encoder press**: Switch Vibe Coding ↔ OpenClaw mode

## Links

- [Adafruit MacroPad Docs](https://learn.adafruit.com/adafruit-macropad-rp2040)
- [CircuitPython](https://circuitpython.org/)
- [OpenClaw](https://github.com/openclaw/openclaw)

## License

MIT License
