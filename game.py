import tkinter as tk


class Theme:

    def __init__(self, boardColor, squareColor, playerColor, opponentColor, selectedPieceColor):
        self.boardColor = boardColor
        self.squareColor = squareColor
        self.playerColor = playerColor
        self.opponentColor = opponentColor
        self.selectedPieceColor = selectedPieceColor

    def __str__(self):
        return 'playerColor: ' + self.playerColor + '\n opponentColor : ' + self.opponentColor


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
