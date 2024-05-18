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

    def compute_individual_payments(self):
        individual_payments = {}
        current_electric = self.data[self.months[-1]]["electric"]
        total_consumption = sum([data["consumption"] for data in self.individual_amounts.values()])
        for person, data in self.individual_amounts.items():
            consumption = data["consumption"]
            percentage = consumption / total_consumption
            payment = current_electric * percentage
            individual_payments[person] = round(payment, 3)
        return individual_payments

    def create_payment_table(self):
        self.payment_table = PrettyTable()
        self.payment_table.title = 'Electricity Payments'
        self.payment_table.field_names = ["Person", "Payment"]
        self.payment_table.align = "l"  # align columns to the left
        for person, payment in self.compute_individual_payments().items():
            self.payment_table.add_row([person, payment])
        self.payment_table.hrules = ALL  # add horizontal lines between rows

    def display_payment_table(self):
        print(self.payment_table)  # print table

    def redistribute_payment(self):
        individual_payments = self.compute_individual_payments()
        if "Papa" not in individual_payments:
            return individual_payments

        num_other_people = len(individual_payments) - 1
        redistributed_amount = individual_payments["Papa"] / num_other_people
        for person in individual_payments:
            if person != "Papa":
                individual_payments[person] += redistributed_amount
        individual_payments["Papa"] = 0

        return individual_payments
    
    def create_redistributed_payment_table(self):
        self.redistributed_payment_table = PrettyTable()
        self.redistributed_payment_table.title = 'Redistributed Electricity Payments'
        self.redistributed_payment_table.field_names = ["Person", "Redistributed Payment"]
        self.redistributed_payment_table.align = "l"  # align columns to the left
        redistributed_payments = self.redistribute_payment()
        for person, payment in redistributed_payments.items():
            self.redistributed_payment_table.add_row([person, round(payment, 3)])
        self.redistributed_payment_table.hrules = ALL  # add horizontal lines between rows

    def display_redistributed_payment_table(self):
        print(self.redistributed_payment_table)  # print table

# usage
calculator = BillCalculator("src/bills.yaml")
calculator.compute_individual_amounts()
calculator.create_table()
calculator.display_table()
calculator.create_payment_table()
calculator.display_payment_table()
calculator.create_redistributed_payment_table()
calculator.display_redistributed_payment_table()