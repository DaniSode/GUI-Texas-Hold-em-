from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtSvg import *
from PyQt5.QtWidgets import *
from abc import abstractmethod
import sys
from pokermodel import *

# NOTE: This is just given as an example of how to use CardView.
# It is expected that you will need to adjust things to make a game out of it. 

###################
# Models
###################

app = QApplication(sys.argv)
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
        self.cards = [MySimpleCard(13, 2), MySimpleCard(7, 0), MySimpleCard(13, 1), MySimpleCard(13, 3), MySimpleCard(7, 3)]

    def add_card(self, card):
        self.cards.append(card)


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


###################
# Main test program
###################
class DisplayBox(QLineEdit):
    def __init__(self, label):
        super().__init__()
        self.label = label
        self.setText(f'{self.label}')
        self.setReadOnly(True)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("padding: 3px 0px;")
        screen = app.primaryScreen()
        self.setFixedWidth(int(screen.size().width() * 0.05))


class EditBox(QLineEdit):
    def __init__(self):
        super().__init__()
        #self.label = label
        #self.setText(f'{self.label}')
        self.setStyleSheet("padding: 3px 0px;")
        screen = app.primaryScreen()
        self.setFixedWidth(int(screen.size().width() * 0.05))


# Ändra inputs
class PlayerView(QHBoxLayout):
    def __init__(self, player_state):
        super().__init__()
        self.player_state = player_state

        hand = HandModel()
        card_view = CardView(hand)
        box = QHBoxLayout()
        box.addWidget(card_view)
        PlayerCard = QWidget()
        screen = app.primaryScreen()
        PlayerCard.setFixedSize(int(screen.size().width() * 0.246), int(screen.size().height() * 0.3))
        PlayerCard.setLayout(box)

        PlayerInformation = QVBoxLayout()
        PlayerInformation.setSpacing(0)
        flip_button = QPushButton('Flip cards')
        widgets = [DisplayBox(f'{self.player_state.name}'), DisplayBox(f'Money: {self.player_state.money}'), DisplayBox('Bet: Input'),
                   flip_button]
        for widget in widgets:
            PlayerInformation.addWidget(widget)
        flip_button.clicked.connect(lambda x, checked=True: hand.flip())

        self.addWidget(PlayerCard)
        self.addLayout(PlayerInformation)


#Måste definiera input pot
class PotInformation(QVBoxLayout):
    def __init__(self):
        super().__init__()
        pot_label = QLabel('Pot')
        pot_label.setAlignment(Qt.AlignCenter)
        amount_button = DisplayBox('1000')
        self.addWidget(pot_label)
        self.addWidget(amount_button)
        self.setAlignment(Qt.AlignCenter)


#Måste ändra input
class TableView(QWidget):
    def __init__(self):
        super().__init__()
        hand = HandModel()
        card_view = CardView(hand)
        box = QHBoxLayout()
        box.addWidget(card_view)
        screen = app.primaryScreen()
        self.setFixedSize(int(screen.size().width() * 0.6), int(screen.size().height() * 0.3))
        self.setLayout(box)


#Måste fixa bet input
class ActionsView(QHBoxLayout):
    def __init__(self):
        super().__init__()
        actions = DisplayBox('')
        actions.setReadOnly(False)
        buttons = [QPushButton('Check/Call'),
                   QPushButton('Fold'),
                   QPushButton('Raise/Bet'),
                   actions]
        for button in buttons:
            self.addWidget(button)


class InformationView(QVBoxLayout):
    def __init__(self, text):
        super().__init__()
        self.text = text
        text = QLabel(self.text)
        text.setFrameStyle(QFrame.Panel | QFrame.Raised)
        text.setAlignment(Qt.AlignCenter)
        screen = app.primaryScreen()
        text.setFixedSize(int(screen.size().width() * 0.1), int(screen.size().height() * 0.1))
        self.setAlignment(Qt.AlignCenter)
        self.addWidget(text)


class label_and_box(QVBoxLayout):

    def __init__(self, label):
        super().__init__()
        self.player_name = label
        lbl = QLabel(label)
        lbl.setAlignment(Qt.AlignCenter)
        self.enter_info = EditBox()
        self.addWidget(lbl)
        self.addWidget(self.enter_info)
        self.setAlignment(Qt.AlignCenter)


class SetupView(QVBoxLayout):
    def __init__(self):
        super().__init__()
        self.lblbox_1 = label_and_box('Name Player 1:')
        self.lblbox_2 = label_and_box('Name Player 2:')
        self.lblbox_3 = label_and_box('Stake:')

        self.addLayout(self.lblbox_1)
        self.addStretch(1)
        self.addLayout(self.lblbox_2)
        self.addStretch(1)
        self.addLayout(self.lblbox_3)
        self.addStretch(1)

    def get_text(self):
        return self.lblbox_1.enter_info.text(), self.lblbox_2.enter_info.text(), self.lblbox_3.enter_info.text()

class SetupWindow(QMainWindow):

    def __init__(self, GameModel):
        super().__init__()
        self.GameModel = GameModel
        self.setWindowTitle("Setup: Texas Hold'em")
        self.setStyleSheet('background-image: url(cards/table.png);')

        self.layout = SetupView()
        self.button = QPushButton("Confirm")
        self.button.setDefault(True)
        self.button.clicked.connect(self.proceed_to_main)
        self.layout.addWidget(self.button, alignment=Qt.AlignCenter)
        screen = app.primaryScreen()
        self.button.setFixedWidth(int(screen.size().width() * 0.05))

        test_widget = QWidget()
        test_widget.setLayout(self.layout)
        self.setCentralWidget(test_widget)

    def proceed_to_main(self):
        self.GameModel.start_game(self.layout.get_text())
        self.w = MainGameWindow(self.GameModel)
        self.w.show()
        self.close()

    # def set_player_info(self):
    #
    #     self.GameModel.start_game(self.layout.PlayerSetup_1.enter_info.text())
    #     self.button.clicked.connect(self.set_player_info())


class MainGameWindow(QMainWindow):
    def __init__(self, game):
        super().__init__()
        self.setWindowTitle("Texas Hold'em")
        self.setStyleSheet('background-image: url(cards/table.png);')
        self.move(100, 50)

        # Lower row
        h_layout = QHBoxLayout()

        # Lower left row
        h_layout.addLayout(PlayerView(game.PlayerStates[0]))
        h_layout.addStretch(1)

        # Lower middle row
        h_lay = QVBoxLayout()
        h_lay.addLayout(PotInformation())
        h_lay.addStretch(1)
        h_lay.addLayout(InformationView("Player 1's turn"))
        h_lay.addStretch(1)
        h_lay.addLayout(ActionsView())
        h_layout.addLayout(h_lay)

        # Lower right row
        h_layout.addStretch(1)
        h_layout.addLayout(PlayerView(game.PlayerStates[1]))

        # Middle row
        h_layout2 = QHBoxLayout()
        h_layout2.addStretch(1)
        h_layout2.addWidget(TableView())
        h_layout2.addStretch(1)

        # Upper row
        h_layout3 = QHBoxLayout()
        h_layout3.addStretch(1)
        h_layout3.addLayout(InformationView("Welcome to Texas Hold'em"))
        h_layout3.addStretch(1)

        # Add all layouts vertically
        main_vertical = QVBoxLayout()
        main_vertical.addLayout(h_layout3)
        main_vertical.addStretch(1)
        main_vertical.addLayout(h_layout2)
        main_vertical.addStretch(1)
        main_vertical.addLayout(h_layout)

        widget = QWidget()
        widget.setLayout(main_vertical)
        self.setCentralWidget(widget)