"""
MacroPad 双控键盘固件
Vibe Coding + OpenClaw 控制模式

功能:
- 12个按键发送快捷键
- 旋钮按下切换模式
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

# ===== 配置 =====
COLOR_VIBE = (0, 0, 255)        # 蓝色 - Vibe Coding
COLOR_OPENCLAW = (0, 255, 0)     # 绿色 - OpenClaw 控制

mode = 0  # 0=Vibe Coding, 1=OpenClaw

# ===== 按键配置 =====
# Vibe Coding 模式快捷键 (Cursor/Windsurf)
vibe_actions = [
    # 第1行: 上下文交互
    ([Keycode.L], "AI Chat", "Cmd+L"),           # 按键1: 打开AI聊天
    ([Keycode.L], "+Context", "Cmd+Shift+L"),    # 按键2: 添加选中代码到上下文
    ([Keycode.RETURN], "Submit", "Cmd+Return"),  # 按键3: 提交
    
    # 第2行: 代码生成
    ([Keycode.K], "Edit", "Cmd+K"),              # 按键4: 内联编辑
    ([Keycode.I], "Composer", "Cmd+I"),          # 按键5: Composer面板
    ([Keycode.I], "FullComp", "Cmd+Shift+I"),    # 按键6: 全屏Composer
    
    # 第3行: 审查
    ([Keycode.TAB], "Accept", "Tab"),            # 按键7: 接受AI建议
    ([Keycode.K], "AI Fix", "Cmd+K"),           # 按键8: 终端AI修复
    ([Keycode.ESCAPE], "Reject", "Esc"),         # 按键9: 拒绝差异
    
    # 第4行: 文件操作
    ([Keycode.N], "New", "Cmd+N"),               # 按键10: 新建文件
    ([Keycode.S], "Save", "Cmd+S"),              # 按键11: 保存
    ([Keycode.GRAVE_ACCENT], "Term", "Cmd+`"),   # 按键12: 切换终端
]

# OpenClaw 控制模式
openclaw_actions = [
    # 第1行: Gateway管理
    ("Status", "openclaw status"),               # 按键1: 查看状态
    ("Restart", "openclaw gateway restart"),     # 按键2: 重启Gateway
    ("Doctor", "openclaw doctor"),              # 按键3: 健康检查
    
    # 第2行: 技能工具
    ("Sync", "clawhub sync"),                   # 按键4: 同步技能
    ("Sessions", "openclaw sessions list"),     # 按键5: 会话列表
    ("Test", "echo test"),                      # 按键6: 测试消息
    
    # 第3行: 硬件控制
    ("Screen", "screenshot"),                   # 按键7: 截屏
    ("Run", "openclaw exec ls"),                # 按键8: 运行命令
    ("KILL", "pkill -f openclaw"),             # 按键9: 急停!
    
    # 第4行: 机械臂
    ("ClawOp", "claw_open"),                    # 按键10: 夹爪张开
    ("ClawCl", "claw_close"),                   # 按键11: 夹爪闭合
    ("Home", "home_all"),                       # 按键12: 归位
]

# ===== 发送快捷键 =====
def send_shortcut(key_codes):
    """发送快捷键组合"""
    # 先按下所有修饰键
    for key in key_codes:
        if key in [Keycode.COMMAND, Keycode.CONTROL, Keycode.OPTION, Keycode.SHIFT]:
            keyboard.press(key)
    time.sleep(0.02)
    
    # 再按功能键
    for key in key_codes:
        if key not in [Keycode.COMMAND, Keycode.CONTROL, Keycode.OPTION, Keycode.SHIFT]:
            keyboard.press(key)
    time.sleep(0.05)
    
    # 释放所有键
    keyboard.release_all()

# ===== LED 动画 =====
def led_animation():
    """启动动画"""
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
                # Vibe Coding 模式 - 发送快捷键
                key_codes, label, shortcut = vibe_actions[i]
                send_shortcut(key_codes)
                print(f"Vibe: {label} ({shortcut})")
            else:
                # OpenClaw 模式
                label, cmd = openclaw_actions[i]
                print(f"OpenClaw: {label} -> {cmd}")
            
            # LED 反馈
            pixels[i] = (255, 255, 255)
            time.sleep(0.1)
            pixels[i] = current_color
    
    # ===== 旋钮按下 - 切换模式 =====
    if not encoder_switch.value:
        mode = 1 - mode
        current_color = COLOR_VIBE if mode == 0 else COLOR_OPENCLAW
        
        # LED 闪烁指示
        for _ in range(3):
            pixels.fill(current_color)
            time.sleep(0.1)
            pixels.fill((0, 0, 0))
            time.sleep(0.1)
        
        print(f"Mode: {'VIBE CODING' if mode == 0 else 'OPENCLAW'}")
        
        # 等待释放
        while not encoder_switch.value:
            time.sleep(0.01)
    
    time.sleep(0.01)
