import numpy as np
import copy
import time

DBG = False

def log(s):
    if DBG:
        print(s)

def sudoku_rec(sudoku, history = None):
    for i in range(0, sudoku.shape[0]):
        for j in range(0, sudoku.shape[1]):
            if isinstance(sudoku[i,j], set):
                for val in sudoku[i,j]:
                    log("0 Playing {0} from ({1},{2})".format(val,i,j))
                    board_new, valid = update_permitted_states(sudoku, i, j, val)

                    if valid:
                        if is_solved(board_new):
                            return board_new, True
                        else:
                            hist_new=None
                            if history:
                                hist_new = copy.deepcopy(history)
                                hist_new.append("Playing {0} from ({1},{2})".format(val,i,j))
                                hist_new.append(board_new)

                            #for b in hist_new:
                            #    print("-------------")
                            #    print(b)
                            board_new, solved = sudoku_rec(board_new, history = hist_new)
                            if solved:
                                return board_new, True



    return np.full((9, 9), -1), False

def sudoku_solver(sudoku):
    if not is_valid(sudoku):
        return np.full((9, 9), -1)
    board = init_board(sudoku)

    if not is_solved(board, skipvalidate=False):
        #history = [board]
        return sudoku_rec(board, history=None)[0]
    else:
        log("Solved by init")
        return board
    log("Tried all options, no solution found")
    return np.full((9, 9), -1)


def is_solved(sudoku, skipvalidate=True):
    for row in sudoku:
        for col in row:
            if isinstance(col, set) or col == -1:
                return False
    if skipvalidate:
        return True
    else:
        return is_valid(sudoku)
    #return True


def is_valid(sudoku):
    # log(sudoku)
    for row in sudoku:
        seen = set()
        for col in row:
            if col > 0:
                if col in seen:
                    log("Row rule violated at {0}".format(row))
                    return False
                else:
                    seen.add(col)

    for col in sudoku.T:
        seen = set()
        for row in col:
            if row > 0:
                if row in seen:
                    log("Column rule violated at {0}".format(col))
                    return False
                else:
                    seen.add(row)

    for x in range(3):
        for y in range(3):
            seen = set()
            for i in range(3*x, 3*x+3):
                for j in range(3 * y, 3 * y + 3):
                    if sudoku[i,j] > 0:
                        if sudoku[i,j] in seen:
                            log("Quadrant rule violated at Q {0},{1}".format(x, y))
                            return False
                        else:
                            seen.add(sudoku[i,j])

    return True

def update_permitted_states(board, i, j, value):
    new_state = copy.deepcopy(board)
    new_state[i,j] = value

    second_step = []
    # update the row i
    for y in range(0, new_state.shape[1]):
        if isinstance(new_state[i,y], set):
            new_state[i,y].discard(value)
            if len(new_state[i,y]) == 1:
                # log("ilegal state 1")
                second_step.append((i,y, list(new_state[i,y])[0]))
            elif len(new_state[i,y]) == 0:
                # log("ilegal state 1")
                return new_state, False

    # update the column j
    for z in range(0, new_state.shape[0]):
        if isinstance(new_state[z,j], set):
            new_state[z,j].discard(value)
            if len(new_state[z,j]) == 1:
                second_step.append((z,j, list(new_state[z,j])[0]))
            elif len(new_state[z,j]) == 0:
                # log("ilegal state 2")
                return new_state, False

    # update the quadrant of (i,j)
    p = i // 3
    q = j // 3
    for x in range(3):
        for y in range(3):
            for qi in range(3*p, 3*p+3):
                for qj in range(3*q, 3*q + 3):
                    if isinstance(new_state[qi,qj], set):
                        new_state[qi,qj].discard(value)
                        if len(new_state[qi,qj]) == 1:
                            # log("ilegal state 3")
                            second_step.append((qi,qj,list(new_state[qi,qj])[0]))
                        elif len(new_state[qi,qj]) == 0:
                            # log("ilegal state 3")
                            return new_state, False

    for step_two in second_step:
        new_state, valid = update_permitted_states(new_state, step_two[0], step_two[1], step_two[2])
        if not valid:
            return new_state, False
    return new_state, True

def init_board(sudoku):
    board = np.array([{1,2,3,4,5,6,7,8,9} for _ in range(81)]).reshape(9,9)
    # log(sudoku)
    for i in range(0, board.shape[0]):
        for j in range(0, board.shape[1]):
            if sudoku[i,j] > 0:
                # log("Play ({0},{1}) = {2}".format(i,j,sudoku[i,j]))
                board, valid = update_permitted_states(board, i, j, sudoku[i,j])
                if not valid:
                    # log("Ilegal state reached 5")
                    return np.full((9, 9), -1)

    # log(board)

    for i in range(0, board.shape[0]):
        for j in range(0, board.shape[1]):
            if isinstance(board[i, j], set) and len(board[i, j]) == 1:
                board[i, j] = board[i, j].pop()

    # log(board)
    return board

