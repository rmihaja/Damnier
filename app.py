from tkinter import *

############### MODELE ###############

# *

############### VIEW ###############

# * variable init
BOARD_SIZE = 8  # ? american chekers has 8 rows and 8 columns
BOARD_LENGTH = 800
BOARD_COLOR = '#c1c1c1'
SQUARE_LENGTH = BOARD_LENGTH / BOARD_SIZE
SQUARE_COLOR = '#000'
PIECE_RADIUS = (0.95 * SQUARE_LENGTH) / 2
PLAYER_COLOR = "#DB380D"
OPPONENT_COLOR = BOARD_COLOR

# Tkinter init
root = Tk()
cnv = Canvas(root, width=BOARD_LENGTH,
             height=BOARD_LENGTH, background=BOARD_COLOR)

# render gui
cnv.pack()

# run tkinter
root.mainloop()
