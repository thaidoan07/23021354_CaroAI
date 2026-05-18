[README.md](https://github.com/user-attachments/files/27958038/README.md)
# Caro AI – Minimax & Alpha-Beta Pruning

Game cờ Caro (4 quân liên tiếp) với AI sử dụng thuật toán **Minimax** và **Alpha-Beta Pruning**.  
Bàn cờ 9×9, giao diện pygame. Bài tập giữa kỳ – môn Trí tuệ nhân tạo.

---

## Cài đặt & Chạy

```bash
# 1. Cài thư viện
pip install -r requirements.txt

# 2. Chạy game
cd source_code
python main.py

# 3. Chạy benchmark (Level 3)
python benchmark.py
```

---

## Cách chơi

| Thao tác | Kết quả |
|---|---|
| Click ô trên bàn cờ | Đánh quân X |
| `R` | Chơi lại |
| `M` | Đổi chế độ AI (Minimax ↔ Alpha-Beta) |
| `+` / `-` | Tăng / giảm độ sâu tìm kiếm |
| `B` | Chạy Benchmark và in kết quả ra console |
| `ESC` | Thoát |

---

## Cấu trúc thư mục

```
source_code/
├── main.py        # Giao diện pygame – điểm chạy chính
├── game.py        # Logic bàn cờ, luật chơi, kiểm tra thắng
├── ai.py          # Thuật toán Minimax và Alpha-Beta
├── evaluate.py    # Hàm đánh giá trạng thái
└── benchmark.py   # Level 3 – so sánh hai thuật toán
requirements.txt
README.md
```

---

## Thuật toán

- **Minimax** (Level 1): tìm kiếm toàn bộ cây trò chơi đến độ sâu giới hạn.  
- **Alpha-Beta** (Level 2): cắt nhánh khi `beta ≤ alpha`, kết hợp sắp xếp nước đi theo khoảng cách tâm để tăng hiệu quả cắt.  
- **Hàm đánh giá**: tính điểm theo độ dài chuỗi (1–4) và số đầu mở của từng chuỗi, cộng dồn cho AI và trừ cho người chơi.

---

## Level 3 – Benchmark

Chạy `benchmark.py` để so sánh Minimax và Alpha-Beta trên 5 trạng thái bàn cờ, với độ sâu 1, 2, 3.  
Kết quả ghi ra file `benchmark_results.csv`.
