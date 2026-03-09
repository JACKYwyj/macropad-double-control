"""
MacroPad 双控键盘固件 V7
- 显示当前模式 + 最后按下的按键功能
- OLED优化排版
"""
import board
import digitalio
import neopixel
import time
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

# ===== OLED 屏幕 =====
try:
    import displayio
    import adafruit_sh1106
    
    displayio.release_displays()
    i2c = board.I2C()
    display = adafruit_sh1106.SH1106(displayio.I2CDisplay(i2c, device_address=0x3c), width=128, height=64)
    HAS_DISPLAY = True
except:
    HAS_DISPLAY = False

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

mode = 0  # 0=Vibe, 1=OpenClaw
encoder_state = 0

# 模型数量 (可修改)
MODEL_COUNT = 5
current_model_index = 0

# 最后按下的按键 (功能名, 快捷键/命令)
last_action = ("--", "--")

# ===== 按键配置 =====
vibe_actions = [
    ([Keycode.L], "AI Chat", "⌘ L"),
    ([Keycode.L], "+Context", "⌘⇧L"),
    ([Keycode.RETURN], "Submit", "⌘↩"),
    ([Keycode.K], "Edit", "⌘ K"),
    ([Keycode.I], "Composer", "⌘ I"),
    ([Keycode.I], "FullComp", "⌘⇧I"),
    ([Keycode.TAB], "Accept", "Tab"),
    ([Keycode.K], "AI Fix", "⌘ K"),
    ([Keycode.ESCAPE], "Reject", "Esc"),
    ([Keycode.N], "New", "⌘ N"),
    ([Keycode.S], "Save", "⌘ S"),
    ([Keycode.GRAVE_ACCENT], "Term", "⌘ `"),
]

openclaw_actions = [
    ("openclaw status", "Status", "status"),
    ("openclaw gateway restart", "Restart", "restart"),
    ("openclaw doctor", "Doctor", "doctor"),
    ("clawhub sync", "Sync", "sync"),
    ("openclaw sessions list", "Sessions", "sessions"),
    ("echo test", "Test", "test"),
    ("openclaw nodes device_status", "Device", "device"),
    ("openclaw exec ls", "Run", "exec ls"),
    ("pkill -f openclaw", "KILL", "pkill"),
    (None, None, None),
    (None, None, None),
    (None, None, None),
]

vibe_valid = [True] * 12
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

# ===== 显示更新 =====
def update_display():
    if not HAS_DISPLAY:
        return
    
    display.fill(0)
    
    # 模式标题
    mode_name = "=== VIBE MODE ===" if mode == 0 else "== OPENCLAW =="
    display.text(mode_name, 0, 0, 1)
    
    # 分隔线
    for x in range(0, 128, 8):
        display.pixel(x, 12, 1)
    
    # 最后按下的功能
    display.text("Last:", 0, 18, 1)
    display.text(last_action[0], 36, 18, 1)
    
    # 快捷键/命令
    display.text(last_action[1], 0, 30, 1)
    
    # 底部提示
    if mode == 0:
        display.text("Model:", 70, 30, 1)
        display.text(f"{current_model_index + 1}/{MODEL_COUNT}", 100, 30, 1)
        display.text("Rot:Switch  Knob:Mode", 0, 50, 1)
    else:
        display.text("Rot:Scroll Knob:Mode", 0, 50, 1)
    
    display.show()

# ===== 设置LED =====
def set_mode_leds():
    color = COLOR_VIBE if mode == 0 else COLOR_OPENCLAW
    valid = vibe_valid if mode == 0 else openclaw_valid
    
    for i in range(12):
        if valid[i]:
            pixels[i] = color
        else:
            pixels[i] = (0, 0, 0)

# ===== 启动 =====
for i in range(12):
    pixels[i] = COLOR_VIBE
    time.sleep(0.02)
time.sleep(0.2)

update_display()
set_mode_leds()

print("Ready!")

# ===== 主循环 =====
while True:
    # 按键检测
    for i, key in enumerate(keys):
        if not key.value:
            valid = vibe_valid if mode == 0 else openclaw_valid
            
            if not valid[i]:
                continue
            
            if mode == 0:
                key_codes, label, shortcut = vibe_actions[i]
                send_shortcut(key_codes)
                last_action = (label, shortcut)
            else:
                cmd, label, shortcut = openclaw_actions[i]
                if cmd:
                    send_command(cmd)
                    last_action = (label, shortcut)
            
            # LED闪烁
            current_color = COLOR_VIBE if mode == 0 else COLOR_OPENCLAW
            pixels[i] = (255, 255, 255)
            time.sleep(0.1)
            set_mode_leds()
            
            # 更新显示
            update_display()
    
    # 旋钮按下 - 切换模式
    if not encoder_switch.value:
        mode = 1 - mode
        last_action = ("--", "--")
        
        for _ in range(3):
            color = COLOR_VIBE if mode == 0 else COLOR_OPENCLAW
            pixels.fill(color)
            time.sleep(0.1)
            pixels.fill((0, 0, 0))
            time.sleep(0.1)
        
        update_display()
        set_mode_leds()
        
        while not encoder_switch.value:
            time.sleep(0.01)
    
    # 旋钮旋转
    delta = read_encoder()
    if delta != 0:
        if mode == 0:
            # Vibe模式: 切换模型编号
            current_model_index = (current_model_index + delta) % MODEL_COUNT
            if current_model_index < 0:
                current_model_index = MODEL_COUNT - 1
            update_display()
        else:
            # OpenClaw模式: 滚动
            if delta > 0:
                keyboard.press(Keycode.OPTION, Keycode.UP_ARROW)
            else:
                keyboard.press(Keycode.OPTION, Keycode.DOWN_ARROW)
            time.sleep(0.05)
            keyboard.release_all()
    
    time.sleep(0.01)
