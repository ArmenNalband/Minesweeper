from UserPlay.backend import Minesweeper
import time


class DFSAgent:
    def __init__(self, game, update_ui_callback, end_game_callback):
        """
        Initializes the DFS agent.
        :param game: An instance of the Minesweeper game.
        :param update_ui_callback: Function to update the UI after each move.
        """
        self.game = game
        self.update_ui_callback = update_ui_callback  # Callback for UI updates
        self.end_game_callback = end_game_callback  # Callback for ending the game
        self.visited = set()

    def dfs(self, row, col):
        """
        Performs Depth-First Search to reveal tiles on the Minesweeper grid.
        :param row: The starting row of the DFS.
        :param col: The starting column of the DFS.
        """
        stack = [(row, col)]

        while stack:
            current_row, current_col = stack.pop()

            if (current_row, current_col) in self.visited:
                continue

            self.visited.add((current_row, current_col))

            # Reveal tile and notify the UI
            tile_value = self.game.reveal_tile(current_row, current_col)
            self.update_ui_callback()
            time.sleep(0.05)  # Delay for visibility

            # Flag the tile if it's a mine
            if tile_value == "M":
                self.game.place_flag(current_row, current_col)
                self.update_ui_callback()
                time.sleep(0.0001)  # Delay for visibility

            # Add neighbors for further exploration if the tile is "0"
            if tile_value == "0":
                for dr, dc in [
                    (-1, -1), (-1, 0), (-1, 1),
                    (0, -1), (0, 1),
                    (1, -1), (1, 0), (1, 1)
                ]:
                    nr, nc = current_row + dr, current_col + dc
                    if 0 <= nr < self.game.grid_size and 0 <= nc < self.game.grid_size:
                        stack.append((nr, nc))

        # Check if the game is won after this move
        if self.game.check_win():
            print("Congratulations! You've won the game!")
            return True

        return True

    def play(self):
        """
        Plays the game using DFS. Starts from the first safe tile found.
        """
        for row in range(self.game.grid_size):
            for col in range(self.game.grid_size):
                if (0, 0) in self.game.mine_positions:
                    success = self.dfs(0, 0)
                    if not success:
                        print("Game Over: Hit a mine!")
                        return
                if (row, col) not in self.visited and (row, col) not in self.game.mine_positions:
                    success = self.dfs(row, col)
                    if not success:
                        print("Game Over: Hit a mine!")
                        return
                    if self.game.check_win():
                        print("Congratulations! You've won the game!")
                        return
        print("Unable to make further progress. Manual intervention needed.")


if __name__ == "__main__":
    # Example usage
    minesweeper_game = Minesweeper(grid_size=10, num_mines=10)
    agent = DFSAgent(minesweeper_game)
    agent.play()
