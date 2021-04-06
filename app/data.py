
import math as math
import copy as copy

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
        return copy.deepcopy(self.layout)

    def getPieceProperty(self, piecePosition):
        pieceRow = piecePosition['row']
        pieceColumn = piecePosition['column']
        piece = piecePosition['value']

        return (pieceRow, pieceColumn, piece)

    def getDiagonalSquares(self, pieceRow, pieceColumn, rowOffset, columnOffset, depth):
        row = math.trunc(pieceRow + rowOffset)
        column = math.trunc(pieceColumn + columnOffset)

        # assure row column is inside of column
        if(row in range(0, self.size) and column in range(0, self.size)):
            value = self.layout[row][column]
            square = {
                'row': row,
                'column': column,
                'value': value
            }

            if (depth == 1):
                return [square]
            else:
                # using recursion to get every squares
                squares = list([square])
                squares.extend(self.getDiagonalSquares(
                    row, column, rowOffset, columnOffset, depth - 1))
                return squares
        else:
            return []

    def getPossibleMoves(self, piecePosition):

        # rangeOffset
        # ? (-1, -1) -> upper left
        # ? (-1, 1) -> bottom left
        # ? (1, -1) -> upper right
        #  ? (1, 1) -> bottom left
        offsets = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        pieceRow, pieceColumn, piece = self.getPieceProperty(piecePosition)

        moves = []

        # check for queen move
        if ('*' in piece):
            # get possible moves upperLeft
            # getting forward move
            for offset in offsets:
                rowOffset, columnOffset = offset
                diagonalSquareMoves = self.getDiagonalSquares(
                    pieceRow, pieceColumn, rowOffset, columnOffset, self.size)
                for diagonalMove in diagonalSquareMoves:
                    if ('E' in diagonalMove['value']):
                        move = (diagonalMove['row'],
                                diagonalMove['column'],
                                '')
                        moves.append(move)
                    else:
                        break

        else:
            for offset in offsets:
                # getting move type
                offsetRow, offsetColumn = offset

                # getting capture move type
                eatableRangeSquares = self.getDiagonalSquares(
                    pieceRow, pieceColumn, offsetRow, offsetColumn, 2)
                if (len(eatableRangeSquares) >= 1):
                    nearbySquare = eatableRangeSquares[0]
                    # if eatableSquares return length of 1, we can try to move if there is nearby empty square
                    if(self.canMove(piece, offsetRow, offsetColumn) and nearbySquare['value'] == 'E'):
                        move = (nearbySquare['row'],
                                nearbySquare['column'], '')
                        moves.append(move)
                    # if else, we can try to eat
                    elif(len(eatableRangeSquares) == 2 and self.canCapture(nearbySquare['value'], piece)):
                        potentialEmptySquare = eatableRangeSquares[1]
                        # check if the square is not empty and belongs to opponent so it can be captured
                        if ('E' in potentialEmptySquare['value']):
                            # 'c' symbolize as a capture move
                            moveType = 'c' + \
                                str(nearbySquare['row']) + \
                                str(nearbySquare['column'])
                            move = (
                                potentialEmptySquare['row'], potentialEmptySquare['column'], moveType)
                            moves.append(move)

        print(moves)
        return moves

    def getPieceMovesBoard(self, piecePosition):
        pieceRow, pieceColumn, piece = self.getPieceProperty(piecePosition)

        pieceBoardMoves = self.getBoardLayout()

        pieceBoardMoves[pieceRow][pieceColumn] += '\''

        for pieceMove in self.getPossibleMoves(piecePosition):
            row, column, moveType = pieceMove
            pieceBoardMoves[row][column] += '+' + moveType

        return pieceBoardMoves

    def movePiece(self, initialPosition, newPosition):

        initialRow, initialColumn, piece = self.getPieceProperty(
            initialPosition)
        newRow, newColumn, empty = self.getPieceProperty(newPosition)
        pieceValue = self.layout[initialRow][initialColumn]

        # swap square value
        self.layout[initialRow][initialColumn] = 'E'
        self.layout[newRow][newColumn] = pieceValue

        # add '*' queen tag to piece layout data if piece can be a queen
        if (self.canUpgradeQueen(piece, newRow)):
            self.layout[newRow][newColumn] += '*'

        # check if move is capture
        # ? following getPossibleMove, every selectable squares follows this pattern:
        # ? {pieceValue: '1' or '2'}{+}{if move is a capture => 'c'{pieceRow}{pieceColumn}}
        print('empty', empty)
        if ('c' in empty):
            print('to capture', empty[3], empty[4])
            print('captureRow')
            self.capturePiece(int(empty[3]), int(empty[4]))
            return 'capture'
        else:
            return 'move'

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

        for deltaRow in range(-1, 2, 2):
            for deltaColumn in range(-1, 2, 2):
                row = pieceRow + deltaRow
                column = pieceColumn + deltaColumn
                print('test ', testNumber)

                # check if offset square position does not exceed board size layout
                if (row in range(0, self.size) and column in range(0, self.size)):
                    print('Square has passed layout.size test')
                    # check if square is empty to perform the move
                    if (self.layout[row][column] == 'E'):
                        print('Square has passed value == E test')
                        capturableSquare = self.getDiagonalSquares(
                            pieceRow, pieceColumn, deltaRow, deltaColumn, 2)
                        if (self.canCapture(capturableSquare['value'][0], piece)):
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
        # and if if player reached opposite row
        return (not ('*' in piece) and (('1' in piece and row == 0) or ('2' in piece and row == self.size - 1)))

    def canMove(self, piece, deltaRow, deltaColumn):

        # check if piece is queen, can move diagonally
        if('*' in piece):
            return self.canMoveQueen(piece, deltaRow, deltaColumn)
        else:
            # check if player move sideways
            if (abs(deltaColumn) == 1):
                if('1' in piece):
                    # player1 have to move forward to the root
                    return (deltaRow == -1)
                elif ('2' in piece):
                    # player2 have to move forward to the layout.size
                    return (deltaRow == 1)

    def canMoveQueen(self, piece, deltaRow, deltaColumn):
        return True
