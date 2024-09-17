"""
This module contains tests for the BillCalculator class. 
It includes tests for output file creation and the correctness of the calculated totals and readings. 
The tests use a fixture to create a BillCalculator object and a set of bills, which are then used in each test method.
"""

import os
import tempfile
import jmespath
import jc.parsers.csv
import pytest
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


@pytest.fixture
def bills_calculator():
    """
    This fixture creates a BillCalculator object with a set of bills.
    The bills include electric, water, internet, and total bills, each with a specific set of shared keys.
    The fixture calculates the bills and outputs them using the TableOutputStrategy.
    The BillCalculator object is then returned for use in the test methods.
    """

    bills = [
        ElectricBill(BillType.ELECTRIC, 3, ELECTRIC_SHARED_KEYS, "Papa"),
        WaterBill(BillType.WATER, 3, WATER_SHARED_KEYS),
        InternetBill(BillType.INTERNET, 2, INTERNET_SHARED_KEYS),
        TotalBill(BillType.TOTAL, 3, ELECTRIC_SHARED_KEYS),
    ]
    calculator = BillCalculator("test/test_bills.yaml", bills)
    calculator.calculate()
    calculator.output_bill(TableOutputStrategy())
    return calculator


class TestOutput:
    """
    This class contains tests for the output of the BillCalculator class. It includes tests for the existence of the
    output file, the correctness of the calculated totals, and the correctness of the calculated readings.
    """

    def test_output_file_exists(
        self, bills_calculator
    ):  # pylint: disable=redefined-outer-name
        """
        Test that the BillCalculator's output method creates a file.
        """
        calculator = bills_calculator
        with tempfile.TemporaryDirectory() as tmpdirname:
            file_path = os.path.join(tmpdirname, f"{calculator.data[0]['month']}.csv")
            calculator.output_bill(CSVOutputStrategy(file_path))

            # Check that a file was created
            assert os.path.isfile(file_path), "File does not exist"

    def test_output_totals(
        self, bills_calculator
    ):  # pylint: disable=redefined-outer-name
        """
        Test that the totals in the BillCalculator's output file are correct.
        """
        calculator = bills_calculator
        with tempfile.TemporaryDirectory() as tmpdirname:
            file_path = os.path.join(tmpdirname, f"{calculator.data[0]['month']}.csv")
            calculator.output_bill(CSVOutputStrategy(file_path))

            # Check that a file was created
            assert os.path.isfile(file_path), "File does not exist"

            # Read the CSV file
            with open(file_path, "r", encoding="utf8") as f:
                csv_data = f.read()

            data = jc.parsers.csv.parse(csv_data)

            # Use JMESPath to get 'Total' for 'Ian'
            ian_total = jmespath.search("[?Name=='Ian'].Total | [0]", data)
            papa_total = jmespath.search("[?Name=='Papa'].Total | [0]", data)
            jack_total = jmespath.search("[?Name=='Jack'].Total | [0]", data)
            ajin_total = jmespath.search("[?Name=='Ajin'].Total | [0]", data)

            # Check the value of 'Total' for 'Ian'
            assert ian_total == "2274.399", "Incorrect total for Ian"
            assert papa_total == "0.0", "Incorrect total for Papa"
            assert jack_total == "2555.695", "Incorrect total for Jack"
            assert ajin_total == "571.156", "Incorrect total for Ajin"

    def test_output_reading(
        self, bills_calculator
    ):  # pylint: disable=redefined-outer-name
        """
        Test that the readings in the BillCalculator's output file are correct.
        """
        calculator = bills_calculator
        with tempfile.TemporaryDirectory() as tmpdirname:
            file_path = os.path.join(tmpdirname, f"{calculator.data[0]['month']}.csv")
            calculator.output_bill(CSVOutputStrategy(file_path))

            # Check that a file was created
            assert os.path.isfile(file_path), "File does not exist"

            # Read the CSV file
            with open(file_path, "r", encoding="utf8") as f:
                csv_data = f.read()

            data = jc.parsers.csv.parse(csv_data)

            # Use JMESPath to get 'Total' for 'Ian'
            ian_veco = jmespath.search("[?Name=='Ian'].Veco | [0]", data)
            papa_veco = jmespath.search("[?Name=='Papa'].Veco | [0]", data)
            jack_veco = jmespath.search("[?Name=='Jack'].Veco | [0]", data)
            ajin_veco = jmespath.search("[?Name=='Ajin'].Veco | [0]", data)

            # Check the value of 'Total' for 'Ian'
            assert ian_veco == "1200", "Incorrect veco for Ian"
            assert papa_veco == "50", "Incorrect  veco for Papa"
            assert jack_veco == "1500", "Incorrect veco for Jack"
            assert ajin_veco == "450", "Incorrect veco for Ajin"
