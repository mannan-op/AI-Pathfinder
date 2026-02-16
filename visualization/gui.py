# visualization/gui.py

import pygame
from environment.grid import Grid

class Visualizer:
    """Handles all Pygame visualization"""
    
    # Colors (RGB)
    COLOR_EMPTY = (255, 255, 255)      # White
    COLOR_WALL = (0, 0, 0)             # Black
    COLOR_START = (0, 255, 0)          # Green
    COLOR_GOAL = (255, 0, 0)         # Red
    COLOR_FRONTIER = (135, 206, 250)   # Sky Blue (nodes to explore)
    COLOR_EXPLORED = (169, 169, 169)   # Gray (visited nodes)
    COLOR_PATH = (255, 255, 0)         # Yellow (final path)
    COLOR_GRID_LINE = (200, 200, 200)  # Light gray
    
    def __init__(self, grid, cell_size=30, title="Pathfinding Visualization"):
        """
        Initialize Pygame window
        grid: Grid object
        cell_size: size of each cell in pixels
        """
        self.grid = grid
        self.cell_size = cell_size
        
        # Calculate window size
        self.width = grid.cols * cell_size
        self.height = grid.rows * cell_size
        
        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(title)
        
        self.clock = pygame.time.Clock()
        
        # Sets to track visualization state
        self.frontier_set = set()
        self.explored_set = set()
        self.path = []
    
    def draw_grid(self):
        """Draw the base grid with cells and grid lines"""
        # Fill background
        self.screen.fill(self.COLOR_EMPTY)
        
        # Draw each cell
        for row in range(self.grid.rows):
            for col in range(self.grid.cols):
                cell_type = self.grid.get_val(row, col)
                
                # Get cell position in pixels
                x = col * self.cell_size
                y = row * self.cell_size
                
                # Draw based on cell type
                if cell_type == Grid.WALL:
                    pygame.draw.rect(self.screen, self.COLOR_WALL, 
                                   (x, y, self.cell_size, self.cell_size))
                elif cell_type == Grid.START:
                    pygame.draw.rect(self.screen, self.COLOR_START, 
                                   (x, y, self.cell_size, self.cell_size))
                elif cell_type == Grid.GOAL:
                    pygame.draw.rect(self.screen, self.COLOR_GOAL, 
                                   (x, y, self.cell_size, self.cell_size))
        
        # Draw grid lines
        for row in range(self.grid.rows + 1):
            pygame.draw.line(self.screen, self.COLOR_GRID_LINE,
                           (0, row * self.cell_size),
                           (self.width, row * self.cell_size))
        
        for col in range(self.grid.cols + 1):
            pygame.draw.line(self.screen, self.COLOR_GRID_LINE,
                           (col * self.cell_size, 0),
                           (col * self.cell_size, self.height))
    
    def draw_cell(self, row, col, color):
        """Draw a single cell with given color"""
        x = col * self.cell_size
        y = row * self.cell_size
        pygame.draw.rect(self.screen, color, 
                        (x, y, self.cell_size, self.cell_size))
    
    def update_frontier(self, frontier_nodes):
        """Update and draw frontier nodes (nodes waiting to be explored)"""
        self.frontier_set = set(frontier_nodes)
        for node in frontier_nodes:
            if node != self.grid.START and node != self.grid.GOAL:
                self.draw_cell(node[0], node[1], self.COLOR_FRONTIER)
    
    def update_explored(self, explored_nodes):
        """Update and draw explored nodes (already visited)"""
        self.explored_set = set(explored_nodes)
        for node in explored_nodes:
            if node != self.grid.START and node != self.grid.GOAL:
                self.draw_cell(node[0], node[1], self.COLOR_EXPLORED)
    
    def draw_path(self, path):
        """Draw the final path"""
        self.path = path
        for node in path:
            if node != self.grid.START and node != self.grid.GOAL:
                self.draw_cell(node[0], node[1], self.COLOR_PATH)
    
    def refresh(self, delay=50):
        """
        Update the display
        delay: milliseconds to wait (for animation speed)
        """
        # Redraw everything in order
        self.draw_grid()
        
        # Draw explored nodes
        for node in self.explored_set:
            if node != self.grid.START and node != self.grid.GOAL:
                self.draw_cell(node[0], node[1], self.COLOR_EXPLORED)
        
        # Draw frontier nodes
        for node in self.frontier_set:
            if node != self.grid.START and node != self.grid.GOAL:
                self.draw_cell(node[0], node[1], self.COLOR_FRONTIER)
        
        # Draw path
        for node in self.path:
            if node != self.grid.START and node != self.grid.GOAL   :
                self.draw_cell(node[0], node[1], self.COLOR_PATH)
        
        # Draw start and target on top
        if self.grid.START:
            self.draw_cell(self.grid.START[0], self.grid.START[1], 
                          self.COLOR_START)
        if self.grid.GOAL:
            self.draw_cell(self.grid.GOAL[0], self.grid.GOAL[1], 
                          self.COLOR_GOAL)
        
        pygame.display.flip()
        pygame.time.delay(delay)
    
    def wait_for_close(self):
        """Keep window open until user closes it"""
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
        pygame.quit()