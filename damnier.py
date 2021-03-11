import tkinter as tk
import socketio
import json


####################### TKINTER BOARD MANAGER #######################


class Board(tk.Frame):

    def __init__(self, root, layout, playerValue, theme):

        # Board Frame value
        self.length = 800
        self.theme = theme
        super().__init__(master=root, height=self.length,
                         width=self.length, bg=self.theme.boardColor)

        # board data from server
        self.layout = layout
        self.size = len(layout[0])
        self.squareSize = self.length / self.size

        # player value : player1 or player2
        self.playerValue = playerValue

        # filling the board with canvases
        self.__create_widgets()

    def __create_widgets(self):
        for row in range(self.size):
            for column in range(self.size):
                squareValue = self.layout[row][column]
                if (squareValue != ''):
                    square = self.createSquare(squareValue, row, column)

                    # flip layout filling if the player is player2 for first pov
                    if (self.playerValue == '2'):
                        square.grid(row=self.size - row,
                                    column=self.size - column)
                    else:
                        square.grid(row=row, column=column)

    def createSquare(self, pieceValue, rowPosition, columnPosition):
        if ('E' in pieceValue):
            return EmptySquare(self, self.squareSize,
                               self.theme.squareColor, rowPosition, columnPosition)
        elif (self.playerValue in pieceValue):
            return PlayerSquare(self, self.squareSize, self.theme.squareColor, pieceValue,
                                self.theme.playerColor, self.theme.selectedPieceColor, rowPosition, columnPosition)
        else:
            # square is automatically for the opponent
            return OpponentSquare(self, self.squareSize, self.theme.squareColor, pieceValue,
                                  self.theme.opponentColor, rowPosition, columnPosition)


class Square(tk.Canvas):

    def __init__(self, root, size, color, row, column):
        # ? bd removes Canvas default margin
        super().__init__(master=root, width=size, height=size,
                         bg=color, bd=-2, highlightbackground=color)

        self.row = row
        self.column = column


class Piece():

    def __init__(self, squareParent, parentSize, value, color, selectedColor):
        self.shape = squareParent.create_oval(self.getPieceCorners(parentSize),
                                              fill=color, outline='white', width=3)

        # add queen overlay if piece is a queen
        if ('*' in value):
            squareParent.create_line(self.getCrownCorners(
                parentSize, (35, 65), (30, 40), (40, 45), 35), fill='white', width=3)

        # if selectedColor is set, piece belongs to player and is selectable
        if (selectedColor != None):
            self.color = color
            self.selectedColor = selectedColor
            # piece click event listener
            squareParent.tag_bind(self.shape, '<ButtonPress-1>',
                                  EventHandler.onPlayerSquareSelected)

    # getting canvas.create_oval points
    def getPieceCorners(self, squareSize):
        topLeftPoint = 0.1 * squareSize, 0.1 * squareSize
        bottomLeftPoint = 0.9 * squareSize, 0.9 * squareSize
        return (topLeftPoint, bottomLeftPoint)

    # getting queen crown shape
    def getCrownCorners(self, parentSize, bottomLeftPoint, outterLeftPoint, innerLeftPoint, ycenter):
        xA, yA = bottomLeftPoint
        xB, yB = outterLeftPoint
        xC, yC = innerLeftPoint

        A = xA, yA
        B = xB, yB
        C = xC, yC

        M = parentSize / 2, ycenter

        # mirroring left points for symetry
        # ? a queen crown is symetric on the y axis
        primeC = parentSize - C[0], C[1]
        primeB = parentSize - B[0], B[1]
        primeA = parentSize - A[0], A[1]

        return (A, B, C, M, primeC, primeB, primeA, A)


class EmptySquare(Square):

    def __init__(self, root, size, squareColor, row, column):
        super().__init__(root, size, squareColor, row, column)
        # empty square click event listener
        self.bind("<Button-1>", EventHandler.onEmptySquareSelected)


class OpponentSquare(Square):

    def __init__(self, root, size, squareColor, pieceValue, pieceColor, row, column):
        super().__init__(root, size, squareColor, row, column)
        self.piece = Piece(self, size, pieceValue, pieceColor, None)


class PlayerSquare(Square):

    def __init__(self, root, size, squareColor, pieceValue, pieceColor, selectedPieceColor, row, column):
        super().__init__(root, size, squareColor, row, column)
        self.piece = Piece(self, size, pieceValue,
                           pieceColor, selectedPieceColor)


class InfoLabel(tk.Frame):

    def __init__(self, root):
        super().__init__(master=root)
        self.label = tk.Label(self)
        self.label.pack()

    # display given message to user
    def notify(self, message):
        self.label.configure(text=message)

####################### TKINTER EVENT MANAGER #######################


