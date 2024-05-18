import yaml


# read the yaml file
def read_yaml_file(filename):
    with open(filename, "r") as file:
        data = yaml.safe_load(file)
    return data


# compute the monthly consumpption of each member
def compute_monthly_consumption(data):
    electric = {}
    # check if there is at least 2 data entries
    if len(data) < 2:
        print("There should be at least 2 data entries")
        return

    for key in data[0]["readings"]:
        electric[key] = [data[0]["readings"][key] - data[1]["readings"][key]]

    return electric


def compute_monthly_electric(data, electric):
    electric_amount = data[0]["electric"]
    electric_kw_total = sum(value[0] for value in electric.values())

    for key in electric:
        consumption = electric[key][0] / electric_kw_total
        due = round(electric_amount * consumption, 3)
        electric[key].append(due)

    return electric


# adjust the electric obj and divide the electric consumpiton of papa to the the other members
def adjust_monthly_electric(electric):
    papa_mount = electric["Papa"][1]
    amount_to_share = round(papa_mount / 3, 3)

    for key in electric:
        adjustment = amount_to_share if key != "Papa" else (papa_mount * -1)
        electric[key].append(round(adjustment + electric[key][1], 3))

    return electric


def add_water_bill(data, bill_obj):
    water_amount = data[0]["water"]
    water_share = round(water_amount / 3, 3)
    for key in bill_obj:
        if key != "Papa":
            bill_obj[key].append(water_share)
        else:
            bill_obj[key].append(0)

    return bill_obj


def add_internet_bill(data, bill_obj):
    internet_amount = data[0]["internet"]
    internet_share = round(internet_amount / 2, 3)

    for key in bill_obj:
        bill_obj[key].append(internet_share if key in ["Jack", "Ian"] else 0)

    return bill_obj


data = read_yaml_file("src/bills2.yaml")
electric = compute_monthly_consumption(data)
print(electric)
bill_obj = compute_monthly_electric(data, electric)
print(bill_obj)
bill_obj = adjust_monthly_electric(bill_obj)
print(bill_obj)
bill_obj = add_water_bill(data, bill_obj)
print(bill_obj)
bill_obj = add_internet_bill(data, bill_obj)
print(bill_obj)
