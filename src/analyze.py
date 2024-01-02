from datetime import datetime
import matplotlib.pyplot as plt
import os
from typing import Callable, List
import pandas as pd

from src.const import FILENAME_DATE_REGEX, RESULT_DIR
from src.data_models import GuessProximity


def load_df(dir_entry: os.DirEntry) -> pd.DataFrame:
    df = pd.read_csv(dir_entry.path)
    filename_date = datetime.strptime(FILENAME_DATE_REGEX.findall(dir_entry.name)[0], "%Y%m%d_%H%M%S")
    df["tested_at"] = filename_date
    return df


def load_all_dfs(dir: str) -> pd.DataFrame:
    dfs: List[pd.DataFrame] = []

    for row in os.scandir(dir):
        dfs.append(load_df(row))
    return pd.concat(dfs)


def _to_start_of_day(dt: datetime) -> datetime:
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def _calculate_percentage(numerator_name: str, denominator_name: str) -> Callable:
    def _calculate_percentage_inner(row: pd.Series) -> float:
        if row[denominator_name] == 0:
            return 0
        raw = row[numerator_name] / row[denominator_name]
        return round(raw, 4) * 100

    return _calculate_percentage_inner


def transform_all_dfs(in_df: pd.DataFrame) -> pd.DataFrame:
    df = in_df.copy()
    df["tested_day"] = df["tested_at"].apply(_to_start_of_day)
    df["total"] = 1
    daily_sums_df = (
        df[["tested_day", "style"]].groupby("tested_day").count().reset_index().rename(columns={"style": "daily_total"})
    )

    first_date = df["tested_day"].min()
    last_date = df["tested_day"].max()
    date_df = pd.DataFrame(pd.date_range(first_date, last_date, freq="D")).rename(columns={0: "tested_day"})
    guess_proximity_df = pd.DataFrame([x.name for x in list(GuessProximity)]).rename(columns={0: "result"})
    guess_date_df = date_df.merge(guess_proximity_df, how="cross")

    ext_daily_sums_df = date_df.merge(daily_sums_df, how="left", on="tested_day").fillna(0)
    ext_daily_sums_df["daily_cumsum"] = ext_daily_sums_df["daily_total"].cumsum()

    ext_date_df = guess_date_df.merge(
        df[["tested_day", "result", "total"]], how="left", on=["tested_day", "result"]
    ).fillna(0)

    pre_result_df = (
        ext_date_df[["tested_day", "result", "total"]]
        .groupby(["tested_day", "result"])
        .agg({"total": "sum"})
        .reset_index()
    )

    pre_result_df["cumsum"] = (
        pre_result_df.groupby("result")["total"]
        .apply(lambda x: x.cumsum())
        .reset_index()
        .sort_values("level_1")["total"]
        .reset_index()["total"]
    )

    result_df = pre_result_df.merge(ext_daily_sums_df, on="tested_day")
    result_df["daily_pct"] = result_df.apply(_calculate_percentage("total", "daily_total"), axis=1)
    result_df["daily_cum_pct"] = result_df.apply(_calculate_percentage("cumsum", "daily_cumsum"), axis=1)
    return result_df


def display_results(result_df: pd.DataFrame) -> pd.DataFrame:
    display_df = result_df[["tested_day", "result", "daily_cum_pct"]].copy()
    display_df = display_df.set_index("tested_day")
    display_df.groupby("result")["daily_cum_pct"].plot(
        legend=True,
        marker="o",
        linewidth=2,
        xlabel="Testing Date",
        ylabel="Cumulative %",
        color={"miss": "red", "close": "orange", "very_close": "blue", "exact": "green"},
    )
    plt.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left", mode="expand", borderaxespad=0, ncol=4)
    plt.show()


def analyze_historical_results(in_dir: str) -> None:
    dfs = load_all_dfs(in_dir)
    result_df = transform_all_dfs(dfs)
    display_results(result_df)


if __name__ == "__main__":
    analyze_historical_results(RESULT_DIR)
