import json

from PyQt5.QtWidgets import QMainWindow
from forms.setting import SettingWindows
from PyQt5.QtCore import pyqtSignal


class SettingWindow(QMainWindow, SettingWindows):
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        with open("data/set.json", "r") as f:
            settings = json.load(f)
        self.spinBox.setValue(settings["service1"])
        self.spinBox_2.setValue(settings["service2"])
        self.spinBox_3.setValue(settings["service3"])
        self.spinBox_4.setValue(settings["service4"])
        self.spinBox_5.setValue(settings["service5"])
        self.save_btn.clicked.connect(self.save_settings)

    def save_settings(self):
        settings = {
            "service1": self.spinBox.value(),
            "service2": self.spinBox_2.value(),
            "service3": self.spinBox_3.value(),
            "service4": self.spinBox_4.value(),
            "service5": self.spinBox_5.value(),
        }
        with open("data/set.json", "w") as f:
            json.dump(settings, f)
        self.close()

    def exit(self):
        self.close()
