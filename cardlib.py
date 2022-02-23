# DAT-171: Computer assignment 3
# Authors: Daniel Soderqvist and Felix Mare


from enum import Enum
from abc import ABC, abstractmethod
import random
from collections import Counter


class Suit(Enum):
    """An Enum-class representing the suits of playing cards.
    """

    Hearts = 1
    Spades = 2
    Clubs = 3
    Diamonds = 4


class PlayingCard(ABC):
    """An abstract base class representing all playing cards.
    """
    def __init__(self, suit):
        self.suit = suit

    @abstractmethod
    def get_value(self):
        """A method returning the value of the card.

        :return: An integer between 2 and 14
        :rtype: int
        """
        pass

    def __eq__(self, other):
        return self.get_value() == other.get_value() and self.suit == other.suit

    def __lt__(self, other):
        if self.get_value() == other.get_value():
            return self.suit.value > other.suit.value

        return self.get_value() < other.get_value()

    def __repr__(self):
        if type(self) == JackCard:
            return f'Jack of {self.suit.name}'
        elif type(self) == QueenCard:
            return f'Queen of {self.suit.name}'
        elif type(self) == KingCard:
            return f'King of {self.suit.name}'
        elif type(self) == AceCard:
            return f'Ace of {self.suit.name}'
        else:
            return f'{self.get_value()} of {self.suit.name}'


class NumberedCard(PlayingCard):
    """A subclass of PlayingCard representing a numbered card.

        :param value: The desired number or value of the card.
        :type value: int
        :param suit: The desired suit of the card.
        :type suit: Suit
        """
    def __init__(self, value, suit):
        super().__init__(suit)
        self.value = value

    def get_value(self):
        return self.value


class JackCard(PlayingCard):
    """A subclass of PlayingCard representing a jack card.

        :param suit: The desired suit of the card.
        :type suit: Suit
            """
    def __init__(self, suit):
        super().__init__(suit)

    def get_value(self):
        return 11


class QueenCard(PlayingCard):
    """A subclass of PlayingCard representing a queen card.

        :param suit: The desired suit of the card.
        :type suit: Suit
            """
    def __init__(self, suit):
        super().__init__(suit)

    def get_value(self):
        return 12


class KingCard(PlayingCard):
    """A subclass of PlayingCard representing a king card.

        :param suit: The desired suit of the card.
        :type suit: Suit
            """
    def __init__(self, suit):
        super().__init__(suit)

    def get_value(self):
        return 13


class AceCard(PlayingCard):
    """A subclass of PlayingCard representing an ace card.

        :param suit: The desired suit of the card.
        :type suit: Suit
            """
    def __init__(self, suit):
        super().__init__(suit)

    def get_value(self):
        return 14


class StandardDeck:
    """A class representing a standard 52-card deck. Generates a full deck when creating an instance.

        :param cards: A list with cards that make up the deck.
        :type cards: list
            """
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
        """A method that randomizes the order of cards in the deck.
        """
        random.shuffle(self.cards)

    def draw(self):
        """A method that draws (removes) and returns the top card from the deck.

            :returns: The top card in the deck.
            :rtype: PlayingCard
                """
        return list.pop(self.cards)

    def __repr__(self):
        return f'Standard deck with cards: {self.cards}'


class Hand:
    """A class representing a players cards on their hand.

        :param cards: A list with cards that make up the hand.
        :type cards: list
            """
    def __init__(self, cards=None):

        if cards is None:
            cards = []
        self.cards = cards

    def add_card(self, card):
        """A method that adds a card to the hand.

            :param card: A playingcard in the hand.
            :type card: PlayingCard
                """
        self.cards.append(card)

    def drop_cards(self, indices):
        """A method that removes a specific card from the hand.

            :param indices: Indices of which card to drop.
            :type indices: list of int
                """
        kept_cards = [self.cards[i] for i in range(len(self.cards)) if i not in indices]
        self.cards = kept_cards

    def sort(self):
        """A method that sort the cards in order depending on their value.
        """
        self.cards.sort()

    def best_poker_hand(self, cards):
        """A method finding out which card combination is the best.

            :param cards: Additionally cards that combines the player's hand.
            :type cards: list
            :return: The player's best poker hand including hierarchy and secondary dependent variables.
            :rtype: PokerHand
                """
        check_funcs = [PokerHand.check_straight_flush,
                       PokerHand.check_four_of_a_kind,
                       PokerHand.check_full_house,
                       PokerHand.check_flush,
                       PokerHand.check_straight,
                       PokerHand.check_three_of_a_kind,
                       PokerHand.check_two_pairs,
                       PokerHand.check_pair,
                       PokerHand.high_cards]

        all_cards = list(self.cards)
        if cards is not None:
            all_cards += cards
            all_cards.sort()

        for fn in check_funcs:

            check = fn(all_cards)

            if check is not None:
                hierarchy, secondary = fn(all_cards)

                return PokerHand(hierarchy, secondary, all_cards)

    def __repr__(self):

        return f'hand with cards: {self.cards}'


