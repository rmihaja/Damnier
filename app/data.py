
import math as math

# *** Data


class Board():

    def __init__(self, size):
        self.turn = 1
        self.size = size
        self.layout = self.createBoard(self.size)

    def createBoard(self, size):
        layout = []
        for row in range(size):
            boardRow = []
            piece = ''
            # check if board belongs to players
            if(row < (size / 2) - 1):
                piece = '2'
            elif(row > (size / 2)):
                piece = '1'
            else:
                piece = 'E'

            # filling the row
            for column in range(size):
                if((row % 2 == 0 and column % 2 != 0) or (row % 2 != 0 and column % 2 == 0)):
                    boardRow.append(piece)
                else:
                    boardRow.append('')
            layout.append(boardRow)

        return layout

    # return array
    def getBoardLayout(self):
        return self.layout

    def getSquarePlayer(self, piecePosition):
        squarePlayer = self.layout[piecePosition['row']
                                   ][piecePosition['column']]
        return squarePlayer[0]

    def getInBetweenSquare(self, pieceRow, pieceColumn, deltaRow, deltaColumn):

        row = math.trunc(pieceRow + math.copysign(1, deltaRow))
        column = math.trunc(pieceColumn + math.copysign(1, deltaColumn))
        value = self.layout[row][column]

        square = {
            'row': row,
            'column': column,
            'value': value
        }

        print('the potential square to eat is ', square)
        return square

    def movePiece(self, piece, initialRow, initialColumn, newRow, newColumn):
        # swap square value
        self.layout[initialRow][initialColumn] = 'E'

        # add '*' queen tag to piece layout data if piece can be a queen
        queenValue = self.canUpgradeQueen(piece, newRow)

        self.layout[newRow][newColumn] = piece + queenValue

    def capturePiece(self, row, column):
        # replace square value to empty
        self.layout[row][column] = 'E'

    def canCapture(self, piece, playerPiece):
        pieceOwner = piece[0]
        playerValue = playerPiece[0]

        return pieceOwner != 'E' and pieceOwner != playerValue

    def canMultipleCapture(self, piecePosition):
        print('\n################################ BEGINTEST ################################\n')
        pieceRow = piecePosition['row']
        pieceColumn = piecePosition['column']
        piece = self.layout[pieceRow][pieceColumn]

        testNumber = 0

        for deltaRow in range(-2, 3, 4):
            for deltaColumn in range(-2, 3, 4):
                row = pieceRow + deltaRow
                column = pieceColumn + deltaColumn
                print('test ', testNumber)

                # check if offset square position does not exceed board size layout
                if ((0 <= row and row < self.size) and (0 <= column and column < self.size)):
                    print('Square has passed layout.size test')
                    # check if square is empty to perform the movement
                    if (self.layout[row][column] == 'E'):
                        print('Square has passed value == E test')
                        capturableSquare = self.getInBetweenSquare(
                            pieceRow, pieceColumn, deltaRow, deltaColumn)
                        if (self.canCapture(capturableSquare['value'], piece)):
                            print('\nRESULT: player can still move while eating')
                            print(
                                '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n')
                            return True
                testNumber += 1
        print('\nRESULT: All squares failed test. player cannot eat multiple time')
        print(
            '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        return False

    def canUpgradeQueen(self, piece, row):
        # check if piece is already a queen
        if ('*' in piece):
            return ''

        # check if player reached opposite row
        if (('1' in piece and row == 0) or ('2' in piece and row == len(self.layout) - 1)):
            return '*'
        else:
            return ''

    def canMove(self, piece, deltaRow, deltaColumn):

        # check if piece is queen, can move diagonally
        if('*' in piece):
            return abs(deltaRow) == abs(deltaColumn)
        else:
            # check if player move sideways
            if (abs(deltaColumn) == 1):
                if('1' in piece):
                    # player1 have to move forward to the root
                    return deltaRow == -1
                elif ('2' in piece):
                    # player2 have to move forward to the layout.size
                    return deltaRow == 1

    def tryMovement(self, piecePosition, emptyPosition):
        pieceRow = piecePosition['row']
        pieceColumn = piecePosition['column']
        emptyRow = emptyPosition['row']
        emptyColumn = emptyPosition['column']

        piece = self.layout[pieceRow][pieceColumn]

        deltaRow = emptyRow - pieceRow
        deltaColumn = emptyColumn - pieceColumn

        # * simple move

        if (self.canMove(piece, deltaRow, deltaColumn)):
            self.movePiece(piece, pieceRow, pieceColumn, emptyRow, emptyColumn)
            return 'move'

        # * move and capture

        # get square in the middle of empty and piece
        capturableSquare = self.getInBetweenSquare(
            pieceRow, pieceColumn, deltaRow, deltaColumn)
        # check if the square is not empty and belongs to opponent so it can be captured
        if (self.canCapture(capturableSquare['value'], piece)):
            self.capturePiece(
                capturableSquare['row'], capturableSquare['column'])
            # move piece if move captures opponent piece
            self.movePiece(piece, pieceRow, pieceColumn, emptyRow, emptyColumn)
            return 'capture'

        # * invalid move
        return None

    # def canMoveQueen(self, deltaRow, deltaColumn):
