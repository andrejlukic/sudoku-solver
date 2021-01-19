import pytest
from sudoku_solver import *


def test_sudoku_solver():
    # test valid puzzle state
    puzzle1 = np.array([[1, 0, 4, 3, 8, 2, 9, 5, 6],
                         [2, 0, 5, 4, 6, 7, 1, 3, 8],
                         [3, 8, 6, 9, 5, 1, 4, 0, 2],
                         [4, 6, 1, 5, 2, 3, 8, 9, 7],
                         [7, 3, 8, 1, 4, 9, 6, 2, 5],
                         [9, 5, 2, 8, 7, 6, 3, 1, 4],
                         [5, 2, 9, 6, 3, 4, 7, 8, 1],
                         [6, 0, 7, 2, 9, 8, 5, 4, 3],
                         [8, 4, 3, 0, 1, 5, 2, 6, 9]])
    assert(is_valid(puzzle1) == True)

    # test row no.3 violation puzzle state
    puzzle2 = np.array([[1, 0, 4, 3, 8, 2, 9, 5, 6],
                        [2, 0, 5, 4, 6, 7, 1, 3, 8],
                        [3, 8, 6, 9, 5, 1, 4, 0, 2],
                        [4, 6, 4, 5, 2, 3, 8, 9, 7],
                        [7, 3, 8, 1, 4, 9, 6, 2, 5],
                        [9, 5, 2, 8, 7, 6, 3, 1, 4],
                        [5, 2, 9, 6, 3, 4, 7, 8, 1],
                        [6, 0, 7, 2, 9, 8, 5, 4, 3],
                        [8, 4, 3, 0, 1, 5, 2, 6, 9]])
    assert (is_valid(puzzle2) == False)

    # test col no.1 violation puzzle state
    puzzle3 = np.array([[1, 0, 4, 3, 8, 2, 9, 5, 6],
                        [2, 0, 5, 4, 6, 7, 1, 3, 8],
                        [3, 8, 6, 9, 5, 1, 4, 0, 2],
                        [4, 6, 1, 5, 2, 3, 8, 9, 7],
                        [7, 3, 8, 1, 4, 9, 6, 2, 5],
                        [9, 5, 2, 8, 7, 6, 3, 1, 4],
                        [9, 2, 9, 6, 3, 4, 7, 8, 1],
                        [6, 0, 7, 2, 9, 8, 5, 4, 3],
                        [8, 4, 3, 0, 1, 5, 2, 6, 9]])
    assert (is_valid(puzzle3) == False)

    # test quadrant 5 violation puzzle state
    puzzle4 = np.array([[1, 0, 4, 3, 8, 2, 9, 5, 6],
                        [2, 0, 5, 4, 6, 7, 1, 3, 8],
                        [3, 8, 6, 9, 5, 1, 4, 0, 2],
                        [4, 6, 1, 5, 2, 3, 8, 9, 7],
                        [7, 3, 8, 1, 4, 9, 6, 2, 5],
                        [9, 5, 2, 8, 7, 5, 3, 1, 4],
                        [5, 2, 9, 6, 3, 4, 7, 8, 1],
                        [6, 0, 7, 2, 9, 8, 5, 4, 3],
                        [8, 4, 3, 0, 1, 5, 2, 6, 9]])
    assert (is_valid(puzzle4) == False)


    assert ((init_board(puzzle1)[0] == np.array([[1, 7, 4, 3, 8, 2, 9, 5, 6],
                                            [2, 9, 5, 4, 6, 7, 1, 3, 8],
                                            [3, 8, 6, 9, 5, 1, 4, 7, 2],
                                            [4, 6, 1, 5, 2, 3, 8, 9, 7],
                                            [7, 3, 8, 1, 4, 9, 6, 2, 5],
                                            [9, 5, 2, 8, 7, 6, 3, 1, 4],
                                            [5, 2, 9, 6, 3, 4, 7, 8, 1],
                                            [6, 1, 7, 2, 9, 8, 5, 4, 3],
                                            [8, 4, 3, 7, 1, 5, 2, 6, 9]])).all())



def test_sudoku_puzzle_files():
    # difficulties = ['very_easy', 'easy', 'medium', 'hard']
    difficulties = ['very_easy', 'easy', 'medium', 'hard']
    for level in difficulties:
        print(level)
        sudokus = np.load(f"data/{level}_puzzle.npy")
        solutions = np.load(f"data/{level}_solution.npy")
        for puzzle, solution in zip(sudokus, solutions):
            assert (np.array_equal(sudoku_solver(puzzle), solution))

