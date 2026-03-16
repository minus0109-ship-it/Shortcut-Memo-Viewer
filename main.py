import sys
import os
import json
import shutil
from PyQt6.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout,
                             QHBoxLayout, QComboBox, QInputDialog, QMessageBox,
                             QFileDialog, QDialog, QColorDialog, QLabel, QGridLayout,
                             QFormLayout, QLineEdit, QSizePolicy, QListWidget, QListWidgetItem)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from pynput import keyboard
import profile_manager
import settings_manager

global_settings = settings_manager.load_settings()
LANG = global_settings.get("lang", "ko")

TR = {
    "ko": {
        "title": "단축키 메모 뷰어",
        "no_file": "파일 없음",
        "no_profile": "프로필 없음",
        "manage_profile": "프로필 관리",
        "color_setting": "설정",
        "default_desc": "단축키를 누르면 설명이 여기에 표시됩니다.",
        "save_btn": "저장하기",
        "save_confirm": "저장 확인",
        "unsaved_msg": "저장되지 않은 수정사항이 있습니다. 저장하시겠습니까?",
        "modified_msg": "수정된 프로필이 있습니다. 저장하시겠습니까?",
        "warn": "경고",
        "warn_msg1": "먼저 프로필을 생성하거나 선택해주세요.",
        "warn_msg2": "설명을 입력해주세요.",
        "capture_msg": "지정할 조합키를 클릭하거나 누르세요. (취소: ESC)",
        "edit_title": "단축키 편집",
        "saved_list": "저장된 조합 목록 (클릭하여 수정):",
        "single_key": "단일 키 (조합 없음)",
        "other_mod": "다른 조합 키 (선택)",
        "assign_key": "키 지정",
        "clear_mod": "조합 해제",
        "mod_label": "조합키:",
        "desc_label": "설명:",
        "add_update": "목록에 추가 / 수정",
        "del_select": "선택 삭제",
        "done_close": "완료 및 창 닫기",
        "base_color": "기본 키",
        "press_color": "키 입력시",
        "saved_color": "저장된 단축키",
        "multi_color": "멀티 단축키",
        "lang_select": "언어 (Language)",
        "new": "새로 만들기",
        "delete": "삭제",
        "load": "불러오기",
        "export": "내보내기",
        "enter_name": "이름 입력:",
        "del_confirm": "삭제하시겠습니까?"
    },
    "en": {
        "title": "Shortcut Memo Viewer",
        "no_file": "No File",
        "no_profile": "No Profile",
        "manage_profile": "Manage Profiles",
        "color_setting": "Settings",
        "default_desc": "Press a key to see its description here.",
        "save_btn": "Save",
        "save_confirm": "Save Confirm",
        "unsaved_msg": "Unsaved changes exist. Save now?",
        "modified_msg": "Modified profile exists. Save now?",
        "warn": "Warning",
        "warn_msg1": "Please create or select a profile first.",
        "warn_msg2": "Please enter a description.",
        "capture_msg": "Click or press a key to assign. (ESC to cancel)",
        "edit_title": "Edit Shortcut",
        "saved_list": "Saved Combinations (Click to edit):",
        "single_key": "Single Key",
        "other_mod": "Other Modifier (Opt)",
        "assign_key": "Assign",
        "clear_mod": "Clear",
        "mod_label": "Modifier:",
        "desc_label": "Desc:",
        "add_update": "Add / Update",
        "del_select": "Delete Selected",
        "done_close": "Done & Close",
        "base_color": "Base Key",
        "press_color": "Pressed",
        "saved_color": "Saved Shortcut",
        "multi_color": "Multi Shortcut",
        "lang_select": "Language",
        "new": "New",
        "delete": "Delete",
        "load": "Load",
        "export": "Export",
        "enter_name": "Enter Name:",
        "del_confirm": "Are you sure you want to delete?"
    }
}


def tr(key):
    return TR.get(LANG, TR["ko"]).get(key, key)


class KeyListenerThread(QThread):
    key_pressed = pyqtSignal(str)
    key_released = pyqtSignal(str)

    def run(self):
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()

    def on_press(self, key):
        try:
            k = key.char
        except AttributeError:
            k = str(key).replace("Key.", "")
        self.key_pressed.emit(str(k))

    def on_release(self, key):
        try:
            k = key.char
        except AttributeError:
            k = str(key).replace("Key.", "")
        self.key_released.emit(str(k))


