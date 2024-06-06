import win32con
from ctypes import *
from ctypes.wintypes import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import tkinter.messagebox
main_key = 192
class HotKey(QThread):
    isPressed = Signal(int)
    def __init__(self):
        super(HotKey, self).__init__()
        self.main_key = 192
    def run(self):
        user32 = windll.user32
        while True:
            if not user32.RegisterHotKey(None, 1, win32con.MOD_ALT, self.main_key):  # alt+~
                tkinter.messagebox.showerror("错误","全局热键注册失败。")
            try:
                msg = MSG()
                if user32.GetMessageA(byref(msg), None, 0, 0) != 0:
                    if msg.message == win32con.WM_HOTKEY:
                        if msg.wParam == win32con.MOD_ALT:
                            self.isPressed.emit(msg.lParam)
            finally:
                success=user32.UnregisterHotKey(None, 1)
