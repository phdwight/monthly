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
            bill_obj[key].append(bill_obj[key][2] + bill_obj[key][3] + bill_obj[key][4])


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

    def __init__(self, bill_type: BillType, share_count, shared_keys, adjustment_key):
        """
        Initialize an electric bill with its type, share count, shared keys, and adjustment key.
        """
        super().__init__(bill_type, share_count, shared_keys)
        self.adjustment_key = adjustment_key

    def calculate(self, data, bill_obj):
        """
        Calculate the electric bill.
        """
        # Compute monthly consumption
        electric = {}
        if len(data) < 2:
            print("There should be at least 2 data entries")
            return

        for key in data[0]["readings"]:
            electric[key] = [data[0]["readings"][key] - data[1]["readings"][key]]

        bill_obj.update(electric)

        # Compute monthly electric
        electric_amount = data[0][self.bill_type.value]
        electric_kw_total = sum(value[0] for value in bill_obj.values())

        for key in bill_obj:
            consumption = bill_obj[key][0] / electric_kw_total
            due = round(electric_amount * consumption, 3)
            bill_obj[key].append(due)

        # Adjust monthly electric
        adjustment_amount = bill_obj[self.adjustment_key][1]
        amount_to_share = round(adjustment_amount / self.share_count, 3)

        for key in bill_obj:
            adjustment = (
                amount_to_share
                if key != self.adjustment_key
                else (adjustment_amount * -1)
            )
            bill_obj[key].append(round(adjustment + bill_obj[key][1], 3))
