# Sudoku solver

## Introduction

The goal of this work is finding an efficient way to solve a Sudoku puzzle. 

Sudoku (数独, sūdoku, digit-single) (/suːˈdoʊkuː/, /-ˈdɒk-/, /sə-/, originally called Number Place) is a logic-based, combinatorial number-placement puzzle. In classic sudoku, the objective is to fill a 9×9 grid with digits so that each column, each row, and each of the nine 3×3 subgrids that compose the grid (also called "boxes", "blocks", or "regions") contain all of the digits from 1 to 9. The puzzle setter provides a partially completed grid, which for a well-posed puzzle has a single solution. -- <cite> Wikipedia [1] </cite>

Since a Sudoku puzzle starts with having one or multiple empty places, each with multiple possible options, this problem can be though of as a constraint satisfaction problem. In a constraint satisfaction problem there are multiple variables with a number of possible values and certain constraints (e.g. in the case of Sudoku a value cannot be repeated in the same row, column or a block). The rest of this document will explain the details of the backtracking approach used to solve Sudoku puzzles.

## Method

Several iterations of the algorithm were implemented and the final approach is a classic backtracking approach with the following key points:

### Algorithm steps
1. A puzzle is initially checked for validity. If it cannot be solved the execution is stopped and an array of -1s is returned
2. All empty spaces are considered and for each of the missing values a set of allowed moves is constructed based on initial state and Sudoku constraints. This greatly reduces the branching factor of the search. If all missing values end up having only a single possible value, the puzzle is considered solved.
3. If the initial step does not solve the puzzle a depth first search is performed. In each step of the recursive search allowed values are not recalculated. In this implementation it has been measured that updating sets of possible values only at the beginning of the search is a faster solution despite having to verify more states.
4. When a solution is found the solved array is returned. If all options have been exhausted a puzzle is considered unsolvable and an array of -1s is returned

### Important functions
A top method is called sudoku_solver:

```{python}
def sudoku_solver(sudoku):
    if not is_valid(sudoku):
        return np.full((9, 9), -1)

    board, moves = init_board(sudoku)

    return dfs(board, moves, 0)[0]
```

 It performs the three steps required to solve the puzzle. First it takes care of validating the initial puzzle by applying Sudoku row, column and block rules. A puzzle must be valid otherwise it cannot be solved. 
 
 In the next step the constraint is applied to remove impossible values for the missing places. This is done by the init_board function. It iterates through given values of the puzzle and applying Sudoku constraints constructs sets of allowed values in the missing spaces. In the last step it solves all those missing spaces that ended up having only one possible value:

 ```{python}
def init_board(sudoku):    

    # Construct sets of allowed moves for all missing values
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
```

This initial step is enough to solve many easy puzzles. For the more difficult puzzles a depth-first search is performed to either reach a solution or determine the puzzle is unsolvable. This is performed in a function called dfs. It has three input variables, the first one is simply a sudoku board, the second one is called moves and holds a set of possible moves for each missing value. The third variable is called next_move contains current index of the move.

```{python}
def dfs(sudoku, moves, next_move):
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

```

The functions is_solved, is_valid and is_valid_move are helper functions that check the state of the puzzle for the Sudoku row, column and box constraints. In the case of is_solved it also verifies that all missing places have been filled and the puzzle is considered solved.


```{python}
def is_valid_move(sudoku, i, j, value):
    '''Checks whether filling a missing space (i,j) with a value violates any constraints'''

    # Check row constraint
    if not all([value != sudoku[i][x] for x in range(9)]):
        return False

    # Check column constraint
    if not all([value != sudoku[x][j] for x in range(9)]):
        return False

    # Check box constraint
    qi = 3 * (i // 3)
    qj = 3 * (j // 3)
    for x in range(qi, qi + 3):
        for y in range(qj, qj + 3):
            if sudoku[x][y] == value:
                return False

    # The move violates no constraints
    return True
```

An important helper function is update_permitted_states. It is only run at the beginning and replaces a missing value with a set of values that are allowed wrt initial state of the puzzle. This function contains an time expensive deep_copy operation which in this case is acceptable since this function is only called at the beginning and not in the depth-first search:

```{python}
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
```

## Results
Final results of the algorithm were measured by repeating the solving of each puzzle 5 times. The resulting table is showing times required to solve the puzzle (seconds). In the first table averages of 5 iterations are displayed:

### Average times
*All results are in seconds
| Puzzle | Very easy   | Easy        | Medium      | Hard        |
|--------|-------------|-------------|-------------|-------------|
| AVG    | 0,04250569  | 0,031753387 | 0,034133975 | 4,332656066 |
| SUM    | 0,637585354 | 0,476300812 | 0,512009621 | 64,98984098 |
| MIN    | 0,039989805 | 3,04222E-05 | 0,016095972 | 0,122862244 |
| MAX    | 0,047394753 | 0,043902636 | 0,040746737 | 19,78553014 |

