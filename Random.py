                    
#Copyright (c) 2023 BUG STUDIO. All rights reserved.

import os
import sys
import random
import psutil
import ctypes
import win32gui
import win32con
import hotKey
import res_Random
import tkinter.messagebox
from configparser import ConfigParser
from PySide6.QtCore import Qt,Slot,QPoint,QEvent,QSettings,QAbstractNativeEventFilter,Signal
from PySide6.QtGui import QAction,QIcon,QKeySequence,QShortcut,QCursor,QMouseEvent
from PySide6.QtWidgets import QHBoxLayout,QRadioButton,QGroupBox,QPushButton,QVBoxLayout,QMenu,QSystemTrayIcon,QFormLayout,QLabel,QLineEdit,QWidget,QTabWidget,QCheckBox,QApplication,QWhatsThis
def windowEnumerationHandler(hwnd,windowlist):
    windowlist.append((hwnd,win32gui.GetWindowText(hwnd)))
class Widget(QWidget):
    _isTracking=False
    isPressed = Signal(int)
    def __init__(self):
        super().__init__()
        self.conf=ConfigParser()
        self.conf.read("config.ini")
        self.value=self.conf.getint("random","value")
        self.light_theme=self.conf.getboolean("window","light_theme")
        self.norepeat=self.conf.getboolean("random","norepeat")
        self.arr=[x for x in range(1,self.value+1)]
        self.setWindowTitle("Random")
        self.button=QPushButton("Rd")
        self.button.setFixedSize(70,30)
        if self.light_theme:
            self.button.setStyleSheet("QPushButton{background-color:rgba(255,255,255,50);color:rgba(0,0,0,100);border-radius:15px;border:0.5px groove gray;border-style:outset;font-family:Microsoft YaHei;font-size:15pt;color:rgb(0,0,0);}"
                                      "QPushButton:hover{background-color:rgba(255,255,255,200);color:rgba(0,0,0,255);border-radius:15px;border:0.5px groove gray;border-style:outset;font-family:Microsoft YaHei;font-size:15pt;color:rgb(0,0,0);}"
                                      "QPushButton:pressed{background-color:rgba(255,255,255,200);color:rgba(0,0,0,255);border-radius:15px;border:0.5px groove gray;border-style:outset;font-family:Microsoft YaHei;font-size:15pt;color:rgb(0,0,0);}")
        else:
            self.button.setStyleSheet("QPushButton{background-color:rgba(0,0,0,50);color:rgba(0,0,0,100);border-radius:15px;border:0.5px groove gray;border-style:outset;font-family:Microsoft YaHei;font-size:15pt;color:rgb(255,255,255);}"
                                      "QPushButton:hover{background-color:rgba(0,0,0,200);color:rgba(0,0,0,255);border-radius:15px;border:0.5px groove gray;border-style:outset;font-family:Microsoft YaHei;font-size:15pt;color:rgb(255,255,255);}"
                                      "QPushButton:pressed{background-color:rgba(0,0,0,200);color:rgba(0,0,0,255);border-radius:15px;border:0.5px groove gray;border-style:outset;font-family:Microsoft YaHei;font-size:15pt;color:rgb(255,255,255);}")
        self.button.installEventFilter(self)
        self.layout=QVBoxLayout()
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)
        self.button.clicked.connect(self.run)
        self._restore_action=QAction()
        self._quit_action=QAction()
        self._tray_icon_menu=QMenu()
        self.tray_icon=QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(":/trayIcon.png"))
        self.tray_icon.setToolTip("Random")
        self.create_actions()
        self.create_tray_icon()
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.listen_keyboard_esc()
        self.listen_keyboard_pgup()
        self.listen_keyboard_pgdown()
        self.listen_keyboard_up()
        self.listen_keyboard_down()
        self.listen_keyboard_enter()
        self.listen_keyboard_left()
        self.listen_keyboard_right()
        self.listen_keyboard_tab()
        self.show()
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
        self._setting_action=QAction("设置",self)
        self._setting_action.triggered.connect(self.setting)
        self._hide_action=QAction("隐藏",self)
        self._hide_action.triggered.connect(self.minimize_to_tray)
        self._restore_action=QAction("显示",self)
        self._restore_action.triggered.connect(self.restore_from_tray)
        self._quit_action=QAction("退出",self)
        self._quit_action.triggered.connect(QApplication.quit)
    def create_tray_icon(self):
        self._tray_icon_menu=QMenu(self)
        self._tray_icon_menu.addAction(self._setting_action)
        self._tray_icon_menu.addSeparator()
        self._tray_icon_menu.addAction(self._hide_action)
        self._tray_icon_menu.addAction(self._restore_action)
        self._tray_icon_menu.addSeparator()
        self._tray_icon_menu.addAction(self._quit_action)
        self.tray_icon.setContextMenu(self._tray_icon_menu)
        self.tray_icon.show()
    def listen_keyboard_esc(self):
        shortcut=QShortcut(QKeySequence("Esc"),self)
        shortcut.activated.connect(self.hide)
    def listen_keyboard_pgup(self):
        shortcut=QShortcut(QKeySequence("PgUp"),self)
        shortcut.activated.connect(self.run)
    def listen_keyboard_pgdown(self):
        shortcut=QShortcut(QKeySequence("PgDown"),self)
        shortcut.activated.connect(self.run)
    def listen_keyboard_up(self):
        shortcut=QShortcut(QKeySequence("Up"),self)
        shortcut.activated.connect(self.run)
    def listen_keyboard_down(self):
        shortcut=QShortcut(QKeySequence("Down"),self)
        shortcut.activated.connect(self.run)
    def listen_keyboard_enter(self):
        shortcut=QShortcut(QKeySequence("Enter"),self)
        shortcut.activated.connect(self.run)
    def listen_keyboard_left(self):
        shortcut=QShortcut(QKeySequence("Left"),self)
        shortcut.activated.connect(self.run)
    def listen_keyboard_right(self):
        shortcut=QShortcut(QKeySequence("Right"),self)
        shortcut.activated.connect(self.run)
    def listen_keyboard_tab(self):
        shortcut=QShortcut(QKeySequence("Tab"),self)
        shortcut.activated.connect(self.run)
    def mousePressEvent(self,e:QMouseEvent):
        if e.button()==Qt.LeftButton:
            self._isTracking=True
    def mouseMoveEvent(self,e:QMouseEvent):
        self.move(e.pos()+self.pos())
    def mouseReleaseEvent(self,e:QMouseEvent):
        if e.button()==Qt.LeftButton:
            self._isTracking=False
    def hot_key_event(self,data):
        if data == 12582913:
            self.run()
    @Slot()
    def run(self):
        temp=random.choice(self.arr)
        self.button.setText(str(temp))
        if self.norepeat:
            self.arr.remove(temp)
            if not self.arr:
                self.arr=[x for x in range(1,self.value+1)]
        windowlist=[]
        win32gui.EnumWindows(windowEnumerationHandler,windowlist)
        for i in windowlist:
            if "幻灯片放映" in i[1].lower():
                win32gui.ShowWindow(i[0],4)
                win32gui.SetForegroundWindow(i[0])
                break
if __name__=="__main__":
    app=QApplication(sys.argv)
    widget=Widget()
    widget.move(10,50)
    widget.setWindowFlags(Qt.WindowStaysOnTopHint|Qt.FramelessWindowHint|Qt.Tool)
    widget.setAttribute(Qt.WA_TranslucentBackground)  
    hot_key = hotKey.HotKey()
    hot_key.isPressed.connect(widget.hot_key_event)
    hot_key.start() 
    widget.show()
    sys.exit(app.exec())
