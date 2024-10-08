"""
This module defines the types of bills and their calculation strategies.

It defines a BillType enum for different types of bills, and an abstract base class Bill for bills. The Bill class
has a method calculate that must be overridden by subclasses to calculate the bill.

The module also defines four concrete subclasses of Bill: TotalBill, WaterBill, InternetBill, and ElectricBill. Each
of these classes overrides the calculate method to calculate the bill in a different way.

The TotalBill class calculates the total bill by summing the other bills. The WaterBill and InternetBill classes
calculate the bill by dividing the total bill amount by the number of shares. The ElectricBill class calculates the
bill by dividing the total bill amount by the total consumption, and then adjusting the bill for each share based on
an adjustment key.
"""

from enum import Enum
from abc import ABC, abstractmethod


class BillType(Enum):
    """
    Enum class for different types of bills.
    """

    WATER = "water"
    INTERNET = "internet"
    ELECTRIC = "electric"
    TOTAL = "total"


class Bill(ABC):
    """
    Abstract base class for a bill.
    """

    def __init__(self, bill_type: BillType, share_count, shared_keys):
        """
        Initialize a bill with its type, share count, and shared keys.
        """
        self.bill_type = bill_type
        self.share_count = share_count
        self.shared_keys = shared_keys

    @abstractmethod
    def calculate(self, data, bill_obj):
        """
        Abstract method to calculate the bill.
        """


class TotalBill(Bill):
    """
    Class for the total bill.
    """

    def calculate(self, data, bill_obj):
        """
        Calculate the total bill.
        """
        for key in bill_obj:
            bill_obj[key].append(
                round(bill_obj[key][2] + bill_obj[key][3] + bill_obj[key][4], 3)
            )


class WaterBill(Bill):
    """
    Class for the water bill.
    """

    def calculate(self, data, bill_obj):
        """
        Calculate the water bill.
        """
        bill_amount = data[0][self.bill_type.value]
        bill_share = round(bill_amount / self.share_count, 3)

        for key in bill_obj:
            bill_obj[key].append(bill_share if key in self.shared_keys else 0)


class InternetBill(Bill):
    """
    Class for the internet bill.
    """

    def calculate(self, data, bill_obj):
        """
        Calculate the internet bill.
        """
        bill_amount = data[0][self.bill_type.value]
        bill_share = round(bill_amount / self.share_count, 3)

        for key in bill_obj:
            bill_obj[key].append(bill_share if key in self.shared_keys else 0)


class ElectricBill(Bill):
    """
    Class for the electric bill.
    """

    # pylint: disable=R0913,R0917
    def __init__(
        self, bill_type: BillType, share_count, shared_keys, adjustment_key, threshold
    ):
        """
        Initialize an electric bill with its type, share count, shared keys, and adjustment key.
        """
        super().__init__(bill_type, share_count, shared_keys)
        self.adjustment_key = adjustment_key
        self.threshold = threshold  # amount to be shared, and the rest to be adjusted

    def calculate(self, data, bill_obj):
        """
        Calculate the electric bill.
        """
        # Ensure there are at least 2 data entries
        if len(data) < 2:
            print("Error: There should be at least 2 data entries")
            return

        # Compute monthly consumption
        electric = self.compute_monthly_consumption(data)
        bill_obj.update(electric)

        # Compute monthly electric amounts
        electric_amount = data[0][self.bill_type.value]
        electric_kw_total = sum(value[0] for value in bill_obj.values())
        self.compute_monthly_electric(bill_obj, electric_amount, electric_kw_total)

        # Adjust monthly electric amounts
        self.adjust_monthly_electric(bill_obj)

    def compute_monthly_consumption(self, data):
        """
        Compute the monthly consumption based on the readings.
        """
        electric = {}
        for key in data[0]["readings"]:
            electric[key] = [data[0]["readings"][key] - data[1]["readings"][key]]
        return electric

    def compute_monthly_electric(self, bill_obj, electric_amount, electric_kw_total):
        """
        Compute the monthly electric amounts for each participant.
        """
        for key in bill_obj:
            consumption = bill_obj[key][0] / electric_kw_total
            due = round(electric_amount * consumption, 3)
            bill_obj[key].append(due)

    def adjust_monthly_electric(self, bill_obj):
        """
        Adjust the monthly electric amounts based on the threshold and adjustment key.
        """
        adjustment_amount = bill_obj[self.adjustment_key][1]  # Papa's bill
        additional_amount = max(0, adjustment_amount - self.threshold["amount"])
        distributable_amount = min(adjustment_amount, self.threshold["amount"])

        # Calculate the amount to share among the participants
        amount_to_share = round(distributable_amount / self.share_count, 3)
        print(f"Amount to share: {amount_to_share}")

        # Adjust the bill for each participant
        for key in bill_obj:
            if key == self.adjustment_key:
                adjustment = -adjustment_amount
            else:
                adjustment = amount_to_share

            if key == self.threshold["key"]:
                adjustment += additional_amount

            bill_obj[key].append(round(adjustment + bill_obj[key][1], 3))