class KeyButton(QPushButton):
    right_clicked = pyqtSignal(str)
    left_clicked = pyqtSignal(str)

    def __init__(self, label, x, y, w, h, settings, parent=None):
        target_str = chr(115) + chr(112) + chr(97) + chr(99) + chr(101)
        display_label = "Spc" if label == "" or label.lower() == target_str else label
        super().__init__(display_label, parent)
        self.label_id = label.lower()
        self.settings = settings
        self.state = "base"
        unit = 45
        self.setGeometry(int(x * unit), int(y * unit), int(w * unit), int(h * unit))
        self.update_style()

    def update_style(self):
        color = self.settings.get(f"{self.state}_color", self.settings.get("base_color", "#ffffff"))
        self.setStyleSheet(
            f"QPushButton {{ background-color:{color}; border:1px solid #bdc3c7; border-radius:4px; font-size:10px; }} QPushButton:hover {{ background-color:#e0e0e0; }}")

    def set_pressed_style(self):
        color = self.settings.get("press_color", "#ffcccc")
        self.setStyleSheet(
            f"QPushButton {{ background-color:{color}; border:1px solid #d63031; border-radius:4px; font-size:10px; }}")

    def set_multi_style(self):
        color = self.settings.get("multi_color", "#fff2cc")
        self.setStyleSheet(
            f"QPushButton {{ background-color:{color}; border:1px solid #e1b12c; border-radius:4px; font-size:10px; }}")

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.RightButton:
            self.right_clicked.emit(self.label_id)
        elif event.button() == Qt.MouseButton.LeftButton:
            self.left_clicked.emit(self.label_id)


class SettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("color_setting"))
        self.settings = settings
        self.layout = QGridLayout(self)

        self.colors = {
            "base_color": tr("base_color"),
            "press_color": tr("press_color"),
            "saved_color": tr("saved_color"),
            "multi_color": tr("multi_color")
        }
        self.buttons = {}
        row = 0

        self.layout.addWidget(QLabel(tr("lang_select")), row, 0)
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["한국어", "English"])
        self.lang_combo.setCurrentText("한국어" if LANG == "ko" else "English")
        self.lang_combo.currentTextChanged.connect(self.change_lang)
        self.layout.addWidget(self.lang_combo, row, 1)
        row += 1

        for key, name in self.colors.items():
            self.layout.addWidget(QLabel(name), row, 0)
            btn = QPushButton()
            btn.setStyleSheet(f"background-color: {self.settings.get(key, '#ffffff')};")
            btn.clicked.connect(lambda checked, k=key: self.change_color(k))
            self.layout.addWidget(btn, row, 1)
            self.buttons[key] = btn
            row += 1

    def change_lang(self, text):
        global LANG
        LANG = "ko" if text == "한국어" else "en"
        self.settings["lang"] = LANG
        settings_manager.save_settings(self.settings)
        if self.parent():
            self.parent().update_ui_texts()

    def change_color(self, key):
        color = QColorDialog.getColor()
        if color.isValid():
            self.settings[key] = color.name()
            self.buttons[key].setStyleSheet(f"background-color: {color.name()};")
            settings_manager.save_settings(self.settings)
            if self.parent(): self.parent().refresh_all_keys()


