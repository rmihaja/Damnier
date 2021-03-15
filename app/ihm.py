from data import *
import tkinter as tk


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
