from enum import Enum
from abc import ABC, abstractmethod
import random
from collections import Counter # Counter is convenient for counting objects (a specialized dictionary)


def check_straight_flush(cards):
    """
    Checks for the best straight flush in a list of cards (may be more than just 5)

    :param cards: A list of playing cards.
    :return: None if no straight flush is found, else the value of the top card.
    """
    vals = [(c.get_value(), c.suit) for c in cards] \
        + [(1, c.suit) for c in cards if c.get_value() == 14]  # Add the aces!

    for c in reversed(cards): # Starting point (high card)
        # Check if we have the value - k in the set of cards:
        found_straight = True
        for k in range(1, 5):
            if (c.get_value() - k, c.suit) not in vals:
                found_straight = False
                break
        if found_straight:

            return c.get_value()


def check_four_of_a_kind(cards):

    value_count = Counter()
    for c in cards:
        value_count[c.get_value()] += 1

    fours = [v[0] for v in value_count.items() if v[1] >= 4]

    if fours:

        return fours


def check_full_house(cards):
    """
    Checks for the best full house in a list of cards (may be more than just 5)

    :param cards: A list of playing cards
    :return: None if no full house is found, else a tuple of the values of the triple and pair.
    """
    value_count = Counter()
    for c in cards:
        value_count[c.get_value()] += 1

    # Find the card ranks that have at least three of a kind
    threes = [v[0] for v in value_count.items() if v[1] >= 3]

    threes.sort()
    # Find the card ranks that have at least a pair
    twos = [v[0] for v in value_count.items() if v[1] >= 2]
    twos.sort()
    # Threes are dominant in full house, lets check that value first:
    for three in reversed(threes):
        for two in reversed(twos):
            if two != three:
                return three, two


def check_flush(cards):

    suit_dict = {}

    for c in cards:
        if c.suit.name in suit_dict:

            suit_dict[c.suit.name].append(c.get_value())

        else:

            suit_dict[c.suit.name] = [c.get_value()]

    value_count = Counter()
    for c in cards:
        value_count[c.suit.name] += 1

    flush = None
    for v in value_count.items():
        if v[1] >= 5:
            flush = v[0]
    if flush:

        return flush, suit_dict[flush]


def check_straight(cards):
    """
    Checks for the best straight flush in a list of cards (may be more than just 5)

    :param cards: A list of playing cards.
    :return: None if no straight flush is found, else the value of the top card.
    """
    vals = [(c.get_value()) for c in cards] \
        + [(1, c.suit) for c in cards if c.get_value() == 14]  # Add the aces!

    for c in reversed(cards): # Starting point (high card)
        # Check if we have the value - k in the set of cards:
        found_straight = True
        for k in range(1, 5):
            if (c.get_value() - k) not in vals:
                found_straight = False
                break
        if found_straight:

            return c.get_value()


def check_three_of_a_kind(cards):

    value_count = Counter()
    for c in cards:
        value_count[c.get_value()] += 1

    threes = [v[0] for v in value_count.items() if v[1] >= 3]

    if threes:

        return threes[-1]


def check_two_pairs(cards):
    """
    Checks for the best full house in a list of cards (may be more than just 5)

    :param cards: A list of playing cards
    :return: None if no full house is found, else a tuple of the values of the triple and pair.
    """
    value_count = Counter()
    for c in cards:
        value_count[c.get_value()] += 1
    # Find the card ranks that have at least two of a kind
    two_pairs = [v[0] for v in value_count.items() if v[1] >= 2]
    two_pairs.sort()
    for i in reversed(cards):
        if i.get_value() != two_pairs[-1] or i.get_value() != two_pairs[-2]:
            highest_card = i.get_value()
            break

    if len(two_pairs) >= 2:
        return ((two_pairs[-1],two_pairs[-2]), highest_card)


def check_pair(cards):

    value_count = Counter()
    for c in cards:
        value_count[c.get_value()] += 1

    pair = [v[0] for v in value_count.items() if v[1] >= 2]
    highest_cards = []
    value_count_2 = 0
    for i in reversed(cards):
        if i.get_value() != pair[-1] and value_count_2 < 3:
            highest_cards.append(i.get_value())
            value_count_2 += 1

    if len(pair) >= 1:
        return (pair[-1], highest_cards)


def high_cards(cards):
    highest_cards = []
    counter = 0
    for c in reversed(cards):
        if counter < 5:
            highest_cards.append(c.get_value())
            counter += 1
    return highest_cards


class Suit(Enum):
    Hearts = 1
    Spades = 2
    Clubs = 3
    Diamonds = 4


class PlayingCard(ABC):
    suit: Suit
    def __init__(self, suit):
        self.suit = suit

    @abstractmethod
    def get_value(self):
        pass

    def __eq__(self, other):
        return self.get_value() == other.get_value() and self.suit == other.suit

    def __lt__(self, other):
        if self.get_value() == other.get_value():
            return self.suit.value > other.suit.value

        return self.get_value() < other.get_value()


class NumberedCard(PlayingCard):

    def __init__(self, value, suit):
        super().__init__(suit)
        self.value = value

    def get_value(self):
        return self.value


class JackCard(PlayingCard):

    def __init__(self, suit):
        super().__init__(suit)

    def get_value(self):
        return 11


class QueenCard(PlayingCard):

    def __init__(self, suit):
        super().__init__(suit)

    def get_value(self):
        return 12


class KingCard(PlayingCard):

    def __init__(self, suit):
        super().__init__(suit)

    def get_value(self):
        return 13


class AceCard(PlayingCard):

    def __init__(self, suit):
        super().__init__(suit)

    def get_value(self):
        return 14


class StandardDeck():

    def __init__(self, cards=None):
        if cards is None:
            cards = []
        self.cards = cards

        for value in range(2,11):
            for suit in Suit:
                cards.append(NumberedCard(value, suit))
        for suit in Suit:
            cards.append(JackCard(suit))
            cards.append(QueenCard(suit))
            cards.append(KingCard(suit))
            cards.append(AceCard(suit))

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self):
        return list.pop(self.cards)


class Hand:

    def __init__(self, cards=None):

        if cards is None:
            cards = []
        self.cards = cards

    def add_card(self, card):
        self.cards.append(card)

    def drop_cards(self, indices):
        kept_cards = [self.cards[i] for i in range(len(self.cards)) if i not in indices]
        self.cards = kept_cards

    def sort(self):
        self.cards.sort()

    def best_poker_hand(self, cards=[]):
        pass


class PokerHand(Enum):
    Straight_Flush = 11
    Four_of_a_Kind = 10
    Full_House = 9
    Flush = 8
    Straight = 7
    Three_of_a_Kind = 6
    Two_Pair = 5
    Pair = 4
    High_Card = 3


h=Hand()
d = StandardDeck()
d.shuffle()
h.add_card(d.draw())
h.add_card(d.draw())
h.add_card(d.draw())
h.add_card(d.draw())
h.add_card(d.draw())

cards = [NumberedCard(13,Suit.Spades), NumberedCard(13,Suit.Spades), NumberedCard(13,Suit.Spades), NumberedCard(9,Suit.Hearts), NumberedCard(13,Suit.Hearts), NumberedCard(10,Suit.Spades), NumberedCard(11, Suit.Spades)]


print(high_cards(cards))
