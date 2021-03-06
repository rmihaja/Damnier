const Board = require('./board'); 

// setup socket.io
const io = require('socket.io')(3000)

io.on('connection', socket => {
    console.log('someone got connected');

    // send board data to player
    // io.emit('board', new)

    // listen to custom event sent by socket
})

// board data

let board = new Board(8);
console.log(board.getBoardLayout(true));
console.log(Board)