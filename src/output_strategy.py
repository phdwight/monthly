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
        pass


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
            "Veco Reading",
            "Electric Amount",
            "Electric Adjusted",
            "Water",
            "Internet",
            "Total",
        ]

        for key, values in bill_obj.items():
            table.add_row([key] + values)

        table.add_row(self.generate_total_row(bill_obj))

        print(table)

    def generate_total_row(self, bill_obj):
        """
        Generate a total row for the table.
        """
        return [
            "Total",
            round(sum([value[0] for value in bill_obj.values()]), 2),
            round(sum([value[1] for value in bill_obj.values()]), 2),
            round(sum([value[2] for value in bill_obj.values()]), 2),
            round(sum([value[3] for value in bill_obj.values()]), 2),
            round(sum([value[4] for value in bill_obj.values()]), 2),
            round(sum([value[5] for value in bill_obj.values()]), 2),
        ]


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
        with open(self.filename, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    "Name",
                    "Veco Reading",
                    "Electric Amount",
                    "Electric Adjusted",
                    "Water",
                    "Internet",
                    "Total",
                ]
            )

            for key, values in bill_obj.items():
                writer.writerow([key] + values)

            writer.writerow(self.generate_total_row(bill_obj))

    def generate_total_row(self, bill_obj):
        """
        Generate a total row for the CSV file.
        """
        return [
            "Total",
            round(sum([value[0] for value in bill_obj.values()]), 2),
            round(sum([value[1] for value in bill_obj.values()]), 2),
            round(sum([value[2] for value in bill_obj.values()]), 2),
            round(sum([value[3] for value in bill_obj.values()]), 2),
            round(sum([value[4] for value in bill_obj.values()]), 2),
            round(sum([value[5] for value in bill_obj.values()]), 2),
        ]