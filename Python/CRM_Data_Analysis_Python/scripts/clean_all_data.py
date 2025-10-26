import os
import re
import pandas as pd
from load_data import load_crm_data
from clean_deals import clean_deals

pd.options.mode.copy_on_write = True
def _to_snake(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"\s+", "_", regex=True)
        .str.replace("-", "_")
    )
    return df

def clean_contacts(contacts: pd.DataFrame) -> pd.DataFrame:
    df = _to_snake(contacts).dropna(how="all").copy()
    df = df.drop_duplicates()
    if "email" in df.columns:
        df.loc[:, "email"] = df["email"].astype(str).str.strip().str.lower()
    if "phone" in df.columns:
        df.loc[:, "phone"] = df["phone"].astype(str).str.strip()
    return df

def clean_calls(calls: pd.DataFrame) -> pd.DataFrame:
    df = _to_snake(calls).dropna(how="all").copy()
    df = df.drop_duplicates()
    for col in df.columns:
        if re.search(r"(date|time|created|called|start|end)", col):
            try:
                df.loc[:, col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)
            except Exception:
                pass
    return df

def _clean_numeric_series(s: pd.Series) -> pd.Series:
    
    s = s.astype(str)
    s = s.str.replace("€", "", regex=False)
    s = s.str.replace("%", "", regex=False)
    s = s.str.replace(" ", "", regex=False)
    
    s = s.str.replace(".", "", regex=False)
    s = s.str.replace(",", ".", regex=False)
    return pd.to_numeric(s, errors="coerce")

def clean_spend(spend: pd.DataFrame) -> pd.DataFrame:
    df = _to_snake(spend).dropna(how="all").copy()
    df = df.drop_duplicates()

    
    for col in df.columns:
        if re.search(r"(date|time|created|updated|month|day)", col):
            try:
                df.loc[:, col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)
            except Exception:
                pass

    
    numeric_like = []
    for col in df.columns:
        if col in {"spend", "cost", "amount", "value", "budget"}:
            numeric_like.append(col)
            continue
        
        sample = df[col].dropna().astype(str).head(50)
        if not sample.empty:
            looks_num = sample.str.contains(r"^-?[\d\s\.,€%]+$", regex=True).mean() > 0.3
            if looks_num:
                numeric_like.append(col)

    for col in set(numeric_like):
        df.loc[:, col] = _clean_numeric_series(df[col])

    return df

def main():
    calls_raw, contacts_raw, deals_raw, spend_raw = load_crm_data()

    deals_cleaned    = clean_deals(deals_raw)
    contacts_cleaned = clean_contacts(contacts_raw)
    calls_cleaned    = clean_calls(calls_raw)
    spend_cleaned    = clean_spend(spend_raw)

    base_dir   = os.path.dirname(__file__)
    output_dir = os.path.abspath(os.path.join(base_dir, "..", "data_cleaned"))
    os.makedirs(output_dir, exist_ok=True)

    files = {
        "deals_cleaned.csv": deals_cleaned,
        "contacts_cleaned.csv": contacts_cleaned,
        "calls_cleaned.csv": calls_cleaned,
        "spend_cleaned.csv": spend_cleaned,
    }
    for name, df in files.items():
        path = os.path.join(output_dir, name)
        df.to_csv(path, index=False, encoding="utf-8-sig")
        print(f"[OK] Saved: {path}")

    print("\n=== Dtypes check ===")
    for name, df in files.items():
        print(name, "->", df.dtypes.to_dict())

if __name__ == "__main__":
    main()
