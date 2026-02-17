# AI Pathfinder — AI 2002 Assignment 1 (Q7)

A Pygame-based AI grid pathfinder that visualises six uninformed search algorithms step-by-step, with dynamic obstacle spawning and re-planning.

---

## Features

| Feature | Details |
|---|---|
| **Algorithms** | BFS, DFS, UCS, DLS, IDDFS, Bidirectional Search |
| **Movement Order** | Clockwise: Up → Right → Bottom → Bottom-Right → Bottom-Left → Left → Top-Left → Top-Right |
| **Dynamic Obstacles** | Random obstacles spawn mid-search; re-planning triggers automatically |
| **GUI** | Real-time step-by-step animation with colour-coded cells |
| **Window Title** | `GOOD PERFORMANCE TIME APP` |

---

## Installation

```bash
pip install pygame-ce
```

> If you have the standard `pygame` installed you can use that instead — replace `pygame-ce` with `pygame` in `requirements.txt`.

Or install all requirements at once:

```bash
pip install -r requirements.txt
```

---

## Running

```bash
python main.py
```

---

## Controls

| Input | Action |
|---|---|
| `SPACE` or **▶ Run** button | Start / Pause the search |
| `→` (right arrow) | Step forward one node (while paused) |
| `R` | Reset search state |
| **Left-click** (grid) | Draw wall |
| **Right-click** (grid) | Erase wall |
| **Wall / Erase** buttons | Switch draw mode |
| **Speed + / Speed -** | Adjust animation speed |
| **↺ Reset** | Clear search state (keeps walls) |
| **✕ Clear Walls** | Remove all walls and reset |

---

## Project Structure

```
ai_pathfinder/
├── main.py                  # Entry point
├── test_logic.py            # Unit tests (no GUI required)
├── requirements.txt
├── README.md
│
├── environment/
│   ├── __init__.py
│   └── grid.py              # Grid class (cells, walls, dynamic obstacles)
│
├── algorithms/
│   ├── __init__.py
│   └── search.py            # BFS, DFS, UCS, DLS, IDDFS, Bidirectional
│
├── visualization/
│   ├── __init__.py
│   └── gui.py               # Pygame visualizer
│
└── utils/
    ├── __init__.py
    └── helpers.py           # get_neighbors_clockwise, path utilities
```

---

## Running Tests (No GUI)

```bash
python test_logic.py
```

---

## Colour Legend

| Colour | Meaning |
|---|---|
| 🟢 Green | Start (S) |
| 🔴 Red | Goal (G) |
| 🔵 Blue | Explored nodes |
| 🟡 Yellow | Frontier nodes |
| 🩵 Cyan | Final path |
| ⬛ Dark grey | Wall |
| 🟣 Purple | Dynamic obstacle |

---

## Algorithms — Brief Notes

### BFS
Explores level by level. Guaranteed shortest path (fewest steps). High memory use.

### DFS
Goes deep first. Fast in lucky cases; may find non-optimal path or get stuck in cycles.

### UCS
Expands by cumulative cost. Diagonal moves cost √2; cardinal moves cost 1. Optimal for weighted graphs.

### DLS (Depth-Limited Search)
DFS with a hard depth cap (`depth_limit=15`). Incomplete if the goal is deeper than the limit.

### IDDFS
Runs DLS with increasing limits (0, 1, 2, …). Combines BFS optimality with DFS memory efficiency.

### Bidirectional Search
Simultaneous BFS from start and goal. Meets in the middle, often exploring far fewer nodes.
