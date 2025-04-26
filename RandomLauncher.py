# -*- coding: utf-8 -*-

import sys
import subprocess
import darkdetect
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow
from qfluentwidgets import Dialog, setTheme, Theme, setThemeColor


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Random")
        self.setWindowIcon(QIcon(":/icon.png"))
        self.resize(400, 300)


class TrayApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.main_window = MainWindow()
        setThemeColor(QColor(9, 81, 41))
        if str(subprocess.run(['tasklist'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW, shell=True)).find("RandomMain.exe") != -1:
            self.showDialog()
        else:
            subprocess.run("RandomMain.exe", shell=True)
            sys.exit()

    def showDialog(self):
        w = Dialog("Random", "Random 已在后台运行")
        w.setTitleBarVisible(False)
        w.yesButton.setText("重启")
        w.cancelButton.setText("取消")
        if w.exec():
            subprocess.run("taskkill -f -im Random.exe", shell=True)
            subprocess.run("RandomMain.exe", shell=True)
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
    app = TrayApp()
    app.run()
