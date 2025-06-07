# -*- coding: utf-8 -*-

import os
from qfluentwidgets import qconfig, QConfig, ConfigItem, OptionsConfigItem, BoolValidator, RangeConfigItem, \
    RangeValidator, OptionsValidator, ConfigValidator


class Config(QConfig):
    Value = RangeConfigItem("MainWindow", "Value", 40, RangeValidator(2, 999))
    Opacity = RangeConfigItem("MainWindow", "Opacity", 50, RangeValidator(1, 100))
    NoRepeat = ConfigItem("MainWindow", "NoRepeat", True, BoolValidator())
    AutoRun = ConfigItem("MainWindow", "AutoRun", True, BoolValidator())
    ShowTime = ConfigItem("MainWindow", "ShowTime", True, BoolValidator())
    IsDark = OptionsConfigItem("MainWindow", "IsDark", True, BoolValidator())
    dpiScale = OptionsConfigItem("MainWindow", "DpiScale", "Auto", OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]), restart=True)
    Position = OptionsConfigItem("MainWindow", "Position", "TopLeft", OptionsValidator(["TopLeft", "TopCenter", "TopRight", "BottomLeft", "BottomCenter", "BottomRight"]))
    RunHotKey = ConfigItem("MainWindow", "RunHotKey", "Ctrl+F1", ConfigValidator())
    ShowHotKey = ConfigItem("MainWindow", "ShowHotKey", "Ctrl+F2", ConfigValidator())
    HideHotKey = ConfigItem("MainWindow", "HideHotKey", "Ctrl+F3", ConfigValidator())


YEAR = "2025"
VERSION = "4.6.3"
cfg = Config()
qconfig.load(os.path.join(os.path.expanduser('~'), '.Random', 'config', 'config.json'), cfg)
