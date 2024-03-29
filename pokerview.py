# DAT-171: Computer assignment 3
# Authors: Daniel Soderqvist and Felix Mare

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtSvg import *
from PyQt5.QtWidgets import *
import sys
from pokermodel import *


app = QApplication(sys.argv)


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
    for suit_file, suit in zip('HSCD', range(1, 5)):  # Check the order of the suits here!!!
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
            graphics_key = (card.get_value(), card.suit.value)
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


class DisplayBox(QLineEdit):
    """
    A modified QLineEdit which is an uneditable text box.
    """
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
    """
    A modified QLineEdit which is an editable text box.
    """
    def __init__(self):
        super().__init__()
        self.setStyleSheet("padding: 3px 0px;")
        screen = app.primaryScreen()
        self.setFixedWidth(int(screen.size().width() * 0.05))


class PlayerView(QHBoxLayout):
    """
    A layout containing a view of a players cards and information such as money and bet.
    """
    def __init__(self, player_number, game):
        super().__init__()
        self.game = game
        self.player_number = player_number
        hand = self.game.PlayerStates[self.player_number].hand
        self.card_view = CardView(hand)
        box = QHBoxLayout()
        box.addWidget(self.card_view)
        player_card = QWidget()
        screen = app.primaryScreen()
        player_card.setFixedSize(int(screen.size().width() * 0.246), int(screen.size().height() * 0.3))
        player_card.setLayout(box)

        player_information = QVBoxLayout()
        player_information.setSpacing(0)

        self.player_name = DisplayBox(f'{self.game.PlayerStates[self.player_number].name}')
        self.player_name.setFont(QFont('Felix Titling'))
        self.player_name.setStyleSheet('padding: 3px 0px; font-weight: bold')
        self.money_box = DisplayBox(f'Money: {self.game.PlayerStates[self.player_number].money}')
        self.blind_box = DisplayBox(f'{self.game.PlayerStates[self.player_number].bet}-blind')
        self.bet_box = DisplayBox(f'Bet: {self.game.PlayerStates[self.player_number].bet}')
        self.flip_button = QPushButton('Flip cards')
        self.flip_button.clicked.connect(lambda x, checked=True: hand.flip())

        player_information.addWidget(self.player_name)
        player_information.addWidget(self.money_box)
        player_information.addWidget(self.bet_box)
        player_information.addWidget(self.flip_button)

        self.addWidget(player_card)
        self.addLayout(player_information)

        self.game.PlayerStates[self.player_number].data_changed.connect(self.update_views)

    def update_views(self):
        """
        A method updating all player information upon receiving the signal.
        """
        self.card_view.change_cards()
        self.money_box.setText(f'Money: {self.game.PlayerStates[self.player_number].money}')
        self.bet_box.setText(f'Bet: {self.game.PlayerStates[self.player_number].bet}')


class PotInformation(QVBoxLayout):
    """
    A layout showing the pot.
    """
    def __init__(self, game):
        super().__init__()
        self.game = game
        pot_label = QLabel('Pot')
        pot_label.setFont(QFont('Times New Roman', 12))
        pot_label.setAlignment(Qt.AlignCenter)
        self.amount_box = DisplayBox('')
        self.addWidget(pot_label)
        self.addWidget(self.amount_box)
        self.setAlignment(Qt.AlignCenter)

        self.game.data_changed.connect(self.update_views)

    def update_views(self):
        """
        A method updating pot information upon receiving the signal.
        """
        self.amount_box.setText(f'{self.game.pot}')


class TableView(QWidget):
    """
    A widget viewing the cards on the table.
    """
    def __init__(self, game):
        super().__init__()
        self.game = game
        hand = self.game.tablestate.tablecards
        self.card_view = CardView(hand)
        box = QHBoxLayout()
        box.addWidget(self.card_view)
        screen = app.primaryScreen()
        self.setFixedSize(int(screen.size().width() * 0.6), int(screen.size().height() * 0.3))
        self.setLayout(box)

        self.game.tablestate.data_changed.connect(self.update_views)

    def update_views(self):
        """
        A method updating the cards on the table upon receiving the signal.
        """
        self.card_view.change_cards()


