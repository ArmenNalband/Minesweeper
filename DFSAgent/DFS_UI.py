import os
import sys
import time
import concurrent.futures
import pygame
import csv
from pathlib import Path

sys.path.insert(0, str(Path(os.getcwd()).resolve().parent))

from UserPlay.backend import Minesweeper
from DFSAgent.DFS_BACKEND import DFSAgent

pygame.init()

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 750  # Extra space for timer, flags, and controls
GRID_SIZE = 16
NUM_MINES = 40
TILE_SIZE = SCREEN_WIDTH // GRID_SIZE

BACKGROUND_COLOR = (211, 211, 211)
LINE_COLOR = (0, 0, 0)
COVERED_CELL_COLOR = (128, 128, 128)
UNCOVERED_CELL_COLOR = BACKGROUND_COLOR
TEXT_COLOR = (0, 0, 0)

FONT = pygame.font.Font(None, 36)
TIMER_FONT = pygame.font.Font(None, 48)

FLAG_IMAGE = pygame.image.load("../Images/Flag.png")
FLAG_IMAGE = pygame.transform.scale(FLAG_IMAGE, (TILE_SIZE - 4, TILE_SIZE - 4))
BOMB_IMAGE = pygame.image.load("../Images/Mine.png")
BOMB_IMAGE = pygame.transform.scale(BOMB_IMAGE, (TILE_SIZE - 4, TILE_SIZE - 4))

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Minesweeper")


# Function to load the next game_id from stats.csv
def load_game_id():
    if not os.path.exists("stats.csv"):
        return 1
    else:
        with open("stats.csv", "r", newline='') as f:
            reader = csv.reader(f)
            rows = list(reader)
            if len(rows) < 2:
                return 1
            else:
                last_game_id = int(rows[-1][0])
                return last_game_id + 1


game_id = load_game_id()

game = Minesweeper(grid_size=GRID_SIZE, num_mines=NUM_MINES)

dfs_agent = DFSAgent(
    game,
    lambda: (draw_tiles(), pygame.display.flip()),
    lambda win: end_game_popup(win)
)

dfs_enabled = False
last_dfs_move_time = time.time()
dfs_future = None  # Replace dfs_thread with dfs_future
step_count = 0

original_reveal_tile = game.reveal_tile
original_flag_tile = game.flag_tile


def reveal_tile_patched(row, col):
    global step_count
    step_count += 1
    return original_reveal_tile(row, col)


def flag_tile_patched(row, col):
    global step_count
    step_count += 1
    return original_flag_tile(row, col)


game.reveal_tile = reveal_tile_patched
game.flag_tile = flag_tile_patched


def draw_button(text, x, y, width, height):
    pygame.draw.rect(screen, BACKGROUND_COLOR, (x, y, width, height))
    button_text = FONT.render(text, True, LINE_COLOR)
    screen.blit(button_text, (x + 10, y + 10))
    return pygame.Rect(x, y, width, height)


