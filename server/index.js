// setup socket.io
const io = require('socket.io')(3000)

io.on('connection', socket => {
    console.log('someone got connected');

    // listen to custom event sent by socket
})