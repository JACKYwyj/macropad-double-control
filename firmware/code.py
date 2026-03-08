"""
MacroPad 双控键盘固件
Vibe Coding + OpenClaw 控制模式
基于 CircuitPython 10.x
"""
import time
import board
import json
import usb_cdc
from digitalio import DigitalInOut, Pull
from adafruit_macropad import MacroPad
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

# ==================== 配置 ====================
CONFIG_VERSION = 1
SERIAL_BAUDRATE = 115200

# ==================== 硬件初始化 ====================
macropad = MacroPad()
keyboard = Keyboard()

# 模式枚举
MODE_VIBE = 0
MODE_OPENCLAW = 1
current_mode = MODE_VIBE

# ==================== 按键配置 ====================
# Vibe Coding 模式 (12键)
vibe_keys = [
    # 1-3: 上下文交互 (蓝色)
    {"label": "AI Chat", "keys": [Keycode.COMMAND, Keycode.L], "color": 0x3B82F6},
    {"label": "+Context", "keys": [Keycode.COMMAND, Keycode.SHIFT, Keycode.L], "color": 0x3B82F6},
    {"label": "Submit", "keys": [Keycode.COMMAND, Keycode.RETURN], "color": 0x3B82F6},
    
    # 4-6: 代码生成 (绿色)
    {"label": "Edit", "keys": [Keycode.COMMAND, Keycode.K], "color": 0x10B981},
    {"label": "Composer", "keys": [Keycode.COMMAND, Keycode.I], "color": 0x10B981},
    {"label": "Full Comp", "keys": [Keycode.COMMAND, Keycode.SHIFT, Keycode.I], "color": 0x10B981},
    
    # 7-9: 审查与终端 (橙/红)
    {"label": "Accept", "keys": [Keycode.TAB], "color": 0xF59E0B},
    {"label": "AI Fix", "keys": [Keycode.COMMAND, Keycode.K], "color": 0xEF4444},
    {"label": "Reject", "keys": [Keycode.ESCAPE], "color": 0xEF4444},
    
    # 10-12: 文件操作 (紫色)
    {"label": "New File", "keys": [Keycode.COMMAND, Keycode.N], "color": 0x8B5CF6},
    {"label": "Save", "keys": [Keycode.COMMAND, Keycode.S], "color": 0x8B5CF6},
    {"label": "Term", "keys": [Keycode.COMMAND, Keycode.GRAVE_ACCENT], "color": 0x8B5CF6},
]

# OpenClaw 控制模式 (12键)
openclaw_keys = [
    # 1-3: Gateway 管理
    {"label": "Status", "action": "shell", "cmd": "openclaw status", "color": 0x10B981},
    {"label": "Restart", "action": "shell", "cmd": "openclaw gateway restart", "color": 0x10B981},
    {"label": "Doctor", "action": "shell", "cmd": "openclaw doctor", "color": 0x10B981},
    
    # 4-6: 技能与工具
    {"label": "Sync", "action": "shell", "cmd": "clawhub sync", "color": 0x3B82F6},
    {"label": "Sessions", "action": "shell", "cmd": "openclaw sessions list", "color": 0x3B82F6},
    {"label": "Test Msg", "action": "shell", "cmd": "echo 'test'", "color": 0x3B82F6},
    
    # 7-9: 硬件控制
    {"label": "Screenshot", "action": "serial", "msg": {"action": "camera_snap"}, "color": 0xF59E0B},
    {"label": "Run Cmd", "action": "shell", "cmd": "openclaw exec ls", "color": 0xF59E0B},
    {"label": "KILL", "action": "shell", "cmd": "pkill -f openclaw", "color": 0xEF4444},
    
    # 10-12: 机械臂控制
    {"label": "Claw Open", "action": "serial", "msg": {"joint": "claw", "angle": 0}, "color": 0xEC4899},
    {"label": "Claw Close", "action": "serial", "msg": {"joint": "claw", "angle": 120}, "color": 0xEC4899},
    {"label": "Home", "action": "serial", "msg": {"action": "home_all"}, "color": 0xEC4899},
]

