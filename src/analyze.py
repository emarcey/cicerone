from datetime import datetime
import matplotlib.pyplot as plt
import os
from typing import Callable, List
import pandas as pd

from src.const import FILENAME_DATE_REGEX, RESULT_DIR


def load_df(dir_entry: os.DirEntry) -> pd.DataFrame:
    df = pd.read_csv(dir_entry.path)
    filename_date = datetime.strptime(FILENAME_DATE_REGEX.findall(dir_entry.name)[0], "%Y%m%d_%H%M%S")
    df["tested_at"] = filename_date
    return df


def load_all_dfs(dir: str) -> pd.DataFrame:
    dfs: List[pd.DataFrame] = []

    for row in os.scandir(dir):
        if row.is_dir():
            continue
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

    daily_sums_df["daily_cumsum"] = daily_sums_df["daily_total"].cumsum()

    pre_result_df = (
        df[["tested_day", "result", "total"]].groupby(["tested_day", "result"]).agg({"total": "sum"}).reset_index()
    )

    pre_result_df["cumsum"] = (
        pre_result_df.groupby("result")["total"]
        .apply(lambda x: x.cumsum())
        .reset_index()
        .sort_values("level_1")["total"]
        .reset_index()["total"]
    )

    result_df = pre_result_df.merge(daily_sums_df, on="tested_day")
    result_df["daily_pct"] = result_df.apply(_calculate_percentage("total", "daily_total"), axis=1)
    result_df["daily_cum_pct"] = result_df.apply(_calculate_percentage("cumsum", "daily_cumsum"), axis=1)
    return result_df


def display_results(in_dir: str, result_df: pd.DataFrame) -> pd.DataFrame:
    output_directory = f"{in_dir}/figs"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
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
    plt.savefig(f"{output_directory}/daily_cum_pct.png")
    plt.cla()
    display_df2 = result_df[["tested_day", "result", "daily_pct"]].loc[result_df["daily_total"] >= 25].copy()
    display_df2 = display_df2.set_index("tested_day")
    display_df2.groupby("result")["daily_pct"].plot(
        legend=True,
        marker="o",
        linewidth=2,
        xlabel="% In Category",
        ylabel="Total",
        color={"miss": "red", "close": "orange", "very_close": "blue", "exact": "green"},
    )
    plt.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left", mode="expand", borderaxespad=0, ncol=4)
    plt.savefig(f"{output_directory}/daily_pct.png")


def analyze_historical_results(in_dir: str) -> None:
    dfs = load_all_dfs(in_dir)
    result_df = transform_all_dfs(dfs)
    display_results(in_dir, result_df)


if __name__ == "__main__":
    analyze_historical_results(RESULT_DIR)
