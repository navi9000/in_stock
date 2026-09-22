import sys
import csv
from datetime import datetime
from decimal import Decimal

def stock_filename(YYYY_MM_DD):
    return f"./stock/stock_{YYYY_MM_DD}.csv"

def invent_filename(YYYY_MM):
    return f"./invent_trans/invent_trans_{YYYY_MM}.csv"

def get_date():
    try:
        first_argument = sys.argv[1]
        dt = datetime.strptime(first_argument, "%Y-%m-%d")
        start_date = "2025-05-01"
        end_date = "2025-07-31"
        if dt < datetime.fromisoformat(start_date) or dt > datetime.fromisoformat(end_date):
            print(f"Invalid date range. Valid are values from {start_date} to {end_date}")
            exit()
        return first_argument
    except IndexError:
        print("No user input. You must provide a value in the YYYY-MM-DD format.")
        exit()
    except ValueError:
        print("Invalid user input. You must provide a value in the YYYY-MM-DD format.")
        exit()

def get_transaction_list(filename, date_limit, item_list={}):
    with open(filename, mode="r") as file:
        invent_dict = csv.DictReader(file, delimiter=";")
        for row in invent_dict:
            row_date = row["trans_date"]
            if datetime.fromisoformat(row_date) > datetime.fromisoformat(date_limit):
                continue
            item_id = row["item_id"]
            item = item_list[item_id] if item_id in item_list else {}
            location_id = row["location_id"]
            location = item[location_id] if location_id in item else {"trans_date": row_date, "qty": Decimal("0"), "cost_amount": Decimal("0")}
            qty = Decimal(row["qty"])
            cost_amount = Decimal(row["cost_amount"])
            location.update({"qty": location["qty"] + qty, "cost_amount": location["cost_amount"] + cost_amount})
            if datetime.fromisoformat(row_date) > datetime.fromisoformat(location["trans_date"]):
                location.update({"trans_date": row_date})
            item[location_id] = location
            item_list[item_id] = item

    return item_list

def save_stock_values_for_date(item_list, date):
    with open(stock_filename(date), mode="w") as file:
        writer = csv.DictWriter(file, delimiter=";", fieldnames=["item_id", "location_id", "trans_date", "qty", "cost_amount"], lineterminator="\n")
        writer.writeheader()
        for item_id in item_list:
            for location_id in item_list[item_id]:
                trans_date = item_list[item_id][location_id]["trans_date"]
                qty = item_list[item_id][location_id]["qty"]
                cost_amount = item_list[item_id][location_id]["cost_amount"]
                writer.writerow({
                    "item_id": item_id,
                    "location_id": location_id,
                    "trans_date": trans_date,
                    "qty": qty,
                    "cost_amount": cost_amount
                })


def main():
    user_input = get_date()

    item_list = get_transaction_list(filename=stock_filename("2025_04_30"), date_limit=user_input)
    item_list = get_transaction_list(filename=invent_filename("2025_05"), date_limit=user_input, item_list=item_list)
    item_list = get_transaction_list(filename=invent_filename("2025_06"), date_limit=user_input, item_list=item_list)
    item_list = get_transaction_list(filename=invent_filename("2025_07"), date_limit=user_input, item_list=item_list)

    save_stock_values_for_date(item_list, user_input.replace("-", "_"))

main()
