# Final Version

import random, pygame, sys, time

# --- Constants & Classic Colors ---
CELL_SIZE = 36
HUD_HEIGHT = 60
COLORS = {
    'hidden': (180, 180, 180), 'empty': (200, 200, 200),
    'grid': (140, 140, 140), 'F': (255, 50, 50), 'mine': (50, 50, 50),
    '1': (0, 0, 255), '2': (0, 128, 0), '3': (255, 0, 0),
    '4': (0, 0, 128), '5': (128, 0, 0), '6': (0, 128, 128),
    '7': (0, 0, 0), '8': (128, 128, 128)
}

def recalculate_hints(board, size):
    for r in range(size):
        for c in range(size):
            if board[r][c] == -1: continue
            count = 0
            for dr, dc in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < size and 0 <= nc < size and board[nr][nc] == -1:
                    count += 1
            board[r][c] = count

def generate_mines(size, mines, start_points):
    board = [[0 for _ in range(size)] for _ in range(size)]
    safe_zone = set()
    for sr, sc in start_points:
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                if 0 <= sr+dr < size and 0 <= sc+dc < size:
                    safe_zone.add((sr+dr, sc+dc))
    possible = [(r, c) for r in range(size) for c in range(size) if (r, c) not in safe_zone]
    while True:
        temp_board = [[0 for _ in range(size)] for _ in range(size)]
        for r, c in random.sample(possible, min(mines, len(possible))):
            temp_board[r][c] = -1
        has_blocker = False
        for sr, sc in safe_zone:
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                nr, nc = sr+dr, sc+dc
                if 0 <= nr < size and 0 <= nc < size and temp_board[nr][nc] == -1:
                    has_blocker = True; break
            if has_blocker: break
        if has_blocker or size > 10:
            board = temp_board; break
    recalculate_hints(board, size)
    return board

def reveal_cells(start_r, start_c, board, visible_board, size):
    if visible_board[start_r][start_c] not in [' ', '.']: return 0
    count, stack = 0, [(start_r, start_c)]
    while stack:
        r, c = stack.pop()
        if visible_board[r][c] not in [' ', '.']: continue
        val = board[r][c]
        visible_board[r][c] = str(val) if val > 0 else '.'
        count += 1
        if val == 0:
            for dr, dc in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
                nr, nc = r+dr, c+dc
                if 0 <= nr < size and 0 <= nc < size and visible_board[nr][nc] == ' ':
                    stack.append((nr, nc))
    return count

def chord(r, c, board, visible_board, size):
    if not visible_board[r][c].isdigit(): return 0, False
    target, flags, neighbors = int(visible_board[r][c]), 0, []
    for dr, dc in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
        nr, nc = r+dr, c+dc
        if 0 <= nr < size and 0 <= nc < size:
            if visible_board[nr][nc] == 'F': flags += 1
            elif visible_board[nr][nc] == ' ': neighbors.append((nr, nc))
    rev, hit = 0, False
    if flags == target:
        for nr, nc in neighbors:
            if board[nr][nc] == -1:
                hit = True; visible_board[nr][nc] = '*'
            else: rev += reveal_cells(nr, nc, board, visible_board, size)
    return rev, hit

