
import random
import pygame
import sys

# Main Logic: Mine Generation
def generate_mines(size, mines, start_r, start_c):
    board = [[0 for _ in range(size)] for _ in range(size)]
    # Keep the first click and its 8 neighbors safe (3x3 area)
    safe_zone = []
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            nr, nc = start_r + dr, start_c + dc
            if 0 <= nr < size and 0 <= nc < size:
                safe_zone.append(nr * size + nc)
                
    possible_positions = [i for i in range(size * size) if i not in safe_zone]
    mine_positions = random.sample(possible_positions, mines)
    
    for pos in mine_positions:
        r, c = divmod(pos, size)
        board[r][c] = -1
        
    for r in range(size):
        for c in range(size):
            if board[r][c] == -1: continue
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < size and 0 <= nc < size and board[nr][nc] == -1:
                        board[r][c] += 1
    return board

# Flood Fill Function
def reveal_cells(start_r, start_c, board, visible_board, size):
    if visible_board[start_r][start_c] not in [' ', 'F']: return 0
    revealed_count, stack = 0, [(start_r, start_c)]
    while stack:
        r, c = stack.pop()
        if visible_board[r][c] not in [' ', 'F']: continue
        val = board[r][c]
        visible_board[r][c] = str(val) if val > 0 else '.'
        revealed_count += 1
        if val == 0:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < size and 0 <= nc < size and visible_board[nr][nc] == ' ':
                        stack.append((nr, nc))
    return revealed_count

# PYGAME GUI
CELL_SIZE = 40
COLORS = {
    'hidden': (180, 180, 180), 'empty': (220, 220, 220),
    'F': (255, 50, 50), 'mine': (50, 50, 50),
    '1': (0, 0, 255), '2': (0, 128, 0), '3': (255, 0, 0), '*': (0, 0, 0)
}

def draw_board(screen, visible_board, font, size):
    screen.fill((255, 255, 255))
    for r in range(size):
        for c in range(size):
            cell = visible_board[r][c]
            rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE - 2, CELL_SIZE - 2)
            color = COLORS['hidden'] if cell in [' ', 'F'] else COLORS['empty']
            pygame.draw.rect(screen, color, rect)
            if cell == 'F':
                pygame.draw.circle(screen, COLORS['F'], rect.center, CELL_SIZE // 4)
            elif cell == '*':
                pygame.draw.circle(screen, COLORS['mine'], rect.center, CELL_SIZE // 3)
            elif cell.isdigit():
                num_text = font.render(cell, True, COLORS.get(cell, (0, 0, 0)))
                screen.blit(num_text, num_text.get_rect(center=rect.center))

# Screen modeling, Vict/Def/Main
def draw_end_screen(screen, won):
    # Darken board
    overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0,0))
    # Modal
    modal_rect = pygame.Rect(0, 0, 250, 120)
    modal_rect.center = (screen.get_width()//2, screen.get_height()//2)
    pygame.draw.rect(screen, (240, 240, 240), modal_rect, border_radius=12)
    # Text
    f_lg = pygame.font.SysFont('Arial', 32, bold=True)
    f_sm = pygame.font.SysFont('Arial', 18, bold=True)
    msg, color = ("VICTORY!", (0, 150, 0)) if won else ("GAME OVER", (200, 0, 0))
    t_surf = f_lg.render(msg, True, color)
    s_surf = f_sm.render("CLICK TO RESTART", True, (50, 50, 50))
    screen.blit(t_surf, t_surf.get_rect(center=(modal_rect.centerx, modal_rect.centery - 20)))
    screen.blit(s_surf, s_surf.get_rect(center=(modal_rect.centerx, modal_rect.centery + 25)))
    pygame.display.flip()

# Difficulty Selection GUI
def get_difficulty_gui(screen):
    font = pygame.font.SysFont('Arial', 32, bold=True)
    easy_rect = pygame.Rect(50, 100, 300, 60)
    hard_rect = pygame.Rect(50, 200, 300, 60)
    pygame.display.set_mode((400, 350))
    while True:
        screen.fill((240, 240, 240))
        pygame.draw.rect(screen, (100, 200, 100), easy_rect, border_radius=8)
        pygame.draw.rect(screen, (200, 100, 100), hard_rect, border_radius=8)
        screen.blit(font.render("MINESWEEPER", True, (40, 40, 40)), (85, 30))
        screen.blit(font.render("EASY (9x9)", True, (255, 255, 255)), (115, 112))
        screen.blit(font.render("HARD (16x16)", True, (255, 255, 255)), (105, 212))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if easy_rect.collidepoint(event.pos): return 9, 10
                if hard_rect.collidepoint(event.pos): return 16, 40
# Main Game Loop
def run_game():
    pygame.init()
    screen = pygame.display.set_mode((400, 350))
    pygame.display.set_caption("Minesweeper")
    while True:
        size, mines = get_difficulty_gui(screen)
        screen = pygame.display.set_mode((size * CELL_SIZE, size * CELL_SIZE))
        font = pygame.font.SysFont('Arial', 24, bold=True)
        visible_board = [[' ' for _ in range(size)] for _ in range(size)]
        board, revealed_count, total_safe = None, 0, (size * size) - mines
        game_over = won = False
        playing = True
        while playing:
            draw_board(screen, visible_board, font, size)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if not game_over and event.type == pygame.MOUSEBUTTONDOWN:
                    c, r = event.pos[0] // CELL_SIZE, event.pos[1] // CELL_SIZE
                    if event.button == 3: # Right Click
                        if visible_board[r][c] == ' ': visible_board[r][c] = 'F'
                        elif visible_board[r][c] == 'F': visible_board[r][c] = ' '
                    elif event.button == 1: # Left Click
                        if visible_board[r][c] == 'F': continue
                        if board is None: board = generate_mines(size, mines, r, c)
                        if board[r][c] == -1:
                            for br in range(size):
                                for bc in range(size):
                                    if board[br][bc] == -1: visible_board[br][bc] = '*'
                            game_over = True
                        else:
                            revealed_count += reveal_cells(r, c, board, visible_board, size)
            if not game_over and revealed_count == total_safe:
                game_over = won = True
            if game_over:
                draw_board(screen, visible_board, font, size)
                draw_end_screen(screen, won)
                waiting = True
                while waiting:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                        if event.type == pygame.MOUSEBUTTONDOWN: playing = waiting = False

if __name__ == "__main__":
    run_game()


