# -*- coding: utf-8 -*-

from qfluentwidgets import qconfig, QConfig, ConfigItem, OptionsConfigItem, BoolValidator, RangeConfigItem, \
    RangeValidator


class Config(QConfig):
    Value = RangeConfigItem("MainWindow", "Value", 40, RangeValidator(2, 999))
    Opacity = RangeConfigItem("MainWindow", "Opacity", 60, RangeValidator(1, 100))
    NoRepeat = ConfigItem("MainWindow", "NoRepeat", True, BoolValidator())
    AutoRun = ConfigItem("MainWindow", "AutoRun", True, BoolValidator())
    ShowTime = ConfigItem("MainWindow", "ShowTime", True, BoolValidator())
    IsDark = OptionsConfigItem("MainWindow", "IsDark", True, BoolValidator())


YEAR = "2025"
VERSION = "4.2.5"
cfg = Config()
qconfig.load('config.json', cfg)
