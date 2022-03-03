from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtSvg import *
from PyQt5.QtWidgets import *
from abc import abstractmethod
import sys
from cardlib import *

# NOTE: This is just given as an example of how to use CardView.
# It is expected that you will need to adjust things to make a game out of it. 

###################
# Models
###################


class CardModel(QObject):
    """ Base class that described what is expected from the CardView widget """

    new_cards = pyqtSignal()  #: Signal should be emited when cards change.

    @abstractmethod
    def __iter__(self):
        """Returns an iterator of card objects"""

    @abstractmethod
    def flipped(self):
        """Returns true of cards should be drawn face down"""


# A trivial card class (you should use the stuff you made in your library instead!
class MySimpleCard:
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit

    def get_value(self):
        return self.value

# You have made a class similar to this (hopefully):
class Hand:
    def __init__(self):
        # Lets use some hardcoded values for most of this to start with
        self.cards = [MySimpleCard(13, 2), MySimpleCard(7, 0)]

    def add_card(self, card):
        self.cards.append(card)

class Table:
    def __init__(self):
        # Lets use some hardcoded values for most of this to start with
        self.cards = [MySimpleCard(13, 2), MySimpleCard(7, 0), MySimpleCard(8, 0), MySimpleCard(10, 0), MySimpleCard(11, 0)]


# We can extend this class to create a model, which updates the view whenever it has changed.
# NOTE: You do NOT have to do it this way.
# You might find it easier to make a Player-model, or a whole GameState-model instead.
# This is just to make a small demo that you can use. You are free to modify
class HandModel(Hand, CardModel):
    def __init__(self):
        Hand.__init__(self)
        CardModel.__init__(self)
        # Additional state needed by the UI
        self.flipped_cards = False

    def __iter__(self):
        return iter(self.cards)

    def flip(self):
        # Flips over the cards (to hide them)
        self.flipped_cards = not self.flipped_cards
        self.new_cards.emit()  # something changed, better emit the signal!

    def flipped(self):
        # This model only flips all or no cards, so we don't care about the index.
        # Might be different for other games though!
        return self.flipped_cards

    def add_card(self, card):
        super().add_card(card)
        self.new_cards.emit()  # something changed, better emit the signal!

class HandModel_Table(Table, CardModel):
    def __init__(self):
        Table.__init__(self)
        CardModel.__init__(self)
        # Additional state needed by the UI
        self.flipped_cards = False

    def __iter__(self):
        return iter(self.cards)

###################
# Card widget code:
###################

class TableScene(QGraphicsScene):
    """ A scene with a table cloth background """
    def __init__(self):
        super().__init__()
        # self.tile = QPixmap('cards/table.png')
        # self.setBackgroundBrush(QBrush(self.tile))


class CardItem(QGraphicsSvgItem):
    """ A simple overloaded QGraphicsSvgItem that also stores the card position """
    def __init__(self, renderer, position):
        super().__init__()
        self.setSharedRenderer(renderer)
        self.position = position


def read_cards():
    """
    Reads all the 52 cards from files.
    :return: Dictionary of SVG renderers
    """
    all_cards = dict()  # Dictionaries let us have convenient mappings between cards and their images
    for suit_file, suit in zip('HDSC', range(4)):  # Check the order of the suits here!!!
        for value_file, value in zip(['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'], range(2, 15)):
            file = value_file + suit_file
            key = (value, suit)  # I'm choosing this tuple to be the key for this dictionary
            all_cards[key] = QSvgRenderer('cards/' + file + '.svg')
    return all_cards


