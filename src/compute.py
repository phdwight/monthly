import yaml
from collections import OrderedDict
from dateutil.relativedelta import relativedelta
from datetime import datetime
from abc import ABC, abstractmethod


class CalculationStrategy(ABC):
    @abstractmethod
    def calculate(self, data):
        pass


class AdjustedPercentageCalculationStrategy(CalculationStrategy):
    def calculate(self, data):
        consumption_without_meter1 = {
            k: v for k, v in data["consumption"].items() if k != "Meter1"
        }
        total_consumption = sum(consumption_without_meter1.values())
        percentages = {
            name: (consumption / total_consumption) * 100
            for name, consumption in consumption_without_meter1.items()
        }
        meter1_percentage = data["percentages"].get("Meter1", 0)
        adjustment = meter1_percentage / len(percentages)
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
        with open(yaml_file, "r") as file:
            data = yaml.safe_load(file)
        sorted_data = OrderedDict(sorted(data.items(), reverse=True))
        readings = {
            month_year: readings["readings"]
            for month_year, readings in sorted_data.items()
        }
        amounts = {
            month_year: readings["amount"]
            for month_year, readings in sorted_data.items()
        }
        current_month_year = list(readings.keys())[0]
        previous_month_year = (
            datetime.strptime(current_month_year, "%B %Y") - relativedelta(months=1)
        ).strftime("%B %Y")
        self.data = {
            "readings": readings,
            "amounts": amounts,
            "current_month_year": current_month_year,
            "previous_month_year": previous_month_year,
        }
        self.consumption_strategy = ConsumptionCalculationStrategy()
        self.percentage_strategy = PercentageCalculationStrategy()
        self.distribution_strategy = DistributionCalculationStrategy()

    def calculate(self):
        self.data["consumption"] = self.consumption_strategy.calculate(self.data)
        self.data["percentages"] = self.percentage_strategy.calculate(self.data)
        self.data["distribution"] = self.distribution_strategy.calculate(self.data)

    def display(self):
        print(f"{self.data['current_month_year']}:")
        for name in self.data["readings"][self.data["current_month_year"]]:
            print(
                f"  {name}: Consumption = {self.data['consumption'][name]}, Percentage = {self.data['percentages'][name]:.2f}%, Amount = ${self.data['distribution'][name]:.2f}"
            )

    def calculate_adjusted(self):
        self.data["adjusted_percentages"] = (
            AdjustedPercentageCalculationStrategy().calculate(self.data)
        )
        self.data[
            "adjusted_distribution"
        ] = DistributionCalculationStrategy().calculate(
            {**self.data, "percentages": self.data["adjusted_percentages"]}
        )

    def display_adjusted(self):
        print(f"Adjusted {self.data['current_month_year']}:")
        for name in self.data["adjusted_percentages"]:
            if name == "Meter1":
                continue
            print(
                f"  {name}: Consumption = {self.data['consumption'][name]}, Adjusted Percentage = {self.data['adjusted_percentages'][name]:.2f}%, Adjusted Amount = ${self.data['adjusted_distribution'][name]:.2f}"
            )


# Example usage
distributor = ReadingDistributor("src/readings.yml")
distributor.calculate()
distributor.display()
distributor.calculate_adjusted()
distributor.display_adjusted()
