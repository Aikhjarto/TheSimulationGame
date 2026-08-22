from __future__ import annotations

from pathlib import Path

from .app import HexSimulation


def run_single_tile_experiment(output_path: str | Path) -> Path:
    """Run the configured single-tile experiment and export its curves as PNG."""
    import matplotlib.pyplot as plt

    simulation = HexSimulation(rows=1, cols=1)
    cell = simulation.grid[0][0]
    cell.plant = 5.0
    cell.grazer = 0.0
    cell.predator = 3.0

    ticks = [0]
    plants = [cell.plant]
    grazers = [cell.grazer]
    predators = [cell.predator]

    for tick in range(1, 101):
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
    figure.savefig(destination, format="png", dpi=150)
    plt.close(figure)
    return destination