import os
import sys
from subprocess import run
import res_RandomSetting
from configparser import ConfigParser
from PySide6.QtCore import Qt,Slot,QPoint,QEvent
from PySide6.QtGui import QAction,QIcon,QKeySequence,QShortcut,QCursor,QMouseEvent
from PySide6.QtWidgets import QHBoxLayout,QRadioButton,QGroupBox,QPushButton,QVBoxLayout,QMenu,QSystemTrayIcon,QFormLayout,QLabel,QLineEdit,QWidget,QTabWidget,QCheckBox,QApplication,QWhatsThis
class Widget(QWidget):
    def __init__(self):
        super().__init__()
        conf=ConfigParser()
        conf.read("config.ini")
        self.light_theme=conf.getboolean("window","light_theme")
        self.value=conf.getint("random","value")
        self.norepeat=conf.getboolean("random","norepeat")
        self.arr=[x for x in range(1,self.value+1)]
        self.setWindowFlags(Qt.WindowCloseButtonHint|Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("Random设置")
        self.setWindowIcon(QIcon(":/icon.png"))  
        self.resize(350,200)
        self.tabWidget = QTabWidget(self)
        self.tabWidget.setTabPosition(QTabWidget.West)
        self.tabWidget.setTabShape(QTabWidget.Rounded)
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tabWidget.addTab(self.tab1, "通用")
        self.tabWidget.addTab(self.tab2, "关于")
        self.tab1Init()
        self.tab2Init()
        self.button_cancel=QPushButton("取消")
        self.button_ok=QPushButton("确定")
        self.button_apply=QPushButton("应用")
        vlayout =QVBoxLayout(self)
        hlayout=QHBoxLayout(self)
        vlayout.addWidget(self.tabWidget)
        vlayout.addLayout(hlayout)
        hlayout.addWidget(self.button_cancel)
        hlayout.addWidget(self.button_ok)
        hlayout.addWidget(self.button_apply)
        self.button_cancel.clicked.connect(self.close)
        self.button_ok.clicked.connect(self.close)
        self.button_apply.clicked.connect(self.Apply)
        self.setLayout(vlayout)
        self.button_apply.setEnabled(False)
    def event(self, event):
        if event.type()==QEvent.EnterWhatsThisMode:
            QWhatsThis.leaveWhatsThisMode()
            os.startfile("config.ini")
        return QWidget.event(self,event)
    def tab1Init(self):
        layout = QFormLayout()
        global line,check,radio_light
        line= QLineEdit()
        line.setText(str(self.value))
        check= QCheckBox("不重复")
        check.setCheckState(Qt.Checked)
        layout.addRow("人数", line)
        layout.addRow(check)
        if self.norepeat:
            check.setChecked(True)
        else:
            check.setChecked(False)
        groupBox = QGroupBox("主题", self)
        radio_light = QRadioButton("浅色", self)
        radio_dark = QRadioButton("深色", self)
        if self.light_theme:
            radio_light.setChecked(True)
        else:
            radio_dark.setChecked(True)
        vLayout = QVBoxLayout(groupBox)
        vLayout.addWidget(radio_light)
        vLayout.addWidget(radio_dark)
        vLayout.addStretch(1)
        groupBox.setLayout(vLayout)
        layout.addRow(groupBox)
        self.tab1.setLayout(layout)
        self.tabWidget.setTabText(0, "设置")
        self.tabWidget.setTabToolTip(0,"设置")
        line.editingFinished.connect(lambda:self.button_apply.setEnabled(True))
        check.stateChanged.connect(lambda:self.button_apply.setEnabled(True))
        radio_light.clicked.connect(lambda:self.button_apply.setEnabled(True))
        radio_dark.clicked.connect(lambda:self.button_apply.setEnabled(True))
    def tab2Init(self):
        layout = QFormLayout()
        layout.addRow(QLabel("Random   v2.1.0"+'\n'+"Developer: sudo (sudobash@qq.com)"+'\n'+"Copyright © 2024 BUG STUDIO. All rights reserved."))
        self.tab2.setLayout(layout)
        self.tabWidget.setTabText(1, "关于")
        self.tabWidget.setTabToolTip(1,"关于")
    def Apply(self):
        conf=ConfigParser()
        conf.read("config.ini")
        conf.set("random","value",line.text())
        conf.set("random","norepeat",str(check.isChecked()))
        conf.set("window","light_theme",str(radio_light.isChecked()))
        with open('config.ini', 'w') as f:
            conf.write(f)
        run("taskkill -f -im Random.exe", shell=True)
        os.startfile("Random.exe")
        self.button_cancel.setEnabled(False)
if __name__=="__main__":
    app=QApplication(sys.argv)
    widget=Widget()
    widget.show()
    sys.exit(app.exec())
