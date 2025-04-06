# -*- coding: utf-8 -*-

import os
import sys
import random
import win32gui
import win32con
from RandomConfig import cfg
from ctypes.wintypes import MSG
from ctypes import windll, byref
from PyQt5.QtGui import QIcon, QMouseEvent
from PyQt5.QtCore import Qt, QTimer, QDateTime, pyqtSignal, QThread
from PyQt5.QtWidgets import QAction, QPushButton, QVBoxLayout, QMenu, QSystemTrayIcon, QWidget, QApplication


def windowEnumerationHandler(hwnd, windowlist):
    windowlist.append((hwnd, win32gui.GetWindowText(hwnd)))


class HotKey(QThread):
    isPressed = pyqtSignal(int)

    def __init__(self):
        super(HotKey, self).__init__()
        self.main_key = 192

    def run(self):
        user32 = windll.user32
        while True:
            if not user32.RegisterHotKey(None, 1, win32con.MOD_ALT, self.main_key):
                print("Error")
            try:
                msg = MSG()
                if user32.GetMessageA(byref(msg), None, 0, 0) != 0:
                    if msg.message == win32con.WM_HOTKEY:
                        if msg.wParam == win32con.MOD_ALT:
                            self.isPressed.emit(msg.lParam)
            finally:
                user32.UnregisterHotKey(None, 1)


class Widget(QWidget):
    _isTracking = False
    isPressed = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.value = cfg.Value.value
        self.light_theme = cfg.LightTheme.value
        self.norepeat = cfg.NoRepeat.value
        self.arr = [x for x in range(1, self.value + 1)]
        self.isOnRandom = False

        self.move(10, 50)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setWindowTitle("Random")
        self.button = QPushButton("Rd")
        self.button.setFixedSize(75, 33)
        if self.light_theme:
            self.button.setStyleSheet(
                "QPushButton{background-color:rgba(255,255,255,100);color:rgba(0,0,0,100);border-radius:16px;border:0.5px groove gray;border-style:outset;font-family:Microsoft YaHei;font-size:15pt;color:rgb(0,0,0);}"
                "QPushButton:hover{background-color:rgba(255,255,255,200);color:rgba(0,0,0,255);border-radius:16px;border:0.5px groove gray;border-style:outset;font-family:Microsoft YaHei;font-size:15pt;color:rgb(0,0,0);}"
                "QPushButton:pressed{background-color:rgba(255,255,255,200);color:rgba(0,0,0,255);border-radius:16px;border:0.5px groove gray;border-style:outset;font-family:Microsoft YaHei;font-size:15pt;color:rgb(0,0,0);}")
        else:
            self.button.setStyleSheet(
                "QPushButton{background-color:rgba(0,0,0,100);color:rgba(0,0,0,100);border-radius:16px;border:0.5px groove gray;border-style:outset;font-family:Microsoft YaHei;font-size:15pt;color:rgb(255,255,255);}"
                "QPushButton:hover{background-color:rgba(0,0,0,200);color:rgba(0,0,0,255);border-radius:16px;border:0.5px groove gray;border-style:outset;font-family:Microsoft YaHei;font-size:15pt;color:rgb(255,255,255);}"
                "QPushButton:pressed{background-color:rgba(0,0,0,200);color:rgba(0,0,0,255);border-radius:16px;border:0.5px groove gray;border-style:outset;font-family:Microsoft YaHei;font-size:15pt;color:rgb(255,255,255);}")
        self.button.installEventFilter(self)
        self.button.clicked.connect(self.run)
        self.updateTime()

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)

        self.timer = QTimer()
        self.timer.start(1000)
        self.timer.timeout.connect(self.updateTime)

        self._restore_action = QAction()
        self._quit_action = QAction()
        self._tray_icon_menu = QMenu()
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("icon.png"))
        self.tray_icon.setToolTip("Random")
        self.create_actions()
        self.create_tray_icon()
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.tray_icon_activated)

        self.hotKey = HotKey()
        self.hotKey.isPressed.connect(self.hotKeyEvent)
        self.hotKey.start()

        self.show()

    def updateTime(self):
        if not self.isOnRandom:
            self.button.setText(QDateTime.currentDateTime().toString('hh:mm'))

    def minimize_to_tray(self):
        self.hide()

    def restore_from_tray(self):
        if self.isMinimized():
            self.showNormal()
        elif self.isMaximized():
            self.showMaximized()
        else:
            self.show()

    def setting(self):
        os.startfile("RandomSetting.exe")

    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.restore_from_tray()

    def create_actions(self):
        self._setting_action = QAction("设置", self)
        self._setting_action.triggered.connect(self.setting)
        self._hide_action = QAction("隐藏", self)
        self._hide_action.triggered.connect(self.minimize_to_tray)
        self._restore_action = QAction("显示", self)
        self._restore_action.triggered.connect(self.restore_from_tray)
        self._quit_action = QAction("退出", self)
        self._quit_action.triggered.connect(QApplication.quit)

    def create_tray_icon(self):
        self._tray_icon_menu = QMenu(self)
        self._tray_icon_menu.addAction(self._setting_action)
        self._tray_icon_menu.addSeparator()
        self._tray_icon_menu.addAction(self._hide_action)
        self._tray_icon_menu.addAction(self._restore_action)
        self._tray_icon_menu.addSeparator()
        self._tray_icon_menu.addAction(self._quit_action)
        self.tray_icon.setContextMenu(self._tray_icon_menu)
        self.tray_icon.show()

    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self._isTracking = True

    def mouseMoveEvent(self, e: QMouseEvent):
        self.move(e.pos() + self.pos())

    def mouseReleaseEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self._isTracking = False

    def hotKeyEvent(self, data):
        if data == 12582913:
            self.run()

    def cancelOnRandom(self):
        self.isOnRandom = False

    def run(self):
        temp = random.choice(self.arr)
        self.button.setText(str(temp))
        if self.norepeat:
            self.arr.remove(temp)
            if not self.arr:
                self.arr = [x for x in range(1, self.value + 1)]

        self.isOnRandom = True
        QTimer.singleShot(5000, self.cancelOnRandom)

        windowlist = []
        win32gui.EnumWindows(windowEnumerationHandler, windowlist)
        for i in windowlist:
            if "幻灯片放映" in i[1].lower():
                win32gui.ShowWindow(i[0], 4)
                win32gui.SetForegroundWindow(i[0])
                break


if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    widget = Widget()
    widget.show()
    sys.exit(app.exec())
