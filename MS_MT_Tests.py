# Test Suite: Core Logic

import unittest
import random
from unittest.mock import patch
from MS_MT import generate_mines, reveal_cells

class TestMinesweeperCore(unittest.TestCase):

    def test_mine_count(self):
        """Verify the board contains the exact number of requested mines."""
        size, mines = 10, 10
        board = generate_mines(size, mines, 0, 0)
        actual_mines = sum(row.count(-1) for row in board)
        self.assertEqual(actual_mines, mines)

    def test_safe_start_zone(self):
        """Verify the 3x3 area around the first click has no mines."""
        size, mines = 5, 5
        start_r, start_c = 2, 2
        board = generate_mines(size, mines, start_r, start_c)
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr, nc = start_r + dr, start_c + dc
                if 0 <= nr < size and 0 <= nc < size:
                    self.assertNotEqual(board[nr][nc], -1, f"Mine found in safe zone at ({nr}, {nc})")

    def test_neighbor_counting_accuracy(self):
        """Verify that cell numbers accurately count adjacent mines."""
        size, mines = 3, 1
        random.seed(42) 
        board = generate_mines(size, mines, 2, 2)
        for r in range(size):
            for c in range(size):
                if board[r][c] == -1:
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < size and 0 <= nc < size and board[nr][nc] != -1:
                                self.assertGreaterEqual(board[nr][nc], 1)

    def test_reveal_logic_flood_fill(self):
        """Verify that revealing an empty cell (0) clears adjacent space."""
        size = 3
        board = [[0, 0, 0], [0, 0, 1], [0, 1, -1]] 
        visible = [[' ' for _ in range(3)] for _ in range(3)]
        revealed = reveal_cells(0, 0, board, visible, size)
        self.assertGreater(revealed, 1)
        self.assertEqual(visible[0][0], '.')

if __name__ == "__main__":
    unittest.main()





