#!/usr/bin/env python3
# =============================================================================
# Block Blast — Ghost Block Edition
# Place pieces on an 8x8 grid. Fill a row or column to clear it and score.
# You get 3 pieces at a time. Game over when none of them fit on the board.
#
# NEW: Every piece has at least 1 GHOST BLOCK (green tint).
# Ghost blocks fill empty cells but DON'T block placement on occupied cells.
#
# Controls: Mouse only — click and drag pieces onto the grid
# =============================================================================

import pygame
import random
import sys
import json
import os
import math

# ── CONSTANTS ─────────────────────────────────────────────────────────────────

GRID_SIZE   = 8
CELL        = 64
GRID_PX     = GRID_SIZE * CELL

TRAY_W      = 240
SCREEN_W    = GRID_PX + TRAY_W
SCREEN_H    = GRID_PX + 80
GRID_X      = 0
GRID_Y      = 80

# Colors
BG          = (18,  18,  28)
GRID_BG     = (30,  30,  45)
GRID_LINE   = (45,  45,  65)
WHITE       = (255, 255, 255)
GRAY        = (120, 120, 140)
DARK_GRAY   = (60,  60,  80)
BLACK       = (0,   0,   0)

# Ghost block color — greenish with transparency effect
GHOST_COLOR = (80,  255, 150)
GHOST_ALPHA = 140

# Block colors
COLORS = [
    (255,  80,  80),
    (80,  180, 255),
    (80,  220, 120),
    (255, 180,  50),
    (200,  80, 255),
    (80,  220, 220),
    (255, 120, 180),
]

SCORE_FILE = "block_blast_highscore.json"


# ── PIECE SHAPES ──────────────────────────────────────────────────────────────
# Each shape is a list of dicts: {"offset": (r,c), "ghost": bool}
# At least one cell per shape is a ghost.

SHAPES = [
    # Single — the only cell is a ghost
    [
        {"offset": (0,0), "ghost": True},
    ],
    # Dominoes
    [
        {"offset": (0,0), "ghost": True},
        {"offset": (0,1), "ghost": False},
    ],
    [
        {"offset": (0,0), "ghost": False},
        {"offset": (1,0), "ghost": True},
    ],
    # Triominoes
    [
        {"offset": (0,0), "ghost": False},
        {"offset": (0,1), "ghost": True},
        {"offset": (0,2), "ghost": False},
    ],
    [
        {"offset": (0,0), "ghost": True},
        {"offset": (1,0), "ghost": False},
        {"offset": (2,0), "ghost": False},
    ],
    [
        {"offset": (0,0), "ghost": False},
        {"offset": (0,1), "ghost": True},
        {"offset": (1,0), "ghost": False},
    ],
    [
        {"offset": (0,0), "ghost": False},
        {"offset": (0,1), "ghost": True},
        {"offset": (1,1), "ghost": False},
    ],
    [
        {"offset": (0,0), "ghost": True},
        {"offset": (1,0), "ghost": False},
        {"offset": (1,1), "ghost": False},
    ],
    [
        {"offset": (0,0), "ghost": False},
        {"offset": (1,0), "ghost": True},
        {"offset": (0,1), "ghost": False},
    ],
    # Tetrominoes
    [
        {"offset": (0,0), "ghost": False},
        {"offset": (0,1), "ghost": True},
        {"offset": (0,2), "ghost": False},
        {"offset": (0,3), "ghost": False},
    ],
    [
        {"offset": (0,0), "ghost": False},
        {"offset": (1,0), "ghost": False},
        {"offset": (2,0), "ghost": True},
        {"offset": (3,0), "ghost": False},
    ],
    [
        {"offset": (0,0), "ghost": False},
        {"offset": (0,1), "ghost": True},
        {"offset": (1,0), "ghost": False},
        {"offset": (1,1), "ghost": False},
    ],
    [
        {"offset": (0,0), "ghost": True},
        {"offset": (0,1), "ghost": False},
        {"offset": (0,2), "ghost": False},
        {"offset": (1,0), "ghost": False},
    ],
    [
        {"offset": (0,0), "ghost": False},
        {"offset": (1,0), "ghost": False},
        {"offset": (2,0), "ghost": False},
        {"offset": (2,1), "ghost": True},
    ],
    [
        {"offset": (0,0), "ghost": False},
        {"offset": (0,1), "ghost": False},
        {"offset": (0,2), "ghost": True},
        {"offset": (1,2), "ghost": False},
    ],
    [
        {"offset": (0,0), "ghost": False},
        {"offset": (0,1), "ghost": True},
        {"offset": (1,1), "ghost": False},
        {"offset": (2,1), "ghost": False},
    ],
    [
        {"offset": (0,0), "ghost": False},
        {"offset": (0,1), "ghost": True},
        {"offset": (1,1), "ghost": False},
        {"offset": (1,2), "ghost": False},
    ],
    [
        {"offset": (0,0), "ghost": False},
        {"offset": (1,0), "ghost": True},
        {"offset": (1,1), "ghost": False},
        {"offset": (2,1), "ghost": False},
    ],
    [
        {"offset": (0,1), "ghost": True},
        {"offset": (0,2), "ghost": False},
        {"offset": (1,0), "ghost": False},
        {"offset": (1,1), "ghost": False},
    ],
    # Pentominoes
    [
        {"offset": (0,0), "ghost": False},
        {"offset": (0,1), "ghost": True},
        {"offset": (0,2), "ghost": False},
        {"offset": (1,1), "ghost": False},
        {"offset": (2,1), "ghost": False},
    ],
    [
        {"offset": (0,0), "ghost": False},
        {"offset": (0,1), "ghost": True},
        {"offset": (0,2), "ghost": False},
        {"offset": (0,3), "ghost": False},
        {"offset": (0,4), "ghost": False},
    ],
    [
        {"offset": (0,0), "ghost": False},
        {"offset": (1,0), "ghost": False},
        {"offset": (2,0), "ghost": True},
        {"offset": (3,0), "ghost": False},
        {"offset": (4,0), "ghost": False},
    ],
    [
        {"offset": (0,0), "ghost": False},
        {"offset": (0,1), "ghost": True},
        {"offset": (1,0), "ghost": False},
        {"offset": (1,1), "ghost": False},
        {"offset": (2,0), "ghost": False},
    ],
    [
        {"offset": (0,0), "ghost": False},
        {"offset": (0,1), "ghost": False},
        {"offset": (0,2), "ghost": True},
        {"offset": (1,0), "ghost": False},
        {"offset": (1,1), "ghost": False},
    ],
]


