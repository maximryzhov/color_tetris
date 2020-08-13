# Classic tetris game. Procedural style, no classes
# 22/01/2018

import pygame as pg
import random
import sys
import os

# === 1. Constants ===
# 1.1. System settings
GAME_WIDTH = 800
GAME_HEIGHT = 600
GAME_TITLE = "Color Tetris"
MAX_FPS = 60

# 1.2. Gameplay settings
GRID_WIDTH = 10
GRID_HEIGHT = 22
HIDDEN_ROWS = 2

PIECE_NAMES = ["I", "O", "T", "S", "Z", "J", "L"]
PIECE_SHAPES = {
    "I": [[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0]],
    "O": [[1, 1], [1, 1]],
    "T": [[0, 1, 0], [1, 1, 1], [0, 0, 0]],
    "S": [[0, 1, 1], [1, 1, 0]],
    "Z": [[1, 1, 0], [0, 1, 1]],
    "J": [[1, 0, 0], [1, 1, 1], [0, 0, 0]],
    "L": [[0, 0, 1], [1, 1, 1], [0, 0, 0]]
}
PIECE_COLORS = {
    "I": pg.Color("cyan"),
    "O": pg.Color("yellow"),
    "T": pg.Color("purple"),
    "S": pg.Color("green"),
    "Z": pg.Color("red"),
    "J": pg.Color("blue"),
    "L": pg.Color("orange")
}

# Classic Tetris score system
SCORES = dict([
    (1, 40),
    (2, 100),
    (3, 300),
    (4, 1200)
])

GRAVITY_INTERVAL = 500
SHIFT_INTERVAL = 80
SOFT_DROP_INTERVAL = 40

EVENT_GRAVITY = pg.USEREVENT
EVENT_SHIFT_LEFT = pg.USEREVENT + 1
EVENT_SHIFT_RIGHT = pg.USEREVENT + 2

# 1.3. Interface settings
CELL_SIZE = 24
BG_COLOR = (0, 0, 0)
FG_COLOR = (255, 255, 255)
FONT_SIZE = 32

BORDER_WIDTH = GRID_WIDTH * CELL_SIZE
BORDER_HEIGHT = (GRID_HEIGHT - HIDDEN_ROWS) * CELL_SIZE
MARGIN_LEFT = GAME_WIDTH / 2 - BORDER_WIDTH / 2
MARGIN_TOP = GAME_HEIGHT / 2 - BORDER_HEIGHT / 2


