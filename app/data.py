
import math as math
import copy as copy

# *** Data


####################### BOARD STATE MANAGER #######################


class Board():

    def __init__(self, size, isBlownAuto):
        self.turn = 1
        self.size = size
        self.isBlownAuto = isBlownAuto
        self.layout = self.createBoard(
            self.size)

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

    def getProperty(self, item):
        row = item['row']
        column = item['column']
        value = item['value']

        return (row, column, value)

    def getDictionary(self, row, column, value):

        return {
            'row': row,
            'column': column,
            'value': value
        }

    def getPlayerPiecesCount(self, playerValue):

        return len(self.getPlayerPieces(playerValue))

    def getPlayerQueensCount(self, playerValue):

        count = 0
        for piece in self.getPlayerPieces(playerValue):
            if '*' in piece:
                count += 1

        return count

    def getPlayerPieces(self, playerValue):

        pieces = []

        for row in range(self.size):
            for column in range(self.size):
                pieceValue = self.layout[row][column]
                if (playerValue in pieceValue):
                    piece = self.getDictionary(row, column, pieceValue)
                    pieces.append(piece)

        return pieces

    def getPlayerMoves(self, player, mustCapture):

        playerPieces = self.getPlayerPieces(player)
        playerMoves = []
        moveCount = 0

        for playerPiece in playerPieces:
            moves = self.getPossibleMoves(playerPiece, mustCapture)
            moveCount += len(moves)
            playerMoves.append(moves)

        return (playerPieces, playerMoves, moveCount)

    def getWinner(self):

        player2Pieces, player2Moves, player2MoveCount = self.getPlayerMoves(
            '2', False)
        player1Pieces, player1Moves, player1MoveCount = self.getPlayerMoves(
            '1', False)

        if(len(player2Pieces) == 0 or player2MoveCount == 0):
            return '1'
        elif(len(player1Pieces) == 0 or player1MoveCount == 0):
            return '2'
        else:
            return None

    def getDiagonalSquares(self, pieceRow, pieceColumn, rowOffset, columnOffset, depth):
        row = math.trunc(pieceRow + rowOffset)
        column = math.trunc(pieceColumn + columnOffset)

        # assure row column is inside of column
        if(row in range(0, self.size) and column in range(0, self.size)):
            value = self.layout[row][column]
            square = self.getDictionary(row, column, value)

            if (depth == 1):
                return [square]
            else:
                # using recursion to get every squares
                squares = [square]
                squares.extend(self.getDiagonalSquares(
                    row, column, rowOffset, columnOffset, depth - 1))
                return squares
        else:
            return []

    def getPossibleMoves(self, piecePosition, mustCapture):

        # rangeOffset
        # ? (-1, -1) -> upper left
        # ? (-1, 1) -> bottom left
        # ? (1, -1) -> upper right
        #  ? (1, 1) -> bottom left
        offsets = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        pieceRow, pieceColumn, piece = self.getProperty(piecePosition)

        moves = []

        # check for queen move
        if ('*' in piece):
            # get possible moves upperLeft
            # getting forward move
            for offset in offsets:
                rowOffset, columnOffset = offset
                diagonalSquareMoves = self.getDiagonalSquares(
                    pieceRow, pieceColumn, rowOffset, columnOffset, self.size)
                capturableSquare = None
                for diagonalMove in diagonalSquareMoves:
                    if ('E' in diagonalMove['value']):
                        if(capturableSquare != None):
                            moveType = 'c' + \
                                str(capturableSquare['row']) + \
                                str(capturableSquare['column'])
                        else:
                            moveType = ''
                        move = self.getDictionary(
                            diagonalMove['row'], diagonalMove['column'], moveType)
                        if(not mustCapture or (mustCapture and 'c' in moveType)):
                            moves.append(move)
                    elif(not piece[0] in diagonalMove['value'] and capturableSquare == None):
                        capturableSquare = diagonalMove
                    else:
                        # we assume it is a friendly piece so we can't assign move anymore
                        break

        else:
            for offset in offsets:
                # getting move type
                offsetRow, offsetColumn = offset

                # getting capture move type
                capturableRangeSquares = self.getDiagonalSquares(
                    pieceRow, pieceColumn, offsetRow, offsetColumn, 2)
                if (len(capturableRangeSquares) >= 1):
                    nearbySquare = capturableRangeSquares[0]
                    # if capturableSquares return length of 1, we can try to move if there is nearby empty square
                    if(not mustCapture and self.canPieceMove(piece, offsetRow, offsetColumn) and nearbySquare['value'] == 'E'):
                        move = self.getDictionary(nearbySquare['row'],
                                                  nearbySquare['column'], '')
                        moves.append(move)
                    # if else, we can try to capture
                    elif(len(capturableRangeSquares) == 2 and self.canCapture(nearbySquare['value'], piece)):
                        potentialEmptySquare = capturableRangeSquares[1]
                        # check if the square is not empty and belongs to opponent so it can be captured
                        if ('E' in potentialEmptySquare['value']):
                            # 'c' symbolize as a capture move
                            moveType = 'c' + \
                                str(nearbySquare['row']) + \
                                str(nearbySquare['column'])
                            move = self.getDictionary(
                                potentialEmptySquare['row'], potentialEmptySquare['column'], moveType)
                            moves.append(move)

        return moves

    def getPieceMovesBoard(self, piecePosition, mustCapture, lastMovedPiecePosition):
        pieceRow, pieceColumn, piece = self.getProperty(piecePosition)

        pieceBoardMoves = self.getBoardLayout()

        pieceBoardMoves[pieceRow][pieceColumn] += '\''

        # TODO review two pieces comparison effectiveness
        if(mustCapture and (pieceRow != lastMovedPiecePosition['row'] and pieceColumn != lastMovedPiecePosition['column'])):
            return pieceBoardMoves

        for pieceMove in self.getPossibleMoves(piecePosition, mustCapture):
            row, column, moveType = self.getProperty(pieceMove)
            pieceBoardMoves[row][column] += '+' + moveType

        return pieceBoardMoves

    def movePiece(self, initialPosition, newPosition, isCaptureAuto):

        self.turn += 1
        initialRow, initialColumn, piece = self.getProperty(
            initialPosition)
        newRow, newColumn, empty = self.getProperty(newPosition)
        pieceValue = self.layout[initialRow][initialColumn]

        if (not 'c' in empty and self.isBlownAuto and self.canPlayerCapture(pieceValue)):
            for playerPiece in self.getPlayerPieces(pieceValue):
                rowPiece, columnPiece, value = self.getProperty(
                    playerPiece)
                if (self.canMultipleCapture(playerPiece)):
                    self.capturePiece(rowPiece, columnPiece)

        if('c' in empty or not self.isBlownAuto or (self.isBlownAuto and not self.canMultipleCapture(initialPosition))):
            # swap square value
            self.layout[initialRow][initialColumn] = 'E'
            self.layout[newRow][newColumn] = pieceValue

            # add '*' queen tag to piece layout data if piece can be a queen
            if (self.canUpgradeQueen(piece, newRow)):
                self.layout[newRow][newColumn] += '*'

        # check if move is capture
        # ? following getPossibleMove, every selectable squares follows this pattern:
        # ? {pieceValue: '1' or '2'}{+}{if move is a capture => 'c'{pieceRow}{pieceColumn}}
        if ('c' in empty):
            self.capturePiece(int(empty[-2]), int(empty[-1]))
            newPosition['value'] = piece
            if (isCaptureAuto and self.canMultipleCapture(newPosition)):
                self.turn -= 1
                self.movePiece(newPosition, self.getPossibleMoves(
                    newPosition, True)[0], True)
            else:
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
        piecePossibleMoves = self.getPossibleMoves(piecePosition, True)

        return len(piecePossibleMoves) >= 1

        return False

    def canUpgradeQueen(self, piece, row):
        # check if piece is already a queen
        # and if if player reached opposite row
        return (not ('*' in piece) and (('1' in piece and row == 0) or ('2' in piece and row == self.size - 1)))

    def canPieceMove(self, piece, deltaRow, deltaColumn):

        # check if player move sideways
        if (abs(deltaColumn) == 1):
            if('1' in piece):
                # player1 have to move forward to the root
                return (deltaRow == -1)
            elif ('2' in piece):
                # player2 have to move forward to the layout.size
                return (deltaRow == 1)

    def canPlayerCapture(self, playerValue):
        return len(self.getPlayerMoves(playerValue, True)[1]) >= 1

    # * AI func

    # evaluate move based on player pieces

    def evaluate(self, player, opponent):

        winEvaluation = 0
        if(self.getWinner() == player):
            winEvaluation = 1
        elif(self.getWinner() == opponent):
            winEvaluation = -1

        queenEvaluation = self.getPlayerQueensCount(
            player) - self.getPlayerQueensCount(opponent)

        piecesCountEvaluation = self.getPlayerPiecesCount(
            player) - self.getPlayerPiecesCount(opponent)

        return winEvaluation + queenEvaluation + piecesCountEvaluation


