"""
evaluate.py - Hàm đánh giá trạng thái bàn cờ Caro
Đánh giá theo quan điểm của AI (O).
Điểm dương = lợi thế cho AI, âm = lợi thế cho người chơi.
"""

from game import EMPTY, HUMAN, AI, DIRECTIONS, WIN_LENGTH


# Bảng điểm cho từng loại chuỗi
SCORE_TABLE = {
    # (length, open_ends): score
    (4, 2): 1_000_000,   # 4 mở 2 đầu = thắng
    (4, 1): 1_000_000,   # 4 đóng 1 đầu = thắng
    (4, 0): 1_000_000,   # 4 = thắng
    (3, 2): 10_000,      # 3 mở 2 đầu = nguy hiểm cao
    (3, 1): 1_000,       # 3 mở 1 đầu
    (3, 0): 100,
    (2, 2): 100,
    (2, 1): 10,
    (2, 0): 1,
    (1, 2): 5,
    (1, 1): 1,
    (1, 0): 0,
}


def evaluate_line_segment(board, r, c, dr, dc, player):
    """
    Từ ô (r, c) theo hướng (dr, dc), đếm chuỗi liên tiếp của player
    và kiểm tra 2 đầu có trống không.
    Trả về score cho đoạn này.
    """
    size = board.size
    length = 1
    # Đếm về phía trước
    nr, nc = r + dr, c + dc
    while 0 <= nr < size and 0 <= nc < size and board.grid[nr][nc] == player:
        length += 1
        nr += dr
        nc += dc
    # Kiểm tra đầu trước
    open_front = 1 if (0 <= nr < size and 0 <= nc < size and board.grid[nr][nc] == EMPTY) else 0

    # Đếm về phía sau
    nr, nc = r - dr, c - dc
    while 0 <= nr < size and 0 <= nc < size and board.grid[nr][nc] == player:
        length += 1
        nr -= dr
        nc -= dc
    # Kiểm tra đầu sau
    open_back = 1 if (0 <= nr < size and 0 <= nc < size and board.grid[nr][nc] == EMPTY) else 0

    open_ends = open_front + open_back
    key = (min(length, 4), open_ends)
    return SCORE_TABLE.get(key, 0)


def evaluate(board):
    """
    Đánh giá toàn bộ bàn cờ.
    Trả về điểm: dương = lợi AI, âm = lợi người.
    """
    # Tránh đánh giá lại vị trí đã tính (dùng visited set theo hướng)
    ai_score = 0
    human_score = 0
    visited = set()

    for r in range(board.size):
        for c in range(board.size):
            player = board.grid[r][c]
            if player == EMPTY:
                continue
            for dr, dc in DIRECTIONS:
                # Chỉ tính từ điểm đầu của chuỗi (không tính ngược)
                prev_r, prev_c = r - dr, c - dc
                if (0 <= prev_r < board.size and 0 <= prev_c < board.size
                        and board.grid[prev_r][prev_c] == player):
                    continue  # Không phải điểm đầu chuỗi

                key = (r, c, dr, dc, player)
                if key in visited:
                    continue
                visited.add(key)

                score = evaluate_line_segment(board, r, c, dr, dc, player)
                if player == AI:
                    ai_score += score
                else:
                    human_score += score

    return ai_score - human_score
