

import tkinter as tk
from tkinter import messagebox

import socketio as socketio
import json as json

from data import Game
from ihm import Home, NewGameSettings, JoinGameSettings, Settings, BoardView, PlayerStats, GameStats

from random import randrange

"""[CODE GUIDELINES]

    Project files should to be read from the bottom (components loading before controller)
    The main controller is App()

"""

# *** Game

####################### USER INTERFACE OBJECT #######################


class Theme:

    def __init__(self, name, boardColor, squareColor, player1Color, player2Color, selectedPieceColor, selectedMoveColor, textColor):

        self.name = name

        self.boardColor = boardColor
        self.squareColor = squareColor
        self.player1Color = player1Color
        self.player2Color = player2Color
        self.selectedPieceColor = selectedPieceColor
        self.selectedMoveColor = selectedMoveColor
        self.textColor = textColor

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

    # board events

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
        self.app.onPlayerMove(moveProperty, True)

    # game events

    def onplayerTimerOut(self, player):
        self.app.displayWinner(player, False)

    # user interface events

    def onNewGameButton(self):
        self.app.getNewGameSettings()

    def onJoinGameButton(self):
        self.app.getJoinGameSettings()

    def onSettingsButton(self):
        self.app.getSettings()

    def onJoinRoomButton(self, roomId):
        self.app.onPlayerJoinRoom(roomId)

    def onWindowClose(self):
        isUserClose = messagebox.askyesno(
            'Quitter', 'Etes-vous sûr de vouloir fermer le programme? Toute partie en cours sera perdu.')
        if (isUserClose):
            print('Closing app')
            if(self.app.serverConnection != None):
                self.app.serverConnection.socket.disconnect()
            self.app.destroy()

    # game creation event

    def onStartNewGameButton(self, gameMode, isGameWithAI, boardSize, timeLimit, isCaptureAuto, isBlownAuto, player1Name, player2Name):
        self.app.getGameBoard(gameMode, True,
                              isGameWithAI,
                              int(boardSize),
                              int(timeLimit),
                              isCaptureAuto, isBlownAuto,
                              player1Name, player2Name)


####################### SERVER COMMUNICATION MANAGER ######################


class ServerConnection():

    def __init__(self, app, isGameCreator, roomId):
        self.app = app
        self.isGameCreator = isGameCreator
        self.room = roomId

        # server init
        self.socket = socketio.Client()
        self.connectServer()

        # * connection events

        # player is connected to socket server
        @self.socket.on('connect')
        def onConnect():
            print('You are connected to server!')
            self.app.onPlayerSocketConnected()

        # player get disconnected from socket server
        @self.socket.on('disconnect')
        def onDisconnect():
            print('Oops, disconnected from server')

        # * room events

        @self.socket.on('room-create')
        def onRoomCreate(data):
            self.room = data
            self.app.gameStats.displayInfo(
                'Inviter votre adversaire avec le code :\n ' + self.room)

        @self.socket.on('room-join')
        def onRoomJoin():
            print('Someone joined room! Sending game data')
            self.app.onPlayer2JoinedRoom()

        # * game events

        @self.socket.on('game-setup')
        def onGameSetup(data):
            # turn data received from server to python readable data
            formattedData = json.loads(data)
            self.app.getGameBoard(formattedData['gameMode'],
                                  False,
                                  formattedData['isGameWithAI'],
                                  formattedData['boardSize'],
                                  formattedData['timeLimit'],
                                  formattedData['isCaptureAuto'],
                                  formattedData['isBlownAuto'],
                                  formattedData['player1Name'],
                                  formattedData['player2Name'])

        @self.socket.on('player-move')
        def onPlayerMove(data):
            move = json.loads(data)
            self.app.onPlayerMove(move, False)

    def connectServer(self):
        # connecting to socket server
        try:
            self.socket.connect('http://localhost:5500')
        except Exception:
            try:
                print('No local server found, connecting to remote')
                self.socket.connect('https://damnier.herokuapp.com/')
            except Exception as error:
                print('Can\'t connect to remote server:', error)
                isRetry = messagebox.askretrycancel(
                    'Erreur', 'Impossible de se connecter au serveur. Réessayez?\n\nNote : Si vous vous connectez pour la première fois au serveur distant, la première tentative sera un échec (le serveur utilisé ne permet pas une longue rétention).\nSoutenez notre projet pour qu\'on puisse acheter un meilleur serveur!')
                print(isRetry)
                if(isRetry):
                    self.connectServer()
                else:
                    self = None
                    app.getHome()

    def sendEvent(self, eventName):
        self.socket.emit(eventName, self.room)

    def sendEventData(self, eventName, eventData):
        # send data as tuple, server will receive it as separate arguments
        self.socket.emit(eventName, (self.room, json.dumps(eventData)))


