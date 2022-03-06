from pokermodel import *
from card_view_ny import *
import sys

def main():


    app = QApplication(sys.argv)
    game = GameModel()
    window = SetupWindow(game)
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()

