import pandas as pd

ID_COLS = ["country", "year"]


def missing_report(df, id_cols=ID_COLS, verbose=True):
    """Report missing values in the wide country/year/indicator table.

    Returns (summary, detail):
      summary - per indicator: number missing, total rows, % missing
      detail  - one row per missing cell: country, year, indicator
    """
    value_cols = [c for c in df.columns if c not in id_cols]

    n_missing = df[value_cols].isna().sum()
    summary = pd.DataFrame({
        "missing": n_missing,
        "total": len(df),
        "pct_missing": (n_missing / len(df) * 100).round(1),
    }).sort_values("missing", ascending=False)

    detail = (
        df.melt(id_vars=id_cols, value_vars=value_cols, var_name="indicator")
        .loc[lambda d: d["value"].isna(), [*id_cols, "indicator"]]
        .sort_values(["indicator", *id_cols])
        .reset_index(drop=True)
    )

    if verbose:
        print("Missing values by indicator:")
        print(summary.to_string())
        if detail.empty:
            print("\nNo missing values.")
        else:
            print("\nMissing years by indicator and country:")
            all_years = sorted(df["year"].unique())
            grouped = detail.groupby(["indicator", "country"])["year"].apply(
                lambda y: _year_ranges(y, all_years))
            with pd.option_context("display.max_colwidth", None):
                print(grouped.to_string())

    return summary, detail


def _year_ranges(years, all_years):
    """Collapse years into runs, e.g. '2000/01 to 2012/13, 2023/24'."""
    pos = sorted(all_years.index(y) for y in years)
    runs, start = [], pos[0]
    for prev, cur in zip(pos, pos[1:] + [None]):
        if cur != prev + 1:
            a, b = all_years[start], all_years[prev]
            runs.append(a if a == b else f"{a} to {b}")
            start = cur
    return ", ".join(runs)
