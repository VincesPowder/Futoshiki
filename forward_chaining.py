import time
import tracemalloc
from collections import deque
from copy import deepcopy
 
 
class ForwardChaining:
    def __init__(self, N, grid, horiz, vert):
        self.N = N
        self.grid = grid
        self.horiz = horiz
        self.vert = vert
 
        # domains[i][j]: set giá trị khả dụng của ô (i,j)
        self.domains = [[set(range(1, N + 1)) for _ in range(N)]
                        for _ in range(N)]
 
        # Queue các ô vừa trở thành singleton cần propagate (Rule 1)
        # Mỗi phần tử: (i, j, v)
        self._queue = deque()
 
        # Set theo dõi ô đã được đưa vào queue để tránh trùng
        self._in_queue = set()
        self.inference_count = 0
 
        # Áp dụng given clues (A5)
        self._apply_given_clues()

    def _apply_given_clues(self):
        """
        A5: Given(i,j,v) => Val(i,j,v).
        Thu hẹp domain về {v} và đưa vào queue để propagate.
        """
        for i in range(self.N):
            for j in range(self.N):
                if self.grid[i][j] != 0:
                    v = self.grid[i][j]
                    self.domains[i][j] = {v}
                    self._enqueue(i, j, v)
 
    def _enqueue(self, i, j, v):
        """Thêm ô (i,j,v) vào queue nếu chưa có."""
        if (i, j) not in self._in_queue:
            self._queue.append((i, j, v))
            self._in_queue.add((i, j))
 
    # RULE 1: FORCED ASSIGNMENT (queue-based)
    def _flush_queue(self):
        """
        Xử lý toàn bộ queue: mỗi ô singleton (i,j,v) được xác định
        → loại v khỏi tất cả ô cùng hàng và cùng cột (A3).
        Nếu một ô mới trở thành singleton → đưa vào queue.
        Trả về False nếu domain rỗng (mâu thuẫn).
        """
        while self._queue:
            i, j, v = self._queue.popleft()
            self._in_queue.discard((i, j))
 
            # Đảm bảo domain ô này vẫn là {v} (có thể đã thay đổi)
            if self.domains[i][j] != {v}:
                continue
 
            # Lan truyền theo hàng
            for jj in range(self.N):
                if jj == j:
                    continue
                if v in self.domains[i][jj]:
                    self.domains[i][jj].discard(v)
                    self.inference_count += 1
                    if not self.domains[i][jj]:
                        return False
                    if len(self.domains[i][jj]) == 1:
                        vv = next(iter(self.domains[i][jj]))
                        self._enqueue(i, jj, vv)
 
            # Lan truyền theo cột
            for ii in range(self.N):
                if ii == i:
                    continue
                if v in self.domains[ii][j]:
                    self.domains[ii][j].discard(v)
                    self.inference_count += 1
                    if not self.domains[ii][j]:
                        return False
                    if len(self.domains[ii][j]) == 1:
                        vv = next(iter(self.domains[ii][j]))
                        self._enqueue(ii, j, vv)
 
        return True
 
    # RULE 2: HIDDEN SINGLE
    def _apply_hidden_singles(self):
        """
        Nếu giá trị v chỉ xuất hiện tại đúng 1 ô trong hàng/cột
        → ép ô đó nhận v (đưa vào queue).
        Trả về (changed, ok).
        """
        changed = False
 
        # Theo hàng
        for i in range(self.N):
            for v in range(1, self.N + 1):
                positions = [j for j in range(self.N) if v in self.domains[i][j]]
                if len(positions) == 0:
                    return changed, False  # v không thể xuất hiện trong hàng → mâu thuẫn
                if len(positions) == 1:
                    j = positions[0]
                    if len(self.domains[i][j]) > 1:
                        self.domains[i][j] = {v}
                        self.inference_count += 1
                        self._enqueue(i, j, v)
                        changed = True
 
        # Theo cột
        for j in range(self.N):
            for v in range(1, self.N + 1):
                positions = [i for i in range(self.N) if v in self.domains[i][j]]
                if len(positions) == 0:
                    return changed, False
                if len(positions) == 1:
                    i = positions[0]
                    if len(self.domains[i][j]) > 1:
                        self.domains[i][j] = {v}
                        self.inference_count += 1
                        self._enqueue(i, j, v)
                        changed = True
 
        return changed, True
 
    # RULE 3: INEQUALITY PROPAGATION
    def _apply_inequality_constraints(self):
        """
        Cắt tỉa domain dựa trên ràng buộc bất đẳng thức (A4).
 
        Với left < right (rel=1):
          Mọi v trong domain_left  phải < max(domain_right)
          Mọi v trong domain_right phải > min(domain_left)
 
        Với left > right (rel=-1): đảo ngược.
        Trả về (changed, ok).
        """
        changed = False
 
        # Ràng buộc ngang: horiz[i][j] giữa (i,j) và (i,j+1)
        for i in range(self.N):
            for j in range(self.N - 1):
                rel = self.horiz[i][j]
                if rel == 0:
                    continue
                c, ok = self._prune_pair(i, j, i, j + 1, rel)
                if not ok:
                    return changed, False
                changed = changed or c
 
        # Ràng buộc dọc: vert[i][j] giữa (i,j) và (i+1,j)
        for i in range(self.N - 1):
            for j in range(self.N):
                rel = self.vert[i][j]
                if rel == 0:
                    continue
                c, ok = self._prune_pair(i, j, i + 1, j, rel)
                if not ok:
                    return changed, False
                changed = changed or c
 
        return changed, True
 
    def _prune_pair(self, r1, c1, r2, c2, rel):
        """
        Cắt tỉa domain[r1][c1] (d_a) và domain[r2][c2] (d_b) theo rel.
        rel=1: d_a < d_b;  rel=-1: d_a > d_b.
        Trả về (changed, ok). Cập nhật queue nếu domain trở thành singleton.
        """
        d_a = self.domains[r1][c1]
        d_b = self.domains[r2][c2]
 
        if not d_a or not d_b:
            return False, False
 
        changed = False
 
        if rel == 1:   # d_a < d_b
            # a phải < max(b): loại mọi v_a >= max(b) khỏi d_a
            threshold_a = max(d_b)
            new_a = {v for v in d_a if v < threshold_a}
            # b phải > min(a): loại mọi v_b <= min(a) khỏi d_b (dùng min(a) MỚI)
            # Tính min(a) trước khi prune để tránh lỗi
            if new_a:
                threshold_b = min(new_a)
                new_b = {v for v in d_b if v > threshold_b}
            else:
                return changed, False
        else:          # rel == -1: d_a > d_b
            threshold_a = min(d_b)
            new_a = {v for v in d_a if v > threshold_a}
            if new_a:
                threshold_b = max(new_a)
                new_b = {v for v in d_b if v < threshold_b}
            else:
                return changed, False
 
        if not new_a or not new_b:
            return changed, False
 
        if new_a != d_a:
            self.domains[r1][c1] = new_a
            self.inference_count += len(d_a) - len(new_a)
            changed = True
            if len(new_a) == 1:
                self._enqueue(r1, c1, next(iter(new_a)))
 
        if new_b != d_b:
            self.domains[r2][c2] = new_b
            self.inference_count += len(d_b) - len(new_b)
            changed = True
            if len(new_b) == 1:
                self._enqueue(r2, c2, next(iter(new_b)))
 
        return changed, True
 
    def propagate(self):
        while True:
            # Rule 1: xử lý tất cả singleton trong queue
            if not self._flush_queue():
                return False
 
            # Rule 3: inequality
            c_ineq, ok = self._apply_inequality_constraints()
            if not ok:
                return False
 
            # Rule 1 lại sau inequality (có thể tạo singleton mới)
            if not self._flush_queue():
                return False
 
            # Rule 2: hidden singles
            c_hidden, ok = self._apply_hidden_singles()
            if not ok:
                return False
 
            # Nếu Rule 2 hoặc 3 tạo ra thay đổi → lặp lại
            if not c_ineq and not c_hidden:
                break  # fixpoint đạt được
 
        return True
 
    def _is_complete(self):
        return all(len(self.domains[i][j]) == 1
                   for i in range(self.N)
                   for j in range(self.N))
 
    def _pick_unassigned_mrv(self):
        best = None
        min_size = self.N + 1
        for i in range(self.N):
            for j in range(self.N):
                s = len(self.domains[i][j])
                if 2 <= s < min_size:
                    min_size = s
                    best = (i, j)
        return best
 
    def _save_state(self):
        return (deepcopy(self.domains),
                deque(self._queue),
                set(self._in_queue))
 
    def _restore_state(self, state):
        self.domains, self._queue, self._in_queue = state
 
    def _backtrack(self):
        if not self.propagate():
            return False
 
        if self._is_complete():
            return True
 
        cell = self._pick_unassigned_mrv()
        if cell is None:
            return False  # có ô rỗng domain
 
        i, j = cell
        values = sorted(self.domains[i][j])
 
        for v in values:
            state = self._save_state()
 
            # Gán thử v cho ô (i,j)
            self.domains[i][j] = {v}
            self.inference_count += 1
            self._enqueue(i, j, v)
 
            if self._backtrack():
                return True
 
            # Thất bại → khôi phục
            self._restore_state(state)
 
        return False
 
    def solve(self):
        tracemalloc.start()
        t0 = time.time()
 
        ok = self._backtrack()
 
        elapsed = time.time() - t0
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
 
        result = None
        if ok:
            result = [[next(iter(self.domains[i][j])) for j in range(self.N)]
                      for i in range(self.N)]
 
        return {
            'result'    : result,
            'time'      : elapsed,
            'memory'    : peak / (1024 * 1024),
            'inferences': self.inference_count,
            'success'   : ok,
        }
 
def format_solution(N, result, horiz, vert):
    """
    Định dạng lưới kết quả theo yêu cầu đề bài:
      Ngang: '<' hoặc '>'
      Dọc:   'v' (top < bottom) hoặc '^' (top > bottom)
    """
    lines = []
    for i in range(N):
        row_parts = []
        for j in range(N):
            row_parts.append(str(result[i][j]))
            if j < N - 1:
                rel = horiz[i][j]
                row_parts.append('<' if rel == 1 else ('>' if rel == -1 else ' '))
        lines.append(' '.join(row_parts))
 
        if i < N - 1:
            vert_parts = []
            for j in range(N):
                rel = vert[i][j]
                vert_parts.append('v' if rel == 1 else ('^' if rel == -1 else ' '))
            lines.append(' '.join(vert_parts))
 
    return '\n'.join(lines)