import pandas as pd

def clean_deals(df):
    df = df.copy()

    # Преобразуем даты
    df["Closing Date"] = pd.to_datetime(df["Closing Date"], errors="coerce", dayfirst=True)
    df["Created Time"] = pd.to_datetime(df["Created Time"], errors="coerce", dayfirst=True)

    # Очистка валютных полей
    for col in ["Initial Amount Paid", "Offer Total Amount"]:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace("€", "", regex=False)
            .str.replace(",", "", regex=False)
            .str.replace(" ", "", regex=False)
            .replace("nan", None)
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Удаляем строки без ID или Stage
    df = df[df["Id"].notna() & df["Stage"].notna()].copy()

    # Приводим имена колонок к нижнему регистру с подчёркиванием
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )

    return df
