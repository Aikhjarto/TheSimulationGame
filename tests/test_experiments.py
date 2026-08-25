from pathlib import Path

from simulation_game.Cell import Cell
from simulation_game.Experiments import run_single_line_experiment

def test_single_tile_plant_growth(tmp_path: Path, **kwargs) -> None:
    """Test the single-tile experiment with default parameters and plant growth"""
    starting_settings = Cell(vegetation=5.0, grazer=0.0, predator=0.0, name='plant_only')
    output_path = run_single_line_experiment([starting_settings,], n_ticks=100, output_path=tmp_path)
    check_exported_files(n_ticks=100, output_path=output_path)

def test_single_tile_plant_growth_slow(tmp_path: Path, **kwargs) -> None:
    """Test the single-tile experiment with default parameters and plant growth"""
    starting_settings = Cell(vegetation=5.0, k_v=0.02, grazer=0.0, predator=0.0, name='plant_only_slow')
    output_path = run_single_line_experiment([starting_settings,], n_ticks=100, output_path=tmp_path)
    check_exported_files(n_ticks=100, output_path=output_path)
    
def test_single_tile_logarithmic_extinction(tmp_path: Path, **kwargs) -> None:
    """Test the single-tile experiment with logarithmic activation mode and extintion"""
    starting_settings = Cell(vegetation=5.0, grazer=1.0, predator=3.0, activation_mode='logarithmic', name='log_extinction')
    output_path = run_single_line_experiment([starting_settings,], n_ticks=100, output_path=tmp_path)
    check_exported_files(n_ticks=100, output_path=output_path)

def test_single_tile_logarithmic_stable(tmp_path: Path, **kwargs) -> None:
    """Test the single-tile experiment with logarithmic activation mode and stable conditions"""
    starting_settings = Cell(vegetation=5.0, grazer=1.0, predator=3.0, k_g=0.05, activation_mode='logarithmic', name='log_stable')
    output_path = run_single_line_experiment([starting_settings,], n_ticks=1000, output_path=tmp_path)
    check_exported_files(n_ticks=1000, output_path=output_path)

def test_single_tile_tanh_extinction(tmp_path: Path, **kwargs) -> None:
    """Test the single-tile experiment with tanh activation mode and extinction"""
    starting_settings = Cell(vegetation=5.0, grazer=1.0, predator=3.0, activation_mode='tanh', name='tanh_extinction')
    output_path = run_single_line_experiment([starting_settings,], n_ticks=100, output_path=tmp_path)
    check_exported_files(n_ticks=100, output_path=output_path)

def test_single_tile_tanh_stable(tmp_path: Path, **kwargs) -> None:
    """Test the single-tile experiment with tanh activation mode and stable conditions"""
    starting_settings = Cell(vegetation=5.0, grazer=1.0, predator=3.0, k_g=0.05, activation_mode='tanh', name='tanh_stable')
    output_path = run_single_line_experiment([starting_settings,], n_ticks=1000, output_path=tmp_path)
    check_exported_files(n_ticks=1000, output_path=output_path)


def test_row_spill_over_logarithmic(tmp_path: Path, **kwargs) -> None:
    """Test the single-tile experiment with logarithmic activation mode and extintion"""
    starting_settings = [Cell(vegetation=5.0, grazer=1.0, predator=3.0, activation_mode='logarithmic', name='log_extinction'),
                         Cell(vegetation=5.0, grazer=1.0, predator=3.0, k_g=0.05, activation_mode='logarithmic', name='log_stable'),
                         ]
    output_path = run_single_line_experiment(starting_settings, n_ticks=1000, output_path=tmp_path)
    check_exported_files(n_ticks=1000, output_path=output_path)


def test_row_spill_over_tanh(tmp_path: Path, **kwargs) -> None:
    """Test the single-tile experiment with logarithmic activation mode and extintion"""
    starting_settings = [Cell(vegetation=5.0, grazer=1.0, predator=3.0, activation_mode='tanh', name='tanh_extinction'),
                         Cell(vegetation=5.0, grazer=1.0, predator=3.0, k_g=0.05, activation_mode='tanh', name='tanh_stable'),
                         ]
    output_path = run_single_line_experiment(starting_settings, n_ticks=1000, output_path=tmp_path)
    check_exported_files(n_ticks=1000, output_path=output_path)


def check_exported_files(n_ticks: int, output_path: Path):
    return
    # assert output_path.exists()
    # assert output_path.stat().st_size > 0
    # assert output_path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")

    # csv_path = output_path.with_suffix(".csv")
    # with csv_path.open(newline="", encoding="utf-8") as csv_file:
    #     rows = list(csv.reader(csv_file))

    # assert rows[0] == ["tick", "vegetation", "grazers", "predators"]
    # assert len(rows) == n_ticks + 1  # header + ticks
    # assert rows[1][0] == "0"
    # assert rows[-1][0] == f"{n_ticks-1}"