"""
MacroPad 双控键盘固件 V2
Vibe Coding + OpenClaw 控制模式

功能:
- 12个按键发送快捷键
- 旋钮按下切换模式
- 旋钮旋转实现:
  - Vibe模式: 代码Diff导航 (Option+F7)
  - OpenClaw模式: 消息历史滚动 (Option+上下箭头)
- LED颜色指示当前模式
"""
import board
import digitalio
import neopixel
import time
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

print("Init...")

# ===== 按键初始化 =====
keys = []
for key_pin in [board.KEY1, board.KEY2, board.KEY3, board.KEY4, board.KEY5, board.KEY6,
                board.KEY7, board.KEY8, board.KEY9, board.KEY10, board.KEY11, board.KEY12]:
    k = digitalio.DigitalInOut(key_pin)
    k.direction = digitalio.Direction.INPUT
    k.pull = digitalio.Pull.UP
    keys.append(k)

# ===== LED =====
pixels = neopixel.NeoPixel(board.NEOPIXEL, 12)

# ===== HID 键盘 =====
keyboard = Keyboard(usb_hid.devices)

# ===== 旋钮开关 =====
encoder_switch = digitalio.DigitalInOut(board.ENCODER_SWITCH)
encoder_switch.direction = digitalio.Direction.INPUT
encoder_switch.pull = digitalio.Pull.UP

# ===== 旋钮编码器 (ROTA, ROTB) =====
rot_a = digitalio.DigitalInOut(board.ROTA)
rot_a.direction = digitalio.Direction.INPUT
rot_a.pull = digitalio.Pull.UP

rot_b = digitalio.DigitalInOut(board.ROTB)
rot_b.direction = digitalio.Direction.INPUT
rot_b.pull = digitalio.Pull.UP

# ===== 配置 =====
COLOR_VIBE = (0, 0, 255)        # 蓝色 - Vibe Coding
COLOR_OPENCLAW = (0, 255, 0)     # 绿色 - OpenClaw 控制

mode = 0  # 0=Vibe Coding, 1=OpenClaw

# ===== 旋钮状态 =====
encoder_state = 0  # 0=00, 1=01, 2=11, 3=10
last_encoder_delta = 0

# ===== 按键配置 =====
# Vibe Coding 模式快捷键 (Cursor/Windsurf)
vibe_actions = [
    # 第1行: 上下文交互
    ([Keycode.L], "AI Chat", "Cmd+L"),
    ([Keycode.L], "+Context", "Cmd+Shift+L"),
    ([Keycode.RETURN], "Submit", "Cmd+Return"),
    
    # 第2行: 代码生成
    ([Keycode.K], "Edit", "Cmd+K"),
    ([Keycode.I], "Composer", "Cmd+I"),
    ([Keycode.I], "FullComp", "Cmd+Shift+I"),
    
    # 第3行: 审查
    ([Keycode.TAB], "Accept", "Tab"),
    ([Keycode.K], "AI Fix", "Cmd+K"),
    ([Keycode.ESCAPE], "Reject", "Esc"),
    
    # 第4行: 文件操作
    ([Keycode.N], "New", "Cmd+N"),
    ([Keycode.S], "Save", "Cmd+S"),
    ([Keycode.GRAVE_ACCENT], "Term", "Cmd+`"),
]

# OpenClaw 控制模式
openclaw_actions = [
    # 第1行: Gateway管理
    ("Status", "openclaw status"),
    ("Restart", "openclaw gateway restart"),
    ("Doctor", "openclaw doctor"),
    
    # 第2行: 技能工具
    ("Sync", "clawhub sync"),
    ("Sessions", "openclaw sessions list"),
    ("Test", "echo test"),
    
    # 第3行: 硬件控制
    ("Screen", "openclaw browser screenshot"),
    ("Run", "openclaw exec ls"),
    ("KILL", "pkill -f openclaw"),
    
    # 第4行: 预留
    ("Msg1", "echo message 1"),
    ("Msg2", "echo message 2"),
    ("Msg3", "echo message 3"),
]

