# -*- coding: utf-8 -*-

from qfluentwidgets import qconfig, QConfig, ConfigItem, OptionsConfigItem, BoolValidator, RangeConfigItem, \
    RangeValidator


class Config(QConfig):
    Value = RangeConfigItem("MainWindow", "Value", 40, RangeValidator(2, 999))
    AutoRun = ConfigItem("MainWindow", "AutoRun", True, BoolValidator())
    NoRepeat = ConfigItem("MainWindow", "NoRepeat", True, BoolValidator())
    LightTheme = OptionsConfigItem("MainWindow", "LightTheme", False, BoolValidator())


YEAR = "2025"
VERSION = "4.1.0"
cfg = Config()
qconfig.load('config.json', cfg)
