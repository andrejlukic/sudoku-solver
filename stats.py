from sudoku_solver import *
import time

DIFF = ['very_easy', 'easy', 'medium', 'hard']
ITERATIONS = 5

def print_results(results):
    for level in DIFF:
        for i in range(ITERATIONS):
                print(results[(i, level)])
                print(results[(i, "{}_total".format(level))])

def stats():
    results = {}
    for i in range(ITERATIONS):
        for level in DIFF:
            print(level)
            inx = 0
            results[(i, level)] = []
            sudokus = np.load(f"data/{level}_puzzle.npy")
            solutions = np.load(f"data/{level}_solution.npy")
            t_level1 = time.time()
            for puzzle, solution in zip(sudokus, solutions):
                t1 = time.time()
                solved = sudoku_solver(puzzle)
                t2 = time.time()
                results[(i, level)].append(t2-t1)
                assert (np.array_equal(solved, solution))
                inx+=1
            t_level2 = time.time()
            results[(i, "{}_total".format(level))] = t_level2 - t_level1
    return results


print(stats())
