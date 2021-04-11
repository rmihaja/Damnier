
from math import inf, trunc
from copy import deepcopy

# *** Data

####################### GAME STATE MANAGER #######################


class Game:

    def __init__(self, gameMode, isGameWithAI, size, timeLimit, isCaptureAuto, isBlownAuto):

        self.boardHistory = []
        self.moveHistory = []

        # game options
        self.isCaptureAuto = isCaptureAuto
        self.isBlownAuto = isBlownAuto

        if (timeLimit > 0):
            self.isTimeLimit = True
        else:
            self.isTimeLimit = False

        # move setup
        self.mustCapture = False
        self.lastMovedPiece = None

        # init game
        self.createGame(gameMode, size, isGameWithAI)
        self.playerTurn = '1'

    def createGame(self, gameMode, size, isGameWithAI):

        self.board = BoardData(size, self.isBlownAuto)
        self.gameType = gameMode

        # player vs AI game
        if (isGameWithAI):
            self.gameType = 'single_' + gameMode
            self.playerAI = AIPlayer('2')

        # player vs player game
        else:
            self.gameType = 'multi_' + gameMode
            if('online' in gameMode):
                self.serverConnection = ServerConnection(self.app)

    def getBoardLayout(self):
        return self.board.getLayout()

    def setPlayerMove(self, move):

        self.boardHistory.append(self.board.getLayout())

        piecePosition, emptyPosition = move['piecePosition'], move['emptyPosition']
        performedMove = self.board.movePiece(
            piecePosition, emptyPosition, self.isCaptureAuto)

        # set last move piece to his future position
        self.lastMovedPiece = emptyPosition
        self.lastMovedPiece['value'] = emptyPosition['value']

        if (performedMove == 'capture' and self.board.canMultipleCapture(self.lastMovedPiece)):
            # after capture, player piece is now positionned on previous empty
            self.mustCapture = True
            return 'capture'

        if (self.board.getWinner() != None):
            return 'gameover'

        if ('single' in self.gameType):
            # AI turn
            minimaxEvaluation, bestBoardMove = self.playerAI.minimax(
                self.board, 3, -inf, inf, self.playerAI.playerValue)
            self.board.layout = bestBoardMove.getLayout()
            print('node evaluated:', self.playerAI.count)
            print('minimax evaluation:', minimaxEvaluation)
            self.playerAI.count = 0
        else:
            self.mustCapture = False
            self.playerTurn = str(int(self.playerTurn) % 2 + 1)
            return 'turn'


####################### BOARD STATE MANAGER #######################


