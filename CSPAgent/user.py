import random, time

class Minesweeper:
    def __init__(self, grid_size=15, num_mines=25):
        self.grid_size = grid_size
        self.num_mines = num_mines
        self.start_time = None
        self.end_time = None
        self.revealed_tiles = set()
        self.flags = set()
        self.flags_remaining = num_mines
        self.game_over = False
        self.grid = self._generate_grid()

    def _generate_grid(self):
        grid = [["0" for _ in range(self.grid_size)] for _ in range(self.grid_size)]

        # Place mines
        mines = set()
        while len(mines) < self.num_mines:
            r = random.randint(0, self.grid_size-1)
            c = random.randint(0, self.grid_size-1)
            mines.add((r,c))
        for (r,c) in mines:
            grid[r][c] = "M"

        # Calculate adjacent mine counts
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                if grid[r][c] == "M":
                    continue
                count = 0
                for dr in [-1,0,1]:
                    for dc in [-1,0,1]:
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = r+dr, c+dc
                        if 0<=nr<self.grid_size and 0<=nc<self.grid_size:
                            if grid[nr][nc] == "M":
                                count += 1
                grid[r][c] = str(count)
        return grid

    def get_elapsed_time(self):
        if not self.start_time:
            return 0
        if self.end_time:
            return int(self.end_time - self.start_time)
        return int(time.time() - self.start_time)

    def get_end_time(self):
        if not self.end_time:
            return self.get_elapsed_time()
        return int(self.end_time - self.start_time)

    def reveal_tile(self, row, col):
        if self.game_over:
            return
        if not self.start_time:
            self.start_time = time.time()

        if (row,col) in self.revealed_tiles:
            return self.grid[row][col]

        if (row,col) in self.flags:
            # Can't reveal a flagged tile
            return None

        if self.grid[row][col] == "M":
            # Hit a mine
            self.game_over = True
            self.end_time = time.time()
            self.revealed_tiles.add((row,col))
            return "M"

        # Flood fill if '0'
        self._flood_fill(row, col)
        return self.grid[row][col]

    def _flood_fill(self, row, col):
        stack = [(row,col)]
        while stack:
            r,c = stack.pop()
            if (r,c) in self.revealed_tiles:
                continue
            self.revealed_tiles.add((r,c))
            if self.grid[r][c] == "0":
                for dr in [-1,0,1]:
                    for dc in [-1,0,1]:
                        if dr==0 and dc==0:
                            continue
                        nr, nc = r+dr, c+dc
                        if 0<=nr<self.grid_size and 0<=nc<self.grid_size:
                            if (nr,nc) not in self.revealed_tiles and (nr,nc) not in self.flags:
                                stack.append((nr,nc))

    def flag_tile(self, row, col):
        if self.game_over:
            return
        if (row,col) in self.flags:
            self.flags.remove((row,col))
            self.flags_remaining += 1
        else:
            if (row,col) not in self.revealed_tiles:
                self.flags.add((row,col))
                self.flags_remaining -= 1

    def check_win(self):
        if self.game_over:
            return False
        # Win if all non-mine tiles are revealed
        revealed_count = len(self.revealed_tiles)
        total_tiles = self.grid_size * self.grid_size
        mine_count = self.num_mines
        if revealed_count == total_tiles - mine_count:
            self.end_time = time.time()
            return True
        return False

    def check_loss(self):
        return self.game_over