####################### APPLICATION MANAGER #######################

class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title('Damnier')
        self.minHeight = 800
        self.minWidth = int(self.minHeight * 1.6)
        self.minsize(width=self.minWidth, height=self.minHeight)
        self.resizable(False, False)

        # setup theme
        self.themes = [
            Theme('default', '#FFF', '#010101', '#FD0002',
                  '#010101', '#FFEB41', '#D9E0B0', '#FFF'),
            Theme('Space blue', '#E2F1F9', '#031D7B',
                  '#D1B9B5', '#FDDF83', '#FFEB41', '#D9E0B0', '#FFF'),
            Theme('Classic brown', '#F5DEB3', '#AC7D58',
                  '#000', '#e0e0e0', '#FFEB41', '#D9E0B0', '#000')
        ]

        # init game
        self.game = None
        self.serverConnection = None

        self.currentTheme = self.themes[randrange(0, len(self.themes))]
        self.configure(bg=self.currentTheme.squareColor)

        # setup the grid layout manager
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)

        # init Event Handler
        self.eventHandler = EventHandler(self)

        # init home + info label
        self.displayedFrame = None
        self.getHome()

    # interface controller

    def getHome(self):
        home = Home(self, self.currentTheme, self.eventHandler)
        self.displayFrame(home)

    def getNewGameSettings(self):
        newGameSettings = NewGameSettings(
            self, self.currentTheme, self.eventHandler)
        self.displayFrame(newGameSettings)

    def getJoinGameSettings(self):
        joinGameSettings = JoinGameSettings(
            self, self.currentTheme, self.eventHandler)
        self.displayFrame(joinGameSettings)

    def getSettings(self):
        settings = Settings(
            self, self.currentTheme, self.eventHandler)
        self.displayFrame(settings)

    def displayFrame(self, frame):
        # destroy game view if there was a game
        if (self.game != None):
            self.boardView.destroy()
            self.gameStats.destroy()
            self.player1Stats.destroy()
            self.player2Stats.destroy()
        if(self.displayedFrame != None):
            self.displayedFrame.destroy()
        self.displayedFrame = frame
        self.displayedFrame.grid(
            row=0, column=0, columnspan=2, rowspan=3, sticky='')

    # game controller

    def getGameBoard(self, gameMode, isGameCreator, isGameWithAI, boardSize, timeLimit, isCaptureAuto, isBlownAuto, player1Name, player2Name):
        self.game = Game(gameMode, isGameWithAI, boardSize, timeLimit,
                         isCaptureAuto, isBlownAuto, player1Name, player2Name)

        self.player2Stats = PlayerStats(
            self, self.game.player2Name, '2', self.currentTheme.getPlayerColor('2'), timeLimit, self.eventHandler)
        self.player2Stats.grid(row=0, column=0)

        self.gameStats = GameStats(self)
        self.gameStats.grid(row=1, column=0)

        self.player1Stats = PlayerStats(
            self, self.game.player1Name, '1', self.currentTheme.getPlayerColor('1'), timeLimit, self.eventHandler)
        self.player1Stats.grid(row=2, column=0)

        self.boardView = BoardView(self, 800, gameMode,
                                   self.eventHandler, self.currentTheme)
        print('game created')

        if ('online' in gameMode):
            if(isGameCreator):
                self.game.isGamePaused = True
                self.serverConnection = ServerConnection(self, True, None)
            else:
                self.game.isPlayerTurn = False
                # setup player two turn as '2' ~forever for the match
                self.game.playerTurn = str(int(self.game.playerTurn) % 2 + 1)
            self.toggleIsPlayerTurn()
        else:
            self.gameStats.displayTurn(
                'Tour de ' + self.game.getPlayerName(self.game.playerTurn))

        self.displayedFrame.destroy()
        self.displayBoard(self.game.getBoardLayout())
        self.displayPlayerStats()
        self.toggleCountdowns(self.game.playerTurn)

    def displayBoard(self, layout):
        self.boardView.createBoardSquares(layout, self.game.playerTurn)
        self.boardView.grid(row=0, column=1, rowspan=3, padx=20, pady=20)

    def displayPlayerStats(self):
        self.player1Stats.setPieceCount(
            self.game.board.getPlayerPiecesCount('1'))
        self.player2Stats.setPieceCount(
            self.game.board.getPlayerPiecesCount('2'))

    def displayWinner(self, playerValue, isWinner):
        self.game.isGameOver = True

        if(isWinner):
            winnerPlayer = self.game.getPlayerName(playerValue)
        else:
            winnerPlayer = self.game.getPlayerName(
                str(int(playerValue) % 2 + 1))

        self.gameStats.displayInfo('Jeu terminé! Victoire à ' + winnerPlayer)
        messagebox.showinfo(
            'Game Over', 'Jeu terminé! Gagnant: ' + winnerPlayer)
        self.getHome()

    def toggleCountdowns(self, playerTurn):
        if(self.game.isTimeLimit and not self.game.isGamePaused):
            self.player1Stats.toggleCountdown(playerTurn)
            self.player2Stats.toggleCountdown(playerTurn)

    # toggle player turn for online game
    def toggleIsPlayerTurn(self):
        self.game.isPlayerTurn = not self.game.isPlayerTurn
        if(self.game.isPlayerTurn):
            self.gameStats.displayTurn('Votre tour')
        else:
            self.gameStats.displayTurn('Tour de l\'adversaire')

    # socket controller

    def onPlayerSocketConnected(self):
        if(self.serverConnection.isGameCreator):
            self.serverConnection.sendEvent('create-room')
        else:
            self.serverConnection.sendEvent('join-room')

    def onPlayerJoinRoom(self, roomId):
        self.serverConnection = ServerConnection(self, False, roomId)

    def onPlayer2JoinedRoom(self):
        self.serverConnection.sendEventData('setup-game', self.game.setups)
        self.game.isGamePaused = False

    # tkinter event controller

    def onPlayerPossibleMove(self, selectedPiece):
        if (not self.game.isGamePaused and self.game.isGameOver != True):
            self.displayBoard(
                self.game.board.getPieceMovesBoard(
                    selectedPiece, self.game.playerTurn, self.game.isPlayerTurn,
                    self.game.isCaptureMandatory,
                    self.game.mustCapture, self.game.lastMovedPiece))

    def onPlayerMove(self, move, isInitiator):

        # sending the move to other player as well for asynchronous validation
        if ('online' in self.game.gameType and isInitiator):
            self.serverConnection.sendEventData('move-player', move)

        moveResult = self.game.setPlayerMove(move)

        if ('gameover' in moveResult):
            self.displayWinner(self.game.board.getWinner(), True)
        elif('turnover' in moveResult):
            self.gameStats.displayInfo('')
            if ('online' in self.game.gameType):
                self.toggleIsPlayerTurn()
            else:
                self.game.playerTurn = str(int(self.game.playerTurn) % 2 + 1)
                self.gameStats.displayTurn(
                    'Tour de ' + self.game.getPlayerName(self.game.playerTurn))
        elif ('capture' in moveResult):
            if ('online' in self.game.gameType):
                if (self.game.isPlayerTurn):
                    self.gameStats.displayInfo(self.game.getPlayerName(
                        'Vous pouvez encore manger un pion'))
                else:
                    self.gameStats.displayInfo(self.game.getPlayerName(
                        'L\'adversaire peut encore manger un pion'))
            else:
                self.gameStats.displayInfo(self.game.getPlayerName(
                    self.game.playerTurn) + ' peut encore manger un pion')

        self.displayBoard(self.game.getBoardLayout())
        self.displayPlayerStats()
        self.toggleCountdowns(self.game.playerTurn)


# * application init
if __name__ == "__main__":

    # launching app
    app = App()

    # handling user close window
    app.protocol("WM_DELETE_WINDOW", app.eventHandler.onWindowClose)

    # firing endless loop
    app.mainloop()
