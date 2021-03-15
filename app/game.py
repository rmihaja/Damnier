from data import Theme, InfoLabel
from ihm import Board
import socketio
import json

####################### APPLICATION MANAGER #######################


class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title('Damnier')
        self.geometry('800x820')
        self.resizable(0, 0)

        # setup the grid layout manager
        self.rowconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # setup turn management
        self.isPlayerTurn = False

        # display info label
        self.infoLabel = InfoLabel(self)
        self.infoLabel.grid(row=1, column=0)

    def setBoardProperty(self, playerValue):
        self.playerValue = playerValue
        self.theme = self.setTheme(self.playerValue)

    def renderBoard(self, layout):
        self.board = Board(self, layout, self.playerValue, self.theme)
        self.board.grid(row=0, column=0)

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

####################### SERVER CONNECTION MANAGER ######################


socket = socketio.Client()

# * event handlers

#  connection events


# player is connected to socket server
@socket.on('connect')
def onConnect():
    print('You in!')

# player get connected to socket server


@socket.on('disconnect')
def onDisconnect():
    print('Oops, disconnected')

#  game events


@socket.on('playersetup')
def onPlayerSetup(data):
    print('Congrats! You are player ' + str(json.loads(data)))
    global app
    app.setBoardProperty(json.loads(data))
    app.infoLabel.notify('En attente d\'un joueur potentiel')


@socket.on('loadboard')
def onLoadboard(data):
    global app
    app.renderBoard(json.loads(data))


@socket.on('playerturn')
def onPlayerTurn(data):
    global app
    app.setPlayerTurn(json.loads(data))


@socket.on('captureopponent')
def onCaptureOpponent():
    print('Gotta capture another piece to end your turn!')
    app.infoLabel.notify('C\'est votre tour! Vous pouvez encore mangez!')

####################### TKINTER EVENT MANAGER #######################


class EventHandler:

    selectedSquare = None
    selectedPiece = None

    @classmethod
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

    @classmethod
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
                print('Sending movement to server')
                socket.emit('move', json.dumps(movementProperty))


# * application init
if __name__ == "__main__":

    # launching app
    app = App()

    # TODO: Add server class
    # connecting to socket server
    try:
        socket.connect('http://localhost:5500')
    except Exception:
        try:
            print('No local server found, connecting to remote')
            socket.connect('https://damnier.herokuapp.com/')
        except Exception as error:
            print('Can\'t connect to remote server:', error)
            app.infoLabel.notify(
                'Erreur: Impossible de se connecter au serveur. Veuillez redémarrer')

    # firing endless loop
    app.mainloop()
