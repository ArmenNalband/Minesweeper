import random
import time


class Minesweeper:
    def __init__(self, grid_size=10, num_mines=10):
        self.grid_size = grid_size
        self.num_mines = num_mines
        self.flags_remaining = num_mines
        self.grid = [[" " for _ in range(grid_size)] for _ in range(grid_size)]
        self.mine_positions = set()
        self.revealed_tiles = set()
        self.flags = set()
        self.game_over = False
        self.start_time = None
        self.end_time = None

        self._place_mines()
        self._calculate_neighbors()

    def _place_mines(self):
        """Randomly places mines on the grid."""
        while len(self.mine_positions) < self.num_mines:
            row = random.randint(0, self.grid_size - 1)
            col = random.randint(0, self.grid_size - 1)
            self.mine_positions.add((row, col))

    def _calculate_neighbors(self):
        """Calculates the number of neighboring mines for each tile."""
        for row, col in self.mine_positions:
            self.grid[row][col] = "M"
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = row + dr, col + dc
                    if 0 <= nr < self.grid_size and 0 <= nc < self.grid_size and self.grid[nr][nc] != "M":
                        if self.grid[nr][nc] == " ":
                            self.grid[nr][nc] = "1"
                        else:
                            self.grid[nr][nc] = str(int(self.grid[nr][nc]) + 1)

    def reveal_tile(self, row, col):
        """Reveals the selected tile and triggers flood-fill for tiles with no neighboring bombs."""
        if not self.start_time:
            self.start_time = time.time()

        if (row, col) in self.revealed_tiles or self.game_over:
            return

        if (row, col) in self.mine_positions:
            self.game_over = True
            self.end_time = time.time()
            return "M"

        self._flood_fill(row, col)

        return self.grid[row][col]

    def _flood_fill(self, row, col):
        """Flood-fill algorithm to open all connected cells with no neighboring bombs."""
        if not (0 <= row < self.grid_size and 0 <= col < self.grid_size):
            return
        if (row, col) in self.revealed_tiles:
            return

        self.revealed_tiles.add((row, col))

        if self.grid[row][col].isdigit() and self.grid[row][col] != "0":
            return

        for dr, dc in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            self._flood_fill(row + dr, col + dc)

    def flag_tile(self, row, col):
        """Flags or unflags a tile and updates the flag counter."""
        if (row, col) in self.flags:
            self.flags.remove((row, col))
            self.flags_remaining += 1
        else:
            if self.flags_remaining > 0:
                self.flags.add((row, col))
                self.flags_remaining -= 1

    def handle_number_click(self, row, col):
        """Handles clicks on already opened blocks with numbers."""
        if (row, col) not in self.revealed_tiles or self.grid[row][col] == " ":
            return False

        tile_value = self.grid[row][col]
        if not tile_value.isdigit() or tile_value == "0":
            return False

        flags_count = 0
        for dr, dc in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            nr, nc = row + dr, col + dc
            if (nr, nc) in self.flags:
                flags_count += 1

        if flags_count == int(tile_value):
            for dr, dc in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                nr, nc = row + dr, col + dc
                if (nr, nc) not in self.flags and 0 <= nr < self.grid_size and 0 <= nc < self.grid_size:
                    if (nr, nc) in self.mine_positions:
                        self.game_over = True
                        return True
                    self.reveal_tile(nr, nc)
        return False

    def auto_place_flags(self):
        """
        Automatically places flags on all remaining unrevealed tiles
        if the number of unrevealed tiles equals the number of flags remaining.
        """
        unrevealed_tiles = [
            (row, col)
            for row in range(self.grid_size)
            for col in range(self.grid_size)
            if (row, col) not in self.revealed_tiles and (row, col) not in self.flags
        ]

        if len(unrevealed_tiles) == self.flags_remaining:
            for tile in unrevealed_tiles:
                self.flags.add(tile)

            if self.flags == self.mine_positions:
                self.end_time = time.time()
                self.game_over = True
                return "win"
            else:
                self.end_time = time.time()
                self.game_over = True
                return "lose"
        return None

    def check_win(self):
        """Checks if the player has won the game."""
        if len(self.revealed_tiles) + len(self.flags) == self.grid_size * self.grid_size:
            if self.flags == self.mine_positions:
                self.end_time = time.time()
                self.game_over = True
                return True
        return False

    def is_game_over(self):
        """Checks if the game is over."""
        return self.game_over

    def get_elapsed_time(self):
        """Returns the elapsed time in seconds since the game started."""
        if not self.start_time:
            return 0
        return int(time.time() - self.start_time)

    def get_end_time(self):
        """Returns the total time the game lasted."""
        if self.end_time:
            return int(self.end_time - self.start_time)
        return 0
