from abc import ABC, abstractmethod
from enum import Enum
import yaml

class BillType(Enum):
    WATER = "water"
    INTERNET = "internet"

class Bill(ABC):
    def __init__(self, bill_type: BillType, share_count, shared_keys):
        self.bill_type = bill_type
        self.share_count = share_count
        self.shared_keys = shared_keys

    @abstractmethod
    def calculate(self, data, bill_obj):
        pass

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

class BillCalculator:
    def __init__(self, filename, bills):
        self.data = self.read_yaml_file(filename)
        self.bills = bills
        self.bill_obj = {}

    def read_yaml_file(self, filename):
        with open(filename, "r") as file:
            data = yaml.safe_load(file)
        return data

    def compute_monthly_consumption(self):
        electric = {}
        if len(self.data) < 2:
            print("There should be at least 2 data entries")
            return

        for key in self.data[0]["readings"]:
            electric[key] = [self.data[0]["readings"][key] - self.data[1]["readings"][key]]

        self.bill_obj = electric

    def compute_monthly_electric(self):
        electric_amount = self.data[0]["electric"]
        electric_kw_total = sum(value[0] for value in self.bill_obj.values())

        for key in self.bill_obj:
            consumption = self.bill_obj[key][0] / electric_kw_total
            due = round(electric_amount * consumption, 3)
            self.bill_obj[key].append(due)

    def adjust_monthly_electric(self):
        papa_mount = self.bill_obj["Papa"][1]
        amount_to_share = round(papa_mount / 3, 3)

        for key in self.bill_obj:
            adjustment = amount_to_share if key != "Papa" else (papa_mount * -1)
            self.bill_obj[key].append(round(adjustment + self.bill_obj[key][1], 3))

    def calculate(self):
        self.compute_monthly_consumption()
        self.compute_monthly_electric()
        self.adjust_monthly_electric()

        for bill in self.bills:
            bill.calculate(self.data, self.bill_obj)

        print(self.bill_obj)


WATER_SHARED_KEYS = ["Jack", "Ian", "Ajin"]
INTERNET_SHARED_KEYS = ["Jack", "Ian"]

bills = [
    WaterBill(BillType.WATER, 3, WATER_SHARED_KEYS),
    InternetBill(BillType.INTERNET, 2, INTERNET_SHARED_KEYS)
]

calculator = BillCalculator("src/bills2.yaml", bills)
calculator.calculate()