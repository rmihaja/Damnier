from tkinter import *

############### MODELE ###############

# * variable init

board = []
boardSize = 8  # ? american chekers has 8 rows and 8 columns


# * functions init

def createBoard(size):
    board = []
    # filling the board with oponent pieces
    for row in range(0, size):
        boardRow = []

        # check if boardRow belongs to players
        if (row < (size / 2) - 1):
            piece = 'O'  # ? O = opponent
        elif (row > (size / 2)):
            piece = 'P'  # ? P = player
        else:
            piece = 'E'  # ? E = empty : available square not occupied

        # filling the row
        for column in range(0, size):
            if ((row % 2 == 0 and column % 2 != 0) or (row % 2 != 0 and column % 2 == 0)):
                boardRow.append(piece)
            else:
                boardRow.append('')
        board.append(boardRow)

    return board


############### VIEW ###############

# * variable init
BOARD_LENGTH = 800
BOARD_COLOR = '#010101'
SQUARE_LENGTH = BOARD_LENGTH / boardSize
SQUARE_COLOR = '#000'
PIECE_RADIUS = (0.95 * SQUARE_LENGTH) / 2
PLAYER_COLOR = "#FD0002"
OPPONENT_COLOR = BOARD_COLOR

# Tkinter init
root = Tk()
root.title('Damnier')
root.geometry(str(BOARD_LENGTH) + 'x' + str(BOARD_LENGTH))

# render gui

# run tkinter
# root.mainloop()
