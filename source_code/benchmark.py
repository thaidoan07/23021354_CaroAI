"""
benchmark.py - Level 3: Phân tích và so sánh Minimax vs Alpha-Beta
Chạy hai thuật toán trên các trạng thái bàn cờ chuẩn bị sẵn,
ghi kết quả ra bảng và file CSV.
"""

import csv
import os
from game import Board, HUMAN, AI, EMPTY
from ai import minimax_search, alphabeta_search


def make_board_from_moves(moves):
    """
    Tạo bàn cờ từ danh sách các nước đi.
    moves: list of (row, col, player)
    """
    b = Board()
    for r, c, p in moves:
        b.place(r, c, p)
    return b


# ─── 5 trạng thái kiểm thử theo yêu cầu đề bài ──────────────────────────────

def get_test_states():
    states = {}

    # 1. Trạng thái đầu ván (bàn cờ gần trống, vài nước đầu)
    b1 = Board()
    b1.place(4, 4, HUMAN)
    b1.place(4, 5, AI)
    states["1_early_game"] = b1

    # 2. Trạng thái giữa ván
    moves2 = [
        (4, 4, HUMAN), (4, 5, AI),
        (3, 6, HUMAN), (5, 5, AI),
        (2, 3, HUMAN), (3, 5, AI),
        (6, 4, HUMAN), (5, 3, AI),
        (1, 2, HUMAN), (6, 6, AI),
    ]
    states["2_mid_game"] = make_board_from_moves(moves2)

    # 3. Trạng thái máy có thể thắng ngay (AI có 3 liên tiếp, cần đánh nước 4)
    moves3 = [
        (4, 4, AI), (0, 0, HUMAN),
        (4, 5, AI), (0, 1, HUMAN),
        (4, 6, AI), (0, 2, HUMAN),
        # AI cần đánh (4,7) để thắng
    ]
    states["3_ai_can_win"] = make_board_from_moves(moves3)

    # 4. Người chơi sắp thắng, máy cần chặn
    moves4 = [
        (3, 3, HUMAN), (0, 0, AI),
        (3, 4, HUMAN), (0, 1, AI),
        (3, 5, HUMAN), (0, 2, AI),
        # HUMAN cần đánh (3,6) để thắng → AI phải chặn
    ]
    states["4_block_human"] = make_board_from_moves(moves4)

    # 5. Hai bên đều có cơ hội tấn công (quân rải rác, chưa ai thắng)
    moves5 = [
        (4, 4, HUMAN), (4, 6, AI),
        (3, 2, HUMAN), (5, 7, AI),
        (6, 3, HUMAN), (6, 7, AI),
        (2, 5, HUMAN), (1, 6, AI),
        (7, 4, HUMAN), (0, 1, AI),
    ]
    states["5_both_attack"] = make_board_from_moves(moves5)

    return states


def run_benchmark(depths=(1, 2, 3), output_csv="benchmark_results.csv"):
    states = get_test_states()
    results = []

    header = [
        "State", "Depth",
        "MM_Move", "MM_Score", "MM_States", "MM_Time(s)",
        "AB_Move", "AB_Score", "AB_States", "AB_Time(s)",
        "States_Saved", "States_Saved_%", "Same_Move"
    ]

    print("=" * 90)
    print(f"{'BENCHMARK: Minimax vs Alpha-Beta':^90}")
    print("=" * 90)

    for state_name, board in states.items():
        for depth in depths:
            b_mm = board.copy()
            b_ab = board.copy()

            mm = minimax_search(b_mm, depth)
            ab = alphabeta_search(b_ab, depth)

            saved = mm.states_explored - ab.states_explored
            saved_pct = (saved / mm.states_explored * 100) if mm.states_explored > 0 else 0
            same_move = (mm.move == ab.move)

            row = [
                state_name, depth,
                str(mm.move), mm.score, mm.states_explored, f"{mm.elapsed:.4f}",
                str(ab.move), ab.score, ab.states_explored, f"{ab.elapsed:.4f}",
                saved, f"{saved_pct:.1f}%", str(same_move)
            ]
            results.append(row)

            print(f"\nState: {state_name} | Depth: {depth}")
            print(f"  Minimax  : move={mm.move}, score={mm.score:>10}, "
                  f"states={mm.states_explored:>7}, time={mm.elapsed:.4f}s")
            print(f"  AlphaBeta: move={ab.move}, score={ab.score:>10}, "
                  f"states={ab.states_explored:>7}, time={ab.elapsed:.4f}s")
            print(f"  >> States saved: {saved} ({saved_pct:.1f}%) | Same move: {same_move}")

    print("\n" + "=" * 90)

    # Ghi CSV
    out_path = os.path.join(os.path.dirname(__file__), output_csv)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(results)
    print(f"\nResults saved to: {out_path}")
    return results


if __name__ == "__main__":
    run_benchmark(depths=[1, 2, 3])
