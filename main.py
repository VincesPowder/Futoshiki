import os
import time
from datetime import datetime
from kb_generator import KBGenerator

# Import các solver từ project của ông
from a_star import FutoshikiAStar
from baseline_solvers import FutoshikiBaseline
from forward_chaining import ForwardChaining
from backward_chaining import BackwardChainingSolver

def parse_input_file(filepath):
    """Đọc và parse file input theo định dạng yêu cầu."""
    with open(filepath, 'r') as f:
        lines = [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]
    N = int(lines[0])
    grid = [list(map(int, line.split(','))) for line in lines[1:N+1]]
    horiz = [list(map(int, line.split(','))) for line in lines[N+1:2*N+1]]
    vert = [list(map(int, line.split(','))) for line in lines[2*N+1:3*N]]
    return N, grid, horiz, vert

def build_knowledge_base(N, grid, horiz, vert):
    """
    Yêu cầu 1 & 2: Ground the KB & Convert to CNF.
    Thiết lập Ground KB thông qua KBGenerator.
    """
    kb_gen = KBGenerator(N)
    kb_gen.generate_base_constraints()
    for i in range(N):
        for j in range(N):
            if grid[i][j] != 0:
                kb_gen.add_given_clue(i + 1, j + 1, grid[i][j])
    for i in range(N):
        for j in range(N - 1):
            if horiz[i][j] != 0:
                kb_gen.add_horizontal_constraint(i + 1, j + 1, horiz[i][j])
    for i in range(N - 1):
        for j in range(N):
            if vert[i][j] != 0:
                kb_gen.add_vertical_constraint(i + 1, j + 1, vert[i][j])
    kb_gen.raw_grid, kb_gen.raw_horiz, kb_gen.raw_vert = grid, horiz, vert
    return kb_gen

def write_performance_log(log_path, filename, solver_name, data):
    """Ghi log hiệu năng vào file log.txt với format giữ nguyên."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if data is None:
        data = {'success': False, 'nodes': 0, 'time': 0, 'memory': 0, 'result': None}
    is_solved = data.get('success', data.get('result') is not None)
    sol_length = "N/A"
    if data.get('result'):
        sol_length = sum(1 for row in data['result'] for val in row if val != 0)
    elif data.get('length'):
        sol_length = data['length']

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] Test Case: {filename} | Solver: {solver_name}\n")
        f.write("Results:\n")
        f.write(f"  Solved: {is_solved}\n")
        f.write(f"  Solution length: {sol_length}\n")
        f.write(f"  Expanded nodes/ Number of inferences: {data.get('nodes', 0)}\n")
        f.write(f"  Search time: {data.get('time', 0) * 1000:.2f}ms\n")
        f.write(f"  Memory used: {data.get('memory', 0):.4f}KB\n")
        f.write("-" * 40 + "\n")

def export_output(output_dir, filename, result, horiz, vert, N):
    if not result: return
    out_path = os.path.join(output_dir, filename.replace('input', 'output'))
    with open(out_path, 'w', encoding='utf-8') as f:
        for i in range(N):
            row_str = ""
            for j in range(N):
                row_str += str(result[i][j])
                if j < N - 1:
                    sign = " < " if horiz[i][j] == 1 else (" > " if horiz[i][j] == -1 else "   ")
                    row_str += sign
            f.write(row_str.rstrip() + "\n")
            if i < N - 1:
                vert_str = ""
                for j in range(N):
                    sign = "^" if vert[i][j] == 1 else ("v" if vert[i][j] == -1 else " ")
                    vert_str += sign + ("   " if j < N - 1 else "")
                f.write(vert_str.rstrip() + "\n")

def main():
    input_dir, output_dir = 'Inputs', 'Outputs'
    summary_log = 'log.txt'
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    if os.path.exists(summary_log): os.remove(summary_log)
        
    print("="*70)
    print(f"{'HỆ THỐNG GIẢI ĐỐ FUTOSHIKI':^70}")
    print("="*70)

    for filename in sorted(os.listdir(input_dir)):
        if filename.endswith('.txt'):
            filepath = os.path.join(input_dir, filename)
            print(f"\n[XỬ LÝ] {filename}")
            try:
                # BƯỚC 1 & 2: GROUND KB & CNF (Thực hiện trong build_knowledge_base)
                N, grid, horiz, vert = parse_input_file(filepath)
                kb_gen = build_knowledge_base(N, grid, horiz, vert)
                # (Không in log hiệu năng cho bước này vì đây là bước chuẩn bị KB)
                
                # BƯỚC 3: FORWARD CHAINING
                fc = ForwardChaining(N, grid, horiz, vert)
                fc_data = fc.solve()
                write_performance_log(summary_log, filename, "Forward Chaining", fc_data)

                # BƯỚC 4: PROLOG-STYLE BACKWARD CHAINING
                bc_solver = BackwardChainingSolver(kb_gen)
                bc_data = bc_solver.run(test_label=filename)
                write_performance_log(summary_log, filename, "Backward Chaining", bc_data)  

                # BƯỚC 5: A* GUIDED SEARCH
                astar = FutoshikiAStar(N, grid, horiz, vert)
                astar_data = astar.solve()
                write_performance_log(summary_log, filename, "A*", astar_data)

                # BƯỚC 6: BRUTE-FORCE & BACKTRACKING (BASELINE)
                baseline = FutoshikiBaseline(N, grid, horiz, vert)
                
                # 6.1 Backtracking
                bt_data = baseline.run(mode="backtracking")
                write_performance_log(summary_log, filename, "Backtracking", bt_data)
                
                # 6.2 Brute-force
                bf_data = baseline.run(mode="brute_force")
                write_performance_log(summary_log, filename, "Brute-force", bf_data)
                
                

               # Xuất file Output mẫu (Ưu tiên A*, sau đó tới FC, cuối cùng mới tới Backtracking)
                if astar_data and astar_data.get('success'):
                    export_output(output_dir, filename, astar_data['result'], horiz, vert, N)
                    print(f"   => Đã xuất kết quả ra {output_dir} (Dùng A*)")
                elif fc_data and fc_data.get('success'):
                    export_output(output_dir, filename, fc_data['result'], horiz, vert, N)
                    print(f"   => Đã xuất kết quả ra {output_dir} (Dùng Forward Chaining)")
                elif bt_data and bt_data.get('success'):
                    export_output(output_dir, filename, bt_data['result'], horiz, vert, N)
                    print(f"   => Đã xuất kết quả ra {output_dir} (Dùng Backtracking)")
                else:
                    print(f"   => KHÔNG XUẤT ĐƯỢC KẾT QUẢ (Tất cả thuật toán đều thất bại/timeout)")

            except Exception as e:
                print(f"   [LỖI] {filename}: {str(e)}")

    print("\n" + "="*70)
    print(f"{'HOÀN THÀNH TẤT CẢ THUẬT TOÁN.':^70}")
    print("="*70)

if __name__ == "__main__":
    main()