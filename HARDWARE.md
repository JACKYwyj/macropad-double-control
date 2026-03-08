# MacroPad 双控键盘 - 硬件需求与配置说明

## 硬件清单

### 1. 核心设备
| 设备 | 型号/规格 | 数量 | 说明 |
|------|----------|------|------|
| 主控制器 | Adafruit MacroPad RP2040 | 1 | 3x4 机械键盘矩阵 + OLED + 旋钮 |
| 机械轴体 | Cherry MX 兼容 | 12 | 建议使用青轴/红轴 |
| 键帽 | Cherry MX 兼容 | 12 | 根据个人喜好选择 |

### 2. 可选扩展设备
| 设备 | 型号/规格 | 数量 | 说明 |
|------|----------|------|------|
| PWM 驱动板 | Adafruit PCA9685 | 1 | 16通道舵机控制 |
| 舵机 | MG996R / SG90 | 1-6 | 机械臂关节 |
| STEMMA QT 线缆 | 4Pin JST-SH | 1 | 连接 MacroPad 与 PCA9685 |
| 独立电源 | 5V 2A | 1 | 舵机供电 (必须独立!) |

---

## 硬件连接图

```
                    ┌─────────────────┐
                    │   Mac/PC        │
                    │   (USB-C)       │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  MacroPad RP2040 │
                    │                  │
                    │  12 Keys        │
                    │  1 Rotary       │
                    │  1 OLED         │
                    │  STEMMA QT (I2C)│
                    └────────┬────────┘
                             │ I2C (SDA/SCL)
                    ┌────────▼────────┐
                    │   PCA9685       │
                    │   16ch PWM      │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
        ┌─────▼─────┐  ┌────▼────┐  ┌────▼────┐
        │  舵机 1   │  │  舵机 2 │  │  舵机 N │
        └───────────┘  └─────────┘  └─────────┘
        
        ⚠️ 重要: 舵机必须使用独立电源供电!
```

---

## 电源配置 (关键!)

### ❌ 错误做法
- 直接从 MacroPad 的 USB 取电给舵机
- 从 MacroPad 的 3.3V 或 5V 引脚取电

**后果**: 电压骤降导致 RP2040 重启，甚至可能烧毁 USB 控制器

### ✅ 正确做法
1. **MacroPad**: 通过 USB-C 连接到电脑 (仅供电 + 数据)
2. **PCA9685**: 
   - V+ 端子接独立 5V/6V 电源 (2A 以上)
   - VCC 接 MacroPad 的 3.3V (逻辑电平)
   - GND 共地
3. **舵机**: 全部接到 PCA9685 的 PWM 通道

---

## 软件环境

### 1. 固件烧录
1. 进入 Bootloader 模式:
   - 按住 **BOOT** 按钮 (旋钮中心)
   - 按一下 **RESET**
   - 松开 BOOT
2. 电脑识别为 **RPI-RP2** 驱动器
3. 下载 CircuitPython 固件:
   - https://circuitpython.org/board/adafruit_macropad_rp2040/
4. 将 `.uf2` 文件拖入 RPI-RP2
5. 自动重启后识别为 **CIRCUITPY**

### 2. 库文件安装
```bash
# 安装 circup
pip3 install circup

# 连接 MacroPad 后运行
circup install adafruit_macropad
```

### 3. 固件部署
将 `firmware/code.py` 复制到 CIRCUITPY 根目录

---

## 功能说明

### 模式 1: Vibe Coding (蓝色 LED)
| 按键 | 功能 | 快捷键 |
|------|------|--------|
| 1 | AI Chat | Cmd + L |
| 2 | +Context | Cmd + Shift + L |
| 3 | Submit | Cmd + Return |
| 4 | Edit | Cmd + K |
| 5 | Composer | Cmd + I |
| 6 | FullComp | Cmd + Shift + I |
| 7 | Accept | Tab |
| 8 | AI Fix | Cmd + K |
| 9 | Reject | Esc |
| 10 | New | Cmd + N |
| 11 | Save | Cmd + S |
| 12 | Terminal | Cmd + ` |

### 模式 2: OpenClaw 控制 (绿色 LED)
| 按键 | 功能 |
|------|------|
| 1 | Status |
| 2 | Restart Gateway |
| 3 | Doctor |
| 4 | Sync Skills |
| 5 | Sessions List |
| 6 | Test Message |
| 7 | Screenshot |
| 8 | Run Command |
| 9 | KILL (急停) |
| 10 | Claw Open |
| 11 | Claw Close |
| 12 | Home All |

### 旋钮操作
- **按下**: 切换 Vibe Coding ↔ OpenClaw 模式
- **旋转**: 参数调节 (预留)

---

## 故障排查

### 问题: 屏幕显示 Error
**解决方案**:
1. 确保库文件完整安装: `circup install adafruit_macropad`
2. 重新烧录 CircuitPython 固件
3. 检查 USB-C 连接线是否支持数据传输 (不要用充电线)

### 问题: 按键无响应
**检查**:
1. 机械轴是否正确安装
2. 是否使用了正确的引脚定义 (board.KEY1-KEY12)

### 问题: LED 不亮
**检查**:
1. NeoPixel 库是否安装: `circup install neopixel`
2. 代码中是否正确初始化 `neopixel.NeoPixel(board.NEOPIXEL, 12)`

---

## 安全注意事项

1. **舵机电源必须独立** - 禁止从 MacroPad 取电
2. **急停功能** - OpenClaw 模式下 Key 9 可强制终止代理
3. **物理覆盖** - 硬件开关优先于软件控制
4. **Docker 隔离** - 建议将 OpenClaw 部署在容器中运行

---

## 扩展开发

### 添加新功能
修改 `firmware/code.py` 中的 `vibe_actions` 或 `openclaw_actions` 数组:

```python
# 添加新的快捷键
([Keycode.COMMAND, Keycode.X], "你的功能"),
```

### 添加机械臂控制
1. 连接 PCA9685 (通过 STEMMA QT)
2. 在代码中添加舵机控制逻辑
3. 通过串口接收 PC 端命令

---

## 参考链接

- [Adafruit MacroPad RP2040 官方文档](https://learn.adafruit.com/adafruit-macropad-rp2040)
- [CircuitPython 库下载](https://circuitpython.org/libraries)
- [OpenClaw 官方仓库](https://github.com/openclaw/openclaw)
