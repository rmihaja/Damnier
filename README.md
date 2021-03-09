# Damnier

Simple checkers game made with Python and Tkinter for my Python Project course.

## Installation

The player communications are made on top of [socket.io](https://socket.io/). It is the only dependency of both client and server.

Download [the project file](https://github.com/Rmihaja/Damnier/archive/main.zip) and open a terminal in the downloaded folder directory.

### Using the preconfigured remote server

A remote server has already been set up for the backend.

To launch the client, install socket.io dependency first :

```
pip install "python-socketio[client]"
```

Then run damnier.py (assuming you have a python environment on your machine) :

```
python damnier.py
```

Note : You will have to look for another player or run two windows of the app to be able to initiate the game and play.

### Using a local server

However if you want to run your own server, you will need [Node.js](https://nodejs.org/).

First install socket.io dependency with npm :

```
npm install
```

Then you can run the server :

```
node .
```

After that, run damnier.py with the command above. The app will connect to the local server instead of the remote one.