####################### AI MANAGER #######################

class AIPlayer():

    def __init__(self, playerValue):
        self.playerValue = playerValue
        self.opponentValue = str(int(self.playerValue) % 2 + 1)
        self.count = 0

    def minimax(self, boardPosition: Board, depth, alpha, beta, player):
        self.count += 1
        if (depth == 0 or boardPosition.getWinner() != None):
            return (boardPosition.evaluate(self.playerValue, self.opponentValue), boardPosition)

        if(player == self.playerValue):
            # maximizing for AIPlayer
            maxEvaluation = -math.inf
            bestBoardMove = None
            for boardPossiblePosition in self.getAllMoves(boardPosition, player):
                # getting evaluation for next node -> opponent move
                evaluation, boardPosition = self.minimax(
                    boardPossiblePosition, depth - 1, alpha, beta, self.opponentValue)
                maxEvaluation = max(maxEvaluation, evaluation)
                if (maxEvaluation == evaluation):
                    bestBoardMove = boardPossiblePosition
                alpha = max(alpha, evaluation)
                # pruning
                if (beta <= alpha):
                    break
            return (maxEvaluation, bestBoardMove)

        else:
            # minimizing for opponent player
            minEvaluation = math.inf
            bestBoardMove = None
            for boardPossiblePosition in self.getAllMoves(boardPosition, player):
                # getting evaluation for next node -> AI
                evaluation, boardPosition = self.minimax(
                    boardPossiblePosition, depth - 1, alpha, beta, self.playerValue)
                minEvaluation = min(minEvaluation, evaluation)
                if (minEvaluation == evaluation):
                    bestBoardMove = boardPossiblePosition
                beta = min(beta, evaluation)
                # pruning
                if (beta <= alpha):
                    break
            return (minEvaluation, bestBoardMove)

    def getAllMoves(self, boardPosition: Board, player):
        boards = []

        newBoardLayout = boardPosition.getBoardLayout()
        playerPieces, playerMoves, playerMoveCount = boardPosition.getPlayerMoves(
            player, False)

        for pieceIndex in range(len(playerPieces)):
            for moveIndex in range(len(playerMoves[pieceIndex])):
                board = copy.deepcopy(boardPosition)
                board.movePiece(
                    playerPieces[pieceIndex], playerMoves[pieceIndex][moveIndex], True)
                boards.append(board)

        return boards
