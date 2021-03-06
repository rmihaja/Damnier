from tkinter import *

############### MODELE ###############

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

# * variable init


boardSize = 8  # ? american chekers has 8 rows and 8 columns
board = createBoard(boardSize)

############### VIEW ###############

# * variable init
BOARD_LENGTH = 800
BOARD_COLOR = '#010101'
SQUARE_LENGTH = BOARD_LENGTH / boardSize
SQUARE_COLOR = '#000'
PIECE_RADIUS = (0.95 * SQUARE_LENGTH) / 2
PLAYER_COLOR = "#FD0002"
OPPONENT_COLOR = BOARD_COLOR

# * method init


def createPiece(canvas, canvasLength, squareValue, playerColor, opponentColor):
    pieceBorderWidth = 3
    pieceColor = ''
    pieceTopLeftCorner = 0.1 * canvasLength, 0.1 * canvasLength
    pieceBottomRightCorner = (0.9) * canvasLength, (0.9) * canvasLength
    if (squareValue == 'O'):
        pieceColor = opponentColor
    elif (squareValue == 'P'):
        pieceColor = playerColor
    canvas.create_oval(pieceTopLeftCorner, pieceBottomRightCorner,
                       fill=pieceColor, outline='white', width=pieceBorderWidth)


def showBoard(board, root, squareLength, pieceRadius, playerColor, opponentColor):
    print(squareLength)
    for row in range(len(board)):
        for column in range(len(board[0])):
            # set square color
            squareValue = board[row][column]
            if (squareValue != ''):
                square = Canvas(root, width=squareLength,
                                height=squareLength, bg=opponentColor, bd=-2)
                if (squareValue != 'E'):
                    createPiece(square, squareLength, squareValue,
                                playerColor, opponentColor)
                square.grid(row=row, column=column)


# Tkinter init
root = Tk()
root.title('Damnier')
root.geometry(str(BOARD_LENGTH) + 'x' + str(BOARD_LENGTH))

# render board
showBoard(board, root, SQUARE_LENGTH, PIECE_RADIUS,
          PLAYER_COLOR, OPPONENT_COLOR)

# run tkinter
root.mainloop()
