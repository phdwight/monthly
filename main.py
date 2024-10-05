"""
This module is responsible for calculating and outputting bills. 
It imports the necessary classes and defines the shared keys for different types of bills. 
It then creates a list of bills and a BillCalculator object, calculates the bills, 
and outputs them using two different strategies: 
TableOutputStrategy and CSVOutputStrategy.
"""

import argparse
import logging
from enum import Enum
from typing import List

from src.bill_calculator import BillCalculator
from src.bill_type import BillType, WaterBill, InternetBill, ElectricBill, TotalBill
from src.output_strategy import TableOutputStrategy, CSVOutputStrategy

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class Person(Enum):
    """
    This class defines the names of the people sharing the bills.
    """

    JACK = "Jack"
    IAN = "Ian"
    AJIN = "Ajin"
    PAPA = "Papa"


# Define shared keys using the Enum values
WATER_SHARED_KEYS: List[str] = [Person.JACK.value, Person.IAN.value, Person.AJIN.value]
INTERNET_SHARED_KEYS: List[str] = [Person.JACK.value, Person.IAN.value]
ELECTRIC_SHARED_KEYS: List[str] = [
    Person.JACK.value,
    Person.IAN.value,
    Person.AJIN.value,
    Person.PAPA.value,
]

# Define threshold using the Enum values
ELECTRIC_THRESHOLD = {"amount": 500, "key": Person.IAN.value}

# Create bills list using the Enum values
bills = [
    ElectricBill(
        BillType.ELECTRIC,
        3,
        ELECTRIC_SHARED_KEYS,
        Person.PAPA.value,
        ELECTRIC_THRESHOLD,
    ),
    WaterBill(BillType.WATER, 3, WATER_SHARED_KEYS),
    InternetBill(BillType.INTERNET, 2, INTERNET_SHARED_KEYS),
    TotalBill(BillType.TOTAL, 3, ELECTRIC_SHARED_KEYS),
]

# Constants for file paths
OUTPUT_DIR = "v2"
CSV_EXTENSION = ".csv"


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Calculate and output bills.")
    parser.add_argument(
        "--file-path",
        type=str,
        required=True,
        help="The path to the YAML file containing the bills data.",
    )
    return parser.parse_args()


def calculate_and_output_bills(file_path: str) -> None:
    """
    Calculate and output bills using the provided file path.
    """
    try:
        calculator = BillCalculator(file_path, bills)
        calculator.calculate()
        calculator.output_bill(TableOutputStrategy())
        output_file_path = f"{OUTPUT_DIR}/{calculator.data[0]['month']}{CSV_EXTENSION}"
        calculator.output_bill(CSVOutputStrategy(output_file_path))
    except Exception as e:
        logging.error(f"An error occurred: {e}")


def main() -> None:
    """
    The main function for calculating and outputting bills.
    """
    args = parse_arguments()
    calculate_and_output_bills(args.file_path)


if __name__ == "__main__":
    main()