class PokerHierarchy(Enum):
    """An Enum-class representing all poker hands and their hierarchy.
    """

    Straight_Flush = 9
    Four_of_a_Kind = 8
    Full_House = 7
    Flush = 6
    Straight = 5
    Three_of_a_Kind = 4
    Two_Pairs = 3
    Pair = 2
    High_cards = 1


class PokerHand:
    """
    A class representing a poker hand that contains all attributes required to distinguish one poker hand from another.

    :param type: The type of PokerHand
    :type type: PokerHierarchy
    :param secondary: A tuple containing the relevant values to compare two hands of the same type.
    :type secondary: Tuple
    :param cards: All the cards in the poker hand.
    :type cards: list of PlayingCard
    """
    def __init__(self, type, secondary, cards):

        self.type = type
        self.name = type.name
        self.hierarchy = type.value
        self.secondary = secondary
        self.cards = cards

    @staticmethod
    def check_straight_flush(cards):
        """A static method that checks if a set of cards contains a straight flush. If this is the case, return
        the PokerHierarchy object, the highest card and suit of the straight. If this is not the case, return none.

            :param cards: The list of cards to evaluate.
            :type cards: list of PlayingCard
            :return: If straight flush is found: PokerHierarchy object, suit and highest card in straight. Else: None
            :rtype: tuple
                """
        vals = [(c.get_value(), c.suit) for c in cards] \
               + [(1, c.suit) for c in cards if c.get_value() == 14]  # Add the aces!

        for c in reversed(cards):  # Starting point (high card)
            # Check if we have the value - k in the set of cards:
            found_straight = True
            for k in range(1, 5):
                if (c.get_value() - k, c.suit) not in vals:
                    found_straight = False
                    break
            if found_straight:
                return PokerHierarchy.Straight_Flush, (c.get_value(), c.suit.name)

    @staticmethod
    def check_four_of_a_kind(cards):
        """A static method that checks if a set of cards contains four of a kind. If this is the case, return
        the PokerHierarchy object and the kind of fours. If this is not the case, return none.

            :param cards: The list of cards to evaluate.
            :type cards: list of PlayingCard
            :return: If four of a kind is found: PokerHierarchy object and the kind of fours. Else: None
            :rtype: tuple
                """
        value_count = Counter()
        for c in cards:
            value_count[c.get_value()] += 1

        fours = [v[0] for v in value_count.items() if v[1] >= 4]

        if fours:
            return PokerHierarchy.Four_of_a_Kind, fours

    @staticmethod
    def check_full_house(cards):
        """A static method that checks if a set of cards contains a full house. If this is the case, return
        the PokerHierarchy object, the kind of threes and twos. If this is not the case, return none.

            :param cards: The list of cards to evaluate.
            :type cards: list of PlayingCard
            :return: If full house is found: PokerHierarchy object and the kind of threes and twos. Else: None
            :rtype: tuple
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
                    return PokerHierarchy.Full_House, (three, two)

    @staticmethod
    def check_flush(cards):
        """A static method that checks if a set of cards contains a flush. If this is the case, return
        the PokerHierarchy object, the values of the cards in the flush and the suit. If this is not the case,
        return none.

            :param cards: The list of cards to evaluate.
            :type cards: list of PlayingCard
            :return: If flush is found: PokerHierarchy object, the values of the cards in the flush and suit. Else: None
            :rtype: tuple
                """
        suit_dict = {}

        for c in reversed(cards):
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
            return PokerHierarchy.Flush, (suit_dict[flush], c.suit.name)

    @staticmethod
    def check_straight(cards):
        """A static method that checks if a set of cards contains a straight. If this is the case, return
        the PokerHierarchy object and the value of the highest card in the straight. If this is not the case,
        return none.

            :param cards: The list of cards to evaluate.
            :type cards: list of PlayingCard
            :return: If straight is found: PokerHierarchy object, the highest card of the straight. Else: None
            :rtype: tuple
                """
        vals = [(c.get_value()) for c in cards] \
               + [(1, c.suit) for c in cards if c.get_value() == 14]  # Add the aces!

        for c in reversed(cards):  # Starting point (high card)
            # Check if we have the value - k in the set of cards:
            found_straight = True
            for k in range(1, 5):
                if (c.get_value() - k) not in vals:
                    found_straight = False
                    break
            if found_straight:
                return PokerHierarchy.Straight, c.get_value()

    @staticmethod
    def check_three_of_a_kind(cards):
        """A static method that checks if a set of cards contains three of a kind. If this is the case, return
        the PokerHierarchy object and the kind of threes. If this is not the case, return none.

            :param cards: The list of cards to evaluate.
            :type cards: list of PlayingCard
            :return: If three of a kind is found: PokerHierarchy object, kind of threes. Else: None
            :rtype: tuple
                """
        value_count = Counter()
        for c in cards:
            value_count[c.get_value()] += 1

        threes = [v[0] for v in value_count.items() if v[1] >= 3]

        if threes:
            return PokerHierarchy.Three_of_a_Kind, threes[-1]

    @staticmethod
    def check_two_pairs(cards):
        """A static method that checks if a set of cards contains two pairs. If this is the case, return
        the PokerHierarchy object and the kind of two pairs. If this is not the case, return none.

            :param cards: The list of cards to evaluate.
            :type cards: list of PlayingCard
            :return: If two pairs are found: PokerHierarchy object, kind of two pairs and remaining highest card. Else: None
            :rtype: tuple
                """

        value_count = Counter()
        for c in cards:
            value_count[c.get_value()] += 1
        # Find the card ranks that have at least two of a kind
        two_pairs = [v[0] for v in value_count.items() if v[1] >= 2]
        two_pairs.sort()
        highest_card = None
        if len(two_pairs) >= 2:
            for i in reversed(cards):
                if i.get_value() != two_pairs[-1] or i.get_value() != two_pairs[-2]:
                    highest_card = i.get_value()
                    break

            return PokerHierarchy.Two_Pairs, (two_pairs[-1], two_pairs[-2], highest_card)

    @staticmethod
    def check_pair(cards):
        """A static method that checks if a set of cards contains a pair. If this is the case, return
        the PokerHierarchy object and the kind of pair. If this is not the case, return none.

            :param cards: The list of cards to evaluate.
            :type cards: list of PlayingCard
            :return: If pair is found: PokerHierarchy object, kind of pair and remaining highest cards. Else: None
            :rtype: tuple
                """
        value_count = Counter()
        for c in cards:
            value_count[c.get_value()] += 1

        pair = [v[0] for v in value_count.items() if v[1] >= 2]
        highest_cards = []
        value_count_2 = 0
        if pair:
            for i in reversed(cards):
                if i.get_value() != pair[-1] and value_count_2 < 3:
                    highest_cards.append(i.get_value())
                    value_count_2 += 1

            return PokerHierarchy.Pair, (pair[-1], highest_cards)

    @staticmethod
    def high_cards(cards):
        """A static method that checks the five greatest cards and returns
        the PokerHierarchy object and the value of the five cards.

            :param cards: The list of cards to evaluate.
            :type cards: list of PlayingCard
            :return: PokerHierarchy object and the five greatest cards.
            :rtype: tuple
                """
        highest_cards = []
        counter = 0
        for c in reversed(cards):
            if counter < 5:
                highest_cards.append(c.get_value())
                counter += 1

        return PokerHierarchy.High_cards, highest_cards

    def __repr__(self):

        if self.hierarchy == PokerHierarchy.Straight_Flush.value:
            return f'{self.name.replace("_"," ")} of {self.secondary[-1]} with highest card {self.secondary[0]}'

        elif self.hierarchy == PokerHierarchy.Four_of_a_Kind.value:
            return f'{self.name} with {self.secondary}'

        elif self.hierarchy == PokerHierarchy.Full_House.value:
            return f'{self.name.replace("_", " ")} with threes in {self.secondary[0]} and pair in {self.secondary[1]}'

        elif self.hierarchy == PokerHierarchy.Flush.value:
            return f'{self.name.replace("_", " ")} of {self.secondary[-1]} with highest cards {self.secondary[0]}'

        elif self.hierarchy == PokerHierarchy.Straight.value:
            return f'{self.name.replace("_", " ")} with highest card {self.secondary}'

        elif self.hierarchy == PokerHierarchy.Three_of_a_Kind.value:
            return f'{self.name.replace("_", " ")} of {self.secondary}'

        elif self.hierarchy == PokerHierarchy.Two_Pairs.value:
            return f'{self.name.replace("_", " ")} of {self.secondary[0]} and {self.secondary[1]} with highest card {self.secondary[2]}'

        elif self.hierarchy == PokerHierarchy.Pair.value:
            return f'{self.name.replace("_", " ")} of {self.secondary[0]} with highest cards {self.secondary[1]}'

        else:
            return f'{self.name.replace("_", " ")} of {self.secondary}'

    def __eq__(self, other):
        return self.hierarchy == other.hierarchy and self.secondary == other.secondary

    def __lt__(self, other):

        if self.hierarchy == other.hierarchy:
            return self.secondary < other.secondary
        else:
            return self.hierarchy < other.hierarchy


# The following code is a testrun of the library. The result is printed in the terminal.

hA = Hand()
hB = Hand()

d = StandardDeck()
d.shuffle()

hA.add_card(d.draw())
hA.add_card(d.draw())

hB.add_card(d.draw())
hB.add_card(d.draw())

cards = [d.draw(), d.draw(), d.draw(), d.draw(), d.draw()]

A = hA.best_poker_hand(cards)
B = hB.best_poker_hand(cards)

print(f'Player A has a {hA}')
print(f'Player B has a {hB}')
print(f'Cards on the table: {cards}\n')

print(f'Player A has {A}')
print(f'Player B has {B}\n')

if A > B:
    print('Winner is player A')
elif B > A:
    print('Winner is player B')
else:
    print('Split pot')


