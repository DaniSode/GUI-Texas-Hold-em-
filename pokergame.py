#
from pokermodel import *
from card_view_ny import *
import sys

game = GameModel()
window = SetupWindow(game)
window.show()
app.exec_()
