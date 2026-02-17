"""
Utility helpers for the AI Pathfinder project.
"""


def get_neighbors_clockwise(row: int, col: int, grid) -> list:
    """
    Return walkable neighbors of (row, col) in the required clockwise order:
      1. Up          (row-1, col)
      2. Right       (row,   col+1)
      3. Bottom      (row+1, col)
      4. Bottom-Right (row+1, col+1)
      5. Bottom-Left  (row+1, col-1)
      6. Left         (row,   col-1)
      7. Top-Left     (row-1, col-1)
      8. Top-Right    (row-1, col+1)

    Only cells that are within bounds and walkable are included.
    """
    directions = [
        (-1,  0),   # 1. Up
        ( 0,  1),   # 2. Right
        ( 1,  0),   # 3. Bottom
        ( 1,  1),   # 4. Bottom-Right
        ( 1, -1),   # 5. Bottom-Left
        ( 0, -1),   # 6. Left
        (-1, -1),   # 7. Top-Left
        (-1,  1),   # 8. Top-Right
    ]

    neighbors = []
    for dr, dc in directions:
        nr, nc = row + dr, col + dc
        if grid.is_valid(nr, nc) and grid.is_walkable(nr, nc):
            neighbors.append((nr, nc))
    return neighbors


def reconstruct_path(came_from: dict, start: tuple, goal: tuple) -> list:
    """
    Reconstruct path from came_from map.
    Returns list of positions from start to goal (inclusive).
    """
    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = came_from.get(current)
    path.reverse()
    if path and path[0] == start:
        return path
    return []


def path_blocked(path: list, grid) -> bool:
    """Return True if any cell in path is now blocked (obstacle spawned on it)."""
    for cell in path:
        r, c = cell
        if not grid.is_walkable(r, c):
            return True
    return False


def manhattan_distance(a: tuple, b: tuple) -> float:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def euclidean_distance(a: tuple, b: tuple) -> float:
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5
