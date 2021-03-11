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
                piece = '2';  // ? 1 = player2 : default opponent / guest
            } else if (row > (size / 2)) {
                piece = '1';  // ? 2 = player1 : default player / initiator
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
    getBoardLayout() {
        return JSON.stringify(this.layout);
    }

    movePiece(piece, initialRow, initialColumn, newRow, newColumn) {
        
        // swap square value
        this.layout[initialRow][initialColumn] = 'E';

        // add '*' queen tag to piece layout data if piece can be a queen
        let queenValue = this.canUpgradeQueen(piece, newRow);

        this.layout[newRow][newColumn] = piece + queenValue;
    }

    capturePiece(row, column) {
        // replace square value to empty
        this.layout[row][column] = 'E';
    }

    tryMovement(piecePosition, emptyPosition) {
        let pieceRow = piecePosition.row;
        let pieceColumn = piecePosition.column;
        let emptyRow = emptyPosition.row;
        let emptyColumn = emptyPosition.column;

        let piece = this.layout[pieceRow][pieceColumn];

        let deltaRow = emptyRow - pieceRow;
        let deltaColumn = emptyColumn - pieceColumn;

        // * simple move

        // move piece if empty square is qdjacent
        if (this.canMove(piece, deltaRow, deltaColumn)) {
            this.movePiece(piece, pieceRow, pieceColumn, emptyRow, emptyColumn);
            return 'move';
        }

        // * move and capture
         
        // get square in the middle of empty and piece
        let capturableSquare = this.getInBetweenSquare(pieceRow, pieceColumn, deltaRow, deltaColumn);
        // check if the square is not empty and belongs to opponent so it can be captured
        if (this.canCapture(capturableSquare.value, piece)) {
            this.capturePiece(capturableSquare.row, capturableSquare.column);
            // move piece if move captures opponent piece
            this.movePiece(piece, pieceRow, pieceColumn, emptyRow, emptyColumn);
            return 'capture';
        }

        // * invalid move

        return null;

    }

    getSquarePlayer(piecePosition) {
        let squareValue = this.layout[piecePosition.row][piecePosition.column];
        return squareValue.charAt(0);
    }

    getInBetweenSquare(pieceRow, pieceColumn, deltaRow, deltaColumn) {
        let square = {
            row: pieceRow + (1 * Math.sign(deltaRow)),
            column: pieceColumn + (1 * Math.sign(deltaColumn))
        }
        square.value = this.layout[square.row][square.column];
        console.log(`                   the potential square to eat is at (${square.row}, ${square.column}) with a value of ${square.value}`)
        return square;
    }

    canCapture(piece, playerPiece) {
        let pieceOwner = piece.charAt(0);
        let playerValue = playerPiece.charAt(0);
        
        return pieceOwner != 'E' && pieceOwner != playerValue;
    }

    canMultipleCapture(piecePosition) {
        console.log('\n################################ BEGINTEST ################################\n')
        let pieceRow = piecePosition.row;
        let pieceColumn = piecePosition.column;
        let piece = this.layout[pieceRow][pieceColumn];
        
        let testNumber = 0;

        for (let deltaRow = -2; deltaRow <= 2; deltaRow += 4) {
            for (let deltaColumn = -2; deltaColumn <= 2; deltaColumn += 4) {
                let row = pieceRow + deltaRow;
                let column = pieceColumn + deltaColumn;
                console.log(`   test${testNumber} - Offset by (${deltaColumn}, ${deltaRow}) from (${pieceRow},${pieceColumn})
                Potential move to Square (${row},${column})`)
                // check if offset square position does not exceed board size layout
                if ((0 <= row && row < this.size) && (0 <= column && column < this.size)) {
                    console.log(`                   Square has passed layout.size test`)
                    // check if square is empty to perform the movement
                    if (this.layout[row][column] == 'E') {
                        console.log(`                   Square has passed value == E test with value of ${this.layout[row][column]}`)
                        let capturableSquare = this.getInBetweenSquare(pieceRow, pieceColumn, deltaRow, deltaColumn);
                        if (this.canCapture(capturableSquare.value, piece)) {
                            console.log(`RESULT: player can move to (${row},${column}) while eating the piece at (${capturableSquare.row},${capturableSquare.column}) own by ${capturableSquare.value}` )
                            console.log(`~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n`);
                            return true;   
                        }
                    }    
                }
                testNumber++;
            }
        }

        console.log(`\nRESULT: All squares failed test. player cannot eat multiple time`);
        console.log(`~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n`);
        return false;
    }

    canUpgradeQueen(piece, row) {
        // check if piece is already a queen
        if (piece.includes('*')) {
            return '';
        }
        // check if player reached opposite row
        if ((piece.includes('1') && row == 0) || (piece.includes('2') && row == this.layout.length - 1)) {
             
            return '*';
        }
        else return ''
    }

    canMove(piece, deltaRow, deltaColumn) {
        
        // check if player move sideways
        if (Math.abs(deltaColumn) == 1) {
            // check if piece is queen, can move forward and backward
            if (piece.includes('*')) {
                return true;
            }
            if (piece.includes('1')) {
                // player1 have to move forward to the root
                return deltaRow == -1;
            } else if (piece.includes('2')) {
                // player2 have to move forward to the layout.size
                return deltaRow == 1;
            }
        }
    }
}