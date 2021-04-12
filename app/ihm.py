import tkinter as tk

# *** IHM

####################### TKINTER WIDGET OVERRIDE #######################

# * Text


class Label(tk.Label):

    def __init__(self, root, text, row=0, column=0, rowspan=1, columnspan=1, pady=20):
        super().__init__(master=root, text=text, font='Helvetica 14')
        self.grid(row=row, column=column,
                  rowspan=rowspan, columnspan=columnspan, pady=(pady, 0))


class Header(tk.Label):

    def __init__(self, root, text, row=0, column=0, rowspan=1, columnspan=1):
        super().__init__(master=root, text=text, font='Helvetica 32 bold')
        self.grid(row=row, column=column,
                  rowspan=rowspan, columnspan=columnspan, pady=(25, 50))

# * inputs


class InputText(tk.Entry):

    def __init__(self, root, defaultText, row=0, column=0, rowspan=1, columnspan=1):

        self.variable = tk.StringVar(value=defaultText)

        super().__init__(master=root, textvariable=self.variable,
                         )
        self.grid(row=row, column=column,
                  rowspan=rowspan, columnspan=columnspan, padx=(20, 0), pady=10, ipadx=10, ipady=5)

    def getValue(self):
        return self.variable.get()


class InputRadio(tk.Radiobutton):

    def __init__(self, root, optionsList, theme, command=None, row=0, column=0, rowspan=1, columnspan=1):

        # define first option as default selected input
        self.variable = tk.StringVar(value=optionsList[0][1])

        for optionIndex in range(len(optionsList)):
            optionText, optionValue = optionsList[optionIndex]
            super().__init__(master=root, text=optionText,
                             command=command,
                             indicator=0,
                             value=optionValue, variable=self.variable)
            self.grid(row=row, column=optionIndex,
                      rowspan=rowspan, columnspan=columnspan)

    def getValue(self):
        return self.variable.get()


class InputCheckbox(tk.Checkbutton):

    def __init__(self, root, text, row=0, column=0, rowspan=1, columnspan=1):

        self.variable = tk.BooleanVar()

        super().__init__(master=root, text=text,
                         onvalue=True,
                         offvalue=False,
                         variable=self.variable)
        self.grid(row=row, column=column,
                  rowspan=rowspan, columnspan=columnspan)

    def getValue(self):
        return self.variable.get()


class Button(tk.Button):

    def __init__(self, root, text, command, theme, row=0, column=0, rowspan=1, columnspan=1):

        self.theme = theme
        super().__init__(master=root, text=text, command=command,
                         background=self.theme.squareColor, activebackground=self.theme.player1Color,
                         foreground=self.theme.textColor, activeforeground=self.theme.player2Color,
                         font='Helvetica 14', width=20, height=2)
        self.grid(row=row, column=column,
                  rowspan=rowspan, columnspan=columnspan, padx=20, pady=20)

        # add intern event listener for user on hover
        self.bind("<Enter>", self.onMouseEnter)
        self.bind("<Leave>", self.onMouseLeave)

    def onMouseEnter(self, event):
        self.configure(background=self.theme.selectedPieceColor,
                       foreground=self.theme.squareColor)

    def onMouseLeave(self, event):
        self.configure(background=self.theme.squareColor,
                       foreground=self.theme.textColor)


class InputRadioDiv(tk.Frame):

    def __init__(self, root, optionsList, theme, command=None, row=0, column=0, rowspan=1, columnspan=1):
        super().__init__(master=root)
        self.inputRadio = InputRadio(
            self, optionsList=optionsList, theme=theme, command=command)
        self.grid(row=row, column=column,
                  rowspan=rowspan, columnspan=columnspan)


class InputFormDiv(tk.Frame):

    def __init__(self, root, labelValue, inputDefaultValue, row=0, column=0, rowspan=1, columnspan=1):
        super().__init__(master=root)
        self.label = Label(self, text=labelValue,
                           column=0, pady=0)
        self.inputText = InputText(self, defaultText=inputDefaultValue,
                                   column=1)
        self.grid(row=row, column=column,
                  rowspan=rowspan, columnspan=columnspan, pady=(20, 0))


####################### TKINTER INTERFACE MANAGER #######################


class Home(tk.Frame):

    def __init__(self, root, theme, eventHandler):

        # Home Frame value
        super().__init__(master=root, padx=100)

        # element init
        Header(self, text='Damnier!')
        Button(self, text='Nouvelle partie',
               command=eventHandler.onNewGameButton, theme=theme,
               row=1)
        Button(self, text='Rejoindre une partie',
               command=eventHandler.onJoinGameButton, theme=theme,
               row=2)