# === 2. Game functions ===
def spawn_piece():
    global piece, piece_color, piece_x, piece_y
    piece_name = random.choice(PIECE_NAMES)
    piece = PIECE_SHAPES[piece_name]
    piece_color = PIECE_COLORS[piece_name]
    if piece_name == "I":
        piece_x = (GRID_WIDTH // 2) - 2
        piece_y = 1
    else:
        piece_x = (GRID_WIDTH // 2) - 1
        piece_y = 0
    pg.time.set_timer(EVENT_GRAVITY, GRAVITY_INTERVAL)


def start_game():
    global grid, grid_colors, score
    score = 0
    grid = [[0] * GRID_WIDTH for row in range(GRID_HEIGHT)]
    grid_colors = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
    spawn_piece()


def check_collision(piece_, piece_x_, piece_y_):
    """
    Returns True if any of the piece cells
    intersect the left or right wall or garbage
    """
    for row_index, row in enumerate(piece_):
        for column_index, cell in enumerate(row):
            if cell == 1:
                if piece_x_ + column_index < 0 \
                        or piece_x_ + column_index >= GRID_WIDTH \
                        or piece_y_ + row_index >= GRID_HEIGHT \
                        or grid[piece_y_ + row_index][piece_x_ + column_index] == 1:
                    return True
    return False


def draw_cell(x, y, color):
    """
    Draws a cell at given coordinates,
    with x and y bein its top left corner.
    """
    inner_margin = 1
    inner_cell = CELL_SIZE - (inner_margin * 2)
    pg.draw.rect(
        screen, color,
        (left + inner_margin, top + inner_margin, inner_cell, inner_cell))


# === 3. Entry point ===
if __name__ == '__main__':
    # 3.1 Pre-initializing
    # Center window position
    os.environ['SDL_VIDEO_CENTERED'] = '1'

    # 3.1. Initializing
    pg.init()
    pg.display.set_caption(GAME_TITLE)
    screen = pg.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
    font = pg.font.Font(None, FONT_SIZE)
    clock = pg.time.Clock()

    # 3.2. Starting a new game
    start_game()
    running = True

# === 4. Main game loop ===
while running:
    # 4.1 Event handling
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
            sys.exit()

        # Keyboard input
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                running = False
                sys.exit()
            if event.key == pg.K_r:
                start_game()
            if event.key == pg.K_LEFT:
                if not check_collision(piece, piece_x - 1, piece_y):
                    piece_x -= 1
                    pg.time.set_timer(EVENT_SHIFT_LEFT, SHIFT_INTERVAL)
            if event.key == pg.K_RIGHT:
                if not check_collision(piece, piece_x + 1, piece_y):
                    piece_x += 1
                    pg.time.set_timer(EVENT_SHIFT_RIGHT, SHIFT_INTERVAL)
            if event.key == pg.K_UP:
                rotated_piece = list(zip(*reversed(piece)))
                if not check_collision(rotated_piece, piece_x, piece_y):
                    piece = rotated_piece
            if event.key == pg.K_DOWN:
                pg.time.set_timer(EVENT_GRAVITY, SOFT_DROP_INTERVAL)
            if event.key == pg.K_SPACE:
                while not check_collision(piece, piece_x, piece_y + 1):
                    piece_y += 1

        if event.type == pg.KEYUP:
            if event.key == pg.K_LEFT:
                pg.time.set_timer(EVENT_SHIFT_LEFT, 0)
            if event.key == pg.K_RIGHT:
                pg.time.set_timer(EVENT_SHIFT_RIGHT, 0)
            if event.key == pg.K_DOWN:
                pg.time.set_timer(EVENT_GRAVITY, GRAVITY_INTERVAL)

        # Custom events:
        if event.type == EVENT_GRAVITY:
            if not check_collision(piece, piece_x, piece_y + 1):
                piece_y += 1
            else:
                # Stick piece onto the grid
                for row_index, row in enumerate(piece):
                    for column_index, cell in enumerate(row):
                        if cell == 1:
                            grid[piece_y + row_index][piece_x +
                                                      column_index] = 1
                            grid_colors[piece_y +
                                        row_index][piece_x +
                                                   column_index] = piece_color
                # Check if the line is cleared
                cleared_lines = 0
                for row_index, row in enumerate(grid):
                    if all(cell == 1 for cell in row):
                        del grid[row_index]
                        grid.insert(0, [0 for _ in range(0, GRID_WIDTH)])
                        cleared_lines += 1
                if cleared_lines:
                    score += SCORES.get(cleared_lines)
                spawn_piece()

                # Check for lockout
                if check_collision(piece, piece_x, piece_y + 1):
                    start_game()

        if event.type == EVENT_SHIFT_LEFT:
            if not check_collision(piece, piece_x - 1, piece_y):
                piece_x -= 1
        if event.type == EVENT_SHIFT_RIGHT:
            if not check_collision(piece, piece_x + 1, piece_y):
                piece_x += 1

    # 4.3. Drawing routines
    # Clear screen
    screen.fill(BG_COLOR)

    # Draw the piece
    for row_index, row in enumerate(piece):
        for column_index, cell in enumerate(row):
            if cell == 1 and piece_y + row_index > HIDDEN_ROWS - 1:
                left = MARGIN_LEFT + (CELL_SIZE * piece_x) + \
                    (CELL_SIZE * column_index)
                top = MARGIN_TOP + (CELL_SIZE * piece_y) + \
                    (CELL_SIZE * row_index) - (CELL_SIZE * HIDDEN_ROWS)
                draw_cell(left, top, piece_color)

    # Draw garbage
    for row_index, row in enumerate(grid):
        for column_index, cell in enumerate(row):
            if cell == 1:
                left = MARGIN_LEFT + (CELL_SIZE * column_index)
                top = MARGIN_TOP + (CELL_SIZE * row_index) - \
                    (CELL_SIZE * HIDDEN_ROWS)
                draw_cell(left, top, grid_colors[row_index][column_index])

    # Draw border around the playfield
    pg.draw.rect(screen, FG_COLOR,
                 (MARGIN_LEFT, MARGIN_TOP, BORDER_WIDTH, BORDER_HEIGHT), 1)

    # Draw score
    score_text = font.render("SCORE: {}".format(score), 1, FG_COLOR)
    screen.blit(score_text, (MARGIN_LEFT, MARGIN_TOP - FONT_SIZE))

    # Update screen
    pg.display.flip()

    # Wait for the frame to end
    clock.tick(MAX_FPS)