class CardView(QGraphicsView):
    """ A View widget that represents the table area displaying a players cards. """

    # We read all the card graphics as static class variables
    back_card = QSvgRenderer('cards/Red_Back_2.svg')
    all_cards = read_cards()

    def __init__(self, card_model: CardModel, card_spacing: int = 250, padding: int = 10):
        """
        Initializes the view to display the content of the given model
        :param cards_model: A model that represents a set of cards. Needs to support the CardModel interface.
        :param card_spacing: Spacing between the visualized cards.
        :param padding: Padding of table area around the visualized cards.
        """
        self.scene = TableScene()
        super().__init__(self.scene)
        self.card_spacing = card_spacing
        self.padding = padding

        self.model = card_model
        # Whenever the this window should update, it should call the "change_cards" method.
        # This can, for example, be done by connecting it to a signal.
        # The view can listen to changes:
        card_model.new_cards.connect(self.change_cards)
        # It is completely optional if you want to do it this way, or have some overreaching Player/GameState
        # call the "change_cards" method instead. z

        # Add the cards the first time around to represent the initial state.
        self.change_cards()

    def change_cards(self):
        # Add the cards from scratch
        self.scene.clear()
        for i, card in enumerate(self.model):
            # The ID of the card in the dictionary of images is a tuple with (value, suit), both integers
            graphics_key = (card.get_value(), card.suit)
            renderer = self.back_card if self.model.flipped() else self.all_cards[graphics_key]
            c = CardItem(renderer, i)

            # Shadow effects are cool!
            shadow = QGraphicsDropShadowEffect(c)
            shadow.setBlurRadius(10.)
            shadow.setOffset(5, 5)
            shadow.setColor(QColor(0, 0, 0, 180))  # Semi-transparent black!
            c.setGraphicsEffect(shadow)

            # Place the cards on the default positions
            c.setPos(c.position * self.card_spacing, 0)
            # We could also do cool things like marking card by making them transparent if we wanted to!
            # c.setOpacity(0.5 if self.model.marked(i) else 1.0)
            self.scene.addItem(c)

        self.update_view()

    def update_view(self):
        scale = (self.viewport().height()-2*self.padding)/313
        self.resetTransform()
        self.scale(scale, scale)
        # Put the scene bounding box
        self.setSceneRect(-self.padding//scale, -self.padding//scale,
                          self.viewport().width()//scale, self.viewport().height()//scale)

    def resizeEvent(self, painter):
        # This method is called when the window is resized.
        # If the widget is resize, we gotta adjust the card sizes.
        # QGraphicsView automatically re-paints everything when we modify the scene.
        self.update_view()
        super().resizeEvent(painter)

    # This is the Controller part of the GUI, handling input events that modify the Model
    # def mousePressEvent(self, event):
    #    # We can check which item, if any, that we clicked on by fetching the scene items (neat!)
    #    pos = self.mapToScene(event.pos())
    #    item = self.scene.itemAt(pos, self.transform())
    #    if item is not None:
    #        # Report back that the user clicked on the card at given position:
    #        # The model can choose to do whatever it wants with this information.
    #        self.model.clicked_position(item.position)

    # You can remove these events if you don't need them.
    # def mouseDoubleClickEvent(self, event):
    #    self.model.flip() # Another possible event. Lets add it to the flip functionality for fun!





class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('Poopy Poker')
        self.setStyleSheet('background-image: url(cards/table.png);')

        #Lower left row
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.CardWidget())
        h_layout.addLayout(self.PlayerInterface())
        h_layout.addStretch(1)

        # Lower middle row
        h_lay = QVBoxLayout()
        h_lay.addLayout(self.PotInformation())
        h_lay.addStretch(1)
        h_lay.addLayout(self.PokerInteraction())
        h_layout.addLayout(h_lay)

        # Lower right row
        h_layout.addStretch(1)
        h_layout.addLayout(self.PlayerInterface())
        h_layout.addWidget(self.CardWidget())

        #Middle row
        h_layout2 = QHBoxLayout()
        h_layout2.addStretch(1)
        h_layout2.addWidget(self.TableWidget())
        h_layout2.addStretch(1)

        #Upper row
        h_layout3 = QHBoxLayout()
        h_layout3.addStretch(1)
        h_layout3.addLayout(self.GeneralInformation())
        h_layout3.addStretch(1)


        #Add all layouts vertically
        main_vertical = QVBoxLayout()
        main_vertical.addLayout(h_layout3)
        main_vertical.addLayout(h_layout2)
        main_vertical.addStretch(1)
        main_vertical.addLayout(h_layout)


        widget = QWidget()
        widget.setLayout(main_vertical)
        self.setCentralWidget(widget)


    def CardWidget(self):

        hand = HandModel()
        card_view = CardView(hand)
        box = QHBoxLayout()
        box.addWidget(card_view)
        player_view = QWidget()
        screen = app.primaryScreen()
        player_view.setFixedSize(int(screen.size().width()*0.246), int(screen.size().height()*0.3))
        player_view.setLayout(box)

        return player_view

    def TableWidget(self):

        hand = HandModel_Table()
        card_view = CardView(hand)
        box = QHBoxLayout()
        box.addWidget(card_view)

        player_view = QWidget()
        screen = app.primaryScreen()
        player_view.setFixedSize(int(screen.size().width()*0.6), int(screen.size().height()*0.3))
        player_view.setLayout(box)

        return player_view

    def PlayerInterface(self):

        player_layout = QVBoxLayout()
        player = QLineEdit('Player')
        player.setReadOnly(True)
        player.setAlignment(Qt.AlignCenter)
        player.setStyleSheet("padding: 3px 0px;")

        money = QLineEdit('Money: Input')
        money.setReadOnly(True)
        money.setAlignment(Qt.AlignCenter)
        money.setStyleSheet("padding: 3px 0px;")

        bet = QLineEdit('Bet: Input')
        bet.setReadOnly(True)
        bet.setAlignment(Qt.AlignCenter)
        bet.setStyleSheet("padding: 3px 0px;")

        player_layout.setSpacing(0)
        widgets = [player, money, bet, QPushButton('Flip cards')]
        for widget in widgets:
            player_layout.addWidget(widget)

        return player_layout


    def PokerInteraction(self):

        horizontal_layout = QHBoxLayout()
        sld = QLineEdit()
        sld.setValidator(QIntValidator())
        sld.setStyleSheet("padding: 2px 0px;")
        buttons = [QPushButton('Check/Call'),
                   QPushButton('Fold'),
                   QPushButton('Raise/Bet'),
                   sld]

        for button in buttons:
            horizontal_layout.addWidget(button)

        return horizontal_layout


    def PotInformation(self):

        vertical_layout = QVBoxLayout()
        #infos = [QLabel('pot'), QPushButton('100')]
        #
        # for info in infos:
        #     vertical_layout.addWidget(info)
        #
        pot_label = QLabel('Pot')
        pot_label.setAlignment(Qt.AlignCenter)
        amount_button = QLineEdit('100000')
        amount_button.setReadOnly(True)
        screen = app.primaryScreen()
        amount_button.setFixedWidth(int(screen.size().width() * 0.05))
        amount_button.setAlignment(Qt.AlignCenter)
        amount_button.setStyleSheet("padding: 3px 0px;")

        vertical_layout.addWidget(pot_label)
        vertical_layout.addWidget(amount_button)
        vertical_layout.setAlignment(Qt.AlignCenter)

        return vertical_layout

    def GeneralInformation(self):

        vertical_layout = QVBoxLayout()
        text = QLabel('Vad de ska stå')
        text.setFrameStyle(QFrame.Panel | QFrame.Raised)
        text.setAlignment(Qt.AlignCenter)
        screen = app.primaryScreen()
        text.setFixedSize(int(screen.size().width() * 0.246), int(screen.size().height() * 0.3))
        vertical_layout.addWidget(text)

        return vertical_layout


###################
# Main test program
###################

# Lets test it out

app = QApplication(sys.argv)

# hand = HandModel()
# hand2 = HandModel()
#
# card_view = CardView(hand)
# card_view2 = CardView(hand2)

# Creating a small demo window to work with, and put the card_view inside:


# box = QHBoxLayout()
# box.addWidget(card_view)
# box.addWidget(card_view2)
# player_view = QWidget()
# player_view.setLayout(box)
# player_view.show()

window = MainWindow()
window.showMaximized()



app.exec_()

