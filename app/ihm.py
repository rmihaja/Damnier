import tkinter as tk
from typing import Text

# *** IHM

####################### TKINTER WIDGET OVERRIDE #######################

# * Text


class Label(tk.Label):

    def __init__(self, root, text):
        super().__init__(master=root, text=text, font='Arial 15')
        self.pack()


class Header(tk.Label):

    def __init__(self, root, text):
        super().__init__(master=root, text=text, font='Arial 30 bold')
        self.pack()

# * inputs


class InputText(tk.Entry):

    def __init__(self, root, defaultText):

        self.variable = tk.StringVar(value=defaultText)

        super().__init__(master=root, textvariable=self.variable)
        self.pack()

    def getValue(self):
        return self.variable.get()


class InputRadio(tk.Radiobutton):

    def __init__(self, root, optionsList):

        # define first option as default selected input
        self.variable = tk.StringVar(value=optionsList[0][1])

        for option in optionsList:
            optionText, optionValue = option
            super().__init__(master=root, text=optionText,
                             value=optionValue, variable=self.variable)
            self.pack()

    def getValue(self):
        return self.variable.get()


class InputCheckbox(tk.Checkbutton):

    def __init__(self, root, text):

        self.variable = tk.BooleanVar()

        super().__init__(master=root, text=text,
                         onvalue=True,
                         offvalue=False,
                         variable=self.variable)
        self.pack()

    def getValue(self):
        return self.variable.get()


class Button(tk.Button):

    def __init__(self, root, text, command):
        super().__init__(master=root, text=text, command=command)
        self.pack()


####################### TKINTER INTERFACE MANAGER #######################


class Home(tk.Frame):

    def __init__(self, root, eventHandler):

        # Home Frame value
        super().__init__(master=root)

        # element init
        Header(self, text='Damnier!')
        Button(self, text='Nouvelle partie',
               command=eventHandler.onNewGameButton)
        Button(self, text='Paramètres',
               command=eventHandler.onSettingsButton)
        Button(self, text='A propos', command=eventHandler.onAboutButton)


class GameSettings(tk.Frame):

    def __init__(self, root, eventHandler):
        super().__init__(master=root)
        Header(self, text='Nouvelle partie')

        Label(self, text='Votre pseudo')
        player1Name = InputText(self, 'Joueur 1')

        Label(self, text='Mode de jeu')
        gameMode = InputRadio(self, optionsList=[
            ('Local', 'local'), ('En ligne', 'multi')
        ])

        Label(self, text='Pseudo du joueur 2')
        player2Name = InputText(self, 'Joueur 2')
        isGameWithAI = InputCheckbox(
            self, text='Jouer contre l\'ordinateur')

        Label(self, text='Taille du damier')
        boardSize = InputRadio(self, optionsList=[
            ('8 x 8', '8'), ('10 x 10', '10'), ('12 x 12', '12')
        ])

        Label(self, text='Gestionnaire du temps')
        timeLimit = InputRadio(self, optionsList=[
            ('Illimité', '0'),
            ('10 secondes', '10'),
            ('3 minutes', '180'),
            ('5 minutes', '300'),
            ('10 minutes', '600')
        ])

        Label(self, text='Options')
        isCaptureAuto = InputCheckbox(
            self, text='Prise de plusieurs pions automatique')
        isBlownAuto = InputCheckbox(self, text='Pions soufflés')

        Button(self, text='Commencer',
               command=lambda:
                   eventHandler.onStartNewGameButton(
                       gameMode.getValue(),
                       isGameWithAI.getValue(),
                       boardSize.getValue(),
                       timeLimit.getValue(),
                       isCaptureAuto.getValue(),
                       isBlownAuto.getValue(),
                       player1Name.getValue(),
                       player2Name.getValue()))


####################### BOARD WIDGETS #######################


class Square(tk.Canvas):

    def __init__(self, root, size, color, row, column):
        # ? bd removes Canvas default margin
        super().__init__(master=root, width=size, height=size,
                         bg=color, bd=-2, highlightbackground=color)

        self.row = row
        self.column = column


class Piece():

    def __init__(self, squareParent, parentSize, value, color, selectedColor, eventHandler):
        # put selected color if piece was selected
        if ('\'' in value):
            self.shape = squareParent.create_oval(self.getPieceCorners(parentSize),
                                                  fill=selectedColor, outline='white', width=3)
        else:
            self.shape = squareParent.create_oval(self.getPieceCorners(parentSize),
                                                  fill=color, outline='white', width=3)

        # add queen overlay if piece is a queen
        if ('*' in value):
            squareParent.create_line(self.getCrownCorners(
                parentSize, (35, 65), (30, 40), (40, 45), 35), fill='white', width=3)

        # if there is eventHandler, piece belongs to player and is selectable
        if (eventHandler != None):
            self.color = color
            self.selectedColor = selectedColor
            # piece click event listener
            squareParent.tag_bind(self.shape, '<ButtonPress-1>',
                                  eventHandler.onPlayerSquareSelected)

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

    def __init__(self, root, size, squareColor, pieceValue, selectableColor, row, column, eventHandler):
        self.value = pieceValue

        # if there is '+' data, player can move to square and it is selectable
        if ('+' in pieceValue):
            super().__init__(root, size, selectableColor, row, column)
            self.bind("<ButtonPress-1>", eventHandler.onEmptySquareSelected)
        else:
            super().__init__(root, size, squareColor, row, column)