class NewGameSettings(tk.Frame):

    def __init__(self, root, theme, eventHandler):
        super().__init__(master=root, padx=100)

        # data init
        gameModesOptions = [
            ('Local', 'local'), ('En ligne', 'online')
        ]

        boardSizesOptions = [
            ('8 x 8', '8'), ('10 x 10', '10')
        ]

        # time value count are converted in seconds
        timeLimitsOptions = [
            ('Illimité', '0'),
            ('3 minutes', '180'),
            ('5 minutes', '300'),
            ('10 minutes', '600')
        ]

        # element init

        Header(self, text='Nouvelle partie')

        self.player1Name = InputFormDiv(self, 'Votre pseudo:', 'Joueur 1',
                                        row=1).inputText

        Label(self, text='Mode de jeu',
              row=2)
        self.gameMode = InputRadioDiv(self, gameModesOptions, theme, command=self.onPlayerSelectGameModeOption,
                                      row=3).inputRadio

        self.player2Name = InputFormDiv(self, 'Pseudo du joueur 2:', 'Joueur 2',
                                        row=4).inputText

        self.isGameWithAI = InputCheckbox(
            self, text='Jouer contre l\'ordinateur',
            row=5)

        Label(self, text='Taille du damier',
              row=6)
        self.boardSize = InputRadioDiv(self, boardSizesOptions, theme,
                                       row=7).inputRadio

        Label(self, text='Gestionnaire du temps',
              row=8)
        self.timeLimit = InputRadioDiv(self, timeLimitsOptions, theme,
                                       row=9).inputRadio

        Label(self, text='Options',
              row=10)
        self.isCaptureAuto = InputCheckbox(
            self, text='Prise de plusieurs pions automatique',
            row=11)
        self.isBlownAuto = InputCheckbox(self, text='Pions soufflés',
                                         row=12)

        Button(self, text='Commencer', theme=theme,
               command=lambda:
                   eventHandler.onStartNewGameButton(
                       self.gameMode.getValue(),
                       self.isGameWithAI.getValue(),
                       self.boardSize.getValue(),
                       self.timeLimit.getValue(),
                       self.isCaptureAuto.getValue(),
                       self.isBlownAuto.getValue(),
                       self.player1Name.getValue(),
                       self.player2Name.getValue()),
                   row=13)

    # event that is only applicable to View
    def onPlayerSelectGameModeOption(self):
        if ('online' in self.gameMode.getValue()):
            self.isGameWithAI.variable.set(False)
            self.isGameWithAI.configure(state='disabled')
        else:
            self.isGameWithAI.configure(state='active')


class JoinGameSettings(tk.Frame):

    def __init__(self, root, theme, eventHandler):
        super().__init__(master=root, padx=100)
        Header(self, text='Rejoindre une partie',
               row=0, column=0)
        roomId = InputFormDiv(self, 'Code de la partie:',
                              '', row=1).inputText
        Button(self, text='Rejoindre',
               command=lambda: eventHandler.onJoinRoomButton(roomId.getValue()), theme=theme,
               row=2, column=0)

# TODO add settings


class Settings(tk.Frame):

    def __init__(self, root, theme, eventHandler):
        super().__init__(master=root, padx=100)
        Header(self, text='Paramètres',
               row=0, column=0)

        Label(self, text='Theme du jeu',
              row=1, column=0)

        InputCheckbox(self, text='Activer le son',
                      row=2, column=0)


####################### BOARD WIDGETS #######################


class Square(tk.Canvas):

    def __init__(self, root, size, color, row, column):
        # ? bd removes Canvas default margin
        super().__init__(master=root, width=size, height=size,
                         bg=color, border=-2, highlightbackground=color)

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
                parentSize, (0.35 * parentSize, 0.65 * parentSize), (0.3 * parentSize, 0.4 * parentSize), (0.4 * parentSize, 0.45 * parentSize), 0.35 * parentSize), fill='white', width=3)

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
        self.label = Label(root, text=self.getFormattedTime(
            self.count), columnspan=2)
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
        super().__init__(master=root, padx=50)

        self.playerValue = playerValue

        if(timeLimit > 0):
            self.countdown = Countdown(
                self, playerValue, timeLimit, eventHandler)
        else:
            self.countdown = None

        Label(self, text=playerName, row=1, columnspan=2)

        PlayerSquare(self, 75, None, '', playerColor,
                     None, 0, 0, None).grid(row=2, column=0)
        self.pieceCount = Label(self, text='', row=2, column=1, pady=0)

        self.infoLabel = Label(self, '', pady=0, row=3, columnspan=2)

    def setPieceCount(self, count):
        self.pieceCount.configure(text=count)

    def toggleCountdown(self, playerTurn):
        if (playerTurn in self.playerValue):
            self.countdown.start()
        else:
            self.countdown.stop()


class GameStats(tk.Frame):

    def __init__(self, root):
        super().__init__(master=root, padx=20, pady=10)

        self.turnLabel = Label(self, '', pady=0, row=0)
        self.infoLabel = Label(self, '', pady=0, row=1)

    def displayTurn(self, turn):
        self.turnLabel.configure(text=turn)

    def displayInfo(self, message):
        self.infoLabel.configure(text=message)


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
                    if (self.isLocalGame == False and playerValue == '2'):
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
