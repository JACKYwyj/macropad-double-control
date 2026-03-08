"""
MacroPad 双控键盘固件 V5
- Vibe模式: 旋钮切换API模型 + OLED显示
- OpenClaw模式: 消息滚动
- LED常亮/按下闪烁
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
    from fourwire import FourWire
    
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

# ===== API 模型列表 =====
api_models = [
    "claude-sonnet",
    "claude-opus", 
    "gpt-4o",
    "gpt-4o-mini",
    "deepseek",
]
current_model_index = 0

# ===== 按键配置 =====
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

openclaw_actions = [
    ("openclaw status", "Status"),
    ("openclaw gateway restart", "Restart"),
    ("openclaw doctor", "Doctor"),
    ("clawhub sync", "Sync"),
    ("openclaw sessions list", "Sessions"),
    ("echo test", "Test"),
    ("openclaw nodes device_status", "Device"),
    ("openclaw exec ls", "Run"),
    ("pkill -f openclaw", "KILL"),
    (None, None),
    (None, None),
    (None, None),
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
    
    # 顶部: 模式
    mode_name = "VIBE CODING" if mode == 0 else "OPENCLAW"
    display.text(mode_name, 0, 0, 1)
    
    if mode == 0:
        # Vibe模式: 显示当前模型
        model = api_models[current_model_index]
        display.text("Model:", 0, 16, 1)
        display.text(model, 0, 28, 1)
        
        # 显示操作提示
        display.text("Rot: Change model", 0, 48, 1)
    else:
        # OpenClaw模式
        display.text("Press key to", 0, 16, 1)
        display.text("run command", 0, 28, 1)
        display.text("Rot: Scroll msg", 0, 48, 1)
    
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
print("Mode: VIBE")

# ===== 主循环 =====
while True:
    # 按键检测
    for i, key in enumerate(keys):
        if not key.value:
            current_color = COLOR_VIBE if mode == 0 else COLOR_OPENCLAW
            valid = vibe_valid if mode == 0 else openclaw_valid
            
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
            
            pixels[i] = (255, 255, 255)
            time.sleep(0.1)
            set_mode_leds()
    
    # 旋钮按下 - 切换模式
    if not encoder_switch.value:
        mode = 1 - mode
        
        for _ in range(3):
            color = COLOR_VIBE if mode == 0 else COLOR_OPENCLAW
            pixels.fill(color)
            time.sleep(0.1)
            pixels.fill((0, 0, 0))
            time.sleep(0.1)
        
        update_display()
        set_mode_leds()
        print(f"Mode: {'VIBE' if mode == 0 else 'OPENCLAW'}")
        
        while not encoder_switch.value:
            time.sleep(0.01)
    
    # 旋钮旋转
    delta = read_encoder()
    if delta != 0:
        if mode == 0:
            # Vibe模式: 切换模型
            current_model_index = (current_model_index + delta) % len(api_models)
            update_display()
            print(f"Model: {api_models[current_model_index]}")
        else:
            # OpenClaw模式: 滚动
            if delta > 0:
                keyboard.press(Keycode.OPTION, Keycode.UP_ARROW)
            else:
                keyboard.press(Keycode.OPTION, Keycode.DOWN_ARROW)
            time.sleep(0.05)
            keyboard.release_all()
    
    time.sleep(0.01)
