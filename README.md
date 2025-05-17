# Bill Calculator

This project is a bill calculator that processes various types of bills and outputs the results using different strategies.

## Getting Started

### Prerequisites

- Python 3.x
- pip (Python package installer)

### Installation

1. Clone the repository:
    ```sh
    git clone <repository_url>
    cd <repository_directory>
    ```

2. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

### Running the Application

To run the main application, execute the following command:
```sh
python main.py --file-path src/bills.yaml 
```

## Project Structure

- `main.py`: Entry point for running the bill calculator.
- `src/`
  - `bill_type.py`: Defines bill types, the abstract `Bill` class, and concrete bill calculation strategies (`TotalBill`, `WaterBill`, `InternetBill`, `ElectricBill`).
  - `bill_calculator.py`: Orchestrates bill calculation using the bill types and strategies.
  - `output_strategy.py`: Handles output formatting and strategies.
  - `bills.yaml`, `bills_2024.yaml`: Example bill data files.
- `test/`: Contains tests and test data.
- `v2/`: Contains CSV files for monthly bill data.

## UML Diagram

A PlantUML diagram describing the main class structure can be found in `project_structure.puml`.

To view the diagram, use a PlantUML viewer or VS Code extension. Example:

```sh
# If you have PlantUML installed
plantuml project_structure.puml
```

---

For more details, see the source files and comments.