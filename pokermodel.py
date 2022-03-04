from PyQt5.QtCore import (pyqtSignal, QObject)


class PlayerState(QObject):
    data_changed = pyqtSignal()

    def __init__(self, name, money):
        super().__init__()
        self.name = name
        self.money = money
        self.wins = 0
        self.active = False

    def set_active(self, active):
        self.active = active
        self.data_changed.emit()

    def won(self):
        self.wins += 1
        self.data_changed.emit()


# class PotState(QObject):
#     def __init__(self):

class MoneyModel:
    pass



class GameModel(QObject):
    data_changed = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.PlayerStates = []

    def start_game(self, player_infos):
        self.PlayerStates.append(PlayerState(player_infos[0], player_infos[2]))
        self.PlayerStates.append(PlayerState(player_infos[1], player_infos[2]))
        self.data_changed.emit()


    def fold(self):
        pass

    def bet(self):
        pass

    def call(self):
        pass

