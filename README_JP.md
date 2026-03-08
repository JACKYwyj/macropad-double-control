# MacroPad  dual-Control Keyboard
[English](./README_EN.md) | [中文](./README.md) | [日本語](./README_JP.md)

---

## 概要

Adafruit MacroPad RP2040 ベースの dual-mode キーボードシステム。**Vibe Coding** と **OpenClaw AI Agent** の両方をサポート。

## 機能

- ✅ **12個プログラム可能キー** - 各モード12個のショートカット
- ✅ **ロータリーエンコーダー** - Vibe: Diff导航/OpenClaw: メッセージスクロール
- ✅ **LED状態表示** - 青=Vibeモード/緑=OpenClawモード
- ✅ **クロスプラットフォーム** - Mac/Windows/Linux  plug-and-play
- ✅ **自動実行** - キーでEnterを自動送信

## ハードウェア

- Adafruit MacroPad RP2040
- Cherry MX 互換スイッチ (12個)
- キーカップ (12個)

[HARDWARE.md](./HARDWARE.md) を参照

## クイックスタート

### 1. ファームウェアをフラッシュ

1. **BOOT** + **RESET** でブートローダーに入る
2. [CircuitPython ファームウェア](https://circuitpython.org/board/adafruit_macropad_rp2040/) をダウンロード
3. `.uf2` を RPI-RP2 ドライブにドラッグ

### 2. ライブラリをインストール

```bash
pip install circup
circup install adafruit_macropad
```

### 3. デプロイ

`firmware/code.py` を CIRCUITPY ルートにコピー

## キー機能

### Vibe Coding モード (青LED)

| キー | 機能 | ショートカット |
|------|------|---------------|
| 1 | AI Chat | Cmd+L |
| 2 | +Context | Cmd+Shift+L |
| 3 | Submit | Cmd+Return |
| 4 | Edit | Cmd+K |
| 5 | Composer | Cmd+I |
| 6 | FullComp | Cmd+Shift+I |
| 7 | Accept | Tab |
| 8 | AI Fix | Cmd+K |
| 9 | Reject | Esc |
| 10 | New | Cmd+N |
| 11 | Save | Cmd+S |
| 12 | Terminal | Cmd+` |

**エンコーダー**: Diff ナビゲーション

### OpenClaw モード (緑LED)

| キー | 機能 | コマンド |
|------|------|---------|
| 1 | Status | openclaw status |
| 2 | Restart | openclaw gateway restart |
| 3 | Doctor | openclaw doctor |
| 4 | Sync | clawhub sync |
| 5 | Sessions | openclaw sessions list |
| 6 | Test | echo test |
| 7 | Device | openclaw nodes device_status |
| 8 | Run | openclaw exec ls |
| 9 | KILL | pkill -f openclaw |

**エンコーダー**: メッセージスクロール

### モード切替

- **エンコーダープレス**: Vibe Coding ↔ OpenClaw モード切替

## リンク

- [Adafruit MacroPad ドキュメント](https://learn.adafruit.com/adafruit-macropad-rp2040)
- [CircuitPython](https://circuitpython.org/)
- [OpenClaw](https://github.com/openclaw/openclaw)

## ライセンス

MIT License
