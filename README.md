# TRI_TUE_NHANTAO
#  Pacman AI – Mô phỏng và So sánh 18 Thuật toán Trí tuệ Nhân tạo

##  Giới thiệu

Đồ án xây dựng hệ thống mô phỏng trò chơi **Pacman** trên nền tảng đồ họa 2D (Python + Pygame), trong đó tác nhân Pacman phải tự động tìm đường từ vị trí xuất phát (P) đến đích (G) trong mê cung dạng lưới. Hệ thống không dừng ở một thuật toán tìm đường đơn thuần, mà tích hợp **6 nhóm thuật toán AI** (tổng cộng **18 thuật toán**) nhằm nghiên cứu và so sánh khả năng suy luận, lập kế hoạch và ra quyết định của tác nhân trong nhiều loại môi trường khác nhau: tĩnh, có thông tin, tối ưu cục bộ, không xác định, có ràng buộc và đối kháng.

>  **[Chèn ảnh]** Ảnh chụp màn hình giao diện chính của chương trình (menu chọn thuật toán + bản đồ mê cung).

---

##  Mục tiêu đồ án

- Nghiên cứu và triển khai các thuật toán tìm kiếm trong AI.
- Xây dựng hệ thống mô phỏng Pacman AI trên môi trường mê cung 2D.
- Đánh giá hiệu quả hoạt động của từng thuật toán trong nhiều môi trường.
- So sánh ưu điểm, nhược điểm và khả năng ứng dụng thực tế của từng thuật toán.

---

##  Mô hình hóa bài toán (PEAS)

| Thành phần | Mô tả |
|---|---|
| **P – Performance** | Đến đích an toàn (né Ghost) → đường đi tối ưu (ít bước nhất) → tối ưu chi phí (né ô phạt / ăn Dots) → thời gian tính toán thấp |
| **E – Environment** | Lưới 2D rời rạc, khả năng quan sát biến thiên (toàn phần / một phần / sensorless), tuần tự, tĩnh hoặc động (có Ghost) |
| **A – Actuators** | 4 hướng di chuyển: lên / xuống / trái / phải |
| **S – Sensors** | GPS (vị trí), Collision (tường), Cost (bản đồ chi phí), Radar (vị trí Ghost), Memory (lịch sử di chuyển) |

Ký hiệu bản đồ: `P` = Pacman, `G` = Goal, `W` = Wall, khoảng trắng = ô trống.
- Trạng thái bắt đầu
0	W	W	W	W	W	W	W	W	W	W	W	W	W	W	W	W	W	W	W	W
1	P									W										W
2	W				W	W	W	W		W			W			W				W
3	W				W					W			W			W				W
4	W				W			W	W	W	W	W	W			W				W
5	W				W								W			W				W
6	W				W	W	W	W	W				W			W				W
7	W												W			W				W
8	W			W	W	W	W	W	W				W			W				W
9	W			W									W			W				W
10	W			W				W	W	W	W	W	W			W				W
11	W			W												W				W
12	W			W	W	W	W	W	W	W	W	W	W	W	W	W				W
13	W																			G
14	W	W	W	W	W	W	W	W	W	W	W	W	W	W	W	W	W	W	W	W
  
- Trạng thái kết thúc
0	W	W	W	W	W	W	W	W	W	W	W	W	W	W	W	W	W	W	W	W
1										W										W
2	W				W	W	W	W		W			W			W				W
3	W				W					W			W			W				W
4	W				W			W	W	W	W	W	W			W				W
5	W				W								W			W				W
6	W				W	W	W	W	W				W			W				W
7	W												W			W				W
8	W			W	W	W	W	W	W				W			W				W
9	W			W									W			W				W
10	W			W				W	W	W	W	W	W			W				W
11	W			W												W				W
12	W			W	W	W	W	W	W	W	W	W	W	W	W	W				W
13	W																			P
14	W	W	W	W	W	W	W	W	W	W	W	W	W	W	W	W	W	W	W	W

---

##  6 nhóm thuật toán đã triển khai

| Nhóm | Tên nhóm | Thuật toán đại diện |
|---|---|---|
| 1 | Tìm kiếm mù (Uninformed Search) | **BFS**, DFS, IDDFS |
| 2 | Tìm kiếm có thông tin (Informed Search) | **Greedy Best-First Search**, A*, IDA* |
| 3 | Tối ưu hóa cục bộ (Local Search) | Hill Climbing, Local Beam Search, **Simulated Annealing** |
| 4 | Môi trường không xác định (Uncertainty) | Partial Observable, **Sensorless (Conformant Planning)**, Nondeterministic |
| 5 | Thỏa mãn ràng buộc (CSP) | AC-3, **Backtracking Search**, Min-Conflicts |
| 6 | Tìm kiếm đối kháng (Adversarial Search) | **Minimax**, Alpha-Beta Pruning, Expectimax |

