from enum import Enum
import pytest
from cardlib import *


# This test assumes you call your suit class "Suit" and the suits "Hearts and "Spades"
def test_cards():
    h5 = NumberedCard(4, Suit.Hearts)
    assert isinstance(h5.suit, Enum)

    sk = KingCard(Suit.Spades)
    assert sk.get_value() == 13

    assert h5 < sk
    assert h5 == h5

    with pytest.raises(TypeError):
        pc = PlayingCard(Suit.Clubs)

    ha = AceCard(Suit.Hearts)
    assert ha.get_value() == 14

    sa = AceCard(Suit.Spades)
    assert not ha == sa

    cj = JackCard(Suit.Clubs)
    assert cj.get_value() == 11

    cq = QueenCard(Suit.Clubs)
    assert cq.get_value() == 12
    assert cj < cq
    assert cj.suit == cq.suit

    assert repr(cq) == 'Queen of Clubs'


# This test assumes you call your shuffle method "shuffle" and the method to draw a card "draw"
def test_deck():
    d = StandardDeck()
    assert len(d.cards) == 52
    c1 = d.draw()
    c2 = d.draw()
    assert len(d.cards) == 50
    assert not c1 == c2
    assert repr(c1) == 'Ace of Diamonds'

    d2 = StandardDeck()
    d2.shuffle()
    c3 = d2.draw()
    c4 = d2.draw()
    assert not ((c3, c4) == (c1, c2))

    d3 = StandardDeck()
    d3.shuffle()
    c5 = d3.draw()
    assert c5 not in d3.cards


# This test builds on the assumptions above and assumes you store the cards in the hand in the list "cards",
# and that your sorting method is called "sort" and sorts in increasing order
def test_hand():
    h = Hand()
    assert len(h.cards) == 0
    d = StandardDeck()
    d.shuffle()
    h.add_card(d.draw())
    h.add_card(d.draw())
    h.add_card(d.draw())
    h.add_card(d.draw())
    h.add_card(d.draw())
    assert len(h.cards) == 5

    h.sort()
    for i in range(4):
        assert h.cards[i] < h.cards[i + 1] or h.cards[i] == h.cards[i + 1]

    cards = h.cards.copy()
    h.drop_cards([3, 0, 1])
    assert len(h.cards) == 2
    assert h.cards[0] == cards[2]
    assert h.cards[1] == cards[4]
    q = Hand()
    q.add_card(NumberedCard(4, Suit.Hearts))
    q.add_card(JackCard(Suit.Hearts))
    assert repr(q) == 'hand with cards: [4 of Hearts, Jack of Hearts]'


# This test builds on the assumptions above. Add your type and data for the commented out tests
# and uncomment them!
def test_pokerhands():

    h1 = Hand()
    h1.add_card(QueenCard(Suit.Diamonds))
    h1.add_card(KingCard(Suit.Hearts))

    h2 = Hand()
    h2.add_card(QueenCard(Suit.Hearts))
    h2.add_card(AceCard(Suit.Hearts))

    cl = [NumberedCard(10, Suit.Diamonds), NumberedCard(9, Suit.Diamonds),
          NumberedCard(8, Suit.Clubs), NumberedCard(6, Suit.Spades)]

    ph1 = h1.best_poker_hand(cl)
    assert isinstance(ph1, PokerHand)
    ph2 = h2.best_poker_hand(cl)
    assert ph1.name == 'High_cards' and max(ph1.secondary) == 13
    assert ph2.name == 'High_cards' and max(ph2.secondary) == 14

    assert ph1 < ph2

    cl.pop(0)
    cl.append(QueenCard(Suit.Spades))
    ph3 = h1.best_poker_hand(cl)
    ph4 = h2.best_poker_hand(cl)
    assert ph3 < ph4
    assert ph1 < ph2

    assert repr(ph3) == 'Pair of 12 with highest cards [13, 9, 8]'
    assert repr(ph4) == 'Pair of 12 with highest cards [14, 9, 8]'

    cl = [QueenCard(Suit.Clubs), QueenCard(Suit.Spades), KingCard(Suit.Clubs), KingCard(Suit.Spades)]
    ph5 = h1.best_poker_hand(cl)
    assert repr(ph5) == 'Full House with threes in 13 and pair in 12'

    h3 = Hand()
    h3.add_card(KingCard(Suit.Diamonds))
    h3.add_card(KingCard(Suit.Hearts))
    bph3 = h3.best_poker_hand(None)

    h4 = Hand()
    h4.add_card(KingCard(Suit.Clubs))
    h4.add_card(KingCard(Suit.Spades))
    bph4 = h4.best_poker_hand(None)

    assert bph4 == bph3
    assert repr(bph3) == 'Pair of 13 with highest cards []'