from game import *
import tkinter as tk
import socketio
import json
from collections import namedtuple

############### SERVER CONNECTION MANAGER ###############

# *  connection setup

socket = socketio.Client()
# connect to socket server
socket.connect('http://localhost:5511')

# * event handlers


@socket.on('connect')
def onConnect():
    print('You in!')


@socket.on('disconnect')
def onDisconnect():
    print('Oops, disconnected')


@socket.on('playersetup')
def onPlayerSetup(data):
    print('Congrats! You are player ' + str(json.loads(data)))
    global app
    app.setBoardProperty(json.loads(data))


@socket.on('loadboard')
def onloadboard(data):
    print('Found someone else to play. Loading game!')
    global app
    app.renderBoard(json.loads(data))


# client server data communication

@socket.on('message')
def onmessage(data):
    # convert JSON data into object with attributes corresponding to dict keys
    message = json.loads(data, object_hook=lambda d: namedtuple(
        'message', d.keys())(*d.values()))
    print(message)
    print(message.type)


############### APPLICATION MANAGER MANAGER ###############


class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title('Damnier')
        self.geometry('800x800')

        # setup the grid layout manager
        self.rowconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def setBoardProperty(self, playerValue):
        self.playerValue = playerValue
        self.theme = self.setTheme(self.playerValue)

    def renderBoard(self, layout):
        print(layout)
        self.board = Board(self, layout, self.playerValue, self.theme)
        self.board.grid(row=0, column=0)

    # TODO : add custom theme
    def setTheme(self, playerValue):
        if (playerValue == 1):
            # player is player1 => red
            return Theme('#FD0002', '#010101', '#FD0002', '#010101', '#FFEB41')
        else:
            # player is player2 => black
            return Theme('#FD0002', '#010101', '#010101', '#FD0002', '#FFEB41')


# * application init


if __name__ == "__main__":
    app = App()
    app.mainloop()
