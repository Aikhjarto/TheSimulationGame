from __future__ import annotations

import csv
from pathlib import Path

from .HexSimulation import HexSimulation
from .Cell import Cell
from typing import List


def run_single_line_experiment(
    starting_settings: List[Cell], n_ticks: int, output_path: str | Path
) -> Path:
    """Run the configured single-tile experiment and export PNG and CSV data."""
    import matplotlib.pyplot as plt

    simulation = HexSimulation(
        rows=1, cols=len(starting_settings), initial_cells=starting_settings
    )

    ticks = [0]

    for tick in range(1, n_ticks + 1):
        simulation.tick()
        ticks.append(tick)

    simulation.visualize_state(output_path)
    simulation.export_as_csv(output_path)

    return Path(output_path)
