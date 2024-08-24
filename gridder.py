import numpy
OFFBOARD = 7

def grid_generator(rows,columns):
    board = [[0 for x in range(columns)] for y in range(rows)]
    for i in range(rows):
        for j in range(columns):
            if i == rows-1 or j == columns-1: board[i][j] = OFFBOARD
    board = numpy.array(board,dtype=object).reshape(rows,columns)
    return board
