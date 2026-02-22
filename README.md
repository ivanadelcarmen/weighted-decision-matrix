# **Interactive Weighted Decision Matrix application using Python classes and Qt**

_**Technology stack**: Python 3.12, Qt Designer, `PyQT6`_

## Abstract

The following project develops an application with an integrated GUI for easily generating and updating a Weighted Decision Matrix (WDM), which is a common method by which users can decide the best option among multiple items and according to different criteria through a scoring system where the user first defines a numeric scale to work with, assigns a weight to each criterion, and then punctuates each item respect each of them. Each item's total score is the weighted sum of all criteria scores, and the item with the highest score is ultimately interpreted as the best option.

The inner logic of the program is built on Python classes to compose abstract objects which are easier to work with, and all interface components have been developed with Qt tools.

All icons are sourced from [Flaticon](https://www.flaticon.com/) and used under the Free License for non-commercial purposes.

## Guideline

Before deploying the project, dependencies have to be installed globally or locally in a virtual environment placed in the root directory which has to be activated. Then, run the application inside the src/ directory which contains all source files. Additionally, the window components (i.e. `columns.py`, `rows.py`, `matrix.py`) can be executed individually for testing. Example for Unix-based shells:

``` bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

``` bash
cd src
python app.py
```

## Architecture

Logically, the WDM specification implies:

- An $n \times k$ matrix, where $n$ is the amount of selected items (rows) and $k$ is the amount of attributes to evaluate (columns)
- Each column has a value $p$ associated with it, between 0 and 1.
- The sum of all $p$ values, each associated with a column, must equal 1
- Each cell has a $(i,j)$ position assigned in the matrix, where $0<i<n+1$ and $0<j<k+1$
- Each cell must contain an integer in the range of $[1,10]$ which indicates the score of item $i$ respect criterion $j$
- The final score of each row $i$ is the weighted sum: $\sum_{j=1}^{k}(i,j)*p_{j}$, where $p_{j}$ is the weight $p$ associated with each column $j$

Each column is written as an object from the `Column` class with title, values, and weight attributes, and a method to set a value at an index (row). 

The `WeightedMatrix` class has the "matrix" attribute (i.e. a list with Column objects) along with the "items" attribute for registering row names, by row index, and other two attributes for keeping count of the amount of rows and columns. The object has methods for inserting a value at a $(i,j)$ position, with indices as indicated in the specification above, and returning final scores for each row index (rather than number). Additionally, CRUD methods for the WDM have been implemented in relation with columns and rows to allow for matrix modification after initial generation.

#

### GUI

The application's interface is structured around three sequential windows that guide users through the matrix creation process: rows definition, columns definition, and matrix scoring. This flow is managed by a central `MainApp` class that uses PyQT6's `QStackedWidget` to handle navigation between screens while maintaining a single shared `WeightedMatrix` instance throughout the session.

The first window, `RowsWindow`, allows users to define the items they wish to compare. Users can dynamically add or remove rows (with a minimum of 2 and maximum of 8), and each row is represented by a text input field with an associated delete button. The interface validates that all fields contain text before enabling the "Next" button, ensuring no blank entries proceed to the next stage.

The `ColumnsWindow` presents a similar interface for defining evaluation criteria. Each column requires both a name and a weight value, with weights constrained to the format "0.XX" and validated in real-time. The interface displays the current sum of all weights and only enables progression when exactly two or more criteria are defined, all fields are filled, and the weights sum to precisely 1.0. This validation ensures the mathematical integrity of the weighted scoring system.

The final window, `MatrixWindow`, displays the complete decision matrix as an interactive table where users score each item against each criterion. The table uses a custom `CellSelectionDelegate` that specifies custom cell selection styles and restricts input to integers between 1 and 10, enforcing the scoring range defined in the specification. Column headers display both the criterion name and its weight, while row headers show the item names. The "Show results" button remains disabled until every cell contains a valid score, at which point users can view the computed weighted scores in a styled dialog that highlights the best option.

Navigation between windows is bidirectional, with a "Modify matrix" button allowing users to return to the rows screen and adjust their whole setup. The application preserves all entered data when navigating backwards, reloading each window with the current matrix state. This approach ensures users can iteratively refine their decision matrix without losing existing inputs.

The UI files were designed using Qt Designer and compiled into Python modules using `pyuic6`, which must be installed as part of the PyQT6 development tools:

``` bash
pip install pyqt6-tools
```

Once installed, UI files can be compiled with the following command structure:

``` bash
cd src
pyuic6.exe ui/matrix.ui -o ui/scripts/matrix_ui.py # Example with the matrix window
```

All icon resources are loaded dynamically using the `resource_path()` utility function defined in `utils.py`, which resolves absolute paths relative to the `src` directory during development and relative to PyInstaller's temporary directory when the application is packaged as an executable as part of the repository's GitHub Actions workflow.

#

### Testing

The core object methods are tested using `unittest`. Run the tests package by executing the following command at the root directory of the project:

``` bash
python -m tests
```

## Repository

```
weighted-decision-matrix/
│
├── src/                   # Source files for the application
│   ├── core/              # Files associated with the package of core classes
│   ├── ui/                # GUI assets such as icons and .ui files with their compilations (scripts)
│   ├── __init__.py        # Python package initializer
│   ├── app.py             # The app's entrypoint
│   ├── columns.py         # Definition of the columns PyQT6 window
│   ├── matrix.py          # Definition of the matrix PyQT6 window
│   ├── rows.py            # Definition of the rows PyQT6 window
│   └── utils.py           # File containing the function for handling absolute paths
│
├── tests/                 # Package of tests for the core scripts
│
├── README.md              # Project overview, instructions, and architecture details
├── LICENSE                # License information for the repository
├── .gitignore             # Directories to be ignored by Git
├── pyinstaller.spec       # Specification for bundling the app into an executable using PyInstaller
└── requirements.txt       # Project dependencies to be installed using pip
```