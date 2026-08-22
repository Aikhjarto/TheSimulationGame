Initial prompt
```
I want a simulation game written in Python.
The game should be based on a hexagonal grid, simulating growth and decline in nature based on three main variables per grid cell: plant matter, amount of prey animals and amount of predator animals.

Each simulation tic, those three variable are adapted per cell, based on the following parameters: 
plant matter growth, 
plant matter nutrition (how much plant matter is converted to prey animals per tic),
hunt success rate (how many prey animals are converted to predator animal per tic),
prey animal old age death rate (how many prey animals die each tic),
predator animal old age deatch rate (how many predator animals die each tic), as well as
a maximum numbers for plant matter, prey animals and predator animals per cell.
The edges should have a traversability parameter.
If the amount of plant matter, or number of animals in a cell is above it's maximum amount, the overhead is spread to adjacent cells based on the traversibilty.

A graphical user interface should display the grid. 
The amount of plant matter, prey animals, predator animals should displayed with three circles of different in each cell.
A button should toggle between displaying the circles and the actual numbers.
The traversibilty from one cell to another should be indicated by the color intensity of the edge which connects the cells.
A legend indicating which values are represented by the different visual items should be presented.
Detailed numbers, including parameters of cells and edges, should be displayed, when hovering over a cell with the mouse or via long press on a touch interface.
By clicking or dragging the mouse, parameters of the cells should be changable. The user should be able to input the exact values.
The user should also be able to spawn plant matter and animals on the cells.
Simulation speed should be adjustable. There should be a button to pause and single-step the simulation.
A button should clear the map from all plant matter, animals and set everything to perfect traversability.
A button should generate a random map.
Double clicking on a cell should show a graph history of the number of plants and animals.

A save/load possibility should be present.

The license should allow the distribute and modify the code, but the original author must be mentioned and the original project or its decendent must not be sold without profit sharing with the original author.

The project should contain a pyproject.toml and a requirements.txt
```