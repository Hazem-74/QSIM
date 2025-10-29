# QSim: Quantum Simulation GUI

QSim is a graphical user interface (GUI) application built with PyQt6 that allows users to design and simulate simple quantum optical circuits on a grid. Users can drag-and-drop optical components like lasers, beam splitters, mirrors, and detectors onto a grid, rotate them, and then run a simulation to calculate the final quantum state vector representing the photon paths.

## Project Structure

The project is organized into three main Python files:

*   `model.py`: Contains the core quantum mechanics and graph-theoretic logic.
*   `viewer.py`: Implements the graphical user interface using PyQt6.
*   `control.py`: Acts as the bridge between the `model` and `viewer`, handling application flow and events.

## File Summaries

### `model.py`

This file encapsulates the backend logic for quantum state representation, operations, and the optical circuit graph.

*   **Purpose**: Defines data structures and algorithms for quantum states, operations, and the simulation graph. It is responsible for calculating the final quantum state of the system based on the optical components laid out in the GUI.
*   **Main Logic**:
    *   **`State` Class**: Represents a quantum state as a NumPy array (state vector). Provides methods to get its dimension and vector.
    *   **`Operation` Class**: Represents a quantum operation (e.g., a beam splitter) as a complex-valued NumPy matrix. It can apply an operation to a `State` and cascade multiple operations. Includes a specific method `modify_to_beam_splitter` to set up a beam splitter operation matrix.
    *   **`Graph` Class**: Extends `networkx.MultiDiGraph` to model the optical circuit.
        *   Manages the addition of optical elements (nodes) and connections (edges) between them.
        *   `add_element` assigns unique IDs and stores element details.
        *   `add_connection` establishes weighted edges between elements.
        *   `__label_paths`: Assigns unique integer labels to possible photon paths within the graph, which are then used as the basis for the quantum state vector.
        *   `calculate_results`: The core simulation method. It initializes a quantum `State` based on the number of path modes, then traverses the graph, applying `Operation` matrices for each optical component (e.g., `BeamSplitter`) to the current `State`.
*   **Methods Highlight**: `apply_operation_on_state`, `cascade_operation`, `modify_to_beam_splitter`, `add_element`, `add_connection`, `__label_paths`, `calculate_results`.

### `viewer.py`

This file is dedicated to the graphical user interface elements and their interactions, built using the PyQt6 framework.

*   **Purpose**: Provides all visual components of the application, including the interactive grid, tool palette, and result display.
*   **Main Logic**:
    *   **`GridItem` and Subclasses (`Laser`, `Detector`, `BeamSplitter`, `PolarBeamSplitter`, `Mirror`, `GridWall`)**: Base class for all optical components that can be placed on the grid. Handles visual attributes, rotation, and drag-and-drop events for moving items on the grid. `GridWall` represents boundaries.
    *   **`GridCell`**: Individual cell on the simulation grid. It's a `QFrame` that can accept `GridItem`s via drag-and-drop.
    *   **`GridArea`**: The main container for all `GridCell`s, forming the simulation workspace. Manages the layout of cells and provides methods to access `GridItem`s at specific coordinates. It also contains and manages a `Photon` object for visualization.
    *   **`Photon`**: A `QWidget` subclass that visually represents a photon as a red dot and can be animated to move between grid cells.
    *   **Tool Palette Components (`tool`, `ToolsList`, `ToolsListsArea`)**: Classes that define the draggable buttons in the left-hand menu, allowing users to select and place new optical components onto the grid.
    *   **`LeftMenu`**: The left sidebar of the application, containing control buttons (Play, Stop, Exit) and the `ToolsListsArea`.
    *   **`CentralWidget`**: The primary layout manager that combines the `LeftMenu` and `SimulationArea`.
    *   **`Ui_MainWindow`**: A setup class that initializes the main `QMainWindow`, populates it with the `CentralWidget`, registers icons and component classes, and provides an interface for the `control.py` to interact with UI elements.
    *   **`VectorWindow`**: A separate window for visualizing the calculated quantum state vector as a table of complex amplitudes.
