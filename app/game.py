import tkinter as tk
import socketio
import json
from data import Board
from ihm import Game

# *** Game


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


####################### EVENT MANAGER #######################


class EventHandler:

    # variable init

    def __init__(self, app):
        self.app = app
        self.selectedSquare = None
        self.serverConnection = None

    # game event

    def onPlayerSquareSelected(self, event):

        # storing canvas event info
        self.selectedSquare = event.widget

        # # highliting selected piece with theme color
        # self.selectedSquare.itemconfigure(
        #     self.selectedPiece, fill=self.selectedSquare.piece.selectedColor)

        # send selectedPiece info to model
        selectedPiece = {
            'row': self.selectedSquare.row,
            'column': self.selectedSquare.column,
            'value': self.selectedSquare.value
        }

        self.app.onPlayerPossibleMovement(selectedPiece)

    def onEmptySquareSelected(self, event):
        # send movement position value if a piece is selected and it is the player's turn
        if((self.selectedSquare != None) and (app.isPlayerTurn)):
            print('piecegame', self.selectedSquare.value)
            selectedPiece = {
                'row': self.selectedSquare.row,
                'column': self.selectedSquare.column,
                'value': self.selectedSquare.value
            }
            selectedEmpty = {
                'row': event.widget.row,
                'column': event.widget.column,
                'value': event.widget.value
            }
            movementProperty = {
                'piecePosition': selectedPiece,
                'emptyPosition': selectedEmpty
            }

            # sending movement data to model/server for validation
            print('Sending movement to model')
            if(self.app.isLocalGame):
                self.app.onPlayerMove(movementProperty)
            else:
                self.serverConnection.socket.emit(
                    'move', json.dumps(movementProperty))

    # home event

    def onNewOfflineMultiGame(self):
        self.app.createLocalGame()

    def onNewOnlineMultiGame(self):
        self.app.isLocalGame = False

        # check if app is already connected to server
        if(self.serverConnection == None):
            self.serverConnection = ServerConnection(self.app)


####################### SERVER COMMUNICATION MANAGER ######################

class ServerConnection():

    def __init__(self, app):
        self.app = app
        self.socket = socketio.Client()

        # connecting to socket server
        try:
            self.socket.connect('http://localhost:5500')
        except Exception:
            try:
                print('No local server found, connecting to remote')
                self.socket.connect('https://damnier.herokuapp.com/')
            except Exception as error:
                print('Can\'t connect to remote server:', error)
                self.app.infoLabel.notify(
                    'Erreur: Impossible de se connecter au serveur')
                self.socket = None

        # * server communication handlers

        #  connection events

        # player is connected to socket server
        @self.socket.on('connect')
        def onConnect():
            print('You in!')

        # player get disconnected from socket server
        @self.socket.on('disconnect')
        def onDisconnect():
            print('Oops, disconnected')

        #  game events

        @self.socket.on('playersetup')
        def onPlayerSetup(data):
            print('Congrats! You are player ' + str(json.loads(data)))
            self.app.setPlayerProperty(json.loads(data))
            self.app.createGame()
            self.app.infoLabel.notify(
                'Connection au serveur réussi. En attente d\'un autre joueur')

        @self.socket.on('loadboard')
        def onLoadboard(data):
            self.app.renderBoard(json.loads(data))

        @self.socket.on('playerturn')
        def onPlayerTurn(data):
            self.app.setPlayerTurn(json.loads(data))

        @self.socket.on('captureopponent')
        def onCaptureOpponent():
            print('Gotta capture another piece to end your turn!')
            self.app.infoLabel.notify(
                'C\'est votre tour! Vous pouvez encore mangez!')


####################### APPLICATION MANAGER #######################


