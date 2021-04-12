import tkinter as tk
from tkinter import messagebox

import socketio as socketio
import json as json

from data import Game, AIPlayer
from ihm import Home, GameSettings, BoardView, PlayerStats

from math import inf
from random import randrange
import time as time

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

#! Comprends pas à quoi ça sert ?

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
        self.app.renderWinner(player, False)

    # user interface events

    def onNewGameButton(self):
        self.app.getGameSettings()

    def onJoinRoomButton(self, roomId):
        self.app.onPlayerJoinRoom(roomId)

    def onSettingsButton(self):
        pass

    def onAboutButton(self):
        pass

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
            print('You in!')
            self.app.onPlayerSocketConnected()

        # player get disconnected from socket server
        @self.socket.on('disconnect')
        def onDisconnect():
            print('Oops, disconnected')

        # * room events

        @self.socket.on('room-create')
        def onRoomCreate(data):
            self.room = data
            print('Yay, you create your own room! Welcome to',
                  self.room)

        @self.socket.on('room-join')
        def onRoomJoin():
            print('Someone joined! Sending game data')
            self.app.onPlayer2JoinedRoom()

        # * game events

        #! Je comprends pas pourquoi @ et rien d'autres à part que c'est surement pour le serveur 

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
                messagebox.showerror(
                    'Erreur', 'Impossible de se connecter au serveur. Réessayez ultérieurement')
                self.socket = None

                #! Pour que ça envoie les données de jeu au serveur si oui lequels ? (def sendEvent etc)

    def sendEvent(self, eventName):
        self.socket.emit(eventName, self.room)

    def sendEventData(self, eventName, eventData):
        # send data as tuple, server will receive it as separate arguments
        self.socket.emit(eventName, (self.room, json.dumps(eventData)))


####################### APPLICATION MANAGER #######################
#! Je vais me servir de ça pour le site !
class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title('Damnier')
        self.minHeight = 800
        self.minWidth = int(self.minHeight * 1.5)
        self.minsize(width=self.minWidth, height=self.minHeight)

        # setup theme
        self.themes = [
            Theme('default', '#FFF', '#010101', '#FD0002',
                  '#010101', '#FFEB41', '#D9E0B0'),
            Theme('Space blue', '#E2F1F9', '#031D7B',
                  '#D1B9B5', '#FDDF83', '#FFEB41', '#D9E0B0'),
            Theme('Classic brown', '#F5DEB3', '#AC7D58',
                  '#000', '#FFF', '#FFEB41', '#D9E0B0')
        ]

        self.currentTheme = self.themes[randrange(0, len(self.themes))]

        # setup the grid layout manager
        #! Configurer la taille des colonnes et les lignes ?

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
    #! Pour que ça te ramène sur l'accueil ?

    def getHome(self):
        home = Home(self, self.eventHandler)
        self.renderFrame(home)

    def getGameSettings(self):
        gameSettings = GameSettings(self, self.eventHandler)
        self.renderFrame(gameSettings)

    #! C'est quoi renderFrame et GameSettings ? 

    def renderFrame(self, frame):
        if(self.displayedFrame != None):
            self.displayedFrame.destroy()
        self.displayedFrame = frame
        self.displayedFrame.grid(row=0, column=0, columnspan=3, sticky='')

    # game controller
    #! C'est pour l'interface du jeu ?

    def getGameBoard(self, gameMode, isGameCreator, isGameWithAI, boardSize, timeLimit, isCaptureAuto, isBlownAuto, player1Name, player2Name):
        self.game = Game(gameMode, isGameWithAI, boardSize, timeLimit, isCaptureAuto, isBlownAuto, player1Name, player2Name)

        self.player1Stats = PlayerStats(
            self, player1Name, '1', self.currentTheme.getPlayerColor('1'), timeLimit, self.eventHandler)
        self.player1Stats.grid(row=0, column=0)

        self.player2Stats = PlayerStats(
            self, player2Name, '2', self.currentTheme.getPlayerColor('2'), timeLimit, self.eventHandler)
        self.player2Stats.grid(row=0, column=2)

        self.boardView = BoardView(self, 800, gameMode,
                                   self.eventHandler, self.currentTheme)
        print('game created')

        if ('online' in gameMode):
            if(isGameCreator):
                self.game.isGamePaused = True
                self.game.isPlayerTurn = True
                self.serverConnection = ServerConnection(self, True, None)
            else:
                # setup player two turn as '2' ~forever for the match
                self.game.playerTurn = str(int(self.game.playerTurn) % 2 + 1)

        self.displayedFrame.destroy()
        self.renderBoard(self.game.getBoardLayout())
        self.renderPlayerStats()
        self.toggleCountdowns(self.game.playerTurn)

#!  C'est quoi renderBoard ?

    def renderBoard(self, layout):
        self.boardView.createBoardSquares(layout, self.game.playerTurn)
        self.boardView.grid(row=0, column=1)

#! C'est pour savoir le nombre de pièces qu'a les joueurs?

    def renderPlayerStats(self):
        self.player1Stats.setPieceCount(
            self.game.board.getPlayerPiecesCount('1'))
        self.player2Stats.setPieceCount(
            self.game.board.getPlayerPiecesCount('2'))

    def renderWinner(self, playerValue, isWinner):
        self.game.isGameOver = True

        if(isWinner):
            winnerPlayer = self.game.getPlayerName(playerValue)
        else:
            winnerPlayer = self.game.getPlayerName(
                str(int(playerValue) % 2 + 1))

        messagebox.showinfo(
            'Game Over', 'Jeu terminé! Gagnant: ' + winnerPlayer)

    def toggleCountdowns(self, playerTurn):
        if(self.game.isTimeLimit and not self.game.isGamePaused):
            self.player1Stats.toggleCountdown(playerTurn)
            self.player2Stats.toggleCountdown(playerTurn)

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
        print('isPlayerTurn', self.game.isPlayerTurn)
        if (not self.game.isGamePaused and self.game.isGameOver != True):
            self.renderBoard(
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
            self.renderWinner(self.game.board.getWinner(), True)
        elif('turnover' in moveResult):
            if ('online' in self.game.gameType):
                # toogle player turn
                self.game.isPlayerTurn = not self.game.isPlayerTurn
            else:
                self.game.playerTurn = str(int(self.game.playerTurn) % 2 + 1)

        self.renderBoard(self.game.getBoardLayout())
        self.renderPlayerStats()
        self.toggleCountdowns(self.game.playerTurn)


# * application init
if __name__ == "__main__":

    # launching app
    app = App()

    # firing endless loop
    app.mainloop()
    app.iconbitmap('/pion.ico')