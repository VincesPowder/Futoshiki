import heapq
import time
import os
import psutil

class FutoshikiAStar:
    def __init__(self, n, grid, horiz, vert):
        self.n = n
        self.grid = [row[:] for row in grid]
        self.horiz = horiz
        self.vert = vert
        self.nodes_expanded = 0
        self.process = psutil.Process(os.getpid())
        # Tối ưu nhược điểm 1: Pre-calculate Degree
        self.degrees = [[self._calculate_degree(r, c) for c in range(n)] for r in range(n)]

    def _calculate_degree(self, r, c):
        deg = 0
        if c > 0 and self.horiz[r][c-1] != 0: deg += 1
        if c < self.n - 1 and self.horiz[r][c] != 0: deg += 1
        if r > 0 and self.vert[r-1][c] != 0: deg += 1
        if r < self.n - 1 and self.vert[r][c] != 0: deg += 1
        return deg

    def get_mem_usage(self):
        return self.process.memory_info().rss / (1024 * 1024)

    def is_valid(self, r, c, val, board):
        for i in range(self.n):
            if board[r][i] == val or board[i][c] == val: return False
        
        if c > 0 and self.horiz[r][c-1] == 1 and board[r][c-1] != 0 and not (board[r][c-1] < val): return False
        if c > 0 and self.horiz[r][c-1] == -1 and board[r][c-1] != 0 and not (board[r][c-1] > val): return False
        if c < self.n-1 and self.horiz[r][c] == 1 and board[r][c+1] != 0 and not (val < board[r][c+1]): return False
        if c < self.n-1 and self.horiz[r][c] == -1 and board[r][c+1] != 0 and not (val > board[r][c+1]): return False
        return True

    def get_domain(self, r, c, board):
        return [v for v in range(1, self.n + 1) if self.is_valid(r, c, v, board)]

    def solve(self):
        start_time = time.perf_counter()
        mem_before = self.get_mem_usage()
        
        # Tối ưu nhược điểm 3: Tie-breaking bằng cách thêm ID tự tăng và ưu tiên g
        node_count = 0
        h_start = sum(row.count(0) for row in self.grid)
        pq = [(h_start, 0, node_count, self.grid)]
        max_mem = mem_before

        while pq:
            f, neg_g, _, curr_board = heapq.heappop(pq)
            g = -neg_g
            self.nodes_expanded += 1
            
            # Tối ưu nhược điểm 4: Ngắt sớm nếu bảng quá nhỏ hoặc giải xong nhanh
            if self.nodes_expanded > 5000: break

            best_cell = None
            min_domain_size = float('inf')

            # Tối ưu nhược điểm 1: Tìm MRV nhanh hơn
            for r in range(self.n):
                for c in range(self.n):
                    if curr_board[r][c] == 0:
                        domain = self.get_domain(r, c, curr_board)
                        d_size = len(domain)
                        if d_size == 0: # Cắt tỉa ngay
                            min_domain_size = 0
                            break
                        if d_size < min_domain_size:
                            min_domain_size = d_size
                            best_cell = (r, c)
                            candidates = domain
                        if d_size == 1: break
                if min_domain_size <= 1: break

            if not best_cell:
                return {"result": curr_board, "nodes": self.nodes_expanded, 
                        "time": time.perf_counter() - start_time, "memory": self.get_mem_usage() - mem_before}

            if min_domain_size == 0: continue

            r, c = best_cell
            for val in candidates:
                new_board = [row[:] for row in curr_board]
                new_board[r][c] = val
                node_count += 1
                # Tối ưu nhược điểm 2: h(n) đơn giản kết hợp MRV mạnh
                h = sum(row.count(0) for row in new_board)
                heapq.heappush(pq, (g + 1 + h, -(g + 1), node_count, new_board))
        
        return None