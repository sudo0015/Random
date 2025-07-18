# -*- coding: utf-8 -*-

import sys
import subprocess
import darkdetect
from psutil import process_iter, Process
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QFrame
from qfluentwidgets import Dialog, setTheme, Theme, setThemeColor, FluentStyleSheet, TextWrap, PrimaryPushButton, \
    BodyLabel
from qframelesswindow import FramelessDialog


class Ui_MessageBox:

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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Random")
        self.resize(400, 300)


class App:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.main_window = MainWindow()
        setThemeColor(QColor(9, 81, 41))
        if str(subprocess.run(['tasklist'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW, shell=True)).find("RandomMain.exe") != -1:
            self.showDialog()
        else:
            subprocess.run(["RandomMain.exe", "--force-start"], shell=True)
            sys.exit()

    def killProcess(self, process_name):
        for proc in process_iter(['pid', 'name']):
            try:
                if proc.info['name'].lower() == process_name.lower():
                    pid = proc.info['pid']
                    p = Process(pid)
                    p.kill()
            except:
                pass

    def showDialog(self):
        w = Dialog("提示", "Random 已在后台运行")
        w.yesButton.setText("重启")
        w.cancelButton.setText("取消")
        if w.exec():
            self.killProcess("RandomMain.exe")
            subprocess.run(["RandomMain.exe", "--force-start"], shell=True)
            sys.exit()
        else:
            sys.exit()

    def run(self):
        sys.exit(self.app.exec())


if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    if darkdetect.isDark():
        setTheme(Theme.DARK)
    else:
        setTheme(Theme.LIGHT)
    app = App()
    app.run()
