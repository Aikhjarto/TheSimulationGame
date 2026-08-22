from pathlib import Path

from simulation_game.experiment import run_single_tile_experiment


def test_single_tile_experiment_exports_100_tick_curves(tmp_path: Path) -> None:
    output_path = run_single_tile_experiment(tmp_path / "single_tile.png")

    assert output_path.exists()
    assert output_path.stat().st_size > 0
    assert output_path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")