The overall average time to solve a puzzle is 1.1 second. 

### Individual puzzles
The biggest variance can be observed in the hardest category where the puzzles 2 and 15 took more than 10 seconds to solve. In total 8 hard puzzles took more than 2 seconds to solve. On the other hand no puzzle in the first three categories took more than 45ms to solve.

| Puzzle | Very easy   | Easy        | Medium      | Hard        |
|--------|-------------|-------------|-------------|-------------|
| 1      | 0,044420052 | 3,04222E-05 | 0,026324558 | 1,629175234 |
| 2      | 0,042080832 | 0,040505362 | 0,016095972 | 19,78553014 |
| 3      | 0,041429186 | 0,000143862 | 0,02790122  | 4,851768541 |
| 4      | 0,039989805 | 0,000141239 | 0,028316164 | 0,622752905 |
| 5      | 0,042485332 | 0,01564889  | 0,036509943 | 2,983942652 |
| 6      | 0,044990969 | 0,041837168 | 0,037923098 | 0,605688381 |
| 7      | 0,044706011 | 0,041808033 | 0,040633726 | 0,471854782 |
| 8      | 0,042393398 | 0,040682173 | 0,038282108 | 0,130409002 |
| 9      | 0,044150209 | 0,041670322 | 0,036317587 | 2,783601332 |
| 10     | 0,040650749 | 0,042778778 | 0,037239408 | 2,197908974 |
| 11     | 0,042076015 | 0,042113113 | 0,038533401 | 8,063878679 |
| 12     | 0,043898535 | 0,041458941 | 0,037240744 | 0,503060579 |
| 13     | 0,040875626 | 0,041095638 | 0,03579936  | 6,519384527 |
| 14     | 0,042476559 | 0,042484236 | 0,038929892 | 0,122862244 |
| 15     | 0,040962076 | 0,043902636 | 0,035962439 | 13,71802301 |


### Individual measurements

For transparency purposes all of the measurements are included here:

| Puzzle | Very easy   | Very easy   | Very easy   | Very easy   | Very easy   | AVG         |
|--------|-------------|-------------|-------------|-------------|-------------|-------------|
| 1      | 0,048888206 | 0,04253912  | 0,043534994 | 0,043696165 | 0,043441772 | 0,044420052 |
| 2      | 0,045021057 | 0,04117322  | 0,041471958 | 0,041343927 | 0,041393995 | 0,042080832 |
| 3      | 0,043449163 | 0,04088378  | 0,041128874 | 0,040920019 | 0,040764093 | 0,041429186 |
| 4      | 0,040414095 | 0,039908886 | 0,040071011 | 0,03981185  | 0,039743185 | 0,039989805 |
| 5      | 0,04207468  | 0,042495012 | 0,042382002 | 0,042437077 | 0,043037891 | 0,042485332 |
| 6      | 0,041954994 | 0,042145967 | 0,042264938 | 0,042608023 | 0,055980921 | 0,044990969 |
| 7      | 0,042302132 | 0,042274952 | 0,042877913 | 0,043937922 | 0,052137136 | 0,044706011 |
| 8      | 0,043148041 | 0,041512966 | 0,041919947 | 0,04203105  | 0,043354988 | 0,042393398 |
| 9      | 0,044039965 | 0,043994904 | 0,043515205 | 0,044334888 | 0,044866085 | 0,044150209 |
| 10     | 0,04042697  | 0,040540934 | 0,040682793 | 0,040642023 | 0,040961027 | 0,040650749 |
| 11     | 0,041842937 | 0,042056799 | 0,04162097  | 0,042519093 | 0,042340279 | 0,042076015 |
| 12     | 0,043903828 | 0,043894053 | 0,043774843 | 0,043838978 | 0,044080973 | 0,043898535 |
| 13     | 0,040874004 | 0,040917158 | 0,040560961 | 0,040853024 | 0,041172981 | 0,040875626 |
| 14     | 0,042379856 | 0,042311192 | 0,042492867 | 0,042481899 | 0,04271698  | 0,042476559 |
| 15     | 0,041013956 | 0,040778875 | 0,040941715 | 0,04104495  | 0,041030884 | 0,040962076 |
| SUM    | 0,641733885 | 0,627427816 | 0,62924099  | 0,632500887 | 0,657023191 | 0,637585354 |
| AVG    | 0,042782259 | 0,041828521 | 0,041949399 | 0,042166726 | 0,043801546 | 0,04250569  |
| MIN    | 0,040414095 | 0,039908886 | 0,040071011 | 0,03981185  | 0,039743185 | 0,039989805 |
| MAX    | 0,048888206 | 0,043994904 | 0,043774843 | 0,044334888 | 0,055980921 | 0,047394753 |

