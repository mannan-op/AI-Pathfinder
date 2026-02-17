"""
Pygame GUI Visualizer for the AI Pathfinder.
Title: GOOD PERFORMANCE TIME APP

Features:
- Step-by-step search animation with configurable speed
- Algorithm selector (BFS, DFS, UCS, DLS, IDDFS, Bidirectional)
- Live stats panel (steps, nodes explored, path length)
- Dynamic obstacle spawning with re-planning
- Mouse interaction: add/remove walls
- Color-coded cell rendering
"""

import pygame
import sys
import time
from environment.grid import Grid
from algorithms.search import bfs, dfs, ucs, dls, iddfs, bidirectional
from utils.helpers import get_neighbors_clockwise, path_blocked

# ======================================================================== #
#  Colour palette                                                            #
# ======================================================================== #
COLOR = {
    "bg":           (18,  18,  24),
    "grid_line":    (40,  40,  55),
    "empty":        (28,  28,  38),
    "wall":         (60,  60,  70),
    "start":        (50, 220, 120),
    "goal":         (240, 90,  80),
    "explored":     (50, 100, 200),
    "frontier":     (220, 180,  40),
    "path":         (0,  230, 180),
    "dynamic":      (200,  60, 200),
    "panel_bg":     (22,  22,  32),
    "panel_border": (70,  70, 100),
    "text":         (220, 220, 240),
    "text_dim":     (120, 120, 150),
    "btn":          (50,  55,  80),
    "btn_hover":    (80,  85, 120),
    "btn_active":   (60, 140, 220),
    "btn_text":     (220, 220, 240),
    "title":        (100, 200, 255),
    "success":      (50, 220, 120),
    "fail":         (240,  90,  80),
}

ALGO_MAP = {
    "BFS":           bfs,
    "DFS":           dfs,
    "UCS":           ucs,
    "DLS":           dls,
    "IDDFS":         iddfs,
    "Bidirectional": bidirectional,
}

PANEL_W = 220        # sidebar width (pixels)
FONT_SM = 14
FONT_MD = 17
FONT_LG = 22


class Button:
    def __init__(self, rect, label, active=False):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.active = active

    def draw(self, surface, font, hover=False):
        color = COLOR["btn_active"] if self.active else (COLOR["btn_hover"] if hover else COLOR["btn"])
        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        pygame.draw.rect(surface, COLOR["panel_border"], self.rect, 1, border_radius=6)
        txt = font.render(self.label, True, COLOR["btn_text"])
        surface.blit(txt, txt.get_rect(center=self.rect.center))

    def is_hovered(self, pos):
        return self.rect.collidepoint(pos)


