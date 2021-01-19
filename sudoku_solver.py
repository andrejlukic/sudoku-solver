import numpy as np
import copy
import time

def sudoku_solver(sudoku):
    '''Returns a solution to a Sudoku puzzle or an array of -1s if it cannot be solved'''

    if not is_valid(sudoku):
        return np.full((9, 9), -1)

    board, moves = init_board(sudoku)

    return dfs(board, moves, 0)[0]


def init_board(sudoku):
    '''Construct sets of allowed moves for missing values of Sudoku board

    The function takes a sudoku puzzle as an input and then iterates through
    all known values to remove any impossible values for the missing spaces.

    If a missing space ends up having only one possible solution then that
    value is considered a solution for that missing space
    '''

    # Construct sets of allowed moves for missing values
    board = np.array([{1, 2, 3, 4, 5, 6, 7, 8, 9} for _ in range(81)]).reshape(9, 9)
    # log(sudoku)
    for i in range(9):
        for j in range(9):
            if sudoku[i, j] > 0:
                # log("Play ({0},{1}) = {2}".format(i,j,sudoku[i,j]))
                board, valid, _ = update_permitted_states(board, i, j, sudoku[i, j])
                if not valid:
                    # log("Ilegal state reached 5")
                    return np.full((9, 9), -1), None

    # Single value solution is considered a solution for that missing space
    moves = []
    for i in range(9):
        for j in range(9):
            if isinstance(board[i, j], set):
                if len(board[i, j]) == 1:
                    board[i, j] = board[i, j].pop()
                else:
                    moves.append((board[i, j], i, j))
                    board[i, j] = 0
    return board, moves


def dfs(sudoku, moves, next_move):
    '''Depth-first search

    Performs a depth-first search using a list of allowed moves until it solves the Sudoku puzzle.

    sudoku: 9x9 numpy array representing Sudoku puzzle
    moves: a set of possible moves for each missing value
    next_move: index of current move
    '''

    if moves and len(moves) > next_move:
        set, i, j = moves[next_move]
        for val in set:
            if is_valid_move(sudoku, i, j, val):
                sudoku[i, j] = val
                sol, res = dfs(sudoku, moves, next_move + 1)
                if res:
                    return sol, True
                sudoku[i, j] = 0
    else:
        if is_solved(sudoku):
            return sudoku, True

    return np.full((9, 9), -1), False


def is_solved(sudoku):
    '''Verifies if all missing spaces have been filled and the resulting solution is valid'''

    for row in sudoku:
        for col in row:
            if col < 1:
                return False
    return is_valid(sudoku)


def is_valid(sudoku):
    '''Checks current state of puzzle for constraints for row, column and block'''

    # Verify row constraint
    for row in sudoku:
        seen = set()
        for col in row:
            if col > 0:
                if col in seen:
                    return False
                else:
                    seen.add(col)

    # Verify column constraint
    for col in sudoku.T:
        seen = set()
        for row in col:
            if row > 0:
                if row in seen:
                    return False
                else:
                    seen.add(row)

    # Verify block constraint
    for x in range(3):
        for y in range(3):
            seen = set()
            for i in range(3 * x, 3 * x + 3):
                for j in range(3 * y, 3 * y + 3):
                    if sudoku[i, j] > 0:
                        if sudoku[i, j] in seen:
                            return False
                        else:
                            seen.add(sudoku[i, j])

    # The current state violates no constraints
    return True


def is_valid_move(sudoku, i, j, value):
    '''Checks whether filling a missing space (i,j) with a value violates any constraints'''

    # check row constraint
    if not all([value != sudoku[i][x] for x in range(9)]):
        return False
    # check column constraint
    if not all([value != sudoku[x][j] for x in range(9)]):
        return False
    # check box constraint
    qi = 3 * (i // 3)
    qj = 3 * (j // 3)
    for x in range(qi, qi + 3):
        for y in range(qj, qj + 3):
            if sudoku[x][y] == value:
                return False
    # The move violates no constraints
    return True


def update_permitted_states(board, i, j, value):
    '''Constructs sets of possible moves for each missing space of the puzzle
    after a value has been placed to (i,j)'''

    # this is expensive so this is only done once at the beginning
    new_state = copy.deepcopy(board)
    new_state[i, j] = value

    second_step = set()
    unsolved = 0
    # update the row i
    for y in range(9):
        if isinstance(new_state[i, y], set):
            new_state[i, y].discard(value)
            unsolved += 1
            if len(new_state[i, y]) == 1:
                # log("ilegal state 1")
                unsolved -= 1
                second_step.add((i, y, list(new_state[i, y])[0]))
            elif len(new_state[i, y]) == 0:
                # log("ilegal state 1")
                return new_state, False, False

    # update the column j
    for z in range(9):
        if isinstance(new_state[z, j], set):
            new_state[z, j].discard(value)
            unsolved += 1
            if len(new_state[z, j]) == 1:
                unsolved -= 1
                second_step.add((z, j, list(new_state[z, j])[0]))
            elif len(new_state[z, j]) == 0:
                # log("ilegal state 2")
                return new_state, False, False

    # update the quadrant of (i,j)
    p = i // 3
    q = j // 3
    for x in range(3):
        for y in range(3):
            for qi in range(3 * p, 3 * p + 3):
                for qj in range(3 * q, 3 * q + 3):
                    if isinstance(new_state[qi, qj], set):
                        new_state[qi, qj].discard(value)
                        unsolved += 1
                        if len(new_state[qi, qj]) == 1:
                            # log("ilegal state 3")
                            unsolved -= 1
                            second_step.add((qi, qj, list(new_state[qi, qj])[0]))
                        elif len(new_state[qi, qj]) == 0:
                            # log("ilegal state 3")
                            return new_state, False, False

    for step_two in second_step:
        new_state, valid, _ = update_permitted_states(new_state, step_two[0], step_two[1], step_two[2])
        if not valid:
            return new_state, False, False
    return new_state, True, unsolved == 0
