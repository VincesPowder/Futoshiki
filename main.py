import os
from kb_generator import KBGenerator
from a_star import FutoshikiAStar
from baseline_solvers import FutoshikiBaseline
from forward_chaining import ForwardChaining, format_solution as fc_format

def parse_input_file(filepath):
    """Đọc và parse file input theo định dạng yêu cầu của đồ án."""
    with open(filepath, 'r') as f:
        # Bỏ qua các dòng chú thích bắt đầu bằng '#' và các dòng trống
        lines = [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]
    
    N = int(lines[0])

    # Thêm int(x.strip()) để xử lý "0, 1, 0" lẫn "0,1,0"
    def parse_row(line):
        return [int(x.strip()) for x in line.split(',')]
    
    # Đọc lưới giá trị ban đầu (Grid)
    grid = [list(map(int, line.split(','))) for line in lines[1:N+1]]
    
    # Đọc ràng buộc ngang (Horizontal constraints)
    horiz_constraints = [list(map(int, line.split(','))) for line in lines[N+1:2*N+1]]
    
    # Đọc ràng buộc dọc (Vertical constraints)
    vert_constraints = [list(map(int, line.split(','))) for line in lines[2*N+1:3*N]]
    
    return N, grid, horiz_constraints, vert_constraints

def build_knowledge_base(N, grid, horiz, vert):
    """Sử dụng KBGenerator để thiết lập Ground KB từ dữ liệu parse được."""
    kb_gen = KBGenerator(N)
    kb_gen.generate_base_constraints()
    
    # Thêm các ô cho trước (Given)
    for i in range(N):
        for j in range(N):
            if grid[i][j] != 0:
                kb_gen.add_given_clue(i + 1, j + 1, grid[i][j])
                
    # Thêm ràng buộc ngang
    for i in range(N):
        for j in range(N - 1):
            if horiz[i][j] != 0:
                kb_gen.add_horizontal_constraint(i + 1, j + 1, horiz[i][j])
                
    # Thêm ràng buộc dọc
    for i in range(N - 1):
        for j in range(N):
            if vert[i][j] != 0:
                kb_gen.add_vertical_constraint(i + 1, j + 1, vert[i][j])

    kb_gen.raw_grid = grid
    kb_gen.raw_horiz = horiz
    kb_gen.raw_vert = vert
                
    return kb_gen

# ==========================================
def solve_forward_chaining(kb_gen):
    """
    TODO: Triển khai thuật toán Forward Chaining
    Sinh viên được giao task này sẽ implement thuật toán tại đây.
    """
    print("Running Forward Chaining...")
    solver = ForwardChaining(kb_gen.N, kb_gen.raw_grid, kb_gen.raw_horiz, kb_gen.raw_vert)
    data = solver.solve()  # trả về dict: result, time, inferences, memory, success
    
    if data and data['success']:
        print("\n" + "="*40)
        print(f"{'THÔNG SỐ HIỆU NĂNG FORWARD CHAINING':^40}")
        print("="*40)
        print(f"1. Thời gian chạy:  {data['time']:.6f} giây")
        print(f"2. Số suy diễn:     {data['inferences']} lần")
        print(f"3. Bộ nhớ tiêu thụ: {data['memory']:.4f} MB")
        print("-" * 40)
        print("KẾT QUẢ BẢNG:")
        for row in data['result']:
            print(f"   {row}")
        print("="*40)
    else:
        print("Không tìm thấy lời giải.")
    pass

def solve_backward_chaining(kb_gen):
    """
    Chạy Backward Chaining cho file input hiện tại.
    In ngắn gọn ra Terminal đầy đủ thông số, chi tiết lưu trong log.
    """
    print("   -> Đang chạy Backward Chaining (Chi tiết lưu tại 'backward_chaining.log')...")
    
    # Khởi tạo solver và thực hiện giải
    from backward_chaining import BackwardChainingSolver
    solver = BackwardChainingSolver(kb_gen)
    data = solver.run()

    # In kết quả đầy đủ các thông số
    if data["success"]:
        print(f"       Giải xong bằng Logic! Time: {data['time']:.4f}s | Memory: {data['memory']:.2f} MB | Nodes: {data['nodes']}")
    else:
        # Backward Chaining thường không giải được 100% ô trống nếu thiếu Fact
        print(f"       Logic không đủ mạnh để phủ kín lưới này! Time: {data['time']:.4f}s | Memory: {data['memory']:.2f} MB | Nodes: {data['nodes']}")
    
    return data

def solve_a_star(kb_gen):
    """
    TODO: Triển khai thuật toán A* với heuristic
    """
    print("Running A* Search...")
    N, grid, horiz, vert = kb_gen.N, kb_gen.raw_grid, kb_gen.raw_horiz, kb_gen.raw_vert
    
    solver = FutoshikiAStar(N, grid, horiz, vert)
    data = solver.solve()

    if data:
        print("\n" + "="*40)
        print(f"{'THÔNG SỐ HIỆU NĂNG A*':^40}")
        print("="*40)
        print(f"1. Thời gian chạy:    {data['time']:.6f} giây")
        print(f"2. Số nút đã mở rộng: {data['nodes']} nút")
        print(f"3. Bộ nhớ tiêu thụ:   {data['memory']:.4f} MB")
        print("-" * 40)
        print("KẾT QUẢ BẢNG:")
        for row in data['result']:
            print(f"   {row}")
        print("="*40)
    else:
        print("Không tìm thấy lời giải.")


