class KBGenerator:
    def __init__(self, N):
        self.N = N
        self.clauses = []
        
    def encode(self, i, j, v):
        """
        Mã hóa biến Val(i, j, v) thành một số nguyên duy nhất.
        i, j, v có giá trị từ 1 đến N.
        """
        return (i - 1) * self.N * self.N + (j - 1) * self.N + v

    def decode(self, literal):
        """Giải mã số nguyên về lại (i, j, v)"""
        val = abs(literal) - 1
        v = (val % self.N) + 1
        val //= self.N
        j = (val % self.N) + 1
        i = (val // self.N) + 1
        return (i, j, v), literal > 0

    def generate_base_constraints(self):
        """Tạo các ràng buộc cơ bản của lưới Futoshiki"""
        N = self.N
        
        # A1 & A2: Mỗi ô có đúng 1 giá trị (At least one & At most one)
        for i in range(1, N + 1):
            for j in range(1, N + 1):
                # Ít nhất 1 giá trị
                self.clauses.append([self.encode(i, j, v) for v in range(1, N + 1)])
                # Nhiều nhất 1 giá trị
                for v1 in range(1, N + 1):
                    for v2 in range(v1 + 1, N + 1):
                        self.clauses.append([-self.encode(i, j, v1), -self.encode(i, j, v2)])

        # A3: Các giá trị trên một hàng phải phân biệt
        for i in range(1, N + 1):
            for v in range(1, N + 1):
                for j1 in range(1, N + 1):
                    for j2 in range(j1 + 1, N + 1):
                        self.clauses.append([-self.encode(i, j1, v), -self.encode(i, j2, v)])

        # Tương tự A3: Các giá trị trên một cột phải phân biệt
        for j in range(1, N + 1):
            for v in range(1, N + 1):
                for i1 in range(1, N + 1):
                    for i2 in range(i1 + 1, N + 1):
                        self.clauses.append([-self.encode(i1, j, v), -self.encode(i2, j, v)])

    def add_given_clue(self, i, j, v):
        """A5: Thêm mệnh đề cho các ô đã có sẵn giá trị (Given)"""
        self.clauses.append([self.encode(i, j, v)])

    def add_horizontal_constraint(self, i, j, relation):
        """
        A4: Ràng buộc hàng ngang.
        relation = 1 (Left < Right), relation = -1 (Left > Right)
        """
        N = self.N
        for v1 in range(1, N + 1):
            for v2 in range(1, N + 1):
                if relation == 1 and v1 >= v2: # Nếu Left < Right mà v1 >= v2 thì mâu thuẫn
                    self.clauses.append([-self.encode(i, j, v1), -self.encode(i, j + 1, v2)])
                elif relation == -1 and v1 <= v2: # Nếu Left > Right mà v1 <= v2 thì mâu thuẫn
                    self.clauses.append([-self.encode(i, j, v1), -self.encode(i, j + 1, v2)])

    def add_vertical_constraint(self, i, j, relation):
        """
        Ràng buộc hàng dọc.
        relation = 1 (Top < Bottom), relation = -1 (Top > Bottom)
        """
        N = self.N
        for v1 in range(1, N + 1):
            for v2 in range(1, N + 1):
                if relation == 1 and v1 >= v2:
                    self.clauses.append([-self.encode(i, j, v1), -self.encode(i + 1, j, v2)])
                elif relation == -1 and v1 <= v2:
                    self.clauses.append([-self.encode(i, j, v1), -self.encode(i + 1, j, v2)])

    def get_kb(self):
        """Trả về toàn bộ Ground KB dưới dạng danh sách các mệnh đề CNF"""
        return self.clauses