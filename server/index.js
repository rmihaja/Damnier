const { Socket } = require('socket.io');
const Game = require('./model/game'); 

// * variable init 
let waitingRoom = [];
let game;

// * socket.io config

const io = require('socket.io')(5511);

io.on('connection', socket => {
    console.log(`Someone went in! There are now ${waitingRoom.length + 1} waiting`);
    
    // temporarely storing player socket while waiting for opponent
    waitingRoom.push(socket);

    // * event emitters

    // send player value if player'1' or '2'
    socket.emit('playersetup', JSON.stringify(waitingRoom.length))
    
    // initiate game when 2 player are connected
    if (waitingRoom.length == 2) {
        game = new Game(8, waitingRoom[0], waitingRoom[1]);
        waitingRoom = [];
        game.updatePlayersBoard();
        console.log('Game started !')
        console.log(`There are now ${waitingRoom.length} waiting`)
        game.incrementTurn();
    }

    // * event handlers

    // player plays a movement
    socket.on('move', data => {
        game.onPlayerMove(JSON.parse(data));
        game.updatePlayersBoard();
        game.incrementTurn();
    });
})
