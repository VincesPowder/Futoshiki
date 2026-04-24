import time
import psutil
import os

class BackwardChainingSolver:
    def __init__(self, kb_gen, log_path="backward_chaining.log"):
        self.kb_gen = kb_gen
        self.N = kb_gen.N
        self.clauses = kb_gen.get_kb()
        self.known_facts = set()
        self.inferred_atoms = {}
        self.log_path = log_path
        self.node_count = 0 
        
        self.literal_to_clauses = {}
        for idx, clause in enumerate(self.clauses):
            for lit in clause:
                self.literal_to_clauses.setdefault(lit, []).append(idx)
            if len(clause) == 1 and clause[0] > 0:
                self.known_facts.add(clause[0])

    def decode_lit(self, lit):
        (r, c, v), is_pos = self.kb_gen.decode(abs(lit))
        name = f"Val({r},{c},{v})"
        return name if lit > 0 else f"¬{name}"

    def write_log(self, tag, message, depth=0):
        indent = ""
        if depth > 0:
            indent = "│   " * (depth - 1) + "├── "
        formatted_message = f"{indent}[{tag}] {message}"
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(f"{formatted_message}\n")

    def format_as_horn(self, goal_lit, clause):
        goal_name = self.decode_lit(goal_lit)
        premises = [self.decode_lit(-lit) for lit in clause if lit != goal_lit]
        return goal_name if not premises else f"{goal_name} ⇐ {' ∧ '.join(premises)}"

    def prove(self, goal_lit, visited=None, depth=0):
        self.node_count += 1
        goal_name = self.decode_lit(goal_lit)
        if goal_lit in self.known_facts:
            self.write_log("FACT", f"Found: {goal_name} (Given clue)", depth)
            return True
        if goal_lit in self.inferred_atoms:
            return self.inferred_atoms[goal_lit]
        if visited is None: visited = set()
        if goal_lit in visited: return False
    
        self.write_log("QUERY", f"Proving: {goal_name}", depth)
        visited.add(goal_lit)

        possible_rules = self.literal_to_clauses.get(goal_lit, [])
        for idx in possible_rules:
            clause = self.clauses[idx]
            self.write_log("RULE", f"Clause #{idx}: {self.format_as_horn(goal_lit, clause)}", depth + 1)
            premises_satisfied = True
            for lit in clause:
                if lit == goal_lit: continue
                if not self.prove(-lit, visited.copy(), depth + 2):
                    premises_satisfied = False
                    break
            if premises_satisfied:
                self.write_log("SUCCESS", f"Proved: {goal_name}", depth)
                self.inferred_atoms[goal_lit] = True
                return True
        self.inferred_atoms[goal_lit] = False
        return False

    def solve(self):
        result_grid = [[0 for _ in range(self.N)] for _ in range(self.N)]
        for i in range(1, self.N + 1):
            for j in range(1, self.N + 1):
                with open(self.log_path, "a", encoding="utf-8") as f:
                    f.write(f"\n--- EXPLORING CELL ({i}, {j}) ---\n")
                for v in range(1, self.N + 1):
                    if self.prove(self.kb_gen.encode(i, j, v)):
                        result_grid[i-1][j-1] = v
                        break
        return result_grid

    def run(self, test_label="Unknown"):
        self.node_count = 0
        self.inferred_atoms = {}
        
        # SỬA Ở ĐÂY: In tiêu đề có tên file test
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(f"\n{'#'*80}\n")
            f.write(f"### [PROCESS START]: {test_label} | Grid: {self.N}x{self.N}\n")
            f.write(f"{'#'*80}\n")

        process = psutil.Process(os.getpid())
        start_mem = process.memory_info().rss / (1024 * 1024)
        start_time = time.time()
        result = self.solve()
        end_time = time.time()
        end_mem = process.memory_info().rss / (1024 * 1024)
        
        return {
            "success": any(0 not in row for row in result),
            "result": result,
            "time": end_time - start_time,
            "memory": max(0, end_mem - start_mem),
            "nodes": self.node_count,
            "length": sum(1 for row in result for val in row if val != 0)
        }