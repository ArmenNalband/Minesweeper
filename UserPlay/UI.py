import pygame
import sys
from backend import Minesweeper

# Initialize PyGame
pygame.init()

# Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 700  # Extra space for the timer and flags
GRID_SIZE = 10
NUM_MINES = 10
TILE_SIZE = SCREEN_WIDTH // GRID_SIZE

# Colors (Updated as provided)
BACKGROUND_COLOR = (211, 211, 211)
LINE_COLOR = (0, 0, 0)
CELL_BORDER_LIGHT = (255, 255, 255)
CELL_BORDER_DARK = (128, 128, 128)
COVERED_CELL_COLOR = (128, 128, 128)
UNCOVERED_CELL_COLOR = BACKGROUND_COLOR
TEXT_COLOR = (0, 0, 0)

# Load Images
FLAG_IMAGE = pygame.image.load("../Images/Flag.png")
FLAG_IMAGE = pygame.transform.scale(FLAG_IMAGE, (TILE_SIZE - 4, TILE_SIZE - 4))

BOMB_IMAGE = pygame.image.load("../Images/Mine.png")
BOMB_IMAGE = pygame.transform.scale(BOMB_IMAGE, (TILE_SIZE - 4, TILE_SIZE - 4))

# Fonts
FONT = pygame.font.Font(None, 36)
TIMER_FONT = pygame.font.Font(None, 48)

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Minesweeper")

# Initialize backend
game = Minesweeper(grid_size=GRID_SIZE, num_mines=NUM_MINES)


def draw_grid():
    """Draws the Minesweeper-style grid with 3D-like borders."""
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x = col * TILE_SIZE
            y = row * TILE_SIZE + 100  # Shift grid down for timer and flags

            pygame.draw.rect(screen, COVERED_CELL_COLOR, (x, y, TILE_SIZE, TILE_SIZE))  # Covered cell

            # Add a 3D-like border effect for each cell
            pygame.draw.line(screen, CELL_BORDER_LIGHT, (x, y), (x + TILE_SIZE - 1, y))  # Top border
            pygame.draw.line(screen, CELL_BORDER_LIGHT, (x, y), (x, y + TILE_SIZE - 1))  # Left border
            pygame.draw.line(screen, CELL_BORDER_DARK, (x + TILE_SIZE - 1, y), (x + TILE_SIZE - 1, y + TILE_SIZE - 1))  # Right border
            pygame.draw.line(screen, CELL_BORDER_DARK, (x, y + TILE_SIZE - 1), (x + TILE_SIZE - 1, y + TILE_SIZE - 1))  # Bottom border


def draw_tiles():
    """Draws the Minesweeper tiles based on their current state."""
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x = col * TILE_SIZE
            y = row * TILE_SIZE + 100  # Shift grid down for timer and flags

            if (row, col) in game.revealed_tiles:
                pygame.draw.rect(screen, UNCOVERED_CELL_COLOR, (x + 2, y + 2, TILE_SIZE - 4, TILE_SIZE - 4))
                tile = game.grid[row][col]
                if tile.isdigit():
                    text = FONT.render(tile, True, TEXT_COLOR)
                    screen.blit(text, (x + TILE_SIZE // 3, y + TILE_SIZE // 4))
                elif tile == "M":
                    screen.blit(BOMB_IMAGE, (x + 2, y + 2))
            elif (row, col) in game.flags:
                screen.blit(FLAG_IMAGE, (x + 2, y + 2))


def draw_timer_and_flags():
    """Draws the timer and the number of flags remaining."""
    elapsed_time = game.get_elapsed_time()
    minutes = elapsed_time // 60
    seconds = elapsed_time % 60
    timer_text = TIMER_FONT.render(f"{minutes:02}:{seconds:02}", True, TEXT_COLOR)
    screen.blit(timer_text, (SCREEN_WIDTH // 4, 30))

    flag_count_text = TIMER_FONT.render(str(game.flags_remaining), True, TEXT_COLOR)
    screen.blit(flag_count_text, (3 * SCREEN_WIDTH // 4 - 30, 30))
    screen.blit(FLAG_IMAGE, (3 * SCREEN_WIDTH // 4, 25))


def end_game_popup(win):
    """Displays a pop-up window showing whether the player won or lost."""
    result = "You Win!" if win else "Game Over!"
    time_spent = game.get_end_time()

    popup = pygame.Surface((400, 200))
    popup.fill((50, 50, 50))
    pygame.draw.rect(popup, (200, 200, 200), (10, 10, 380, 180))

    result_text = TIMER_FONT.render(result, True, TEXT_COLOR)
    popup.blit(result_text, (100, 50))

    time_text = FONT.render(f"Time: {time_spent // 60}m {time_spent % 60}s", True, TEXT_COLOR)
    popup.blit(time_text, (100, 100))

    # Create Close button
    close_button = pygame.Rect(150, 150, 100, 30)
    pygame.draw.rect(popup, (0, 0, 0), close_button)
    close_text = FONT.render("Close", True, (255, 255, 255))
    popup.blit(close_text, (170, 155))

    screen.blit(popup, (100, 250))
    pygame.display.flip()

    # Wait for the user to click the Close button
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if close_button.collidepoint(event.pos[0] - 100, event.pos[1] - 250):  # Adjust for popup position
                    pygame.quit()
                    sys.exit()


def main():
    """Main game loop."""
    clock = pygame.time.Clock()
    running = True

    while running:
        screen.fill(BACKGROUND_COLOR)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                col = mouse_x // TILE_SIZE
                row = (mouse_y - 100) // TILE_SIZE  # Adjust for timer and flags offset

                if event.button == 1:  # Left click to reveal or handle number click
                    if not game.is_game_over():
                        if (row, col) in game.revealed_tiles:
                            # Handle clicking on already opened blocks
                            if game.handle_number_click(row, col):
                                end_game_popup(win=False)
                                running = False
                        else:
                            tile_state = game.reveal_tile(row, col)
                            if tile_state == "M":
                                end_game_popup(win=False)
                                running = False
                            elif game.check_win():
                                end_game_popup(win=True)
                                running = False
                elif event.button == 3:  # Right click to flag
                    if not game.is_game_over():
                        game.flag_tile(row, col)

        # Check if the game is won automatically
        if game.check_win():
            end_game_popup(win=True)
            running = False

        # Draw UI
        draw_timer_and_flags()
        draw_grid()
        draw_tiles()

        # Refresh screen
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()



if __name__ == "__main__":
    main()
