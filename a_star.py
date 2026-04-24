import heapq 
import time
import os
import tracemalloc

class FutoshikiAStar:
    def __init__(self, n, grid, horiz, vert):
        self.n = n
        self.grid = [row[:] for row in grid]
        self.horiz = horiz
        self.vert = vert
        self.nodes_expanded = 0
        self.degrees = [[self._calculate_degree(r, c) for c in range(n)] for r in range(n)]

    def _calculate_degree(self, r, c):
        deg = 0
        if c > 0 and self.horiz[r][c-1] != 0: deg += 1
        if c < self.n - 1 and self.horiz[r][c] != 0: deg += 1
        if r > 0 and self.vert[r-1][c] != 0: deg += 1
        if r < self.n - 1 and self.vert[r][c] != 0: deg += 1
        return deg


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
        tracemalloc.start()
        start_time = time.perf_counter()
        
        node_count = 0
        # Chuyển bảng về dạng tuple 1D để tối ưu bộ nhớ và tốc độ so sánh
        grid_1d = tuple(item for row in self.grid for item in row)
        h_start = grid_1d.count(0)
        
        # Priority Queue: (f, -g, node_id, board_1d)
        pq = [(h_start, 0, node_count, grid_1d)]

        while pq:
            f, neg_g, _, curr_board = heapq.heappop(pq)
            g = -neg_g
            
            # 1. ĐIỀU KIỆN THẮNG: Chỉ thắng khi không còn số 0
            if 0 not in curr_board:
                # LẤY ĐỈNH BỘ NHỚ VÀ DỪNG ĐO
                _, peak = tracemalloc.get_traced_memory() 
                tracemalloc.stop()
                res_2d = [list(curr_board[i:i+self.n]) for i in range(0, len(curr_board), self.n)]
                return {
                    "success": True,
                    "result": res_2d, 
                    "nodes": self.nodes_expanded, 
                    "time": time.perf_counter() - start_time, 
                    "memory": peak / 1024
                }

            self.nodes_expanded += 1
            if self.nodes_expanded > 50000: break 

            best_idx = -1
            min_domain_size = float('inf')
            candidates = []

            # 2. CHỌN Ô (MRV + DEGREE HEURISTIC)
            for i in range(self.n * self.n):
                if curr_board[i] == 0:
                    r, c = divmod(i, self.n)
                    # Kiểm tra domain đồng thời cả ngang và dọc
                    domain = [v for v in range(1, self.n + 1) if self.is_valid_1d(i, v, curr_board)]
                    d_size = len(domain)
                    
                    if d_size == 0:
                        min_domain_size = 0
                        break
                    
                    if d_size < min_domain_size:
                        min_domain_size = d_size
                        best_idx = i
                        candidates = domain
                    elif d_size == min_domain_size:
                        # Tie-break bằng Degree Heuristic
                        if best_idx == -1 or self.degrees[r][c] > self.degrees[best_idx // self.n][best_idx % self.n]:
                            best_idx = i
                            candidates = domain
                    if d_size == 1: break 
            
            if min_domain_size == 0 or best_idx == -1:
                continue

            # 3. FORWARD CHECKING
            for val in candidates:
                new_board_list = list(curr_board)
                new_board_list[best_idx] = val
                new_board = tuple(new_board_list)
                
                is_dead_end = False
                for j in range(self.n * self.n):
                    if new_board[j] == 0:
                        # Kiểm tra xem ô j còn giá trị nào khả thi không
                        has_value = any(self.is_valid_1d(j, v, new_board) for v in range(1, self.n + 1))
                        if not has_value:
                            is_dead_end = True
                            break
                
                if not is_dead_end:
                    node_count += 1
                    h = new_board.count(0)
                    heapq.heappush(pq, (g + 1 + h, -(g + 1), node_count, new_board))
        
        tracemalloc.stop()
        return None

    def is_valid_1d(self, idx, val, board_1d):
        r, c = divmod(idx, self.n)
        row_start = r * self.n
        
        for i in range(self.n):
            if i != c and board_1d[row_start + i] == val: return False
            if i != r and board_1d[i * self.n + c] == val: return False
        
        # Ràng buộc ngang
        if c > 0 and self.horiz[r][c-1] != 0:
            left = board_1d[row_start + c - 1]
            if left != 0:
                if self.horiz[r][c-1] == 1 and not (left < val): return False
                if self.horiz[r][c-1] == -1 and not (left > val): return False
        if c < self.n - 1 and self.horiz[r][c] != 0:
            right = board_1d[row_start + c + 1]
            if right != 0:
                if self.horiz[r][c] == 1 and not (val < right): return False
                if self.horiz[r][c] == -1 and not (val > right): return False

        # Ràng buộc dọc
        if r > 0 and self.vert[r-1][c] != 0:
            up = board_1d[(r-1) * self.n + c]
            if up != 0:
                if self.vert[r-1][c] == 1 and not (up < val): return False
                if self.vert[r-1][c] == -1 and not (up > val): return False
        if r < self.n - 1 and self.vert[r][c] != 0:
            down = board_1d[(r+1) * self.n + c]
            if down != 0:
                if self.vert[r][c] == 1 and not (val < down): return False
                if self.vert[r][c] == -1 and not (val > down): return False
        return True