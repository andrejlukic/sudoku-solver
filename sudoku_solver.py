import numpy as np
import copy
import time

DBG = False


def log(s):
    if DBG:
        print(s)


def sudoku_rec(sudoku, moves, next_move, history=None):
    if moves and len(moves) > next_move:
        set, i, j = moves[next_move]
        for val in set:
            if is_valid_move(sudoku, i, j, val):
                # valid_state, stack = update_moves(moves, i, j, val)
                # if valid_state:
                sudoku[i, j] = val
                sol, res = sudoku_rec(sudoku, moves, next_move + 1, history)
                if res:
                    return sol, True
                sudoku[i, j] = 0
                # revert_moves(moves, stack)
    else:
        if is_solved(sudoku):
            return sudoku, True

    return np.full((9, 9), -1), False


def sudoku_solver(sudoku):
    if not is_valid(sudoku):
        return np.full((9, 9), -1)

    board, moves = init_board(sudoku)

    return sudoku_rec(board, moves, 0, history=None)[0]


def is_solved(sudoku):
    for row in sudoku:
        for col in row:
            if col < 1:
                return False
    return is_valid(sudoku)


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
            for i in range(3 * x, 3 * x + 3):
                for j in range(3 * y, 3 * y + 3):
                    if sudoku[i, j] > 0:
                        if sudoku[i, j] in seen:
                            log("Quadrant rule violated at Q {0},{1}".format(x, y))
                            return False
                        else:
                            seen.add(sudoku[i, j])

    return True


def is_valid_move(sudoku, i, j, value):
    # check row
    if not all([value != sudoku[i][x] for x in range(9)]):
        return False
    # check column
    if not all([value != sudoku[x][j] for x in range(9)]):
        return False
    # check quadrant
    qi = 3 * (i // 3)
    qj = 3 * (j // 3)
    for x in range(qi, qi + 3):
        for y in range(qj, qj + 3):
            if sudoku[x][y] == value:
                return False
    return True


def update_permitted_states(board, i, j, value):
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


def init_board(sudoku):
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

    # log(board)

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


def update_moves(moves, x, y, value):
    p = x // 3
    q = y // 3
    stack = []
    for mset, i, j in moves:
        if (i != x or y != j) and (i == x or j == y
                                   or i in range(3 * p, 3 * p + 3)
                                   or j in range(3 * q, 3 * q + 3)) and value in mset:
            mset.discard(value)
            stack.append((value, i, j))
            if len(mset) == 0:
                # log("ilegal state 1")
                return False, stack
    # update the quadrant of (i,j)
    return True, stack


def revert_moves(moves, stack):
    for m, x, y in moves:
        for move, i, j in stack:
            if i == x and j == y:
                m.add(move)


if __name__ == "__main__":
    puzzle1 = np.array([[1, 0, 4, 3, 8, 2, 9, 5, 6],
                        [2, 0, 5, 4, 6, 7, 1, 3, 8],
                        [3, 8, 6, 9, 5, 1, 4, 0, 2],
                        [4, 6, 1, 5, 2, 3, 8, 9, 7],
                        [7, 3, 8, 1, 4, 9, 6, 2, 5],
                        [9, 5, 2, 8, 7, 6, 3, 1, 4],
                        [5, 2, 9, 6, 3, 4, 7, 8, 1],
                        [6, 0, 7, 2, 9, 8, 5, 4, 3],
                        [8, 4, 3, 0, 1, 5, 2, 6, 9]])

    # Load sudokus
    sudoku = np.load("data/very_easy_puzzle.npy")
    solutions = np.load("data/very_easy_solution.npy")

    difficulties = ['hard']
    for level in difficulties:
        print(level)
        sudokus = np.load(f"data/{level}_puzzle.npy")
        solutions = np.load(f"data/{level}_solution.npy")
        i = 0
        total_start = time.time()
        for puzzle, solution in zip(sudokus, solutions):
            i += 1
            # if i == 3:
            # print("Example {0}".format(puzzle))
            start = time.time()
            solversol = sudoku_solver(puzzle)
            end = time.time()
            if np.array_equal(solversol, solution):
                print("Success {0} in {1} secs".format(i, end - start))
            else:
                print("Fail")
                print("Example {0}".format(i))
                print("Example {0}".format(puzzle))
                print("Solution:")
                print(solution)
                print("Solver:")
                print(solversol)
        total_end = time.time()
        print(total_end - total_start)
