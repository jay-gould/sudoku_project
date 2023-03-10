def print_grid(grid):
    for i in range(len(grid)):
        if i % 3 == 0 and i != 0:
            print("- - - - - - - - - - - - - ")

        for j in range(len(grid[0])):
            if j % 3 == 0 and j != 0:
                print(" | ", end="")

            if j == 8:
                print(grid[i][j])
            else:
                print(str(grid[i][j]) + " ", end="")

def find_next_empty_square(grid):
  #find first value in grid equal to 0
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == 0:
                return (i, j)  # row, col
   #if no 0's found, return none 
    return None

def valid(grid, value, position):
    # Check row
    for i in range(len(grid[0])):
        if grid[position[0]][i] == value and position[1] != i:
            return False

    # Check column
    for i in range(len(grid)):
        if grid[i][position[1]] == value and position[0] != i:
            return False

    # Check box
    box_x_start = position[1] // 3
    box_y_start = position[0] // 3

    for i in range(box_y_start*3, box_y_start*3 + 3):
        for j in range(box_x_start * 3, box_x_start*3 + 3):
            if grid[i][j] == value and (i,j) != position:
                return False

    return True

def solve(grid):
    find = find_next_empty_square(grid)
    if not find:
        return True
    else:
        row, col = find

    for i in range(1,10):
        if valid(grid, i, (row, col)):
            grid[row][col] = i

            if solve(grid):
                return True

            grid[row][col] = 0

    return False

"""
#input 9x9 sudoku grid (nested list) and output solution

example_grid = [[3, 0, 6, 5, 0, 8, 4, 0, 0],
                         [5, 2, 0, 0, 0, 0, 0, 0, 0],
                         [0, 8, 7, 0, 0, 0, 0, 3, 1],
                         [0, 0, 3, 0, 1, 0, 0, 8, 0],
                         [9, 0, 0, 8, 6, 3, 0, 0, 5],
                         [0, 5, 0, 0, 9, 0, 6, 0, 0],
                         [1, 3, 0, 0, 0, 0, 2, 5, 0],
                         [0, 0, 0, 0, 0, 0, 0, 7, 4],
                         [0, 0, 5, 2, 0, 6, 3, 0, 0]]

print("Unsolved Grid:")
print_grid(example_grid)
solve(example_grid)
print("Solved Grid:")
print_grid(example_grid)
"""