class BoardData():

    def __init__(self, size, isBlownAuto):
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

    # return board layout array
    def getLayout(self):
        return deepcopy(self.layout)

    # method communications
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

        return len(self.moveHistory)

    def getPlayerPiecesCount(self, player):
        return len(self.getPlayerPieces(player))

    def getPlayerQueensCount(self, player):

        count = 0
        for piece in self.getPlayerPieces(player):
            if '*' in piece:
                count += 1

        return count

    def getPlayerPieces(self, player):

        pieces = []

        for row in range(self.size):
            for column in range(self.size):
                pieceValue = self.layout[row][column]
                if (player in pieceValue):
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
        row = trunc(pieceRow + rowOffset)
        column = trunc(pieceColumn + columnOffset)

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

    def getPossibleMoves(self, piece, mustCapture):

        # rangeOffset
        # ? (-1, -1) -> upper left
        # ? (-1, 1) -> bottom left
        # ? (1, -1) -> upper right
        #  ? (1, 1) -> bottom left
        offsets = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        pieceRow, pieceColumn, pieceValue = self.getProperty(piece)

        moves = []

        # check for queen move
        if ('*' in pieceValue):
            # get possible moves upperLeft
            # getting forward move
            for offset in offsets:
                rowOffset, columnOffset = offset
                diagonalSquareMoves = self.getDiagonalSquares(
                    pieceRow, pieceColumn, rowOffset, columnOffset, self.size)
                capturableSquare = None
                for diagonalMove in diagonalSquareMoves:

                    moveRow, moveColumn, moveSquareValue = self.getProperty(
                        diagonalMove)

                    if ('E' in moveSquareValue):
                        if(capturableSquare != None):

                            captureRow, captureColumn, captureSquareValue = self.getProperty(
                                capturableSquare)
                            moveType = 'c' + \
                                str(captureRow) + \
                                str(captureColumn)
                        else:
                            moveType = ''

                        move = self.getDictionary(
                            moveRow, moveColumn, moveType)
                        if(not mustCapture or (mustCapture and 'c' in moveType)):
                            moves.append(move)
                    elif(not pieceValue[0] in moveSquareValue and capturableSquare == None):
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
                    nearbySquareRow, nearbySquareColumn, nearbySquareValue = self.getProperty(
                        capturableRangeSquares[0])

                    # if capturableSquares return length of 1, we can try to move if there is nearby empty square
                    if(not mustCapture and self.canPieceMove(pieceValue, offsetRow, offsetColumn) and nearbySquareValue == 'E'):
                        move = self.getDictionary(nearbySquareRow,
                                                  nearbySquareColumn, '')
                        moves.append(move)
                    # if else, we can try to capture
                    elif(len(capturableRangeSquares) == 2 and nearbySquareValue != 'E' and pieceValue[0] != nearbySquareValue[0]):
                        # check if the square we can move to eat is empty
                        if ('E' in capturableRangeSquares[1]['value']):
                            emptyRow, emptyColumn, emptyValue = self.getProperty(
                                capturableRangeSquares[1])
                            # 'c' symbolize as a capture move
                            moveType = 'c' + \
                                str(nearbySquareRow) + \
                                str(nearbySquareColumn)
                            move = self.getDictionary(
                                emptyRow, emptyColumn, moveType)
                            moves.append(move)

        return moves

    def getPieceMovesBoard(self, piece, mustCapture, lastMovedPiece):
        pieceRow, pieceColumn, pieceValue = self.getProperty(piece)

        pieceBoardMoves = self.getLayout()

        pieceBoardMoves[pieceRow][pieceColumn] += '\''

        # TODO review two pieces comparison effectiveness
        if(mustCapture):
            movedPieceRow, movedPieceColumn, movedPieceValue = self.getProperty(
                lastMovedPiece)
            if (pieceRow != movedPieceRow and pieceColumn != movedPieceColumn):
                return pieceBoardMoves

        for pieceMove in self.getPossibleMoves(piece, mustCapture):
            row, column, moveType = self.getProperty(pieceMove)
            pieceBoardMoves[row][column] += '+' + moveType

        return pieceBoardMoves

    def movePiece(self, initialPosition, newPosition, isCaptureAuto):

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
                self.movePiece(newPosition, self.getPossibleMoves(
                    newPosition, True)[0], True)
            else:
                return 'capture'
        else:
            return 'move'

    def capturePiece(self, row, column):
        # replace square value to empty
        self.layout[row][column] = 'E'

    def canMultipleCapture(self, piecePosition):
        piecePossibleMoves = self.getPossibleMoves(piecePosition, True)

        return len(piecePossibleMoves) >= 1

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

    def minimax(self, board, depth, alpha, beta, player):
        self.count += 1
        if (depth == 0 or board.getWinner() != None):
            return (board.evaluate(self.playerValue, self.opponentValue), board)

        if(player == self.playerValue):
            # maximizing for AIPlayer
            maxEvaluation = -inf
            bestBoardMove = None
            for boardPossiblePosition in self.getAllMoves(board, player):
                # getting evaluation for next node -> opponent move
                evaluation, board = self.minimax(
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
            minEvaluation = inf
            bestBoardMove = None
            for boardPossiblePosition in self.getAllMoves(board, player):
                # getting evaluation for next node -> AI
                evaluation, board = self.minimax(
                    boardPossiblePosition, depth - 1, alpha, beta, self.playerValue)
                minEvaluation = min(minEvaluation, evaluation)
                if (minEvaluation == evaluation):
                    bestBoardMove = boardPossiblePosition
                beta = min(beta, evaluation)
                # pruning
                if (beta <= alpha):
                    break
            return (minEvaluation, bestBoardMove)

    def getAllMoves(self, board, player):
        boards = []

        playerPieces, playerMoves, playerMoveCount = board.getPlayerMoves(
            player, False)

        for pieceIndex in range(len(playerPieces)):
            for moveIndex in range(len(playerMoves[pieceIndex])):
                boardPossiblePosition = deepcopy(board)
                boardPossiblePosition.movePiece(
                    playerPieces[pieceIndex], playerMoves[pieceIndex][moveIndex], True)
                boards.append(boardPossiblePosition)

        return boards
