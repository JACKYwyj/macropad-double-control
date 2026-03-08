"""
MacroPad 双控键盘固件 V4
- 有效按钮常亮
- 按下时闪烁
- 无效按钮不亮
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

# ===== 旋钮 =====
encoder_switch = digitalio.DigitalInOut(board.ENCODER_SWITCH)
encoder_switch.direction = digitalio.Direction.INPUT
encoder_switch.pull = digitalio.Pull.UP

rot_a = digitalio.DigitalInOut(board.ROTA)
rot_a.direction = digitalio.Direction.INPUT
rot_a.pull = digitalio.Pull.UP

rot_b = digitalio.DigitalInOut(board.ROTB)
rot_b.direction = digitalio.Direction.INPUT
rot_b.pull = digitalio.Pull.UP

# ===== 配置 =====
COLOR_VIBE = (0, 0, 255)
COLOR_OPENCLAW = (0, 255, 0)

mode = 0
encoder_state = 0

# ===== 按键配置 =====
# Vibe Coding 模式 - 全部12个按键都有功能
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

# OpenClaw 模式 - 只有9个按键有功能
# 10,11,12 无功能
openclaw_actions = [
    ("openclaw status", "Status"),              # 1
    ("openclaw gateway restart", "Restart"),     # 2
    ("openclaw doctor", "Doctor"),              # 3
    ("clawhub sync", "Sync"),                  # 4
    ("openclaw sessions list", "Sessions"),     # 5
    ("echo test", "Test"),                     # 6
    ("openclaw nodes device_status", "Device"), # 7
    ("openclaw exec ls", "Run"),              # 8
    ("pkill -f openclaw", "KILL"),            # 9
    (None, None),  # 10 - 无功能
    (None, None),  # 11 - 无功能
    (None, None),  # 12 - 无功能
]

# ===== 有效按键映射 =====
vibe_valid = [True] * 12  # 全部有效
openclaw_valid = [True, True, True, True, True, True, True, True, True, False, False, False]

# ===== 发送快捷键 =====
def send_shortcut(key_codes):
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
    if not text:
        return
    for char in text:
        if char == ' ':
            keyboard.press(Keycode.SPACE)
            time.sleep(0.01)
            keyboard.release(Keycode.SPACE)
        elif char == '-':
            keyboard.press(Keycode.MINUS)
            time.sleep(0.01)
            keyboard.release(Keycode.MINUS)
        elif char.isupper() or char in '!@#$%^&*()_+{}|:"<>?':
            keyboard.press(Keycode.SHIFT)
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

# ===== 设置LED =====
def set_mode_leds():
    """根据当前模式设置LED"""
    color = COLOR_VIBE if mode == 0 else COLOR_OPENCLAW
    valid = vibe_valid if mode == 0 else openclaw_valid
    
    for i in range(12):
        if valid[i]:
            pixels[i] = color
        else:
            pixels[i] = (0, 0, 0)

# ===== 启动动画 =====
for i in range(12):
    pixels[i] = COLOR_VIBE
    time.sleep(0.02)
time.sleep(0.2)
set_mode_leds()

print("Ready!")

# ===== 主循环 =====
while True:
    for i, key in enumerate(keys):
        if not key.value:
            current_color = COLOR_VIBE if mode == 0 else COLOR_OPENCLAW
            valid = vibe_valid if mode == 0 else openclaw_valid
            
            # 检查按键是否有效
            if not valid[i]:
                continue
            
            if mode == 0:
                key_codes = vibe_actions[i][0]
                send_shortcut(key_codes)
                print(f"Vibe: {vibe_actions[i][1]}")
            else:
                cmd, label = openclaw_actions[i]
                if cmd:
                    send_command(cmd)
                    print(f"OpenClaw: {label}")
            
            # 按下闪烁
            pixels[i] = (255, 255, 255)
            time.sleep(0.1)
            set_mode_leds()
    
    # 旋钮按下 - 切换模式
    if not encoder_switch.value:
        mode = 1 - mode
        
        # 切换动画
        color = COLOR_VIBE if mode == 0 else COLOR_OPENCLAW
        for _ in range(3):
            pixels.fill(color)
            time.sleep(0.1)
            pixels.fill((0, 0, 0))
            time.sleep(0.1)
        
        set_mode_leds()
        print(f"Mode: {'VIBE' if mode == 0 else 'OPENCLAW'}")
        
        while not encoder_switch.value:
            time.sleep(0.01)
    
    # 旋钮旋转
    delta = read_encoder()
    if delta != 0:
        if mode == 0:
            if delta > 0:
                keyboard.press(Keycode.OPTION, Keycode.F7)
            else:
                keyboard.press(Keycode.OPTION, Keycode.SHIFT, Keycode.F7)
            time.sleep(0.05)
            keyboard.release_all()
        else:
            if delta > 0:
                keyboard.press(Keycode.OPTION, Keycode.UP_ARROW)
            else:
                keyboard.press(Keycode.OPTION, Keycode.DOWN_ARROW)
            time.sleep(0.05)
            keyboard.release_all()
    
    time.sleep(0.01)
