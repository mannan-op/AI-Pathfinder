"""
All six uninformed search algorithms.
Each algorithm is implemented as a generator that yields (explored, frontier, path)
tuples at every step, enabling step-by-step GUI visualization.

Movement uses get_neighbors_clockwise() for consistent ordering.
"""

from collections import deque
import heapq
from utils.helpers import get_neighbors_clockwise, reconstruct_path


# ======================================================================== #
#  1. Breadth-First Search (BFS)                                            #
# ======================================================================== #

def bfs(grid, start: tuple, goal: tuple):
    """
    Explores nodes level-by-level.
    Guaranteed to find the shortest path (in terms of number of steps).
    """
    queue = deque([start])
    came_from = {start: None}
    explored = []
    frontier = list(queue)

    while queue:
        current = queue.popleft()
        explored.append(current)
        frontier = list(queue)

        if current == goal:
            path = reconstruct_path(came_from, start, goal)
            yield list(explored), list(frontier), path
            return

        for neighbor in get_neighbors_clockwise(*current, grid):
            if neighbor not in came_from:
                came_from[neighbor] = current
                queue.append(neighbor)

        frontier = list(queue)
        yield list(explored), list(frontier), []

    yield list(explored), [], []   # no path found


# ======================================================================== #
#  2. Depth-First Search (DFS)                                              #
# ======================================================================== #

def dfs(grid, start: tuple, goal: tuple):
    """
    Explores as deep as possible along each branch before backtracking.
    NOT guaranteed to find the shortest path.
    """
    stack = [start]
    came_from = {start: None}
    explored = []

    while stack:
        current = stack.pop()

        if current in explored:
            yield list(explored), list(stack), []
            continue

        explored.append(current)

        if current == goal:
            path = reconstruct_path(came_from, start, goal)
            yield list(explored), list(stack), path
            return

        for neighbor in reversed(get_neighbors_clockwise(*current, grid)):
            if neighbor not in came_from:
                came_from[neighbor] = current
                stack.append(neighbor)

        yield list(explored), list(stack), []

    yield list(explored), [], []


# ======================================================================== #
#  3. Uniform-Cost Search (UCS)                                             #
# ======================================================================== #

def ucs(grid, start: tuple, goal: tuple):
    """
    Expands the node with the lowest path cost first.
    Diagonal moves cost √2; cardinal moves cost 1.
    """
    def step_cost(a, b):
        if a[0] != b[0] and a[1] != b[1]:
            return 1.414   # diagonal ≈ √2
        return 1.0

    heap = [(0.0, start)]
    came_from = {start: None}
    cost_so_far = {start: 0.0}
    explored = []
    frontier_set = {start}

    while heap:
        cost, current = heapq.heappop(heap)
        frontier_set.discard(current)

        if current in explored:
            yield list(explored), list(frontier_set), []
            continue

        explored.append(current)

        if current == goal:
            path = reconstruct_path(came_from, start, goal)
            yield list(explored), list(frontier_set), path
            return

        for neighbor in get_neighbors_clockwise(*current, grid):
            new_cost = cost_so_far[current] + step_cost(current, neighbor)
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                came_from[neighbor] = current
                heapq.heappush(heap, (new_cost, neighbor))
                frontier_set.add(neighbor)

        yield list(explored), list(frontier_set), []

    yield list(explored), [], []


# ======================================================================== #
#  4. Depth-Limited Search (DLS)                                            #
# ======================================================================== #

def dls(grid, start: tuple, goal: tuple, depth_limit: int = 15):
    """
    DFS with a depth cap. Will not explore beyond depth_limit.
    Returns path if found within the limit, otherwise nothing.
    """
    explored = []
    frontier = []
    found = [False]

    def _dls_recursive(node, depth, path_set, came_from):
        explored.append(node)
        current_frontier = [n for n in get_neighbors_clockwise(*node, grid)
                            if n not in came_from]
        frontier.clear()
        frontier.extend(current_frontier)

        yield list(explored), list(frontier), []

        if node == goal:
            found[0] = True
            path = reconstruct_path(came_from, start, goal)
            yield list(explored), [], path
            return

        if depth == 0:
            return

        for neighbor in get_neighbors_clockwise(*node, grid):
            if neighbor not in came_from:
                came_from[neighbor] = node
                path_set.add(neighbor)
                yield from _dls_recursive(neighbor, depth - 1, path_set, came_from)
                if found[0]:
                    return
                path_set.discard(neighbor)

    came_from = {start: None}
    yield from _dls_recursive(start, depth_limit, {start}, came_from)

    if not found[0]:
        yield list(explored), [], []