class ActionsView(QHBoxLayout):
    """
    A layout containing the buttons for fold, call and bet etc.
    """
    def __init__(self, GameModel):
        super().__init__()
        self.GameModel = GameModel
        self.raise_amount = EditBox()
        self.raise_amount.setValidator(QIntValidator(0, 10000000000))
        self.check_call_button = QPushButton('Check/Call')
        self.check_call_button.clicked.connect(self.call_check)
        self.fold_button = QPushButton('Fold')
        self.fold_button.clicked.connect(self.fold)
        self.all_in_button = QPushButton('All In')
        self.all_in_button.clicked.connect(self.all_in)
        self.raise_bet_button = QPushButton('Raise/Bet')
        self.raise_bet_button.clicked.connect(self.make_bet)

        self.addWidget(self.check_call_button)
        self.addWidget(self.fold_button)
        self.addWidget(self.all_in_button)
        self.addWidget(self.raise_bet_button)
        self.addWidget(self.raise_amount)

    def get_raise_amount(self):
        """
        A method returning the text that was entered in the raise amount box.
        """
        if self.raise_amount.text() == '':
            self.raise_amount.setText('0')
        return self.raise_amount.text()

    def make_bet(self):
        """
        A method that runs the bet from gamemodel upon receiving the signal.
        """
        self.GameModel.bet(self.get_raise_amount())
        self.raise_amount.setText('')

    def all_in(self):
        """
        A method that runs the all in from gamemodel upon receiving the signal.
        """
        self.GameModel.all_in()

    def fold(self):
        """
        A method that runs the fold from gamemodel upon receiving the signal.
        """
        self.GameModel.fold()

    def call_check(self):
        """
        A method that runs the call from gamemodel upon receiving the signal.
        """
        self.GameModel.call()


class HeaderView(QVBoxLayout):
    """
    A layout that contains the main window header of the program.
    """
    def __init__(self):
        super().__init__()
        header = QLabel('Welcome to a beautiful game of Poker')
        header.setFrameStyle(QFrame.Panel | QFrame.Raised)
        header.setFont(QFont('Comic Sans MS', 40)) # Chiller - typsnitt
        header.setAlignment(Qt.AlignCenter)
        screen = app.primaryScreen()
        header.setFixedSize(int(screen.size().width() * 0.75), int(screen.size().height() * 0.1))
        self.setAlignment(Qt.AlignCenter)
        self.addWidget(header)


class InformationView(QVBoxLayout):
    """
    A layout that contains labels showing the state of the game.
    """
    def __init__(self, game):
        super().__init__()

        self.game = game

        self.player_turn = QLabel()
        self.player_turn.setAlignment(Qt.AlignCenter)
        self.player_turn.setFont(QFont('Constantia', 14))
        self.player_turn.setStyleSheet("color: #35322f")

        self.text = QLabel()
        self.text.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.text.setFont(QFont('Constantia', 10))
        self.text.setAlignment(Qt.AlignCenter)
        screen = app.primaryScreen()
        self.text.setFixedSize(int(screen.size().width() * 0.15), int(screen.size().height() * 0.1))
        self.text.setWordWrap(True)
        self.setAlignment(Qt.AlignCenter)
        self.addWidget(self.text)
        self.addWidget(self.player_turn)


        self.game.data_changed.connect(self.update_player)
        self.game.signal_bet.connect(self.update_view_bet)
        self.game.signal_call.connect(self.update_view_call)
        self.game.signal_fold.connect(self.update_view_fold)
        self.game.signal_all_in.connect(self.update_view_all_in)
        self.game.signal_winner.connect(self.update_winner)
        self.game.signal_endround.connect(self.update_end_of_round)
        self.game.signal_endgame.connect(self.end_game)

    def update_player(self):
        """
        A method that updates the view of the active player upon receiving the signal.
        """
        test = [player.name for player in self.game.PlayerStates if player.active]
        self.player_turn.setText(f"\n{test[0]}'s turn")

    def update_view_bet(self, text):
        """
        A method that updates the view with the bet information upon receiving the signal.
        """
        self.text.setText(text)

    def update_view_call(self, text):
        """
        A method that updates the view with the call information upon receiving the signal.
        """
        self.text.setText(text)

    def update_view_fold(self, text):
        """
        A method that updates the view with the fold information upon receiving the signal.
        """
        self.text.setText(text)

    def update_view_all_in(self, text):
        """
        A method that updates the view with the all in information upon receiving the signal.
        """
        self.text.setText(text)

    def update_winner(self, text):
        """
        A method that updates the view with the round winner information upon receiving the signal.
        """
        self.text.setText(text)

    def update_end_of_round(self):
        """
        A method that shows a message box upon the end of a round. Waits for the user to press ok to continue.
        """
        end_box = QMessageBox()
        end_box.setWindowTitle('Round finished')
        end_box.setText("Press ok to move on to the next round!")
        end_box.exec()
        self.text.setText('')

    def end_game(self, text):
        """
        A method that shows a message box upon the end of the game. Waits for the user to press ok to quit the application.
        """
        end_box = QMessageBox()
        end_box.setWindowTitle('Game finished')

        end_box.setText(text)
        end_box.exec()
        quit()


