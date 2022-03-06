# DAT-171: Computer assignment 3
# Authors: Daniel Soderqvist and Felix Mare

from pokerview import *
import sys

def main():
    app = QApplication(sys.argv)
    game = GameModel()
    window = SetupWindow(game)
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()