class EventHandler:

    selectedSquare = None
    selectedPiece = None

    @classmethod
    def onPlayerSquareSelected(cls, event):
        # check if there is already a selected piece
        if (cls.selectedSquare != None and cls.selectedPiece != None):
            # reset previous selected piece
            cls.selectedSquare.itemconfigure(
                cls.selectedPiece, fill=cls.selectedSquare.piece.color)

        # storing canvas event info
        cls.selectedSquare = event.widget
        cls.selectedPiece = cls.selectedSquare.find_closest(event.x, event.y)

        # highliting selected piece with theme color
        cls.selectedSquare.itemconfigure(
            cls.selectedPiece, fill=cls.selectedSquare.piece.selectedColor)

    @classmethod
    def onEmptySquareSelected(cls, event):
        # send movement position value if a piece is selected and it is the player's turn
        if((cls.selectedSquare != None) and (app.isPlayerTurn)):
            selectedPiece = {
                'row': cls.selectedSquare.row,
                'column': cls.selectedSquare.column
            }
            selectedEmpty = {
                'row': event.widget.row,
                'column': event.widget.column
            }
            movementProperty = {
                'piecePosition': selectedPiece,
                'emptyPosition': selectedEmpty
            }

            # sending data to server if one of the farvest allowed movement (2 squares difference)
            # * specific, detailed move validation is operated by the server
            deltaRow = abs(selectedPiece['row'] - selectedEmpty['row'])
            deltaColumn = abs(
                selectedPiece['column'] - selectedEmpty['column'])
            if(deltaRow in range(1, 3) and deltaColumn in range(1, 3)):
                print('Sending movement to server')
                socket.emit('move', json.dumps(movementProperty))


####################### SERVER CONNECTION MANAGER ######################


socket = socketio.Client()

# * event handlers

#  connection events


# player is connected to socket server


@socket.on('connect')
def onConnect():
    print('You in!')

# player get connected to socket server


@socket.on('disconnect')
def onDisconnect():
    print('Oops, disconnected')

#  game events


@socket.on('playersetup')
def onPlayerSetup(data):
    print('Congrats! You are player ' + str(json.loads(data)))
    global app
    app.setBoardProperty(json.loads(data))
    app.infoLabel.notify('En attente d\'un joueur potentiel')


@socket.on('loadboard')
def onLoadboard(data):
    global app
    app.renderBoard(json.loads(data))


@socket.on('playerturn')
def onPlayerTurn(data):
    global app
    app.setPlayerTurn(json.loads(data))


@socket.on('captureopponent')
def onCaptureOpponent():
    print('Gotta capture another piece to end your turn!')
    app.infoLabel.notify('C\'est votre tour! Vous pouvez encore mangez!')


####################### APPLICATION MANAGER #######################

class Theme:

    def __init__(self, boardColor, squareColor, playerColor, opponentColor, selectedPieceColor):
        self.boardColor = boardColor
        self.squareColor = squareColor
        self.playerColor = playerColor
        self.opponentColor = opponentColor
        self.selectedPieceColor = selectedPieceColor

    def __str__(self):
        return 'playerColor: ' + self.playerColor + '\n opponentColor : ' + self.opponentColor


class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title('Damnier')
        self.geometry('800x820')
        self.resizable(0, 0)

        # setup the grid layout manager
        self.rowconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # setup turn management
        self.isPlayerTurn = False

        # display info label
        self.infoLabel = InfoLabel(self)
        self.infoLabel.grid(row=1, column=0)

    def setBoardProperty(self, playerValue):
        self.playerValue = playerValue
        self.theme = self.setTheme(self.playerValue)

    def renderBoard(self, layout):
        self.board = Board(self, layout, self.playerValue, self.theme)
        self.board.grid(row=0, column=0)

    # TODO : add custom theme
    def setTheme(self, playerValue):
        if (playerValue == '1'):
            # player is player1 => initial colors
            return Theme('#FFF', '#010101', '#FD0002', '#010101', '#FFEB41')
        else:
            # player is player2 => swap player colors
            return Theme('#FFF', '#010101', '#010101', '#FD0002', '#FFEB41')

    def setPlayerTurn(self, turn):
        self.isPlayerTurn = turn
        if (self.isPlayerTurn):
            self.infoLabel.notify('C\'est votre tour! ')
        else:
            self.infoLabel.notify('Tour de l\'adversaire. ')


# * application init
if __name__ == "__main__":

    # launching app
    app = App()

    # TODO: Add server class
    # connecting to socket server
    try:
        socket.connect('http://localhost:5500')
    except Exception:
        try:
            print('No local server found, connecting to remote')
            socket.connect('https://damnier.herokuapp.com/')
        except Exception as error:
            print('Can\'t connect to remote server:', error)
            app.infoLabel.notify(
                'Erreur: Impossible de se connecter au serveur. Veuillez redémarrer')

    # firing endless loop
    app.mainloop()
