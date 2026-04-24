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
        self.node_count = 0  # Khởi tạo bộ đếm Node
        
        # Khởi tạo Indexing để truy vấn nhanh hơn
        self.literal_to_clauses = {}
        for idx, clause in enumerate(self.clauses):
            for lit in clause:
                self.literal_to_clauses.setdefault(lit, []).append(idx)
            if len(clause) == 1 and clause[0] > 0:
                self.known_facts.add(clause[0])

    def write_log(self, message, depth=0, clause=None):
        """
        Ghi log và tự động giải mã các con số Literal sang tọa độ Val(r,c,v).
        """
        indent = "|   " * depth
    
        # Nếu có truyền vào một clause, thực hiện giải mã từng phần tử
        if clause:
            decoded_clause = []
            for lit in clause:
                sign = "" if lit > 0 else "NOT "
                # kb_gen.decode trả về ((r, c, v), is_pos)
                (r, c, v), _ = self.kb_gen.decode(abs(lit))
                decoded_clause.append(f"{sign}Val({r},{c},{v})")
            message += f" -> [{', '.join(decoded_clause)}]"

        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(f"{indent}{message}\n")

    def prove(self, goal_lit, visited=None, depth=0):
        self.node_count += 1 # Tăng số Node mỗi khi thực hiện một truy vấn mới
        
        # 1. Giải mã literal mục tiêu để in log
        (r, c, v), is_pos = self.kb_gen.decode(goal_lit)
        goal_name = f"Val({r},{c},{v})" if is_pos else f"NOT Val({r},{c},{v})"
        
        # 2. Kiểm tra các sự thật đã biết (Facts)
        if goal_lit in self.known_facts:
            self.write_log(f"[FACT] Found: {goal_name} is a given clue.", depth)
            return True

        # Kiểm tra bộ nhớ đệm (Memoization)
        if goal_lit in self.inferred_atoms:
            return self.inferred_atoms[goal_lit]
    
        if visited is None: visited = set()
        if goal_lit in visited: return False
    
        # 3. Ghi log quá trình truy vấn
        self.write_log(f"[QUERY] Trying to prove: {goal_name}", depth)
        visited.add(goal_lit)

        # 4. Kiểm tra các luật (Clauses) có thể suy ra goal_lit
        possible_rules = self.literal_to_clauses.get(goal_lit, [])
        for idx in possible_rules:
            clause = self.clauses[idx]
            # Truyền clause vào để write_log thực hiện giải mã
            self.write_log(f"[RULE] Testing Rule #{idx}", depth, clause=clause)
        
            premises_satisfied = True
            for lit in clause:
                if lit == goal_lit: continue
                # Modus Ponens: Để goal_lit ĐÚNG, thì phủ định của các literal khác (~lit) phải ĐÚNG
                if not self.prove(-lit, visited.copy(), depth + 1):
                    premises_satisfied = False
                    break
        
            if premises_satisfied:
                self.write_log(f"[SUCCESS] {goal_name} has been proved.", depth)
                self.inferred_atoms[goal_lit] = True
                return True

        self.inferred_atoms[goal_lit] = False
        return False

    def solve(self):
        """Duyệt qua các ô trống và thực hiện truy vấn từng giá trị."""
        result_grid = [[0 for _ in range(self.N)] for _ in range(self.N)]
        for i in range(1, self.N + 1):
            for j in range(1, self.N + 1):
                for v in range(1, self.N + 1):
                    if self.prove(self.kb_gen.encode(i, j, v)):
                        result_grid[i-1][j-1] = v
                        break
        return result_grid

    def run(self):
        self.node_count = 0 # Reset node trước khi chạy
        self.write_log(f"\n{'='*30} START SOLVING {self.N}x{self.N} {'='*30}")
        process = psutil.Process(os.getpid())
        start_mem = process.memory_info().rss / (1024 * 1024)
        start_time = time.time()
        
        result = self.solve()
        
        end_time = time.time()
        end_mem = process.memory_info().rss / (1024 * 1024)
        self.write_log(f"{'='*30} END PROCESS (Time: {end_time - start_time:.4f}s) {'='*30}\n")
        
        return {
            "success": any(0 not in row for row in result),
            "result": result,
            "time": end_time - start_time,
            "memory": max(0, end_mem - start_mem),
            "nodes": self.node_count, 
            "mode": "backward_chaining"
        }