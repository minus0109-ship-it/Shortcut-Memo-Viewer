# Shortcut Memo Viewer (단축키 메모 뷰어)

[![Language](https://img.shields.io/badge/Language-Python-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-PyQt6-green.svg)](https://pypi.org/project/PyQt6/)

Read this in other languages: [English](#english) | [한국어](#한국어)

---

## English

A custom virtual keyboard application that visualizes real-time keystrokes and helps you map, learn, and manage your own shortcut dictionaries.

### Key Features
* **Real-time Visualization:** Pressed keys and modifiers (Ctrl, Alt, Shift, etc.) are highlighted instantly.
* **Intuitive Shortcut Editing:** Right-click any key on the virtual keyboard to add, edit, or delete descriptions.
* **Complex Combinations:** Supports mapping and displaying complex multi-key combinations.
* **Profile Management:** Create, load, export, and delete multiple JSON-based profiles for different workflows.
* **Customization & Localization:** Customize keyboard colors for different key states and switch the UI language between English and Korean.

### Use Cases
* **Gaming Key Mapping:** Save control layouts for various games to instantly check interaction keys (like E/F) without launching the game.
* **Conflict Prevention:** Simulate and verify custom key bindings to ensure no overlapping shortcuts.
* **Tool Learning:** Visually memorize complex hotkeys for coding editors or design tools.

### Installation
1. Install Python 3.x.
2. Install the required libraries:
   ```bash
   pip install PyQt6 pynput
