from pysat.solvers import Solver
import argparse

def solve_sat(grid):
    N = len(grid)
    n_steps = 2 * N -2
    
    cnf = []
    variables = {}
    var_count = 1
    
    # Create variables for each position at each step
    # variables[(step, i, j)] = var_num
    for step in range(n_steps + 1):
        for i in range(1, N + 1):
            for j in range(1, N + 1):
                if grid[i-1][j-1] != 'X':
                    variables[(step, i, j)] = var_count
                    var_count += 1
    
    # Constraints
    
    # 1. Start at (1,1) at step 0
    cnf.append([variables[(0, 1, 1)]])
    
    # 2. Goal must be reached at some step
    goal_clause = [variables[(step, N, N)] for step in range(n_steps + 1) if (step, N, N) in variables]

    cnf.append(goal_clause)
    
    # 3. At each step, at most one position (for all pairs)
    for step in range(n_steps + 1):
        positions = [(i,j) for i in range(1, N+1) for j in range(1, N+1) if (step, i, j) in variables]
        for k in range(len(positions)):
            for l in range(k+1, len(positions)):
                i1, j1 = positions[k]
                i2, j2 = positions[l]
                cnf.append([-variables[(step, i1, j1)], -variables[(step, i2, j2)]])
    
    # 4. Transition between steps: only right or down moves
    for step in range(n_steps):
        for i in range(1, N + 1):
            for j in range(1, N + 1):
                if (step, i, j) not in variables:
                    continue
                
                next_positions = []
                # Right move
                if j < N and (step+1, i, j+1) in variables:
                    next_positions.append(variables[(step+1, i, j+1)])
                # Down move
                if i < N and (step+1, i+1, j) in variables:
                    next_positions.append(variables[(step+1, i+1, j)])
                
                if next_positions:
                    # Current position implies one of the next positions
                    cnf.append([-variables[(step, i, j)]] + next_positions)
                else:
                    # No valid moves from this position
                    cnf.append([-variables[(step, i, j)]])
    
    # Solve
    solver = Solver(bootstrap_with=cnf)
    if solver.solve():
        model = solver.get_model()
        # Reconstruct the path
        path = []
        for step in range(n_steps + 1):
            for i in range(1, N + 1):
                for j in range(1, N + 1):
                    if (step, i, j) in variables and model[variables[(step, i, j)]-1] > 0:
                        path.append((i, j))
        return "SAT", path
    
    return "UNSAT"

def solve_incremental_sat(grid):
    N = len(grid)
    max_steps = 2 * N -2
    
    for step_limit in range(1, max_steps + 1):
        cnf = []
        variables = {}
        var_count = 1
        
        # Create variables for each position at each step
        # variables[(step, i, j)] = var_num
        for step in range(step_limit + 1):
            for i in range(1, N + 1):
                for j in range(1, N + 1):
                    if grid[i-1][j-1] != 'X':
                        variables[(step, i, j)] = var_count
                        var_count += 1
        
        # Constraints
        
        # 1. Start at (1,1) at step 0
        cnf.append([variables[(0, 1, 1)]])
        
        # 2. Goal must be reached at some step
        goal_clause = [variables[(step, N, N)] for step in range(step_limit + 1) if (step, N, N) in variables]
        if not goal_clause:
            continue  # No path in this step limit
        cnf.append(goal_clause)
        
        # 3. At each step, at most one position (for all pairs)
        for step in range(step_limit + 1):
            positions = [(i,j) for i in range(1, N+1) for j in range(1, N+1) if (step, i, j) in variables]
            for k in range(len(positions)):
                for l in range(k+1, len(positions)):
                    i1, j1 = positions[k]
                    i2, j2 = positions[l]
                    cnf.append([-variables[(step, i1, j1)], -variables[(step, i2, j2)]])
        
        # 4. Transition between steps: only right or down moves
        for step in range(step_limit):
            for i in range(1, N + 1):
                for j in range(1, N + 1):
                    if (step, i, j) not in variables:
                        continue
                    
                    next_positions = []
                    # Right move
                    if j < N and (step+1, i, j+1) in variables:
                        next_positions.append(variables[(step+1, i, j+1)])
                    # Down move
                    if i < N and (step+1, i+1, j) in variables:
                        next_positions.append(variables[(step+1, i+1, j)])
                    
                    if next_positions:
                        # Current position implies one of the next positions
                        cnf.append([-variables[(step, i, j)]] + next_positions)
                    else:
                        # No valid moves from this position
                        cnf.append([-variables[(step, i, j)]])
        
        # Solve
        solver = Solver(bootstrap_with=cnf)
        if solver.solve():
            model = solver.get_model()
            # Reconstruct the path
            path = []
            for step in range(step_limit + 1):
                for i in range(1, N + 1):
                    for j in range(1, N + 1):
                        if (step, i, j) in variables and model[variables[(step, i, j)]-1] > 0:
                            path.append((i, j))
            return "SAT", path, step_limit
    
    return "UNSAT"

# Example usage:
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
    result,path,length=solve_incremental_sat(grid)
else:
    result,path = solve_sat(grid)

if result == "SAT":
    print(result)
    if(length!=-1):
        print(f"Path length= {length}:")
    print(path)
else:
    print("No solution exists")