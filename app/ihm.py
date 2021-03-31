import tkinter as tk

# *** IHM


####################### BOARD OBJECT #######################


class Square(tk.Canvas):

    def __init__(self, root, size, color, row, column):
        # ? bd removes Canvas default margin
        super().__init__(master=root, width=size, height=size,
                         bg=color, bd=-2, highlightbackground=color)

        self.row = row
        self.column = column


class Piece():

    def __init__(self, squareParent, parentSize, value, color, selectedColor, eventHandler):
        self.shape = squareParent.create_oval(self.getPieceCorners(parentSize),
                                              fill=color, outline='white', width=3)

        # add queen overlay if piece is a queen
        if ('*' in value):
            squareParent.create_line(self.getCrownCorners(
                parentSize, (35, 65), (30, 40), (40, 45), 35), fill='white', width=3)

        # if there is eventHandler, piece belongs to player and is selectable
        if (eventHandler != None):
            self.color = color
            self.selectedColor = selectedColor
            # piece click event listener
            squareParent.tag_bind(self.shape, '<ButtonPress-1>',
                                  eventHandler.onPlayerSquareSelected)

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

    def __init__(self, root, size, squareColor, row, column, eventHandler):
        super().__init__(root, size, squareColor, row, column)
        # empty square click event listener
        self.bind("<ButtonPress-1>", eventHandler.onEmptySquareSelected)


class OpponentSquare(Square):

    def __init__(self, root, size, squareColor, pieceValue, pieceColor, row, column):
        super().__init__(root, size, squareColor, row, column)
        self.piece = Piece(self, size, pieceValue, pieceColor, None, None)


class PlayerSquare(Square):

    def __init__(self, root, size, squareColor, pieceValue, pieceColor, selectedPieceColor, row, column, eventHandler):
        super().__init__(root, size, squareColor, row, column)
        self.piece = Piece(self, size, pieceValue,
                           pieceColor, selectedPieceColor, eventHandler)


####################### TKINTER BOARD MANAGER #######################


class Game(tk.Frame):

    def __init__(self, root, length, isLocal, eventHandler, theme):

        # Board Frame value
        self.length = length
        self.theme = theme
        super().__init__(master=root, height=self.length,
                         width=self.length, bg=self.theme.boardColor)

        # game state
        self.isLocalGame = isLocal

        # event handler to pass to controller
        self.eventHandler = eventHandler

    def setPlayerValues(self, playerValue, playerTheme):
        # player value : player1 or player2
        self.playerValue = playerValue
        self.theme = playerTheme
        

    def createBoardSquares(self, layout):
        # board config
        self.boardSize = len(layout[0])
        self.squareSize = self.length / self.boardSize

        for row in range(self.boardSize):
            for column in range(self.boardSize):
                squareValue = layout[row][column]
                if (squareValue != ''):
                    square = self.createSquare(
                        squareValue, row, column, self.eventHandler)

                    # flip layout filling if the player is player2 for first pov
                    if (self.isLocalGame == False and self.playerValue == '2'):
                        square.grid(row=self.boardSize - row,
                                    column=self.boardSize - column)
                    else:
                        square.grid(row=row, column=column)
        

    def createSquare(self, pieceValue, rowPosition, columnPosition, eventHandler):
        if ('E' in pieceValue):
            return EmptySquare(self, self.squareSize,
                               self.theme.squareColor, rowPosition, columnPosition, eventHandler)
        elif (self.playerValue in pieceValue):
            return PlayerSquare(self, self.squareSize, self.theme.squareColor, pieceValue,
                                self.theme.playerColor, self.theme.selectedPieceColor, rowPosition, columnPosition, eventHandler)
        else:
            # square is automatically for the opponent
            return OpponentSquare(self, self.squareSize, self.theme.squareColor, pieceValue,
                                  self.theme.opponentColor, rowPosition, columnPosition)
