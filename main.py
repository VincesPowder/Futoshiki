import os
from kb_generator import KBGenerator

def parse_input_file(filepath):
    """Đọc và parse file input theo định dạng yêu cầu của đồ án."""
    with open(filepath, 'r') as f:
        # Bỏ qua các dòng chú thích bắt đầu bằng '#' và các dòng trống
        lines = [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]
    
    N = int(lines[0])
    
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
                
    return kb_gen

# ==========================================
def solve_forward_chaining(kb_gen):
    """
    TODO: Triển khai thuật toán Forward Chaining
    Sinh viên được giao task này sẽ implement thuật toán tại đây.
    """
    print("Running Forward Chaining...")
    pass

def solve_backward_chaining(kb_gen):
    """
    TODO: Triển khai thuật toán Backward Chaining (SLD Resolution)
    """
    print("Running Backward Chaining...")
    pass

def solve_a_star(kb_gen):
    """
    TODO: Triển khai thuật toán A* với heuristic
    """
    print("Running A* Search...")
    pass

def solve_brute_force(kb_gen):
    """
    TODO: Triển khai Brute-force / Backtracking để đối sánh hiệu năng
    """
    print("Running Brute-force / Backtracking...")
    pass

# ==========================================

def main():
    input_dir = 'Inputs'
    output_dir = 'Outputs'
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Duyệt qua các file input từ input-01.txt đến input-10.txt
    for filename in sorted(os.listdir(input_dir)):
        if filename.endswith('.txt'):
            filepath = os.path.join(input_dir, filename)
            print(f"--- Đang xử lý: {filename} ---")
            
            try:
                N, grid, horiz, vert = parse_input_file(filepath)
                kb_gen = build_knowledge_base(N, grid, horiz, vert)
                
                print(f"Khởi tạo Knowledge Base thành công với {len(kb_gen.get_kb())} mệnh đề (clauses).")
                
                # Tại đây có thể thêm logic dùng argument từ command line để chọn thuật toán
                # Hiện tại gọi thử stub của Forward Chaining
                solve_forward_chaining(kb_gen)
                
                # TODO: Format lại kết quả đầu ra theo yêu cầu và ghi vào thư mục Outputs
                
            except Exception as e:
                print(f"Lỗi khi xử lý file {filename}: {str(e)}")

if __name__ == "__main__":
    # Đảm bảo bạn đã có thư mục Inputs và chứa các file .txt chuẩn format trước khi chạy
    main()