
// * heroku server config
let port = process.env.PORT;
// if working with remote server, port will have value
if (port == null || port == "") {
    // if not, set arbitrary port
    port = 5500;
}

// * socket.io config

const io = require('socket.io')(port);

io.on('connection', socket => {
    console.log(`Someone went in!`);
    
    socket.on('create-room', () => {
        roomId = generateId();
        console.log(`Room ${roomId} created for player`);
        socket.join(roomId);
        io.to(roomId).emit('room-create', roomId);
    });

    socket.on('join-room', roomId => {
        socket.join(roomId);
        console.log(`Someone joined room ${roomId}, alerting initiator to send game setup data`);
        socket.to(roomId).emit('room-join');
    });

    socket.on('setup-game', (roomId, data) => {
        console.log(`${roomId}: sending back setup data`);
        socket.to(roomId).emit('game-setup', data);
    });

    socket.on('move-player', (roomId, data) => {
        socket.to(roomId).emit('player-move', data);
    });

})

const generateId = () => {
    // generate unique id of base 16 of length 4  
    return Math.random().toString(16).substr(2, 4);
}