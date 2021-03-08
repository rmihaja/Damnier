module.exports = class Board {
    
    // * constructor init
    constructor(size) {
        this.size = size;
        this.layout = this.generateBoard(this.size);
    }

    generateBoard(size) {
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
        if(playerValue == 1)
        {
            return JSON.stringify(this.layout);
        }
        else {
            return JSON.stringify(this.layout);
        }
    }

    // flip the board horizontally for player as player2
    flipLayout(layout) {
        let flippedLayout = layout;
        for (let i = 0; i < flippedLayout.length; i++) {
            flippedLayout[i].reverse(); // ? reverse each row
        }
        return flippedLayout.reverse() // ? reverse column before return
    }

    movePiece(initiator, piecePosition, emptyPosition) {
        let xpiece = piecePosition.x;
        let ypiece = piecePosition.y;
        let xempty = emptyPosition.x;
        let yempty = emptyPosition.y;

        console.log(this.layout);
        // swap case value
        this.layout[xempty][yempty] = initiator;
        this.layout[xpiece][ypiece] = 'E';
        console.log(this.layout);
    }
}