def draw_hud(screen, font, mines_left, elapsed, size, s_left):
    pygame.draw.rect(screen, (50, 50, 50), (0, 0, size * CELL_SIZE, HUD_HEIGHT))
    m_txt = font.render(f"MINES: {max(0, mines_left)}", True, (255, 50, 50))
    t_txt = font.render(f"TIME: {int(elapsed)}", True, (255, 255, 0))
    screen.blit(m_txt, (15, 10))
    screen.blit(t_txt, (size * CELL_SIZE - t_txt.get_width() - 15, 10))
    if s_left > 0:
        s_txt = font.render(f"SAFETY: {s_left}", True, (100, 255, 100))
        screen.blit(s_txt, (size * CELL_SIZE // 2 - s_txt.get_width() // 2, 35))

def draw_board(screen, visible, font, size):
    for r in range(size):
        for c in range(size):
            cell, rect = visible[r][c], pygame.Rect(c*CELL_SIZE, r*CELL_SIZE+HUD_HEIGHT, CELL_SIZE, CELL_SIZE)
            color = COLORS['hidden'] if cell in [' ', 'F'] else COLORS['empty']
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, COLORS['grid'], rect, 1)
            if cell == 'F':
                pygame.draw.polygon(screen, COLORS['F'], [(rect.centerx-6, rect.centery-8), (rect.centerx+8, rect.centery-2), (rect.centerx-6, rect.centery+4)])
            elif cell in ['*', 'X']:
                pygame.draw.circle(screen, (0,0,0), rect.center, CELL_SIZE//3)
                if cell == '*': pygame.draw.rect(screen, (255,0,0), rect, 2)
            elif cell.isdigit() or cell == '.':
                val = cell if cell.isdigit() else ""
                num = font.render(val, True, COLORS.get(cell, (0,0,0)))
                screen.blit(num, num.get_rect(center=rect.center))

def failure_animation(screen, board, visible, font, size, mines, flags, start_time):
    for r in range(size):
        for c in range(size):
            if board[r][c] == -1 and visible[r][c] != '*':
                visible[r][c] = 'X'
                screen.fill((255, 255, 255)); draw_board(screen, visible, font, size)
                elapsed = time.time() - start_time if start_time else 0
                draw_hud(screen, font, mines - flags, elapsed, size, 0)
                pygame.display.flip(); pygame.time.delay(30)

def draw_end_screen(screen, won):
    overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160)); screen.blit(overlay, (0, 0))
    modal = pygame.Rect(0, 0, 260, 130); modal.center = (screen.get_width()//2, screen.get_height()//2)
    pygame.draw.rect(screen, (240, 240, 240), modal, border_radius=15)
    f_lg, f_sm = pygame.font.SysFont('Arial', 32, bold=True), pygame.font.SysFont('Arial', 18, bold=True)
    msg, color = ("VICTORY!", (0,150,0)) if won else ("GAME OVER", (200,0,0))
    t_s, s_s = f_lg.render(msg, True, color), f_sm.render("CLICK TO RESTART", True, (50,50,50))
    screen.blit(t_s, t_s.get_rect(center=(modal.centerx, modal.centery-20)))
    screen.blit(s_s, s_s.get_rect(center=(modal.centerx, modal.centery+25))); pygame.display.flip()

def get_difficulty_gui(screen):
    font = pygame.font.SysFont('Arial', 32, bold=True)
    easy_r, hard_r, rand_r = pygame.Rect(50, 80, 300, 60), pygame.Rect(50, 160, 300, 60), pygame.Rect(50, 240, 300, 60)
    pygame.display.set_mode((400, 350))
    while True:
        screen.fill((240, 240, 240))
        for r, c, txt in [(easy_r, (100,200,100), "EASY (9x9)"), (hard_r, (200,100,100), "HARD (16x16)"), (rand_r, (100,150,200), "RANDOM")]:
            pygame.draw.rect(screen, c, r, border_radius=8)
            surf = font.render(txt, True, (255,255,255)); screen.blit(surf, surf.get_rect(center=r.center))
        title = font.render("MINESWEEPER", True, (40,40,40)); screen.blit(title, (85, 20)); pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if easy_r.collidepoint(event.pos): return 9, 10, False
                if hard_r.collidepoint(event.pos): return 16, 40, False
                if rand_r.collidepoint(event.pos): return 12, 55, True

def run_game():
    pygame.init()
    screen = pygame.display.set_mode((400, 350))
    pygame.display.set_caption("Minesweeper Pro")
    while True:
        size, mines, is_rand = get_difficulty_gui(screen)
        screen = pygame.display.set_mode((size * CELL_SIZE, size * CELL_SIZE + HUD_HEIGHT))
        font = pygame.font.SysFont('Arial', 22, bold=True)
        visible, board, flags, revealed, safe_total = [[' ' for _ in range(size)] for _ in range(size)], None, 0, 0, (size*size)-mines
        start_time, game_over, won, playing = None, False, False, True
        safety_clicks = 5 if is_rand else 1
        initial_points = []; is_first_action = False
        reveals_since_last_bonus = 0 

        while playing:
            elapsed = time.time() - start_time if start_time and not (game_over or won) else (0 if not start_time else elapsed)
            screen.fill((255, 255, 255)); draw_board(screen, visible, font, size)
            draw_hud(screen, font, mines-flags, elapsed, size, safety_clicks)
            if game_over or won:
                draw_end_screen(screen, won)
                event = pygame.event.wait()
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN: playing = False
            else:
                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mx, my = event.pos
                        if my < HUD_HEIGHT: continue
                        c, r = mx // CELL_SIZE, (my - HUD_HEIGHT) // CELL_SIZE
                        if not (0 <= r < size and 0 <= c < size): continue
                        changed = False
                        
                        if event.button == 3:
                            if visible[r][c] == ' ': visible[r][c] = 'F'; flags += 1
                            elif visible[r][c] == 'F': visible[r][c] = ' '; flags -= 1
                        
                        elif event.button == 1 and visible[r][c] != 'F':
                            if safety_clicks > 0 and visible[r][c] == ' ':
                                if board is None:
                                    if (r, c) not in initial_points:
                                        initial_points.append((r, c)); visible[r][c] = '.'; safety_clicks -= 1
                                        if safety_clicks == 0:
                                            for pr, pc in initial_points: visible[pr][pc] = ' '
                                            board = generate_mines(size, mines, initial_points)
                                            start_time = time.time(); is_first_action = True
                                            for pr, pc in initial_points: revealed += reveal_cells(pr, pc, board, visible, size)
                                else:
                                    if board[r][c] == -1:
                                        board[r][c] = 0
                                        hidden_spots = [(nr, nc) for nr in range(size) for nc in range(size) if visible[nr][nc] == ' ' and (nr, nc) != (r, c)]
                                        if hidden_spots:
                                            new_r, new_c = random.choice(hidden_spots); board[new_r][new_c] = -1
                                        recalculate_hints(board, size)
                                    safety_clicks -= 1
                                    rev = reveal_cells(r, c, board, visible, size)
                                    revealed += rev; changed = True
                                    if is_rand: reveals_since_last_bonus += rev
                            
                            elif board is not None:
                                is_first_action = False
                                if visible[r][c].isdigit():
                                    rev, hit = chord(r, c, board, visible, size); revealed += rev
                                    if rev > 0: 
                                        changed = True
                                        if is_rand: reveals_since_last_bonus += rev
                                    if hit: game_over = True
                                elif visible[r][c] == ' ':
                                    if board[r][c] == -1: visible[r][c] = '*'; game_over = True
                                    else: 
                                        rev = reveal_cells(r, c, board, visible, size)
                                        revealed += rev; changed = True
                                        if is_rand: reveals_since_last_bonus += rev

                        if is_rand and reveals_since_last_bonus >= 5:
                            safety_clicks += reveals_since_last_bonus // 5
                            reveals_since_last_bonus %= 5

                        if is_rand and changed and not game_over:
                            locked = [(nr, nc) for nr in range(size) for nc in range(size) if visible[nr][nc] == 'F' and board[nr][nc] == -1]
                            hidden = [(nr, nc) for nr in range(size) for nc in range(size) if visible[nr][nc] in [' ', 'F'] and (nr, nc) not in locked]
                            for nr in range(size):
                                for nc in range(size):
                                    if (nr, nc) not in locked: board[nr][nc] = 0
                            if hidden:
                                new_spots = random.sample(hidden, min(mines - len(locked), len(hidden)))
                                for mr, mc in new_spots: board[mr][mc] = -1
                            recalculate_hints(board, size); cur_rev = 0
                            for nr in range(size):
                                for nc in range(size):
                                    if visible[nr][nc] not in [' ', 'F', '*', 'X']:
                                        cur_rev += 1; visible[nr][nc] = str(board[nr][nc]) if board[nr][nc] > 0 else '.'
                            revealed = cur_rev
                        if game_over: failure_animation(screen, board, visible, font, size, mines, flags, start_time)
                if board is not None and not is_first_action and not game_over and revealed >= safe_total: won = True

if __name__ == "__main__":
    run_game()
