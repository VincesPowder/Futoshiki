# Futoshiki Solver

Futoshiki Solver is a Python-based implementation of the Futoshiki logic puzzle. This project is integrated with multiple artificial intelligence search and inference algorithms (such as A*, Forward Chaining, Backward Chaining) to automatically solve the puzzle grids and evaluate algorithm performance.

The project supports both a graphical user interface (GUI) and a command-line interface (CLI), allowing for comparison between classical search strategies under the same problem conditions.

## Authors

Group 14 – 24C07

* 24127132 – Nguyễn Thị Ngọc Trâm
* 24127158 – Nguyễn Trần Lan Duy
* 24127262 – Đỗ Thành Vinh
* 24127465 – Tạ Mai Như Ngọc

Course: CSC14003 – Introduction to Artificial Intelligence
Project 2: Logic

## Project Structure

* `main.py` – main entry point of the application (used for batch testing all test cases via CLI)
* `gui.py` – graphical user interface (GUI) using the Pygame library
* `a_star.py` – A* Search solver
* `forward_chaining.py` – Forward Chaining solver
* `backward_chaining.py` – Backward Chaining solver (SLD resolution)
* `baseline_solvers.py` – baseline algorithms for performance comparison (Brute-Force and Backtracking)
* `kb_generator.py` – Knowledge Base generator to encode the grid into CNF logic clauses
* `Inputs/` – directory containing input files (`input-01.txt` to `input-10.txt`)
* `Outputs/` – directory containing solved puzzle results

## Requirements

Install dependencies before running the project:

```bash
pip install -r requirements.txt
```

Required packages:

```txt
pygame
```

## How to Run Source Code

### Step 1: Prepare resources

Ensure the `Inputs/` folder contains correctly formatted test case files (including grid size, given values, and inequality constraints).

### Step 2: Run the program

You can run the project in two modes:

**Graphical User Interface (GUI) mode:**
```bash
python gui.py
```

**Command Line Interface (CLI - Batch processing) mode:**
```bash
python main.py
```

### Step 3: Use the application

**1. Graphical User Interface (GUI) Mode:**
* Click **Test** to select a puzzle from the list (e.g., `input-01.txt`).
* Click **Solver** to choose a solving algorithm.
* Available algorithms:
  * Forward Chaining
  * Backward Chaining
  * A*
  * Backtracking
  * Brute-force
* Click **Restart** to reload the current puzzle or interrupt a running algorithm.
* Click **Quit** to exit the program.
* The solving process metrics (time, expanded nodes/inferences, memory) will be displayed directly on the white Log screen below the grid.

**2. Command Line Interface (CLI - Batch processing) Mode:**
* When running `main.py`, the program will automatically read and process all test cases located in the `Inputs/` directory.
* It executes all implemented algorithms sequentially for each test case.
* The full execution summary is automatically saved to `log.txt`, and the successfully solved puzzle grids are exported to the `Outputs/` folder.

## Output

Solver performance is saved automatically in the following log files:

```txt
log.txt
backward_chaining.log
```

Recorded metrics include:

* Search time
* Expanded nodes / Inferences
* Memory used
* Solution length

The grid results of successfully solved puzzles will be exported to the `Outputs/` folder.

## Notes

* Python 3.x is required.
* The `tracemalloc` library (available in the Python standard library) is used for memory tracking.
