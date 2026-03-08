# MacroPad 双控键盘配置软件架构

## 技术栈

### 运行时选择
| 方案 | 优点 | 缺点 |
|------|------|------|
| **Tauri (Rust + Web)** | ⭐ 最佳：体积小、全平台原生、性能好 | 需要 Rust 环境 |
| Electron | 生态成熟 | 体积大 (~150MB) |
| PyQt | Python 原生 | 需打包、跨平台 UI 不一致 |

**推荐：Tauri 2.x** - 体积小 (~10MB)、原生体验、支持全平台

### 前端
- **Vue 3** + **Vite** - 快速开发
- **Pinia** - 状态管理
- **TailwindCSS** - 样式

---

## 项目结构

```
macropad-config/
├── src/                    # 前端 Vue 代码
│   ├── components/
│   │   ├── KeyMatrix.vue   # 12键可视化配置
│   │   ├── Encoder.vue     # 旋钮配置
│   │   ├── ModeSelector.vue# 模式切换
│   │   └── SerialPanel.vue # 串口连接
│   ├── stores/
│   │   └── config.ts       # 配置状态管理
│   ├── utils/
│   │   └── serial.ts       # 串口通信封装
│   └── App.vue
├── src-tauri/              # Rust 后端
│   ├── src/
│   │   ├── main.rs         # 入口
│   │   ├── serial.rs       # 串口通信
│   │   └── hotkey.rs       # 快捷键生成
│   ├── Cargo.toml
│   └── tauri.conf.json
└── package.json
```

---

## 核心功能

### 1. 设备连接
```typescript
// 串口连接 (前端调用 Rust 命令)
async function connect(port: string): Promise<boolean>
async function disconnect(): Promise<void>
async function sendConfig(config: MacroPadConfig): Promise<void>
async function readConfig(): Promise<MacroPadConfig>
```

### 2. 配置数据模型
```typescript
interface MacroPadConfig {
  version: number;
  currentMode: 'vibe' | 'openclaw';
  modes: {
    vibe: KeyConfig[12];
    openclaw: KeyConfig[12];
  };
}

interface KeyConfig {
  type: 'hotkey' | 'shell' | 'serial' | 'layer';
  label: string;       // OLED 显示文字
  icon: string;        // 图标名
  color: string;       // LED 颜色 (hex)
  // hotkey 类型
  keys?: string[];     // ['cmd', 'shift', 'k']
  // shell 类型  
  command?: string;    // shell 命令
  // serial 类型
  serialMsg?: object;  // JSON 消息给机械臂
}
```

### 3. 快捷键兼容
- **Mac**: Cmd, Option, Control, Shift
- **Windows**: Ctrl, Alt, Win, Shift
- **Linux**: Ctrl, Alt, Super, Shift

自动检测操作系统并转换修饰键：
```rust
fn normalize_modifier(os: &str, key: &str) -> String {
    match (os, key) {
        ("macos", "ctrl") => "cmd",
        ("macos", "alt") => "option",
        ("windows", "cmd") => "ctrl",
        ("linux", "cmd") => "super",
        _ => key
    }
}
```

### 4. 固件通信协议
```
┌─────────────────────────────────────┐
│           USB CDC 串口              │
├─────────────────────────────────────┤
│  帧格式: [CMD:1B] [LEN:1B] [DATA:N] │
├─────────────────────────────────────┤
│  CMD_LIST:                          │
│    0x01 - 获取配置                   │
│    0x02 - 设置配置                   │
│    0x03 - 读取按键状态               │
│    0x04 - 设置 LED                   │
│    0x05 - 设置 OLED                  │
│    0x06 - 发送串口数据               │
│    0xFF - 心跳/保活                  │
└─────────────────────────────────────┘
```

---

## 配置文件格式

保存为 `~/.config/macropad/config.json`:
```json
{
  "version": 1,
  "theme": "dark",
  "defaultMode": "vibe",
  "vibe": {
    "1": {"type": "hotkey", "keys": ["cmd", "l"], "label": "AI Chat", "color": "#3b82f6"},
    ...
  },
  "openclaw": {
    "1": {"type": "shell", "command": "openclaw status", "label": "Status", "color": "#10b981"},
    ...
  }
}
```

---

## 部署方式

### 开发模式
```bash
# 前端
npm install
npm run dev

# Rust 后端
cd src-tauri
cargo build --debug
```

### 构建发布
```bash
# 全平台构建
npm run tauri build

# 输出:
#   target/release/bundle/mac/MacroPad Config.app
#   target/release/bundle/msi/MacroPad Config_1.0.0_x64-setup.exe
#   target/release/deb/macropad-config_1.0.0_amd64.deb
```

---

## 依赖固件 (CircuitPython)

设备端需要烧录 `circuitpython` + 自定义 `code.py`:
```python
# code.py 核心伪代码
import usb_cdc
import json

def handle_command(data):
    cmd = data[0]
    payload = json.loads(data[1:])
    
    if cmd == 0x02:  # 设置配置
        save_config(payload)
    elif cmd == 0x04:  # 设置 LED
        set_led(payload['key'], payload['color'])

# 主循环
while True:
    if usb_cdc.console.in_waiting:
        data = usb_cdc.console.readline()
        handle_command(json.loads(data))
```

---

## 实现计划

1. **Phase 1**: 创建设 Tauri 项目框架
2. **Phase 2**: 实现串口通信 Rust 后端
3. **Phase 3**: Vue 前端 - 设备连接 + 按键配置 UI
4. **Phase 4**: 快捷键兼容层 + 配置文件管理
5. **Phase 5**: 固件端通信协议实现
6. **Phase 6**: 测试 + 打包发布
