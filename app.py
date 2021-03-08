import tkinter as tk
import socketio
import json
from collections import namedtuple

####################### TKINTER BOARD MANAGER #######################

class Board(tk.Frame):

    def __init__(self, root, layout, playerValue, theme):
        self.playerValue = playerValue
        self.length = 800
        self.theme = theme
        super().__init__(master=root, height=self.length,
                         width=self.length, bg=self.theme.boardColor)
        # board data from server
        self.layout = layout
        self.size = len(layout[0])
        self.squareSize = self.length / self.size

        # filling the board with canvases
        self.__create_widgets()

    def __create_widgets(self):
        for row in range(self.size):
            for column in range(self.size):
                squareValue = self.layout[row][column]
                if (squareValue != ''):
                    square = self.createSquare(squareValue)
                    square.grid(row=row, column=column)

    def createSquare(self, value):
        if (value == 'E'):
            return EmptySquare(self, self.squareSize,
                               self.theme.squareColor)
        elif (value == self.playerValue):
            return PlayerSquare(self, self.squareSize, self.theme.squareColor,
                                self.theme.playerColor, self.theme.selectedPieceColor)
        else:
            # square is automatically for the opponent
            return OpponentSquare(self, self.squareSize, self.theme.squareColor,
                                  self.theme.opponentColor)


class Square(tk.Canvas):

    def __init__(self, root, size, color):
        # ? bd removes Canvas default margin
        super().__init__(master=root, width=size, height=size, bg=color, bd=-2)

    @staticmethod
    def getPieceCorners(squareSize):
        topLeftPoint = 0.1 * squareSize, 0.1 * squareSize
        bottomLeftPoint = 0.9 * squareSize, 0.9 * squareSize
        return (topLeftPoint, bottomLeftPoint)


class EmptySquare(Square):

    def __init__(self, root, size, squareColor):
        super().__init__(root, size, squareColor)
        self.bind("<Button-1>", EventHandler.onEmptySquareSelected)


class OpponentSquare(Square):

    def __init__(self, root, size, squareColor, pieceColor):
        super().__init__(root, size, squareColor)
        self.piece = self.create_oval(Square.getPieceCorners(
            size), fill=pieceColor, outline='white', width=3)


class PlayerSquare(OpponentSquare):

    def __init__(self, root, size, squareColor, pieceColor, selectedPieceColor):
        super().__init__(root, size, squareColor, pieceColor)
        self.pieceColor = pieceColor
        self.selectedPieceColor = selectedPieceColor
        self.bind(
            "<Button-1>", EventHandler.onPlayerSquareSelected)


####################### TKINTER EVENT MANAGER #######################

class EventHandler:

    selectedSquare = None
    selectedPiece = None
    selectedEmpty = None

    @classmethod
    def onPlayerSquareSelected(cls, event):
        if (cls.selectedSquare != None):
            cls.selectedSquare.itemconfigure(
                cls.selectedSquare.piece, fill=cls.selectedSquare.pieceColor)
        cls.selectedSquare = event.widget
        cls.selectedSquare.itemconfigure(
            cls.selectedSquare.piece, fill=cls.selectedSquare.selectedPieceColor)

    @classmethod
    def onEmptySquareSelected(cls, event):
        print('touché')
        if(cls.selectedSquare != None):
            cls.selectedPiece = {
                'x': cls.selectedSquare.grid_info()['row'],
                'y': cls.selectedSquare.grid_info()['column']
            }
            cls.selectedEmpty = {
                'x': event.widget.grid_info()['row'],
                'y': event.widget.grid_info()['column']
            }



####################### SERVER CONNECTION MANAGER ######################################

# *  connection setup

socket = socketio.Client()
# connect to socket server
socket.connect('http://localhost:5511')

# * event handlers


@socket.on('connect')
def onConnect():
    print('You in!')


@socket.on('disconnect')
def onDisconnect():
    print('Oops, disconnected')


@socket.on('playersetup')
def onPlayerSetup(data):
    print('Congrats! You are player ' + str(json.loads(data)))
    global app
    app.setBoardProperty(json.loads(data))


@socket.on('loadboard')
def onloadboard(data):
    print('Found someone else to play. Loading game!')
    global app
    app.renderBoard(json.loads(data))


# client server data communication

@socket.on('message')
def onmessage(data):
    # convert JSON data into object with attributes corresponding to dict keys
    message = json.loads(data, object_hook=lambda d: namedtuple(
        'message', d.keys())(*d.values()))
    print(message)
    print(message.type)


############### APPLICATION MANAGER ###############

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
        self.geometry('800x800')

        # setup the grid layout manager
        self.rowconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def setBoardProperty(self, playerValue):
        self.playerValue = playerValue
        self.theme = self.setTheme(self.playerValue)

    def renderBoard(self, layout):
        self.board = Board(self, layout, self.playerValue, self.theme)
        self.board.grid(row=0, column=0)

    # TODO : add custom theme
    def setTheme(self, playerValue):
        if (playerValue == 1):
            # player is player1 => red
            return Theme('#FD0002', '#010101', '#FD0002', '#010101', '#FFEB41')
        else:
            # player is player2 => black
            return Theme('#FD0002', '#010101', '#010101', '#FD0002', '#FFEB41')


# * application init


if __name__ == "__main__":
    app = App()
    app.mainloop()

