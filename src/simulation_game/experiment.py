from __future__ import annotations

import csv
from pathlib import Path

from .app import HexSimulation, Cell


def run_single_tile_experiment(starting_settings: Cell, n_ticks: int, output_path: str | Path) -> Path:
    """Run the configured single-tile experiment and export PNG and CSV data."""
    import matplotlib.pyplot as plt

    simulation = HexSimulation(rows=1, cols=1)
    cell = simulation.grid[0][0]
    cell.__dict__.update(starting_settings.__dict__)

    ticks = [0]
    plants = [cell.plant]
    grazers = [cell.grazer]
    predators = [cell.predator]

    for tick in range(1, n_ticks + 1):
        simulation.tick()
        ticks.append(tick)
        plants.append(cell.plant)
        grazers.append(cell.grazer)
        predators.append(cell.predator)

    parameters = (
        f"k_v={cell.k_v:g}, k_g={cell.k_g:g}, k_gv={cell.k_gv:g}, "
        f"k_gp={cell.k_gp:g}, k_p={cell.k_p:g}, k_pg={cell.k_pg:g}"
    )
    figure, axis = plt.subplots(figsize=(8, 4.5))
    axis.plot(ticks, plants, label="Vegetation", color="#4caa62")
    axis.plot(ticks, grazers, label="Grazers", color="#d4a72c")
    axis.plot(ticks, predators, label="Predators", color="#c94c4c")
    axis.set_xlabel("Tick")
    axis.set_ylabel("Population / density")
    axis.set_title("Single-tile ecosystem over 100 ticks")
    axis.legend()
    figure.text(0.5, 0.01, parameters, ha="center", fontsize=9)
    figure.tight_layout(rect=(0, 0.06, 1, 1))

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    csv_path = destination.with_suffix(".csv")
    with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["tick", "vegetation", "grazers", "predators"])
        writer.writerows(zip(ticks, plants, grazers, predators))

    figure.savefig(destination, format="png", dpi=150)
    plt.close(figure)
    return destination