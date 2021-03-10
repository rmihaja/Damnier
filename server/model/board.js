module.exports = class Board {
    
    // * constructor init
    constructor(size) {
        this.size = size;
        this.layout = this.createBoard(this.size);
    }

    createBoard(size) {
        let layout = [];
        for (let row = 0; row < size; row++) {
            let boardRow = [];
            let piece;
            // check if boardRow belongs to players
            if (row < (size / 2) - 1) {
                piece = 2;  // ? 1 = player2 : default opponent / guest
            } else if (row > (size / 2)) {
                piece = 1;  // ? 2 = player1 : default player / initiator
            } else {
                piece = 'E';  // ? E = empty : available square not occupied
            }
        
            
            // filling the row
            for (let column = 0; column < size; column++) {
                if ((row % 2 == 0 && column % 2 != 0) || (row % 2 != 0 && column % 2 == 0)) {
                    boardRow.push(piece);
                }
                else {
                    boardRow.push('');
                }
            }
            
            layout.push(boardRow);
        }
        return layout;
    }

    // return stringified array readable by python
    getBoardLayout(playerValue) {
        return JSON.stringify(this.layout);
    }

    // TODO : use this feature
    // flip the board horizontally for player as player2
    flipLayout(layout) {
        let flippedLayout = layout;
        for (let i = 0; i < flippedLayout.length; i++) {
            flippedLayout[i].reverse(); // ? reverse each row
        }
        return flippedLayout.reverse() // ? reverse column before return
    }

    movePiece(playerPiece, initialRow, initialColumn, newRow, newColumn) {
        
        // swap square value
        this.layout[initialRow][initialColumn] = 'E';
        this.layout[newRow][newColumn] = playerPiece;
    }

    tryMovement(author, piecePosition, emptyPosition) {
        let pieceRow = piecePosition.row;
        let pieceColumn = piecePosition.column;
        let emptyRow = emptyPosition.row;
        let emptyColumn = emptyPosition.column;

        let deltaRow = pieceRow - emptyRow;
        let deltaColumn = pieceColumn - emptyColumn;

        // move piece if empty square is qdjacent
        if (this.canMove(author, deltaRow, deltaColumn)) {
            this.movePiece(author, pieceRow, pieceColumn, emptyRow, emptyColumn);
            return true;
        } 
        
        if(this.canEat(deltaRow, deltaColumn)) {
            // delete opponent piece if author player can eat it
            let eatableSquareRow = pieceRow - 1 * Math.sign(deltaRow);
            let eatableSquareColumn = pieceColumn - 1 * Math.sign(deltaColumn);
            let eatableSquare = this.layout[eatableSquareRow][eatableSquareColumn];
            // check if the square is not empty and belongs to opponent so it can be eaten
            if (eatableSquare != 'E' && eatableSquare != author) {
                this.eatPiece(eatableSquareRow, eatableSquareColumn);
                this.movePiece(author, pieceRow, pieceColumn, emptyRow, emptyColumn);
                return true;
            }
        }

        return false;

    }

    canMove(player, deltaRow, deltaColumn) {
        // check if player move sideways
        if(Math.abs(deltaColumn) == 1) {
            if (player == 1) {
                // player1 have to move forward on the layout
                return deltaRow == 1;
            } else if (player == 2) {
                // console.log(deltaRow);
                // player2 have to move backward on the layout
                return deltaRow == -1;
            }
        }
    }

    canEat(deltaRow, deltaColumn) {
        return Math.abs(deltaRow) == 2 && Math.abs(deltaColumn) == 2;
    }

    eatPiece(row, column) {
        // replace square value to empty
        this.layout[row][column] = 'E';
    }
}