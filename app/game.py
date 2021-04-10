
import tkinter as tk
import socketio as socketio
import json as json
from data import Game, AIPlayer
from ihm import Home, BoardView
from math import inf

# *** Game

####################### USER INTERFACE OBJECT #######################


class Theme:

    def __init__(self, name, boardColor, squareColor, player1Color, player2Color, selectedPieceColor, selectedMoveColor):

        self.name = name

        self.boardColor = boardColor
        self.squareColor = squareColor
        self.player1Color = player1Color
        self.player2Color = player2Color
        self.selectedPieceColor = selectedPieceColor
        self.selectedMoveColor = selectedMoveColor

    def getPlayerColor(self, player):

        if ('1' in player):
            return self.player1Color
        else:
            return self.player2Color


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

        # send selectedPiece info to model
        selectedPiece = {
            'row': self.selectedSquare.row,
            'column': self.selectedSquare.column,
            'value': self.selectedSquare.value
        }

        self.app.onPlayerPossibleMove(selectedPiece)

    def onEmptySquareSelected(self, event):
        # send move position value if a piece is selected and it is the player's turn
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
        moveProperty = {
            'piecePosition': selectedPiece,
            'emptyPosition': selectedEmpty
        }

        # sending move data to model/server for validation
        print('Sending move to model')
        self.app.onPlayerMove(moveProperty)

    # home event

    def onNewGameButton(self):
        self.app.getGameBoard(True, True,
                              8, False, False)

    def onSettingsButton(self):
        pass

    def onAboutButton(self):
        pass

    # game creation event
    def onStartNewGameButton(self, isLocalGame, isMultiGame, boardSize, isCaptureAuto, isBlownAuto):
        self.app.getGameBoard(isLocalGame, isMultiGame,
                              boardSize, isCaptureAuto, isBlownAuto)


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
        self.minLength = 800
        self.minsize(width=self.minLength, height=self.minLength)

        # setup theme
        self.themes = [
            Theme('default', '#FFF', '#010101', '#FD0002',
                  '#010101', '#FFEB41', '#D9E0B0'),
            Theme('Space blue', '#E2F1F9', '#031D7B',
                  '#D1B9B5', '#FDDF83', '#FFEB41', '#D9E0B0'),
            Theme('Classic brown', '#F5DEB3', '#AC7D58',
                  '#000', 'FFF', '#FFEB41', '#D9E0B0')
        ]

        # setup the grid layout manager
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=1)

        # init Event Handler
        self.eventHandler = EventHandler(self)

        # init home + info label
        self.displayedFrame = None
        self.getHome()

    # interface controller

    def getHome(self):
        home = Home(self, self.eventHandler)
        self.renderFrame(home)

    def renderFrame(self, frame):
        if(self.displayedFrame != None):
            self.displayedFrame.destroy()
        self.displayedFrame = frame
        self.displayedFrame.grid(row=0, column=0, columnspan=3, sticky='')

    # game controller

    def getGameBoard(self, isLocalGame, isMultiGame, size, isCaptureAuto, isBlownAuto):
        self.game = Game(isLocalGame, isMultiGame, size,
                         isCaptureAuto, isBlownAuto)
        self.boardView = BoardView(self, 800, isLocalGame,
                                   self.eventHandler, self.themes[0])
        print('game created')

        self.displayedFrame.destroy()
        self.renderBoard(self.game.getBoardLayout())

    def renderBoard(self, layout):
        self.boardView.createBoardSquares(layout, self.game.playerTurn)
        self.boardView.grid(row=0, column=1)

    def onPlayerPossibleMove(self, selectedPiece):
        self.renderBoard(
            self.game.board.getPieceMovesBoard(
                selectedPiece, self.game.mustCapture, self.game.lastMovedPiece))

    def onPlayerMove(self, move):

        performedMove = self.game.setPlayerMove(move)
        if (performedMove == 'gameover'):
            print('gameover')
        else:
            self.renderBoard(self.game.getBoardLayout())


# * application init
if __name__ == "__main__":

    # launching app
    app = App()

    # firing endless loop
    app.mainloop()
