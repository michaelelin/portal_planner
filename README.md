# Portal Planner
Attempts to solve levels in a much simplified, two-dimensional version of the game *Portal* using classical planning.

## Installation
This requires Python 3 to run. Tested with Python 3.7.1 on MacOS, but any version 3.7+ should work fine.

Install dependencies with [pip](https://packaging.python.org/tutorials/installing-packages/#ensure-you-can-run-pip-from-the-command-line):
```
$ pip3 install -r requirements.txt
```

## Running
There are three entry points to the program. In order of increasing complexity:

**Viewer**: Displays a view of an existing level. Existing levels are stored in the `levels/` directory as JSON files.
```
$ python3 view.py <level-file>
```

**Solver**: Solves an existing level and animates the solution. Note that this can get kind of slow on some levels (e.g. `levels/p05.json` takes several seconds on my machine). This is because my planner implementation is very basic and poorly optimized and doesn't use any heuristics in its state space search. To use a [much faster remote planner](http://solver.planning.domains/) that I did not write, add the `-r` flag to the command.
```
$ python3 solve.py [-r] <level-file>
```

**Editor**: Allows creation and editing of levels. Note that `level-file` is optional here; if none is included, a new level will be created.
```
$ python3 edit.py [-r] [level-file]
```
The editor allows the user to:
- Adjust the zoom level with a slider (because my version on Tk on MacOS is buggy so scroll events don't work)
- Pan around the level by right clicking and dragging
- Rename the level
- Select the player's capabilities (whether they can create orange or blue portals)
- Use tools to place or remove gameplay elements. These should be fairly intuitive to use and self-explanatory.
- Save the current level as a JSON file (so it can be loaded back up later in the editor or solver)
- Run the current level through the solver

## Gameplay Elements
The following is a reference of how different gameplay elements work and what they look like.
- **Player** (small red circle): This is the character that is controlled by the AI agent. It can move around, move through portals, interact with objects, and create portals.
- **Goal** (small yellow circle): In order to solve a level, the player must reach the goal.
- **Cube** (black square): This is an object that can be picked up and put down by a player. Only one cube can be carried at a time. Activates buttons when placed on them.
- **Button** (large red circle): A button can control doors. It is activated when either a player is standing on it or a cube has been placed on it.
- **Portal** (blue or orange line segment): At most one of each type of portal (blue or orange) can exist at a time. A player can walk into one portal and come out of the other portal, if both exist. If a level allows it, a player can create a portal on a portalable wall that is visible to the player, replacing the existing portal.
- **Wall** (black line segment): Prevents a player from passing through.
- **Portalable Wall** (brown line segment): Like a wall, but a portal can be created on it.
- **Ledge** (black line segment with a dashed line segment beside it): A player may drop down a ledge from the solid side to the dashed side, but cannot climb up it in the opposite direction.
- **Grill** (light blue line segment): A player can pass through a grill, but they cannot carry any items through the grill and passing through it removes all of the portals that they created.
- **Door** (green line segment): A player may pass through a door only if it's open (it becomes a dotted line segment when it opens). A door is open only when all of the buttons it is connected to are activated. If it is connected to no buttons, then it is always open. Connections are shown as dashed blue line segments.
