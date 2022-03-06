# DAT-171: Computer assignment 3
# Authors: Daniel Soderqvist and Felix Mare


from PyQt5.QtCore import (pyqtSignal, QObject)
from cardlib import *


class CardModel(QObject):
    """ Base class that described what is expected from the CardView widget """

    new_cards = pyqtSignal()  #: Signal should be emited when cards change.

    @abstractmethod
    def __iter__(self):
        """Returns an iterator of card objects"""

    @abstractmethod
    def flipped(self):
        """Returns true of cards should be drawn face down"""


class HandModel(Hand, CardModel):
    """
    A class representing the handmodel.
    """
    def __init__(self):
        Hand.__init__(self)
        CardModel.__init__(self)
        # Additional state needed by the UI
        self.flipped_cards = False

    def __iter__(self):
        return iter(self.cards)

    def flip(self):
        """
        Flips over the cards (to hide them)
        """
        self.flipped_cards = not self.flipped_cards
        self.new_cards.emit()  # something changed, better emit the signal!

    def flipped(self):
        """
        This model only flips all or no cards
        """
        return self.flipped_cards

    def add_card(self, card):
        super().add_card(card)
        self.new_cards.emit()  # something changed, better emit the signal!


class PlayerState(QObject):
    """
    A Class representing a player state containing name, money, bet etc.
    """
    data_changed = pyqtSignal()

    def __init__(self, name, money):
        super().__init__()
        self.hand = HandModel()
        self.name = name
        self.money = int(money)
        self.bet = 0
        self.wins = 0
        self.active = False
        self.started = False

    def set_active(self, active):
        """
        A method that sets a player as active or not.
        """
        self.active = active
        self.data_changed.emit()

    def set_starter(self, start):
        """
        A method that sets if a player has started a round or not.
        """
        self.started = start
        self.data_changed.emit()

    def won(self, amount):
        """
        A method that adds the pot to the player's money.
        """
        self.money += int(amount)
        self.wins += 1
        self.data_changed.emit()

    def reset_bet(self):
        """
        A method that resets a player's bet.
        """
        self.bet = 0
        self.data_changed.emit()


class TableState(QObject):
    """
    A class representing the table containing its cards.
    """
    data_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.tablecards = HandModel()
        self.data_changed.emit()


class Blinds(QObject):  # NOT YET IMPLEMENTED
    """
    A class representing small and big blind.
    """
    data_changed = pyqtSignal()

    def __init__(self, small, big):
        super().__init__()
        self.small = int(small)
        self.big = int(big)


