import time
import psutil
import os

class FutoshikiBaseline:
    def __init__(self, N, grid, horiz, vert, time_limit=10):
        """
        Khởi tạo solver với giới hạn thời gian chạy.
        time_limit: Thời gian tối đa cho phép (giây). 
        """
        self.N = N
        self.original_grid = [row[:] for row in grid]
        self.grid = [row[:] for row in grid]
        self.horiz = horiz
        self.vert = vert
        self.nodes_expanded = 0
        self.time_limit = time_limit
        self.start_time = 0
        self.is_timeout = False

    def reset_grid(self):
        self.grid = [row[:] for row in self.original_grid]
        self.nodes_expanded = 0
        self.is_timeout = False

    def check_timeout(self):
        """Kiểm tra xem đã vượt quá thời gian cho phép chưa."""
        if time.time() - self.start_time > self.time_limit:
            self.is_timeout = True
            return True
        return False

    def is_safe(self, r, c, val):
        # 1. Kiểm tra hàng và cột 
        for i in range(self.N):
            if self.grid[r][i] == val or self.grid[i][c] == val:
                return False

        # 2. Kiểm tra ràng buộc ngang 
        if c > 0 and self.horiz[r][c-1] != 0:
            left_v = self.grid[r][c-1]
            if left_v != 0:
                if self.horiz[r][c-1] == 1 and not (left_v < val): return False
                if self.horiz[r][c-1] == -1 and not (left_v > val): return False
        
        if c < self.N - 1 and self.horiz[r][c] != 0:
            right_v = self.grid[r][c+1]
            if right_v != 0:
                if self.horiz[r][c] == 1 and not (val < right_v): return False
                if self.horiz[r][c] == -1 and not (val > right_v): return False

        # 3. Kiểm tra ràng buộc dọc 
        if r > 0 and self.vert[r-1][c] != 0:
            top_v = self.grid[r-1][c]
            if top_v != 0:
                if self.vert[r-1][c] == 1 and not (top_v < val): return False
                if self.vert[r-1][c] == -1 and not (top_v > val): return False

        if r < self.N - 1 and self.vert[r][c] != 0:
            bot_v = self.grid[r+1][c]
            if bot_v != 0:
                if self.vert[r][c] == 1 and not (val < bot_v): return False
                if self.vert[r][c] == -1 and not (val > bot_v): return False
        return True

    def is_entire_grid_valid(self):
        for r in range(self.N):
            for c in range(self.N):
                val = self.grid[r][c]
                self.grid[r][c] = 0
                if not self.is_safe(r, c, val):
                    self.grid[r][c] = val
                    return False
                self.grid[r][c] = val
        return True

    def solve_backtracking(self):
        if self.check_timeout(): return False # Ngắt nếu quá giờ
        self.nodes_expanded += 1
        for r in range(self.N):
            for c in range(self.N):
                if self.grid[r][c] == 0:
                    for val in range(1, self.N + 1):
                        if self.is_safe(r, c, val):
                            self.grid[r][c] = val
                            if self.solve_backtracking(): return True
                            self.grid[r][c] = 0
                    return False
        return True

    def solve_brute_force(self):
        if self.check_timeout(): return False # Ngắt nếu quá giờ
        self.nodes_expanded += 1
        for r in range(self.N):
            for c in range(self.N):
                if self.grid[r][c] == 0:
                    for val in range(1, self.N + 1):
                        self.grid[r][c] = val
                        if self.solve_brute_force(): return True
                        self.grid[r][c] = 0
                    return False
        return self.is_entire_grid_valid()

    def run(self, mode="backtracking"):
        self.reset_grid()
        self.start_time = time.time()
        process = psutil.Process(os.getpid())
        start_mem = process.memory_info().rss / (1024 * 1024)
        
        if mode == "backtracking":
            success = self.solve_backtracking()
        else:
            success = self.solve_brute_force()
            
        end_time = time.time()
        end_mem = process.memory_info().rss / (1024 * 1024)
        
        return {
            "success": success and not self.is_timeout,
            "timeout": self.is_timeout,
            "result": self.grid,
            "nodes": self.nodes_expanded,
            "time": end_time - self.start_time,
            "memory": max(0, end_mem - start_mem),
            "mode": mode
        }