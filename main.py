"""
This module is responsible for calculating and outputting bills. 
It imports the necessary classes and defines the shared keys for different types of bills. 
It then creates a list of bills and a BillCalculator object, calculates the bills, 
and outputs them using two different strategies: 
TableOutputStrategy and CSVOutputStrategy.
"""

import argparse

from src.bill_calculator import (
    BillCalculator,
)

from src.bill_type import (
    BillType,
    WaterBill,
    InternetBill,
    ElectricBill,
    TotalBill,
)

from src.output_strategy import (
    TableOutputStrategy,
    CSVOutputStrategy,
)


WATER_SHARED_KEYS = ["Jack", "Ian", "Ajin"]
INTERNET_SHARED_KEYS = ["Jack", "Ian"]
ELECTRIC_SHARED_KEYS = ["Jack", "Ian", "Ajin", "Papa"]

ELECTRIC_THRESHOLD = {"amount": 500, "key": "Ian"}

bills = [
    ElectricBill(BillType.ELECTRIC, 3, ELECTRIC_SHARED_KEYS, "Papa", ELECTRIC_THRESHOLD),
    WaterBill(BillType.WATER, 3, WATER_SHARED_KEYS),
    InternetBill(BillType.INTERNET, 2, INTERNET_SHARED_KEYS),
    TotalBill(BillType.TOTAL, 3, ELECTRIC_SHARED_KEYS),
]


def main():
    """
    The main function for calculating and outputting bills.
    """
    parser = argparse.ArgumentParser(description="Calculate and output bills.")
    parser.add_argument(
        "--file-path",
        type=str,
        required=True,
        help="The path to the YAML file containing the bills data.",
    )
    args = parser.parse_args()

    calculator = BillCalculator(args.file_path, bills)
    calculator.calculate()
    calculator.output_bill(TableOutputStrategy())
    calculator.output_bill(CSVOutputStrategy(f"v2/{calculator.data[0]['month']}.csv"))


main()
