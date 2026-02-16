class Grid:
    EMPTY = 0
    WALL = 1
    START = 2
    GOAL = 3

    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.grid = [[self.EMPTY for _ in range(cols)] for _ in range(rows)]
        self.START = None
        self.GOAL = None

    def set_start(self, row, col):
        self.grid[row][col] = self.START
        self.START = (row, col)

    def set_goal(self, row, col):
        self.grid[row][col] = self.GOAL
        self.GOAL = (row, col)

    def add_wall(self, row, col):
        if self.grid[row][col] == self.EMPTY:
            self.grid[row][col] = self.WALL

    def remove_wall(self, row, col):
        if self.grid[row][col] == self.WALL:
            self.grid[row][col] = self.EMPTY

    def is_valid(self, row, col):
        return 0 <= row < self.rows and 0 <= col < self.cols and self.grid[row][col] != self.WALL
    
    def is_walkable(self, row, col):
        return self.is_valid(row, col) and self.grid[row][col] != self.WALL
    
    def get_val(self, row, col):
        if self.is_valid(row, col):
            return self.grid[row][col]
        return None
    
    def reset(self):
        self.grid = [[self.EMPTY for _ in range(self.cols)] for _ in range(self.rows)]
        self.START = None
        self.GOAL = None