# ===== 发送快捷键 =====
def send_shortcut(key_codes):
    """发送快捷键组合"""
    # 先按下修饰键
    for key in key_codes:
        if key in [Keycode.COMMAND, Keycode.CONTROL, Keycode.OPTION, Keycode.SHIFT]:
            keyboard.press(key)
    time.sleep(0.02)
    
    # 再按功能键
    for key in key_codes:
        if key not in [Keycode.COMMAND, Keycode.CONTROL, Keycode.OPTION, Keycode.SHIFT]:
            keyboard.press(key)
    time.sleep(0.05)
    
    keyboard.release_all()

# ===== 旋钮读取 =====
def read_encoder():
    """读取旋钮增量"""
    global encoder_state
    a = rot_a.value
    b = rot_b.value
    current = (a << 1) | b
    
    delta = 0
    if encoder_state == 0 and current == 1:
        delta = 1
    elif encoder_state == 1 and current == 3:
        delta = 1
    elif encoder_state == 3 and current == 2:
        delta = 1
    elif encoder_state == 2 and current == 0:
        delta = 1
    elif encoder_state == 0 and current == 2:
        delta = -1
    elif encoder_state == 2 and current == 3:
        delta = -1
    elif encoder_state == 3 and current == 1:
        delta = -1
    elif encoder_state == 1 and current == 0:
        delta = -1
    
    encoder_state = current
    return delta

# ===== LED 动画 =====
def led_animation():
    for i in range(12):
        pixels[i] = COLOR_VIBE
        time.sleep(0.02)
    time.sleep(0.2)
    pixels.fill((0, 0, 0))

led_animation()
print("Ready!")
print("Mode: VIBE CODING")

# ===== 主循环 =====
while True:
    # ===== 按键检测 =====
    for i, key in enumerate(keys):
        if not key.value:
            current_color = COLOR_VIBE if mode == 0 else COLOR_OPENCLAW
            
            if mode == 0:
                key_codes, label, shortcut = vibe_actions[i]
                send_shortcut(key_codes)
                print(f"Vibe: {label}")
            else:
                label, cmd = openclaw_actions[i]
                print(f"OpenClaw: {label}")
            
            # LED 反馈
            pixels[i] = (255, 255, 255)
            time.sleep(0.1)
            pixels[i] = current_color
    
    # ===== 旋钮按下 - 切换模式 =====
    if not encoder_switch.value:
        mode = 1 - mode
        current_color = COLOR_VIBE if mode == 0 else COLOR_OPENCLAW
        
        # LED 闪烁
        for _ in range(3):
            pixels.fill(current_color)
            time.sleep(0.1)
            pixels.fill((0, 0, 0))
            time.sleep(0.1)
        
        print(f"Mode: {'VIBE' if mode == 0 else 'OPENCLAW'}")
        
        while not encoder_switch.value:
            time.sleep(0.01)
    
    # ===== 旋钮旋转 =====
    delta = read_encoder()
    if delta != 0:
        if mode == 0:
            # Vibe模式: 代码Diff导航 (Option+F7 / Option+Shift+F7)
            if delta > 0:
                # 右转: 下一处改动
                keyboard.press(Keycode.OPTION, Keycode.F7)
            else:
                # 左转: 上一处改动
                keyboard.press(Keycode.OPTION, Keycode.SHIFT, Keycode.F7)
            time.sleep(0.05)
            keyboard.release_all()
            print(f"Diff: {'next' if delta > 0 else 'prev'}")
        else:
            # OpenClaw模式: 消息历史滚动 (Option+上下箭头)
            if delta > 0:
                # 上滚动
                keyboard.press(Keycode.OPTION, Keycode.UP_ARROW)
            else:
                # 下滚动
                keyboard.press(Keycode.OPTION, Keycode.DOWN_ARROW)
            time.sleep(0.05)
            keyboard.release_all()
            print(f"Scroll: {'up' if delta > 0 else 'down'}")
    
    time.sleep(0.01)
