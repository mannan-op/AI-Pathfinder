from environment.grid import Grid
# Quick test
if __name__ == "__main__":
    grid = Grid(10, 10)
    grid.set_start(0, 0)
    grid.set_goal(9, 9)
    grid.add_wall(5, 5)
    print(f"Start: {grid.START}")
    print(f"Goal: {grid.GOAL}")
    print(f"Is (5,5) walkable? {grid.is_walkable(5, 5)}")  # False
    print(f"Is (5,6) walkable? {grid.is_walkable(5, 6)}")  # True