class ShortcutEditDialog(QDialog):
    def __init__(self, key_id, shortcuts_data, preset_mod=None, preset_desc=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{tr('edit_title')}: {key_id.upper()}")
        self.resize(350, 450)
        self.key_id = key_id.lower().strip()
        self.shortcuts_data = shortcuts_data.copy()
        self.capture_requested = False

        self.layout = QVBoxLayout(self)

        self.layout.addWidget(QLabel(tr("saved_list")))
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        self.layout.addWidget(self.list_widget)

        form_layout = QFormLayout()
        self.mod_input = QLineEdit(preset_mod if preset_mod else "")
        self.mod_input.setReadOnly(True)
        self.mod_input.setPlaceholderText(tr("other_mod"))

        mod_btn_layout = QHBoxLayout()
        self.btn_capture = QPushButton(tr("assign_key"))
        self.btn_capture.setAutoDefault(False)
        self.btn_capture.clicked.connect(self.request_capture)
        self.btn_clear_mod = QPushButton(tr("clear_mod"))
        self.btn_clear_mod.setAutoDefault(False)
        self.btn_clear_mod.clicked.connect(self.mod_input.clear)

        mod_btn_layout.addWidget(self.btn_capture)
        mod_btn_layout.addWidget(self.btn_clear_mod)

        mod_layout = QHBoxLayout()
        mod_layout.addWidget(self.mod_input)
        mod_layout.addLayout(mod_btn_layout)

        self.desc_input = QLineEdit(preset_desc if preset_desc else "")
        self.desc_input.returnPressed.connect(self.accept_and_save)

        form_layout.addRow(tr("mod_label"), mod_layout)
        form_layout.addRow(tr("desc_label"), self.desc_input)
        self.layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        self.btn_add_update = QPushButton(tr("add_update"))
        self.btn_add_update.setAutoDefault(False)
        self.btn_add_update.clicked.connect(self.add_or_update)
        self.btn_del = QPushButton(tr("del_select"))
        self.btn_del.setAutoDefault(False)
        self.btn_del.clicked.connect(self.delete_selected)

        btn_layout.addWidget(self.btn_add_update)
        btn_layout.addWidget(self.btn_del)
        self.layout.addLayout(btn_layout)

        self.btn_close = QPushButton(tr("done_close"))
        self.btn_close.setDefault(True)
        self.btn_close.clicked.connect(self.accept_and_save)
        self.layout.addWidget(self.btn_close)

        self.refresh_list()

    def get_priority(self, k):
        if 'ctrl' in k: return 1
        if 'alt' in k: return 2
        if 'shift' in k: return 3
        if 'win' in k: return 4
        if len(k) > 1: return 5
        return 6

    def format_shortcut_key(self, key1, key2=""):
        keys = [k for k in [key1, key2] if k]
        keys.sort(key=lambda x: (self.get_priority(x), x))
        return "+".join(keys)

    def refresh_list(self):
        self.list_widget.clear()
        for dict_key, info in self.shortcuts_data.items():
            keys_in_combo = dict_key.split('+')
            if self.key_id in keys_in_combo:
                desc = info.get("desc", "")
                display_text = f"[{' + '.join(k.upper() for k in keys_in_combo)}] {desc}"
                item = QListWidgetItem(display_text)
                item.setData(Qt.ItemDataRole.UserRole, dict_key)
                self.list_widget.addItem(item)

    def on_item_clicked(self, item):
        dict_key = item.data(Qt.ItemDataRole.UserRole)
        info = self.shortcuts_data.get(dict_key, {})
        keys_in_combo = dict_key.split('+')
        other_keys = [k for k in keys_in_combo if k != self.key_id]

        self.mod_input.setText(other_keys[0] if other_keys else "")
        self.desc_input.setText(info.get("desc", ""))

    def add_or_update(self):
        raw_mod = self.mod_input.text().lower().strip()
        other_key = raw_mod.split('_')[0] if '_' in raw_mod else raw_mod
        desc = self.desc_input.text().strip()

        if not desc:
            QMessageBox.warning(self, tr("warn"), tr("warn_msg2"))
            return

        dict_key = self.format_shortcut_key(self.key_id, other_key)
        self.shortcuts_data[dict_key] = {"desc": desc}
        self.refresh_list()
        self.mod_input.clear()
        self.desc_input.clear()

    def delete_selected(self):
        item = self.list_widget.currentItem()
        if item:
            dict_key = item.data(Qt.ItemDataRole.UserRole)
            if dict_key in self.shortcuts_data:
                del self.shortcuts_data[dict_key]
            self.refresh_list()
            self.mod_input.clear()
            self.desc_input.clear()

    def accept_and_save(self):
        raw_mod = self.mod_input.text().lower().strip()
        other_key = raw_mod.split('_')[0] if '_' in raw_mod else raw_mod
        desc = self.desc_input.text().strip()

        if desc:
            dict_key = self.format_shortcut_key(self.key_id, other_key)
            self.shortcuts_data[dict_key] = {"desc": desc}
        self.accept()

    def request_capture(self):
        self.capture_requested = True
        self.reject()


class ProfileManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("manage_profile"))
        self.resize(300, 200)
        self.layout = QVBoxLayout(self)
        self.combo = QComboBox()
        self.refresh_combo()
        self.layout.addWidget(self.combo)
        for text_key, func in [("new", self.new_profile), ("delete", self.del_profile),
                               ("load", self.load_profile_external), ("export", self.export_profile)]:
            btn = QPushButton(tr(text_key))
            btn.clicked.connect(func)
            self.layout.addWidget(btn)

    def refresh_combo(self):
        self.combo.clear()
        profiles = profile_manager.get_profiles()
        if profiles:
            self.combo.addItems([p.replace('.json', '') for p in profiles])
        else:
            self.combo.addItem(tr("no_profile"))
        if self.parent(): self.parent().refresh_profile_combo()

    def new_profile(self):
        text, ok = QInputDialog.getText(self, tr("new"), tr("enter_name"))
        if ok and text:
            profile_manager.create_profile(text)
            self.refresh_combo()

    def del_profile(self):
        target = self.combo.currentText()
        if target and target != tr("no_profile") and QMessageBox.question(self, tr("delete"), tr("del_confirm"),
                                                                          QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            profile_manager.delete_profile(target)
            self.refresh_combo()

    def load_profile_external(self):
        fname, _ = QFileDialog.getOpenFileName(self, tr("load"), '', 'JSON Files (*.json)')
        if fname:
            shutil.copy(fname, "profiles/")
            self.refresh_combo()

    def export_profile(self):
        target = self.combo.currentText()
        if target and target != tr("no_profile"):
            fname, _ = QFileDialog.getSaveFileName(self, tr("export"), f'{target}.json', 'JSON Files (*.json)')
            if fname: profile_manager.export_profile(target, fname)


class KeyboardApp(QWidget):
    capture_completed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.resize(1100, 450)
        os.makedirs("layouts", exist_ok=True)
        self.settings = global_settings
        self.main_layout = QVBoxLayout(self)
        self.control_layout = QHBoxLayout()
        self.current_profile_data = {"shortcuts": {}}
        self.combo_data = {}
        self.pressed_keys = set()
        self.buttons = []
        self.is_modified = False

        self.is_capturing = False
        self.capture_target_key = ""
        self.capture_temp_desc = ""
        self.capture_temp_mod = ""
        self.capture_completed.connect(self.finish_capture)

        self.layout_combo = QComboBox()
        self.load_combo_items(self.layout_combo, "layouts")
        self.layout_combo.currentTextChanged.connect(self.draw_keyboard)
        self.control_layout.addWidget(self.layout_combo)

        self.profile_combo = QComboBox()
        self.refresh_profile_combo()
        self.profile_combo.currentTextChanged.connect(self.load_current_profile)
        self.control_layout.addWidget(self.profile_combo)

        self.btn_manage = QPushButton()
        self.btn_manage.clicked.connect(lambda: ProfileManagerDialog(self).exec())
        self.control_layout.addWidget(self.btn_manage)

        self.btn_settings = QPushButton()
        self.btn_settings.clicked.connect(lambda: SettingsDialog(self.settings, self).exec())
        self.control_layout.addWidget(self.btn_settings)
        self.main_layout.addLayout(self.control_layout)

        self.keyboard_area = QWidget()
        self.keyboard_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.main_layout.addWidget(self.keyboard_area)

        bottom_layout = QHBoxLayout()
        self.description_label = QLabel()
        self.description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.description_label.setWordWrap(True)
        self.description_label.setMinimumHeight(50)
        self.description_label.setMaximumHeight(65)
        self.description_label.setStyleSheet(
            "QLabel { font-size: 14px; padding: 10px; border: 1px solid #bdc3c7; border-radius: 5px; background-color: #ffffff; color: #2c3e50; }")
        bottom_layout.addWidget(self.description_label, stretch=1)

        self.btn_global_save = QPushButton()
        self.btn_global_save.setEnabled(False)
        self.btn_global_save.setMinimumHeight(50)
        self.btn_global_save.clicked.connect(self.save_profile_data)
        bottom_layout.addWidget(self.btn_global_save)

        self.main_layout.addLayout(bottom_layout)

        self.update_ui_texts()
        self.draw_keyboard()

        self.listener_thread = KeyListenerThread()
        self.listener_thread.key_pressed.connect(self.highlight_key)
        self.listener_thread.key_released.connect(self.unhighlight_key)
        self.listener_thread.start()

    def update_ui_texts(self):
        self.setWindowTitle(tr("title"))
        self.btn_manage.setText(tr("manage_profile"))
        self.btn_settings.setText(tr("color_setting"))
        self.description_label.setText(tr("default_desc"))
        self.btn_global_save.setText(tr("save_btn"))

    def mark_as_modified(self):
        self.is_modified = True
        self.btn_global_save.setEnabled(True)

    def save_profile_data(self):
        profile_name = self.profile_combo.currentText()
        if profile_name and profile_name != tr("no_profile"):
            filepath = os.path.join("profiles", f"{profile_name}.json")
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.current_profile_data, f, indent=4, ensure_ascii=False)
            self.is_modified = False
            self.btn_global_save.setEnabled(False)

    def closeEvent(self, event):
        if self.is_modified:
            reply = QMessageBox.question(self, tr("save_confirm"), tr("unsaved_msg"),
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
            if reply == QMessageBox.StandardButton.Yes:
                self.save_profile_data()
                event.accept()
            elif reply == QMessageBox.StandardButton.No:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def sync_profile_data(self):
        self.combo_data.clear()
        shortcuts = self.current_profile_data.get("shortcuts", {})
        for dict_key in shortcuts.keys():
            parts = dict_key.split('+')
            if len(parts) > 1:
                for i, p in enumerate(parts):
                    others = parts[:i] + parts[i + 1:]
                    if p not in self.combo_data:
                        self.combo_data[p] = []
                    self.combo_data[p].extend(others)
        self.apply_profile_colors()

    def load_current_profile(self):
        if self.is_modified:
            reply = QMessageBox.question(self, tr("save_confirm"), tr("modified_msg"),
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.save_profile_data()
            self.is_modified = False
            self.btn_global_save.setEnabled(False)

        profile_name = self.profile_combo.currentText()
        self.current_profile_data = {"shortcuts": {}}

        if profile_name and profile_name != tr("no_profile"):
            filepath = os.path.join("profiles", f"{profile_name}.json")
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        self.current_profile_data = json.load(f)
                        if isinstance(self.current_profile_data.get("shortcuts"), list):
                            self.current_profile_data["shortcuts"] = {}
                except:
                    pass

        self.sync_profile_data()

    def apply_profile_colors(self):
        shortcuts = self.current_profile_data.get("shortcuts", {})
        for btn in self.buttons:
            is_saved = False
            for dict_key in shortcuts.keys():
                parts = dict_key.split('+')
                if len(parts) == 1 and self.is_key_match(parts[0], btn):
                    is_saved = True
                    break
            btn.state = "saved" if is_saved else "base"
        self.update_keyboard_visuals()

    def refresh_all_keys(self):
        self.apply_profile_colors()

    def load_combo_items(self, combo, folder):
        combo.clear()
        files = [f for f in os.listdir(folder) if f.endswith('.json')]
        combo.addItems(files) if files else combo.addItem(tr("no_file"))

    def refresh_profile_combo(self):
        self.profile_combo.clear()
        profiles = profile_manager.get_profiles()
        self.profile_combo.addItems(
            [p.replace('.json', '') for p in profiles]) if profiles else self.profile_combo.addItem(tr("no_profile"))
        self.load_current_profile()

    def handle_left_click(self, key_id):
        if self.is_capturing:
            self.capture_completed.emit(key_id)

    def finish_capture(self, k_str):
        if self.is_capturing:
            self.is_capturing = False
            if k_str == "esc":
                self.open_edit_dialog(self.capture_target_key, self.capture_temp_desc, self.capture_temp_mod)
            else:
                mod_base = k_str.split('_')[0] if '_' in k_str else k_str
                self.open_edit_dialog(self.capture_target_key, self.capture_temp_desc, mod_base)

    def draw_keyboard(self):
        for child in self.keyboard_area.children():
            if isinstance(child, QPushButton): child.deleteLater()
        self.buttons.clear()
        selected_file = self.layout_combo.currentText()
        if not selected_file or selected_file == tr("no_file"): return
        try:
            with open(os.path.join("layouts", selected_file), 'r', encoding='utf-8') as f:
                kle_data = json.load(f)
        except:
            return

        current_y = 0.0
        for row in kle_data:
            current_x, w, h = 0.0, 1.0, 1.0
            for item in row:
                if isinstance(item, dict):
                    current_x += item.get("x", 0.0)
                    current_y += item.get("y", 0.0)
                    w, h = item.get("w", 1.0), item.get("h", 1.0)
                elif isinstance(item, str):
                    btn = KeyButton(item, current_x, current_y, w, h, self.settings, self.keyboard_area)
                    btn.assigned_id = btn.label_id
                    btn.show()
                    btn.right_clicked.connect(self.open_edit_dialog)
                    btn.left_clicked.connect(self.handle_left_click)
                    self.buttons.append(btn)
                    current_x += w
                    w, h = 1.0, 1.0
            current_y += 1.0

        for modifier in ['ctrl', 'shift', 'alt', 'win']:
            mod_btns = [b for b in self.buttons if b.label_id == modifier]
            if len(mod_btns) > 1:
                mod_btns.sort(key=lambda b: b.x())
                mod_btns[0].assigned_id = f"{modifier}_l"
                mod_btns[-1].assigned_id = f"{modifier}_r"

        self.load_current_profile()

    def normalize_key(self, k_str):
        k_str = k_str.lower().strip()
        s_key = chr(115) + chr(112) + chr(97) + chr(99) + chr(101)
        mapping = {
            "caps_lock": "caps lock",
            "page_up": "pgup",
            "page_down": "pgdn",
            "insert": "ins",
            "delete": "del",
            s_key: " "
        }
        for mod in ['ctrl', 'alt', 'shift', 'win']:
            if mod in k_str: return k_str
        return mapping.get(k_str, k_str)

    def update_keyboard_visuals(self):
        for btn in self.buttons:
            btn.update_style()

        active_bases = {k.split('_')[0] if '_' in k else k for k in self.pressed_keys}

        for base_key in active_bases:
            targets = self.combo_data.get(base_key, [])
            for target in targets:
                for btn in self.buttons:
                    if self.is_key_match(target, btn):
                        btn.set_multi_style()

        for pressed in self.pressed_keys:
            for btn in self.buttons:
                if self.is_key_match(pressed, btn):
                    btn.set_pressed_style()

    def highlight_key(self, key_str):
        k_str = self.normalize_key(key_str)

        if self.is_capturing:
            self.capture_completed.emit(k_str)
            return

        if k_str in self.pressed_keys:
            return
        self.pressed_keys.add(k_str)

        self.update_keyboard_visuals()

        shortcuts = self.current_profile_data.get("shortcuts", {})
        active_bases = {k.split('_')[0] if '_' in k else k for k in self.pressed_keys}

        best_match_desc = ""
        best_match_len = 0
        best_match_display = ""

        for dict_key, info in shortcuts.items():
            keys_in_combo = dict_key.split('+')

            if all(k in active_bases for k in keys_in_combo):
                if len(keys_in_combo) > best_match_len:
                    best_match_len = len(keys_in_combo)
                    best_match_desc = info.get("desc", "")
                    best_match_display = f"[{' + '.join(k.upper() for k in keys_in_combo)}] {best_match_desc}"

        if best_match_display:
            self.description_label.setText(best_match_display)
        else:
            self.description_label.setText(tr("default_desc"))

    def unhighlight_key(self, key_str):
        if self.is_capturing:
            return

        k_str = self.normalize_key(key_str)
        self.pressed_keys.discard(k_str)
        self.update_keyboard_visuals()

    def is_key_match(self, input_key, btn):
        b_id = getattr(btn, 'assigned_id', btn.label_id).lower().strip()
        l_id = btn.label_id.lower().strip()

        if input_key == b_id: return True
        if input_key == l_id: return True
        if '\n' in l_id and input_key in l_id.split('\n'): return True
        if b_id == l_id and '_' in input_key:
            base = input_key.split('_')[0]
            if base in ['ctrl', 'alt', 'shift', 'win'] and l_id == base:
                return True
        return False

    def open_edit_dialog(self, key_id, preset_desc=None, preset_mod=None):
        if self.is_capturing: return

        profile_name = self.profile_combo.currentText()
        if profile_name == tr("no_profile") or not profile_name:
            QMessageBox.warning(self, tr("warn"), tr("warn_msg1"))
            return

        if "shortcuts" not in self.current_profile_data:
            self.current_profile_data["shortcuts"] = {}

        dialog = ShortcutEditDialog(key_id, self.current_profile_data["shortcuts"], preset_mod, preset_desc, self)
        result = dialog.exec()

        if dialog.capture_requested:
            self.is_capturing = True
            self.capture_target_key = key_id
            self.capture_temp_desc = dialog.desc_input.text()
            self.current_profile_data["shortcuts"] = dialog.shortcuts_data
            self.description_label.setText(tr("capture_msg"))
            return

        if result == QDialog.DialogCode.Accepted:
            self.current_profile_data["shortcuts"] = dialog.shortcuts_data
            self.mark_as_modified()
            self.sync_profile_data()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = KeyboardApp()
    ex.show()
    sys.exit(app.exec())