# 当前模式配置
key_configs = {
    MODE_VIBE: vibe_keys,
    MODE_OPENCLAW: openclaw_keys
}

# ==================== 显示界面 ====================
def draw_display():
    """更新 OLED 显示"""
    macropad.display.text.fill(0)
    
    # 顶部：模式名称
    mode_name = "VIBE CODING" if current_mode == MODE_VIBE else "OPENCLAW"
    macropad.display.text.text(mode_name, 0, 0, 1)
    
    # 显示12个按键标签 (每行4个，共3行)
    config = key_configs[current_mode]
    for i, key in enumerate(config):
        row = i // 4
        col = i % 4
        x = col * 32
        y = 12 + row * 18
        # 截断过长的标签
        label = key["label"][:6]
        macropad.display.text.text(label, x, y, 1)
    
    macropad.display.show()

def set_leds():
    """根据当前模式设置 LED 颜色"""
    config = key_configs[current_mode]
    for i in range(12):
        key_index = macropad.keyboard.keys[i]
        if key_index < 12:
            macropad.pixels[key_index] = config[key_index].get("color", 0xFFFFFF)

def update_encoder_mode():
    """旋钮按下切换模式"""
    global current_mode
    current_mode = (current_mode + 1) % 2
    set_leds()
    draw_display()

# ==================== 命令处理 ====================
def execute_action(config):
    """执行按键动作"""
    action_type = config.get("action", "hotkey")
    
    if action_type == "hotkey":
        # 发送快捷键
        keys = config.get("keys", [])
        if keys:
            keyboard.press(*keys)
            time.sleep(0.05)
            keyboard.release(*keys)
            
    elif action_type == "shell":
        # 通过 USB 串口发送 shell 命令到 PC
        cmd = config.get("cmd", "")
        if cmd and usb_cdc.console:
            usb_cdc.console.write(f"SHELL:{cmd}\n".encode())
            
    elif action_type == "serial":
        # 通过串口发送 JSON 给机械臂
        msg = config.get("msg", {})
        if usb_cdc.console:
            usb_cdc.console.write(f"SERIAL:{json.dumps(msg)}\n".encode())

# ==================== 串口通信 ====================
def handle_serial_command(data: str):
    """处理来自 PC 的串口命令"""
    try:
        if data.startswith("SHELL:"):
            # 执行 shell 命令 (由 PC 端执行)
            pass
        elif data.startswith("SERIAL:"):
            # 转发给机械臂
            pass
        elif data.startswith("CONFIG:"):
            # 接收新配置
            pass
    except Exception as e:
        print(f"Error: {e}")

# ==================== 主循环 ====================
def main():
    # 初始化显示
    draw_display()
    set_leds()
    
    # 记录上次编码器位置
    last_encoder = macropad.encoder
    
    print(f"MacroPad Firmware v{CONFIG_VERSION} Ready")
    print(f"Mode: {'VIBE CODING' if current_mode == 'MODE_VIBE' else 'OPENCLAW'}")
    
    while True:
        # 按键事件处理
        event = macropad.keys.events.get()
        if event:
            key_number = event.key_number
            if event.pressed:
                # 执行对应按键的动作
                config = key_configs[current_mode][key_number]
                execute_action(config)
                # 视觉反馈：闪烁
                macropad.pixels[key_number] = 0xFFFFFF
                time.sleep(0.1)
                set_leds()
        
        # 旋钮按下：切换模式
        if macropad.encoder_switch:
            update_encoder_mode()
            time.sleep(0.2)  # 防抖
        
        # 旋钮旋转：在 OpenClaw 模式下可作为参数调节
        encoder_delta = macropad.encoder - last_encoder
        if encoder_delta != 0 and current_mode == MODE_OPENCLAW:
            # 可以发送增量值给 PC
            if usb_cdc.console:
                usb_cdc.console.write(f"ENCODER:{encoder_delta}\n".encode())
        last_encoder = macropad.encoder
        
        # 处理串口命令
        if usb_cdc.console and usb_cdc.console.in_waiting:
            data = usb_cdc.console.readline()
            handle_serial_command(data.decode())
        
        time.sleep(0.01)

if __name__ == "__main__":
    main()
