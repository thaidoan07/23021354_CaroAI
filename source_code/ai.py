"""
ai.py - Thuật toán AI: Minimax và Alpha-Beta Pruning
Level 1: Minimax với giới hạn độ sâu
Level 2: Alpha-Beta Pruning
"""

import time
from game import HUMAN, AI, WIN_LENGTH
from evaluate import evaluate

INF = float('inf')
WIN_SCORE  =  10_000_000
LOSE_SCORE = -10_000_000


class AIResult:
    def __init__(self, move, score, states_explored, elapsed):
        self.move = move                    # (row, col)
        self.score = score                  # điểm đánh giá
        self.states_explored = states_explored  # số trạng thái đã xét
        self.elapsed = elapsed              # thời gian chạy (giây)

    def __repr__(self):
        return (f"Move={self.move}, Score={self.score}, "
                f"States={self.states_explored}, Time={self.elapsed:.4f}s")


# ─── Minimax ─────────────────────────────────────────────────────────────────

def minimax(board, depth, is_maximizing, counter):
    """
    Minimax thuần, không cắt nhánh.
    counter: list 1 phần tử để đếm số trạng thái.
    Trả về (score, best_move).
    """
    counter[0] += 1

    winner = board.get_winner()
    if winner == AI:
        return WIN_SCORE + depth, None
    if winner == HUMAN:
        return LOSE_SCORE - depth, None
    if board.is_full():
        return 0, None
    if depth == 0:
        return evaluate(board), None

    moves = board.get_candidate_moves()
    # Same ordering as Alpha-Beta for consistent comparison
    center = board.size // 2
    moves.sort(key=lambda m: abs(m[0] - center) + abs(m[1] - center))
    best_move = moves[0] if moves else None

    if is_maximizing:
        best_score = -INF
        for r, c in moves:
            board.place(r, c, AI)
            score, _ = minimax(board, depth - 1, False, counter)
            board.undo(r, c)
            if score > best_score:
                best_score = score
                best_move = (r, c)
        return best_score, best_move
    else:
        best_score = INF
        for r, c in moves:
            board.place(r, c, HUMAN)
            score, _ = minimax(board, depth - 1, True, counter)
            board.undo(r, c)
            if score < best_score:
                best_score = score
                best_move = (r, c)
        return best_score, best_move


def minimax_search(board, depth):
    """
    Entry point cho Minimax.
    Trả về AIResult.
    """
    counter = [0]
    t0 = time.time()
    score, move = minimax(board, depth, True, counter)
    elapsed = time.time() - t0
    return AIResult(move, score, counter[0], elapsed)


# ─── Alpha-Beta Pruning ───────────────────────────────────────────────────────

def alphabeta(board, depth, alpha, beta, is_maximizing, counter):
    """
    Minimax với Alpha-Beta Pruning.
    alpha: giá trị tốt nhất hiện tại cho MAX.
    beta:  giá trị tốt nhất hiện tại cho MIN.
    Cắt nhánh khi beta <= alpha.
    """
    counter[0] += 1

    winner = board.get_winner()
    if winner == AI:
        return WIN_SCORE + depth, None
    if winner == HUMAN:
        return LOSE_SCORE - depth, None
    if board.is_full():
        return 0, None
    if depth == 0:
        return evaluate(board), None

    moves = board.get_candidate_moves()
    # Sắp xếp nước đi ưu tiên: gần trung tâm hơn (cải tiến nhỏ hợp lệ)
    center = board.size // 2
    moves.sort(key=lambda m: abs(m[0] - center) + abs(m[1] - center))

    best_move = moves[0] if moves else None

    if is_maximizing:
        best_score = -INF
        for r, c in moves:
            board.place(r, c, AI)
            score, _ = alphabeta(board, depth - 1, alpha, beta, False, counter)
            board.undo(r, c)
            if score > best_score:
                best_score = score
                best_move = (r, c)
            alpha = max(alpha, best_score)
            if beta <= alpha:   # Cắt nhánh Beta
                break
        return best_score, best_move
    else:
        best_score = INF
        for r, c in moves:
            board.place(r, c, HUMAN)
            score, _ = alphabeta(board, depth - 1, alpha, beta, True, counter)
            board.undo(r, c)
            if score < best_score:
                best_score = score
                best_move = (r, c)
            beta = min(beta, best_score)
            if beta <= alpha:   # Cắt nhánh Alpha
                break
        return best_score, best_move


def alphabeta_search(board, depth):
    """
    Entry point cho Alpha-Beta.
    Trả về AIResult.
    """
    counter = [0]
    t0 = time.time()
    score, move = alphabeta(board, depth, -INF, INF, True, counter)
    elapsed = time.time() - t0
    return AIResult(move, score, counter[0], elapsed)
