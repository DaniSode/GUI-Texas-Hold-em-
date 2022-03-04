from PyQt5.QtCore import (pyqtSignal, QObject)


class PlayerState(QObject):
    data_changed = pyqtSignal()

    def __init__(self, name, money):
        super().__init__()
        self.name = name
        self.money = int(money)
        self.bet = 0
        self.wins = 0
        self.active = False

    def set_active(self, active):
        self.active = active
        self.data_changed.emit()

    def won(self):
        self.wins += 1
        self.data_changed.emit()


class MoneyModel:
    pass


class GameModel(QObject):
    data_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.PlayerStates = []
        self.pot = 0

    def start_game(self, player_infos):
        self.PlayerStates.append(PlayerState(player_infos[0], player_infos[2]))
        self.PlayerStates.append(PlayerState(player_infos[1], player_infos[2]))
        self.data_changed.emit()
        self.PlayerStates[0].set_active(True)

    def next_player(self):
        for player in self.PlayerStates:
            if player.active:
                player.set_active(False)
            else:
                player.set_active(True)

    def fold(self):
        pass

    def bet(self, amount):

        for player in self.PlayerStates:
            if player.active:
                self.pot += int(amount)
                player.bet += int(amount)
                player.money -= int(amount)
                player.data_changed.emit()

        self.next_player()
        self.data_changed.emit()

    def call(self):
        pass
