from typing import List
import pandas as pd


def summarize_by_title(df: pd.DataFrame, title_col: str = "title_normalized", top_n: int = 20) -> pd.DataFrame:
    """
    Возвращает топ-N тайтлов по количеству вакансий.
    """
    counts = (
        df[title_col]
        .value_counts()
        .reset_index()
        .rename(columns={"index": title_col, title_col: "vacancy_count"})
    )
    return counts.head(top_n)


def summarize_by_country_and_title(df: pd.DataFrame,
                                   country_col: str = "country",
                                   title_col: str = "title_normalized") -> pd.DataFrame:
    """
    Группировка: страна × нормализованный тайтл.
    """
    grouped = (
        df.groupby([country_col, title_col])
        .size()
        .reset_index(name="vacancy_count")
        .sort_values(["country", "vacancy_count"], ascending=[True, False])
    )
    return grouped


def build_skill_matrix(df: pd.DataFrame,
                       title_col: str = "title_normalized",
                       skill_cols: List[str] = None) -> pd.DataFrame:
    """
    Матрица: title × skill (средняя доля упоминаний скилла).
    """
    if skill_cols is None:
        skill_cols = [c for c in df.columns if c.startswith("skill_")]

    matrix = (
        df.groupby(title_col)[skill_cols]
        .mean()
        .sort_index()
    )
    return matrix
