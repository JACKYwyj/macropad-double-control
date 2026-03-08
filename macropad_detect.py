#!/usr/bin/env python3
"""
MacroPad 设备识别脚本
支持 Mac/Windows/Linux 全平台
"""
import sys
import os
import serial.tools.list_ports

def find_macropad():
    """查找已连接的 Adafruit MacroPad RP2040"""
    ports = list(serial.tools.list_ports.comports())
    
    # MacroPad 可能的 VID/PID
    MACROPAD_VIDS = ["0x239a", "0x1209"]  # Adafruit, Raspberry Pi
    MACROPAD_PIDS = ["0x80b4", "0x000a"]  # MacroPad, RP2040
    
    for port in ports:
        # 检查 VID/PID (如果可用)
        if hasattr(port, 'hwid'):
            hwid = port.hwid.upper()
            if any(vid in hwid for vid in MACROPAD_VIDS):
                if any(pid in hwid for pid in MACROPAD_PIDS):
                    return port.device, port.description
        
        # 备用：检查串口名称特征
        port_name = port.device.lower()
        port_desc = port.description.lower() if port.description else ""
        
        keywords = ["macro", "rp2040", "adafruit", "circuitpython", "usb serial"]
        if any(kw in port_name or kw in port_desc for kw in keywords):
            return port.device, port.description
    
    return None, None

def main():
    print("🔍 正在扫描 MacroPad 设备...")
    
    device, desc = find_macropad()
    
    if device:
        print(f"✅ 找到设备!")
        print(f"   端口: {device}")
        print(f"   描述: {desc}")
        
        # 测试连接
        try:
            ser = serial.Serial(device, 115200, timeout=1)
            print(f"   状态: 已连接")
            ser.close()
        except Exception as e:
            print(f"   状态: 连接测试失败 - {e}")
    else:
        print("❌ 未找到 MacroPad 设备")
        print("\n请检查:")
        print("  1. 设备是否通过 USB-C 连接")
        print("  2. 是否已安装 CircuitPython 固件")
        print("  3. USB 驱动是否正常 (Windows 可能需要手动安装)")
        
        # 列出所有可用串口
        print("\n📋 当前可用的串口设备:")
        for port in serial.tools.list_ports.comports():
            print(f"   {port.device}: {port.description or 'Unknown'}")

if __name__ == "__main__":
    main()