| Puzzle | Easy        | Easy        | Easy        | Easy        | Easy        | AVG         |
|--------|-------------|-------------|-------------|-------------|-------------|-------------|
| 1      | 3,58E-05    | 2,81E-05    | 2,79E-05    | 3,22E-05    | 2,81E-05    | 3,04222E-05 |
| 2      | 0,039696932 | 0,040373087 | 0,040261984 | 0,041937828 | 0,040256977 | 0,040505362 |
| 3      | 0,000141859 | 0,000142813 | 0,000144958 | 0,000146866 | 0,000142813 | 0,000143862 |
| 4      | 0,000138283 | 0,000140905 | 0,000142813 | 0,000144243 | 0,000139952 | 0,000141239 |
| 5      | 0,015302896 | 0,015571833 | 0,015592813 | 0,016217947 | 0,015558958 | 0,01564889  |
| 6      | 0,041229963 | 0,041975021 | 0,041940928 | 0,042165995 | 0,041873932 | 0,041837168 |
| 7      | 0,041754723 | 0,041755676 | 0,041871071 | 0,041952848 | 0,041705847 | 0,041808033 |
| 8      | 0,040555954 | 0,04076004  | 0,040697813 | 0,040693998 | 0,040703058 | 0,040682173 |
| 9      | 0,041231871 | 0,041526794 | 0,041585922 | 0,04227519  | 0,041731834 | 0,041670322 |
| 10     | 0,042807102 | 0,042239904 | 0,04299593  | 0,042919874 | 0,04293108  | 0,042778778 |
| 11     | 0,04162097  | 0,041981936 | 0,042041063 | 0,042730808 | 0,04219079  | 0,042113113 |
| 12     | 0,040961027 | 0,041545868 | 0,041420937 | 0,041732788 | 0,041634083 | 0,041458941 |
| 13     | 0,040496111 | 0,040967941 | 0,041027069 | 0,041995049 | 0,040992022 | 0,041095638 |
| 14     | 0,041889906 | 0,042585135 | 0,042577267 | 0,04262805  | 0,042740822 | 0,042484236 |
| 15     | 0,045571804 | 0,04334116  | 0,04349494  | 0,043456078 | 0,043649197 | 0,043902636 |
| SUM    | 0,473435163 | 0,474936247 | 0,475823402 | 0,481029749 | 0,476279497 | 0,476300812 |
| AVG    | 0,031562344 | 0,031662416 | 0,03172156  | 0,03206865  | 0,031751966 | 0,031753387 |
| MIN    | 3,57628E-05 | 2,81334E-05 | 2,7895E-05  | 3,21865E-05 | 2,81334E-05 | 3,04222E-05 |
| MAX    | 0,045571804 | 0,04334116  | 0,04349494  | 0,043456078 | 0,043649197 | 0,043902636 |

| Puzzle | Medium      | Medium      | Medium      | Medium      | Medium      | AVG         |
|--------|-------------|-------------|-------------|-------------|-------------|-------------|
| 1      | 0,026784897 | 0,025964022 | 0,025983334 | 0,026913881 | 0,025976658 | 0,026324558 |
| 2      | 0,015975237 | 0,015943766 | 0,015916824 | 0,016732216 | 0,015911818 | 0,016095972 |
| 3      | 0,02764082  | 0,027800083 | 0,027929068 | 0,028223991 | 0,02791214  | 0,02790122  |
| 4      | 0,027982235 | 0,028357267 | 0,028419018 | 0,028424263 | 0,028398037 | 0,028316164 |
| 5      | 0,036133289 | 0,036484003 | 0,036659241 | 0,03669095  | 0,036582232 | 0,036509943 |
| 6      | 0,039218903 | 0,03777194  | 0,037501812 | 0,037714958 | 0,037407875 | 0,037923098 |
| 7      | 0,042657137 | 0,039045095 | 0,038667202 | 0,038623095 | 0,044176102 | 0,040633726 |
| 8      | 0,037521839 | 0,037354946 | 0,038465977 | 0,038043022 | 0,040024757 | 0,038282108 |
| 9      | 0,035905838 | 0,035822153 | 0,036399126 | 0,036391973 | 0,037068844 | 0,036317587 |
| 10     | 0,037273884 | 0,036855698 | 0,037638187 | 0,037041187 | 0,037388086 | 0,037239408 |
| 11     | 0,038465977 | 0,038504839 | 0,038493872 | 0,038550138 | 0,038652182 | 0,038533401 |
| 12     | 0,037137747 | 0,037044048 | 0,03715682  | 0,037015915 | 0,037849188 | 0,037240744 |
| 13     | 0,035681963 | 0,035691977 | 0,035804033 | 0,035649776 | 0,036169052 | 0,03579936  |
| 14     | 0,038885832 | 0,038865089 | 0,03901124  | 0,038844109 | 0,039043188 | 0,038929892 |
| 15     | 0,035953045 | 0,035932779 | 0,036088943 | 0,035911322 | 0,035926104 | 0,035962439 |
| SUM    | 0,513218641 | 0,507437706 | 0,510134697 | 0,510770798 | 0,518486261 | 0,512009621 |
| AVG    | 0,034214576 | 0,03382918  | 0,03400898  | 0,034051387 | 0,034565751 | 0,034133975 |
| MIN    | 0,015975237 | 0,015943766 | 0,015916824 | 0,016732216 | 0,015911818 | 0,016095972 |
| MAX    | 0,042657137 | 0,039045095 | 0,03901124  | 0,038844109 | 0,044176102 | 0,040746737 |

