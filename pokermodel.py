from PyQt5.QtCore import (pyqtSignal, QObject)


class PlayerState(QObject):
    data_changed = pyqtSignal()

    def __init__(self, name):
        super().__init__()
        self.name = name
        self.wins = 0
        self.active = False

    def set_active(self, active):
        self.active = active
        self.data_changed.emit()

    def won(self):
        self.wins += 1
        self.data_changed.emit()


class PotState(QObject):
    def __init__(self):


class TexasHoldEm(QObject):

    def __init__(self):

    def fold(self):
        pass

    def bet(self):
        pass

    def call(self):
        pass
