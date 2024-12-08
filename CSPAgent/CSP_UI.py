import pygame
import sys
import time
import os
import csv
import concurrent.futures
from user import Minesweeper
from CSP_BACKEND import CSPBacktrackingAgent, Observer

pygame.init()

def load_game_id():
    if not os.path.exists("CSP_STAT.csv"):
        return 1
    else:
        with open("CSP_STAT.csv", "r", newline='') as f:
            reader = csv.reader(f)
            rows = list(reader)
            if len(rows) < 2:
                return 1
            else:
                last_game_id = int(rows[-1][0])
                return last_game_id + 1

# Global variables for statistics
game_id = load_game_id()
steps_count = 0  # Count solver steps

# Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
GRID_SIZE = 6
NUM_MINES = 12
TILE_SIZE = SCREEN_WIDTH // GRID_SIZE

BACKGROUND_COLOR = (211, 211, 211)
LINE_COLOR = (0, 0, 0)
TEXT_COLOR = (0, 0, 0)

FONT = pygame.font.Font(None, 36)
TIMER_FONT = pygame.font.Font(None, 48)

FLAG_IMAGE = pygame.image.load(os.path.join("..","Images","Flag.png"))
FLAG_IMAGE = pygame.transform.scale(FLAG_IMAGE, (TILE_SIZE - 4, TILE_SIZE - 4))

BOMB_IMAGE = pygame.image.load(os.path.join("..","Images","Mine.png"))
BOMB_IMAGE = pygame.transform.scale(BOMB_IMAGE, (TILE_SIZE - 4, TILE_SIZE - 4))

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Minesweeper")

class UIHandler(Observer):
    def __init__(self):
        self.current_test_cell = None
        self.delay_until = 0.0
        self.highlight_color = (255, 255, 0)

    def update(self, event_type, data=None):
        if event_type == "action_performed":
            self.current_test_cell = data
            self.delay_until = time.time() + 0.5

    def get_current_test_cell(self):
        return self.current_test_cell

    def is_delay_active(self):
        return time.time() < self.delay_until

game = Minesweeper(grid_size=GRID_SIZE, num_mines=NUM_MINES)
csp_agent = CSPBacktrackingAgent(game)
ui_handler = UIHandler()
csp_agent.add_observer(ui_handler)

csp_enabled = False
last_algo_move_time = time.time()
game_state = "running"

executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
solver_future = None  # Holds the future for a solver step if running

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

    csp_status = "ON" if csp_enabled else "OFF"
    draw_button(f"CSP: {csp_status}", 120, SCREEN_HEIGHT - 80, 100, 40)

def draw_grid():
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x = col * TILE_SIZE
            y = row * TILE_SIZE + 100
            pygame.draw.rect(screen, BACKGROUND_COLOR, (x, y, TILE_SIZE, TILE_SIZE))
            pygame.draw.rect(screen, LINE_COLOR, (x, y, TILE_SIZE, TILE_SIZE), 1)

