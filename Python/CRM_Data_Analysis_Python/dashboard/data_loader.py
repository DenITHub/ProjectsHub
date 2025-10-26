import os
import pandas as pd

def load_data():
    base_dir = os.path.dirname(__file__)
    data_dir = os.path.abspath(os.path.join(base_dir, "..", "data"))

    deals = pd.read_excel(os.path.join(data_dir, "deals.xlsx"))
    contacts = pd.read_excel(os.path.join(data_dir, "contacts.xlsx"))
    calls = pd.read_excel(os.path.join(data_dir, "calls.xlsx"))
    spend = pd.read_excel(os.path.join(data_dir, "spend.xlsx"))

    # --- Clean deals ---
    deals["Created Time"] = pd.to_datetime(deals["Created Time"], errors="coerce", dayfirst=True)
    deals["Closing Date"] = pd.to_datetime(deals["Closing Date"], errors="coerce", dayfirst=True)

    for col in ["Initial Amount Paid", "Offer Total Amount"]:
        deals[col] = (
            deals[col].astype(str).str.replace("€", "").str.replace(",", "").str.strip()
        )
        deals[col] = pd.to_numeric(deals[col], errors="coerce")

    deals["stage"] = deals["Stage"].astype(str).str.lower().str.strip()
    deals["is_won"] = deals["stage"] == "payment done"
    deals.columns = deals.columns.str.lower().str.replace(" ", "_")

    # Нормализация для фильтров
    if "created_time" in deals.columns:
        deals["created_time"] = pd.to_datetime(deals["created_time"], errors="coerce")
    if "product" in deals.columns:
        deals["product"] = deals["product"].astype(str).str.strip()

    # Приведение имен колонок в contacts/calls к snake_case
    contacts.columns = contacts.columns.str.lower().str.replace(" ", "_")
    calls.columns = calls.columns.str.lower().str.replace(" ", "_")

    return deals, contacts, calls, spend
