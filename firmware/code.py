"""
MacroPad 双控键盘固件 V3
Vibe Coding + OpenClaw 控制模式

兼容 Mac/Windows/Linux - 命令自带回车
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

# ===== 旋钮编码器 =====
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
encoder_state = 0

# ===== 按键配置 =====
# Vibe Coding 模式快捷键 (Cursor/Windsurf)
vibe_actions = [
    ([Keycode.L], "AI Chat"),
    ([Keycode.L], "+Context"),
    ([Keycode.RETURN], "Submit"),
    ([Keycode.K], "Edit"),
    ([Keycode.I], "Composer"),
    ([Keycode.I], "FullComp"),
    ([Keycode.TAB], "Accept"),
    ([Keycode.K], "AI Fix"),
    ([Keycode.ESCAPE], "Reject"),
    ([Keycode.N], "New"),
    ([Keycode.S], "Save"),
    ([Keycode.GRAVE_ACCENT], "Term"),
]

# OpenClaw 控制模式 - 直接发送命令+回车 (兼容 Mac/Windows/Linux)
openclaw_actions = [
    # Gateway管理
    ("openclaw status", "Status"),
    ("openclaw gateway restart", "Restart"),
    ("openclaw doctor", "Doctor"),
    
    # 技能工具
    ("clawhub sync", "Sync"),
    ("openclaw sessions list", "Sessions"),
    ("echo test", "Test"),
    
    # 硬件控制
    ("openclaw nodes device_status", "Device"),
    ("openclaw exec ls", "Run"),
    ("pkill -f openclaw", "KILL"),
    
    # 预留
    ("echo 1", "Msg1"),
    ("echo 2", "Msg2"),
    ("echo 3", "Msg3"),
]

# ===== 发送快捷键 =====
def send_shortcut(key_codes):
    """发送快捷键组合"""
    for key in key_codes:
        if key in [Keycode.COMMAND, Keycode.CONTROL, Keycode.OPTION, Keycode.SHIFT]:
            keyboard.press(key)
    time.sleep(0.02)
    for key in key_codes:
        if key not in [Keycode.COMMAND, Keycode.CONTROL, Keycode.OPTION, Keycode.SHIFT]:
            keyboard.press(key)
    time.sleep(0.05)
    keyboard.release_all()

# ===== 发送命令+回车 =====
def send_command(text):
    """发送命令并回车 - 兼容 Mac/Windows/Linux"""
    # 逐字符发送
    for char in text:
        if char == ' ':
            keyboard.press(Keycode.SPACE)
            time.sleep(0.01)
            keyboard.release(Keycode.SPACE)
        elif char == '-':
            keyboard.press(Keycode.MINUS)
            time.sleep(0.01)
            keyboard.release(Keycode.MINUS)
        elif char == '_':
            keyboard.press(Keycode.SHIFT, Keycode.MINUS)
            time.sleep(0.01)
            keyboard.release_all()
        elif char.isupper() or char in '!@#$%^&*()_+{}|:"<>?':
            keyboard.press(Keycode.SHIFT)
            # 发送大写字母或符号
            key = getattr(Keycode, char.upper(), None)
            if key:
                keyboard.press(key)
                time.sleep(0.01)
                keyboard.release(key)
            keyboard.release(Keycode.SHIFT)
        else:
            key = getattr(Keycode, char.upper(), None)
            if key:
                keyboard.press(key)
                time.sleep(0.01)
                keyboard.release(key)
        time.sleep(0.01)
    
    # 发送回车 (兼容所有系统)
    keyboard.press(Keycode.RETURN)
    time.sleep(0.05)
    keyboard.release(Keycode.RETURN)

# ===== 旋钮读取 =====
def read_encoder():
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
for i in range(12):
    pixels[i] = COLOR_VIBE
    time.sleep(0.02)
time.sleep(0.2)
pixels.fill((0, 0, 0))

print("Ready!")
print("Mode: VIBE")

# ===== 主循环 =====
while True:
    # 按键检测
    for i, key in enumerate(keys):
        if not key.value:
            current_color = COLOR_VIBE if mode == 0 else COLOR_OPENCLAW
            
            if mode == 0:
                # Vibe Coding - 发送快捷键
                key_codes = vibe_actions[i][0]
                send_shortcut(key_codes)
                print(f"Vibe: {vibe_actions[i][1]}")
            else:
                # OpenClaw - 发送命令+回车
                cmd, label = openclaw_actions[i]
                send_command(cmd)
                print(f"OpenClaw: {label}")
            
            # LED 反馈
            pixels[i] = (255, 255, 255)
            time.sleep(0.1)
            pixels[i] = current_color
    
    # 旋钮按下 - 切换模式
    if not encoder_switch.value:
        mode = 1 - mode
        current_color = COLOR_VIBE if mode == 0 else COLOR_OPENCLAW
        
        for _ in range(3):
            pixels.fill(current_color)
            time.sleep(0.1)
            pixels.fill((0, 0, 0))
            time.sleep(0.1)
        
        print(f"Mode: {'VIBE' if mode == 0 else 'OPENCLAW'}")
        
        while not encoder_switch.value:
            time.sleep(0.01)
    
    # 旋钮旋转
    delta = read_encoder()
    if delta != 0:
        if mode == 0:
            # Vibe模式: Diff导航
            if delta > 0:
                keyboard.press(Keycode.OPTION, Keycode.F7)
            else:
                keyboard.press(Keycode.OPTION, Keycode.SHIFT, Keycode.F7)
            time.sleep(0.05)
            keyboard.release_all()
            print(f"Diff: {'next' if delta > 0 else 'prev'}")
        else:
            # OpenClaw模式: 滚动
            if delta > 0:
                keyboard.press(Keycode.OPTION, Keycode.UP_ARROW)
            else:
                keyboard.press(Keycode.OPTION, Keycode.DOWN_ARROW)
            time.sleep(0.05)
            keyboard.release_all()
            print(f"Scroll: {'up' if delta > 0 else 'down'}")
    
    time.sleep(0.01)
