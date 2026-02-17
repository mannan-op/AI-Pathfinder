"""
Grid environment for the AI Pathfinder project.
Supports static walls and dynamic obstacles.
"""
import random


class Grid:
    """
    A 2D grid environment for search algorithms.
    Cells can be empty, walls, start, goal, or dynamic obstacles.
    """

    EMPTY = 0
    WALL = 1
    START = 2
    GOAL = 3
    DYNAMIC_OBSTACLE = 4

    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.grid = [[self.EMPTY] * cols for _ in range(rows)]
        self.start_pos = None
        self.goal_pos = None

    # ------------------------------------------------------------------ #
    #  Cell setters                                                         #
    # ------------------------------------------------------------------ #

    def set_start(self, row: int, col: int):
        """Set the start position."""
        if self.start_pos:
            r, c = self.start_pos
            self.grid[r][c] = self.EMPTY
        self.start_pos = (row, col)
        self.grid[row][col] = self.START

    def set_goal(self, row: int, col: int):
        """Set the goal position."""
        if self.goal_pos:
            r, c = self.goal_pos
            self.grid[r][c] = self.EMPTY
        self.goal_pos = (row, col)
        self.grid[row][col] = self.GOAL

    def add_wall(self, row: int, col: int):
        """Add a static wall at (row, col)."""
        if (row, col) not in (self.start_pos, self.goal_pos):
            self.grid[row][col] = self.WALL

    def remove_wall(self, row: int, col: int):
        """Remove wall at (row, col)."""
        if self.grid[row][col] == self.WALL:
            self.grid[row][col] = self.EMPTY

    def add_dynamic_obstacle(self, row: int, col: int):
        """Add a dynamic obstacle at (row, col)."""
        if (row, col) not in (self.start_pos, self.goal_pos):
            if self.grid[row][col] == self.EMPTY:
                self.grid[row][col] = self.DYNAMIC_OBSTACLE
                return True
        return False

    def remove_dynamic_obstacle(self, row: int, col: int):
        """Remove dynamic obstacle at (row, col)."""
        if self.grid[row][col] == self.DYNAMIC_OBSTACLE:
            self.grid[row][col] = self.EMPTY

    # ------------------------------------------------------------------ #
    #  Queries                                                              #
    # ------------------------------------------------------------------ #

    def is_valid(self, row: int, col: int) -> bool:
        """Return True if (row, col) is within grid bounds."""
        return 0 <= row < self.rows and 0 <= col < self.cols

    def is_walkable(self, row: int, col: int) -> bool:
        """Return True if the cell can be traversed."""
        if not self.is_valid(row, col):
            return False
        return self.grid[row][col] not in (self.WALL, self.DYNAMIC_OBSTACLE)

    def is_wall(self, row: int, col: int) -> bool:
        return self.grid[row][col] == self.WALL

    def is_blocked(self, row: int, col: int) -> bool:
        """Return True if cell is any kind of obstacle."""
        return self.grid[row][col] in (self.WALL, self.DYNAMIC_OBSTACLE)

    def get_cell(self, row: int, col: int) -> int:
        return self.grid[row][col]

    # ------------------------------------------------------------------ #
    #  Dynamic obstacle spawning                                            #
    # ------------------------------------------------------------------ #

    def spawn_dynamic_obstacle(self, probability: float = 0.02) -> tuple | None:
        """
        With the given probability, spawn a dynamic obstacle at a random
        empty cell.  Returns the cell coordinates if one was spawned, else None.
        """
        if random.random() < probability:
            empty_cells = [
                (r, c)
                for r in range(self.rows)
                for c in range(self.cols)
                if self.grid[r][c] == self.EMPTY
                and (r, c) != self.start_pos
                and (r, c) != self.goal_pos
            ]
            if empty_cells:
                cell = random.choice(empty_cells)
                self.grid[cell[0]][cell[1]] = self.DYNAMIC_OBSTACLE
                return cell
        return None

    # ------------------------------------------------------------------ #
    #  Utility                                                              #
    # ------------------------------------------------------------------ #

    def reset_search_state(self):
        """Clear dynamic obstacles from the grid."""
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == self.DYNAMIC_OBSTACLE:
                    self.grid[r][c] = self.EMPTY

    def copy(self):
        """Return a deep copy of this grid."""
        new_grid = Grid(self.rows, self.cols)
        new_grid.grid = [row[:] for row in self.grid]
        new_grid.start_pos = self.start_pos
        new_grid.goal_pos = self.goal_pos
        return new_grid

    def __repr__(self):
        symbols = {
            self.EMPTY: ".",
            self.WALL: "#",
            self.START: "S",
            self.GOAL: "G",
            self.DYNAMIC_OBSTACLE: "D",
        }
        lines = []
        for row in self.grid:
            lines.append(" ".join(symbols.get(cell, "?") for cell in row))
        return "\n".join(lines)
