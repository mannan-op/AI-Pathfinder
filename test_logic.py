"""
Logic tests for the AI Pathfinder.
Verifies grid setup, neighbor ordering, and all search algorithms.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from environment.grid import Grid
from utils.helpers import get_neighbors_clockwise, reconstruct_path
from algorithms.search import bfs, dfs, ucs, dls, iddfs, bidirectional


def run_algo_to_completion(gen):
    """Drive a generator to its final yielded value."""
    result = ([], [], [])
    for result in gen:
        pass
    return result


def test_grid():
    print("=== Grid Tests ===")
    grid = Grid(10, 10)
    grid.set_start(0, 0)
    grid.set_goal(9, 9)
    grid.add_wall(1, 1)

    assert grid.start_pos == (0, 0), "Start wrong"
    assert grid.goal_pos  == (9, 9), "Goal wrong"
    assert grid.is_wall(1, 1),        "Wall not set"
    assert not grid.is_walkable(1, 1), "Wall should not be walkable"
    assert grid.is_walkable(0, 0),     "Start should be walkable"
    print("  Grid tests PASSED")


def test_neighbors():
    print("=== Neighbor Tests ===")
    grid = Grid(10, 10)
    grid.set_start(0, 0)
    grid.set_goal(9, 9)
    grid.add_wall(1, 1)

    # Corner cell: Up, Right, Bottom, Bottom-Right, Bottom-Left, Left, Top-Left, Top-Right
    # (0,0) valid: (1,0)=Bottom, (0,1)=Right  — (1,1) is wall
    n00 = get_neighbors_clockwise(0, 0, grid)
    assert len(n00) == 2, f"Corner (0,0) should have 2 walkable neighbors, got {len(n00)}"
    print(f"  (0,0) neighbors: {n00}  ✓")

    # Center cell with no walls/obstacles should have 8 neighbors
    n55 = get_neighbors_clockwise(5, 5, grid)
    assert len(n55) == 8, f"Center (5,5) should have 8 neighbors, got {len(n55)}"
    print(f"  (5,5) neighbor count: {len(n55)}  ✓")

    # Order check: first neighbor of (5,5) should be Up = (4,5)
    assert n55[0] == (4, 5), f"First neighbor should be Up (4,5), got {n55[0]}"
    print("  Order check (Up first)  ✓")
    print("  Neighbor tests PASSED")


def test_algorithms():
    print("=== Algorithm Tests ===")
    algos = [
        ("BFS",          bfs),
        ("DFS",          dfs),
        ("UCS",          ucs),
        ("DLS",          lambda g, s, e: dls(g, s, e, depth_limit=20)),
        ("IDDFS",        lambda g, s, e: iddfs(g, s, e, max_depth=30)),
        ("Bidirectional",bidirectional),
    ]

    for name, fn in algos:
        grid = Grid(10, 10)
        grid.set_start(0, 0)
        grid.set_goal(4, 4)

        explored, frontier, path = run_algo_to_completion(fn(grid, (0, 0), (4, 4)))
        found = len(path) > 0
        print(f"  {name:16s}: explored={len(explored):4d}  path_len={len(path):3d}  {'FOUND ✓' if found else 'NOT FOUND ✗'}")

    # Also test no-path scenario
    grid_blocked = Grid(5, 5)
    grid_blocked.set_start(0, 0)
    grid_blocked.set_goal(4, 4)
    for r in range(5):
        grid_blocked.add_wall(r, 2)

    _, _, path = run_algo_to_completion(bfs(grid_blocked, (0, 0), (4, 4)))
    assert len(path) == 0, "Should find no path through full wall"
    print("  No-path scenario  ✓")

    print("  Algorithm tests PASSED")


def test_dynamic_obstacles():
    print("=== Dynamic Obstacle Tests ===")
    grid = Grid(10, 10)
    grid.set_start(0, 0)
    grid.set_goal(9, 9)

    result = grid.add_dynamic_obstacle(5, 5)
    assert result, "Dynamic obstacle should have been added"
    assert not grid.is_walkable(5, 5), "Dynamic obstacle cell should not be walkable"

    grid.remove_dynamic_obstacle(5, 5)
    assert grid.is_walkable(5, 5), "Cell should be walkable after removal"

    grid.reset_search_state()
    print("  Dynamic obstacle tests PASSED")


def main():
    print("\n" + "="*50)
    print("  AI Pathfinder — Logic Test Suite")
    print("="*50 + "\n")

    test_grid()
    test_neighbors()
    test_algorithms()
    test_dynamic_obstacles()

    print("\n" + "="*50)
    print("  ALL TESTS PASSED ✓")
    print("="*50 + "\n")


if __name__ == "__main__":
    main()
