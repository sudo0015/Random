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
from PyQt5.QtWidgets import QAction, QPushButton, QVBoxLayout, QSystemTrayIcon, QWidget, QApplication, QHBoxLayout, \
    QLabel, QFrame
from qfluentwidgets import RoundMenu, setTheme, Theme, BodyLabel, PrimaryPushButton, TextWrap, FluentStyleSheet
from qframelesswindow import FramelessDialog
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


class Ui_MessageBox:
    """ Ui of message box """

    yesSignal = pyqtSignal()
    cancelSignal = pyqtSignal()

    def _setUpUi(self, title, content, parent):
        self.content = content
        self.titleLabel = QLabel(title, parent)
        self.contentLabel = BodyLabel(content, parent)

        self.buttonGroup = QFrame(parent)
        self.yesButton = PrimaryPushButton(self.tr('OK'), self.buttonGroup)
        self.cancelButton = QPushButton(self.tr('Cancel'), self.buttonGroup)

        self.vBoxLayout = QVBoxLayout(parent)
        self.textLayout = QVBoxLayout()
        self.buttonLayout = QHBoxLayout(self.buttonGroup)

        self.__initWidget()

    def __initWidget(self):
        self.__setQss()
        self.__initLayout()

        self.yesButton.setAttribute(Qt.WA_LayoutUsesWidgetRect)
        self.cancelButton.setAttribute(Qt.WA_LayoutUsesWidgetRect)

        self.yesButton.setFocus()
        self.buttonGroup.setFixedHeight(81)

        self.contentLabel.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._adjustText()

        self.yesButton.clicked.connect(self.__onYesButtonClicked)
        self.cancelButton.clicked.connect(self.__onCancelButtonClicked)

    def _adjustText(self):
        if self.isWindow():
            if self.parent():
                w = max(self.titleLabel.width(), self.parent().width())
                chars = max(min(w / 9, 140), 30)
            else:
                chars = 100
        else:
            w = max(self.titleLabel.width(), self.window().width())
            chars = max(min(w / 9, 100), 30)

        self.contentLabel.setText(TextWrap.wrap(self.content, chars, False)[0])

    def __initLayout(self):
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.addLayout(self.textLayout, 1)
        self.vBoxLayout.addWidget(self.buttonGroup, 0, Qt.AlignBottom)
        self.vBoxLayout.setSizeConstraint(QVBoxLayout.SetMinimumSize)

        self.textLayout.setSpacing(12)
        self.textLayout.setContentsMargins(24, 24, 24, 24)
        self.textLayout.addWidget(self.titleLabel, 0, Qt.AlignTop)
        self.textLayout.addWidget(self.contentLabel, 0, Qt.AlignTop)

        self.buttonLayout.setSpacing(12)
        self.buttonLayout.setContentsMargins(24, 24, 24, 24)
        self.buttonLayout.addWidget(self.yesButton, 1, Qt.AlignVCenter)
        self.buttonLayout.addWidget(self.cancelButton, 1, Qt.AlignVCenter)

    def __onCancelButtonClicked(self):
        self.reject()
        self.cancelSignal.emit()

    def __onYesButtonClicked(self):
        self.accept()
        self.yesSignal.emit()

    def __setQss(self):
        self.titleLabel.setObjectName("titleLabel")
        self.contentLabel.setObjectName("contentLabel")
        self.buttonGroup.setObjectName('buttonGroup')
        self.cancelButton.setObjectName('cancelButton')

        FluentStyleSheet.DIALOG.apply(self)
        FluentStyleSheet.DIALOG.apply(self.contentLabel)

        self.yesButton.adjustSize()
        self.cancelButton.adjustSize()

    def setContentCopyable(self, isCopyable: bool):
        """ set whether the content is copyable """
        if isCopyable:
            self.contentLabel.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse)
        else:
            self.contentLabel.setTextInteractionFlags(
                Qt.TextInteractionFlag.NoTextInteraction)


class Dialog(FramelessDialog, Ui_MessageBox):
    """ Dialog box """

    yesSignal = pyqtSignal()
    cancelSignal = pyqtSignal()

    def __init__(self, title: str, content: str, parent=None):
        super().__init__(parent=parent)
        self._setUpUi(title, content, self)

        self.windowTitleLabel = QLabel("Random", self)

        self.setResizeEnabled(False)
        self.resize(240, 192)
        self.titleBar.hide()

        self.vBoxLayout.insertWidget(0, self.windowTitleLabel, 0, Qt.AlignTop)
        self.windowTitleLabel.setObjectName('windowTitleLabel')
        FluentStyleSheet.DIALOG.apply(self)
        self.setFixedSize(self.size())


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
    isPressed = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.value = cfg.Value.value
        self.isDark = cfg.IsDark.value
        self.norepeat = cfg.NoRepeat.value
        self.arr = [x for x in range(1, self.value + 1)]
        self.isShowTime = cfg.ShowTime.value
        self.isOnRandom = False
        self.isTracking = False

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

        self.desktop = QApplication.screens()[0].size()
        self.moveWidget(cfg.Position.value)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.button)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setAlignment(Qt.AlignCenter)
        self.setLayout(self.layout)

        if self.isShowTime:
            self.updateTime()
            self.timer = QTimer()
            self.timer.start(1000)
            self.timer.timeout.connect(self.updateTime)
            self.onRandomTimer = QTimer()
            self.onRandomTimer.timeout.connect(self.cancelOnRandom)

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
            self.isTracking = True
        elif e.button() == Qt.RightButton:
            self._tray_icon_menu.exec(QCursor.pos())

    def mouseMoveEvent(self, e: QMouseEvent):
        self.move(e.pos() + self.pos())

    def mouseReleaseEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self.isTracking = False

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
        self._help_action = QAction(FIF.HELP.icon(), "帮助", self)
        self._setting_action.triggered.connect(lambda: subprocess.Popen("RandomSetting.exe", shell=True))
        self._help_action.triggered.connect(lambda: os.startfile(os.path.abspath("./Doc/RandomHelp.html")))

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
        self._tray_icon_menu.addAction(self._help_action)
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
        w = Dialog("错误", "检测到热键冲突", self)
        w.yesButton.setText("转到设置")
        w.cancelButton.setText("忽略")
        w.move(self.desktop.width() // 2 - w.width() // 2, self.desktop.height() // 2 - w.height() // 2)
        if w.exec():
            subprocess.Popen("RandomSetting.exe", shell=True)
        else:
            pass

    def updateTime(self):
        if not self.isOnRandom:
            self.button.setText(QDateTime.currentDateTime().toString('hh:mm'))

    def cancelOnRandom(self):
        self.isOnRandom = False

    def run(self):
        temp = random.choice(self.arr)
        self.button.setText(str(temp))
        if self.norepeat:
            self.arr.remove(temp)
            if not self.arr:
                self.arr = [x for x in range(1, self.value + 1)]

        if self.isShowTime:
            self.isOnRandom = True
            if self.onRandomTimer.isActive():
                self.onRandomTimer.stop()
                self.onRandomTimer.start(5000)
            else:
                self.onRandomTimer.start(5000)

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
