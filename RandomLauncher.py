# -*- coding: utf-8 -*-

import sys
import subprocess
from qfluentwidgets import Dialog

if str(subprocess.run(['tasklist'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW, shell=True)).find("Random.exe") != -1:
    w = Dialog("Random", "Random已在后台运行。是否重启？")
    w.setTitleBarVisible(False)
    w.yesButton.setText("确定")
    w.cancelButton.setText("取消")
    if w.exec():
        subprocess.run("taskkill -f -im Random.exe", shell=True)
        subprocess.run("RandomMain.exe", shell=True)
    else:
        sys.exit()
else:
    subprocess.run("RandomMain.exe", shell=True)
