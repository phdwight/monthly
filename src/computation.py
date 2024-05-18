"""
This module calculates and outputs bills.

It defines a BillCalculator class that reads bill data from a YAML file, calculates the bills, and outputs them.
The calculation is done by instances of subclasses of the BillType class, which are passed to the BillCalculator
when it's created. The output is done by instances of subclasses of the OutputStrategy class, which are passed to
the BillCalculator's output_bill method.

The module also defines some constants for shared keys in the bill data, and creates some bill and output strategy
instances for testing purposes.
"""

import yaml

from bill_type import BillType, WaterBill, InternetBill, ElectricBill, TotalBill
from output_strategy import OutputStrategy, TableOutputStrategy, CSVOutputStrategy


class BillCalculator:
    """
    Class for calculating bills.
    """

    def __init__(self, filename, bill_type):
        """
        Initialize the bill calculator with a filename and a list of bills.
        """
        self.data = self.read_yaml_file(filename)
        self.bills = bill_type
        self.bill_obj = {}

    def read_yaml_file(self, filename):
        """
        Read a YAML file and return its data.
        """
        with open(filename, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
        return data

    def calculate(self):
        """
        Calculate all the bills.
        """
        for bill in self.bills:
            bill.calculate(self.data, self.bill_obj)

    def output_bill(self, strategy: OutputStrategy):
        """
        Output the bill using a given output strategy.
        """
        strategy.output(self.bill_obj)


WATER_SHARED_KEYS = ["Jack", "Ian", "Ajin"]
INTERNET_SHARED_KEYS = ["Jack", "Ian"]
ELECTRIC_SHARED_KEYS = ["Jack", "Ian", "Ajin", "Papa"]

bills = [
    ElectricBill(BillType.ELECTRIC, 3, ELECTRIC_SHARED_KEYS, "Papa"),
    WaterBill(BillType.WATER, 3, WATER_SHARED_KEYS),
    InternetBill(BillType.INTERNET, 2, INTERNET_SHARED_KEYS),
    TotalBill(BillType.TOTAL, 3, ELECTRIC_SHARED_KEYS),
]

calculator = BillCalculator("src/bills.yaml", bills)
calculator.calculate()
calculator.output_bill(TableOutputStrategy())
calculator.output_bill(CSVOutputStrategy(f"v2/{calculator.data[0]['month']}.csv"))
