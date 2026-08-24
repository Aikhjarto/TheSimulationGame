from pathlib import Path
import csv

from simulation_game.app import Cell
from simulation_game.experiment import run_single_tile_experiment

def test_single_tile_logarithmic_extinction(tmp_path: Path, **kwargs) -> None:
    """Test the single-tile experiment with logarithmic activation mode and extintion"""
    starting_settings = Cell(plant=5.0, grazer=1.0, predator=3.0, activation_mode='logarithmic')
    output_path = run_single_tile_experiment(starting_settings, n_ticks=100, output_path=tmp_path / "single_tile.png")
    check_exported_files(starting_settings, n_ticks=100, output_path=output_path)

def test_single_tile_logarithmic_stable(tmp_path: Path, **kwargs) -> None:
    """Test the single-tile experiment with logarithmic activation mode and stable conditions"""
    starting_settings = Cell(plant=5.0, grazer=1.0, predator=3.0, k_g=0.05, activation_mode='logarithmic')
    output_path = run_single_tile_experiment(starting_settings, n_ticks=1000, output_path=tmp_path / "single_tile.png")
    check_exported_files(starting_settings, n_ticks=1000, output_path=output_path)

def test_single_tile_tanh_extinction(tmp_path: Path, **kwargs) -> None:
    """Test the single-tile experiment with tanh activation mode and extinction"""
    starting_settings = Cell(plant=5.0, grazer=1.0, predator=3.0, activation_mode='tanh')
    output_path = run_single_tile_experiment(starting_settings, n_ticks=100, output_path=tmp_path / "single_tile.png")
    check_exported_files(starting_settings, n_ticks=100, output_path=output_path)

def test_single_tile_tanh_stable(tmp_path: Path, **kwargs) -> None:
    """Test the single-tile experiment with tanh activation mode and stable conditions"""
    starting_settings = Cell(plant=5.0, grazer=1.0, predator=3.0, k_g=0.05, activation_mode='tanh')
    output_path = run_single_tile_experiment(starting_settings, n_ticks=1000, output_path=tmp_path / "single_tile.png")
    check_exported_files(starting_settings, n_ticks=1000, output_path=output_path)

def check_exported_files(starting_settings: Cell, n_ticks: int, output_path: Path):
    assert output_path.exists()
    assert output_path.stat().st_size > 0
    assert output_path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")

    csv_path = output_path.with_suffix(".csv")
    with csv_path.open(newline="", encoding="utf-8") as csv_file:
        rows = list(csv.reader(csv_file))

    assert rows[0] == ["tick", "vegetation", "grazers", "predators"]
    assert len(rows) == n_ticks + 2  # header + ticks 0..100
    assert rows[1][0] == "0"
    assert rows[-1][0] == f"{n_ticks}"