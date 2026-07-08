import heapq
from collections import deque
import collections
import random
import math

# 1. BFS: Tìm đường ngắn nhất (số bước ít nhất)
def bfs(grid, start, goal):
    # Hàng đợi queue lưu trữ các vị trí cần duyệt theo thứ tự, start là tọa độ hiện tại, [start] là lộ trình đã đi]
    queue = deque([(start, [start])])
    # Tập hợp (Set) 'visited' lưu các ô đã đi qua. Sử dụng Set kiểm tra 'in' (O(1)) nhanh hơn List
    visited = {start}
    # Vòng lặp chính: chạy đến khi hàng đợi rỗng (không còn đường đi)
    while queue:
        # Lấy phần tử đầu tiên khỏi hàng đợi (FIFO)
        (x, y), path = queue.popleft()
        # Nếu đạt goal, trả về đường đi -> Tìm được đường ngắn nhất
        if (x, y) == goal:
            return path
        # Duyệt các ô lân cận PHẢI, TRÁI, XUỐNG, LÊN
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            # Điều kiện kiểm tra: nằm trong lưới, không phải tường, chưa thăm
            if 0 <= ny < len(grid) and 0 <= nx < len(grid[0]) and grid[ny][nx] != 'W' and (nx, ny) not in visited:
                visited.add((nx, ny))   # Đánh dấu đã thăm
                queue.append(((nx, ny), path + [(nx, ny)])) # Thêm vào cuối hàng đợi
    return []

