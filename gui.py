import pygame
import os
import glob
import sys
import time
import threading

from a_star import FutoshikiAStar
from forward_chaining import ForwardChaining
from baseline_solvers import FutoshikiBaseline
from backward_chaining import BackwardChainingSolver
from kb_generator import KBGenerator
# ---------------------------------------------

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
PANEL_Y = 600

pygame.init()
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Futoshiki Solver")

FONT = pygame.font.SysFont('tahoma', 16)
ICON_FONT = pygame.font.SysFont('arial', 40)
LARGE_FONT = pygame.font.SysFont('tahoma', 32, bold=True)

class FutoshikiGame:
    def __init__(self):
       # --- LOG SCREEN VARIABLES ---
        self.log = ["Welcome to Futoshiki Solver!", "Select a Testcase to begin."]
        self.log_offset = 0
        self.max_log_lines = 4 
        self.log_font = pygame.font.SysFont("consolas", 16)
        
        # X=20, Y=610, Rộng=900, Cao=100
        self.log_rect = pygame.Rect(20, PANEL_Y + 10, 900, 100)
        
        self.N = 0
        self.grid = []
        self.horiz_constraints = []
        self.vert_constraints = []
        self.solved_grid = None
        
        self.log = ["Welcome to Futoshiki Solver!", "Select a Testcase to begin."]
        self.log_offset = 0
        
        self.button_highlight_time = {}
        self.highlight_duration = 0.15
        self.stop_event = threading.Event()
             
        # --- MENU SOLVER (Mọc lên trên nút Solver) ---
        self.solver_menu_open = False
        self.solver_selected = "Forward Chaining"
        algo_names = ["Forward Chaining", "Backward Chaining", "A* Search", "Backtracking", "Brute Force"]
        self.solver_menu = {}
        for i, algo in enumerate(algo_names):
            # Căn chỉnh theo X=940 của nút Solver
            self.solver_menu[algo] = pygame.Rect(930, (PANEL_Y - 170) + i * 32, 145, 30)# Tăng W lên 145 để chứa vừa chữ "Backward Chaining"
            
        W, H = 145, 45 
        
        # Dời X của cột 1 sang 930 một chút để lấy chỗ cho nút to ra
        # Cột 2 vẫn giữ ở 1090
        self.buttons = {
            "Solver":  pygame.Rect(930, PANEL_Y + 10, W, H),
            "Test":    pygame.Rect(1090, PANEL_Y + 10, W, H),
            "Restart": pygame.Rect(930, PANEL_Y + 65, W, H),
            "Quit":    pygame.Rect(1090, PANEL_Y + 65, W, H),
        }
        
       
        # --- MENU TEST (Đọc từ folder Inputs) ---
        self.test_menu_open = False
        self.test_menu = {}
        self.test_menu_scroll_offset = 0
        self.max_visible_tests = 5
        self.load_testcases_to_menu()
        
        self.solver_running = False
        self.current_test_name = None

        self.MainLoop()

    def draw_log_screen(self):
        # 1. Vẽ nền trắng
        pygame.draw.rect(SCREEN, (255, 255, 255), self.log_rect)
        # 2. Vẽ viền màu hồng (Pink) với độ dày là 4 pixel
        pygame.draw.rect(SCREEN, (255, 182, 193), self.log_rect, 4)
    def draw_log_screen(self):
        # 1. Vẽ nền trắng và viền hồng
        pygame.draw.rect(SCREEN, (255, 255, 255), self.log_rect)
        pygame.draw.rect(SCREEN, (255, 182, 193), self.log_rect, 4)

        total_logs = len(self.log)
        max_offset = max(0, total_logs - self.max_log_lines)
        
        # Đảm bảo log_offset không bị vượt quá giới hạn
        self.log_offset = max(0, min(self.log_offset, max_offset))

        # 2. Cắt danh sách log dựa trên vị trí cuộn
        end_idx = total_logs - self.log_offset
        start_idx = max(0, end_idx - self.max_log_lines)
        visible_logs = self.log[start_idx:end_idx]

        # 3. In chữ
        y_offset = self.log_rect.y + 10
        for line in visible_logs:
            text_surface = self.log_font.render(line, True, (0, 0, 0)) 
            SCREEN.blit(text_surface, (self.log_rect.x + 10, y_offset))
            y_offset += 20

        # 4. Vẽ thanh cuộn (Scrollbar) nếu có nhiều hơn 4 dòng
        if total_logs > self.max_log_lines:
            sb_width = 12
            # Đặt thanh cuộn sát lề phải, lùi vào 12px
            sb_rect = pygame.Rect(self.log_rect.right - sb_width - 12, self.log_rect.y + 4, sb_width, self.log_rect.height - 8)
            
            # Nền xám nhạt của thanh cuộn
            pygame.draw.rect(SCREEN, (240, 240, 240), sb_rect, border_radius=4) 
            
            # Tính chiều cao của "tay cầm" (thumb)
            thumb_h = max(20, int(sb_rect.height * (self.max_log_lines / total_logs)))
            
            # Tính tọa độ Y của tay cầm (cuộn lên thì thumb chạy lên, cuộn xuống thì thumb chạy xuống)
            thumb_y = sb_rect.bottom - thumb_h - (self.log_offset / max_offset) * (sb_rect.height - thumb_h)
            
            thumb_rect = pygame.Rect(sb_rect.x, thumb_y, sb_width, thumb_h)
            
            # Vẽ tay cầm thanh cuộn màu hồng
            pygame.draw.rect(SCREEN, (255, 182, 193), thumb_rect, border_radius=4)
            
    def load_testcases_to_menu(self):
        files = sorted(glob.glob(os.path.join("Inputs", "*.txt")))
        self.test_menu = {os.path.basename(f): f for f in files}

    def parse_input_file(self, filepath):
        try:
            with open(filepath, 'r') as f:
                lines = [line.split('#')[0].strip() for line in f.readlines()]
                lines = [line for line in lines if line]
                
                self.N = int(lines[0])
                self.grid = [[int(x) for x in lines[i].split(',')] for i in range(1, self.N + 1)]
                self.horiz_constraints = [[int(x) for x in lines[i].split(',')] for i in range(self.N + 1, 2 * self.N + 1)]
                self.vert_constraints = [[int(x) for x in lines[i].split(',')] for i in range(2 * self.N + 1, 3 * self.N)]
            self.solved_grid = None
            self.log.append(f"Loaded {os.path.basename(filepath)} ({self.N}x{self.N})")
            self.log_offset = 0
        except Exception as e:
            self.log.append(f"Lỗi đọc file: {e}")
            self.log_offset = 0

    def run_solver_thread(self):
        self.log.append(f"Running {self.solver_selected}...")
        self.log_offset = 0
        
        # 1. Khởi tạo Knowledge Base (Cần thiết cho Backward Chaining)
        kb_gen = KBGenerator(self.N)
        kb_gen.generate_base_constraints()
        for r in range(self.N):
            for c in range(self.N):
                if self.grid[r][c] != 0:
                    kb_gen.add_given_clue(r + 1, c + 1, self.grid[r][c])
                    
        for r in range(self.N):
            for c in range(self.N - 1):
                if self.horiz_constraints[r][c] != 0:
                    kb_gen.add_horizontal_constraint(r + 1, c + 1, self.horiz_constraints[r][c])
                    
        for r in range(self.N - 1):
            for c in range(self.N):
                if self.vert_constraints[r][c] != 0:
                    kb_gen.add_vertical_constraint(r + 1, c + 1, self.vert_constraints[r][c])
        
        # 2. Chạy thuật toán tương ứng
        data = None
        try:
            if self.solver_selected == "A* Search":
                solver = FutoshikiAStar(self.N, self.grid, self.horiz_constraints, self.vert_constraints)
                data = solver.solve()
                
            elif self.solver_selected == "Forward Chaining":
                solver = ForwardChaining(self.N, self.grid, self.horiz_constraints, self.vert_constraints)
                data = solver.solve()
                
            elif self.solver_selected == "Backward Chaining":
                solver = BackwardChainingSolver(kb_gen)
                data = solver.run()
                
            elif self.solver_selected == "Backtracking":
                solver = FutoshikiBaseline(self.N, self.grid, self.horiz_constraints, self.vert_constraints, time_limit=30)
                data = solver.run(mode="backtracking")
                
            elif self.solver_selected == "Brute Force":
                # Gọi mode khác "backtracking" để baseline_solvers chạy brute force thuần túy
                solver = FutoshikiBaseline(self.N, self.grid, self.horiz_constraints, self.vert_constraints, time_limit=30)
                data = solver.run(mode="brute_force")

            # 3. Process the returned results (English Logs)
            if self.stop_event.is_set():
                self.log.append("Action: Solver stopped by user.")
            else:
                if data:
                    # 1. Trường hợp quá giờ (Riêng cho Backtracking / Brute Force)
                    if data.get("timeout"):
                        self.log.append(f"Result: TIMEOUT!")
                        self.solved_grid = None # Xóa trắng kết quả ảo
                        
                    # 2. Trường hợp giải THÀNH CÔNG thực sự
                    elif data.get("success"):
                        self.log.append(f"Result: Solved successfully using {self.solver_selected}")
                        if "time" in data:
                            self.log.append(f"Search time: {data['time']:.4f} seconds")
                        if "nodes" in data or "visited" in data:
                            node_count = data.get("nodes", data.get("visited", "N/A"))
                            self.log.append(f"Expanded nodes: {node_count}")
                            
                        self.solved_grid = data["result"] # Chỉ cập nhật bảng khi thành công
                        
                    # 3. Trường hợp thất bại hoặc giải dang dở (Backward Chaining)
                    else:
                        if self.solver_selected == "Backward Chaining":
                            self.log.append("Result: Grid partially solved (Logic insufficient).")
                            self.solved_grid = data["result"] # Cho phép vẽ bảng dở dang
                        else:
                            self.log.append("Result: No solution found!")
                            self.solved_grid = None
                else:
                    self.log.append("Result: Error or no data returned!")

        except Exception as e:
            self.log.append(f"Error: {str(e)}")

        self.solver_running = False

    def GetClickedElement(self, pos):
        # Kiểm tra click vào nút Test Menu
        if self.buttons["Test"].collidepoint(pos):
            return "BTN_Test"
            
        # Kiểm tra click vào nút Solver Menu
        if self.buttons["Solver"].collidepoint(pos):
            return "BTN_Solver"
            
        # Kiểm tra click menu Test (đang mở)
        if self.test_menu_open:
            visible_tests = list(self.test_menu.keys())[self.test_menu_scroll_offset:self.test_menu_scroll_offset + self.max_visible_tests]
            for idx, test_name in enumerate(visible_tests):
                rect = pygame.Rect(1090, (PANEL_Y - 170) + idx * 32, 145, 30)
                if rect.collidepoint(pos):
                    return f"TEST_{test_name}"
                    
        # Kiểm tra click menu Solver (đang mở)
        if self.solver_menu_open:
            for algo, rect in self.solver_menu.items():
                if rect.collidepoint(pos):
                    return f"ALGO_{algo}"
                    
        # Kiểm tra các nút còn lại
        for name, rect in self.buttons.items():
            if name not in ["Test", "Solver"] and rect.collidepoint(pos):
                return f"BTN_{name}"
                
        return None

    def MainLoop(self):
        clock = pygame.time.Clock()
        while True:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); return

                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Xử lý cuộn chuột
                    # Xử lý cuộn chuột
                    if event.button == 4:  # Scroll up
                        test_menu_area = pygame.Rect(1090, PANEL_Y - 180, 150, 170)
                        if self.test_menu_open and test_menu_area.collidepoint(event.pos):
                            self.test_menu_scroll_offset = max(0, self.test_menu_scroll_offset - 1)
                        # Cuộn log (nếu trỏ chuột vào log)
                        elif self.log_rect.collidepoint(event.pos):
                            self.log_offset = min(self.log_offset + 1, max(0, len(self.log) - self.max_log_lines))
                            
                    elif event.button == 5:  # Scroll down
                        test_menu_area = pygame.Rect(1090, PANEL_Y - 180, 150, 170)
                        if self.test_menu_open and test_menu_area.collidepoint(event.pos):
                            max_offset = max(0, len(self.test_menu) - self.max_visible_tests)
                            self.test_menu_scroll_offset = min(self.test_menu_scroll_offset + 1, max_offset)
                        # Cuộn log
                        elif self.log_rect.collidepoint(event.pos):
                            self.log_offset = max(self.log_offset - 1, 0)
                            
                    # Xử lý Click trái
                    elif event.button == 1:
                        clicked = self.GetClickedElement(event.pos)
                        
                        if clicked == "BTN_Test":
                            self.test_menu_open = not self.test_menu_open
                            self.solver_menu_open = False
                            self.button_highlight_time["Test"] = time.time()
                            
                        elif clicked == "BTN_Solver":
                            if not self.solver_running:
                                self.solver_menu_open = not self.solver_menu_open
                                self.test_menu_open = False
                                self.button_highlight_time["Solver"] = time.time()
                            else:
                                self.log.append("Cannot change solver while running.")
                                self.log_offset = 0
                                
                        elif clicked == "BTN_Restart":
                            # Nếu thuật toán đang chạy, dừng nó lại
                            if self.solver_running:
                                self.stop_event.set()
                            
                            # Tải lại testcase nếu đã có testcase được chọn
                            if self.current_test_name:
                                self.parse_input_file(self.test_menu[self.current_test_name])
                                self.log.append(f"Restarted testcase: {self.current_test_name}")
                            else:
                                self.log.append("Vui lòng chọn testcase trước khi Restart!")
                                
                            self.log_offset = 0
                            self.button_highlight_time["Restart"] = time.time()
                            
                        elif clicked == "BTN_Quit":
                            pygame.quit(); return
                            
                        elif clicked and clicked.startswith("TEST_"):
                            test_name = clicked.replace("TEST_", "")
                            self.current_test_name = test_name
                            self.parse_input_file(self.test_menu[test_name])
                            self.test_menu_open = False
                            
                        elif clicked and clicked.startswith("ALGO_"):
                            algo = clicked.replace("ALGO_", "")
                            self.solver_selected = algo
                            self.solver_menu_open = False
                            if self.N > 0:
                                self.stop_event.clear()
                                self.solver_running = True
                                threading.Thread(target=self.run_solver_thread, daemon=True).start()
                            else:
                                self.log.append("Please load a testcase first!")
                                self.log_offset = 0

            self.UpdateScreen(mouse_pos)
            clock.tick(60)

    def draw_rounded_rect_with_border(self, surface, rect, bg_color, border_color_outer, border_color_inner):
        # Nền màu
        pygame.draw.rect(surface, bg_color, rect, border_radius=5)
        # Viền ngoài (Hồng đậm)
        pygame.draw.rect(surface, border_color_outer, rect, 2, border_radius=5)
        # Viền trong (Trắng)
        inner_rect = rect.inflate(-4, -4)
        pygame.draw.rect(surface, border_color_inner, inner_rect, 2, border_radius=3)

    def UpdateScreen(self, mouse_pos):
        # 1. Background cho toàn bộ màn hình
        bg_dark = (20, 40, 50)
        SCREEN.fill(bg_dark) 
        
        # 2. Panel ở dưới cùng (khu vực chứa menu, log)
        pygame.draw.rect(SCREEN, (30, 65, 70), (0, PANEL_Y, SCREEN_WIDTH, 120))

        board_size = min(500, SCREEN_HEIGHT - 160)
        start_x = (SCREEN_WIDTH - board_size) // 2
        start_y = (PANEL_Y - board_size) // 2

        hole_padding = 15 # Tạo khoảng lề 15px cho bàn cờ thở
        hole_rect = pygame.Rect(start_x - hole_padding, start_y - hole_padding, board_size + hole_padding, board_size + hole_padding)
        self.draw_rounded_rect_with_border(SCREEN, hole_rect, (30, 65, 70), (155, 50, 100), (255, 255, 255))
        
        welcome_font = pygame.font.SysFont('trebuchet ms', 70, bold=True, italic=True)
        welcome_surf = welcome_font.render("WELCOME!", True, (70, 90, 110))
        welcome_surf.set_alpha(100) 
        text_rect = welcome_surf.get_rect(center=hole_rect.center)
        SCREEN.blit(welcome_surf, text_rect)
        # --- VẼ NÚT BẤM
        for name, rect in self.buttons.items():
            is_highlighted = False
            if name == "Test" and self.test_menu_open: is_highlighted = True
            elif name == "Solver" and self.solver_menu_open: is_highlighted = True
            elif name in self.button_highlight_time:
                if time.time() - self.button_highlight_time[name] < self.highlight_duration:
                    is_highlighted = True
                else: del self.button_highlight_time[name]
            
            color = (200, 230, 150) if is_highlighted else (255, 200, 230)
            self.draw_rounded_rect_with_border(SCREEN, rect, color, (155, 50, 100), (255, 255, 255))
            
            text_surf = FONT.render(name, True, (155, 50, 100))
            SCREEN.blit(text_surf, text_surf.get_rect(center=rect.center))

        # --- VẼ MENU SOLVER ---
        if self.solver_menu_open:
            for algo, rect in self.solver_menu.items():
                color = (200, 230, 150) if self.solver_selected == algo else (255, 200, 230)
                self.draw_rounded_rect_with_border(SCREEN, rect, color, (155, 50, 100), (255, 255, 255))
                item_text = FONT.render(algo, True, (155, 50, 100))
                SCREEN.blit(item_text, item_text.get_rect(center=rect.center))

        # --- VẼ MENU TEST & THANH CUỘN ---
        if self.test_menu_open:
            visible_tests = list(self.test_menu.keys())[self.test_menu_scroll_offset:self.test_menu_scroll_offset + self.max_visible_tests]
            for idx, test_name in enumerate(visible_tests):
                test_rect = pygame.Rect(1090, (PANEL_Y - 170) + idx * 32, 145, 30)
                color = (200, 230, 150) if self.current_test_name == test_name else (255, 200, 230)
                self.draw_rounded_rect_with_border(SCREEN, test_rect, color, (155, 50, 100), (255, 255, 255))
                item_text = FONT.render(test_name, True, (155, 50, 100))
                SCREEN.blit(item_text, item_text.get_rect(center=test_rect.center))
            
            if len(self.test_menu) > self.max_visible_tests:
                scroll_bar_x, scroll_bar_y, scroll_bar_w = 1240, PANEL_Y - 165, 8
                total_h = self.max_visible_tests * 30
                pygame.draw.rect(SCREEN, (255, 200, 230), (scroll_bar_x, scroll_bar_y, scroll_bar_w, total_h))
                max_offset = len(self.test_menu) - self.max_visible_tests
                thumb_h = max(10, int(total_h * self.max_visible_tests / len(self.test_menu)))
                thumb_pos = scroll_bar_y + (self.test_menu_scroll_offset / max_offset if max_offset > 0 else 0) * (total_h - thumb_h)
                pygame.draw.rect(SCREEN, (155, 50, 100), (scroll_bar_x, thumb_pos, scroll_bar_w, thumb_h), border_radius=2)


        # --- VẼ LƯỚI FUTOSHIKI TRÊN MÀN HÌNH CHÍNH ---
        if self.N > 0:
            board_size = min(500, SCREEN_HEIGHT - 160)
            cell_size = board_size // self.N
            gap = 15
            actual_cell = cell_size - gap
            
            start_x = (SCREEN_WIDTH - board_size) // 2
            start_y = (PANEL_Y - board_size) // 2

            # VÒNG LẶP 1: Vẽ tất cả các ô vuông trắng và số trước
            for r in range(self.N):
                for c in range(self.N):
                    cx = start_x + c * cell_size
                    cy = start_y + r * cell_size

                    # Ô vuông bài
                    cell_rect = pygame.Rect(cx, cy, actual_cell, actual_cell)
                    self.draw_rounded_rect_with_border(SCREEN, cell_rect, (255, 255, 255), (155, 50, 100), (255, 255, 255))
                    
                    val = self.grid[r][c]
                    is_solved = False
                    if val == 0 and self.solved_grid:
                        val = self.solved_grid[r][c]
                        is_solved = True
                        
                    if val != 0:
                        color = (50, 150, 50) if is_solved else (0, 0, 0)
                        txt = LARGE_FONT.render(str(val), True, color)
                        SCREEN.blit(txt, txt.get_rect(center=cell_rect.center))

            # VÒNG LẶP 2: Vẽ các dấu bất đẳng thức bằng Line để nét như chữ mà canh giữa tuyệt đối
            for r in range(self.N):
                for c in range(self.N):
                    cx = start_x + c * cell_size
                    cy = start_y + r * cell_size

                    # Dấu ngang < >
                    if c < self.N - 1 and r < len(self.horiz_constraints):
                        val = self.horiz_constraints[r][c]
                        if val != 0:
                            center_x = cx + actual_cell + gap // 2
                            center_y = cy + actual_cell // 2
                            color = (255, 100, 100) # Đỏ hồng
                            
                            # Kích thước ký hiệu (Rộng 10, Cao 14)
                            tw, th = 10, 14 
                            
                            if val == 1: # Dấu '<'
                                points = [
                                    (center_x + tw//2, center_y - th//2), # Góc trên phải
                                    (center_x - tw//2, center_y),         # Mũi nhọn bên trái
                                    (center_x + tw//2, center_y + th//2)  # Góc dưới phải
                                ]
                            else: # Dấu '>'
                                points = [
                                    (center_x - tw//2, center_y - th//2), # Góc trên trái
                                    (center_x + tw//2, center_y),         # Mũi nhọn bên phải
                                    (center_x - tw//2, center_y + th//2)  # Góc dưới trái
                                ]
                            # Tham số 'False' nghĩa là vẽ đường nét mở (không bị đóng lại thành tam giác)
                            pygame.draw.lines(SCREEN, color, False, points, 3)

                    # Dấu dọc ^ v
                    if r < self.N - 1 and r < len(self.vert_constraints):
                        val = self.vert_constraints[r][c]
                        if val != 0:
                            center_x = cx + actual_cell // 2
                            center_y = cy + actual_cell + gap // 2
                            color = (100, 200, 255) # Xanh dương
                            
                            # Kích thước ký hiệu lật ngược lại (Rộng 14, Cao 10)
                            tw, th = 14, 10 
                            
                            if val == 1: # Dấu '^'
                                points = [
                                    (center_x - tw//2, center_y + th//2), # Góc dưới trái
                                    (center_x, center_y - th//2),         # Mũi nhọn bên trên
                                    (center_x + tw//2, center_y + th//2)  # Góc dưới phải
                                ]
                            else: # Dấu 'v'
                                points = [
                                    (center_x - tw//2, center_y - th//2), # Góc trên trái
                                    (center_x, center_y + th//2),         # Mũi nhọn bên dưới
                                    (center_x + tw//2, center_y - th//2)  # Góc trên phải
                                ]
                            pygame.draw.lines(SCREEN, color, False, points, 3)
        # --- VẼ LOG PANEL ---
        self.draw_log_screen()

        pygame.display.update()

if __name__ == "__main__":
    FutoshikiGame()