class Visualizer:
    def __init__(self, grid: Grid, cell_size: int = 28):
        self.grid = grid
        self.cell_size = cell_size

        self.explored = []
        self.frontier = []
        self.path = []
        self.dynamic_spawned = []

        # State
        self.running_algo = False
        self.algo_gen = None
        self.current_algo = "BFS"
        self.status = "Ready"
        self.steps = 0
        self.nodes_explored = 0
        self.path_len = 0
        self.speed = 8   # steps per second
        self.dynamic_prob = 0.015
        self.draw_mode = "wall"   # "wall" or "erase"
        self.drag_drawing = False
        self.last_step_time = 0
        self.replanning = False

        # Layout
        self.grid_pixel_w = grid.cols * cell_size
        self.grid_pixel_h = grid.rows * cell_size
        self.win_w = self.grid_pixel_w + PANEL_W
        self.win_h = max(self.grid_pixel_h, 600)

        pygame.init()
        self.screen = pygame.display.set_mode((self.win_w, self.win_h))
        pygame.display.set_caption("GOOD PERFORMANCE TIME APP")

        self.font_sm = pygame.font.SysFont("segoeui", FONT_SM)
        self.font_md = pygame.font.SysFont("segoeui", FONT_MD)
        self.font_lg = pygame.font.SysFont("segoeui", FONT_LG, bold=True)
        self.font_title = pygame.font.SysFont("segoeui", 16, bold=True)

        self._build_buttons()

    # ------------------------------------------------------------------ #
    #  UI layout                                                            #
    # ------------------------------------------------------------------ #

    def _build_buttons(self):
        px = self.grid_pixel_w + 12
        self.algo_buttons = []
        for i, name in enumerate(ALGO_MAP):
            y = 80 + i * 44
            btn = Button((px, y, PANEL_W - 24, 36), name, active=(name == self.current_algo))
            self.algo_buttons.append(btn)

        bx = self.grid_pixel_w + 12
        by_base = 80 + len(ALGO_MAP) * 44 + 20

        self.btn_run   = Button((bx, by_base,      PANEL_W - 24, 36), "▶  Run")
        self.btn_step  = Button((bx, by_base + 44, PANEL_W - 24, 36), "⏭  Step")
        self.btn_reset = Button((bx, by_base + 88, PANEL_W - 24, 36), "↺  Reset")
        self.btn_clear = Button((bx, by_base + 132, PANEL_W - 24, 36), "✕  Clear Walls")

        self.btn_speed_up   = Button((bx,      by_base + 190, (PANEL_W - 36) // 2, 32), "Speed +")
        self.btn_speed_down = Button((bx + (PANEL_W - 36) // 2 + 12, by_base + 190, (PANEL_W - 36) // 2, 32), "Speed -")

        self.btn_wall_mode  = Button((bx,      by_base + 234, (PANEL_W - 36) // 2, 32), "Wall", active=True)
        self.btn_erase_mode = Button((bx + (PANEL_W - 36) // 2 + 12, by_base + 234, (PANEL_W - 36) // 2, 32), "Erase")

        self.all_buttons = (
            self.algo_buttons
            + [self.btn_run, self.btn_step, self.btn_reset, self.btn_clear,
               self.btn_speed_up, self.btn_speed_down,
               self.btn_wall_mode, self.btn_erase_mode]
        )

    # ------------------------------------------------------------------ #
    #  Cell drawing                                                         #
    # ------------------------------------------------------------------ #

    def _cell_rect(self, row, col):
        x = col * self.cell_size
        y = row * self.cell_size
        return pygame.Rect(x, y, self.cell_size - 1, self.cell_size - 1)

    def _draw_grid(self):
        explored_set = set(self.explored)
        frontier_set = set(self.frontier)
        path_set     = set(self.path)
        dynamic_set  = set(self.dynamic_spawned)

        for row in range(self.grid.rows):
            for col in range(self.grid.cols):
                rect = self._cell_rect(row, col)
                cell = self.grid.get_cell(row, col)
                pos = (row, col)

                if pos == self.grid.start_pos:
                    color = COLOR["start"]
                elif pos == self.grid.goal_pos:
                    color = COLOR["goal"]
                elif cell == Grid.WALL:
                    color = COLOR["wall"]
                elif cell == Grid.DYNAMIC_OBSTACLE:
                    color = COLOR["dynamic"]
                elif pos in path_set:
                    color = COLOR["path"]
                elif pos in explored_set:
                    color = COLOR["explored"]
                elif pos in frontier_set:
                    color = COLOR["frontier"]
                else:
                    color = COLOR["empty"]

                pygame.draw.rect(self.screen, color, rect, border_radius=2)

                # Labels for start / goal
                if pos == self.grid.start_pos:
                    lbl = self.font_title.render("S", True, (10, 10, 20))
                    self.screen.blit(lbl, lbl.get_rect(center=rect.center))
                elif pos == self.grid.goal_pos:
                    lbl = self.font_title.render("G", True, (10, 10, 20))
                    self.screen.blit(lbl, lbl.get_rect(center=rect.center))

    # ------------------------------------------------------------------ #
    #  Sidebar panel                                                        #
    # ------------------------------------------------------------------ #

    def _draw_panel(self):
        panel_rect = pygame.Rect(self.grid_pixel_w, 0, PANEL_W, self.win_h)
        pygame.draw.rect(self.screen, COLOR["panel_bg"], panel_rect)
        pygame.draw.line(self.screen, COLOR["panel_border"],
                         (self.grid_pixel_w, 0), (self.grid_pixel_w, self.win_h), 2)

        px = self.grid_pixel_w + 12
        # Title
        title = self.font_lg.render("GOOD PERFORMANCE", True, COLOR["title"])
        self.screen.blit(title, (px, 10))
        title2 = self.font_lg.render("TIME APP", True, COLOR["title"])
        self.screen.blit(title2, (px, 32))

        # Algo buttons
        algo_lbl = self.font_md.render("Algorithm:", True, COLOR["text"])
        self.screen.blit(algo_lbl, (px, 62))

        mouse_pos = pygame.mouse.get_pos()
        for btn in self.algo_buttons:
            btn.active = (btn.label == self.current_algo)
            btn.draw(self.screen, self.font_md, hover=btn.is_hovered(mouse_pos))

        # Action buttons
        by_base = 80 + len(ALGO_MAP) * 44 + 20
        self.btn_run.label = "⏸  Pause" if self.running_algo else "▶  Run"
        for btn in [self.btn_run, self.btn_step, self.btn_reset, self.btn_clear,
                    self.btn_speed_up, self.btn_speed_down]:
            btn.draw(self.screen, self.font_md, hover=btn.is_hovered(mouse_pos))

        self.btn_wall_mode.active  = (self.draw_mode == "wall")
        self.btn_erase_mode.active = (self.draw_mode == "erase")
        self.btn_wall_mode.draw(self.screen,  self.font_sm, hover=self.btn_wall_mode.is_hovered(mouse_pos))
        self.btn_erase_mode.draw(self.screen, self.font_sm, hover=self.btn_erase_mode.is_hovered(mouse_pos))

        # Stats
        stats_y = by_base + 280
        sep_color = COLOR["panel_border"]
        pygame.draw.line(self.screen, sep_color, (px, stats_y - 8), (self.grid_pixel_w + PANEL_W - 12, stats_y - 8))

        stats = [
            ("Algorithm",    self.current_algo),
            ("Steps",        str(self.steps)),
            ("Nodes Explored", str(self.nodes_explored)),
            ("Path Length",  str(self.path_len) if self.path_len else "—"),
            ("Speed",        f"{self.speed} sps"),
            ("Dyn. Prob.",   f"{self.dynamic_prob:.3f}"),
            ("Status",       self.status),
        ]
        for i, (key, val) in enumerate(stats):
            key_surf = self.font_sm.render(key + ":", True, COLOR["text_dim"])
            val_color = (
                COLOR["success"] if val == "Found!" else
                COLOR["fail"]    if val in ("No Path!", "Replanning…") else
                COLOR["text"]
            )
            val_surf = self.font_sm.render(val, True, val_color)
            self.screen.blit(key_surf, (px, stats_y + i * 24))
            self.screen.blit(val_surf, (px + 110, stats_y + i * 24))

        # Legend
        legend_y = stats_y + len(stats) * 24 + 16
        pygame.draw.line(self.screen, sep_color, (px, legend_y - 6), (self.grid_pixel_w + PANEL_W - 12, legend_y - 6))
        legend_items = [
            (COLOR["start"],    "Start"),
            (COLOR["goal"],     "Goal"),
            (COLOR["explored"], "Explored"),
            (COLOR["frontier"], "Frontier"),
            (COLOR["path"],     "Path"),
            (COLOR["wall"],     "Wall"),
            (COLOR["dynamic"],  "Dynamic Obs."),
        ]
        for i, (color, label) in enumerate(legend_items):
            pygame.draw.rect(self.screen, color, (px, legend_y + i * 22, 14, 14), border_radius=3)
            txt = self.font_sm.render(label, True, COLOR["text"])
            self.screen.blit(txt, (px + 20, legend_y + i * 22))

    # ------------------------------------------------------------------ #
    #  Algorithm stepping                                                   #
    # ------------------------------------------------------------------ #

    def _start_algo(self):
        if not self.grid.start_pos or not self.grid.goal_pos:
            self.status = "Set start/goal!"
            return
        self.explored = []
        self.frontier = []
        self.path = []
        self.dynamic_spawned = []
        self.steps = 0
        self.nodes_explored = 0
        self.path_len = 0
        self.status = "Running…"
        algo_fn = ALGO_MAP[self.current_algo]

        # DLS needs depth_limit; others take just grid, start, goal
        if self.current_algo == "DLS":
            self.algo_gen = algo_fn(self.grid, self.grid.start_pos, self.grid.goal_pos, depth_limit=15)
        elif self.current_algo == "IDDFS":
            self.algo_gen = algo_fn(self.grid, self.grid.start_pos, self.grid.goal_pos, max_depth=50)
        else:
            self.algo_gen = algo_fn(self.grid, self.grid.start_pos, self.grid.goal_pos)

    def _do_step(self):
        if self.algo_gen is None:
            self._start_algo()
            if self.algo_gen is None:
                return

        try:
            explored, frontier, path = next(self.algo_gen)
            self.explored = explored
            self.frontier = frontier
            self.steps += 1
            self.nodes_explored = len(explored)

            # Dynamic obstacle spawning
            spawned = self.grid.spawn_dynamic_obstacle(self.dynamic_prob)
            if spawned:
                self.dynamic_spawned.append(spawned)

                # Check if the new obstacle blocks planned path or next frontier node
                if path and path_blocked(path, self.grid):
                    self.status = "Replanning…"
                    self.replanning = True
                    self._start_algo()
                    return
                elif frontier and any(not self.grid.is_walkable(*f) for f in frontier[:3]):
                    self.status = "Replanning…"
                    self.replanning = True
                    self._start_algo()
                    return

            if path:
                self.path = path
                self.path_len = len(path)
                self.status = "Found!"
                self.running_algo = False
                self.algo_gen = None
            elif not frontier and not self.frontier:
                # Check if generator exhausted
                pass

        except StopIteration:
            if not self.path:
                self.status = "No Path!"
            self.running_algo = False
            self.algo_gen = None

    def _reset(self):
        self.grid.reset_search_state()
        self.explored = []
        self.frontier = []
        self.path = []
        self.dynamic_spawned = []
        self.steps = 0
        self.nodes_explored = 0
        self.path_len = 0
        self.status = "Ready"
        self.running_algo = False
        self.algo_gen = None
        self.replanning = False

    def _clear_walls(self):
        self._reset()
        for r in range(self.grid.rows):
            for c in range(self.grid.cols):
                if self.grid.grid[r][c] == Grid.WALL:
                    self.grid.grid[r][c] = Grid.EMPTY

    # ------------------------------------------------------------------ #
    #  Mouse / keyboard interaction                                         #
    # ------------------------------------------------------------------ #

    def _grid_cell_at(self, mouse_x, mouse_y):
        if mouse_x >= self.grid_pixel_w or mouse_y >= self.grid_pixel_h:
            return None
        col = mouse_x // self.cell_size
        row = mouse_y // self.cell_size
        if self.grid.is_valid(row, col):
            return row, col
        return None

    def _handle_grid_click(self, pos):
        cell = self._grid_cell_at(*pos)
        if cell is None:
            return
        row, col = cell
        if (row, col) in (self.grid.start_pos, self.grid.goal_pos):
            return
        if self.draw_mode == "wall":
            if self.grid.grid[row][col] != Grid.WALL:
                self.grid.grid[row][col] = Grid.WALL
        else:
            if self.grid.grid[row][col] == Grid.WALL:
                self.grid.grid[row][col] = Grid.EMPTY

    def _handle_button_click(self, pos):
        for btn in self.algo_buttons:
            if btn.is_hovered(pos):
                self.current_algo = btn.label
                self._reset()
                return
        if self.btn_run.is_hovered(pos):
            if self.running_algo:
                self.running_algo = False
                self.status = "Paused"
            else:
                if self.algo_gen is None:
                    self._start_algo()
                self.running_algo = True
                self.status = "Running…"
        elif self.btn_step.is_hovered(pos):
            self.running_algo = False
            if self.algo_gen is None:
                self._start_algo()
            self._do_step()
        elif self.btn_reset.is_hovered(pos):
            self._reset()
        elif self.btn_clear.is_hovered(pos):
            self._clear_walls()
        elif self.btn_speed_up.is_hovered(pos):
            self.speed = min(60, self.speed + 2)
        elif self.btn_speed_down.is_hovered(pos):
            self.speed = max(1, self.speed - 2)
        elif self.btn_wall_mode.is_hovered(pos):
            self.draw_mode = "wall"
        elif self.btn_erase_mode.is_hovered(pos):
            self.draw_mode = "erase"

    # ------------------------------------------------------------------ #
    #  Public helpers (for main.py compatibility)                          #
    # ------------------------------------------------------------------ #

    def update_explored(self, explored):
        self.explored = explored

    def update_frontier(self, frontier):
        self.frontier = frontier

    def refresh(self):
        self.screen.fill(COLOR["bg"])
        self._draw_grid()
        self._draw_panel()
        pygame.display.flip()

    def wait_for_close(self):
        """Legacy helper: block until the window is closed."""
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.refresh()
            clock.tick(30)

    # ------------------------------------------------------------------ #
    #  Main loop                                                            #
    # ------------------------------------------------------------------ #

    def run(self):
        clock = pygame.time.Clock()

        while True:
            now = time.time()
            mouse_pos = pygame.mouse.get_pos()

            # ---- Events ----
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self._handle_button_click(self.btn_run.rect.center)
                    elif event.key == pygame.K_r:
                        self._reset()
                    elif event.key == pygame.K_RIGHT:
                        if not self.running_algo:
                            if self.algo_gen is None:
                                self._start_algo()
                            self._do_step()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if event.pos[0] < self.grid_pixel_w:
                            self.drag_drawing = True
                            self._handle_grid_click(event.pos)
                        else:
                            self._handle_button_click(event.pos)
                    elif event.button == 3:
                        # Right-click erases walls
                        cell = self._grid_cell_at(*event.pos)
                        if cell:
                            r, c = cell
                            if self.grid.grid[r][c] == Grid.WALL:
                                self.grid.grid[r][c] = Grid.EMPTY

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.drag_drawing = False

                elif event.type == pygame.MOUSEMOTION:
                    if self.drag_drawing and event.pos[0] < self.grid_pixel_w:
                        self._handle_grid_click(event.pos)

            # ---- Algorithm step ----
            if self.running_algo and self.algo_gen is not None:
                step_interval = 1.0 / self.speed
                if now - self.last_step_time >= step_interval:
                    self._do_step()
                    self.last_step_time = now

            # ---- Render ----
            self.screen.fill(COLOR["bg"])
            self._draw_grid()
            self._draw_panel()
            pygame.display.flip()
            clock.tick(60)
