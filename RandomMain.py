# -*- coding: utf-8 -*-

import os
import sys
import random
import win32gui
import win32con
import subprocess
import darkdetect
import portalocker
import RandomResource
from RandomConfig import cfg
from ctypes.wintypes import MSG
from ctypes import windll, byref
from PyQt5.QtGui import QIcon, QMouseEvent, QCursor
from PyQt5.QtCore import Qt, QTimer, QDateTime, pyqtSignal, QThread
from PyQt5.QtWidgets import QAction, QPushButton, QVBoxLayout, QSystemTrayIcon, QWidget, QApplication
from qfluentwidgets import RoundMenu, setTheme, Theme, Dialog
from qfluentwidgets import FluentIcon as FIF


def windowEnumerationHandler(hwnd, windowlist):
    windowlist.append((hwnd, win32gui.GetWindowText(hwnd)))


class Mutex:
    def __init__(self):
        self.file = None

    def __enter__(self):
        self.file = open('RandomMain.lockfile', 'w')
        try:
            portalocker.lock(self.file, portalocker.LOCK_EX | portalocker.LOCK_NB)
        except portalocker.AlreadyLocked:
            sys.exit()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            portalocker.unlock(self.file)
            self.file.close()
            os.remove('RandomMain.lockfile')


class HotKey(QThread):
    isPressed = pyqtSignal(int)
    showDialogRequested = pyqtSignal()

    def __init__(self):
        super(HotKey, self).__init__()
        self.main_key = 192
        self.isListening = True

    def run(self):
        while self.isListening:
            if not windll.user32.RegisterHotKey(None, 1, win32con.MOD_ALT, self.main_key):
                self.isListening = False
                self.showDialogRequested.emit()
                return
            try:
                msg = MSG()
                if windll.user32.GetMessageA(byref(msg), None, 0, 0) != 0:
                    if msg.message == win32con.WM_HOTKEY:
                        if msg.wParam == win32con.MOD_ALT:
                            self.isPressed.emit(msg.lParam)
            finally:
                windll.user32.UnregisterHotKey(None, 1)


