from tkinter import *
import socketio

############### SERVER CONNECTION ###############

#  setup client
socket = socketio.Client()
# connect to socket server
socket.connect('http://localhost:3000')

# * event handler


@socket.on('connect')
def onConnect():
    print('I\'m in!')


@socket.on('disconnect')
def onDisconnect():
    print('Bye')

############### MODELE ###############


# * functions init


def generateBoard(size):
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


def movePiece(piecePosition, emptyPosition):
    xpiece, ypiece = piecePosition
    xempty, yempty = emptyPosition

    # interchange case value
    board[xempty][yempty] = 'P'
    board[xpiece][ypiece] = 'E'

    renderBoard()


boardSize = 8  # ? american chekers has 8 rows and 8 columns
board = generateBoard(boardSize)

############### VIEW ###############

# * variable init
PLAYER_COLOR = '#FD0002'
OPPONENT_COLOR = '#010101'
BOARD_LENGTH = 800
BOARD_COLOR = PLAYER_COLOR
SQUARE_LENGTH = BOARD_LENGTH / boardSize
SQUARE_COLOR = OPPONENT_COLOR  # must have opposite color of board
PIECE_RADIUS = (0.95 * SQUARE_LENGTH) / 2
SELECTED_PIECE_COLOR = '#FFEB41'
# store previous piece event : (0) selectedCanvas, (1) selectedPiece, (2) Piece position
pieceEvent = [None, None, None]
canMove = True

# * method init


def renderBoard():
    createBoard(board, root, SQUARE_LENGTH, SQUARE_COLOR, PIECE_RADIUS,
                PLAYER_COLOR, OPPONENT_COLOR)


def createBoard(board, root, squareLength, squareColor, pieceRadius, playerColor, opponentColor):
    for row in range(len(board)):
        for column in range(len(board[0])):
            # set square color
            squareValue = board[row][column]
            if (squareValue != ''):
                square = Canvas(root, width=squareLength,
                                height=squareLength, bg=squareColor, bd=-2)  # ? bd removes Canvas default margin
                if (squareValue != 'E'):
                    createPiece(square, squareLength, squareValue,
                                playerColor, opponentColor)
                else:
                    square.bind("<Button-1>", selectEmptySquare)

                square.grid(row=row, column=column)


def createPiece(canvas, canvasLength, squareValue, playerColor, opponentColor):
    pieceBorderWidth = 3
    pieceColor = ''
    pieceTopLeftCorner = 0.1 * canvasLength, 0.1 * canvasLength
    pieceBottomRightCorner = (0.9) * canvasLength, (0.9) * canvasLength
    if (squareValue == 'O'):
        pieceColor = opponentColor
    elif (squareValue == 'P'):
        pieceColor = playerColor
        canvas.bind("<Button-1>", selectPiece)
    canvas.create_oval(pieceTopLeftCorner, pieceBottomRightCorner,
                       fill=pieceColor, outline='white', width=pieceBorderWidth)


def getGridPosition(selectedWidget):
    return (selectedWidget.grid_info()['row'],
            selectedWidget.grid_info()['column'])

# event listeners


def selectPiece(event):

    # reset last highlighted piece
    if (pieceEvent[0] != None):
        pieceEvent[0].itemconfigure(pieceEvent[1], fill=PLAYER_COLOR)
    # get piece event
    triggeredCanvas = event.widget
    selectedPiece = triggeredCanvas.find_closest(event.x, event.y)
    # store piece event to global variable
    pieceEvent[0] = triggeredCanvas
    pieceEvent[1] = selectedPiece
    pieceEvent[2] = getGridPosition(triggeredCanvas)
    # change piece color to highlight it
    triggeredCanvas.itemconfigure(selectedPiece, fill=SELECTED_PIECE_COLOR)


def selectEmptySquare(event):
    emptyPosition = getGridPosition(event.widget)
    if (pieceEvent[2] != None):
        # check if movement is valid (can only move forward)
        if (emptyPosition[0] - pieceEvent[2][0] == -1):
            movePiece(pieceEvent[2], emptyPosition)


# Tkinter init
root = Tk()
root.title('Damnier')
root.geometry(str(BOARD_LENGTH) + 'x' + str(BOARD_LENGTH))
root.configure(bg=BOARD_COLOR)

# render board
renderBoard()

# run tkinter
root.mainloop()
