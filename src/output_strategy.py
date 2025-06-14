"""
This module defines strategies for outputting bill data. It includes an abstract base class, OutputStrategy,
and two concrete strategies, TableOutputStrategy and CSVOutputStrategy. TableOutputStrategy outputs the bill data
as a table in the console, while CSVOutputStrategy writes the bill data to a CSV file.
"""

import csv

from abc import ABC, abstractmethod
from prettytable import PrettyTable


class OutputStrategy(ABC):
    """
    Abstract base class for output strategies.
    """

    @abstractmethod
    def output(self, bill_obj):
        """
        Abstract method to output a bill object.
        """

    @staticmethod
    def generate_total_row(bill_obj):
        """
        Generate a total row for the output.

        Returns:
            list: The first element is the label string ("Total"), and each subsequent element is the sum of the
            corresponding column in the bill_obj values, rounded to 2 decimal places. The order of columns matches
            the order in the bill_obj value lists.
        """
        if not bill_obj:
            return ["Total"]
        columns = list(zip(*bill_obj.values()))
        totals = [
            round(sum(col), 2)
            for col in columns
        ]
        return ["Total"] + totals


class TableOutputStrategy(OutputStrategy):
    """
    Class for outputting a bill object as a table.
    """

    def output(self, bill_obj):
        """
        Output the bill object as a table.
        """
        table = PrettyTable()
        table.field_names = [
            "Name",
            "Veco",
            "Electric Amount",
            "Electric Adjusted",
            "Water",
            "Internet",
            "Total",
        ]

        for key, values in bill_obj.items():
            table.add_row([key] + values)

        table.add_row(OutputStrategy.generate_total_row(bill_obj))

        print(table)


class CSVOutputStrategy(OutputStrategy):
    """
    Class for outputting a bill object as a CSV file.
    """

    def __init__(self, filename):
        """
        Initialize the CSV output strategy with a filename.
        """
        self.filename = filename

    def output(self, bill_obj):
        """
        Output the bill object as a CSV file.
        """
        with open(self.filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    "Name",
                    "Veco",
                    "Electric Amount",
                    "Electric Adjusted",
                    "Water",
                    "Internet",
                    "Total",
                ]
            )

            for key, values in bill_obj.items():
                writer.writerow([key] + values)

            writer.writerow(OutputStrategy.generate_total_row(bill_obj))
