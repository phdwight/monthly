from enum import Enum
from abc import ABC, abstractmethod


class BillType(Enum):
    WATER = "water"
    INTERNET = "internet"
    ELECTRIC = "electric"
    TOTAL = "total"


class Bill(ABC):
    def __init__(self, bill_type: BillType, share_count, shared_keys):
        self.bill_type = bill_type
        self.share_count = share_count
        self.shared_keys = shared_keys

    @abstractmethod
    def calculate(self, data, bill_obj):
        pass


class TotalBill(Bill):
    def calculate(self, data, bill_obj):
        for key in bill_obj:
            bill_obj[key].append(bill_obj[key][2] + bill_obj[key][3] + bill_obj[key][4])


class WaterBill(Bill):
    def calculate(self, data, bill_obj):
        bill_amount = data[0][self.bill_type.value]
        bill_share = round(bill_amount / self.share_count, 3)

        for key in bill_obj:
            bill_obj[key].append(bill_share if key in self.shared_keys else 0)


class InternetBill(Bill):
    def calculate(self, data, bill_obj):
        bill_amount = data[0][self.bill_type.value]
        bill_share = round(bill_amount / self.share_count, 3)

        for key in bill_obj:
            bill_obj[key].append(bill_share if key in self.shared_keys else 0)


class ElectricBill(Bill):
    def __init__(self, bill_type: BillType, share_count, shared_keys, adjustment_key):
        super().__init__(bill_type, share_count, shared_keys)
        self.adjustment_key = adjustment_key

    def calculate(self, data, bill_obj):
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
