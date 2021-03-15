from game import EventHandler
import tkinter as tk

####################### USER INTERFACE OBJECT #######################


class Theme:

    def __init__(self, boardColor, squareColor, playerColor, opponentColor, selectedPieceColor):
        self.boardColor = boardColor
        self.squareColor = squareColor
        self.playerColor = playerColor
        self.opponentColor = opponentColor
        self.selectedPieceColor = selectedPieceColor

    def __str__(self):
        return 'playerColor: ' + self.playerColor + '\n opponentColor : ' + self.opponentColor


class InfoLabel(tk.Frame):

    def __init__(self, root):
        super().__init__(master=root)
        self.label = tk.Label(self)
        self.label.pack()

    # display given message to user
    def notify(self, message):
        self.label.configure(text=message)


####################### BOARD OBJECT #######################


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
