import yaml
import csv
from collections import OrderedDict
from dateutil.relativedelta import relativedelta
from datetime import datetime
from abc import ABC, abstractmethod
from decimal import Decimal, getcontext
from pathlib import Path


class CalculationStrategy(ABC):
    @abstractmethod
    def calculate(self, data):
        pass


class AdjustedPercentageCalculationStrategy(CalculationStrategy):
    def calculate(self, data):
        # Get the name of the first meter
        first_meter = list(data["consumption"].keys())[0]
        consumption_without_first_meter = {
            k: v for k, v in data["consumption"].items() if k != first_meter
        }
        total_consumption = sum(consumption_without_first_meter.values())
        percentages = {
            name: (consumption / total_consumption) * 100
            for name, consumption in consumption_without_first_meter.items()
        }
        first_meter_percentage = data["percentages"].get(first_meter, 0)
        adjustment = first_meter_percentage / len(percentages)
        return {
            name: percentage + adjustment for name, percentage in percentages.items()
        }


class ConsumptionCalculationStrategy(CalculationStrategy):
    def calculate(self, data):
        current_readings = data["readings"][data["current_month_year"]]
        previous_readings = data["readings"].get(
            data["previous_month_year"], {name: 0 for name in current_readings}
        )
        return {
            name: current_readings[name] - previous_readings.get(name, 0)
            for name in current_readings
        }


class PercentageCalculationStrategy(CalculationStrategy):
    def calculate(self, data):
        total_consumption = sum(data["consumption"].values())
        return {
            name: (consumption / total_consumption) * 100
            for name, consumption in data["consumption"].items()
        }


class DistributionCalculationStrategy(CalculationStrategy):
    def calculate(self, data):
        return {
            name: (percentage / 100) * data["amounts"][data["current_month_year"]]
            for name, percentage in data["percentages"].items()
        }


class ReadingDistributor:
    def __init__(self, yaml_file):
        data = yaml.safe_load(Path(yaml_file).read_text())
        sorted_data = dict(sorted(data.items(), reverse=True))
        readings = {
            month_year: readings["readings"]
            for month_year, readings in sorted_data.items()
        }
        amounts = {
            month_year: readings["amount"]
            for month_year, readings in sorted_data.items()
        }
        water = {
            month_year: readings["water"]
            for month_year, readings in sorted_data.items()
        }
        sorted_keys = sorted(readings.keys(), reverse=True, key=lambda date: datetime.strptime(date, "%B %Y"))
        current_month_year = sorted_keys[0]
        previous_month_year = (
            datetime.strptime(current_month_year, "%B %Y") - relativedelta(months=1)
        ).strftime("%B %Y")
        self.data = {
            "readings": readings,
            "amounts": amounts,
            "water": water,
            "current_month_year": current_month_year,
            "previous_month_year": previous_month_year,
        }
        self.consumption_strategy = ConsumptionCalculationStrategy()
        self.percentage_strategy = PercentageCalculationStrategy()
        self.distribution_strategy = DistributionCalculationStrategy()
        self.first_meter = list(
            self.data["readings"][self.data["current_month_year"]].keys()
        )[0]

    def calculate(self):
        self.data["consumption"] = self.consumption_strategy.calculate(self.data)
        self.data["percentages"] = self.percentage_strategy.calculate(self.data)
        self.data["distribution"] = self.distribution_strategy.calculate(self.data)

    def display(self):
        print(f"{self.data['current_month_year']}:")
        for name in self.data["readings"][self.data["current_month_year"]]:
            print(
                f"  {name}: Consumption = {self.data['consumption'][name]}, Percentage = {self.data['percentages'][name]:.2f}%, Amount = ₱{self.data['distribution'][name]:.2f}"
            )

    def calculate_adjusted(self):
        getcontext().prec = 6  # set the precision you need
        # Get the name of the first meter
        first_meter_percentage = self.data["percentages"].pop(self.first_meter, 0)
        adjustment_percentage = first_meter_percentage / len(self.data["percentages"])
        self.data["adjusted_percentages"] = {
            name: float(Decimal(percentage) + Decimal(adjustment_percentage))
            for name, percentage in self.data["percentages"].items()
        }
        self.data["adjusted_distribution"] = {
            name: float(
                (Decimal(percentage) / 100)
                * Decimal(self.data["amounts"][self.data["current_month_year"]])
            )
            for name, percentage in self.data["adjusted_percentages"].items()
        }
        self.data["adjusted_distribution"][self.first_meter] = 0

        # Distribute the 'water' amount equally among the last three meters
        water_amount = Decimal(self.data["water"][self.data["current_month_year"]])
        water_distribution = float(
            water_amount / Decimal(len(self.data["percentages"]))
        )
        for name in self.data["percentages"]:
            self.data["adjusted_distribution"][name] += water_distribution

    def display_adjusted(self):
        output = [f"{self.data['current_month_year']}:"] 
        water_amount = self.data["water"][self.data["current_month_year"]]
        water_distribution = water_amount / len(self.data["percentages"])
        for name, percentage in self.data["adjusted_percentages"].items():
            if name == self.first_meter:
                continue
            output.append(
                f"  {name}: Adjusted Percentage = {percentage:.2f}%, Adjusted Reading = {self.data['consumption'][name]}, Water Amount = ₱{water_distribution:.2f}, Total = ₱{self.data['adjusted_distribution'][name]:.2f}"
            )
        return "\n".join(output)

    def output_to_file(self):
        current_month_year = self.data["current_month_year"].replace(" ", "_")
        filename = f"{current_month_year}.txt"
        output = [f"Adjusted {self.data['current_month_year']}:"]
        water_amount = self.data["water"][self.data["current_month_year"]]
        water_distribution = water_amount / len(self.data["percentages"])
        for name, percentage in self.data["adjusted_percentages"].items():
            if name == self.first_meter:
                continue
            output.append(
                f"  {name}: Adjusted Percentage = {percentage:.2f}%, Reading = {self.data['consumption'][name]}, Water Amount = ₱{water_distribution:.2f}, Total = ₱{self.data['adjusted_distribution'][name]:.2f}"
            )
        total_adjusted_amount = sum(
            value
            for key, value in self.data["adjusted_distribution"].items()
            if key != self.first_meter
        )
        output.append(f"Total Adjusted Amount = ₱{total_adjusted_amount:.2f}")
        Path(filename).write_text("\n".join(output))

    def output_to_csv(self):
        current_month_year = self.data["current_month_year"].replace(" ", "_")
        filename = f"{current_month_year}.csv"
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['Name', 'Adjusted Percentage', 'Reading', 'Water Amount', 'Total']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            water_amount = self.data["water"][self.data["current_month_year"]]
            water_distribution = water_amount / len(self.data["percentages"])
            for name, percentage in self.data["adjusted_percentages"].items():
                if name == self.first_meter:
                    continue
                writer.writerow({
                    'Name': name,
                    'Adjusted Percentage': f"{percentage:.2f}%",
                    'Reading': self.data['consumption'][name],
                    'Water Amount': f"₱{water_distribution:.2f}",
                    'Total': f"₱{self.data['adjusted_distribution'][name]:.2f}"
                })


# Example usage
distributor = ReadingDistributor("src/readings.yml")
distributor.calculate()
distributor.display()
distributor.calculate_adjusted()
print(distributor.display_adjusted())
distributor.output_to_file()
distributor.output_to_csv()