def draw_tiles():
    current_test_cell = ui_handler.get_current_test_cell()
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x = col * TILE_SIZE
            y = row * TILE_SIZE + 100

            if current_test_cell == (row, col) and (row, col) not in game.revealed_tiles:
                pygame.draw.rect(screen, ui_handler.highlight_color, (x, y, TILE_SIZE, TILE_SIZE))
            else:
                if (row, col) in game.revealed_tiles:
                    pygame.draw.rect(screen, (255, 255, 255), (x, y, TILE_SIZE, TILE_SIZE))
                else:
                    pygame.draw.rect(screen, BACKGROUND_COLOR, (x, y, TILE_SIZE, TILE_SIZE))

            pygame.draw.rect(screen, LINE_COLOR, (x, y, TILE_SIZE, TILE_SIZE), 1)

            if (row, col) in game.revealed_tiles:
                tile = game.grid[row][col]
                if tile.isdigit():
                    text = FONT.render(tile, True, TEXT_COLOR)
                    screen.blit(text, (x + TILE_SIZE // 4, y + TILE_SIZE // 4))
                elif tile == "M":
                    screen.blit(BOMB_IMAGE, (x + 2, y + 2))
            elif (row, col) in game.flags:
                screen.blit(FLAG_IMAGE, (x + 2, y + 2))

def end_game_popup(win):
    global game_id, steps_count
    result = "You Win!" if win else "Game Over!"
    time_spent = game.get_end_time()

    # Determine result as "win" or "lose"
    final_result = "win" if win else "lose"

    # Write stats to "CSP_STAT.csv" with the given info
    csv_file = "CSP_STAT.csv"
    file_exists = os.path.exists(csv_file)
    with open(csv_file, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["GameID", "Result", "Time"])
        writer.writerow([str(game_id), final_result, str(int(time_spent))])

    # Increment game_id for next game
    game_id += 1

    popup = pygame.Surface((400, 200))
    popup.fill((50, 50, 50))
    pygame.draw.rect(popup, (200, 200, 200), (10, 10, 380, 180))

    result_text = TIMER_FONT.render(result, True, TEXT_COLOR)
    popup.blit(result_text, (100, 50))

    time_text = FONT.render(f"Time: {time_spent // 60}m {time_spent % 60}s", True, TEXT_COLOR)
    popup.blit(time_text, (100, 100))

    restart_button_rect = pygame.draw.rect(popup, (100, 200, 100), (140, 140, 120, 40))
    restart_text = FONT.render("Restart", True, TEXT_COLOR)
    popup.blit(restart_text, (150, 145))

    screen.blit(popup, (100, 250))
    pygame.display.flip()

    waiting = True
    while waiting:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                # If user closes window here, we just exit
                pygame.quit()
                sys.exit()
            elif e.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if 240 <= mx <= 360 and 390 <= my <= 430:
                    # On restart, reset steps_count
                    steps_count = 0
                    return "restart"

def solver_step():
    global steps_count
    # Increment steps each solver step
    steps_count += 1
    result = csp_agent.play_step()
    if result == "failure":
        guess_result = csp_agent.try_guessing()
    return True

def main():
    global csp_enabled, last_algo_move_time, game_state, game, csp_agent, solver_future

    clock = pygame.time.Clock()
    running = True

    while running:
        screen.fill(BACKGROUND_COLOR)

        if game_state in ["lost", "won"]:
            action = end_game_popup(win=(game_state=="won"))
            if action == "restart":
                game = Minesweeper(grid_size=GRID_SIZE, num_mines=NUM_MINES)
                csp_agent = CSPBacktrackingAgent(game)
                csp_agent.add_observer(ui_handler)
                game_state = "running"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and game_state == "running":
                mx, my = pygame.mouse.get_pos()

                if event.button == 1:  # Left click
                    if 10 <= mx <= 110 and SCREEN_HEIGHT - 80 <= my <= SCREEN_HEIGHT:
                        csp_enabled = False
                    elif 120 <= mx <= 220 and SCREEN_HEIGHT - 80 <= my <= SCREEN_HEIGHT:
                        csp_enabled = not csp_enabled
                    else:
                        col = mx // TILE_SIZE
                        row = (my - 100) // TILE_SIZE
                        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
                            tile_state = game.reveal_tile(row, col)
                            if tile_state == "M":
                                game_state = "lost"
                                game.end_time = time.time()
                            elif game.check_win():
                                game_state = "won"
                                game.end_time = time.time()

                elif event.button == 3 and not csp_enabled and game_state == "running":
                    col = mx // TILE_SIZE
                    row = (my - 100) // TILE_SIZE
                    if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
                        game.flag_tile(row, col)
                        if game.check_win():
                            game_state = "won"
                            game.end_time = time.time()

        if game_state == "running" and csp_enabled and not ui_handler.is_delay_active() and time.time() - last_algo_move_time >= 1:
            # Start a solver step in the background if not started
            # Only start if no future running
            if solver_future is None or solver_future.done():
                last_algo_move_time = time.time()
                from concurrent.futures import ThreadPoolExecutor
                # Already created executor above, we can use it directly
                solver_future = executor.submit(solver_step)

        # Check solver future result if any
        if solver_future and solver_future.done():
            # Just ensure no exception
            solver_future.result()
            solver_future = None
            # If done, next frame we can start next step after delay done

        if game.check_loss():
            game_state = "lost"
            draw_grid()
            game.end_time = time.time()
        elif game.check_win():
            game_state = "won"
            draw_grid()
            game.end_time = time.time()

        draw_timer_and_flags()
        draw_grid()
        draw_tiles()

        pygame.display.flip()
        clock.tick(30)

    executor.shutdown(wait=False)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    main()