def solve_brute_force(kb_gen):
    N, grid, horiz, vert = kb_gen.N, kb_gen.raw_grid, kb_gen.raw_horiz, kb_gen.raw_vert
    # Thiết lập giới hạn 10 giây cho mỗi thuật toán baseline
    solver = FutoshikiBaseline(N, grid, horiz, vert, time_limit=10)

    # 1. Chạy Backtracking
    print("\n--- Running Backtracking (Baseline) ---")
    data_bt = solver.run(mode="backtracking")
    if data_bt["success"]:
        print(f"Time: {data_bt['time']:.6f}s | Nodes: {data_bt['nodes']} | Mem: {data_bt['memory']:.4f}MB")
    elif data_bt["timeout"]:
        print(f"!!! TIMEOUT: Backtracking dừng sau {data_bt['time']:.2f}s.")
    else:
        print("Không tìm thấy lời giải.")
    
    # 2. Chạy Brute-force (Chỉ chạy khi N <= 4 hoặc để so sánh sự bùng nổ tổ hợp)
    if N <= 4:
        print("--- Running Brute-force (Naive) ---")
        data_bf = solver.run(mode="brute-force")
        if data_bf["success"]:
            print(f"Time: {data_bf['time']:.6f}s | Nodes: {data_bf['nodes']} | Mem: {data_bf['memory']:.4f}MB")
        elif data_bf["timeout"]:
            print(f"!!! TIMEOUT: Brute-force ngắt sau {data_bf['time']:.2f}s | Nodes {data_bf['nodes']} | Mem: {data_bf['memory']:.4f}MB.")
    else:
        print(f"Skipping Brute-force for N={N} to avoid hanging.")
    
    return data_bt # Luôn trả về kết quả Backtracking để hàm main ghi file output

# ==========================================

def main():
    input_dir = 'Inputs'
    output_dir = 'Outputs'
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    print("="*70)
    print(f"{'HỆ THỐNG GIẢI ĐỐ FUTOSHIKI - AI PROJECT 2':^70}")
    print("="*70)

    # Duyệt qua các file input từ input-01.txt đến input-10.txt
    for filename in sorted(os.listdir(input_dir)):
        if filename.endswith('.txt'):
            filepath = os.path.join(input_dir, filename)
            print(f"\n[XỬ LÝ] {filename}")
            
            try:
                # 1. Đọc file và xây dựng Knowledge Base 
                N, grid, horiz, vert = parse_input_file(filepath)
                kb_gen = build_knowledge_base(N, grid, horiz, vert)
                print(f"   KB khởi tạo thành công với {len(kb_gen.get_kb())} mệnh đề.")
                
                # 2. CHẠY SO SÁNH CÁC THUẬT TOÁN 
                print("\n>>> SO SÁNH HIỆU NĂNG GIỮA CÁC CHIẾN LƯỢC:")
                
                # Chạy A* (Chiến lược số 5) 
                solve_a_star(kb_gen)
                
                # Chạy Brute-force & Backtracking (Chiến lược số 6) 
                solve_brute_force(kb_gen)
                
                # Chạy Backward Chaining (Chiến lược số 3 - SLD Resolution) 
                # Khi bạn hoàn thiện file backward_chaining.py, hàm này sẽ tự động chạy
                solve_backward_chaining(kb_gen)

                # 3. XUẤT KẾT QUẢ RA FILE THEO ĐỊNH DẠNG 
                # Lấy kết quả từ A* để thực hiện việc ghi file
                from a_star import FutoshikiAStar
                solver = FutoshikiAStar(N, grid, horiz, vert)
                data = solver.solve()
                
                if data and 'result' in data:
                    solved_grid = data['result']
                    out_path = os.path.join(output_dir, filename.replace('input', 'output'))
                    
                    with open(out_path, 'w', encoding='utf-8') as f:
                        for i in range(N):
                            # Hàng chứa số và dấu bất đẳng thức ngang
                            row_str = ""
                            for j in range(N):
                                row_str += str(solved_grid[i][j])
                                if j < N - 1:
                                    # horiz[i][j] = 1 là '<', -1 là '>'
                                    sign = " < " if horiz[i][j] == 1 else (" > " if horiz[i][j] == -1 else "   ")
                                    row_str += sign
                            f.write(row_str.rstrip() + "\n")
                            
                            # Hàng chứa các dấu bất đẳng thức dọc
                            if i < N - 1:
                                vert_str = ""
                                for j in range(N):
                                    # vert[i][j] = 1 là '^' (top < bot), -1 là 'v' (top > bot)
                                    sign = "^" if vert[i][j] == 1 else ("v" if vert[i][j] == -1 else " ")
                                    # Căn lề: Mỗi số chiếm 1 ký tự, dấu ngang chiếm 3 ký tự (tổng cụm là 4).
                                    # Dấu dọc nằm dưới số nên cần 3 khoảng trắng sau nó để thẳng hàng cột tiếp theo.
                                    vert_str += sign + ("   " if j < N - 1 else "")
                                f.write(vert_str.rstrip() + "\n")
                    print(f"\n   => Đã xuất kết quả thành công ra file: {out_path}")
                
            except Exception as e:
                print(f"   [LỖI] {filename}: {str(e)}")

    print("\n" + "="*70)
    print(f"{'HOÀN THÀNH PHÂN TÍCH VÀ TRÍCH XUẤT DỮ LIỆU':^70}")
    print("="*70)



if __name__ == "__main__":
    # Đảm bảo bạn đã có thư mục Inputs và chứa các file .txt chuẩn format trước khi chạy
    main()