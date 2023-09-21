//function to grab the grid from the html
function readSudokuGrid(){
    var sudokuGrid = [];
    for(var row = 0; row<9; row++){
        sudokuRow = [];
        for (var col = 0; col<9; col++){
            var idString = row + "-" + col;
            var sudokuCell = document.getElementById(idString);
            if(!sudokuCell.value){
                var sudokuCellValue = 0;
            } else {
                var sudokuCellValue = parseInt(sudokuCell.value);
            };
            sudokuRow.push(sudokuCellValue);
        }
        sudokuGrid.push(sudokuRow);
    }
    return sudokuGrid;
}

//function to write the grid into the html
function writeSudokuGrid(sudokuGrid){
    for(var row = 0; row < sudokuGrid.length; row++){
        for(var col = 0; col < sudokuGrid[row].length; col++){
            let idString = row.toString() + "-" + col.toString();
            let sudokuCell = document.getElementById(idString);
            if(sudokuGrid[row][col] != 0){
                sudokuCell.value = sudokuGrid[row][col];
            } else{
                sudokuCell.value = null;
            }
            
        }
    }            
}

//Functions to solve the sudoku puzzle
//Function to find first value in grid equal to 0
function findNextEmptySquare(sudokuGrid){
    for(var row = 0; row < sudokuGrid.length; row++){
        for(var col = 0; col < sudokuGrid[row].length; col++){
            if(sudokuGrid[row][col] === 0){
                return [row, col];
            }
        }
    }
    //If no 0s found, return null
    return null;
}

//Function to check if the number is valid
function isValid(sudokuGrid, value, position) {
    //Check row
    for(let col = 0; col < sudokuGrid[position[0]].length; col++){
        if( sudokuGrid[position[0]][col] === value && position[1] != col){
            return false;
        }
    }

    //check column
    for (let row = 0; row < sudokuGrid.length; row++){
        if( sudokuGrid[row][position[1]] == value && position[1] != row){
            return false;
        }
    }

    //check box
    var boxRowStart = Math.floor(position[0]/3);
    var boxColStart = Math.floor(position[1]/3);

    for(let row = boxRowStart*3; row < 3*(boxRowStart+1); row++){
        for(let col = boxColStart*3; col< 3*(boxColStart+1); col++){
            if(sudokuGrid[row][col] == value && [row,col] != position){
                return false;
            }
        }
    }
    return true;
}   

function solvePuzzle(sudokuGrid){
    let nextEmptySquare = findNextEmptySquare(sudokuGrid);
    if(!nextEmptySquare){
        return true;
    } else{
        var row = nextEmptySquare[0]
        var col = nextEmptySquare[1]
    }

    for(var value = 1; value<10; value ++){
        if(isValid(sudokuGrid, value, nextEmptySquare)){
            sudokuGrid[row][col] = value;
            if(solvePuzzle(sudokuGrid)){
                return true;
            }
            sudokuGrid[row][col] = 0;
        }
    }
    return false;
}

var form = document.getElementById('upload-submit');
form.addEventListener('submit', function(event) {
    event.preventDefault();
    let sudokuGrid = readSudokuGrid();
    solvePuzzle(sudokuGrid);
    writeSudokuGrid(sudokuGrid);
});

window.onload = function(){
    let sudokuGrid = [[3, 0, 6, 5, 0, 8, 4, 0, 0],
    [5, 2, 0, 0, 0, 0, 0, 0, 0],
    [0, 8, 7, 0, 0, 0, 0, 3, 1],
    [0, 0, 3, 0, 1, 0, 0, 8, 0],
    [9, 0, 0, 8, 6, 3, 0, 0, 5],
    [0, 5, 0, 0, 9, 0, 6, 0, 0],
    [1, 3, 0, 0, 0, 0, 2, 5, 0],
    [0, 0, 0, 0, 0, 0, 0, 7, 4],
    [0, 0, 5, 2, 0, 6, 3, 0, 0]];

    writeSudokuGrid(sudokuGrid);
}