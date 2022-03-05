from PyQt5.QtCore import (pyqtSignal, QObject)
from cardlib import *


class PlayerState(QObject):
    data_changed = pyqtSignal()

    def __init__(self, name, money):
        super().__init__()
        self.name = name
        self.money = int(money)
        self.bet = 0
        self.wins = 0
        self.active = False
        self.started = False

    def set_active(self, active):
        self.active = active
        self.data_changed.emit()

    def set_starter(self, start):
        self.started = start

    def won(self, amount):
        self.money += int(amount)
        self.wins += 1

    def reset_bet(self):
        self.bet = 0


class MoneyModel:
    pass


class GameModel(QObject):
    data_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.PlayerStates = []
        self.pot = 0

    def start_game(self, player_infos):
        """
        Sets player names and starting money based on input. Sets player 1 as the starting player.
        """
        self.PlayerStates.append(PlayerState(player_infos[0], player_infos[2]))
        self.PlayerStates.append(PlayerState(player_infos[1], player_infos[2]))
        self.data_changed.emit()
        self.PlayerStates[0].set_active(True)
        self.PlayerStates[0].set_starter(True)

    def who_is_active(self):
        for player in self.PlayerStates:
            if player.active:
                active_player = player
            else:
                not_active_player = player
        return active_player, not_active_player

    def new_card_event(self):
        print('NewCardEvent')
        for player in self.PlayerStates:
            if player.started:
                player.set_active(True)
            else:
                player.set_active(False)

    def fold(self):
        players = self.who_is_active()

        players[1].won(self.pot)
        players[1].data_changed.emit()
        self.next_round()
        self.data_changed.emit()

    def all_in(self):
        players = self.who_is_active()

        amount = players[0].money
        self.pot += int(amount)
        players[0].bet += int(amount)
        players[0].money -= int(amount)
        players[0].data_changed.emit()

        self.next_player()
        self.data_changed.emit()

    def bet(self, amount):
        players = self.who_is_active()

        self.pot += int(amount)
        players[0].bet += int(amount)
        players[0].money -= int(amount)
        players[0].data_changed.emit()

        self.next_player()
        self.data_changed.emit()

    def call(self):
        players = self.who_is_active()
        if players[0].bet == players[1].bet and players[0].active != players[0].started:
            self.new_card_event()
        elif players[0].bet == players[1].bet:
            self.next_player()
        else:
            diff_amount = players[1].bet-players[0].bet
            players[0].bet += diff_amount
            players[0].money -= diff_amount
            self.pot += diff_amount
            self.new_card_event()

        players[0].data_changed.emit()
        self.data_changed.emit()

    def evaluate_winner(self):

        self.next_round()
        # Måste ha if bets are equal då vill vi trigga nytt card event

    def next_player(self):
        """
        Switches the active player
        """
        for player in self.PlayerStates:
            if player.active:
                player.set_active(False)
            else:
                player.set_active(True)

    def next_round(self):
        """
        Resets the pot and player bets. Sets the new starting player as active.
        """
        self.pot = 0
        for player in self.PlayerStates:
            player.reset_bet()
            #Släng kort på hand och dra nya
            player.data_changed.emit()

        #Kolla vem som började senast
        for player in self.PlayerStates:
            if player.started:
                player.set_starter(False)
                player.set_active(False)
            else:
                player.set_starter(True)
                player.set_active(True)
        #Släng kort på bordet
        self.data_changed.emit()