class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title('Damnier')
        self.width = 800
        self.height = self.width + 20
        self.minsize(width=self.width, height=self.height)
        self.resizable(0, 0)

        # setup the grid layout manager
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # setup turn management
        self.isPlayerTurn = False

        # init Event Handler
        self.eventHandler = EventHandler(self)

        # init home + info label
        self.__create_widgets()

    def __create_widgets(self):
        self.home = Home(self, self.eventHandler)
        self.infoLabel = InfoLabel(self)

        self.home.grid(row=0, column=0, sticky='')
        self.infoLabel.grid(row=1, column=0, sticky='')

    def createLocalGame(self):
        self.isLocalGame = True
        self.board = Board(8)
        self.setPlayerProperty('1')
        self.setPlayerTurn('1')
        self.createGame()
        self.renderBoard(self.board.getBoardLayout())
        self.isPlayerTurn = True

    def setPlayerProperty(self, playerValue):
        self.playerValue = playerValue
        self.theme = self.setTheme(self.playerValue)
        print('player value set')

    def createGame(self):
        self.game = Game(self, self.width, self.isLocalGame,
                         self.eventHandler, self.theme)
        self.game.setPlayerValues(self.playerValue, self.theme)
        self.game.grid(row=0, column=0)
        print('game created')

    def renderBoard(self, layout):
        self.game.createBoardSquares(layout)

    # TODO : add custom theme
    def setTheme(self, playerValue):
        if (playerValue == '1'):
            # player is player1 => initial colors
            return Theme('#FFF', '#010101', '#FD0002', '#010101', '#FFEB41')
        else:
            # player is player2 => swap player colors
            return Theme('#FFF', '#010101', '#010101', '#FD0002', '#FFEB41')

    def setPlayerTurn(self, turn):
        if(self.isLocalGame):
            if(turn == '1'):
                self.infoLabel.notify('Au tour des rouges')
            else:
                self.infoLabel.notify('Au tour des noires')
        else:
            self.isPlayerTurn = turn
            if (self.isPlayerTurn):
                self.infoLabel.notify('C\'est votre tour! ')
            else:
                self.infoLabel.notify('Tour de l\'adversaire. ')

    def onPlayerPossibleMovement(self, selectedPiece):
        self.renderBoard(self.board.getPieceMovesBoard(selectedPiece))

    def onPlayerMove(self, movement):
        performedMovement = self.board.movePiece(
            movement['piecePosition'], movement['emptyPosition'])
        self.board.turn += 1
        # if (performedMovement == 'capture' and self.board.canMultipleCapture(movement['emptyPosition'])):
        #     # after capture, player piece is now positionned on previous empty
        #     player = self.board.getSquarePlayer(
        #         movement['emptyPosition'])
        #     app.infoLabel.notify(
        #         'Vous pouvez encore mangez!')
        # else:
        self.setPlayerProperty(str((int(self.playerValue) % 2) + 1))
        self.setPlayerTurn(self.playerValue)
        self.game.setPlayerValues(self.playerValue, self.theme)

        self.renderBoard(self.board.getBoardLayout())


class Home(tk.Frame):

    def __init__(self, root, eventHandler):

        # Home Frame value
        self.length = 800
        super().__init__(master=root, height=self.length, width=self.length)

        # event handler to pass to app
        self.eventHandler = eventHandler

        self.__create_widgets()

    def __create_widgets(self):
        self.title = tk.Label(
            self, text='Welcome to Damnier!', font='Arial 30 bold')
        self.newOfflineMultiGame = tk.Button(
            self, text='Nouvelle partie multijoueur local', command=self.eventHandler.onNewOfflineMultiGame)
        self.newOnlineMultiGame = tk.Button(
            self, text='Nouvelle partie multijoueur en ligne', command=self.eventHandler.onNewOnlineMultiGame)

        # packing the buttons
        self.title.pack()
        self.newOfflineMultiGame.pack()
        self.newOnlineMultiGame.pack()


# * application init
if __name__ == "__main__":

    # launching app
    app = App()

    # firing endless loop
    app.mainloop()