class GameModel(QObject):
    """
    A class containing all the information and actions to play a game of texas hold em.
    """
    signal_bet = pyqtSignal(str)
    signal_call = pyqtSignal(str)
    signal_fold = pyqtSignal(str)
    signal_all_in = pyqtSignal(str)
    signal_winner = pyqtSignal(str)
    signal_endround = pyqtSignal()
    signal_endgame = pyqtSignal(str)
    data_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.endgame = False
        self.PlayerStates = []
        self.pot = 0
        self.deck = StandardDeck()
        self.deck.shuffle()
        self.tablestate = TableState()
        self.blinds = []

    def start_game(self, player_infos):
        """
        Sets player names and starting money based on input. Sets player 1 as the starting player.
        """
        self.PlayerStates.append(PlayerState(player_infos[0], player_infos[2]))
        self.PlayerStates.append(PlayerState(player_infos[1], player_infos[2]))

        # In case of implementing blinds
        # self.blinds = Blinds(player_infos[-2], player_infos[-1])
        # self.PlayerStates[0].bet += self.blinds.small
        # self.PlayerStates[1].bet += self.blinds.big
        # self.PlayerStates[0].money -= self.blinds.small
        # self.PlayerStates[1].money -= self.blinds.big

        self.data_changed.emit()
        self.PlayerStates[0].set_active(True)
        self.PlayerStates[1].hand.flip()
        self.PlayerStates[0].set_starter(True)
        for player in self.PlayerStates:
            player.hand.add_card((self.deck.draw()))
            player.hand.add_card((self.deck.draw()))

    def who_is_active(self):
        """
        A method returning a list with the active and not active players. First player is the active one.
        """
        for player in self.PlayerStates:
            if player.active:
                active_player = player
                player.hand.flipped_cards = True
            else:
                not_active_player = player
                player.hand.flipped_cards = False
        self.data_changed.emit()

        return active_player, not_active_player

    def new_card_event(self):
        """
        A method that puts additional cards on the table depending on the state of the game. Also sets the start player
        as active.
        """
        self.PlayerStates[0].bet = 0
        self.PlayerStates[1].bet = 0

        if len(self.tablestate.tablecards.cards) == 0:
            self.tablestate.tablecards.add_card(self.deck.draw())
            self.tablestate.tablecards.add_card(self.deck.draw())
            self.tablestate.tablecards.add_card(self.deck.draw())
        elif len(self.tablestate.tablecards.cards) == 3:
            self.tablestate.tablecards.add_card(self.deck.draw())
        elif len(self.tablestate.tablecards.cards) == 4:
            self.tablestate.tablecards.add_card(self.deck.draw())
        else:
            self.evaluate_winner()

        for player in self.PlayerStates:
            if player.started:
                player.set_active(True)
            else:
                player.set_active(False)

    def fold(self):
        """
        A method that makes the active player fold.
        """
        self.PlayerStates[0].hand.flipped_cards = False
        self.PlayerStates[1].hand.flipped_cards = False
        self.PlayerStates[0].data_changed.emit()
        self.PlayerStates[1].data_changed.emit()
        players = self.who_is_active()
        self.signal_winner.emit(f"{players[0].name} folded!\n{players[1].name} wins the pot of {self.pot}.")
        players[1].won(self.pot)
        players[1].data_changed.emit()
        self.next_round()
        self.data_changed.emit()

    def all_in(self):
        """
        A method that makes the active player go all in
        """
        players = self.who_is_active()
        amount = players[0].money
        if players[0].money + players[0].bet > players[1].money + players[1].bet:
            self.signal_all_in.emit("You can't bet more than your opponent's money!")
        elif players[0].money + players[0].bet == players[1].bet:
            self.pot += int(amount)
            players[0].bet += int(amount)
            players[0].money -= int(amount)
            players[0].data_changed.emit()
            self.signal_all_in.emit(f'{players[0].name} is all in!')
            while len(self.tablestate.tablecards.cards) != 5:
                self.new_card_event()
            self.evaluate_winner()
            self.data_changed.emit()
        elif self.PlayerStates[0].money == 0 or self.PlayerStates[0].money == 0:
            while len(self.tablestate.tablecards.cards) != 5:
                self.new_card_event()
            self.evaluate_winner()
            self.data_changed.emit()
        else:
            self.pot += int(amount)
            players[0].bet += int(amount)
            players[0].money -= int(amount)
            players[0].data_changed.emit()
            self.signal_all_in.emit(f'{players[0].name} is all in!')
            self.next_player()
            self.data_changed.emit()

    def bet(self, raise_amount):
        """
        A method that makes the active player bet with a given amount.
        """
        players = self.who_is_active()
        amount = int(raise_amount) + int(players[1].bet) - int(players[0].bet)
        if int(amount) > players[0].money:
            self.signal_bet.emit("You don't have enough money!\nTry a smaller bet!")
        elif int(amount) == 0 or amount == '':
            self.signal_bet.emit("You need to atleast bet 1 or check!")
        elif int(amount) - players[0].money == 0:
            self.signal_bet.emit("Are you sure you want to go all in?\nPress All In button")
        elif int(amount) > players[1].money + players[1].bet:
            self.signal_bet.emit("You can't bet more than your opponent's money!\nTry a smaller bet!")
        else:
            if players[0].bet == players[1].bet:
                self.signal_bet.emit(f"{players[0].name} bet {amount}")
            else:
                self.signal_bet.emit(f"{players[0].name} called {players[1].name} and raised them {int(raise_amount)}")

            self.pot += int(amount)
            players[0].bet += int(amount)
            players[0].money -= int(amount)
            players[0].data_changed.emit()
            self.next_player()
            self.data_changed.emit()

    def call(self):
        """
        A method that makes the active player call the current bet or check.
        """
        players = self.who_is_active()
        if players[0].bet == players[1].bet and players[0].active != players[0].started:
            self.signal_call.emit(f"{players[0].name} checked")
            self.new_card_event()
        elif players[0].bet == players[1].bet:
            self.signal_call.emit(f"{players[0].name} checked")
            self.next_player()
        else:
            diff_amount = players[1].bet-players[0].bet
            players[0].bet += diff_amount
            players[0].money -= diff_amount
            self.pot += diff_amount
            self.signal_call.emit(f"{players[0].name} called {players[1].name}")
            if players[0].money == 0:
                self.signal_call.emit("Are you sure you want to go all in?\nPress All In button")
                return
            if players[1].money == 0:
                while len(self.tablestate.tablecards.cards) != 5:
                    self.new_card_event()
                self.evaluate_winner()
                return
            self.new_card_event()
        players[0].data_changed.emit()
        self.data_changed.emit()

    def evaluate_winner(self):
        """
        A method that evaluates the winner of the round. Shows both of the players cards and emits a signal with information
        regarding the players PokerHands.
        """
        self.PlayerStates[0].hand.flipped_cards = False
        self.PlayerStates[1].hand.flipped_cards = False
        self.PlayerStates[0].data_changed.emit()
        self.PlayerStates[1].data_changed.emit()

        bph0 = self.PlayerStates[0].hand.best_poker_hand(self.tablestate.tablecards.cards)
        bph1 = self.PlayerStates[1].hand.best_poker_hand(self.tablestate.tablecards.cards)

        hand_string = f'{self.PlayerStates[0].name} has {str(bph0)}, {self.PlayerStates[1].name} has {str(bph1)}. '

        if bph0 > bph1:
            self.PlayerStates[0].won(self.pot)
            self.signal_winner.emit(hand_string+f'{self.PlayerStates[0].name} wins the pot of {self.pot}!')

        elif bph1 > bph0:
            self.PlayerStates[1].won(self.pot)
            self.signal_winner.emit(hand_string+f'{self.PlayerStates[1].name} wins the pot of {self.pot}!')

        else:
            self.signal_winner.emit(hand_string+f'The pot of {self.pot} is split between the players.')
            self.PlayerStates[0].won(self.pot/2)
            self.PlayerStates[1].won(self.pot/2)

        self.data_changed.emit()

        if self.PlayerStates[0].money == 0:
            self.signal_endgame.emit(f"The Winner of The game is {self.PlayerStates[1].name}")

        elif self.PlayerStates[1].money == 0:
            self.signal_endgame.emit(f"The Winner of The game is {self.PlayerStates[0].name}")

        else:
            self.next_round()

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
        Resets the pot and player bets. Sets the new starting player as active. Makes sure that the new starting has
        cards face up.
        """
        self.signal_endround.emit()
        self.pot = 0
        self.deck = StandardDeck()
        self.deck.shuffle()
        self.tablestate.tablecards.clear_all_cards()
        self.tablestate.data_changed.emit()
        for player in self.PlayerStates:
            player.reset_bet()
            player.hand.clear_all_cards()
            player.hand.add_card(self.deck.draw())
            player.hand.add_card(self.deck.draw())
            player.data_changed.emit()

        # Check who started the last time.
        for player in self.PlayerStates:
            if player.started:
                player.set_starter(False)
                player.set_active(False)
                player.hand.flipped_cards = True

            else:
                player.set_starter(True)
                player.set_active(True)
                player.hand.flipped_cards = False
        self.PlayerStates[0].data_changed.emit()
        self.PlayerStates[1].data_changed.emit()
        self.data_changed.emit()
