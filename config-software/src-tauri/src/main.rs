// src-tauri/src/main.rs
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use serial::{SystemPort, PortSettings};
use std::io::{Read, Write};
use std::sync::Mutex;
use tauri::State;

// 串口连接状态
struct SerialState {
    port: Option<SystemPort>,
    port_name: String,
}

// 获取可用串口列表
#[tauri::command]
fn list_ports() -> Vec<String> {
    let ports = serial::available_ports()
        .unwrap_or_default();
    
    ports.into_iter()
        .map(|p| p.port_name())
        .collect()
}

// 连接串口
#[tauri::command]
fn connect_serial(port_name: String, state: State<Mutex<SerialState>>) -> Result<String, String> {
    let mut port = serial::open(&port_name)
        .map_err(|e| format!("无法打开串口: {}", e))?;
    
    port.configure(&PortSettings {
        baud_rate: serial::Baud115200,
        char_size: serial::Bits8,
        parity: serial::ParityNone,
        stop_bits: serial::Stop1,
        flow_control: serial::FlowNone,
    })
    .map_err(|e| format!("无法配置串口: {}", e))?;
    
    let mut state = state.lock().unwrap();
    state.port = Some(port);
    state.port_name = port_name.clone();
    
    Ok(format!("已连接到 {}", port_name))
}

// 断开串口
#[tauri::command]
fn disconnect_serial(state: State<Mutex<SerialState>>) -> Result<(), String> {
    let mut state = state.lock().unwrap();
    state.port = None;
    state.port_name = String::new();
    Ok(())
}

// 发送配置到设备
#[tauri::command]
fn send_config(config: String, state: State<Mutex<SerialState>>) -> Result<(), String> {
    let mut state = state.lock().unwrap();
    
    if let Some(ref mut port) = state.port {
        // 发送配置命令 (0x02)
        let data = format!("02:{}\n", config);
        port.write(data.as_bytes())
            .map_err(|e| format!("发送失败: {}", e))?;
        Ok(())
    } else {
        Err("未连接设备".to_string())
    }
}

// 读取设备配置
#[tauri::command]
fn read_config(state: State<Mutex<SerialState>>) -> Result<String, String> {
    let mut state = state.lock().unwrap();
    
    if let Some(ref mut port) = state.port {
        // 发送读取命令 (0x01)
        port.write(b"01\n")
            .map_err(|e| format!("发送失败: {}", e))?;
        
        // 读取响应
        let mut buf = [0u8; 1024];
        match port.read(&mut buf) {
            Ok(n) => Ok(String::from_utf8_lossy(&buf[..n]).to_string()),
            Err(e) => Err(format!("读取失败: {}", e))
        }
    } else {
        Err("未连接设备".to_string())
    }
}

// 发送快捷键 (测试用)
#[tauri::command]
fn send_key(combo: Vec<String>) -> Result<(), String> {
    println!("发送快捷键: {:?}", combo);
    Ok(())
}

// 发送 Shell 命令 (测试用)
#[tauri::command]
fn send_shell(command: String) -> Result<String, String> {
    use std::process::Command;
    
    let output = Command::new("sh")
        .arg("-c")
        .arg(&command)
        .output()
        .map_err(|e| format!("执行失败: {}", e))?;
    
    Ok(String::from_utf8_lossy(&output.stdout).to_string())
}

fn main() {
    tauri::Builder::default()
        .manage(Mutex::new(SerialState {
            port: None,
            port_name: String::new(),
        }))
        .invoke_handler(tauri::generate_handler![
            list_ports,
            connect_serial,
            disconnect_serial,
            send_config,
            read_config,
            send_key,
            send_shell
        ])
        .run(tauri::generate_context!())
        .expect("启动失败");
}