| Puzzle | Hard        | Hard        | Hard        | Hard        | Hard        | AVG         |
|--------|-------------|-------------|-------------|-------------|-------------|-------------|
| 1      | 1,624381304 | 1,617240191 | 1,64294982  | 1,630486965 | 1,63081789  | 1,629175234 |
| 2      | 19,74583602 | 19,7254858  | 19,79040003 | 19,81360507 | 19,85232377 | 19,78553014 |
| 3      | 4,796211958 | 4,870120049 | 4,859557867 | 4,854656935 | 4,878295898 | 4,851768541 |
| 4      | 0,618426323 | 0,625224829 | 0,627216101 | 0,62144804  | 0,621449232 | 0,622752905 |
| 5      | 2,978605986 | 2,97266531  | 2,98410511  | 2,997309923 | 2,98702693  | 2,983942652 |
| 6      | 0,59912014  | 0,602492809 | 0,607396841 | 0,606023073 | 0,613409042 | 0,605688381 |
| 7      | 0,469991207 | 0,470411062 | 0,472069025 | 0,475340605 | 0,471462011 | 0,471854782 |
| 8      | 0,144898176 | 0,126060963 | 0,12706089  | 0,127909899 | 0,126115084 | 0,130409002 |
| 9      | 2,755866289 | 2,776688814 | 2,793885946 | 2,788400888 | 2,803164721 | 2,783601332 |
| 10     | 2,169946194 | 2,187305927 | 2,197039843 | 2,200797796 | 2,234455109 | 2,197908974 |
| 11     | 7,986277103 | 8,040416718 | 8,051577806 | 8,168320894 | 8,072800875 | 8,063878679 |
| 12     | 0,500502825 | 0,499968052 | 0,507086039 | 0,503600121 | 0,504145861 | 0,503060579 |
| 13     | 6,489829779 | 6,481079102 | 6,53818202  | 6,543782949 | 6,544048786 | 6,519384527 |
| 14     | 0,122421026 | 0,121567965 | 0,123761177 | 0,124468327 | 0,122092724 | 0,122862244 |
| 15     | 13,5942831  | 13,66433215 | 13,89912987 | 13,69106102 | 13,74130893 | 13,71802301 |
| SUM    | 64,59659743 | 64,78105974 | 65,22141838 | 65,14721251 | 65,20291686 | 64,98984098 |
| AVG    | 4,306439829 | 4,318737316 | 4,348094559 | 4,3431475   | 4,346861124 | 4,332656066 |
| MIN    | 0,122421026 | 0,121567965 | 0,123761177 | 0,124468327 | 0,122092724 | 0,122862244 |
| MAX    | 19,74583602 | 19,7254858  | 19,79040003 | 19,81360507 | 19,85232377 | 19,78553014 |

## Potential further improvements
An approach that was attempted was improsing further constraints on possible values at every step of recursion. This further reduces branching out recursively however being inside a recursive call the implementation itself is of equal importance. Potentially replacing the numpy arrays with a lighter list of lists could potentially be fast enough to gain more speed. Lists lookups are fast and could in this case prove to be faster than np arrays. 

Another potential improvement would be the usage of multiprocessing library to split the work amongst several CPU cores or even machines. For that to work the performance gain of the additional CPUs would have to overweight the overhead of process switching. So what exactly constitues a chunk of work would have to be carefully thought through. 



[1]: hhttps://en.wikipedia.org/wiki/Sudoku