import yaml
from prettytable import PrettyTable, ALL

class BillCalculator:
    def __init__(self, filename):
        self.data = self.read_yaml_file(filename)
        self.months = sorted(list(self.data.keys()))
        self.individual_amounts = {}
        self.table = PrettyTable()
        self.table.title = 'Electricity Consumption'
        self.table.field_names = ["Person", "Previous Reading", "Current Reading", "Consumption", "Percentage"]
        self.table.align = "l"  # align columns to the left

    def read_yaml_file(self, filename):
        with open(filename, "r") as file:
            data = yaml.safe_load(file)
        return data

    def compute_individual_amounts(self):
        for i in range(1, len(self.months)):
            current_month = self.months[i]
            previous_month = self.months[i - 1]

            current_readings = self.data[current_month]["readings"]
            previous_readings = self.data[previous_month]["readings"]
            total_current_readings = sum(current_readings.values())
            total_previous_readings = sum(previous_readings.values())

            total_consumption = total_current_readings - total_previous_readings
            electric_amount = self.data[current_month]["electric"]

            for person in current_readings.keys():
                individual_consumption = (
                    current_readings[person] - previous_readings.get(person, 0)
                )
                proportion = individual_consumption / total_consumption
                individual_amount = proportion * electric_amount

                if person not in self.individual_amounts:
                    self.individual_amounts[person] = {
                "consumption": 0,
                "amount": 0
                }
                self.individual_amounts[person]["consumption"] += individual_consumption
                self.individual_amounts[person]["amount"] += round(individual_amount, 3)

        return self.individual_amounts

    def create_table(self):
        total_consumption = sum([data["consumption"] for data in self.individual_amounts.values()])
        for person, data in self.individual_amounts.items():
            previous_reading = self.data[self.months[-2]]["readings"].get(person, 0)
            current_reading = self.data[self.months[-1]]["readings"].get(person, 0)
            consumption = data["consumption"]
            percentage = (consumption / total_consumption) * 100
            self.table.add_row([person, previous_reading, current_reading, consumption, f"{percentage:.2f}%"])
        self.table.hrules = ALL  # add horizontal lines between rows

    def display_table(self):
        print(self.table)  # print table

calculator = BillCalculator("src/bills.yaml")
individual_amounts = calculator.compute_individual_amounts()
calculator.create_table()
calculator.display_table()
print(individual_amounts)