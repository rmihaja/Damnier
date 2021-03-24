import tkinter as tk
import math as math
from tkinter import Event, font
import socketio
import json

# *** data


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

    def movePiece(self, piece, initialRow, initialColumn, newRow, newColumn):
        # swap square value
        self.layout[initialRow][initialColumn] = 'E'

        # add '*' queen tag to piece layout data if piece can be a queen
        queenValue = self.canUpgradeQueen(piece, newRow)

        self.layout[newRow][newColumn] = piece + queenValue

    def capturePiece(self, row, column):
        # replace square value to empty
        self.layout[row][column] = 'E'

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
        # check if player move sideways
        if (abs(deltaColumn) == 1):
            # check if piece is queen, can move forward and backward
            if('*' in piece):
                return True
            if('1' in piece):
                # player1 have to move forward to the root
                return deltaRow == -1
            elif ('2' in piece):
                # player2 have to move forward to the layout.size
                return deltaRow == 1


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
        self.bind("<ButtonPress-1>", EventHandler.onEmptySquareSelected)


class OpponentSquare(Square):

    def __init__(self, root, size, squareColor, pieceValue, pieceColor, row, column):
        super().__init__(root, size, squareColor, row, column)
        self.piece = Piece(self, size, pieceValue, pieceColor, None)


class PlayerSquare(Square):

    def __init__(self, root, size, squareColor, pieceValue, pieceColor, selectedPieceColor, row, column):
        super().__init__(root, size, squareColor, row, column)
        self.piece = Piece(self, size, pieceValue,
                           pieceColor, selectedPieceColor)


####################### TKINTER BOARD MANAGER #######################


class Game(tk.Frame):

    def __init__(self, root, isLocal, layout, playerValue, theme):

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
        self.isLocalGame = isLocal

        # filling the board with canvases
        self.__create_widgets()

    def __create_widgets(self):
        for row in range(self.size):
            for column in range(self.size):
                squareValue = self.layout[row][column]
                if (squareValue != ''):
                    square = self.createSquare(squareValue, row, column)

                    # flip layout filling if the player is player2 for first pov
                    if (self.playerValue == '2' and not(self.isLocalGame)):
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

# *** game

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


####################### APPLICATION MANAGER #######################


class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title('Damnier')
        self.geometry('800x820')
        self.resizable(0, 0)

        # setup the grid layout manager
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # setup turn management
        self.isPlayerTurn = False

        # init home + info label
        self.__create_widgets()

    def __create_widgets(self):
        self.home = Home(self)
        self.infoLabel = InfoLabel(self)

        self.home.grid(row=0, column=0, sticky='')
        self.infoLabel.grid(row=1, column=0, sticky='')

    def createLocalGame(self):
        self.isLocalGame = True
        self.board = Board(8)
        self.setPlayerProperty('1')
        self.setPlayerTurn('1')
        self.renderBoard(self.board.getBoardLayout())
        self.isPlayerTurn = True

    def setPlayerProperty(self, playerValue):
        self.playerValue = playerValue
        self.theme = self.setTheme(self.playerValue)

    def renderBoard(self, layout):
        self.game = Game(self, self.isLocalGame, layout,
                         self.playerValue, self.theme)
        self.game.grid(row=0, column=0)

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

    def onPlayerMove(self, movement):
        performedMovement = self.board.tryMovement(
            movement['piecePosition'], movement['emptyPosition'])
        if (performedMovement != None):
            self.board.turn += 1
            if (performedMovement == 'capture' and self.board.canMultipleCapture(movement['emptyPosition'])):
                # after capture, player piece is now positionned on previous empty
                player = self.board.getSquarePlayer(
                    movement['emptyPosition'])
                app.infoLabel.notify(
                    'C\'est votre tour! Vous pouvez encore mangez!')
            else:
                self.setPlayerProperty(str((int(self.playerValue) % 2) + 1))

            self.renderBoard(self.board.getBoardLayout())


class Home(tk.Frame):

    def __init__(self, root):

        # Home Frame value
        self.length = 800
        super().__init__(master=root, height=self.length, width=self.length)

        self.__create_widgets()

    def __create_widgets(self):
        self.title = tk.Label(
            self, text='Welcome to Damnier!', font='Arial 30 bold')
        self.newOfflineMultiGame = tk.Button(
            self, text='Nouvelle partie multijoueur local', command=EventHandler.onNewOfflineMultiGame)
        self.newOnlineMultiGame = tk.Button(
            self, text='Nouvelle partie multijoueur en ligne', command=EventHandler.onNewOnlineMultiGame)

        # packing the buttons
        self.title.pack()
        self.newOfflineMultiGame.pack()
        self.newOnlineMultiGame.pack()


####################### TKINTER EVENT MANAGER #######################


class EventHandler:

    # variable init

    socket = None
    selectedSquare = None
    selectedPiece = None

    # game event

    @ classmethod
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

    @ classmethod
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
                print('Sending movement to model')
                if(app.isLocalGame):
                    app.onPlayerMove(movementProperty)
                else:
                    cls.socket.emit('move', json.dumps(movementProperty))

    # home event

    @classmethod
    def onNewOfflineMultiGame(cls):
        app.createLocalGame()

    @classmethod
    def onNewOnlineMultiGame(cls):
        app.isLocalGame = False

        if(cls.socket == None):
            cls.socket = socketio.Client()

            # TODO: Add server class
            # connecting to socket server
            try:
                cls.socket.connect('http://localhost:5500')
            except Exception:
                try:
                    print('No local server found, connecting to remote')
                    cls.socket.connect('https://damnier.herokuapp.com/')
                except Exception as error:
                    print('Can\'t connect to remote server:', error)
                    app.infoLabel.notify(
                        'Erreur: Impossible de se connecter au serveur')
                    cls.socket = None

        # * event handlers

        #  connection events

        # player is connected to socket server

        @cls.socket.on('connect')
        def onConnect():
            print('You in!')

        # player get connected to socket server

        @cls.socket.on('disconnect')
        def onDisconnect():
            print('Oops, disconnected')

        #  game events

        @cls.socket.on('playersetup')
        def onPlayerSetup(data):
            print('Congrats! You are player ' + str(json.loads(data)))
            global app
            app.setPlayerProperty(json.loads(data))
            app.infoLabel.notify('En attente d\'un joueur potentiel')

        @cls.socket.on('loadboard')
        def onLoadboard(data):
            global app
            app.renderBoard(json.loads(data))

        @cls.socket.on('playerturn')
        def onPlayerTurn(data):
            global app
            app.setPlayerTurn(json.loads(data))

        @cls.socket.on('captureopponent')
        def onCaptureOpponent():
            print('Gotta capture another piece to end your turn!')
            app.infoLabel.notify(
                'C\'est votre tour! Vous pouvez encore mangez!')


####################### SERVER CONNECTION MANAGER ######################
# * application init
if __name__ == "__main__":

    # launching app
    app = App()

    # firing endless loop
    app.mainloop()