Mỗi thuật toán được demo trực tiếp trên cùng một bản đồ để đảm bảo tính công bằng khi so sánh.
- Nhóm thuật toán tìm kiếm mù
  <img width="2384" height="1798" alt="Nhom1" src="https://github.com/user-attachments/assets/ecf98974-955c-4cdb-a483-e6953392ea1e" />
- Nhóm thuật toán tìm kiếm có thông tin
  <img width="2384" height="1798" alt="Nhom2" src="https://github.com/user-attachments/assets/d1910ba6-032a-4d44-913f-08df9911e34d" />
- Nhóm thuật toán tối ưu hóa cục bộ
  <img width="2384" height="1798" alt="Nhom3" src="https://github.com/user-attachments/assets/318733e1-6890-4147-9fe6-444ebc13187c">
- Nhóm môi trường không xác định
  <img width="2384" height="1798" alt="Nhom4" src="https://github.com/user-attachments/assets/3090a17e-f2ba-4f37-91ed-b802a9215b90" />
- Nhóm bài toán thỏa mãn ràng buộc
  <img width="800" height="603" alt="Nhom5" src="https://github.com/user-attachments/assets/052b8be5-3d01-4178-9f21-7f6cd8c2f2db" />
- Nhóm thuật toán tìm kiếm đối kháng
  <img width="800" height="603" alt="Nhom6" src="https://github.com/user-attachments/assets/94bb0fe2-423f-44ce-9025-bde6a962faa3" />
---

##  Bảng so sánh chi tiết (dựa trên số liệu thực nghiệm trong báo cáo)

### Nhóm 1 — Tìm kiếm mù (Uninformed Search)

| Thuật toán | Số nút duyệt | Độ dài đường đi | Thời gian | Ghi chú |
|---|---|---|---|---|
| BFS | 125 | 31 bước (tối ưu) | 0.35 ms (nhanh nhất) | Đảm bảo đường đi ngắn nhất |
| DFS | 82 (ít nhất) | 59 bước | — | Tốn ít bộ nhớ nhưng đường đi dài, ngoằn ngoèo |
| IDDFS | 125 | 31 bước (tối ưu) | 35.50 ms (chậm nhất) | Lặp lại tìm kiếm nhiều lần |

### Nhóm 2 — Tìm kiếm có thông tin (Informed Search)

| Thuật toán | Số nút duyệt | Độ dài đường đi | Thời gian | Ghi chú |
|---|---|---|---|---|
| Greedy Best-First Search | 45 (ít nhất) | 65 bước | 0.25 ms (nhanh nhất) | Không đảm bảo tối ưu |
| A* Search | 58 | 37 bước (tối ưu) | 0.85 ms | Cân bằng tốc độ – tối ưu |
| IDA* | 58 | 37 bước (tối ưu) | 3.20 ms | Tối ưu, ít bộ nhớ nhưng chậm hơn A* |

### Nhóm 3 — Tối ưu hóa cục bộ (Local Search)

| Thuật toán | Số nút duyệt | Độ dài đường đi | Thời gian | Ghi chú |
|---|---|---|---|---|
| Hill Climbing | 31 (ít nhất) | 31 bước | 0.15 ms (nhanh nhất) | Nhanh nhưng dễ kẹt cực trị địa phương |
| Local Beam Search | 85 | 31 bước | — | Duy trì nhiều nhánh song song |
| Simulated Annealing | — | 67 bước | 3.10 ms | Thoát cực trị địa phương nhưng phụ thuộc yếu tố ngẫu nhiên |

### Nhóm 4 — Môi trường không xác định (Uncertainty)

| Thuật toán | Số nút duyệt | Độ dài đường đi | Thời gian | Ghi chú |
|---|---|---|---|---|
| Partial Observable | 150 (nhiều nhất) | 148 bước | 2.40 ms (ổn định) | Tái lập kế hoạch liên tục khi mở rộng tầm nhìn |
| Sensorless (Conformant) | 45 | — | 60.20 ms (chậm nhất) | Thu hẹp tập trạng thái niềm tin (Belief State) |
| Nondeterministic | 35 (ít nhất) | — | 8.50 ms | Lập kế hoạch theo nhiều khả năng có thể xảy ra |

*Cả 3 thuật toán đều đạt trạng thái SUCCESS trên bản đồ thử nghiệm.*

### Nhóm 5 — Thỏa mãn ràng buộc (CSP)