class Widget(QWidget):
    _isTracking = False
    isPressed = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.value = cfg.Value.value
        self.isDark = cfg.IsDark.value
        self.norepeat = cfg.NoRepeat.value
        self.arr = [x for x in range(1, self.value + 1)]
        self.isOnRandom = False

        self.setWindowTitle("Random")
        self.button = QPushButton("Rd")
        self.button.setFixedSize(75, 33)
        self.setFixedSize(100, 50)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        if not self.isDark:
            self.button.setStyleSheet(
                "QPushButton{background-color:rgba(249,249,249," + str(2.55*cfg.Opacity.value) + ");color:rgba(249,249,249," + str(2.55*cfg.Opacity.value) + ");border-radius:16px;border:0.5px groove gray;border-style:outset;font-family:Microsoft YaHei;font-size:15pt;color:rgb(0,0,0);}"
                "QPushButton:hover{background-color:rgba(249,249,249,255);color:rgba(249,249,249,255);border-radius:16px;border:0.5px groove gray;border-style:outset;font-family:Microsoft YaHei;font-size:15pt;color:rgb(0,0,0);}"
                "QPushButton:pressed{background-color:rgba(249,249,249,255);color:rgba(249,249,249,255);border-radius:16px;border:0.5px groove gray;border-style:outset;font-family:Microsoft YaHei;font-size:15pt;color:rgb(0,0,0);}")
        else:
            self.button.setStyleSheet(
                "QPushButton{background-color:rgba(39,39,39," + str(2.55*cfg.Opacity.value) + ");color:rgba(39,39,39," + str(2.55*cfg.Opacity.value) + ");border-radius:16px;border:0.5px groove gray;border-style:outset;font-family:Microsoft YaHei;font-size:15pt;color:rgb(255,255,255);}"
                "QPushButton:hover{background-color:rgba(39,39,39,255);color:rgba(39,39,39,255);border-radius:16px;border:0.5px groove gray;border-style:outset;font-family:Microsoft YaHei;font-size:15pt;color:rgb(255,255,255);}"
                "QPushButton:pressed{background-color:rgba(39,39,39,255);color:rgba(39,39,39,255);border-radius:16px;border:0.5px groove gray;border-style:outset;font-family:Microsoft YaHei;font-size:15pt;color:rgb(255,255,255);}")
        self.button.installEventFilter(self)
        self.button.clicked.connect(self.run)
        self.updateTime()

        self.desktop = QApplication.screens()[0].size()
        self.moveWidget(cfg.Position.value)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.button)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setAlignment(Qt.AlignCenter)
        self.setLayout(self.layout)

        self.timer = QTimer()
        self.timer.start(1000)
        self.timer.timeout.connect(self.updateTime)

        self._restore_action = QAction()
        self._quit_action = QAction()
        self._tray_icon_menu = RoundMenu()
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(":/icon.png"))
        self.tray_icon.setToolTip("Random")
        self.createActions()
        self.createTrayIcon()
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.trayIconActivated)

        self.hotKey = HotKey()
        self.hotKey.isPressed.connect(self.hotKeyEvent)
        self.hotKey.showDialogRequested.connect(self.showHotkeyWarning)
        self.hotKey.start()
        self.show()

    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self._isTracking = True
        elif e.button() == Qt.RightButton:
            self._tray_icon_menu.exec(QCursor.pos())

    def mouseMoveEvent(self, e: QMouseEvent):
        self.move(e.pos() + self.pos())

    def mouseReleaseEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self._isTracking = False

    def moveWidget(self, position):
        if position == "TopLeft":
            self.move(10, 50)
        elif position == "TopCenter":
            self.move(self.desktop.width() // 2 - self.width() // 2, 50)
        elif position == "TopRight":
            self.move(self.desktop.width() - 10 - self.width(), 50)
        elif position == "BottomLeft":
            self.move(10, self.desktop.height() - 100 - self.height())
        elif position == "BottomCenter":
            self.move(self.desktop.width() // 2 - self.width() // 2, self.desktop.height() - 100 - self.height())
        elif position == "BottomRight":
            self.move(self.desktop.width() - 10 - self.width(), self.desktop.height() - 100 - self.height())

    def updateTime(self):
        if not self.isOnRandom:
            self.button.setText(QDateTime.currentDateTime().toString('hh:mm'))

    def restoreFromTray(self):
        if self.isMinimized():
            self.showNormal()
        elif self.isMaximized():
            self.showMaximized()
        else:
            self.show()

    def trayIconActivated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger or reason == QSystemTrayIcon.ActivationReason.Context:
            self._tray_icon_menu.exec(QCursor.pos())

    def createActions(self):
        self._setting_action = QAction(FIF.SETTING.icon(), "设置", self)
        self._setting_action.triggered.connect(lambda: subprocess.Popen("RandomSetting.exe", shell=True))

        self._reset_action = QAction(FIF.CANCEL.icon(), "复位", self)
        self._topleft_action = QAction("左上", self)
        self._topcenter_action = QAction("上中", self)
        self._topright_action = QAction("右上", self)
        self._bottomleft_action = QAction("左下", self)
        self._bottomcenter_action = QAction("下中", self)
        self._bottomright_action = QAction("右下", self)
        self._reset_action.triggered.connect(lambda: self.moveWidget(cfg.Position.value))
        self._topleft_action.triggered.connect(lambda: self.moveWidget("TopLeft"))
        self._topcenter_action.triggered.connect(lambda: self.moveWidget("TopCenter"))
        self._topright_action.triggered.connect(lambda: self.moveWidget("TopRight"))
        self._bottomleft_action.triggered.connect(lambda: self.moveWidget("BottomLeft"))
        self._bottomcenter_action.triggered.connect(lambda: self.moveWidget("BottomCenter"))
        self._bottomright_action.triggered.connect(lambda: self.moveWidget("BottomRight"))


        self._hide_action = QAction(FIF.REMOVE_FROM.icon(), "隐藏", self)
        self._restore_action = QAction(FIF.ADD_TO.icon(), "显示", self)
        self._hide_action.triggered.connect(self.hide)
        self._restore_action.triggered.connect(self.restoreFromTray)

        self._quit_action = QAction(FIF.CLOSE.icon(), "退出", self)
        self._quit_action.triggered.connect(self.quit)

    def createTrayIcon(self):
        self.subMenu = RoundMenu("移动")
        self.subMenu.setIcon(FIF.MOVE)
        self.subMenu.addActions([self._topleft_action, self._topcenter_action, self._topright_action, self._bottomleft_action, self._bottomcenter_action, self._bottomright_action])

        self._tray_icon_menu.addAction(self._setting_action)
        self._tray_icon_menu.addSeparator()
        self._tray_icon_menu.addAction(self._reset_action)
        self._tray_icon_menu.addMenu(self.subMenu)
        self._tray_icon_menu.addSeparator()
        self._tray_icon_menu.addAction(self._restore_action)
        self._tray_icon_menu.addAction(self._hide_action)
        self._tray_icon_menu.addSeparator()
        self._tray_icon_menu.addAction(self._quit_action)
        self.tray_icon.setContextMenu(self._tray_icon_menu)
        self.tray_icon.show()

    def quit(self):
        self.tray_icon.hide()
        self.tray_icon.deleteLater()
        QApplication.quit()
        sys.exit()

    def hotKeyEvent(self, data):
        if data == 12582913:
            self.run()

    def showHotkeyWarning(self):
        w = Dialog("Random", "检测到热键冲突", self)
        w.setTitleBarVisible(False)
        w.yesButton.setText("转到设置")
        w.cancelButton.setText("忽略")
        w.move(self.desktop.width() // 2 - w.width() // 2, self.desktop.height() // 2 - w.height() // 2)
        if w.exec():
            subprocess.Popen("RandomSetting.exe", shell=True)
        else:
            pass

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
    if (len(sys.argv) == 2 and sys.argv[1] == '--force-start') or cfg.AutoRun.value:
        with Mutex():
            QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
            QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
            QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
            if darkdetect.isDark():
                setTheme(Theme.DARK)
            else:
                setTheme(Theme.LIGHT)
            app = QApplication(sys.argv)
            widget = Widget()
            widget.show()
            sys.exit(app.exec())
    else:
        sys.exit()
