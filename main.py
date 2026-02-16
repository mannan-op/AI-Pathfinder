
import pygame
from environment.grid import Grid
from visualization.gui import Visualizer

def create_sample_grid():
    """Create a sample grid with some walls"""
    grid = Grid(20, 20)  # 20x20 grid
    
    # Set start and target
    grid.set_start(0, 0)
    grid.set_goal(19, 19)
    
    # Add some walls (creating a simple obstacle)
    for i in range(5, 15):
        grid.add_wall(i, 10)
    
    return grid

def main():
    # Create grid
    grid = create_sample_grid()
    
    # Create visualizer
    visualizer = Visualizer(grid, cell_size=30)
    
    # Draw initial state
    visualizer.refresh()
    
    # Simulate some exploration (just for testing)
    # Pretend we're exploring some cells
    explored = [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0)]
    frontier = [(2, 1), (3, 0), (1, 2)]
    
    visualizer.update_explored(explored)
    visualizer.update_frontier(frontier)
    visualizer.refresh()
    
    # Wait for user to close window
    visualizer.wait_for_close()

if __name__ == "__main__":
    main()