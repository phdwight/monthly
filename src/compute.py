import yaml
from collections import OrderedDict
from dateutil.relativedelta import relativedelta
from datetime import datetime


class ReadingDistributor:
    def __init__(self, yaml_file):
        with open(yaml_file, "r") as file:
            data = yaml.safe_load(file)
        sorted_data = OrderedDict(sorted(data.items(), reverse=True))
        self.readings = {
            month_year: readings["readings"]
            for month_year, readings in sorted_data.items()
        }
        self.amounts = {
            month_year: readings["amount"]
            for month_year, readings in sorted_data.items()
        }
        self.consumptions = self.calculate_consumptions()
        self.total_consumption = {
            month_year: sum(consumption.values())
            for month_year, consumption in self.consumptions.items()
        }
        self.percentages = self.calculate_percentages()
        self.distribution = self.distribute_amount()

    def calculate_consumptions(self):
        consumptions = {}
        month_years = list(self.readings.keys())
        for i, month_year in enumerate(month_years):
            current_readings = self.readings[month_year]
            previous_month_year = (
                datetime.strptime(month_year, "%B %Y") - relativedelta(months=1)
            ).strftime("%B %Y")
            previous_readings = self.readings.get(
                previous_month_year, {name: 0 for name in current_readings}
            )
            consumptions[month_year] = {
                name: current_readings[name] - previous_readings.get(name, 0)
                for name in current_readings
            }
        return consumptions

    def calculate_percentages(self):
        percentages = {}
        for month_year in self.consumptions:
            total_consumption = self.total_consumption[month_year]
            percentages[month_year] = {
                name: (consumption / total_consumption) * 100
                for name, consumption in self.consumptions[month_year].items()
            }
        return percentages

    def distribute_amount(self):
        distribution = {}
        for month_year in self.percentages:
            distribution[month_year] = {
                name: (percentage / 100) * self.amounts[month_year]
                for name, percentage in self.percentages[month_year].items()
            }
        return distribution

    def display(self):
        for month_year in sorted(self.readings.keys(), reverse=True):
            print(f"{month_year}:")
            for name in self.readings[month_year]:
                print(
                    f"  {name}: Consumption = {self.consumptions[month_year][name]}, Percentage = {self.percentages[month_year][name]:.2f}%, Amount = ${self.distribution[month_year][name]:.2f}"
                )


# Example usage
distributor = ReadingDistributor("src/readings.yml")
distributor.display()
