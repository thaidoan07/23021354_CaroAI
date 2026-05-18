"""
main.py - Pygame UI for Caro AI
Supports: Human vs AI (Minimax or Alpha-Beta)
Hotkeys:
  R       - New game
  M       - Toggle AI mode (Minimax / Alpha-Beta)
  +/-     - Increase / decrease search depth
  B       - Run Benchmark (Level 3)
  ESC     - Quit
"""

import sys
import pygame
import threading
from game import Board, HUMAN, AI, EMPTY
from ai import minimax_search, alphabeta_search
from benchmark import run_benchmark

# ─── Màu sắc & kích thước ────────────────────────────────────────────────────
BG_COLOR        = (245, 230, 200)   # Nền màu vàng gỗ
GRID_COLOR      = (160, 120, 70)    # Đường kẻ nâu
BOARD_COLOR     = (220, 185, 140)   # Nền bàn cờ
X_COLOR         = (30,  80,  200)   # Người chơi (X) - xanh dương
O_COLOR         = (200, 40,  40)    # Máy (O) - đỏ
LAST_MOVE_COLOR = (255, 220, 0)     # Nước đi vừa đánh
WIN_LINE_COLOR  = (50, 200, 50)     # Đường thắng
TEXT_COLOR      = (50,  35,  20)
PANEL_COLOR     = (50,  35,  20)
PANEL_TEXT      = (230, 210, 180)
HINT_COLOR      = (100, 160, 255, 80)
BTN_COLOR       = (80,  55,  30)
BTN_HOVER       = (120, 90, 55)
BTN_TEXT        = (240, 220, 190)

CELL_SIZE  = 54
MARGIN     = 20
PANEL_W    = 280
BOARD_SIZE = 9

BOARD_PX   = CELL_SIZE * BOARD_SIZE
SCREEN_W   = MARGIN * 2 + BOARD_PX + PANEL_W + 20
SCREEN_H   = MARGIN * 2 + BOARD_PX + 20

FPS = 60


def cell_rect(r, c):
    x = MARGIN + c * CELL_SIZE
    y = MARGIN + r * CELL_SIZE
    return pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)


def cell_center(r, c):
    x = MARGIN + c * CELL_SIZE + CELL_SIZE // 2
    y = MARGIN + r * CELL_SIZE + CELL_SIZE // 2
    return x, y


def pixel_to_grid(px, py):
    c = (px - MARGIN) // CELL_SIZE
    r = (py - MARGIN) // CELL_SIZE
    return r, c


def find_win_sequence(board):
    """Tìm 4 ô thắng cuộc để vẽ đường highlight."""
    from game import DIRECTIONS, WIN_LENGTH
    for r in range(board.size):
        for c in range(board.size):
            p = board.grid[r][c]
            if p == EMPTY:
                continue
            for dr, dc in DIRECTIONS:
                seq = [(r, c)]
                for k in range(1, WIN_LENGTH):
                    nr, nc = r + dr * k, c + dc * k
                    if not (0 <= nr < board.size and 0 <= nc < board.size):
                        break
                    if board.grid[nr][nc] != p:
                        break
                    seq.append((nr, nc))
                if len(seq) >= WIN_LENGTH:
                    return seq, p
    return None, None


class Button:
    def __init__(self, rect, text, font, action=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.action = action
        self.hovered = False

    def draw(self, surf):
        color = BTN_HOVER if self.hovered else BTN_COLOR
        pygame.draw.rect(surf, color, self.rect, border_radius=8)
        pygame.draw.rect(surf, PANEL_TEXT, self.rect, 1, border_radius=8)
        label = self.font.render(self.text, True, BTN_TEXT)
        surf.blit(label, label.get_rect(center=self.rect.center))

    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)

    def check_click(self, pos):
        if self.rect.collidepoint(pos) and self.action:
            self.action()


class CaroGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Caro AI  –  Minimax & Alpha-Beta")

        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        self.clock  = pygame.time.Clock()

        # Fonts
        self.font_title  = pygame.font.SysFont("Arial", 22, bold=True)
        self.font_body   = pygame.font.SysFont("Arial", 15)
        self.font_small  = pygame.font.SysFont("Arial", 13)
        self.font_piece  = pygame.font.SysFont("Arial", 28, bold=True)
        self.font_btn    = pygame.font.SysFont("Arial", 14, bold=True)

        self.board     = Board(BOARD_SIZE)
        self.use_ab    = True          # True = Alpha-Beta, False = Minimax
        self.depth     = 3
        self.ai_turn   = False         # True = waiting for AI
        self.game_over = False
        self.winner    = None
        self.win_seq   = []
        self.status_msg = "Your turn! (X)"
        self.last_result = None        # AIResult from last AI move

        # AI runs in background thread to keep UI responsive
        self.ai_thinking = False
        self.ai_thread   = None

        # Move log
        self.move_log = []   # list of str

        bx = MARGIN + BOARD_PX + 15
        by = MARGIN
        bw = PANEL_W - 15

        self.buttons = [
            Button((bx, by,      bw, 34), "New Game  [R]",        self.font_btn, self.reset),
            Button((bx, by + 42, bw, 34), "Toggle AI  [M]",       self.font_btn, self.toggle_ai),
            Button((bx, by + 84, bw, 34), "Benchmark  [B]",       self.font_btn, self.run_bench),
            Button((bx, by + 126, bw//2 - 4, 34), "Depth +",     self.font_btn, self.depth_up),
            Button((bx + bw//2 + 4, by + 126, bw//2 - 4, 34), "Depth -", self.font_btn, self.depth_down),
        ]

    def reset(self):
        self.board      = Board(BOARD_SIZE)
        self.ai_turn    = False
        self.game_over  = False
        self.winner     = None
        self.win_seq    = []
        self.last_result = None
        self.move_log   = []
        self.status_msg = "Your turn! (X)"

    def toggle_ai(self):
        self.use_ab = not self.use_ab
        mode = "Alpha-Beta" if self.use_ab else "Minimax"
        self.status_msg = f"AI mode: {mode}"

    def depth_up(self):
        if self.depth < 6:
            self.depth += 1
            self.status_msg = f"Search depth: {self.depth}"

    def depth_down(self):
        if self.depth > 1:
            self.depth -= 1
            self.status_msg = f"Search depth: {self.depth}"

    def run_bench(self):
        self.status_msg = "Running Benchmark... (see console)"
        def bench_thread():
            run_benchmark(depths=[1, 2, 3])
        t = threading.Thread(target=bench_thread, daemon=True)
        t.start()

    def human_move(self, r, c):
        if self.game_over or self.ai_thinking:
            return
        if not self.board.is_valid(r, c) or not self.board.is_empty(r, c):
            return
        self.board.place(r, c, HUMAN)
        self.move_log.append(f"Human: ({r},{c})")
        self._check_end()
        if not self.game_over:
            self.ai_turn = True
            self.status_msg = "AI is thinking..."
            self._start_ai_thread()

    def _start_ai_thread(self):
        self.ai_thinking = True
        def ai_work():
            b = self.board.copy()
            if self.use_ab:
                result = alphabeta_search(b, self.depth)
            else:
                result = minimax_search(b, self.depth)
            self.last_result = result
            self._ai_done(result.move)
        self.ai_thread = threading.Thread(target=ai_work, daemon=True)
        self.ai_thread.start()

    def _ai_done(self, move):
        self.ai_thinking = False
        self.ai_turn = False
        if move and not self.game_over:
            r, c = move
            self.board.place(r, c, AI)
            mode = "AB" if self.use_ab else "MM"
            self.move_log.append(
                f"AI({mode}): ({r},{c})  "
                f"score={self.last_result.score}  "
                f"states={self.last_result.states_explored}  "
                f"t={self.last_result.elapsed:.3f}s"
            )
            self._check_end()
            if not self.game_over:
                self.status_msg = "Your turn (X)"

    def _check_end(self):
        winner = self.board.get_winner()
        if winner:
            self.winner = winner
            self.game_over = True
            self.win_seq, _ = find_win_sequence(self.board)
            if winner == HUMAN:
                self.status_msg = "You win!"
            else:
                self.status_msg = "AI wins!"
        elif self.board.is_full():
            self.game_over = True
            self.status_msg = "Draw!"

    # ─── Vẽ ──────────────────────────────────────────────────────────────────

    def draw_board(self):
        # Draw all cells as individual squares
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                rect = cell_rect(r, c)
                pygame.draw.rect(self.screen, BOARD_COLOR, rect)
                pygame.draw.rect(self.screen, GRID_COLOR, rect, 1)

    def draw_pieces(self):
        win_cells = set(map(tuple, self.win_seq)) if self.win_seq else set()

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                p = self.board.grid[r][c]
                if p == EMPTY:
                    continue

                is_last = (self.board.last_move == (r, c))
                is_win  = (r, c) in win_cells
                sym     = "X" if p == HUMAN else "O"

                # Pick color: green for winning cells, yellow dot for last move, normal otherwise
                if is_win:
                    color = WIN_LINE_COLOR
                elif is_last:
                    color = LAST_MOVE_COLOR
                else:
                    color = X_COLOR if p == HUMAN else O_COLOR

                cx, cy = cell_center(r, c)
                label = self.font_piece.render(sym, True, color)
                self.screen.blit(label, label.get_rect(center=(cx, cy)))

    def draw_panel(self):
        bx = MARGIN + BOARD_PX + 15
        by = MARGIN

        # Title
        title = self.font_title.render("CARO AI", True, PANEL_COLOR)
        self.screen.blit(title, (bx, by - 30))

        # Buttons
        for btn in self.buttons:
            btn.draw(self.screen)

        # Info
        iy = by + 175
        mode_str = "Alpha-Beta" if self.use_ab else "Minimax"
        infos = [
            f"AI Mode  : {mode_str}",
            f"Depth    : {self.depth}",
            f"Turn     : {'AI' if self.ai_turn else 'Human'}",
        ]
        for info in infos:
            surf = self.font_body.render(info, True, TEXT_COLOR)
            self.screen.blit(surf, (bx, iy))
            iy += 22

        # Status
        iy += 8
        pygame.draw.line(self.screen, GRID_COLOR, (bx, iy), (bx + PANEL_W - 20, iy), 1)
        iy += 8
        status_surf = self.font_body.render(self.status_msg, True, TEXT_COLOR)
        self.screen.blit(status_surf, (bx, iy))
        iy += 28

        # Last AI result
        if self.last_result and self.last_result.move:
            pygame.draw.line(self.screen, GRID_COLOR, (bx, iy), (bx + PANEL_W - 20, iy), 1)
            iy += 8
            ai_head = self.font_small.render("-- Last AI Move --", True, GRID_COLOR)
            self.screen.blit(ai_head, (bx, iy)); iy += 18
            details = [
                f"Move   : {self.last_result.move}",
                f"Score  : {self.last_result.score}",
                f"States : {self.last_result.states_explored}",
                f"Time   : {self.last_result.elapsed:.4f}s",
            ]
            for d in details:
                surf = self.font_small.render(d, True, TEXT_COLOR)
                self.screen.blit(surf, (bx, iy))
                iy += 17

        # Move log
        iy += 8
        pygame.draw.line(self.screen, GRID_COLOR, (bx, iy), (bx + PANEL_W - 20, iy), 1)
        iy += 8
        log_head = self.font_small.render("-- Move History --", True, GRID_COLOR)
        self.screen.blit(log_head, (bx, iy)); iy += 18
        for entry in self.move_log[-8:]:
            surf = self.font_small.render(entry[:38], True, TEXT_COLOR)
            self.screen.blit(surf, (bx, iy))
            iy += 15
            if iy > SCREEN_H - 20:
                break

    def draw_thinking_overlay(self):
        if self.ai_thinking:
            s = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            s.fill((0, 0, 0, 30))
            self.screen.blit(s, (0, 0))
            msg = self.font_title.render("AI is thinking...", True, (30, 30, 30))
            bw, bh = msg.get_size()
            board_cx = MARGIN + BOARD_PX // 2
            board_cy = MARGIN + BOARD_PX // 2
            pygame.draw.rect(self.screen, (255, 250, 230),
                             (board_cx - bw//2 - 10, board_cy - bh//2 - 8, bw + 20, bh + 16),
                             border_radius=10)
            self.screen.blit(msg, (board_cx - bw//2, board_cy - bh//2))

    def run(self):
        while True:
            self.clock.tick(FPS)
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()
                    elif event.key == pygame.K_r:
                        self.reset()
                    elif event.key == pygame.K_m:
                        self.toggle_ai()
                    elif event.key == pygame.K_b:
                        self.run_bench()
                    elif event.key in (pygame.K_PLUS, pygame.K_EQUALS):
                        self.depth_up()
                    elif event.key == pygame.K_MINUS:
                        self.depth_down()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for btn in self.buttons:
                        btn.check_click(mouse_pos)
                    # Click on the board area
                    mx, my = mouse_pos
                    if (MARGIN <= mx < MARGIN + BOARD_PX and
                            MARGIN <= my < MARGIN + BOARD_PX and
                            not self.game_over and not self.ai_thinking):
                        r, c = pixel_to_grid(mx, my)
                        if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                            self.human_move(r, c)

            for btn in self.buttons:
                btn.check_hover(mouse_pos)

            # ─── Render ───────────────────────────────────────────────────
            self.screen.fill(BG_COLOR)
            self.draw_board()
            self.draw_pieces()
            self.draw_panel()
            self.draw_thinking_overlay()

            pygame.display.flip()


if __name__ == "__main__":
    game = CaroGame()
    game.run()
