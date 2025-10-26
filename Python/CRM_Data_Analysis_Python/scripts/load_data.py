import pandas as pd
import os

def load_crm_data():
    base_dir = os.path.dirname(__file__)
    data_dir = os.path.abspath(os.path.join(base_dir, "..", "data"))

    deals = pd.read_excel(os.path.join(data_dir, "deals.xlsx"))
    contacts = pd.read_excel(os.path.join(data_dir, "contacts.xlsx"))
    calls = pd.read_excel(os.path.join(data_dir, "calls.xlsx"))
    spend = pd.read_excel(os.path.join(data_dir, "spend.xlsx"))

    return calls, contacts, deals, spend