| Thuật toán | Số nút duyệt | Độ dài đường đi | Thời gian | Ghi chú |
|---|---|---|---|---|
| AC-3 | 65 | 57 bước (ngắn nhất) | 1.40 ms | Lọc miền giá trị trước khi tìm kiếm |
| Backtracking Search | 95 (nhiều nhất) | 83 bước (dài nhất) | 1.10 ms (nhanh nhất) | Quay lui khi vi phạm ràng buộc |
| Min-Conflicts | 40 (ít nhất) | 65 bước | 6.80 ms (chậm nhất) | Dễ sa lầy cực trị địa phương |

### Nhóm 6 — Tìm kiếm đối kháng (Adversarial Search)

| Thuật toán | Số nút duyệt | Độ dài đường đi | Thời gian | Ghi chú |
|---|---|---|---|---|
| Minimax | 2 | 76 bước | 0.31 ms | Dự đoán nước đi của Ghost |
| Alpha-Beta Pruning | 2 | 76 bước | 0.12 ms (nhanh nhất) | Cùng chất lượng Minimax, nhanh gấp ~3 lần nhờ cắt tỉa |
| Expectimax | 2 | 30 bước (ngắn nhất) | — | Tối ưu theo kỳ vọng, phù hợp Ghost di chuyển ngẫu nhiên |

- Tìm kiếm điểm mù 
<img width="936" height="165" alt="image" src="https://github.com/user-attachments/assets/ae05cbff-a3a9-4d6b-9973-323f1507a73c" />
- Tìm kiếm có thông tin 
- <img width="852" height="166" alt="image" src="https://github.com/user-attachments/assets/e67e020a-2b8f-44e8-96e9-29e095bab1d9" />
- Thuật toán tối ưu hóa cục bộ
- <img width="864" height="179" alt="image" src="https://github.com/user-attachments/assets/99d453d2-b7ed-48dc-9b44-4918483b5a62" />
- Môi trường không xác định
- <img width="865" height="183" alt="image" src="https://github.com/user-attachments/assets/4d790ded-efc3-4441-9727-a915ade011ef" />
- Thõa mãn ràng buộc
- <img width="877" height="193" alt="image" src="https://github.com/user-attachments/assets/d58f2101-46c9-4b5c-a37c-f7a8bc8059fa" />
- Thuật toán tiềm kiếm đối kháng
- <img width="905" height="191" alt="image" src="https://github.com/user-attachments/assets/064f3521-1a58-482e-a7ac-764c5f18963e" />
---

##  Nhận định so sánh giữa các nhóm

- **Tri thức (Heuristic) là chìa khóa**: so với nhóm tìm kiếm mù (G1), nhóm có thông tin (G2) giảm đáng kể số nút duyệt và thời gian nhờ hàm heuristic Manhattan.
- **Đánh đổi Không gian – Thời gian**: nhóm Local Search (G3) tiết kiệm bộ nhớ nhưng chất lượng lời giải kém ổn định; nhóm môi trường không xác định (G4) tốn thời gian do phải tính nhiều khả năng (Belief States).
- **Giá trị của Pruning**: Alpha-Beta Pruning (G6) nhanh gấp ~3 lần Minimax nhờ cắt tỉa nhánh, rất phù hợp game thời gian thực.
- **Không có thuật toán vạn năng**: mỗi nhóm phù hợp với một dạng môi trường riêng — hệ thống AI hiện đại cần biết chọn/kết hợp thuật toán theo đặc thù bài toán.

---

##  Ưu điểm hệ thống

- Kiến trúc thống nhất, tích hợp đồng thời 18 thuật toán trên cùng một môi trường mô phỏng.
- Giao diện trực quan, hỗ trợ quan sát thời gian thực quá trình ra quyết định của Pacman.
- Triển khai đa dạng loại môi trường: tĩnh, quan sát một phần, không xác định, có ràng buộc, đối kháng.

##  Hạn chế

- Một số thuật toán (Minimax, Sensorless) xử lý chậm khi bản đồ lớn.
- Nhóm Local Search phụ thuộc tham số khởi tạo, dễ kẹt cực trị địa phương.
- Mới chỉ thử nghiệm trên mê cung 2D với số lượng Ghost hạn chế.
- Heuristic còn đơn giản (chỉ dùng khoảng cách Manhattan).

##  Hướng phát triển

- Tích hợp Reinforcement Learning (Q-Learning, SARSA, DQN).
- Bổ sung Monte Carlo Tree Search, Genetic Algorithm.
- Mở rộng bản đồ lớn hơn, sinh ngẫu nhiên, nhiều Ghost với chiến thuật khác nhau.
- Thêm công cụ thống kê tự động (thời gian, số nút, chi phí, tỷ lệ thành công).