*   **Methods Highlight**: `mouseMoveEvent` (for drag), `dropEvent` (for placing items), `rotate`, `create_grid`, `move_photon`, `connect_play_button`, `visualize_vector`.

### `control.py`

This file serves as the application's controller, integrating the UI (`viewer.py`) with the simulation logic (`model.py`).

*   **Purpose**: Orchestrates the interaction between the GUI and the quantum simulation engine. It responds to user input, translates UI states into model inputs, triggers calculations, and updates the UI with results.
*   **Main Logic**:
    *   **`MainWindow` Class**: Inherits `QMainWindow` and is the central application controller.
        *   Initializes the `Ui_MainWindow` from `viewer.py` and the `Graph` from `model.py`.
        *   Connects UI buttons (Play, Exit) to corresponding methods (`simulate`, `exit`).
        *   **`simulate` Method**: This is the core method called when the user clicks 'Play'.
            1.  Calls `build_graph()` to construct a `model.Graph` instance based on the `GridItem`s currently placed in the `viewer.GridArea`.
            2.  Invokes `graph.calculate_results(visualize=True)` from `model.py` to perform the quantum simulation and get the final state vector.
            3.  Calls `ui.visualize_vector()` to display the simulation results in a `VectorWindow`.
        *   **`build_graph` Method**: Iterates through the `GridArea` (using BFS starting from `Laser`s) to identify connected optical components and their orientations. It translates these components and their connections into nodes and edges in a `model.Graph`.
        *   **Auxiliary Traversal Methods (`__get_successors`, `__get_next_element_in_dir`, `__get_dx_dy_from_orientation`, `__check_valid_position`)**: These helpers are used by `build_graph` to intelligently traverse the grid, understand how light interacts with components (e.g., reflection from a mirror, splitting at a beam splitter), and find the next elements in the light path.
        *   **`exit` Method**: Terminates the application.
*   **Methods Highlight**: `simulate`, `build_graph`, `__get_successors`, `__get_next_element_in_dir`, `exit`.

## Project Requirements

To run QSim, you need the following Python libraries:

*   `PyQt6`
*   `networkx`
*   `numpy`
*   `matplotlib`

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/Hazem-74/QSim.git
    cd QSim/QSim 
    ```
    *(Note: The provided directory `/home/salastro/Documents/Hazem's Bible/QSIM/QSim` suggests a nested `QSim` directory structure, so the `cd` command reflects that.)*

2.  **Install dependencies**:
    It's recommended to use a virtual environment.
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    pip install PyQt6 networkx numpy matplotlib
    ```

## How to Run

1.  **Ensure you have the image assets**: The `viewer.py` expects an `images/` directory containing icon files (e.g., `laser.png`, `detector.png`, etc.) relative to the script's execution path. Make sure these are present in your `QSim` directory alongside the Python files.

2.  **Run the main control script**:
    ```bash
    python control.py
    ```

    This will launch the QSim GUI application.

## Usage

1.  **Drag and Drop**: Select optical components from the left-hand "Components" menu and drag them onto the grid.
2.  **Rotate Components**: Click on any placed component in the grid to rotate it by 90 degrees. This changes its orientation, affecting how light interacts with it.
3.  **Run Simulation**: Click the "Play" button in the left menu to start the simulation.
    *   The application will build the quantum optical circuit graph.
    *   It will then calculate the final quantum state vector based on the paths light can take.
    *   A separate "Quantum State Vector" window will appear, displaying the complex amplitudes for each path mode.
4.  **Stop Simulation**: (Currently, the "Stop" button is not connected to functionality in the provided code, but typically it would interrupt an ongoing simulation or clear results).
5.  **Exit Application**: Click the "Exit" button to close the QSim application.