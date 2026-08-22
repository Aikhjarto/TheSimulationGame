# The Simulation Game

A Python simulation game on a hexagonal grid where plant matter, prey, and predators grow and decline over time.

## Features

- Hex-grid ecosystem simulation
- Per-cell variables and tunable parameters
- Per-edge traversability controlling overflow spread
- Visual mode toggle (circles or numbers)
- Hover and long-press details panel
- Click-and-drag painting tools for values and parameters
- Spawn tools for plant matter, prey, and predators
- Pause, single-step, and speed control
- Random map generation and full reset
- Save and load simulation maps as JSON

## Run

```bash
python -m simulation_game
```

Or install and run:

```bash
pip install -e .
the-simulation-game
```

## Controls

- Select a tool from the right panel
- Enter a numeric value
- Click or drag on cells to apply
- Double-click a cell to open its plant/prey/predator history graph
- Use the edge tool to set traversability between neighboring cells
- Toggle visual mode to switch between circles and numbers
- Save Map / Load Map to persist or restore full map state

## Single-tile experiment

Run the 100-tick experiment with low vegetation, no grazers, and three predators:

```bash
python -c "from simulation_game.experiment import run_single_tile_experiment; run_single_tile_experiment('single_tile.png')"
```

The resulting PNG contains vegetation, grazer, and predator curves with a caption listing the tile's k-parameters. Run the test with `pytest` to verify the export.


## Math
$v(t)$: vegetation density 

$g(t)$: grazer population

$p(t)$: predator population

$$
\frac{\mathrm dv(t)}{\mathrm{dt}} = k_\mathrm v v(t) \left(1-\frac{v(t)}{v_\mathrm{max}}\right) - k_\mathrm g g(t)
$$

$$
\frac{\mathrm dg(t)}{\mathrm{dt}} = k_\mathrm g g(t) \ln\left(k_\mathrm{gv} \frac{g(t)}{v(t)}\right) - k_\mathrm{gp} p(t)
$$

$$
\frac{\mathrm d p(t)}{\mathrm{dt}} = k_\mathrm p p(t) \ln\left(k_\mathrm{pg} \frac{p(t)}{g(t)}\right)
$$