def generate_smv_model(N):
    # Validate input
    if N < 1:
        raise ValueError("Queue size N must be at least 1")

    # Helper function to generate queue transitions
    def generate_queue_transitions(direction, green_cond):
        transitions = []
        
        # First position
        transitions.append(f"""
  next({direction}_queue[0]) := case
    {direction}_queue[0] = waiting & {green_cond} : passing;
    {direction}_queue[0] = passing : cleared;
    {direction}_queue[0] = cleared & {direction}_queue[1] != cleared : {direction}_queue[1];
    TRUE : {direction}_queue[0];
  esac;""")
        
        # Middle positions
        for i in range(1, N-1):
            transitions.append(f"""
  next({direction}_queue[{i}]) := case
    {direction}_queue[{i}] = cleared & {direction}_queue[{i+1}] != cleared : {direction}_queue[{i+1}];
    TRUE : {direction}_queue[{i}];
  esac;""")
        
        # Last position (if N > 1)
        if N > 1:
            transitions.append(f"""
  next({direction}_queue[{N-1}]) := case
    {direction}_queue[{N-1}] = cleared : {{cleared, waiting}};
    TRUE : {direction}_queue[{N-1}];
  esac;""")
        
        return "\n".join(transitions)

    # Generate the SMV model
    smv_model = f"""MODULE main
VAR
  phase : {{NS_GREEN, NS_YELLOW, WE_GREEN, WE_YELLOW}};
  timer : 0..{10};

  -- Queues for each direction with N={N}"""
    
    # Queue declarations
    for direction in ['north', 'south', 'west', 'east']:
        smv_model += f"""
  {direction}_queue : array 0..{N-1} of {{waiting, passing, cleared}};"""
    
    smv_model += f"""

ASSIGN
  init(phase) := NS_GREEN;
  init(timer) := {10};"""
    
    # Initializations
    for direction in ['north', 'south', 'west', 'east']:
        for i in range(N):
            smv_model += f"""
  init({direction}_queue[{i}]) := cleared;"""
    
    # Traffic light and timer logic
    smv_model += f"""

  -- Traffic light phase transitions
  next(phase) := case
    phase = NS_GREEN & timer = 0 : NS_YELLOW;
    phase = NS_YELLOW & timer = 0 : WE_GREEN;
    phase = WE_GREEN & timer = 0 : WE_YELLOW;
    phase = WE_YELLOW & timer = 0 : NS_GREEN;
    TRUE : phase;
  esac;

  -- Timer countdown logic
  next(timer) := case
    (phase = NS_GREEN | phase = WE_GREEN) : 
      (timer > 0) ? (timer - 1) : 1;
    (phase = NS_YELLOW | phase = WE_YELLOW) : 
      (timer > 0) ? (timer - 1) : {10};
    TRUE : timer;
  esac;"""
    
    # Queue transitions
    smv_model += generate_queue_transitions("north", "phase = NS_GREEN")
    smv_model += generate_queue_transitions("south", "phase = NS_GREEN")
    smv_model += generate_queue_transitions("west", "phase = WE_GREEN")
    smv_model += generate_queue_transitions("east", "phase = WE_GREEN")
    
    # # Liveness specifications
    # liveness_parts = []
    # for direction in ['north', 'south', 'west', 'east']:
    #     for i in range(N):
    #         liveness_parts.append(f"({direction}_queue[{i}] = waiting -> AF {direction}_queue[{i}] = cleared)")
    
    smv_model += f"""

-- Liveness: Every car in every queue eventually clears
-- 1. Basic Liveness: Every car eventually clears
CTLSPEC AG (AF (north_queue[0] = cleared));
CTLSPEC AG (AF (south_queue[0] = cleared));
CTLSPEC AG (AF (west_queue[0] = cleared));
CTLSPEC AG (AF (east_queue[0] = cleared));

-- 2. Queue Progression: If a car is waiting behind cleared spaces, it moves forward
--    (For position 1: if position 0 is cleared, car should eventually move to position 0)
CTLSPEC AG (north_queue[1] = waiting & north_queue[0] = cleared -> AF north_queue[0] = passing);
CTLSPEC AG (south_queue[1] = waiting & south_queue[0] = cleared -> AF south_queue[0] = passing);
CTLSPEC AG (west_queue[1] = waiting & west_queue[0] = cleared -> AF west_queue[0] = passing);
CTLSPEC AG (east_queue[1] = waiting & east_queue[0] = cleared -> AF east_queue[0] = passing);

-- 3. FIFO Order Preservation: A car can't pass while cars ahead are waiting
CTLSPEC AG !(north_queue[1] = passing & north_queue[0] = waiting);
CTLSPEC AG !(south_queue[1] = passing & south_queue[0] = waiting);
CTLSPEC AG !(west_queue[1] = passing & west_queue[0] = waiting);
CTLSPEC AG !(east_queue[1] = passing & east_queue[0] = waiting);

-- 4. No Blocking: New cars can always enter the queue if there's space
CTLSPEC AG (north_queue[{N-1}] = cleared -> EX north_queue[{N-1}] = waiting);
CTLSPEC AG (south_queue[{N-1}] = cleared -> EX south_queue[{N-1}] = waiting);
CTLSPEC AG (west_queue[{N-1}] = cleared -> EX west_queue[{N-1}] = waiting);
CTLSPEC AG (east_queue[{N-1}] = cleared -> EX east_queue[{N-1}] = waiting);

-- 5. Fairness: Traffic lights alternate infinitely
CTLSPEC AG (AF phase = NS_GREEN) & AG (AF phase = WE_GREEN);"""
    
    # Fairness and safety
    passing_north = " | ".join([f"north_queue[{i}] = passing | south_queue[{i}] = passing" for i in range(N)])
    passing_west = " | ".join([f"west_queue[{i}] = passing | east_queue[{i}] = passing" for i in range(N)])
    
    smv_model += f"""

-- 6. Safety: No simultaneous passing from perpendicular directions
DEFINE
  passing_north := ({passing_north});
  passing_west := ({passing_west});
CTLSPEC AG !(passing_north & passing_west);"""
    
    return smv_model

# Example usage:
N = int(input("Enter queue length: "))

smv_code = generate_smv_model(N)
smv_file=f"traffic_intersection_N{N}.smv"

# Save to file
with open(smv_file, "w") as f:
    f.write(smv_code)

import subprocess

# Path to your NuSMV binary (adjust if NuSMV is not in PATH)
nusmv_path = "NuSMV"  # or full path e.g., "/usr/bin/NuSMV"

# Run NuSMV and capture the output
try:
    result = subprocess.run([nusmv_path, smv_file], capture_output=True, text=True, check=True)
    print("NuSMV Output:\n", result.stdout)
except subprocess.CalledProcessError as e:
    print("Error running NuSMV:\n", e.stderr)