class LabelAndBox(QVBoxLayout):
    """
    A layout containing an editable box with an associated label.
    """
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
    """
    A layout containing all widgets shown in the setup window of the program. Takes input such as player names and stake.
    """
    def __init__(self):
        super().__init__()
        self.lbl_box_1 = LabelAndBox('Name Player 1:')
        self.lbl_box_2 = LabelAndBox('Name Player 2:')
        self.lbl_box_3 = LabelAndBox('Stake:')
        self.lbl_box_4 = LabelAndBox('Small-blind:')
        self.lbl_box_5 = LabelAndBox('Big-blind:')
        self.lbl_box_3.enter_info.setValidator(QIntValidator(0, 10000000000))
        self.lbl_box_4.enter_info.setValidator(QIntValidator(0, 10000000000))
        self.lbl_box_5.enter_info.setValidator(QIntValidator(0, 10000000000))
        self.addLayout(self.lbl_box_1)
        self.addStretch(1)
        self.addLayout(self.lbl_box_2)
        self.addStretch(1)
        self.addLayout(self.lbl_box_3)
        self.addStretch(1)

        # In case of implementing blinds
        # self.addLayout(self.lbl_box_4)
        # self.addStretch(1)
        # self.addLayout(self.lbl_box_5)
        # self.addStretch(1)

    def get_text(self):
        """
        A method that returns the information in the text boxes.
        """
        if self.lbl_box_1.enter_info.text() == '':
            self.lbl_box_1.enter_info.setText('Player 1')
        if self.lbl_box_2.enter_info.text() == '':
            self.lbl_box_2.enter_info.setText('Player 2')
        if self.lbl_box_3.enter_info.text() == '':
            self.lbl_box_3.enter_info.setText('100')

            # In case of implementing blinds
        # if self.lbl_box_4.enter_info.text() == '':
        #     self.lbl_box_4.enter_info.setText('10')
        # if self.lbl_box_5.enter_info.text() == '':
        #     self.lbl_box_5.enter_info.setText('20')

        return self.lbl_box_1.enter_info.text(), self.lbl_box_2.enter_info.text(), self.lbl_box_3.enter_info.text(), self.lbl_box_4.enter_info.text(), self.lbl_box_5.enter_info.text()


class SetupWindow(QMainWindow):
    """
    A window that contains the GUI of the game setup.
    """
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
        """
        A method that closes the window and proceeds to the main game.
        """
        self.GameModel.start_game(self.layout.get_text())
        self.w = MainGameWindow(self.GameModel)
        self.w.show()
        self.close()


class MainGameWindow(QMainWindow):
    """
    A window that contains the GUI of the main game.
    """
    def __init__(self, game):
        super().__init__()

        self.setWindowTitle("Texas Hold'em")
        self.setStyleSheet('background-image: url(cards/table.png);')
        self.move(100, 50)

        # Lower row
        h_layout = QHBoxLayout()

        # Lower left row
        h_layout.addLayout(PlayerView(0, game))
        h_layout.addStretch(1)

        # Lower middle row
        h_lay = QVBoxLayout()
        h_lay.addLayout(PotInformation(game))
        h_lay.addStretch(1)
        h_lay.addLayout(InformationView(game))
        h_lay.addStretch(1)
        h_lay.addLayout(ActionsView(game))
        h_layout.addLayout(h_lay)

        # Lower right row
        h_layout.addStretch(1)
        h_layout.addLayout(PlayerView(1, game))

        # Middle row
        h_layout2 = QHBoxLayout()
        h_layout2.addStretch(1)
        h_layout2.addWidget(TableView(game))
        h_layout2.addStretch(1)

        # Upper row
        h_layout3 = QHBoxLayout()
        h_layout3.addStretch(1)
        h_layout3.addLayout(HeaderView())
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

        game.data_changed.emit()