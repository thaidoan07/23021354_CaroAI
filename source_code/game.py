"""
game.py - Core game logic for Caro AI
Board size: 9x9 minimum
Win condition: 4 consecutive pieces (row, col, diagonal)
"""

EMPTY = 0
HUMAN = 1   # X
AI    = 2   # O

BOARD_SIZE = 9
WIN_LENGTH = 4

DIRECTIONS = [(0, 1), (1, 0), (1, 1), (1, -1)]


class Board:
    def __init__(self, size=BOARD_SIZE):
        self.size = size
        self.grid = [[EMPTY] * size for _ in range(size)]
        self.last_move = None
        self.move_count = 0

    def copy(self):
        b = Board(self.size)
        b.grid = [row[:] for row in self.grid]
        b.last_move = self.last_move
        b.move_count = self.move_count
        return b

    def is_valid(self, r, c):
        return 0 <= r < self.size and 0 <= c < self.size

    def is_empty(self, r, c):
        return self.grid[r][c] == EMPTY

    def place(self, r, c, player):
        self.grid[r][c] = player
        self.last_move = (r, c)
        self.move_count += 1

    def undo(self, r, c):
        self.grid[r][c] = EMPTY
        self.move_count -= 1

    def is_full(self):
        return self.move_count >= self.size * self.size

    def count_consecutive(self, r, c, dr, dc, player):
        """Count consecutive pieces in one direction from (r,c)."""
        count = 0
        nr, nc = r + dr, c + dc
        while self.is_valid(nr, nc) and self.grid[nr][nc] == player:
            count += 1
            nr += dr
            nc += dc
        return count

    def check_win(self, r, c, player):
        """Check if placing at (r,c) wins for player."""
        for dr, dc in DIRECTIONS:
            fwd = self.count_consecutive(r, c, dr, dc, player)
            bwd = self.count_consecutive(r, c, -dr, -dc, player)
            if fwd + bwd + 1 >= WIN_LENGTH:
                return True
        return False

    def get_winner(self):
        """Return winner (HUMAN/AI) or None."""
        for r in range(self.size):
            for c in range(self.size):
                p = self.grid[r][c]
                if p != EMPTY and self.check_win(r, c, p):
                    return p
        return None

    def is_terminal(self):
        return self.get_winner() is not None or self.is_full()

    def get_candidate_moves(self, radius=2):
        """
        Only generate moves near existing pieces.
        If board is empty, return center.
        """
        if self.move_count == 0:
            center = self.size // 2
            return [(center, center)]

        candidates = set()
        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c] != EMPTY:
                    for dr in range(-radius, radius + 1):
                        for dc in range(-radius, radius + 1):
                            nr, nc = r + dr, c + dc
                            if self.is_valid(nr, nc) and self.grid[nr][nc] == EMPTY:
                                candidates.add((nr, nc))
        return list(candidates)

    def display(self):
        symbols = {EMPTY: '.', HUMAN: 'X', AI: 'O'}
        header = '   ' + ' '.join(f'{c:2}' for c in range(self.size))
        print(header)
        for r in range(self.size):
            row = ' '.join(symbols[self.grid[r][c]] for c in range(self.size))
            print(f'{r:2} {row}')
        print()
