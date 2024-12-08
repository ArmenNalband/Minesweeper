import copy

class Observer:
    def update(self, event_type, data=None):
        pass

class CSPBacktrackingAgent:
    def __init__(self, game):
        self.game = game
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, event_type, data=None):
        # After successful reveal/flag action
        for obs in self.observers:
            obs.update(event_type, data)

    def deduce_safe_cells_and_mines(self):
        return [], []

    def propagate_constraints(self, safe_cells, mines):
        for r, c in safe_cells:
            if (r, c) not in self.game.revealed_tiles:
                result = self.game.reveal_tile(r, c)
                if result == "M":
                    return False
                self.notify_observers("action_performed", (r,c))
        for r, c in mines:
            if (r, c) not in self.game.flags:
                self.game.flag_tile(r, c)
                self.notify_observers("action_performed", (r,c))
        return True

    def play_step(self):
        safe_cells, mines = self.deduce_safe_cells_and_mines()
        return "failure" if not (safe_cells or mines) or not self.propagate_constraints(safe_cells, mines) else "success"

    def try_guessing(self):
        candidates = self.get_uncertain_cells()
        return "failure" if not candidates else self.backtrack_guessing(candidates, 0)

    def backtrack_guessing(self, candidates, index):
        if index == len(candidates):
            return "success"

        row, col = candidates[index]
        saved_state = self.save_state()

        if self.game.flags_remaining > 0:
            self.game.flag_tile(row, col)
            self.notify_observers("action_performed", (row,col))
            if self._process_and_continue(candidates, index):
                return "success"
            self.restore_state(saved_state)

        if self.game.grid[row][col] != "M":
            self.restore_state(saved_state)
            if self._try_safe_guess(candidates, index, row, col):
                return "success"

        return "failure"

    def _process_and_continue(self, candidates, index):
        safe_cells, mines = self.deduce_safe_cells_and_mines()
        return self.propagate_constraints(safe_cells, mines) and not self.game.check_loss() and (
            self.game.check_win() or self.backtrack_guessing(candidates, index + 1) == "success")

    def _try_safe_guess(self, candidates, index, row, col):
        safe_state = self.save_state()
        result = self.game.reveal_tile(row, col)
        if result != "M":
            self.notify_observers("action_performed", (row,col))
            if self._process_and_continue(candidates, index):
                return True
            self.restore_state(safe_state)
        else:
            self.restore_state(safe_state)
        return False

    def get_uncertain_cells(self):
        return [(r, c) for r in range(self.game.grid_size) for c in range(self.game.grid_size)
                if (r, c) not in self.game.revealed_tiles and (r, c) not in self.game.flags]

    def save_state(self):
        return {
            'revealed_tiles': copy.deepcopy(self.game.revealed_tiles),
            'flags': copy.deepcopy(self.game.flags),
            'flags_remaining': self.game.flags_remaining,
            'game_over': self.game.game_over,
            'end_time': self.game.end_time
        }

    def restore_state(self, state):
        self.game.revealed_tiles = state['revealed_tiles']
        self.game.flags = state['flags']
        self.game.flags_remaining = state['flags_remaining']
        self.game.game_over = state['game_over']
        self.game.end_time = state['end_time']