def draw_timer_and_flags():
    elapsed_time = game.get_elapsed_time()
    minutes = elapsed_time // 60
    seconds = elapsed_time % 60
    timer_text = TIMER_FONT.render(f"{minutes:02}:{seconds:02}", True, TEXT_COLOR)
    screen.blit(timer_text, (SCREEN_WIDTH // 4, 30))

    flag_count_text = TIMER_FONT.render(str(game.flags_remaining), True, TEXT_COLOR)
    screen.blit(flag_count_text, (3 * SCREEN_WIDTH // 4 - 30, 30))
    screen.blit(FLAG_IMAGE, (3 * SCREEN_WIDTH // 4, 25))
    dfs_status = "ON" if dfs_enabled else "OFF"
    draw_button(f"DFS: {dfs_status}", 10, SCREEN_HEIGHT - 50, 100, 40)


def draw_grid():
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x = col * TILE_SIZE
            y = row * TILE_SIZE + 100
            pygame.draw.rect(screen, BACKGROUND_COLOR, (x, y, TILE_SIZE, TILE_SIZE))
            pygame.draw.rect(screen, LINE_COLOR, (x, y, TILE_SIZE, TILE_SIZE), 1)


def draw_tiles():
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x = col * TILE_SIZE
            y = row * TILE_SIZE + 100
            if (row, col) in game.revealed_tiles:
                pygame.draw.rect(screen, (255, 255, 255), (x, y, TILE_SIZE, TILE_SIZE))
                tile = game.grid[row][col]
                if tile.isdigit():
                    text = FONT.render(tile, True, TEXT_COLOR)
                    screen.blit(text, (x + TILE_SIZE // 4, y + TILE_SIZE // 4))
                elif tile == "M":
                    screen.blit(BOMB_IMAGE, (x + 2, y + 2))
            elif (row, col) in game.flags:
                screen.blit(FLAG_IMAGE, (x + 2, y + 2))


def end_game_popup(win):
    result = "You Win!" if win else "Game Over!"
    elapsed_time = game.get_elapsed_time()

    popup = pygame.Surface((400, 200))
    popup.fill((50, 50, 50))
    pygame.draw.rect(popup, (200, 200, 200), (10, 10, 380, 180))

    result_text = TIMER_FONT.render(result, True, TEXT_COLOR)
    popup.blit(result_text, (100, 50))

    time_text = FONT.render(f"Time: {elapsed_time // 60}m {elapsed_time % 60}s", True, TEXT_COLOR)
    popup.blit(time_text, (100, 100))

    close_button = pygame.Rect(150, 150, 100, 30)
    pygame.draw.rect(popup, (0, 0, 0), close_button)
    close_text = FONT.render("Close", True, (255, 255, 255))
    popup.blit(close_text, (170, 155))

    screen.blit(popup, (100, 250))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_stats_and_exit(result, elapsed_time, step_count)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if close_button.collidepoint(event.pos[0] - 100, event.pos[1] - 250):
                    waiting = False

    # After closing the popup, save stats and exit
    save_stats_and_exit(result, elapsed_time, step_count)


def save_stats_and_exit(result_text, elapsed_time, steps):
    result = "win" if "Win" in result_text else "lose"

    row = [str(game_id), result, str(int(elapsed_time)), str(steps)]
    file_exists = os.path.exists("stats.csv")
    with open("stats.csv", "a", newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["GameID", "Result", "Time", "Steps"])
        writer.writerow(row)

    pygame.quit()
    sys.exit()


def run_dfs():
    dfs_agent.play()


# Use a ThreadPoolExecutor from concurrent.futures instead of threading
import concurrent.futures

executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)


def main():
    global dfs_enabled, last_dfs_move_time, dfs_future
    clock = pygame.time.Clock()
    running = True

    while running:
        screen.fill(BACKGROUND_COLOR)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Exit without popup
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if event.button == 1:
                    if 10 <= mouse_x <= 200 and SCREEN_HEIGHT - 50 <= mouse_y <= SCREEN_HEIGHT:
                        old_state = dfs_enabled
                        dfs_enabled = not dfs_enabled
                        # If DFS just turned on, start run_dfs if not already running
                        if dfs_enabled and (dfs_future is None or dfs_future.done()):
                            dfs_future = executor.submit(run_dfs)
                        elif not dfs_enabled and old_state:
                            # DFS disabled, will stop on next sleep call in DFSAgent
                            pass
                    elif not dfs_enabled:
                        col = mouse_x // TILE_SIZE
                        row = (mouse_y - 100) // TILE_SIZE
                        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
                            tile_state = game.reveal_tile(row, col)
                            if tile_state == "M":
                                draw_timer_and_flags()
                                draw_grid()
                                draw_tiles()
                                pygame.display.flip()
                                end_game_popup(win=False)
                            elif game.check_win():
                                draw_timer_and_flags()
                                draw_grid()
                                draw_tiles()
                                pygame.display.flip()
                                end_game_popup(win=True)
                elif event.button == 3 and not dfs_enabled:
                    col = mouse_x // TILE_SIZE
                    row = (mouse_y - 100) // TILE_SIZE
                    if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
                        game.flag_tile(row, col)

        if game.is_game_over():
            draw_timer_and_flags()
            draw_grid()
            draw_tiles()
            pygame.display.flip()
            end_game_popup(win=game.check_win())

        auto_place_result = game.auto_place_flags()
        if auto_place_result == "win":
            draw_timer_and_flags()
            draw_grid()
            draw_tiles()
            pygame.display.flip()
            end_game_popup(win=True)
        elif auto_place_result == "lose":
            draw_timer_and_flags()
            draw_grid()
            draw_tiles()
            pygame.display.flip()
            end_game_popup(win=False)

        if game.check_win():
            draw_timer_and_flags()
            draw_grid()
            draw_tiles()
            pygame.display.flip()
            end_game_popup(win=True)

        draw_timer_and_flags()
        draw_grid()
        draw_tiles()
        pygame.display.flip()
        clock.tick(30)


if __name__ == "__main__":
    main()
