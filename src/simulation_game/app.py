# flake8: noqa
from __future__ import annotations

import json
import math
import random
import tkinter as tk
from dataclasses import dataclass
from tkinter import filedialog, ttk
from typing import Callable


@dataclass
class Cell:
    plant: float = 20.0
    prey: float = 8.0
    predator: float = 3.0

    plant_growth: float = 1.9
    plant_nutrition: float = 0.20
    hunt_success: float = 0.08
    prey_death_rate: float = 0.04
    predator_death_rate: float = 0.03

    max_plant: float = 100.0
    max_prey: float = 50.0
    max_predator: float = 30.0

    def clamp_non_negative(self) -> None:
        self.plant = max(0.0, self.plant)
        self.prey = max(0.0, self.prey)
        self.predator = max(0.0, self.predator)


class HexSimulation:
    def __init__(self, rows: int, cols: int) -> None:
        self.rows = rows
        self.cols = cols
        self.grid: list[list[Cell]] = [[Cell() for _ in range(cols)] for _ in range(rows)]
        self.edges: dict[tuple[tuple[int, int], tuple[int, int]], float] = {}
        self._init_edges(1.0)

    def _init_edges(self, traversability: float) -> None:
        self.edges.clear()
        for r in range(self.rows):
            for c in range(self.cols):
                for nr, nc in self.neighbors(r, c):
                    key = self.edge_key((r, c), (nr, nc))
                    if key not in self.edges:
                        self.edges[key] = traversability

    @staticmethod
    def edge_key(a: tuple[int, int], b: tuple[int, int]) -> tuple[tuple[int, int], tuple[int, int]]:
        return (a, b) if a <= b else (b, a)

    def in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < self.rows and 0 <= c < self.cols

    def neighbors(self, r: int, c: int) -> list[tuple[int, int]]:
        if r % 2 == 0:
            directions = [(-1, -1), (-1, 0), (0, -1), (0, 1), (1, -1), (1, 0)]
        else:
            directions = [(-1, 0), (-1, 1), (0, -1), (0, 1), (1, 0), (1, 1)]
        result: list[tuple[int, int]] = []
        for dr, dc in directions:
            nr = r + dr
            nc = c + dc
            if self.in_bounds(nr, nc):
                result.append((nr, nc))
        return result

    def traversability(self, a: tuple[int, int], b: tuple[int, int]) -> float:
        return self.edges.get(self.edge_key(a, b), 0.0)

    def set_traversability(self, a: tuple[int, int], b: tuple[int, int], value: float) -> None:
        if not self.in_bounds(*a) or not self.in_bounds(*b):
            return
        if b not in self.neighbors(*a):
            return
        self.edges[self.edge_key(a, b)] = max(0.0, min(1.0, value))

    def clear_map(self) -> None:
        for row in self.grid:
            for cell in row:
                cell.plant = 0.0
                cell.prey = 0.0
                cell.predator = 0.0
        self._init_edges(1.0)

    def randomize(self) -> None:
        for row in self.grid:
            for cell in row:
                cell.max_plant = random.uniform(70.0, 150.0)
                cell.max_prey = random.uniform(30.0, 70.0)
                cell.max_predator = random.uniform(15.0, 45.0)

                cell.plant_growth = random.uniform(1.0, 1.08)
                cell.plant_nutrition = random.uniform(0.03, 0.22)
                cell.hunt_success = random.uniform(0.03, 0.25)
                cell.prey_death_rate = random.uniform(0.01, 0.12)
                cell.predator_death_rate = random.uniform(0.01, 0.12)

                cell.plant = random.uniform(0.0, cell.max_plant)
                cell.prey = random.uniform(0.0, cell.max_prey)
                cell.predator = random.uniform(0.0, cell.max_predator)

        for key in list(self.edges):
            self.edges[key] = random.uniform(0.0, 1.0)

    def tick(self) -> None:
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]

                # plants growth
                cell.plant *= max(0.0, cell.plant_growth)

                # plants eaten by prey
                plants_devoured = cell.prey / cell.plant_nutrition
                cell.plant -= plants_devoured

                # prey death
                cell.prey *= max(0.0, 1.0 - cell.prey_death_rate)

                # prey changed by available plants (negative if not enough plants to eat)
                cell.prey += cell.plant * cell.plant_nutrition

                # predeator death
                cell.predator *= max(0.0, 1.0 - cell.predator_death_rate)

                # predators eat prey
                prey_devoured = cell.predator * cell.hunt_success
                cell.prey -= prey_devoured

                # number of predator change
                cell.predator = cell.prey * cell.hunt_success
                
                cell.clamp_non_negative()

        self._apply_overflow("plant", "max_plant", rounds=2)
        self._apply_overflow("prey", "max_prey", rounds=2)
        self._apply_overflow("predator", "max_predator", rounds=2)

    def to_dict(self) -> dict[str, object]:
        return {
            "rows": self.rows,
            "cols": self.cols,
            "cells": [[cell.__dict__.copy() for cell in row] for row in self.grid],
            "edges": [
                {
                    "a": [a[0], a[1]],
                    "b": [b[0], b[1]],
                    "traversability": value,
                }
                for (a, b), value in self.edges.items()
            ],
        }

    def load_dict(self, payload: dict[str, object]) -> None:
        rows_raw = payload.get("rows")
        cols_raw = payload.get("cols")
        if not isinstance(rows_raw, (int, float, str)):
            raise ValueError("Invalid row count")
        if not isinstance(cols_raw, (int, float, str)):
            raise ValueError("Invalid column count")

        rows = int(rows_raw)
        cols = int(cols_raw)
        cells = payload["cells"]
        edges = payload["edges"]

        if not isinstance(cells, list) or len(cells) != rows:
            raise ValueError("Invalid cell payload dimensions")

        new_grid: list[list[Cell]] = []
        for row in cells:
            if not isinstance(row, list) or len(row) != cols:
                raise ValueError("Invalid cell row dimensions")

            new_row: list[Cell] = []
            for item in row:
                if not isinstance(item, dict):
                    raise ValueError("Invalid cell payload entry")

                new_row.append(
                    Cell(
                        plant=float(item.get("plant", 0.0)),
                        prey=float(item.get("prey", 0.0)),
                        predator=float(item.get("predator", 0.0)),
                        plant_growth=float(item.get("plant_growth", 1.0)),
                        plant_nutrition=float(item.get("plant_nutrition", 0.0)),
                        hunt_success=float(item.get("hunt_success", 0.0)),
                        prey_death_rate=float(item.get("prey_death_rate", 0.0)),
                        predator_death_rate=float(
                            item.get("predator_death_rate", 0.0)
                        ),
                        max_plant=max(0.01, float(item.get("max_plant", 1.0))),
                        max_prey=max(0.01, float(item.get("max_prey", 1.0))),
                        max_predator=max(0.01, float(item.get("max_predator", 1.0))),
                    )
                )
            new_grid.append(new_row)

        new_edges: dict[tuple[tuple[int, int], tuple[int, int]], float] = {}
        if not isinstance(edges, list):
            raise ValueError("Invalid edge payload")

        for item in edges:
            if not isinstance(item, dict):
                continue
            a_raw = item.get("a")
            b_raw = item.get("b")
            trv = float(item.get("traversability", 1.0))
            if not isinstance(a_raw, list) or not isinstance(b_raw, list):
                continue
            if len(a_raw) != 2 or len(b_raw) != 2:
                continue
            a = (int(a_raw[0]), int(a_raw[1]))
            b = (int(b_raw[0]), int(b_raw[1]))
            if not (0 <= a[0] < rows and 0 <= a[1] < cols):
                continue
            if not (0 <= b[0] < rows and 0 <= b[1] < cols):
                continue

            key = self.edge_key(a, b)
            new_edges[key] = max(0.0, min(1.0, trv))

        self.rows = rows
        self.cols = cols
        self.grid = new_grid
        self.edges = {}
        self._init_edges(1.0)
        for key, value in new_edges.items():
            if key in self.edges:
                self.edges[key] = value

    def _apply_overflow(self, value_attr: str, max_attr: str, rounds: int = 1) -> None:
        for _ in range(rounds):
            deltas: dict[tuple[int, int], float] = {}
            changed = False

            for r in range(self.rows):
                for c in range(self.cols):
                    cell = self.grid[r][c]
                    value = getattr(cell, value_attr)
                    maximum = getattr(cell, max_attr)

                    if value <= maximum:
                        continue

                    overflow = value - maximum
                    weighted_neighbors: list[tuple[tuple[int, int], float]] = []
                    total_weight = 0.0
                    for nr, nc in self.neighbors(r, c):
                        trv = self.traversability((r, c), (nr, nc))
                        if trv <= 0.0:
                            continue
                        weighted_neighbors.append(((nr, nc), trv))
                        total_weight += trv

                    if total_weight <= 0.0:
                        continue

                    setattr(cell, value_attr, maximum)
                    changed = True
                    for (nr, nc), weight in weighted_neighbors:
                        share = overflow * (weight / total_weight)
                        deltas[(nr, nc)] = deltas.get((nr, nc), 0.0) + share

            for (r, c), add in deltas.items():
                cell = self.grid[r][c]
                setattr(cell, value_attr, getattr(cell, value_attr) + add)

            if not changed:
                break


class HexSimulationApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("The Simulation Game")

        self.model = HexSimulation(rows=10, cols=12)
        self.hex_size = 28.0
        self.margin = 38.0

        self.show_numbers = tk.BooleanVar(value=False)
        self.running = False
        self.dragging = False
        self.long_press_id: str | None = None

        self.tool_var = tk.StringVar(value="spawn_plant")
        self.value_var = tk.StringVar(value="10")
        self.speed_var = tk.DoubleVar(value=4.0)
        self.info_var = tk.StringVar(value="Hover over a cell to inspect details.")

        self.cell_centers: dict[tuple[int, int], tuple[float, float]] = {}
        self.cell_polygons: dict[tuple[int, int], int] = {}
        self.tick_count = 0
        self.history_limit = 200
        self.cell_history: dict[tuple[int, int], list[tuple[int, float, float, float]]] = {}
        self.history_windows: dict[tuple[int, int], tuple[tk.Toplevel, tk.Canvas]] = {}

        self._reset_histories()

        self._build_ui()
        self._redraw_all()
        self._schedule_loop()

    def _build_ui(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        frame = ttk.Frame(self.root, padding=8)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(frame, bg="#10281d", width=980, height=680, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<Double-Button-1>", self._on_double_click)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<Motion>", self._on_hover)

        controls = ttk.Frame(frame, padding=(10, 4, 6, 6))
        controls.grid(row=0, column=1, sticky="ns")

        ttk.Label(controls, text="Simulation", font=("Segoe UI", 11, "bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 6)
        )

        self.pause_btn = ttk.Button(controls, text="Pause", command=self._toggle_running)
        self.pause_btn.grid(row=1, column=0, sticky="ew", pady=2)

        ttk.Button(controls, text="Single Step", command=self._single_step).grid(
            row=2, column=0, sticky="ew", pady=2
        )

        ttk.Label(controls, text="Speed (ticks/sec)").grid(row=3, column=0, sticky="w", pady=(8, 0))
        ttk.Scale(controls, from_=0.5, to=20.0, variable=self.speed_var, orient="horizontal").grid(
            row=4, column=0, sticky="ew"
        )

        ttk.Button(controls, text="Toggle Circles/Numbers", command=self._toggle_mode).grid(
            row=5, column=0, sticky="ew", pady=(8, 2)
        )
        ttk.Button(controls, text="Clear Map", command=self._clear_map).grid(
            row=6, column=0, sticky="ew", pady=2
        )
        ttk.Button(controls, text="Random Map", command=self._random_map).grid(
            row=7, column=0, sticky="ew", pady=2
        )
        ttk.Button(controls, text="Save Map", command=self._save_map).grid(
            row=8, column=0, sticky="ew", pady=(8, 2)
        )
        ttk.Button(controls, text="Load Map", command=self._load_map).grid(
            row=9, column=0, sticky="ew", pady=2
        )

        ttk.Separator(controls, orient="horizontal").grid(
            row=10, column=0, sticky="ew", pady=8
        )

        ttk.Label(controls, text="Edit Tool", font=("Segoe UI", 10, "bold")).grid(
            row=11, column=0, sticky="w", pady=(0, 4)
        )

        tools = [
            "spawn_plant",
            "spawn_prey",
            "spawn_predator",
            "set_plant",
            "set_prey",
            "set_predator",
            "set_plant_growth",
            "set_plant_nutrition",
            "set_hunt_success",
            "set_prey_death_rate",
            "set_predator_death_rate",
            "set_max_plant",
            "set_max_prey",
            "set_max_predator",
            "set_edge_traversability",
        ]

        ttk.Combobox(controls, textvariable=self.tool_var, values=tools, state="readonly").grid(
            row=12, column=0, sticky="ew"
        )

        ttk.Label(controls, text="Tool Value").grid(row=13, column=0, sticky="w", pady=(6, 0))
        ttk.Entry(controls, textvariable=self.value_var).grid(row=14, column=0, sticky="ew")
        ttk.Label(
            controls,
            text="Click or drag to apply to cells.\nFor edges, click between two neighbors.",
            foreground="#444",
            justify="left",
        ).grid(row=15, column=0, sticky="w", pady=(4, 0))

        ttk.Separator(controls, orient="horizontal").grid(
            row=16, column=0, sticky="ew", pady=8
        )
        ttk.Label(controls, text="Legend", font=("Segoe UI", 10, "bold")).grid(
            row=17, column=0, sticky="w"
        )
        ttk.Label(controls, text="Green circle: Plant matter").grid(
            row=18, column=0, sticky="w"
        )
        ttk.Label(controls, text="Gold circle: Prey animals").grid(
            row=19, column=0, sticky="w"
        )
        ttk.Label(controls, text="Red circle: Predator animals").grid(
            row=20, column=0, sticky="w"
        )
        ttk.Label(controls, text="Edge color: Traversability (dim -> white)").grid(
            row=21, column=0, sticky="w", pady=(0, 6)
        )

        ttk.Label(controls, text="Details", font=("Segoe UI", 10, "bold")).grid(
            row=22, column=0, sticky="w"
        )
        info = ttk.Label(controls, textvariable=self.info_var, justify="left", wraplength=270)
        info.grid(row=23, column=0, sticky="ew")

    def _hex_points(self, cx: float, cy: float) -> list[float]:
        points: list[float] = []
        for i in range(6):
            angle = math.radians(60 * i - 30)
            points.extend([cx + self.hex_size * math.cos(angle), cy + self.hex_size * math.sin(angle)])
        return points

    def _center_for(self, r: int, c: int) -> tuple[float, float]:
        x = self.margin + self.hex_size * math.sqrt(3.0) * (c + 0.5 * (r % 2))
        y = self.margin + self.hex_size * 1.5 * r
        return x, y

    def _shared_edge_segment(
        self, a: tuple[int, int], b: tuple[int, int]
    ) -> tuple[float, float, float, float]:
        ax, ay = self._center_for(*a)
        bx, by = self._center_for(*b)

        dx = bx - ax
        dy = by - ay
        dist = math.hypot(dx, dy)
        if dist <= 1e-9:
            return ax, ay, ax, ay

        nx = dx / dist
        ny = dy / dist

        # Side midpoint is one apothem away from center in neighbor direction.
        apothem = self.hex_size * math.cos(math.radians(30.0))
        mx = ax + nx * apothem
        my = ay + ny * apothem

        tx = -ny
        ty = nx
        half_side = self.hex_size / 2.0

        x1 = mx + tx * half_side
        y1 = my + ty * half_side
        x2 = mx - tx * half_side
        y2 = my - ty * half_side
        return x1, y1, x2, y2

    def _iter_edges_once(self) -> list[tuple[tuple[int, int], tuple[int, int], float]]:
        result: list[tuple[tuple[int, int], tuple[int, int], float]] = []
        for (a, b), value in self.model.edges.items():
            result.append((a, b, value))
        return result

    def _traversability_color(self, value: float) -> str:
        value = max(0.0, min(1.0, value))
        base = (16, 40, 29)
        white = (255, 255, 255)
        r = int(base[0] + (white[0] - base[0]) * value)
        g = int(base[1] + (white[1] - base[1]) * value)
        b = int(base[2] + (white[2] - base[2]) * value)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _redraw_all(self) -> None:
        self.canvas.delete("all")
        self.cell_centers.clear()
        self.cell_polygons.clear()

        for r in range(self.model.rows):
            for c in range(self.model.cols):
                cx, cy = self._center_for(r, c)
                self.cell_centers[(r, c)] = (cx, cy)
                pts = self._hex_points(cx, cy)
                tag = f"cell-{r}-{c}"
                poly = self.canvas.create_polygon(
                    pts,
                    fill="#193d2b",
                    outline="#2f684b",
                    width=1,
                    tags=("cell", tag),
                )
                self.cell_polygons[(r, c)] = poly
                self._draw_cell_data(r, c, tag)

        # Draw traversability directly on shared hex edges.
        for (a, b, trv) in self._iter_edges_once():
            x1, y1, x2, y2 = self._shared_edge_segment(a, b)
            self.canvas.create_line(
                x1,
                y1,
                x2,
                y2,
                fill=self._traversability_color(trv),
                width=4,
                capstyle=tk.ROUND,
                tags=("edge",),
            )

    def _draw_cell_data(self, r: int, c: int, tag: str) -> None:
        cell = self.model.grid[r][c]
        cx, cy = self.cell_centers[(r, c)]

        if self.show_numbers.get():
            text = (
                f"pl {cell.plant:.0f}\n"
                f"pr {cell.prey:.0f}\n"
                f"pd {cell.predator:.0f}"
            )
            self.canvas.create_text(
                cx,
                cy,
                text=text,
                fill="#e8f5ee",
                font=("Consolas", 9, "bold"),
                tags=(tag,),
            )
            return

        ratios = [
            (cell.plant / max(cell.max_plant, 1e-6), "#62d96b", (-11.0, -8.0)),
            (cell.prey / max(cell.max_prey, 1e-6), "#f2cf4a", (11.0, -8.0)),
            (cell.predator / max(cell.max_predator, 1e-6), "#e05b5b", (0.0, 11.0)),
        ]

        for ratio, color, (ox, oy) in ratios:
            radius = 2.5 + 8.5 * max(0.0, min(1.0, ratio))
            self.canvas.create_oval(
                cx + ox - radius,
                cy + oy - radius,
                cx + ox + radius,
                cy + oy + radius,
                fill=color,
                outline="#0f2018",
                width=1,
                tags=(tag,),
            )

    def _get_cell_from_event(self, event: tk.Event) -> tuple[int, int] | None:
        item_ids = self.canvas.find_withtag("current")
        if not item_ids:
            return None

        item_id = item_ids[0]
        for tag in self.canvas.gettags(item_id):
            if tag.startswith("cell-"):
                _, rs, cs = tag.split("-")
                return int(rs), int(cs)
        return None

    def _find_neighbor_pair_for_edge_edit(self, x: float, y: float) -> tuple[tuple[int, int], tuple[int, int]] | None:
        distances: list[tuple[float, tuple[int, int]]] = []
        for coord, (cx, cy) in self.cell_centers.items():
            d2 = (x - cx) ** 2 + (y - cy) ** 2
            distances.append((d2, coord))
        distances.sort(key=lambda item: item[0])
        if len(distances) < 2:
            return None

        a = distances[0][1]
        b = distances[1][1]
        if b not in self.model.neighbors(*a):
            return None

        ax, ay = self.cell_centers[a]
        bx, by = self.cell_centers[b]
        mx = 0.5 * (ax + bx)
        my = 0.5 * (ay + by)
        if (x - mx) ** 2 + (y - my) ** 2 > (self.hex_size * 0.95) ** 2:
            return None

        return a, b

    def _get_numeric_input(self) -> float | None:
        try:
            return float(self.value_var.get().strip())
        except ValueError:
            self.info_var.set("Invalid numeric value in Tool Value.")
            return None

    def _apply_tool_to_cell(self, r: int, c: int) -> None:
        value = self._get_numeric_input()
        if value is None:
            return

        cell = self.model.grid[r][c]
        tool = self.tool_var.get()

        direct_map = {
            "set_plant": "plant",
            "set_prey": "prey",
            "set_predator": "predator",
            "set_plant_growth": "plant_growth",
            "set_plant_nutrition": "plant_nutrition",
            "set_hunt_success": "hunt_success",
            "set_prey_death_rate": "prey_death_rate",
            "set_predator_death_rate": "predator_death_rate",
            "set_max_plant": "max_plant",
            "set_max_prey": "max_prey",
            "set_max_predator": "max_predator",
        }

        if tool in direct_map:
            attr = direct_map[tool]
            if "rate" in attr or attr in {"plant_nutrition", "hunt_success"}:
                value = max(0.0, min(1.0, value))
            elif attr.startswith("max_"):
                value = max(0.01, value)
            else:
                value = max(0.0, value)
            setattr(cell, attr, value)
        elif tool == "spawn_plant":
            cell.plant = max(0.0, cell.plant + value)
        elif tool == "spawn_prey":
            cell.prey = max(0.0, cell.prey + value)
        elif tool == "spawn_predator":
            cell.predator = max(0.0, cell.predator + value)

        cell.clamp_non_negative()

    def _apply_tool(self, event: tk.Event) -> None:
        tool = self.tool_var.get()

        if tool == "set_edge_traversability":
            value = self._get_numeric_input()
            if value is None:
                return
            pair = self._find_neighbor_pair_for_edge_edit(event.x, event.y)
            if pair is None:
                return
            a, b = pair
            self.model.set_traversability(a, b, value)
            self._update_info_for_cell(a[0], a[1])
            self._redraw_all()
            return

        cell_coord = self._get_cell_from_event(event)
        if cell_coord is None:
            return

        r, c = cell_coord
        self._apply_tool_to_cell(r, c)
        self._record_cell_history(r, c)
        self._update_info_for_cell(r, c)
        self._redraw_all()

    def _on_press(self, event: tk.Event) -> None:
        self.dragging = True
        self._apply_tool(event)

        cell_coord = self._get_cell_from_event(event)
        if cell_coord is not None:
            self._start_long_press(cell_coord)

    def _on_drag(self, event: tk.Event) -> None:
        self._cancel_long_press()
        self._apply_tool(event)

    def _on_double_click(self, event: tk.Event) -> None:
        cell_coord = self._get_cell_from_event(event)
        if cell_coord is None:
            return
        self._show_history_window(cell_coord)

    def _on_release(self, _event: tk.Event) -> None:
        self.dragging = False
        self._cancel_long_press()

    def _on_hover(self, event: tk.Event) -> None:
        if self.dragging:
            return
        cell_coord = self._get_cell_from_event(event)
        if cell_coord is None:
            return
        self._update_info_for_cell(*cell_coord)

    def _start_long_press(self, coord: tuple[int, int]) -> None:
        self._cancel_long_press()

        def show_info() -> None:
            self._update_info_for_cell(*coord)
            self.long_press_id = None

        self.long_press_id = self.root.after(600, show_info)

    def _cancel_long_press(self) -> None:
        if self.long_press_id is not None:
            self.root.after_cancel(self.long_press_id)
            self.long_press_id = None

    def _update_info_for_cell(self, r: int, c: int) -> None:
        cell = self.model.grid[r][c]
        edge_parts = []
        for nr, nc in self.model.neighbors(r, c):
            trv = self.model.traversability((r, c), (nr, nc))
            edge_parts.append(f"({nr},{nc})={trv:.2f}")

        self.info_var.set(
            "\n".join(
                [
                    f"Cell ({r}, {c})",
                    f"plant={cell.plant:.2f}, prey={cell.prey:.2f}, predator={cell.predator:.2f}",
                    (
                        "growth={:.2f}, nutrition={:.2f}, hunt={:.2f}, "
                        "prey_death={:.2f}, predator_death={:.2f}"
                    ).format(
                        cell.plant_growth,
                        cell.plant_nutrition,
                        cell.hunt_success,
                        cell.prey_death_rate,
                        cell.predator_death_rate,
                    ),
                    f"max_plant={cell.max_plant:.2f}, max_prey={cell.max_prey:.2f}, max_predator={cell.max_predator:.2f}",
                    "edges: " + ", ".join(edge_parts),
                ]
            )
        )

    def _toggle_running(self) -> None:
        self.running = not self.running
        self.pause_btn.configure(text="Pause" if self.running else "Resume")

    def _toggle_mode(self) -> None:
        self.show_numbers.set(not self.show_numbers.get())
        self._redraw_all()

    def _single_step(self) -> None:
        self.model.tick()
        self.tick_count += 1
        self._record_all_histories()
        self._redraw_all()

    def _clear_map(self) -> None:
        self.model.clear_map()
        self.running = False
        self.pause_btn.configure(text="Resume")
        self.info_var.set("Map cleared: all plant, prey, and predator values set to 0.")
        self.tick_count += 1
        self._record_all_histories()
        self._redraw_all()

    def _random_map(self) -> None:
        self.model.randomize()
        self.tick_count += 1
        self._record_all_histories()
        self._redraw_all()

    def _save_map(self) -> None:
        file_path = filedialog.asksaveasfilename(
            title="Save Simulation Map",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not file_path:
            return

        payload = self.model.to_dict()
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            self.info_var.set(f"Map saved: {file_path}")
        except OSError as exc:
            self.info_var.set(f"Failed to save map: {exc}")

    def _load_map(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Load Simulation Map",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                payload = json.load(f)
            if not isinstance(payload, dict):
                raise ValueError("Invalid map format")
            self.model.load_dict(payload)
            self._reset_histories()
            self._redraw_all()
            self.info_var.set(f"Map loaded: {file_path}")
        except (OSError, ValueError, KeyError, TypeError) as exc:
            self.info_var.set(f"Failed to load map: {exc}")

    def _schedule_loop(self) -> None:
        self._tick_loop()

    def _tick_loop(self) -> None:
        if self.running:
            self.model.tick()
            self.tick_count += 1
            self._record_all_histories()
            self._redraw_all()

        speed = max(0.5, float(self.speed_var.get()))
        delay_ms = int(1000.0 / speed)
        self.root.after(delay_ms, self._tick_loop)

    def _reset_histories(self) -> None:
        self.tick_count = 0
        self.cell_history.clear()
        self._record_all_histories()

    def _record_cell_history(self, r: int, c: int) -> None:
        cell = self.model.grid[r][c]
        key = (r, c)
        if key not in self.cell_history:
            self.cell_history[key] = []
        self.cell_history[key].append((self.tick_count, cell.plant, cell.prey, cell.predator))

        # Keep only the last N ticks of history for each cell.
        min_tick = self.tick_count - self.history_limit + 1
        self.cell_history[key] = [
            sample for sample in self.cell_history[key] if sample[0] >= min_tick
        ]

        if key in self.history_windows:
            self._redraw_history_graph(key)

    def _record_all_histories(self) -> None:
        for r in range(self.model.rows):
            for c in range(self.model.cols):
                self._record_cell_history(r, c)

    def _show_history_window(self, coord: tuple[int, int]) -> None:
        existing = self.history_windows.get(coord)
        if existing is None or not existing[0].winfo_exists():
            window = tk.Toplevel(self.root)
            window.title(f"Cell History ({coord[0]}, {coord[1]})")
            window.geometry("620x360")
            canvas = tk.Canvas(
                window,
                bg="#111a15",
                highlightthickness=0,
            )
            canvas.pack(fill="both", expand=True)
            window.bind(
                "<Configure>",
                lambda _event, cell=coord: self._on_history_resize(cell),
            )
            window.bind(
                "<Destroy>",
                lambda _event, cell=coord: self._on_history_window_closed(cell),
            )
            self.history_windows[coord] = (window, canvas)

        self._redraw_history_graph(coord)
        self.history_windows[coord][0].lift()

    def _on_history_window_closed(self, coord: tuple[int, int]) -> None:
        existing = self.history_windows.get(coord)
        if existing is not None and not existing[0].winfo_exists():
            self.history_windows.pop(coord, None)

    def _on_history_resize(self, coord: tuple[int, int]) -> None:
        self._redraw_history_graph(coord)

    def _redraw_history_graph(self, coord: tuple[int, int]) -> None:
        existing = self.history_windows.get(coord)
        if existing is None:
            return
        history_canvas = existing[1]
        if not history_canvas.winfo_exists():
            self.history_windows.pop(coord, None)
            return

        history = self.cell_history.get(coord, [])
        history_canvas.delete("all")

        width = max(100, history_canvas.winfo_width())
        height = max(100, history_canvas.winfo_height())

        left = 50
        top = 35
        right = width - 20
        bottom = height - 35

        history_canvas.create_rectangle(
            left,
            top,
            right,
            bottom,
            outline="#3f5d4f",
            width=1,
        )

        history_canvas.create_text(
            left,
            18,
            anchor="w",
            fill="#eaf5ef",
            font=("Segoe UI", 10, "bold"),
            text=f"History for cell ({coord[0]}, {coord[1]})",
        )

        legend = [
            ("Plant", "#62d96b"),
            ("Prey", "#f2cf4a"),
            ("Predator", "#e05b5b"),
        ]
        legend_x = right - 170
        for i, (label, color) in enumerate(legend):
            y = 18 + i * 14
            history_canvas.create_line(
                legend_x,
                y,
                legend_x + 16,
                y,
                fill=color,
                width=3,
            )
            history_canvas.create_text(
                legend_x + 22,
                y,
                anchor="w",
                fill="#d9e9df",
                font=("Segoe UI", 9),
                text=label,
            )

        if len(history) < 2:
            history_canvas.create_text(
                (left + right) / 2,
                (top + bottom) / 2,
                fill="#cddad2",
                font=("Segoe UI", 10),
                text="Not enough history yet. Run the simulation or edit the cell.",
            )
            return

        times = [p[0] for p in history]
        plants = [p[1] for p in history]
        preys = [p[2] for p in history]
        predators = [p[3] for p in history]

        all_values = plants + preys + predators
        y_max = max(1.0, max(all_values))
        y_min = 0.0
        x_min = float(min(times))
        x_max = float(max(times))
        if x_max <= x_min:
            x_max = x_min + 1.0

        def to_xy(tick: int, value: float) -> tuple[float, float]:
            x = left + (right - left) * ((tick - x_min) / (x_max - x_min))
            y = bottom - (bottom - top) * ((value - y_min) / (y_max - y_min))
            return x, y

        for y_div in range(5):
            y = top + (bottom - top) * (y_div / 4.0)
            history_canvas.create_line(left, y, right, y, fill="#1d2d25", width=1)
            value = y_max * (1.0 - y_div / 4.0)
            history_canvas.create_text(
                left - 8,
                y,
                anchor="e",
                fill="#bfd2c5",
                font=("Segoe UI", 8),
                text=f"{value:.0f}",
            )

        self._draw_series_line(history_canvas, times, plants, "#62d96b", to_xy)
        self._draw_series_line(history_canvas, times, preys, "#f2cf4a", to_xy)
        self._draw_series_line(history_canvas, times, predators, "#e05b5b", to_xy)

        history_canvas.create_text(
            right,
            bottom + 16,
            anchor="e",
            fill="#bfd2c5",
            font=("Segoe UI", 8),
            text=f"ticks {int(x_min)} - {int(x_max)}",
        )

    def _draw_series_line(
        self,
        history_canvas: tk.Canvas,
        ticks: list[int],
        values: list[float],
        color: str,
        mapper: Callable[[int, float], tuple[float, float]],
    ) -> None:
        points: list[float] = []
        for tick, value in zip(ticks, values):
            x, y = mapper(tick, value)
            points.extend([x, y])
        if len(points) >= 4:
            history_canvas.create_line(
                *points,
                fill=color,
                width=2,
                smooth=True,
            )


def main() -> None:
    root = tk.Tk()
    app = HexSimulationApp(root)
    app.running = True
    app.pause_btn.configure(text="Pause")
    root.mainloop()


if __name__ == "__main__":
    main()
