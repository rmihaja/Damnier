const Board = require('./board'); 

module.exports = class Game {

    constructor(size, initiator, guest) {
        this.board = new Board(size);
        this.turn = 0;
        this.players = [initiator, guest];
    }

    updatePlayersBoard() {
        for (let player of this.players) {
            player.emit('loadboard', this.board.getBoardLayout(player.value));
        }
    }

    incrementTurn() {
        this.players[this.turn % 2].emit('playerturn', JSON.stringify(true));
        this.players[(this.turn + 1) % 2].emit('playerturn', JSON.stringify(false))
        this.turn++;
    }

    onPlayerMove(movement) {
        let performedMovement = this.board.tryMovement(movement.piecePosition, movement.emptyPosition)
        if (performedMovement != null) {
            this.updatePlayersBoard();
            if (performedMovement == 'capture' && this.board.canMultipleCapture(movement.emptyPosition)) {
                // after capture, player piece is now positionned on previous empty
                let player = this.board.getSquarePlayer(movement.emptyPosition);
                this.players[parseInt(player) - 1].emit('captureopponent');
            }
            else this.incrementTurn();
        }

    }
}