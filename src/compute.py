import yaml
import csv
from collections import OrderedDict
from dateutil.relativedelta import relativedelta
from datetime import datetime
from abc import ABC, abstractmethod
from decimal import Decimal, getcontext
from pathlib import Path
from enum import Enum


class SpecificUsers(Enum):
    JACK = "Jack"
    IAN = "Ian"


class Constants:
    PRECISION = 6
    INTERNET_DISTRIBUTION_USERS = 2
    DATE_FORMAT = "%B %Y"
    FILE_EXTENSION_TXT = "txt"
    FILE_EXTENSION_CSV = "csv"


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
        self.names = list(readings.values())[0].keys()
        amounts = {
            month_year: readings["amount"]
            for month_year, readings in sorted_data.items()
        }
        water = {
            month_year: readings["water"]
            for month_year, readings in sorted_data.items()
        }
        internet = {
            month_year: readings["internet"]
            for month_year, readings in sorted_data.items()
        }
        sorted_keys = sorted(
            readings.keys(),
            reverse=True,
            key=lambda date: datetime.strptime(date, "%B %Y"),
        )
        current_month_year = sorted_keys[0]
        previous_month_year = (
            datetime.strptime(current_month_year, "%B %Y") - relativedelta(months=1)
        ).strftime("%B %Y")
        self.data = {
            "readings": readings,
            "amounts": amounts,
            "water": water,
            "internet": internet,
            "current_month_year": current_month_year,
            "previous_month_year": previous_month_year,
        }
        self.consumption_strategy = ConsumptionCalculationStrategy()
        self.percentage_strategy = PercentageCalculationStrategy()
        self.distribution_strategy = DistributionCalculationStrategy()
        self.first_meter = list(
            self.data["readings"][self.data["current_month_year"]].keys()
        )[0]

    def calculate_percentages(self, data):
        total = sum(data.values())
        return {name: (value / total) * 100 for name, value in data.items()}

    def distribute_amount(self, data, amount):
        return {name: (percentage / 100) * amount for name, percentage in data.items()}

    def write_to_file(self, filename, data):
        with open(filename, "w") as file:
            file.write(data)

    def create_filename(self, extension):
        current_month_year = self.data["current_month_year"].replace(" ", "_")
        return f"{current_month_year}.{extension}"

    def calculate_total_amount(self, data):
        return sum(value for value in data.values())

    def calculate(self):
        self.data["consumption"] = self.consumption_strategy.calculate(self.data)
        self.data["percentages"] = self.calculate_percentages(self.data["consumption"])
        self.data["distribution"] = self.distribute_amount(
            self.data["percentages"],
            self.data["amounts"][self.data["current_month_year"]],
        )

    def check_names(self):
        # Check if the names are consistent across all months
        for month, reading in self.data["readings"].items():
            if set(reading.keys()) != set(self.names):
                print(f"Warning: Names in {month} do not match initial names.")

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
        getcontext().prec = Constants.PRECISION
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
        water_recipients = [name for name in self.data["percentages"] if name != "papa"]
        water_distribution = float(water_amount / Decimal(len(water_recipients)))
        for name in water_recipients:
            self.data["adjusted_distribution"][name] += water_distribution

        # Distribute the 'internet' amount among specific users
        internet_amount = Decimal(
            self.data["internet"][self.data["current_month_year"]]
        )
        specific_users = [SpecificUsers.JACK.value, SpecificUsers.IAN.value]
        internet_distribution = float(
            internet_amount / Decimal(Constants.INTERNET_DISTRIBUTION_USERS)
        )
        for name in specific_users:
            if name in self.data["adjusted_distribution"]:
                self.data["adjusted_distribution"][name] += internet_distribution

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
        filename = self.create_filename(Constants.FILE_EXTENSION_TXT)
        output = self.display_adjusted()
        self.write_to_file(filename, output)

    def output_to_csv(self):
        filename = self.create_filename(Constants.FILE_EXTENSION_CSV)
        with open(filename, "w", newline="") as csvfile:
            fieldnames = [
                "Name",
                "Adjusted Percentage",
                "Reading",
                "Water",
                "Internet",
                "VECO",
                "Total",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            water_amount = self.data["water"][self.data["current_month_year"]]
            water_distribution = water_amount / len(self.data["percentages"])
            internet_amount = self.data["internet"][self.data["current_month_year"]]
            internet_distribution = internet_amount / 2  # distribute to 2 users only
            total_amount = 0
            for name, percentage in self.data["adjusted_percentages"].items():
                if name == self.first_meter:
                    continue
                total = self.data["adjusted_distribution"][name]
                total_without_water_and_internet = total - water_distribution
                if name in ["Jack", "Ian"]:  # distribute to Jack and Ian only
                    total_without_water_and_internet -= internet_distribution
                total_amount += total
                writer.writerow(
                    {
                        "Name": name,
                        "Adjusted Percentage": f"{percentage:.2f}%",
                        "Reading": self.data["consumption"][name],
                        "Water": f"₱{water_distribution:.2f}",
                        "Internet": (
                            f"₱{internet_distribution:.2f}"
                            if name in ["Jack", "Ian"]
                            else ""
                        ),
                        "VECO": f"₱{total_without_water_and_internet:.2f}",
                        "Total": f"₱{total:.2f}",
                    }
                )
            writer.writerow(
                {
                    "Name": "Grand Total",
                    "Adjusted Percentage": "",
                    "Reading": "",
                    "Water": "",
                    "Internet": "",
                    "VECO": "",
                    "Total": f"₱{total_amount:.2f}",
                }
            )


# Example usage
distributor = ReadingDistributor("src/readings.yml")
distributor.calculate()
distributor.display()
distributor.calculate_adjusted()
print(distributor.display_adjusted())
distributor.output_to_file()
distributor.output_to_csv()
