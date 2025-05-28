from z3 import Solver, Int, Or, And, Not, sat
import argparse

def solve_with_smt(grid):
    print("Non-incremental")
    N = len(grid)
    path_length = 2 * N - 2  # Minimal path length (right/down moves only)
    s = Solver()
    
    # Create variables for x and y positions at each step
    x = [Int(f'x_{t}') for t in range(path_length + 1)]
    y = [Int(f'y_{t}') for t in range(path_length + 1)]
    
    # Start at (1,1)
    s.add(x[0] == 1, y[0] == 1)
    # End at (N,N)
    s.add(x[path_length] == N, y[path_length] == N)
    
    # Movement constraints: each step must move right or down
    for t in range(1, path_length + 1):
        move_right = And(x[t] == x[t-1], y[t] == y[t-1] + 1)
        move_down = And(x[t] == x[t-1] + 1, y[t] == y[t-1])
        s.add(Or(move_right, move_down))
    
    # Position invariant: x[t] + y[t] = t + 2 (ensures step progression)
    for t in range(path_length + 1):
        s.add(x[t] + y[t] == t + 2)
    
    # Obstacle constraints: path cannot visit cells marked 'X'
    for i in range(N):
        for j in range(N):
            if grid[i][j] == 'X':
                # Convert grid indices (0-based) to 1-based coordinates
                obs_x, obs_y = i + 1, j + 1
                for t in range(path_length + 1):
                    s.add(Not(And(x[t] == obs_x, y[t] == obs_y)))
    
    # Grid bounds constraints
    for t in range(path_length + 1):
        s.add(x[t] >= 1, x[t] <= N)
        s.add(y[t] >= 1, y[t] <= N)
    
    # Solve and reconstruct the path
    if s.check() == sat:
        model = s.model()
        path = []
        for t in range(path_length + 1):
            xt = model.eval(x[t]).as_long()
            yt = model.eval(y[t]).as_long()
            path.append((xt, yt))
        return "SAT", path
    else:
        return "UNSAT"

def solve_with_smt_incremental(grid):
    print("Incremental")
    N = len(grid)
    max_path_length = 2 * N - 2  # Maximum possible path length (right/down moves only)
    
    # Try path lengths from 1 to max_path_length
    for path_length in range(1, max_path_length + 1):
        s = Solver()
        
        # Create variables for x and y positions at each step
        x = [Int(f'x_{t}') for t in range(path_length + 1)]
        y = [Int(f'y_{t}') for t in range(path_length + 1)]
        
        # Start at (1,1)
        s.add(x[0] == 1, y[0] == 1)
        # End at (N,N)
        s.add(x[path_length] == N, y[path_length] == N)
        
        # Movement constraints: each step must move right or down
        for t in range(1, path_length + 1):
            move_right = And(x[t] == x[t-1], y[t] == y[t-1] + 1)
            move_down = And(x[t] == x[t-1] + 1, y[t] == y[t-1])
            s.add(Or(move_right, move_down))
        
        # Position invariant: x[t] + y[t] = t + 2 (ensures step progression)
        for t in range(path_length + 1):
            s.add(x[t] + y[t] == t + 2)
        
        # Obstacle constraints: path cannot visit cells marked 'X'
        for i in range(N):
            for j in range(N):
                if grid[i][j] == 'X':
                    # Convert grid indices (0-based) to 1-based coordinates
                    obs_x, obs_y = i + 1, j + 1
                    for t in range(path_length + 1):
                        s.add(Not(And(x[t] == obs_x, y[t] == obs_y)))
        
        # Grid bounds constraints
        for t in range(path_length + 1):
            s.add(x[t] >= 1, x[t] <= N)
            s.add(y[t] >= 1, y[t] <= N)
        
        # Solve and reconstruct the path if solution exists
        if s.check() == sat:
            model = s.model()
            path = []
            for t in range(path_length + 1):
                xt = model.eval(x[t]).as_long()
                yt = model.eval(y[t]).as_long()
                path.append((xt, yt))
            return "SAT", path, path_length
    
    return "UNSAT", None, None

grid = [
    ['S', 'X', 'X', 'X', '.'],
    ['.', 'X', '.', 'X', '.'],
    ['.', '.', '.', 'X', '.'],
    ['X', 'X', '.', '.', '.'],
    ['.', '.', '.', '.', 'G']
]

parser = argparse.ArgumentParser()
parser.add_argument("--incr", action="store_true", help="Enables incremental solving")
args = parser.parse_args()

length=-1

if args.incr:  # Use args.incr instead of args.flag
    result, path, length = solve_with_smt_incremental(grid)
else:
    result, path = solve_with_smt(grid)

if result == "SAT":
    print(result)
    if(length!=-1):
        print(f"Path length= {length}:")
    print(path)
else:
    print("No solution exists")