# ======================================================================== #
#  5. Iterative Deepening DFS (IDDFS)                                       #
# ======================================================================== #

def iddfs(grid, start: tuple, goal: tuple, max_depth: int = 50):
    """
    Repeatedly calls DLS with increasing depth limits.
    Combines DFS memory efficiency with BFS optimality (on uniform-cost graphs).
    """
    all_explored = []
    all_frontier = []

    for limit in range(0, max_depth + 1):
        explored = []
        frontier = []
        found = [False]

        def _dls(node, depth, came_from):
            explored.append(node)
            all_explored.append(node)

            if node == goal:
                found[0] = True
                path = reconstruct_path(came_from, start, goal)
                yield list(all_explored), [], path
                return

            if depth == 0:
                yield list(all_explored), list(frontier), []
                return

            for neighbor in get_neighbors_clockwise(*node, grid):
                if neighbor not in came_from:
                    came_from[neighbor] = node
                    frontier.append(neighbor)
                    yield list(all_explored), list(frontier), []
                    yield from _dls(neighbor, depth - 1, came_from)
                    if found[0]:
                        return
                    frontier.discard(neighbor) if hasattr(frontier, 'discard') else None

        came_from = {start: None}
        gen = _dls(start, limit, came_from)
        for step in gen:
            yield step
            if found[0]:
                return

    yield list(all_explored), [], []


# ======================================================================== #
#  6. Bidirectional Search                                                   #
# ======================================================================== #

def bidirectional(grid, start: tuple, goal: tuple):
    """
    Runs BFS simultaneously from start and goal.
    Terminates when the two frontiers meet.
    """
    # Forward BFS
    fwd_queue = deque([start])
    fwd_visited = {start: None}

    # Backward BFS
    bwd_queue = deque([goal])
    bwd_visited = {goal: None}

    explored_fwd = []
    explored_bwd = []
    meeting_point = None

    def _intersect():
        for node in fwd_visited:
            if node in bwd_visited:
                return node
        return None

    while fwd_queue or bwd_queue:
        # ---- Forward step ----
        if fwd_queue:
            current = fwd_queue.popleft()
            explored_fwd.append(current)

            meeting_point = _intersect()
            if meeting_point:
                break

            for neighbor in get_neighbors_clockwise(*current, grid):
                if neighbor not in fwd_visited:
                    fwd_visited[neighbor] = current
                    fwd_queue.append(neighbor)

        # ---- Backward step ----
        if bwd_queue:
            current = bwd_queue.popleft()
            explored_bwd.append(current)

            meeting_point = _intersect()
            if meeting_point:
                break

            for neighbor in get_neighbors_clockwise(*current, grid):
                if neighbor not in bwd_visited:
                    bwd_visited[neighbor] = current
                    bwd_queue.append(neighbor)

        all_explored = list(set(explored_fwd) | set(explored_bwd))
        all_frontier = list(set(fwd_queue) | set(bwd_queue))
        yield all_explored, all_frontier, []

    # Reconstruct combined path
    if meeting_point:
        # Forward half: meeting_point → start
        path_fwd = []
        node = meeting_point
        while node is not None:
            path_fwd.append(node)
            node = fwd_visited.get(node)
        path_fwd.reverse()

        # Backward half: meeting_point → goal
        path_bwd = []
        node = bwd_visited.get(meeting_point)
        while node is not None:
            path_bwd.append(node)
            node = bwd_visited.get(node)

        full_path = path_fwd + path_bwd
        all_explored = list(set(explored_fwd) | set(explored_bwd))
        yield all_explored, [], full_path
    else:
        yield list(set(explored_fwd) | set(explored_bwd)), [], []