class OpponentSquare(Square):

    def __init__(self, root, size, squareColor, pieceValue, pieceColor, row, column):
        super().__init__(root, size, squareColor, row, column)
        self.piece = Piece(self, size, pieceValue, pieceColor, None, None)


class PlayerSquare(Square):

    def __init__(self, root, size, squareColor, pieceValue, pieceColor, selectedPieceColor, row, column, eventHandler):
        super().__init__(root, size, squareColor, row, column)
        self.piece = Piece(self, size, pieceValue,
                           pieceColor, selectedPieceColor, eventHandler)
        self.value = pieceValue


##########i1############# TKINTER BOARD MANAGER #######################


class Countdown(tk.Label):

    def __init__(self, root, name, initialCount, eventHandler):

        # ? set playerValue as countdown name for more versatile and independant component
        self.name = name
        self.root = root
        self.count = initialCount
        self.label = Label(root, text=self.getFormattedTime(self.count))
        self.eventHandler = eventHandler
        self.clock = self.root.after(0, lambda: print('clock initialized'))

        super().__init__(master=self.root)

    # count passed is in seconds
    def getFormattedTime(self, count):
        minutes, seconds = divmod(count, 60)
        return '{:02d}:{:02d}'.format(minutes, seconds)

    def start(self):
        self.isCountdownRunning = True
        self.run()

    def run(self):
        if(self.isCountdownRunning == True):
            self.count -= 1
            self.label.configure(text=self.getFormattedTime(self.count))
            if (self.count <= 0):
                self.stop()
                self.eventHandler.onplayerTimerOut(self.name)
            else:
                self.clock = self.root.after(1000, self.run)

    def stop(self):
        self.isCountdownRunning = False
        self.root.after_cancel(self.clock)


class PlayerStats(tk.Frame):

    def __init__(self, root, playerName, playerValue, playerColor, timeLimit, eventHandler):
        super().__init__(master=root)

        self.playerValue = playerValue

        if(timeLimit > 0):
            self.countdown = Countdown(
                self, playerValue, timeLimit, eventHandler)
        else:
            self.countdown = None

        Label(self, text=playerName)
        PlayerSquare(self, 75, None, '', playerColor,
                     None, 0, 0, None).pack()

        self.pieceCount = Label(self, text='')

    def setPieceCount(self, count):
        self.pieceCount.configure(text=count)

    def toggleCountdown(self, playerTurn):
        if (playerTurn in self.playerValue):
            self.countdown.start()
        else:
            self.countdown.stop()


class BoardView(tk.Frame):

    def __init__(self, root, length, gameMode, eventHandler, theme):

        # Board config
        self.length = length
        self.theme = theme
        super().__init__(master=root, height=self.length,
                         width=self.length, bg=self.theme.boardColor)

        # game state
        if('local' in gameMode):
            self.isLocalGame = True
        else:
            self.isLocalGame = False

        # event handler to pass to controller
        self.eventHandler = eventHandler

    def createBoardSquares(self, layout, playerValue):

        # board config
        self.boardSize = len(layout[0])
        self.squareSize = self.length / self.boardSize

        for row in range(self.boardSize):
            for column in range(self.boardSize):
                squareValue = layout[row][column]
                if (squareValue != ''):
                    square = self.createSquare(
                        playerValue, squareValue, row, column, self.eventHandler)

                    # flip layout filling if the player is player2 for first pov
                    if (self.isLocalGame == False and self.playerValue == '2'):
                        square.grid(row=self.boardSize - row,
                                    column=self.boardSize - column)
                    else:
                        square.grid(row=row, column=column)

    def createSquare(self, playerValue, pieceValue, rowPosition, columnPosition, eventHandler):
        if ('E' in pieceValue):
            return EmptySquare(self, self.squareSize,
                               self.theme.squareColor, pieceValue,
                               self.theme.selectedPieceColor,
                               rowPosition, columnPosition,
                               eventHandler)
        elif (playerValue in pieceValue):
            return PlayerSquare(self, self.squareSize,
                                self.theme.squareColor, pieceValue,
                                self.theme.getPlayerColor(pieceValue),
                                self.theme.selectedPieceColor,
                                rowPosition, columnPosition,
                                eventHandler)
        else:
            # square is automatically for the opponent
            return OpponentSquare(self, self.squareSize,
                                  self.theme.squareColor, pieceValue,
                                  self.theme.getPlayerColor(pieceValue),
                                  rowPosition, columnPosition)
