# Test Suite

import unittest
import random
from Minesweeper_Game import generate_mines, reveal_cells, recalculate_hints

class TestMinesweeperV3(unittest.TestCase):

    def test_multi_point_safe_zone(self):
        """Verify that all 5 initial safety clicks and their neighbors are mine-free."""
        size, mines = 12, 55
        # Simulating 5 initial clicks for Random Mode
        start_points = [(0, 0), (2, 2), (5, 5), (10, 10), (0, 11)]
        board = generate_mines(size, mines, start_points)
        
        for sr, sc in start_points:
            for dr in range(-1, 2):
                for dc in range(-1, 2):
                    nr, nc = sr + dr, sc + dc
                    if 0 <= nr < size and 0 <= nc < size:
                        self.assertNotEqual(board[nr][nc], -1, 
                            f"Mine found in safety zone at ({nr}, {nc})")

    def test_mine_count_random_mode(self):
        """Verify mine count remains exact despite high density in Random Mode."""
        size, mines = 12, 55
        start_points = [(5, 5)]
        board = generate_mines(size, mines, start_points)
        actual_mines = sum(row.count(-1) for row in board)
        self.assertEqual(actual_mines, mines)

    def test_dynamic_hint_recalculation(self):
        """Verify hints update correctly when mines are moved (essential for Random Mode)."""
        size = 3
        # Initialize a blank 3x3 board
        board = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        
        # Place a single mine at (0,0) and recalculate
        board[0][0] = -1
        recalculate_hints(board, size)
        # Neighbors (0,1), (1,0), (1,1) should show 1
        self.assertEqual(board[0][1], 1)
        self.assertEqual(board[1][0], 1)
        self.assertEqual(board[1][1], 1)

        # Move the mine to (2,2), clear old mine, and recalculate
        board[0][0] = 0
        board[2][2] = -1
        recalculate_hints(board, size)
        self.assertEqual(board[0][1], 0) # Old hint should be cleared
        self.assertEqual(board[1][1], 1) # (1,1) is now a neighbor of (2,2)
        self.assertEqual(board[2][1], 1) # New neighbor
        self.assertEqual(board[1][2], 1) # New neighbor

    def test_win_prevention_logic(self):
        """Verify generator places a blocker mine to prevent 1-click victories."""
        size, mines = 9, 10
        start_points = [(4, 4)]
        board = generate_mines(size, mines, start_points)
        
        # A blocker mine must be directly adjacent (orthogonally) to the safe zone
        has_blocker = False
        # The safe zone for (4,4) is the 3x3 area [3-5, 3-5]
        # We check cells immediately outside this 3x3 perimeter
        for r in range(size):
            for c in range(size):
                if board[r][c] == -1:
                    # Check if this mine is adjacent to any cell in the 3x3 safe zone
                    for sr in range(3, 6):
                        for sc in range(3, 6):
                            if abs(r - sr) <= 1 and abs(c - sc) <= 1:
                                # This mine borders the safe zone, blocking the flood fill
                                has_blocker = True
                                break
                    if has_blocker: break
            if has_blocker: break
        self.assertTrue(has_blocker, "No blocker mine found to prevent 1-click win")

    def test_reveal_logic_dot_notation(self):
        """Verify empty cells are marked with '.' for visibility."""
        size = 3
        board = [[0, 1, -1], [0, 1, 1], [0, 0, 0]]
        visible = [[' ' for _ in range(3)] for _ in range(3)]
        reveal_cells(0, 0, board, visible, size)
        # The (0,0) cell is empty (0), so it should be '.'
        self.assertEqual(visible[0][0], '.')

if __name__ == "__main__":
    unittest.main()
