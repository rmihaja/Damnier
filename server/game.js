const Board = require('./board'); 

module.exports = class Game {

    constructor(size, initiator, guest) {
        this.board = new Board(size);
        this.player1 = {
            value: 1,
            socket: initiator,
        };
        this.player2 = {
            value: 2,
            socket: guest,
        };
        this.players = [this.player1, this.player2];
    }

    updatePlayersBoard() {
        for (let player of this.players) {
            console.log(player.value);
            player.socket.emit('loadboard', this.board.getBoardLayout(player.value));
        }
    }

    sendMessage(type, player, message) {
        let messageData = {
            type: type,
            message: message
        };
        player.socket.emit('message', JSON.stringify(messageData));
    }
}