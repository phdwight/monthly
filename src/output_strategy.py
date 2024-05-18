import csv

from abc import ABC, abstractmethod
from prettytable import PrettyTable

class OutputStrategy(ABC):
    @abstractmethod
    def output(self, bill_obj):
        pass


class TableOutputStrategy(OutputStrategy):
    def output(self, bill_obj):
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
    def __init__(self, filename):
        self.filename = filename

    def output(self, bill_obj):
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
        return [
            "Total",
            round(sum([value[0] for value in bill_obj.values()]), 2),
            round(sum([value[1] for value in bill_obj.values()]), 2),
            round(sum([value[2] for value in bill_obj.values()]), 2),
            round(sum([value[3] for value in bill_obj.values()]), 2),
            round(sum([value[4] for value in bill_obj.values()]), 2),
            round(sum([value[5] for value in bill_obj.values()]), 2),
        ]