# 2. IDA*: Tìm đường tối ưu với bộ nhớ cực thấp (Đệ quy & Quay lui)
def ida_star(grid, cost_map, start, goal):
    def heuristic_star(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def search(path, g, f_limit, visited):
        current = path[-1]

        f = g + heuristic_star(current, goal)
        if f > f_limit:
            return f, None

        if current == goal:
            return True, path.copy()

        min_val = float('inf')

        neighbors = []

        for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
            neighbor = (current[0] + dx, current[1] + dy)

            if (
                0 <= neighbor[1] < len(grid)
                and 0 <= neighbor[0] < len(grid[0])
                and grid[neighbor[1]][neighbor[0]] != 'W'
                and neighbor not in visited
            ):
                neighbors.append(neighbor)

        neighbors.sort(
            key=lambda p:
                heuristic_star(p, goal)
                + cost_map[p[1]][p[0]]
            )

        for neighbor in neighbors:
            visited.add(neighbor)
            path.append(neighbor)

            cost = cost_map[neighbor[1]][neighbor[0]]

            found, result_path = search(
                path,
                g + cost,
                f_limit,
                visited
            )

            path.pop()
            visited.remove(neighbor)

            if found is True:
                return True, result_path

            if found < min_val:
                min_val = found

        return min_val, None

    f_limit = heuristic_star(start, goal)

    while f_limit != float('inf'):
        result, path = search([start], 0, f_limit, {start})

        if result is True:
            return path

        if result == float('inf'):
            return []

        f_limit = result

    return []

# # 3. Local Beam Search: Tìm đường đi tốn ít chi phí nhất 
def local_beam_search(grid, cost_map, start, goal, k=15): # TĂNG k LÊN 15
    def heuristic_beam(a, b): 
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
        
    # Khởi tạo chùm với (f_score, chi phí g, vị trí, đường đi)
    beam = [(heuristic_beam(start, goal), 0, start, [start])]
    
    # Dùng dictionary visited để lưu chi phí g thấp nhất tại mỗi ô.
    visited = {start: 0}
    
    iterations = 0
    max_iterations = 2000 
    
    while beam and iterations < max_iterations:
        iterations += 1
        next_beam = []
        
        # Duyệt qua từng trạng thái trong chùm hiện tại
        for f, g, (x, y), path in beam:
            # Trả về đường đi nếu đã tới đích
            if (x, y) == goal: 
                return path
                
            # Duyệt 4 hướng lân cận
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = x + dx, y + dy
                
                # Kiểm tra giới hạn bản đồ và tường
                if 0 <= ny < len(grid) and 0 <= nx < len(grid[0]) and grid[ny][nx] != 'W':
                    new_g = g + cost_map[ny][nx]
                    
                    # Chỉ kết nạp ô mới nếu chưa từng có tia nào đi qua,
                    # HOẶC tia hiện tại tìm được đường đến ô đó với chi phí RẺ HƠN.
                    if (nx, ny) not in visited or new_g < visited[(nx, ny)]:
                        visited[(nx, ny)] = new_g
                        new_path = path + [(nx, ny)]
                        f_score = new_g + heuristic_beam((nx, ny), goal)
                        next_beam.append((f_score, new_g, (nx, ny), new_path))
                        
        # Nếu không còn hướng nào để đi, thoát sớm
        if not next_beam: 
            break
            
        # Sắp xếp các trạng thái theo f_score tăng dần
        next_beam.sort(key=lambda x: x[0])
        # Giữ lại k trạng thái có chi phí thấp nhất
        beam = next_beam[:k]
        
    # Trả về rỗng nếu không tìm thấy đường hoặc vượt quá giới hạn
    return []

# 4. Thuật toán DFS (Depth-First Search) - Tìm kiếm theo chiều sâu
def dfs(grid, start, goal):
    # Khởi tạo Stack (Ngăn xếp) để lưu trữ các trạng thái cần duyệt.
    # Mỗi phần tử là một tuple gồm: (tọa độ_hiện_tại, lộ_trình_từ_điểm_xuất_phát)
    stack = [(start, [start])]
    
    # Sử dụng Set (Tập hợp) để lưu các đỉnh đã duyệt.
    # Mục đích: Tối ưu thời gian tra cứu O(1) và ngăn chặn tình trạng lặp vô hạn (chu trình).
    visited = {start}
    
    while stack:
        # Trích xuất trạng thái mới nhất từ đỉnh Stack (nguyên lý LIFO - Last In, First Out).
        # Thao tác này định hình đặc tính của DFS: Liên tục đào sâu vào một nhánh cho đến khi chạm ngõ cụt.
        current, path = stack.pop()
        
        # Điều kiện dừng: Nếu đỉnh hiện tại là đích đến, thuật toán hoàn tất và trả về lộ trình.
        if current == goal:
            return path
            
        # Mở rộng không gian trạng thái bằng cách duyệt qua các đỉnh kề (Lên, Xuống, Trái, Phải).
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx = current[0] + dx
            ny = current[1] + dy
            
            # Ràng buộc không gian:
            # 1. Tọa độ (nx, ny) phải nằm trong giới hạn của ma trận.
            # 2. Ô lưới không phải là vật cản/tường ('W').
            if 0 <= ny < len(grid) and 0 <= nx < len(grid[0]) and grid[ny][nx] != 'W':
                
                # Chỉ xử lý các trạng thái chưa được đưa vào tập closed (visited).
                if (nx, ny) not in visited:
                    visited.add((nx, ny)) # Đánh dấu trạng thái đã duyệt
                    
                    # Cập nhật lộ trình và đẩy trạng thái mới vào Stack để tiếp tục khai triển ở bước sau.
                    stack.append(((nx, ny), path + [(nx, ny)]))
                    
    # Trả về mảng rỗng nếu không gian trạng thái đã cạn mà không tìm thấy lời giải.
    return []

# 5. Greedy Best-First Search - Thuật toán Tìm kiếm Tham lam
def greedy_search(grid, start, goal):
    # Khởi tạo Hàng đợi (Queue) để lưu trữ các trạng thái đang mở.
    queue = [(start, [start])]
    
    # Sử dụng Set để lưu trữ các trạng thái đã đóng (đã duyệt).
    visited = {start}
    
    while queue:
        best_idx = 0
        min_dist = float('inf') # Khởi tạo giới hạn vô cùng lớn
        
        # Đánh giá heuristic cho toàn bộ các trạng thái hiện có trong hàng đợi.
        # Mục tiêu: Chọn ra trạng thái có giá trị heuristic (h) nhỏ nhất.
        for i in range(len(queue)):
            curr_pos = queue[i][0]
            
            # Sử dụng khoảng cách Manhattan làm hàm Heuristic h(n)
            # Công thức: h(n) = |x1 - x2| + |y1 - y2|
            dist = abs(curr_pos[0] - goal[0]) + abs(curr_pos[1] - goal[1])
            
            # Cập nhật trạng thái có triển vọng nhất
            if dist < min_dist:
                min_dist = dist
                best_idx = i
        
        # Trích xuất trạng thái ưu tiên cao nhất (h(n) nhỏ nhất) ra khỏi hàng đợi để duyệt.
        current, path = queue.pop(best_idx)
        
        # Điều kiện dừng: Đạt được trạng thái đích.
        if current == goal:
            return path
            
        # Mở rộng trạng thái hiện tại theo 4 hướng kề.
        # Đổi thứ tự ưu tiên: Duyệt Trái/Phải trước, Lên/Xuống sau
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = current[0] + dx, current[1] + dy
            
            # Ràng buộc điều kiện hợp lệ của ma trận (không vượt biên, không chạm tường).
            if 0 <= ny < len(grid) and 0 <= nx < len(grid[0]) and grid[ny][nx] != 'W':
                
                # Tránh việc duyệt lại các trạng thái đã đưa vào tập closed (visited).
                if (nx, ny) not in visited:
                    visited.add((nx, ny))
                    
                    # Đẩy trạng thái mới vào hàng đợi để đánh giá heuristic ở vòng lặp tiếp theo.
                    queue.append(((nx, ny), path + [(nx, ny)]))
                    
    # Trả về danh sách rỗng nếu thuật toán hội tụ mà không tìm thấy đường đi.
    return []

# 6. Thuật toán Luyện kim mô phỏng (Simulated Annealing)
def simulated_annealing(grid, start, goal):
    # Các tham số hệ thống
    T = 100.0         
    T_min = 0.01      
    alpha = 0.995     # Tăng nhẹ hệ số (0.995) để làm lạnh chậm hơn, cho phép khám phá sâu hơn
    
    current_state = start
    path = [current_state] 
    
    # Bổ sung bộ nhớ để tránh đi lặp lại ô cũ (tránh infinite loop)
    visited = {start}
    
    def h(pos):
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    while T > T_min:
        # Điều kiện hội tụ: Đạt được trạng thái đích
        if current_state == goal:
            return path
            
        # Tìm các láng giềng hợp lệ (CHƯA TỪNG ĐI QUA)
        neighbors = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = current_state[0] + dx, current_state[1] + dy
            if 0 <= ny < len(grid) and 0 <= nx < len(grid[0]) and grid[ny][nx] != 'W':
                if (nx, ny) not in visited:
                    neighbors.append((nx, ny))
                
        # Xử lý ngõ cụt (Dead-end): Nếu không còn đường đi mới, buộc phải quay lui
        if not neighbors:
            if len(path) > 1:
                path.pop() # Xóa ô hiện tại khỏi lộ trình
                current_state = path[-1] # Lùi lại 1 bước
                continue # Bỏ qua bước làm lạnh để tiếp tục tìm đường
            else:
                break # Kẹt hoàn toàn tại điểm xuất phát
                
        # Chọn ngẫu nhiên một trạng thái láng giềng
        next_state = random.choice(neighbors)
        
        # Tính delta heuristic
        delta = h(next_state) - h(current_state)
        
        # Nguyên lý SA: Chấp nhận vô điều kiện nước đi tốt, hoặc chấp nhận có xác suất nước đi xấu
        if delta < 0:
            current_state = next_state
            visited.add(current_state)
            path.append(current_state)
        else:
            p = math.exp(-delta / T)
            if random.random() < p:
                current_state = next_state
                visited.add(current_state)
                path.append(current_state)
                
        # Cập nhật lịch trình làm lạnh (Cooling Schedule)
        T = alpha * T
        
    # Trả về mảng rỗng nếu cạn nhiệt độ mà vẫn chưa tới đích
    return []

# 7. Partial Observable
def partial_observable(grid, p_pos, goal, visited_tiles, partial_history):
    px, py = p_pos
    # 4 hướng đi cơ bản
    moves = [(px+1, py), (px-1, py), (px, py+1), (px, py-1)]
    
    # Lọc bỏ tường
    valid_moves = [m for m in moves if 0 <= m[1] < len(grid) and 0 <= m[0] < len(grid[0]) and grid[m[1]][m[0]] != 'W']
    
    # 1. Nếu đứng cạnh đích, đi vào đích ngay
    for m in valid_moves:
        if m == goal: return [p_pos, m]
        
    # 2. Ưu tiên những ô chưa thăm (để mở rộng bản đồ)
    unvisited = [
        m for m in valid_moves
        if (m[1], m[0]) not in visited_tiles
    ]
    
    # 3. Tính toán trọng số cho các hướng đi
    # Pacman sẽ chọn hướng nào gần đích nhất (Manhattan distance)
    if unvisited:
        # Chọn ô chưa thăm mà gần đích nhất
        best_move = min(unvisited, key=lambda m: abs(m[0]-goal[0]) + abs(m[1]-goal[1]))
        return [p_pos, best_move]
    
    # 4. Nếu xung quanh đều đã thăm (KẸT): Chỉ lùi về ô trước đó
    # Đây là lúc nó mới dùng đến lịch sử để quay đầu
    if len(partial_history) >= 2:
        prev = partial_history[-2]

    # Xóa vị trí hiện tại khỏi lịch sử để tránh lặp qua lại
        partial_history.pop()

        return [p_pos, prev]
        
    # Nếu không còn đường nào khác, đứng im
    return [p_pos]

# 8. SENSORLESS (Môi trường mù / Conformant Planning)

def conformant_sensorless(grid, start, goal):
    from collections import deque
    
    # 1. Khởi tạo Trạng thái Niềm tin ban đầu (Belief State)
    # Thay vì 1 điểm, nó là một TẬP HỢP (frozenset) các vị trí có thể
    initial_belief = frozenset([start])
    
    # Queue lưu: (trạng_thái_niềm_tin_hiện_tại, lộ_trình_hành_động)
    queue = deque([(initial_belief, [start])])
    
    # Lưu các Belief State đã xét để tránh lặp vô tận
    visited_beliefs = {initial_belief}
    
    while queue:
        current_belief, path = queue.popleft()
        
        # 2. Điều kiện đích: TẤT CẢ các vị trí trong Belief State đều phải là Đích
        if all(state == goal for state in current_belief):
            return path
            
        # 3. Thử áp dụng 4 hành động (Lên, Xuống, Trái, Phải)
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            next_belief = set()
            
            # Dự đoán kết quả của hành động lên TOÀN BỘ không gian niềm tin
            for x, y in current_belief:
                nx, ny = x + dx, y + dy
                
                # Hàm chuyển trạng thái (Transition Model) không có cảm biến:
                if 0 <= ny < len(grid) and 0 <= nx < len(grid[0]) and grid[ny][nx] != 'W':
                    next_belief.add((nx, ny)) # Đường trống -> Đi tới
                else:
                    next_belief.add((x, y))   # Đụng tường -> Trượt tại chỗ (Không chết)
                    
            next_belief_frozen = frozenset(next_belief)
            
            # 4. Nếu Trạng thái Niềm tin này là mới, đưa vào Queue
            if next_belief_frozen not in visited_beliefs:
                visited_beliefs.add(next_belief_frozen)
                
                # Lấy đại diện tọa độ để Pacman biết đường vẽ đồ họa
                representative_state = list(next_belief)[0]
                queue.append((next_belief_frozen, path + [representative_state]))
                
    return []
# 9. AC-3:
def ac3(grid, ghost_positions, start, goal, danger_radius=1):
    # Lấy kích thước hàng và cột của mê cung
    rows, cols = len(grid), len(grid[0])
    # Khởi tạo tập hợp chứa các tọa độ ô không an toàn
    forbidden = set()
    # Duyệt qua vị trí của từng con ma
    for gx, gy in ghost_positions:
        # Duyệt trong vùng bán kính nguy hiểm xung quanh con ma
        for r in range(gy - danger_radius, gy + danger_radius + 1):
            for c in range(gx - danger_radius, gx + danger_radius + 1):
                # Kiểm tra nếu tọa độ nằm trong phạm vi bản đồ
                if 0 <= r < rows and 0 <= c < cols:
                    # Không được cấm vị trí bắt đầu hoặc đích
                    if (c, r) != start and (c, r) != goal:
                        # Thêm ô này vào danh sách cấm
                        forbidden.add((c, r))
    # Khởi tạo dictionary lưu danh sách kề cho mỗi ô an toàn
    domain = {}
    for r in range(rows):
        for c in range(cols):
            # Nếu ô không phải là tường và không nằm trong vùng cấm
            if grid[r][c] != 'W' and (c, r) not in forbidden:
                # Danh sách các hàng xóm hợp lệ
                neighbors = []
                # Xét 4 hướng lân cận: Phải, Trái, Lên, Xuống
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nx, ny = c + dx, r + dy
                    # Kiểm tra ô lân cận nằm trong lưới, không phải tường và không bị cấm
                    if 0 <= ny < rows and 0 <= nx < cols and grid[ny][nx] != 'W' and (nx, ny) not in forbidden:
                        # Thêm vào danh sách hàng xóm hợp lệ
                        neighbors.append((nx, ny))
                # Lưu danh sách hàng xóm vào domain
                domain[(c, r)] = neighbors
    # # Hàng đợi lưu (vị trí hiện tại, đường đi đã đi được)
    queue = deque([(start, [start])])
    # Tập hợp các ô đã duyệt để tránh vòng lặp
    visited = {start}
    # Lặp chừng nào hàng đợi còn phần tử
    while queue:
        # Lấy phần tử đầu tiên ra
        curr, path = queue.popleft()
        # Nếu đã tới đích, trả về lộ trình tìm được
        if curr == goal:
            return path
        # Duyệt các hàng xóm hợp lệ đã được lưu trong domain
        for neighbor in domain.get(curr, []):
            # Nếu chưa thăm ô này
            if neighbor not in visited:
                # Đánh dấu đã thăm
                visited.add(neighbor)
                # Thêm vào hàng đợi để duyệt tiếp
                queue.append((neighbor, path + [neighbor]))
    # Nếu hàng đợi cạn mà không tìm thấy đích, trả về danh sách trống
    return []

#10. Alpha-Beta:
def get_valid_moves(grid, pos):
    # Đảm bảo pos luôn là một tuple phẳng dạng (x, y)
    if isinstance(pos, (list, tuple)) and len(pos) > 0:
        if isinstance(pos[0], (list, tuple)):
            pos = pos[0]
    
    x, y = int(pos[0]), int(pos[1])
    moves = []
    
    # Duyệt 4 hướng đi hợp lệ
    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        nx, ny = x + dx, y + dy
        if 0 <= ny < len(grid) and 0 <= nx < len(grid[0]):
            if grid[ny][nx] != 'W':
                moves.append((nx, ny))
    return moves

def get_real_distance(grid, start_pos, end_pos):
    """Tính khoảng cách thực tế đi trong mê cung thay vì đường chim bay"""
    if start_pos == end_pos: return 0
    queue = [(start_pos, 0)]
    visited = {start_pos}
    
    while queue:
        curr, dist = queue.pop(0)
        if curr == end_pos:
            return dist
        for nx, ny in get_valid_moves(grid, curr):
            if (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append(((nx, ny), dist + 1))
    return 999 # Không có đường tới

def heuristic(p_pos, g_pos, goal, is_pacman, grid):
    px, py = int(p_pos[0]), int(p_pos[1])
    gx, gy = int(g_pos[0]), int(g_pos[1])
    
    # Thay thế Manhattan bằng khoảng cách di chuyển thực tế trên mê cung
    goal_dist = get_real_distance(grid, p_pos, goal)
    ghost_dist = get_real_distance(grid, p_pos, g_pos)
    
    if is_pacman:
        if ghost_dist <= 2: # Nếu ma ở khoảng cách 2 ô
            return -999999  # Phạt cực nặng để nó sợ và đổi hướng
        return (-goal_dist * 50) + (ghost_dist * 100)
    else:
        if ghost_dist == 0:
            return -999999
        return ghost_dist * 100

def alpha_beta(grid, p_pos, g_pos, goal, depth, alpha, beta, is_pacman, ghost_history=None):
    if ghost_history is None: 
        ghost_history = []
        
    if depth == 0 or p_pos == g_pos or p_pos == goal:
        return heuristic(p_pos, g_pos, goal, is_pacman, grid)

    if is_pacman:
        value = float('-inf')
        for nxt in get_valid_moves(grid, p_pos):
            # Nhường lượt kế tiếp cho MA (is_pacman=False)
            score = alpha_beta(grid, nxt, g_pos, goal, depth - 1, alpha, beta, False, ghost_history)
            value = max(value, score)
            alpha = max(alpha, value)
            if beta <= alpha: 
                break
        return value
    else:
        value = float('inf')
        for nxt in get_valid_moves(grid, g_pos):
            if nxt in ghost_history[-2:]: 
                continue
            # Nhường lượt kế tiếp cho PACMAN (is_pacman=True)
            score = alpha_beta(grid, p_pos, nxt, goal, depth - 1, alpha, beta, True, ghost_history + [nxt])
            value = min(value, score)
            beta = min(beta, value)
            if beta <= alpha: 
                break
        return value

def get_best_move(grid, p_pos, g_pos, goal, depth, history):
    # Lấy đường đi ngắn nhất tới Goal
    bfs_path = bfs(grid, p_pos, goal)

    # Nếu không còn đường
    if len(bfs_path) < 2:
        return [p_pos]

    valid_moves = get_valid_moves(grid, p_pos)
    recent = history[-4:] if len(history) >= 4 else history
    best_move = bfs_path[1]
    best_score = float("-inf")

    for move in valid_moves:

        if move in recent:
            continue

        score = alpha_beta(
            grid,
            move,
            g_pos,
            goal,
            depth - 1,
            float("-inf"),
            float("inf"),
            False,
            history # Thêm tham số này vào
        )

        # thưởng nếu đi đúng hướng BFS
        if move == bfs_path[1]:
            score += 50

        if score > best_score:
            best_score = score
            best_move = move
        if best_move == p_pos:
            best_move = bfs_path[1]
    return [p_pos, best_move]

def get_best_ghost_move(grid, p_pos, g_pos, goal, depth, ghost_history):
    valid_moves = get_valid_moves(grid, g_pos)
    if not valid_moves: 
        return g_pos
    
    best_move = g_pos
    best_value = float('inf')
    
    for nxt in valid_moves:
        if nxt in ghost_history[-2:]: 
            continue
        # Giả lập Ma đi thử nxt -> lượt tiếp theo cây tính toán của PACMAN (True)
        val = alpha_beta(grid, p_pos, nxt, goal, depth - 1, float('-inf'), float('inf'), True, ghost_history + [nxt])
        if val < best_value:
            best_value = val
            best_move = nxt
    return best_move

# 11. BACKTRACKING (NHÓM 5)
def backtracking(grid, ghost_positions, start, goal, danger_radius=1):
    rows, cols = len(grid), len(grid[0])
    forbidden = set()
    
    # 1. Tính toán vùng nguy hiểm của các con ma
    for gx, gy in ghost_positions:
        for r in range(int(gy) - danger_radius, int(gy) + danger_radius + 1):
            for c in range(int(gx) - danger_radius, int(gx) + danger_radius + 1):
                if 0 <= r < rows and 0 <= c < cols:
                    if (c, r) != start and (c, r) != goal:
                        forbidden.add((c, r))

    # 2. Hàm đệ quy tìm đường
    def backtrack(curr, path, visited):
        if curr == goal:
            return path
            
        # Duyệt 4 hướng lân cận
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = curr[0] + dx, curr[1] + dy
            
            # Chộp đích ngay nếu thấy
            if (nx, ny) == goal:
                return path + [(nx, ny)]
                
            # Kiểm tra hợp lệ: trong bản đồ, không đụng tường, không vào vùng cấm, chưa thăm
            if 0 <= ny < rows and 0 <= nx < cols:
                if grid[ny][nx] != 'W' and (nx, ny) not in forbidden and (nx, ny) not in visited:
                    visited.add((nx, ny)) # Đánh dấu đã thăm
                    
                    # Gọi đệ quy đi tiếp
                    result = backtrack((nx, ny), path + [(nx, ny)], visited)
                    if result: 
                        return result # Nếu tìm thấy đường thì trả về luôn
                        
        return [] # Hết đường thì quay lui

    return backtrack(start, [start], {start})
# 12. MINIMAX (NHÓM 6)
def minimax(grid, p_pos, g_pos, goal, depth, is_pacman, ghost_history=None):
    if ghost_history is None: 
        ghost_history = []
        
    # Điều kiện dừng: Hết độ sâu hoặc đụng nhau hoặc tới đích
    if depth == 0 or p_pos == g_pos or p_pos == goal:
        return heuristic(p_pos, g_pos, goal, is_pacman, grid)

    if is_pacman:
        value = float('-inf')
        for nxt in get_valid_moves(grid, p_pos):
            # Nhường lượt kế tiếp cho MA (is_pacman=False)
            score = minimax(grid, nxt, g_pos, goal, depth - 1, False, ghost_history)
            value = max(value, score)
            # Khác biệt: Không có cắt tỉa alpha-beta ở đây
        return value
    else:
        value = float('inf')
        for nxt in get_valid_moves(grid, g_pos):
            if nxt in ghost_history[-2:]: 
                continue
            # Nhường lượt kế tiếp cho PACMAN (is_pacman=True)
            score = minimax(grid, p_pos, nxt, goal, depth - 1, True, ghost_history + [nxt])
            value = min(value, score)
            # Khác biệt: Không có cắt tỉa alpha-beta ở đây
        return value

def get_best_move_minimax_pacman(grid, p_pos, g_pos, goal, depth, history):
    bfs_path = bfs(grid, p_pos, goal)
    if len(bfs_path) < 2:
        return [p_pos]

    valid_moves = get_valid_moves(grid, p_pos)
    recent = history[-4:] if len(history) >= 4 else history
    best_move = bfs_path[1]
    best_score = float("-inf")

    for move in valid_moves:
        if move in recent:
            continue
            
        # Gọi hàm Minimax thay vì Alpha-Beta
        score = minimax(grid, move, g_pos, goal, depth - 1, False, history)

        if move == bfs_path[1]:
            score += 50

        if score > best_score:
            best_score = score
            best_move = move
        if best_move == p_pos:
            best_move = bfs_path[1]
    return [p_pos, best_move]

def get_best_ghost_move_minimax(grid, p_pos, g_pos, goal, depth, ghost_history):
    valid_moves = get_valid_moves(grid, g_pos)
    if not valid_moves: 
        return g_pos
    
    best_move = g_pos
    best_value = float('inf')
    
    for nxt in valid_moves:
        if nxt in ghost_history[-2:]: 
            continue
        # Gọi hàm Minimax thay vì Alpha-Beta
        val = minimax(grid, p_pos, nxt, goal, depth - 1, True, ghost_history + [nxt])
        if val < best_value:
            best_value = val
            best_move = nxt
    return best_move


# 13. IDDFS - Iterative Deepening Depth-First Search
def iddfs(grid, start, goal):

    def dls(node, path, depth, visited):
        """DLS - Depth Limited Search: DFS giới hạn độ sâu"""
        if node == goal:
            return path
        if depth == 0:
            return None
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = node[0] + dx, node[1] + dy
            if (0 <= ny < len(grid) and 0 <= nx < len(grid[0])
                    and grid[ny][nx] != 'W' and (nx, ny) not in visited):
                visited.add((nx, ny))
                result = dls((nx, ny), path + [(nx, ny)], depth - 1, visited)
                visited.remove((nx, ny))
                if result is not None:
                    return result
        return None

    # Tăng dần giới hạn độ sâu từ 0 đến khi tìm thấy đường
    max_depth = len(grid) * len(grid[0])
    for depth in range(max_depth):
        visited = {start}
        result = dls(start, [start], depth, visited)
        if result is not None:
            return result
    return []


# 14. LEO ĐỒI (Hill Climbing) - Steepest Ascent
def hill_climbing(grid, start, goal):
    def heuristic_hill(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    current = start
    path = [start]
    visited = {start}

    while current != goal:
        neighbors = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = current[0] + dx, current[1] + dy
            if (0 <= ny < len(grid) and 0 <= nx < len(grid[0])
                    and grid[ny][nx] != 'W' and (nx, ny) not in visited):
                neighbors.append((nx, ny))

        if not neighbors:
            # Kẹt cục bộ: quay lui về vị trí chưa kẹt
            if len(path) > 1:
                path.pop()
                current = path[-1]
                continue
            else:
                return []  # Hoàn toàn bị kẹt

        # Chọn hàng xóm gần đích nhất (tham lam)
        best = min(neighbors, key=lambda p: heuristic_hill(p, goal))
        best_h = heuristic_hill(best, goal)
        curr_h = heuristic_hill(current, goal)

        if best_h >= curr_h and len(neighbors) > 1:
            # Nếu hàng xóm tốt nhất không tốt hơn hiện tại, chọn ngẫu nhiên để thoát
            import random
            best = random.choice(neighbors)

        visited.add(best)
        path.append(best)
        current = best

    return path


# 15. EXPECTIMAX - Expectimax Search
def heuristic_expectimax(p_pos, g_pos, goal, grid):
    # Tính Manhattan distance
    dist_to_goal = abs(p_pos[0] - goal[0]) + abs(p_pos[1] - goal[1])
    dist_to_ghost = abs(p_pos[0] - g_pos[0]) + abs(p_pos[1] - g_pos[1])
    
    score = -dist_to_goal
    if dist_to_ghost <= 2: 
        score -= 1000 # Trừng phạt khi gần ma
    return score

def expectimax(grid, p_pos, g_pos, goal, depth, is_pacman, ghost_history):
    # Điều kiện dừng
    if depth == 0 or p_pos == g_pos:
        return heuristic_expectimax(p_pos, g_pos, goal, grid)

    if is_pacman:
        value = float('-inf')
        moves = get_valid_moves(grid, p_pos) # Đảm bảo hàm này đã có trong algorithms.py
        for nxt in moves:
            score = expectimax(grid, nxt, g_pos, goal, depth - 1, False, ghost_history)
            value = max(value, score)
        return value
    else:
        moves = get_valid_moves(grid, g_pos)
        # Lọc để tránh ma đứng yên tại chỗ
        filtered_moves = [m for m in moves if m not in ghost_history[-2:]]
        valid_moves = filtered_moves if filtered_moves else moves
        
        prob = 1.0 / len(valid_moves)
        value = 0.0
        for nxt in valid_moves:
            value += prob * expectimax(grid, p_pos, nxt, goal, depth - 1, True, ghost_history + [nxt])
        return value

def get_best_move_expectimax(grid, p_pos, g_pos, goal, depth, history):
    valid_moves = get_valid_moves(grid, p_pos)
    bfs_path = bfs(grid, p_pos, goal) # Đảm bảo hàm bfs đã có
    
    best_move = bfs_path[1] if len(bfs_path) > 1 else p_pos
    best_score = float('-inf')
    recent = history[-4:]

    for move in valid_moves:
        # Gọi hàm expectimax trong CÙNG FILE nên không còn lỗi NameError
        score = expectimax(grid, move, g_pos, goal, depth - 1, False, [])
        if move in recent:
            score -= 200
        if len(bfs_path) > 1 and move == bfs_path[1]:
            score += 50
        if score > best_score:
            best_score = score
            best_move = move
            
    if best_move == p_pos and len(bfs_path) > 1:
        return [p_pos, bfs_path[1]]
    return [p_pos, best_move]

def get_best_ghost_move_expectimax(grid, p_pos, g_pos, goal, depth, ghost_history):
    valid_moves = get_valid_moves(grid, g_pos)
    if not valid_moves: return g_pos
    filtered = [m for m in valid_moves if m not in ghost_history[-2:]]
    return random.choice(filtered if filtered else valid_moves)


def get_best_ghost_move_expectimax(grid, p_pos, g_pos, goal, depth, ghost_history):
    """Ma trong Expectimax di chuyển ngẫu nhiên (không phải tối ưu)"""
    valid_moves = get_valid_moves(grid, g_pos)
    if not valid_moves:
        return g_pos
    valid_moves = [m for m in valid_moves if m not in ghost_history[-2:]] or valid_moves
    import random
    return random.choice(valid_moves)


# 16. MIN-CONFLICTS (CSP Local Search)
def min_conflicts(grid, ghost_position,start, goal, max_steps=5000):
    import random

    def conflicts(pos):
        """Số xung đột = khoảng cách Manhattan tới đích"""
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    current = start
    path = [start]
    visited = {start}

    for _ in range(max_steps):
        if current == goal:
            return path

        neighbors = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = current[0] + dx, current[1] + dy
            if (0 <= ny < len(grid) and 0 <= nx < len(grid[0])
                    and grid[ny][nx] != 'W' and (nx, ny) not in visited):
                neighbors.append((nx, ny))

        if not neighbors:
            # Kẹt: quay lui (backtrack)
            if len(path) > 1:
                path.pop()
                current = path[-1]
                continue
            else:
                return []

        min_c = min(conflicts(n) for n in neighbors)
        best_neighbors = [n for n in neighbors if conflicts(n) == min_c]

        # Chọn ngẫu nhiên trong số các hàng xóm tốt nhất (tránh kẹt đối xứng)
        chosen = random.choice(best_neighbors)
        visited.add(chosen)
        path.append(chosen)
        current = chosen

    return []

#17. Nondeterministic
def nondeterministic(grid, start, goal):
    import random
    from collections import deque
    
    print(f"[ALGO] nondeterministic called: start={start}, goal={goal}")
    print(f"[ALGO] grid size: {len(grid)} rows x {len(grid[0])} cols")
    print(f"[ALGO] start cell: {grid[start[1]][start[0]]!r}")
    print(f"[ALGO] goal cell:  {grid[goal[1]][goal[0]]!r}")

    if not start or not goal:
        print("[ALGO] ERROR: start or goal is None")
        return []
    if grid[start[1]][start[0]] == 'W':
        print("[ALGO] ERROR: start is a wall")
        return []
    if grid[goal[1]][goal[0]] == 'W':
        print("[ALGO] ERROR: goal is a wall")
        return []

    queue = deque([(start, [start])])
    visited = {start}

    while queue:
        (x, y), path = queue.popleft()
        if (x, y) == goal:
            print(f"[ALGO] Path found! Length={len(path)}")
            return path
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if (0 <= ny < len(grid) and 0 <= nx < len(grid[0])
                    and grid[ny][nx] != 'W' and (nx, ny) not in visited):
                visited.add((nx, ny))
                queue.append(((nx, ny), path + [(nx, ny)]))

    print("[ALGO] ERROR: No path found after exhausting all nodes")
    return []

# A* (A-Star Search)
def a_star(grid, cost_map, start, goal):

    def heuristic_astar(a, b):
        # Manhattan Distance
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Priority Queue: (f, g, node, path)
    open_set = []
    heapq.heappush(
        open_set,
        (heuristic_astar(start, goal), 0, start, [start])
    )

    visited = {}

    while open_set:
        f, g, current, path = heapq.heappop(open_set)

        if current == goal:
            return path

        if current in visited and visited[current] <= g:
            continue

        visited[current] = g

        x, y = current

        for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
            nx = x + dx
            ny = y + dy

            if (
                0 <= ny < len(grid)
                and 0 <= nx < len(grid[0])
                and grid[ny][nx] != 'W'
            ):
                neighbor = (nx, ny)

                new_g = g + cost_map[ny][nx]
                new_f = new_g + heuristic_astar(neighbor, goal)

                heapq.heappush(
                    open_set,
                    (
                        new_f,
                        new_g,
                        neighbor,
                        path + [neighbor]
                    )
                )

    return []