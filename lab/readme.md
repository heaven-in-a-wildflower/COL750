# Instructions to Run Programs

## Dependencies

To install the required dependencies, run:

```sh
pip install pysat python-sat z3-solver
```

## Usage

### **SAT Solver**
Modify the grid in the program to test different inputs.

#### **Non-incremental Mode**
```sh
python sat.py
```

#### **Incremental Mode**
```sh
python sat.py --incr
```

### **SMT Solver**
Modify the grid in the program to test different inputs.

#### **Non-incremental Mode**
```sh
python smt.py
```

#### **Incremental Mode**
```sh
python smt.py --incr
```

### **Traffic Intersection Problem**
When prompted, enter the queue length. The python file generates the .smv file for given N and also runs it.

```sh
python nusmv.py
```



