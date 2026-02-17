"""
AI Pathfinder — Main Entry Point
AI 2002 Assignment 1, Q7

Run with:
    python main.py

Controls:
    SPACE / ▶ Run      — Start / Pause the search
    →  (right arrow)   — Single step (when paused)
    R                  — Reset search
    Left-click (grid)  — Draw wall
    Right-click (grid) — Erase wall
"""

import pygame
from environment.grid import Grid
from visualization.gui import Visualizer
from utils.helpers import get_neighbors_clockwise


def create_sample_grid():
    """Create a 20×20 grid with a vertical wall in the middle."""
    grid = Grid(20, 20)

    # Start and goal in opposite corners
    grid.set_start(0, 0)
    grid.set_goal(19, 19)

    # Vertical wall with a gap to force the algorithm to route around
    for i in range(5, 15):
        grid.add_wall(i, 10)

    return grid


def test_neighbors(grid):
    """Quick console test of get_neighbors_clockwise."""
    print("\n--- Testing get_neighbors_clockwise ---\n")

    neighbors = get_neighbors_clockwise(5, 5, grid)
    print(f"Neighbors of (5,  5): {neighbors}")
    print(f"Expected 8, got: {len(neighbors)}")

    neighbors = get_neighbors_clockwise(0, 0, grid)
    print(f"Neighbors of (0,  0): {neighbors}")
    print(f"Expected 3, got: {len(neighbors)}")

    neighbors_wall = get_neighbors_clockwise(5, 9, grid)
    print(f"Neighbors of (5,  9) [next to wall]: {neighbors_wall}")
    print()


def main():
    grid = create_sample_grid()

    # Console sanity-check
    test_neighbors(grid)

    # Launch GUI (full interactive mode)
    vis = Visualizer(grid, cell_size=30)
    vis.run()


if __name__ == "__main__":
    main()
