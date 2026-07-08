import pygame
import os
import random
import map_loader
import algorithms

# --- CẤU HÌNH GIAO DIỆN HỆ THỐNG ---
TILE_SIZE = 30
FPS = 60
BG_COLOR = (30, 27, 38)         # Màu nền mê cung
OUTER_BG_COLOR = (15, 15, 25)   # Màu nền không gian ngoài
LEFT_UI_WIDTH = 180             # Chiều rộng Menu trái
MENU_OPEN_WIDTH = 280           # Chiều rộng menu khi mở (2 cột)
RIGHT_UI_WIDTH = 220            # Chiều rộng Thanh lộ trình bên phải

# --- KHỞI TẠO BIẾN CHO CÁC THỰC THỂ (GHOST) ---
ghost_positions = [] 
ghost_animations = [] 
ghost_frame_idx = 0
full_history = []

def draw_logo(screen, x, y, width):
    """Load và vẽ logo từ assets/Logo/Logo.png"""
    logo_path = "assets/Logo/Logo.png"
    if os.path.exists(logo_path):
        logo_img = pygame.image.load(logo_path).convert_alpha()
        aspect_ratio = logo_img.get_height() / logo_img.get_width()
        new_width = width
        new_height = int(width * aspect_ratio)
        scaled_logo = pygame.transform.smoothscale(logo_img, (new_width, new_height))
        screen.blit(scaled_logo, (x, y))
    else:
        pygame.draw.rect(screen, (255, 140, 0), (x, y, width, 50), border_radius=10)
        font = pygame.font.SysFont("Segoe UI", 16, bold=True)
        text_surf = font.render("PACMAN PATHFINDER", True, (255, 255, 255))
        screen.blit(text_surf, (x + (width - text_surf.get_width()) // 2, y + 14))

def load_ghost_assets():
    ghost_anims = []
    base_path = "assets/ghost"
    
    # Kiểm tra đường dẫn thư mục
    if not os.path.exists(base_path):
        return []

    # Duyệt 4 con ma (ghost_1 đến ghost_4)
    for i in range(1, 5): 
        ghost_dir = os.path.join(base_path, f"ghost_{i}")
        if os.path.exists(ghost_dir):
            frames = []
            # Lấy tất cả file .png trong thư mục và sắp xếp theo tên (frame1, frame2...)
            files = sorted([f for f in os.listdir(ghost_dir) if f.lower().endswith('.png')])
            for file in files:
                path = os.path.join(ghost_dir, file)
                img = pygame.image.load(path).convert_alpha()
                frames.append(img)
            if frames:
                ghost_anims.append(frames)
    return ghost_anims
# Hàm này dùng để spawn ma ở nhóm 5/6
def spawn_ghosts(grid):
    # Định nghĩa các vị trí cố định rải rác trong bản đồ để ma không chồng lên nhau
    positions = [(5, 5), (10, 5), (2, 9), (16, 10)]
    valid_positions = []
    for (gx, gy) in positions:
        if 0 <= gy < len(grid) and 0 <= gx < len(grid[0]) and grid[gy][gx] != 'W':
            valid_positions.append((gx, gy))
    return valid_positions

def draw_fog_of_war(screen, grid, visited_tiles, pos_x, pos_y, offset_x, offset_y, TILE_SIZE, ROWS, COLS):
    fog_surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
    fog_surf.fill((0, 0, 0))
    fog_surf.set_alpha(200)

    px, py = int(round(pos_x / TILE_SIZE)), int(round(pos_y / TILE_SIZE))
    
    for r in range(ROWS):
        for c in range(COLS):
            # CÁC ĐIỀU KIỆN ĐỂ MỘT Ô ĐƯỢC SOI SÁNG:
            # 1. Ô đó nằm trong tầm nhìn đèn pin (bán kính 1)
            # 2. HOẶC ô đó đã nằm trong danh sách visited_tiles
            is_in_flashlight = (abs(r - py) <= 1 and abs(c - px) <= 1)
            is_visited = (r, c) in visited_tiles
            
            # Chỉ vẽ sương mù nếu ô đó KHÔNG thuộc cả 2 điều kiện trên
            if not (is_in_flashlight or is_visited):
                cell_x = c * TILE_SIZE + offset_x
                cell_y = r * TILE_SIZE + offset_y
                screen.blit(fog_surf, (cell_x, cell_y))

def main():
    # Khởi tạo thuật toán mặc định ban đầu
    algo_type = 'bfs'
    ghost_positions = []
    ghost_last_dir = []
    pygame.init()
    pygame.display.set_caption("PACMAN THOÁT KHỎI MÊ CUNG")

    grid = [list(row) for row in map_loader.load_map("level1.txt")]
    ROWS, COLS = len(grid), len(grid[0])

    maze_w = COLS * TILE_SIZE
    maze_h = ROWS * TILE_SIZE

    # Khởi tạo kích thước cửa sổ ban đầu
    window_width = LEFT_UI_WIDTH + 40 + maze_w + 40 + RIGHT_UI_WIDTH
    window_height = max(maze_h + 250, 500)
    screen = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)

    ghost_positions = []
    global ghost_animations
    ghost_animations = load_ghost_assets()
    global ghost_frame_idx 
    ghost_frame_idx = 0

    # Đọc thông tin thực tế chiều cao Logo để căn chỉnh
    logo_path = "assets/Logo/Logo.png"
    logo_height = 80
    if os.path.exists(logo_path):
        temp_logo = pygame.image.load(logo_path).convert_alpha()
        aspect_ratio = temp_logo.get_height() / temp_logo.get_width()
        logo_height = int(maze_w * aspect_ratio)
    
    logo_gap = 20
    window_height = max(10 + logo_height + logo_gap + maze_h + 40, 450)
    screen = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)

    show_menu = False
    is_paused = False
    is_running = False
    scroll_y = 0
    def load_assets():
        frames = []
        path = "assets/pacman"
        if os.path.exists(path):
            files = sorted([f for f in os.listdir(path) if f.endswith('.png')])
            for f in files:
                img = pygame.image.load(os.path.join(path, f)).convert_alpha()
                frames.append(pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE)))
        else:
            surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            pygame.draw.circle(surf, (255, 255, 0), (TILE_SIZE//2, TILE_SIZE//2), TILE_SIZE//2 - 2)
            frames = [surf] * 4

        wall_path = "assets/wall/sprite-1-1.png"
        if os.path.exists(wall_path):
            wall_sprite = pygame.transform.scale(
                pygame.image.load(wall_path).convert_alpha(),
                (TILE_SIZE, TILE_SIZE)
            )
        else:
            wall_sprite = pygame.Surface((TILE_SIZE, TILE_SIZE))
            wall_sprite.fill((33, 33, 255))

        return frames, wall_sprite

    pacman_frames, wall_sprite = load_assets()

    direction_map = {(1, 0): 0, (0, 1): 1, (0, -1): 2, (-1, 0): 3}
    
    start, goal = map_loader.get_positions(grid)

    # --- KHỞI TẠO MA TRẬN CHI PHÍ GỐC ---
    initial_dots = [[False for _ in range(COLS)] for _ in range(ROWS)]
    for r in range(ROWS):
        for c in range(COLS):
            if grid[r][c] not in ['W', 'P', 'G']:
                if random.random() < 0.25:  # Tỷ lệ xuất hiện hạt ngẫu nhiên là 25%
                    initial_dots[r][c] = True

    # Tạo bản sao ma trận chi phí dùng cho việc ăn hạt trực tiếp
    cost_map = [[1 for _ in range(COLS)] for _ in range(ROWS)]
    def reset_cost_map():
        for r in range(ROWS):
            for c in range(COLS):
                cost_map[r][c] = 15 if initial_dots[r][c] else 1

    reset_cost_map()

    dots_eaten = 0

    # --- KHỞI TẠO BIẾN LƯU VẾT ĐƯỜNG ĐI (VIỀN TÍM) ---
    visited_tiles = set()
    visited_tiles.add((start[1], start[0]))
    partial_history = [start]
    # Hàm tính toán lộ trình
    def calculate_path(current_algo):
        temp_cost_map = [[1 for _ in range(COLS)] for _ in range(ROWS)]
        for r in range(ROWS):
            for c in range(COLS):
                temp_cost_map[r][c] = 15 if initial_dots[r][c] else 1

        if current_algo == 'local_beam_search':
            return algorithms.local_beam_search(grid, temp_cost_map, start, goal)
        elif current_algo == 'bfs':
            return algorithms.bfs(grid, start, goal)
        elif current_algo == 'dfs':
            return algorithms.dfs(grid, start, goal)
        elif current_algo == 'greedy':
            return algorithms.greedy_search(grid, start, goal)
        elif current_algo == 'simulated_annealing':
            return algorithms.simulated_annealing(grid, start, goal)
        elif current_algo == 'sensorless':
            # Gọi thuật toán Conformant Planning (Belief State)
            return algorithms.conformant_sensorless(grid, start, goal)
        elif current_algo == 'ida_star':
            return algorithms.ida_star(grid, temp_cost_map, start, goal)
        elif current_algo == 'ac3':
            return algorithms.ac3(grid, ghost_positions, start, goal)
        elif current_algo == 'alpha_beta':
            return algorithms.get_best_move(grid,start, ghost_positions[0], goal, depth=3, history=[])
        elif current_algo == 'backtracking':
            return algorithms.backtracking(grid, ghost_positions, start, goal) 
        elif current_algo == 'minimax':
            return algorithms.get_best_move_minimax_pacman(grid, start, ghost_positions[0], goal, depth=6, history=[])
        elif current_algo == 'partial_observable':
            curr_grid_pos = (int(round(pos_x / TILE_SIZE)), int(round(pos_y / TILE_SIZE)))
            return algorithms.partial_observable(grid, curr_grid_pos, goal, visited_tiles, partial_history)
        elif current_algo == 'iddfs':
            return algorithms.iddfs(grid, start, goal)
        elif current_algo == 'hill_climbing':
            return algorithms.hill_climbing(grid, start, goal)
        elif current_algo == 'expectimax':
            g_pos = ghost_positions[0] if ghost_positions else start
            return algorithms.get_best_move_expectimax(grid, start, g_pos, goal, depth=3, history=[])
        elif current_algo == 'min_conflicts':
            return algorithms.min_conflicts(grid, ghost_positions, start, goal)
        elif current_algo == 'nondeterministic':
            try:
                result = algorithms.nondeterministic(grid, start, goal)
                print(f"[NONDETER] start={start} goal={goal} path_len={len(result)}")
                if not result:
                    print(f"[NONDETER] grid[start[1]][start[0]]={grid[start[1]][start[0]]!r}")
                    print(f"[NONDETER] grid[goal[1]][goal[0]]={grid[goal[1]][goal[0]]!r}")
                    print(f"[NONDETER] ROWS={len(grid)} COLS={len(grid[0])}")
                return result
            except Exception as e:
                print(f"[NONDETER] ERROR: {e}")
                import traceback; traceback.print_exc()
                return []
        elif current_algo == 'a_star':
            return algorithms.a_star(grid, temp_cost_map, start, goal)
        return []

    path = calculate_path(algo_type)

    # --- LOGIC TỰ ĐỘNG XÁC ĐỊNH HƯỚNG MẶT BAN ĐẦU QUAY VÀO TRONG ---
    def get_default_direction(start_pos, current_path):
        if isinstance(current_path, list) and len(current_path) > 1:
            next_step = current_path[1]
            dx = next_step[0] - start_pos[0]
            dy = next_step[1] - start_pos[1]
            if (dx, dy) in direction_map:
                return direction_map[(dx, dy)]
        return 0

    current_dir = get_default_direction(start, path)

    pos_x = float(start[0] * TILE_SIZE)
    pos_y = float(start[1] * TILE_SIZE)

    path_index = 0
    frame_in_anim = 0
    anim_timer = 0
    speed = 0.15

    clock = pygame.time.Clock()
    running = True

    blink_timer = 0
    blink_on = True
    forbidden_cells = set()

    is_calculating = False
    ghost_timer = 0
    full_history = [start]
    running = True
    ghost_pixel_pos = [[float(p[0] * TILE_SIZE), float(p[1] * TILE_SIZE)] for p in ghost_positions]
    ghost_history = [ghost_positions[0]] if ghost_positions else []
    ghost_move_timer = 0
    ghost_move_delay = 30
    memory_map = [['?' for _ in range(COLS)] for _ in range(ROWS)]

    while running:
        px, py = int(round(pos_x / TILE_SIZE)), int(round(pos_y / TILE_SIZE))
        if 0 <= py < ROWS and 0 <= px < COLS:
    # Chỉ ghi nhận vào memory nếu nó là đường hoặc đã biết
    # KHÔNG ghi đè 'W' nếu đó là tường thật
            if grid[py][px] != 'W':
                memory_map[py][px] = grid[py][px]
            else:
                memory_map[py][px] = 'W' # Xác nhận đây là tường
            visited_tiles.add((py, px))
        mx, my = pygame.mouse.get_pos()
        screen_w, screen_h = screen.get_size()

        font = pygame.font.SysFont("Segoe UI", 16)          
        bold_font = pygame.font.SysFont("Segoe UI", 16, bold=True)
        large_font = pygame.font.SysFont("Segoe UI", 20, bold=True)
        small_bold = pygame.font.SysFont("Segoe UI", 13, bold=True)

        btn_objects = {}
        buttons_list = ["Menu", "Start", "Stop", "Restart"]
        for i, text in enumerate(buttons_list):
            btn_objects[text] = pygame.Rect(12, 20 + i * 55, LEFT_UI_WIDTH - 24, 42)
        
        pause_rect = pygame.Rect(12, 240, LEFT_UI_WIDTH - 24, 42)


        close_btn_rect = pygame.Rect(MENU_OPEN_WIDTH - 30, 12, 22, 22)
        algo_list = ["bfs","dfs","greedy","simulated_annealing", "ida_star", "a_star", "local_beam_search", "partial_observable","sensorless", "ac3", "alpha_beta","backtracking", "minimax", "iddfs", "hill_climbing", "expectimax", "min_conflicts", "nondeterministic"]
        max_scroll = max(0, (len(algo_list) * 55) - (screen_h - 150))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

            if event.type == pygame.MOUSEWHEEL:
                if show_menu:
                    scroll_y -= event.y * 30  # Tăng số này nếu muốn cuộn nhanh hơn
                    scroll_y = max(0, min(scroll_y, max_scroll))
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if show_menu:
                    if close_btn_rect.collidepoint(mx, my):
                        show_menu = False
                    else:
                        clicked_algo = None
                        for i, algo_item in enumerate(algo_list):
                            # Tọa độ Y khớp với lúc vẽ menu: 70 + i * 55 - scroll_y
                            btn_y = 70 + i * 55 - scroll_y 
                            if 60 <= btn_y < screen_h - 5:
                                btn_rect = pygame.Rect(20, btn_y, 200, 42)
                                if btn_rect.collidepoint(mx, my):
                                    clicked_algo = algo_item
                                    break
                        
                        if clicked_algo and clicked_algo != algo_type:
                            algo_type = clicked_algo
        
                             # 1. Reset các biến trạng thái dùng chung
                            ghost_positions = []
                            ghost_pixel_pos = []
                            forbidden_cells.clear()  
                            visited_tiles.clear()
                            visited_tiles.add((start[1], start[0]))
                            partial_history = [start]
                            full_history = [start]
        
                            # 2. Reset các thông số di chuyển
                            pos_x = float(start[0] * TILE_SIZE)
                            pos_y = float(start[1] * TILE_SIZE)
                            path_index = 0
                            frame_in_anim = 0
                            dots_eaten = 0
                            is_running = False
                            is_paused = False
        
                            # 3. Reset bản đồ chi phí (Cost Map)
                            reset_cost_map()
        
                            # 4. Khởi tạo riêng cho từng thuật toán
                            if algo_type in ['alpha_beta', 'minimax', 'expectimax']:
                                ghost_positions = [(16, 10)] 
                                ghost_last_dir = [None]
                                # Reset thêm ghost_history cho Alpha-Beta / Expectimax
                                ghost_history = [ghost_positions[0]] if ghost_positions else []
                            elif algo_type in ['ac3', 'backtracking', 'min_conflicts']:
                                ghost_positions = spawn_ghosts(grid)
                                ghost_last_dir = [None] * len(ghost_positions)
        
                            # Cập nhật lại ghost_pixel_pos nếu có ma
                            if ghost_positions:
                                ghost_pixel_pos = [[float(p[0] * TILE_SIZE), float(p[1] * TILE_SIZE)] for p in ghost_positions]
        
                            # 5. Tính toán lộ trình mới
                            path = calculate_path(algo_type)
                            current_dir = get_default_direction(start, path)
        
                        show_menu = False
                else:
                    if btn_objects["Menu"].collidepoint(mx, my):
                        show_menu = True
                    elif btn_objects["Start"].collidepoint(mx, my):
                        is_running = True
                        if algo_type in ['ac3', 'backtracking', 'min_conflicts'] and not ghost_positions:
                            ghost_positions = spawn_ghosts(grid)
                            ghost_last_dir = [None] * len(ghost_positions)
                        if algo_type in ['expectimax'] and not ghost_positions:
                            ghost_positions = [(16, 10)]
                            ghost_last_dir = [None]
                            ghost_history = [ghost_positions[0]]
                        if algo_type in ['alpha_beta', 'minimax']:
                            full_history.clear()
                            full_history.append(start)
                        # Nondeterministic dùng random.shuffle nên tính lại mỗi lần Start
                        if algo_type == 'nondeterministic':
                            pos_x = float(start[0] * TILE_SIZE)
                            pos_y = float(start[1] * TILE_SIZE)
                            path_index = 0
                            visited_tiles.clear()
                            visited_tiles.add((start[1], start[0]))
                        path = calculate_path(algo_type)
                    elif btn_objects["Stop"].collidepoint(mx, my):
                        is_running = False
                    elif btn_objects["Restart"].collidepoint(mx, my):
                        # Reset trạng thái khi nhấn Restart
                        pos_x = float(start[0] * TILE_SIZE)
                        pos_y = float(start[1] * TILE_SIZE)
                        path_index = 0
                        frame_in_anim = 0  # Ép ngậm miệng khi Restart
                        dots_eaten = 0
                        is_running = False
                        is_paused = False
                        reset_cost_map()
                        
                        visited_tiles.clear()
                        visited_tiles.add((start[1], start[0]))
                        partial_history = [start]
                        if algo_type in ['alpha_beta', 'minimax']:
                            full_history.clear()
                            full_history.append(start)
                        path = calculate_path(algo_type)

                        current_dir = get_default_direction(start, path)
                    elif pause_rect.collidepoint(mx, my):
                        is_paused = not is_paused

        if is_running and not is_paused and algo_type == 'alpha_beta':
            # Tăng bộ đếm mỗi khung hình
            ghost_move_timer += 1
    
            # Chỉ thực hiện di chuyển khi bộ đếm đạt ngưỡng delay
            if ghost_move_timer >= ghost_move_delay:
                ghost_move_timer = 0 # Reset bộ đếm
        
                # --- Logic di chuyển cũ của bạn ở đây ---
                if len(ghost_pixel_pos) != len(ghost_positions):
                    ghost_pixel_pos = [[float(p[0] * TILE_SIZE), float(p[1] * TILE_SIZE)] for p in ghost_positions]

                pacman_pos = (int(round(pos_x / TILE_SIZE)), int(round(pos_y / TILE_SIZE)))

                # Gán target an toàn để tránh lỗi UnboundLocalError
                target = ghost_positions[0] 
        
                if ghost_positions:
                    target = algorithms.get_best_ghost_move(
                        grid, pacman_pos, ghost_positions[0], goal, depth=3, ghost_history=ghost_history
                    )

                ghost_positions[0] = target
                ghost_history.append(target)

            if len(ghost_history) > 5:
                ghost_history.pop(0)

            ghost_pixel_pos[0][0] = ghost_positions[0][0] * TILE_SIZE
            ghost_pixel_pos[0][1] = ghost_positions[0][1] * TILE_SIZE
        
        # CHÈN KHỐI NÀY NGAY DƯỚI KHỐI ALPHA-BETA
        if is_running and not is_paused and algo_type == 'minimax':
            ghost_move_timer += 1
            if ghost_move_timer >= ghost_move_delay:
                ghost_move_timer = 0 
                if len(ghost_pixel_pos) != len(ghost_positions):
                    ghost_pixel_pos = [[float(p[0] * TILE_SIZE), float(p[1] * TILE_SIZE)] for p in ghost_positions]
                pacman_pos = (int(round(pos_x / TILE_SIZE)), int(round(pos_y / TILE_SIZE)))
                target = ghost_positions[0] 
                if ghost_positions:
                    # GỌI HÀM CỦA MINIMAX
                    target = algorithms.get_best_ghost_move_minimax(
                        grid, pacman_pos, ghost_positions[0], goal, depth=3, ghost_history=ghost_history
                    )
                ghost_positions[0] = target
                ghost_history.append(target)
            if len(ghost_history) > 5: ghost_history.pop(0)
            ghost_pixel_pos[0][0] = ghost_positions[0][0] * TILE_SIZE
            ghost_pixel_pos[0][1] = ghost_positions[0][1] * TILE_SIZE

        # KHỐI EXPECTIMAX (tương tự Alpha-Beta nhưng ma đi ngẫu nhiên)
        if is_running and not is_paused and algo_type == 'expectimax':
            curr_pos = (int(round(pos_x / TILE_SIZE)), int(round(pos_y / TILE_SIZE)))
            target_pixel_x = goal[0] * TILE_SIZE
            target_pixel_y = goal[1] * TILE_SIZE
            if abs(pos_x - target_pixel_x) < 5 and abs(pos_y - target_pixel_y) < 5:
                pos_x = float(target_pixel_x)
                pos_y = float(target_pixel_y)
                is_running = False
            elif path_index >= len(path) - 1:
                if abs(pos_x - curr_pos[0]*TILE_SIZE) < 15 and abs(pos_y - curr_pos[1]*TILE_SIZE) < 15:
                    if ghost_positions:
                        new_path = algorithms.get_best_move_expectimax(
                            grid, curr_pos, ghost_positions[0], goal, depth=3, history=full_history
                        )
                        if isinstance(new_path, list) and len(new_path) > 1:
                            path = new_path
                            path_index = 0
                            next_move = new_path[1]
                            if not full_history or full_history[-1] != next_move:
                                full_history.append(next_move)
            for (gx, gy) in ghost_positions:
                dist = ((pos_x - gx*TILE_SIZE)**2 + (pos_y - gy*TILE_SIZE)**2)**0.5
                if dist < TILE_SIZE * 0.5:
                    is_running = False

        if is_running and not is_paused and algo_type == 'expectimax':
            ghost_move_timer += 1
            if ghost_move_timer >= ghost_move_delay:
                ghost_move_timer = 0
                if len(ghost_pixel_pos) != len(ghost_positions):
                    ghost_pixel_pos = [[float(p[0] * TILE_SIZE), float(p[1] * TILE_SIZE)] for p in ghost_positions]
                if ghost_positions:
                    target = algorithms.get_best_ghost_move_expectimax(
                        grid,
                        (int(round(pos_x / TILE_SIZE)), int(round(pos_y / TILE_SIZE))),
                        ghost_positions[0], goal, depth=3, ghost_history=ghost_history
                    )
                    ghost_positions[0] = target
                    ghost_history.append(target)
            if len(ghost_history) > 5:
                ghost_history.pop(0)
            if ghost_pixel_pos:
                ghost_pixel_pos[0][0] = ghost_positions[0][0] * TILE_SIZE
                ghost_pixel_pos[0][1] = ghost_positions[0][1] * TILE_SIZE

        # --- LOGIC DI CHUYỂN, ĂN HẠT & GHI LOG ĐÃ ĐI QUA ---
        if is_running and not is_paused and path is not None and len(path) > 0 and path_index < len(path) - 1:
            curr = path[path_index]
            next_n = path[path_index + 1]
            dx = next_n[0] - curr[0]
            dy = next_n[1] - curr[1]

            if (dx, dy) in direction_map:
                current_dir = direction_map[(dx, dy)]

            tx = next_n[0] * TILE_SIZE
            ty = next_n[1] * TILE_SIZE

            pos_x += (tx - pos_x) * speed
            pos_y += (ty - pos_y) * speed

            # Chỉ chạy hoạt ảnh há ngậm miệng khi thực sự di chuyển
            anim_timer += 1
            if anim_timer >= 5:
                frame_in_anim = (frame_in_anim + 1) % (len(pacman_frames) // 4 if len(pacman_frames) > 4 else 1)
                anim_timer = 0

            if abs(pos_x - tx) < 1 and abs(pos_y - ty) < 1:
                pos_x = tx
                pos_y = ty
                path_index += 1
        
                # CHỈ CẬP NHẬT VISITED VÀ LỘ TRÌNH NẾU LÀ PARTIAL_OBSERVABLE
                if algo_type == "partial_observable":
                    visited_tiles.add((next_n[1], next_n[0]))
                    partial_history.append(next_n)
            
                    # Tính toán lại đường đi cho partial tại đây
                    new_path = algorithms.partial_observable(grid, next_n, goal, visited_tiles, partial_history)
                    
                    # KIỂM TRA ĐÍCH: Nếu đã ở đích hoặc không tìm thấy đường đi mới hợp lệ
                    curr_grid_pos = (int(round(pos_x / TILE_SIZE)), int(round(pos_y / TILE_SIZE)))
                    if curr_grid_pos == goal:
                        is_running = False  # Dừng ngay lập tức
                    else:
                        path = new_path
                        path_index = 0
        
                # NẾU LÀ CÁC THUẬT TOÁN TĨNH (BFS, IDA*, AC-3...), KHÔNG GHI ĐÈ PATH
                elif algo_type in ['bfs','dfs', 'greedy', 'simulated_annealing', 'ida_star', 'local_beam_search', 'ac3', 'alpha_beta', 'backtracking', 'minimax','sensorless', 'iddfs', 'hill_climbing', 'min_conflicts', 'nondeterministic']:
                    visited_tiles.add((next_n[1], next_n[0]))
                if cost_map[next_n[1]][next_n[0]] == 15:
                    cost_map[next_n[1]][next_n[0]] = 1
                    dots_eaten += 1
                if algo_type == "partial_observable":
                    partial_history.append(next_n)
                    curr_grid_pos = (int(round(pos_x / TILE_SIZE)), int(round(pos_y / TILE_SIZE)))
                    path = algorithms.partial_observable(grid, curr_grid_pos, goal, visited_tiles, partial_history)
                    path_index = 0
        
        # --- ĐÓNG BĂNG HÌNH ẢNH NGẬM MIỆNG KHI KHÔNG CHẠY ---
        elif not is_running:
            frame_in_anim = 0

        # ====================================================
        # PHẦN VẼ ĐỒ HỌA MÀN HÌNH GIAO DIỆN CHÍNH
        # ====================================================
        screen.fill(OUTER_BG_COLOR)

        maze_rect = pygame.Rect(0, 0, maze_w, maze_h)
        maze_rect.centerx = (screen_w - RIGHT_UI_WIDTH + LEFT_UI_WIDTH) // 2
        maze_rect.centery = (screen_h + 50) // 2

        if maze_rect.left < LEFT_UI_WIDTH + 10:
            maze_rect.left = LEFT_UI_WIDTH + 10

        offset_x = maze_rect.x
        offset_y = maze_rect.y

        logo_y = offset_y - logo_height - logo_gap
        if logo_y < 10:
            shift_down = 10 - logo_y
            offset_y += shift_down
            maze_rect.y += shift_down
            logo_y = 10

        draw_logo(screen, offset_x, logo_y, maze_w)
        pygame.draw.rect(screen, BG_COLOR, maze_rect)

        # Vẽ cấu trúc ô bản đồ mê cung
        for r in range(ROWS):
            for c in range(COLS):
                cell_x = c * TILE_SIZE + offset_x
                cell_y = r * TILE_SIZE + offset_y

                if grid[r][c] == 'W':
                    screen.blit(wall_sprite, (cell_x, cell_y))
                
                else:
                    if algo_type in ['ac3', 'backtracking', 'min_conflicts'] and (c, r) in forbidden_cells:
                        if blink_on:
                            pygame.draw.rect(
                                screen, 
                                (180, 50, 50), 
                                (cell_x + 2, cell_y + 2, TILE_SIZE - 4, TILE_SIZE - 4), 
                                border_radius=4
                            )
                    if (r, c) in visited_tiles:
                        pygame.draw.rect(screen, (180, 0, 255), (cell_x + 1, cell_y + 1, TILE_SIZE - 2, TILE_SIZE - 2), 2, border_radius=3)

                    if grid[r][c] == 'P':
                        pygame.draw.rect(screen, (0, 200, 115), (cell_x + 4, cell_y + 4, TILE_SIZE - 8, TILE_SIZE - 8), border_radius=5)
                    elif grid[r][c] == 'G':
                        pygame.draw.rect(screen, (255, 0, 100), (cell_x + 4, cell_y + 4, TILE_SIZE - 8, TILE_SIZE - 8), border_radius=4)
                    
                    elif algo_type in ['ida_star', 'local_beam_search', 'a_star']:
                        if cost_map[r][c] == 15:
                            pygame.draw.circle(screen, (255, 215, 0), (cell_x + TILE_SIZE // 2, cell_y + TILE_SIZE // 2), 5)
        
        # --- HIỆU ỨNG MÔI TRƯỜNG MÙ (SENSORLESS) ---
        
        # --- HIỆU ỨNG MÔI TRƯỜNG MÙ (SENSORLESS) ---
        if algo_type in ('sensorless', 'nondeterministic'):
            # Phủ màn đen mờ lên toàn bộ mê cung (môi trường mù / không xác định)
            blind_fog = pygame.Surface((maze_w, maze_h))
            blind_fog.fill((0, 0, 0))
            blind_fog.set_alpha(240)
            screen.blit(blind_fog, (offset_x, offset_y))

            # Tính vị trí Pacman hiện tại trên lưới để vẽ vùng sáng
            _px = int(round(pos_x / TILE_SIZE))
            _py = int(round(pos_y / TILE_SIZE))

            # Xóa fog xung quanh Pacman (bán kính 1) để luôn thấy vị trí hiện tại
            _reveal_surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
            _reveal_surf.fill((30, 27, 38))  # Màu nền mê cung
            for _dr in range(-1, 2):
                for _dc in range(-1, 2):
                    _nr, _nc = _py + _dr, _px + _dc
                    if 0 <= _nr < ROWS and 0 <= _nc < COLS:
                        _cx = _nc * TILE_SIZE + offset_x
                        _cy = _nr * TILE_SIZE + offset_y
                        # Vẽ lại ô gốc (tường hoặc đường) để xóa fog
                        if grid[_nr][_nc] == 'W':
                            screen.blit(wall_sprite, (_cx, _cy))
                        else:
                            pygame.draw.rect(screen, (30, 27, 38), (_cx, _cy, TILE_SIZE, TILE_SIZE))

            # Vẽ lại vết chân đã đi qua
            for (r, c) in visited_tiles:
                cell_x = c * TILE_SIZE + offset_x
                cell_y = r * TILE_SIZE + offset_y
                color = (180, 0, 255) if algo_type == 'sensorless' else (0, 180, 255)
                pygame.draw.rect(screen, color, (cell_x + 1, cell_y + 1, TILE_SIZE - 2, TILE_SIZE - 2), 2, border_radius=3)

            # Vẽ ô đích luôn hiển thị (để Pacman biết mục tiêu)
            goal_x, goal_y = goal[0] * TILE_SIZE + offset_x, goal[1] * TILE_SIZE + offset_y
            pygame.draw.rect(screen, (30, 27, 38), (goal_x, goal_y, TILE_SIZE, TILE_SIZE))
            pygame.draw.rect(screen, (255, 0, 100), (goal_x + 4, goal_y + 4, TILE_SIZE - 8, TILE_SIZE - 8), border_radius=4)


        # Vẽ nhân vật Pacman
        frame_idx = (current_dir * 4) + frame_in_anim
        if frame_idx >= len(pacman_frames):
            frame_idx = 0
        screen.blit(pacman_frames[frame_idx], (int(pos_x) + offset_x, int(pos_y) + offset_y))
        if algo_type == 'partial_observable':
            draw_fog_of_war(screen, grid, visited_tiles, pos_x, pos_y, offset_x, offset_y, TILE_SIZE, ROWS, COLS)
        # --- LOGIC KIỂM TRA VA CHẠM VỚI MA (AC-3) ---
        if is_running and algo_type in ['ac3', 'backtracking', 'min_conflicts']:
            blink_timer += 1
            if blink_timer >= 30:
                blink_on = not blink_on
                blink_timer = 0
            if algo_type in ['ac3', 'backtracking', 'min_conflicts']:
                forbidden_cells = set()
                for gx, gy in ghost_positions:
                    for r in range(gy - 1, gy + 2): 
                        for c in range(gx - 1, gx + 2):
                            if 0 <= r < len(grid) and 0 <= c < len(grid[0]):
                                if (c, r) != start and (c, r) != goal:
                                    forbidden_cells.add((c, r))

        if is_running and not is_paused and algo_type == 'alpha_beta':
            # 1. Xác định vị trí lưới hiện tại
            curr_pos = (int(round(pos_x / TILE_SIZE)), int(round(pos_y / TILE_SIZE)))
            
            # 2. Tính tọa độ pixel của đích
            target_pixel_x = goal[0] * TILE_SIZE
            target_pixel_y = goal[1] * TILE_SIZE
            
            # 3. KIỂM TRA ĐÍCH BẰNG PIXEL (Dùng sai số nhỏ để tránh dừng lưng chừng)
            # Nếu Pacman cách đích dưới 5 pixel, coi như đã tới nơi
            if abs(pos_x - target_pixel_x) < 5 and abs(pos_y - target_pixel_y) < 5:
                pos_x = float(target_pixel_x) # Gắn chặt vào tọa độ đích
                pos_y = float(target_pixel_y)
                is_running = False
                print("Đã tới đích hoàn toàn!")
            
            # 4. CHỈ TÍNH BƯỚC TIẾP THEO KHI ĐÃ ĐI ĐẾN Ô HIỆN TẠI (Lưới)
            elif path_index >= len(path) - 1:
                if abs(pos_x - curr_pos[0]*TILE_SIZE) < 15 and abs(pos_y - curr_pos[1]*TILE_SIZE) < 15:
                    if ghost_positions:
                        new_path = algorithms.get_best_move(
                            grid,
                            curr_pos,
                            ghost_positions[0],
                            goal,
                            depth=6,
                            history=full_history
                        )
                        if isinstance(new_path, list) and len(new_path) > 1:
                            path = new_path
                            path_index = 0 
                            next_move = new_path[1]
                            if not full_history or full_history[-1] != next_move:
                                full_history.append(next_move)
                    else:
                        print("Lỗi: Không tìm thấy vị trí ma!")
            
            # 4. Kiểm tra va chạm với ma
            for (gx, gy) in ghost_positions:
                # Kiểm tra va chạm pixel thay vì chỉ so sánh grid để nhạy hơn
                dist = ((pos_x - gx*TILE_SIZE)**2 + (pos_y - gy*TILE_SIZE)**2)**0.5
                if dist < TILE_SIZE * 0.5: # Nếu khoảng cách < nửa ô
                    is_running = False
                    print("Game Over: Pacman bị bắt!")

        # KHỐI NONDETERMINISTIC — kiểm tra đích và tính lại đường khi hết path
        if is_running and not is_paused and algo_type == 'nondeterministic':
            curr_pos = (int(round(pos_x / TILE_SIZE)), int(round(pos_y / TILE_SIZE)))
            target_pixel_x = goal[0] * TILE_SIZE
            target_pixel_y = goal[1] * TILE_SIZE
            # Dừng khi tới đích
            if abs(pos_x - target_pixel_x) < 5 and abs(pos_y - target_pixel_y) < 5:
                pos_x = float(target_pixel_x)
                pos_y = float(target_pixel_y)
                is_running = False
            # Nếu hết path thì tính lại (do random shuffle có thể tìm đường khác)
            elif path_index >= len(path) - 1 and curr_pos != goal:
                new_path = algorithms.nondeterministic(grid, curr_pos, goal)
                if isinstance(new_path, list) and len(new_path) > 1:
                    path = new_path
                    path_index = 0

        # KHỐI MINIMAX 
        if is_running and not is_paused and algo_type == 'minimax':
            curr_pos = (int(round(pos_x / TILE_SIZE)), int(round(pos_y / TILE_SIZE)))
            
            # 1. Kiểm tra đích (giữ nguyên)
            target_pixel_x = goal[0] * TILE_SIZE
            target_pixel_y = goal[1] * TILE_SIZE
            if abs(pos_x - target_pixel_x) < 5 and abs(pos_y - target_pixel_y) < 5:
                pos_x = float(target_pixel_x)
                pos_y = float(target_pixel_y)
                is_running = False
            
            
            elif path_index >= len(path) - 1:
                # Nếu đã đi hết đường cũ, tính lại đường mới ngay lập tức
                if ghost_positions:
                    # Tính toán lại lộ trình dựa trên vị trí ma hiện tại (DEPTH=6 là ổn)
                    new_path = algorithms.get_best_move_minimax_pacman(
                        grid, curr_pos, ghost_positions[0], goal, depth=6, history=full_history
                    )
                    if isinstance(new_path, list) and len(new_path) > 1:
                        path = new_path
                        path_index = 0 # RESET ĐỂ BẢNG ROUTE PATH CẬP NHẬT TỪ ĐẦU
                        
                        # Lưu lịch sử để thuật toán biết đường tránh
                        next_move = new_path[1]
                        if not full_history or full_history[-1] != next_move:
                            full_history.append(next_move)
            
            # 3. Kiểm tra va chạm (giữ nguyên)
            for (gx, gy) in ghost_positions:
                dist = ((pos_x - gx*TILE_SIZE)**2 + (pos_y - gy*TILE_SIZE)**2)**0.5
                if dist < TILE_SIZE * 0.5:
                    is_running = False
                    print("Game Over: Pacman bị bắt!")
                    
        # --- VẼ MA (AC-3) ---
        if ghost_animations and ghost_positions:
            # Kiểm tra an toàn trước khi vẽ để tránh IndexError
            if len(ghost_pixel_pos) < len(ghost_positions):
                ghost_pixel_pos = [[float(p[0] * TILE_SIZE), float(p[1] * TILE_SIZE)] for p in ghost_positions]

            for i, pos in enumerate(ghost_positions):
                # Chọn frame hoạt ảnh
                anim = ghost_animations[i % len(ghost_animations)]
                frame = anim[pygame.time.get_ticks() // 200 % len(anim)]
                frame = pygame.transform.scale(frame, (TILE_SIZE, TILE_SIZE))
        
                # Vẽ dựa trên ghost_pixel_pos đã làm mượt
                # Đảm bảo i không vượt quá độ dài của ghost_pixel_pos
                if i < len(ghost_pixel_pos):
                    draw_x = int(ghost_pixel_pos[i][0]) + offset_x
                    draw_y = int(ghost_pixel_pos[i][1]) + offset_y
                    screen.blit(frame, (draw_x, draw_y))
                
        # ----------------------------------------------------
        # THANH MENU ĐIỀU KHIỂN CHÍNH BÊN TRÁI
        # ----------------------------------------------------
        pygame.draw.rect(screen, (24, 24, 35), (0, 0, LEFT_UI_WIDTH, screen_h))
        pygame.draw.line(screen, (40, 40, 60), (LEFT_UI_WIDTH, 0), (LEFT_UI_WIDTH, screen_h), 2)

        for text in buttons_list:
            btn = btn_objects[text]
            is_hover = btn.collidepoint(mx, my)
            btn_color = (100, 100, 140) if is_hover else (45, 45, 65)
            pygame.draw.rect(screen, btn_color, btn, border_radius=8)
            text_surf = bold_font.render(text, True, (255, 255, 255))
            screen.blit(text_surf, (btn.x + 15, btn.y + (btn.height - text_surf.get_height()) // 2))

        pause_btn_text = "Continue" if is_paused else "Pause"
        is_p_hover = pause_rect.collidepoint(mx, my)
        pause_color = (140, 70, 70) if is_paused else ((100, 100, 140) if is_p_hover else (45, 45, 65))
        pygame.draw.rect(screen, pause_color, pause_rect, border_radius=8)
        p_text_surf = bold_font.render(pause_btn_text, True, (255, 255, 255))
        screen.blit(p_text_surf, (pause_rect.x + 15, pause_rect.y + (pause_rect.height - p_text_surf.get_height()) // 2))

        info_y = screen_h - 40
        if info_y > 300:
            algo_info = font.render(f"Algo: {algo_type.upper()}", True, (0, 255, 150))
            screen.blit(algo_info, (15, info_y))
        # --- VẼ MENU THUẬT TOÁN (CHÈN VÀO TRƯỚC PHẦN VẼ THANH MENU BÊN TRÁI) ---
        if show_menu:
            # 1. Tạo Surface menu
            menu_surface = pygame.Surface((MENU_OPEN_WIDTH, screen_h))
            menu_surface.fill((30, 30, 45))
            
            # --- LỚP 1: VẼ CÁC NÚT THUẬT TOÁN (Vẽ trước) ---
            for i, algo_item in enumerate(algo_list):
                # Vị trí nút (trừ đi scroll_y để tạo hiệu ứng cuộn)
                btn_y = 70 + (i * 55) - scroll_y
                
                # Chỉ vẽ nếu nút nằm trong vùng nhìn thấy (dưới tiêu đề 60px)
                if btn_y >= 60 and btn_y < screen_h - 45:
                    btn_rect = pygame.Rect(20, btn_y, MENU_OPEN_WIDTH - 40, 42)
                    is_hover = btn_rect.collidepoint(mx, my)
                    color = (0, 140, 255) if algo_type == algo_item else ((60, 60, 90) if is_hover else (40, 40, 55))
                    
                    pygame.draw.rect(menu_surface, color, btn_rect, border_radius=6)
                    name_surf = small_bold.render(algo_item.replace("_", " ").upper(), True, (255, 255, 255))
                    menu_surface.blit(name_surf, (btn_rect.x + 10, btn_rect.y + 12))

            # --- LỚP 2: VẼ TIÊU ĐỀ & NÚT X (Vẽ sau cùng để nằm trên) ---
            # Vẽ một khối nền che khuất mọi thứ trượt lên trên (từ y=0 đến y=60)
            pygame.draw.rect(menu_surface, (30, 30, 45), (0, 0, MENU_OPEN_WIDTH, 60))
            pygame.draw.line(menu_surface, (0, 150, 255), (0, 60), (MENU_OPEN_WIDTH, 60), 2)
            
            # Tiêu đề
            title_surf = large_font.render("CHỌN THUẬT TOÁN", True, (255, 255, 255))
            menu_surface.blit(title_surf, (20, 20))
            
            # Nút X
            close_btn_rect = pygame.Rect(MENU_OPEN_WIDTH - 40, 15, 30, 30)
            pygame.draw.rect(menu_surface, (200, 50, 50), close_btn_rect, border_radius=5)
            x_surf = bold_font.render("X", True, (255, 255, 255))
            menu_surface.blit(x_surf, (close_btn_rect.x + 8, close_btn_rect.y + 4))

            # Dán toàn bộ lên màn hình
            screen.blit(menu_surface, (0, 0))
        # ----------------------------------------------------
        # GIAO DIỆN THANH LỘ TRÌNH VÀ CHI PHÍ (ROUTE PATH) BÊN PHẢI
        # ----------------------------------------------------
        taskbar_x = screen_w - RIGHT_UI_WIDTH
        pygame.draw.rect(screen, (24, 24, 35), (taskbar_x, 0, RIGHT_UI_WIDTH, screen_h))
        pygame.draw.line(screen, (40, 40, 60), (taskbar_x, 0), (taskbar_x, screen_h), 2)

        title_surf = large_font.render("ROUTE PATH", True, (0, 255, 150))
        screen.blit(title_surf, (taskbar_x + 15, 20))
        
        if path:
            if algo_type in ['ida_star', 'local_beam_search']:
                cost_text = f"Cost (Dots): {dots_eaten} Pts"
                cost_surf = bold_font.render(cost_text, True, (255, 215, 0))
            else:
                cost_surf = bold_font.render("Cost: None", True, (150, 150, 150))
            screen.blit(cost_surf, (taskbar_x + 15, 52))

            # --- LOGIC ĐỊNH TUYẾN BẢNG HIỂN THỊ ROUTE PATH ---
            if algo_type in ['alpha_beta', 'minimax', 'expectimax']:
                step_info = font.render(f"History: {len(full_history)} Steps", True, (200, 200, 200))
                path_to_display = full_history
                current_highlight_idx = max(0, len(full_history) - 1)
            elif algo_type == 'partial_observable':
                # Partial Observable dùng partial_history để vẽ lịch sử
                step_info = font.render(f"History: {len(partial_history)} Steps", True, (200, 200, 200))
                path_to_display = partial_history
                current_highlight_idx = max(0, len(partial_history) - 1)
            else:
                # Các thuật toán tĩnh dùng path gốc
                step_info = font.render(f"Progress: {path_index}/{len(path)-1} Steps", True, (200, 200, 200))
                path_to_display = path
                current_highlight_idx = path_index

            screen.blit(step_info, (taskbar_x + 15, 75))

            max_visible_items = (screen_h - 130) // 26
            # Cho danh sách tự động cuộn xuống theo bước đi
            start_idx = max(0, current_highlight_idx - max_visible_items // 2)
            end_idx = min(len(path_to_display), start_idx + max_visible_items)
            
            for idx in range(start_idx, end_idx):
                node = path_to_display[idx]
                node_text = f"Step {idx:02d}: ({node[1]}, {node[0]})"
                
                if idx < current_highlight_idx:
                    text_color = (110, 110, 120)  # Bước đã qua (Màu xám)
                    prefix = "  [o] "
                elif idx == current_highlight_idx:
                    text_color = (255, 230, 0)    # Bước hiện tại (Màu Vàng chói lọi)
                    prefix = "-> [*] "
                else:
                    text_color = (220, 220, 230)  # Bước chưa tới (Màu Trắng)
                    prefix = "  [ ] " 

                item_y = 110 + (idx - start_idx) * 24
                coord_surf = font.render(f"{prefix}{node_text}", True, text_color)
                screen.blit(coord_surf, (taskbar_x + 10, item_y))
        else:
            no_path_surf = font.render("No path found!", True, (255, 100, 100))
            screen.blit(no_path_surf, (taskbar_x + 15, 90))
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()

if __name__ == "__main__":
    main()