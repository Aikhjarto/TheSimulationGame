import csv
import random
from pathlib import Path
from typing import Sequence

import matplotlib.pyplot as plt

from simulation_game.Cell import Cell


class HexSimulation:
    def __init__(
        self, rows: int, cols: int, initial_cells: Sequence[Cell] = ()
    ) -> None:
        self.rows = rows
        self.cols = cols
        self.grid: list[list[Cell]] = [
            [Cell() for _ in range(cols)] for _ in range(rows)
        ]
        if initial_cells:
            for i, cell in enumerate(initial_cells):
                r = i // cols
                c = i % cols
                self.grid[r][c].__dict__.update(cell.__dict__)
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
    def edge_key(
        a: tuple[int, int], b: tuple[int, int]
    ) -> tuple[tuple[int, int], tuple[int, int]]:
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

    def set_traversability(
        self, a: tuple[int, int], b: tuple[int, int], value: float
    ) -> None:
        if not self.in_bounds(*a) or not self.in_bounds(*b):
            return
        if b not in self.neighbors(*a):
            return
        self.edges[self.edge_key(a, b)] = max(0.0, min(1.0, value))

    def clear_map(self) -> None:
        for row in self.grid:
            for cell in row:
                cell.plant = 0.0
                cell.grazer = 0.0
                cell.predator = 0.0
        self._init_edges(1.0)

    def randomize(self) -> None:
        for row in self.grid:
            for cell in row:
                cell.max_plant = random.uniform(70.0, 150.0)
                cell.max_grazer = random.uniform(30.0, 70.0)
                cell.max_predator = random.uniform(15.0, 45.0)

                cell.k_v = random.uniform(0.05, 0.2)
                cell.k_g = random.uniform(0.005, 0.02)
                cell.k_gv = random.uniform(0.5, 2.0)
                cell.k_gp = random.uniform(0.005, 0.02)
                cell.k_p = random.uniform(0.005, 0.02)
                cell.k_pg = random.uniform(0.5, 2.0)

                cell.plant = random.uniform(0.0, cell.max_plant)
                cell.grazer = random.uniform(0.0, cell.max_grazer)
                cell.predator = random.uniform(0.0, cell.max_predator)

        for key in list(self.edges):
            self.edges[key] = random.uniform(0.0, 1.0)

    def tick(self) -> None:
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                cell.tick()

        self._apply_overflow("plant", "max_plant", rounds=2)
        self._apply_overflow("grazer", "max_grazer", rounds=2)
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
                        grazer=float(item.get("grazer", 0.0)),
                        predator=float(item.get("predator", 0.0)),
                        k_v=float(item.get("k_v", 0.10)),
                        k_g=float(item.get("k_g", 0.01)),
                        k_gv=float(item.get("k_gv", 1.0)),
                        k_gp=float(item.get("k_gp", 0.01)),
                        k_p=float(item.get("k_p", 0.01)),
                        k_pg=float(item.get("k_pg", 1.0)),
                        max_plant=max(0.01, float(item.get("max_plant", 1.0))),
                        max_grazer=max(0.01, float(item.get("max_grazer", 1.0))),
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

    def export_as_csv(self, output_dir: str | Path) -> None:
        destination = Path(output_dir)
        destination.parent.mkdir(parents=True, exist_ok=True)

        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                ticks = range(len(cell.hist_plant))
                csv_path = destination.joinpath(
                    f"hex_simulation_{r}x{c}_{cell.name}.csv"
                )
                with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow(["tick", "vegetation", "grazers", "predators"])
                    writer.writerows(
                        zip(
                            ticks, cell.hist_plant, cell.hist_grazer, cell.hist_predator
                        )
                    )

    def visualize_state(self, output_path: str | Path) -> None:

        destination = Path(output_path)
        destination.parent.mkdir(parents=True, exist_ok=True)

        figure, axis = plt.subplots(figsize=(8, 4.5))
        caption = figure.text(0.5, 0.01, "", ha="center", fontsize=9)
        try:
            for r in range(self.rows):
                for c in range(self.cols):
                    cell = self.grid[r][c]
                    parameters = (
                        f"k_v={cell.k_v:g}, k_g={cell.k_g:g}, k_gv={cell.k_gv:g}, "
                        f"k_gp={cell.k_gp:g}, k_p={cell.k_p:g}, k_pg={cell.k_pg:g}"
                    )
                    ticks = range(len(cell.hist_plant))
                    axis.clear()
                    caption.set_text(parameters)
                    axis.plot(
                        ticks, cell.hist_plant, label="Vegetation", color="#4caa62"
                    )
                    axis.plot(ticks, cell.hist_grazer, label="Grazers", color="#d4a72c")
                    axis.plot(
                        ticks, cell.hist_predator, label="Predators", color="#c94c4c"
                    )
                    axis.set_xlabel("Tick")
                    axis.set_ylabel("Population / density")
                    axis.set_title(f"{r}x{c} ecosystem over {len(ticks)} ticks")
                    axis.legend()
                    axis.grid(True)
                    figure.tight_layout(rect=(0, 0.06, 1, 1))
                    figure.savefig(
                        destination.joinpath(f"hex_simulation_{r}x{c}_{cell.name}.png"),
                        format="png",
                        dpi=150,
                    )
        finally:
            plt.close(figure)