# ── HIGH SCORE ────────────────────────────────────────────────────────────────

def load_highscore():
    try:
        with open(SCORE_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get("highscore", 0)
    except Exception:
        return 0

def save_highscore(score):
    try:
        with open(SCORE_FILE, "w", encoding="utf-8") as f:
            json.dump({"highscore": score}, f)
    except Exception:
        pass


# ── PIECE CLASS ───────────────────────────────────────────────────────────────

class Piece:
    def __init__(self):
        shape_data = random.choice(SHAPES)
        self.cell_data = shape_data  # list of {"offset": (r,c), "ghost": bool}
        self.color = random.choice(COLORS)
        offsets = [d["offset"] for d in shape_data]
        self.rows = max(r for r, c in offsets) + 1
        self.cols = max(c for r, c in offsets) + 1

    def cells(self, anchor_r, anchor_c):
        """Return list of (r, c, is_ghost) for all cells in this piece."""
        return [(anchor_r + d["offset"][0], anchor_c + d["offset"][1], d["ghost"])
                for d in self.cell_data]

    def normal_cells(self, anchor_r, anchor_c):
        """Return only non-ghost cells."""
        return [(r, c) for r, c, g in self.cells(anchor_r, anchor_c) if not g]

    def ghost_cells(self, anchor_r, anchor_c):
        """Return only ghost cells."""
        return [(r, c) for r, c, g in self.cells(anchor_r, anchor_c) if g]

    def ghost_count(self):
        return sum(1 for d in self.cell_data if d["ghost"])

    def normal_count(self):
        return sum(1 for d in self.cell_data if not d["ghost"])


# ── DRAW HELPERS ──────────────────────────────────────────────────────────────

def draw_block(surface, color, gx, gy, size):
    r, g, b = tuple(color)[:3]
    rect = pygame.Rect(gx, gy, size, size)
    pygame.draw.rect(surface, (r, g, b), rect)
    # Highlight top-left
    hl = tuple(min(255, v + 50) for v in (r, g, b))
    pygame.draw.line(surface, hl, (gx + 1, gy + 1), (gx + size - 2, gy + 1), 2)
    pygame.draw.line(surface, hl, (gx + 1, gy + 1), (gx + 1, gy + size - 2), 2)
    # Shadow bottom-right
    sd = tuple(max(0, v - 50) for v in (r, g, b))
    pygame.draw.line(surface, sd, (gx + 1, gy + size - 2), (gx + size - 2, gy + size - 2), 2)
    pygame.draw.line(surface, sd, (gx + size - 2, gy + 1), (gx + size - 2, gy + size - 2), 2)

def draw_ghost_block(surface, gx, gy, size):
    """Draw a ghost block with a distinct green tint and hatch pattern."""
    rect = pygame.Rect(gx, gy, size, size)
    # Green-tinted background
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    s.fill((80, 255, 150, GHOST_ALPHA))
    surface.blit(s, (gx, gy))
    # Hatch lines
    for i in range(0, size, 6):
        pygame.draw.line(surface, (60, 200, 120, 100), 
                         (gx + i, gy), (gx + size, gy + size - i), 1)
    # Border
    pygame.draw.rect(surface, (60, 200, 120), rect, 1)

def draw_text_centered(surface, font, text, color, y):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(SCREEN_W // 2, y))
    surface.blit(surf, rect)


# ── GRID HELPERS ──────────────────────────────────────────────────────────────

def can_place(grid, piece, anchor_r, anchor_c):
    """
    A piece can be placed if:
    - All NORMAL cells land on empty grid cells
    - All cells (normal + ghost) are within bounds
    - Ghost cells can land on ANY cell (empty or filled)
    """
    for r, c, is_ghost in piece.cells(anchor_r, anchor_c):
        # Check bounds for ALL cells
        if not (0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE):
            return False
        # Normal cells must land on empty spots
        if not is_ghost and grid[r][c] is not None:
            return False
        # Ghost cells can land anywhere (empty or filled) — no check needed
    return True

def place_piece(grid, piece, anchor_r, anchor_c):
    """Place all cells (normal + ghost) onto the grid."""
    for r, c, is_ghost in piece.cells(anchor_r, anchor_c):
        if is_ghost:
            # Ghost blocks fill empty cells, but if the cell is already filled,
            # it gets overwritten with the ghost color (or we could leave it)
            # Design choice: ghost fills empty, preserves existing filled cells
            if grid[r][c] is None:
                grid[r][c] = GHOST_COLOR
            # If already filled, leave as-is (ghost doesn't overwrite)
        else:
            grid[r][c] = piece.color

def find_clears(grid):
    full_rows = [r for r in range(GRID_SIZE) if all(grid[r][c] is not None for c in range(GRID_SIZE))]
    full_cols = [c for c in range(GRID_SIZE) if all(grid[r][c] is not None for r in range(GRID_SIZE))]
    return full_rows, full_cols

def clear_lines(grid, rows, cols):
    for r in rows:
        for c in range(GRID_SIZE):
            grid[r][c] = None
    for c in cols:
        for r in range(GRID_SIZE):
            grid[r][c] = None

def any_piece_fits(grid, pieces):
    for piece in pieces:
        if piece is None:
            continue
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if can_place(grid, piece, r, c):
                    return True
    return False

def score_for_clear(rows, cols):
    total = len(rows) + len(cols)
    if total == 0:
        return 0
    base = total * 10
    bonus = (total - 1) * 5
    return base + bonus


# ── TRAY LAYOUT ───────────────────────────────────────────────────────────────

TRAY_CELL = 22
TRAY_X    = GRID_PX + 20

def tray_piece_rect(piece, slot):
    slot_h  = (SCREEN_H - GRID_Y) // 3
    slot_y  = GRID_Y + slot * slot_h + slot_h // 2
    piece_h = piece.rows * TRAY_CELL
    piece_w = piece.cols * TRAY_CELL
    px      = TRAY_X + (TRAY_W - piece_w) // 2 - 10
    py      = slot_y - piece_h // 2
    return px, py

def draw_tray_piece(surface, piece, px, py, cell_size=TRAY_CELL):
    for r, c, is_ghost in piece.cells(0, 0):
        gx = px + c * cell_size
        gy = py + r * cell_size
        if is_ghost:
            draw_ghost_block(surface, gx, gy, cell_size - 2)
        else:
            draw_block(surface, piece.color, gx, gy, cell_size - 2)

def draw_piece_at(surface, piece, px, py, cell_size, alpha=255):
    """Draw a piece at an arbitrary position (used for dragging)."""
    for r, c, is_ghost in piece.cells(0, 0):
        gx = px + c * cell_size
        gy = py + r * cell_size
        if is_ghost:
            draw_ghost_block(surface, gx, gy, cell_size - 2)
        else:
            draw_block(surface, piece.color, gx, gy, cell_size - 2)

def pixel_to_grid(px, py):
    if px < GRID_X or px >= GRID_X + GRID_PX:
        return None
    if py < GRID_Y or py >= GRID_Y + GRID_PX:
        return None
    col = (px - GRID_X) // CELL
    row = (py - GRID_Y) // CELL
    return row, col


# ── FLASH EFFECT ──────────────────────────────────────────────────────────────

class FlashEffect:
    def __init__(self, cells, duration=300):
        self.cells = cells
        self.duration = duration
        self.timer = duration

    def update(self, dt):
        self.timer -= dt

    @property
    def alive(self):
        return self.timer > 0

    @property
    def alpha(self):
        return int(255 * self.timer / self.duration)


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Block Blast — Ghost Block Edition")
    clock = pygame.time.Clock()

    font_big   = pygame.font.SysFont("monospace", 42, bold=True)
    font_med   = pygame.font.SysFont("monospace", 24, bold=True)
    font_small = pygame.font.SysFont("monospace", 16)
    font_tiny  = pygame.font.SysFont("monospace", 12)

    highscore = load_highscore()

    def new_game():
        grid   = [[None] * GRID_SIZE for _ in range(GRID_SIZE)]
        pieces = [Piece(), Piece(), Piece()]
        score  = 0
        return grid, pieces, score

    grid, pieces, score = new_game()

    dragging   = False
    drag_piece = None
    drag_slot  = None
    drag_pos   = (0, 0)
    ghost_pos  = None

    flashes    = []
    state      = "start"
    new_best   = False

    while True:
        dt = clock.tick(60)

        # ── events ────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

            if event.type == pygame.KEYDOWN:
                if state == "start":
                    state = "playing"
                elif state == "gameover":
                    if event.key == pygame.K_r:
                        grid, pieces, score = new_game()
                        flashes = []
                        new_best = False
                        state = "playing"
                    elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                        pygame.quit()
                        sys.exit(0)

            if state != "playing":
                continue

            if event.type == pygame.MOUSEMOTION:
                drag_pos = event.pos
                if dragging:
                    mx, my = drag_pos
                    cell = pixel_to_grid(
                        mx - drag_piece.cols * CELL // 2 + CELL // 2,
                        my - drag_piece.rows * CELL // 2 + CELL // 2
                    )
                    if cell:
                        ar, ac = cell
                        ghost_pos = (ar, ac) if can_place(grid, drag_piece, ar, ac) else None
                    else:
                        ghost_pos = None

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                if event.button == 3 and dragging:
                    dragging = False
                    drag_piece = None
                    drag_slot = None
                    ghost_pos = None

                elif event.button == 1:
                    if not dragging:
                        # Pick up from tray
                        for slot, piece in enumerate(pieces):
                            if piece is None:
                                continue
                            px, py = tray_piece_rect(piece, slot)
                            pw = piece.cols * TRAY_CELL
                            ph = piece.rows * TRAY_CELL
                            if px <= mx <= px + pw and py <= my <= py + ph:
                                dragging = True
                                drag_piece = piece
                                drag_slot = slot
                                drag_pos = (mx, my)
                                ghost_pos = None
                                break
                    else:
                        # Place on grid
                        if ghost_pos:
                            ar, ac = ghost_pos
                            place_piece(grid, drag_piece, ar, ac)
                            pieces[drag_slot] = None

                            # Check clears
                            full_rows, full_cols = find_clears(grid)
                            if full_rows or full_cols:
                                flash_cells = [(r, c) for r in full_rows for c in range(GRID_SIZE)]
                                flash_cells += [(r, c) for r in range(GRID_SIZE) for c in full_cols]
                                flashes.append(FlashEffect(list(set(flash_cells))))
                                pts = score_for_clear(full_rows, full_cols)
                                pts += drag_piece.normal_count() + drag_piece.ghost_count()
                                score += pts
                                clear_lines(grid, full_rows, full_cols)
                            else:
                                score += drag_piece.normal_count() + drag_piece.ghost_count()

                            if score > highscore:
                                highscore = score
                                new_best = True
                                save_highscore(highscore)

                            if all(p is None for p in pieces):
                                pieces = [Piece(), Piece(), Piece()]

                            if not any_piece_fits(grid, pieces):
                                state = "gameover"

                        dragging = False
                        drag_piece = None
                        drag_slot = None
                        ghost_pos = None

        # ── update effects ─────────────────────────────────────────────────
        flashes = [f for f in flashes if f.alive]
        for f in flashes:
            f.update(dt)

        # ── draw ──────────────────────────────────────────────────────────
        screen.fill(BG)

        if state == "start":
            draw_text_centered(screen, font_big, "BLOCK BLAST", (80, 180, 255), 140)
            draw_text_centered(screen, font_med, "Ghost Block Edition", GHOST_COLOR, 190)
            draw_text_centered(screen, font_small, "Every piece has ghost blocks", GRAY, 240)
            draw_text_centered(screen, font_small, "Ghosts fill empty cells, ignore filled ones", GRAY, 265)
            draw_text_centered(screen, font_small, "Drag pieces onto the grid", WHITE, 310)
            draw_text_centered(screen, font_small, "Fill rows or columns to clear them", GRAY, 340)
            draw_text_centered(screen, font_small, "Press any key to start", WHITE, 400)
            if highscore > 0:
                draw_text_centered(screen, font_small, f"Best: {highscore}", (255, 200, 50), 440)

        else:
            # ── Score bar ──
            score_surf = font_med.render(f"Score: {score}", True, WHITE)
            best_surf  = font_small.render(f"Best: {highscore}", True, (255, 200, 50))
            ghost_info = font_tiny.render("Green = ghost block (fits anywhere)", True, GHOST_COLOR)
            screen.blit(score_surf, (12, 15))
            screen.blit(best_surf, (12, 45))
            screen.blit(ghost_info, (SCREEN_W - 250, 20))

            # ── Grid background ──
            grid_rect = pygame.Rect(GRID_X, GRID_Y, GRID_PX, GRID_PX)
            pygame.draw.rect(screen, GRID_BG, grid_rect)

            for i in range(GRID_SIZE + 1):
                x = GRID_X + i * CELL
                y = GRID_Y + i * CELL
                pygame.draw.line(screen, GRID_LINE, (x, GRID_Y), (x, GRID_Y + GRID_PX))
                pygame.draw.line(screen, GRID_LINE, (GRID_X, y), (GRID_X + GRID_PX, y))

            # ── Ghost preview ──
            if dragging and ghost_pos:
                ar, ac = ghost_pos
                for r, c, is_ghost in drag_piece.cells(ar, ac):
                    gx = GRID_X + c * CELL
                    gy = GRID_Y + r * CELL
                    if is_ghost:
                        s = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
                        s.fill((80, 255, 150, 80))
                        screen.blit(s, (gx, gy))
                    else:
                        s = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
                        _c = tuple(drag_piece.color)[:3]
                        s.fill((_c[0], _c[1], _c[2], 80))
                        screen.blit(s, (gx, gy))

            # ── Draw placed blocks ──
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    if grid[r][c] is not None:
                        gx = GRID_X + c * CELL
                        gy = GRID_Y + r * CELL
                        if grid[r][c] == GHOST_COLOR:
                            draw_ghost_block(screen, gx, gy, CELL - 1)
                        else:
                            draw_block(screen, grid[r][c], gx, gy, CELL - 1)

            # ── Flash effects ──
            for flash in flashes:
                for r, c in flash.cells:
                    gx = GRID_X + c * CELL
                    gy = GRID_Y + r * CELL
                    s = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
                    a = max(0, min(255, int(flash.alpha)))
                    s.fill((255, 255, 255, a))
                    screen.blit(s, (gx, gy))

            # ── Tray divider ──
            pygame.draw.line(screen, GRID_LINE, (GRID_PX, GRID_Y), (GRID_PX, SCREEN_H), 2)

            # ── Tray pieces ──
            for slot, piece in enumerate(pieces):
                if piece is None or (dragging and slot == drag_slot):
                    continue
                px, py = tray_piece_rect(piece, slot)
                draw_tray_piece(screen, piece, px, py)

            # ── Held piece ──
            if dragging and drag_piece:
                mx, my = drag_pos
                px = mx - drag_piece.cols * CELL // 2
                py = my - drag_piece.rows * CELL // 2
                draw_piece_at(screen, drag_piece, px, py, CELL - 2)

            # ── Game over ──
            if state == "gameover":
                overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 170))
                screen.blit(overlay, (0, 0))
                draw_text_centered(screen, font_big, "GAME OVER", (220, 50, 50), 220)
                draw_text_centered(screen, font_med, f"Score: {score}", WHITE, 290)
                if new_best:
                    draw_text_centered(screen, font_med, "New Best!", (255, 200, 50), 330)
                else:
                    draw_text_centered(screen, font_small, f"Best: {highscore}", (255, 200, 50), 330)
                draw_text_centered(screen, font_small, "R - Restart    Q - Quit", GRAY, 390)

        pygame.display.flip()


if __name__ == "__main__":
    main()
