"""Build the EAC macroeconomic convergence indicators.

Missing data are never filled in. Every output carries a count of the
criteria it is based on, so readers can see how much data stands behind it.
"""
import numpy as np
import pandas as pd

from tools.criteria import PRIMARY_CRITERIA, SUSTAIN_YEARS

ID_COLS = ["country", "year"]
CRITERIA = list(PRIMARY_CRITERIA)


def prepare(df):
    """Put each indicator in the units the threshold uses.

    The workbook records the fiscal position as a balance (negative = deficit),
    so the deficit is its negative: a balance of -4.5 is a deficit of 4.5.
    """
    out = df[ID_COLS + CRITERIA].copy()
    out["fiscal_deficit"] = -out["fiscal_deficit"]
    return out


def compliance(df):
    """True/False for each criterion met; missing where the data are missing."""
    met = df[ID_COLS].copy()
    for col, (limit, kind, _) in PRIMARY_CRITERIA.items():
        ok = df[col] <= limit if kind == "ceiling" else df[col] >= limit
        met[col] = ok.astype("boolean").mask(df[col].isna())
    return met


def scores(df):
    """Distance-to-threshold score from 0 to 1 for each criterion.

    1 = criterion met. Otherwise 1 - (gap / threshold), floored at 0, where
    gap is how far the value is on the wrong side of the threshold. So
    inflation of 12% (gap 4 on an 8% ceiling) scores 0.5, and reserves of
    2.25 months (gap 2.25 on a 4.5 floor) scores 0.5.

    This scaling is a design choice of this project, not an EAC formula.
    """
    s = df[ID_COLS].copy()
    for col, (limit, kind, _) in PRIMARY_CRITERIA.items():
        gap = df[col] - limit if kind == "ceiling" else limit - df[col]
        s[col] = (1 - gap.clip(lower=0) / limit).clip(lower=0)
    return s


def country_index(df, min_criteria=3):
    """Per country-year: criteria met, criteria observed, composite score.

    The composite is the equal-weighted mean of the available criterion
    scores. It is only reported when at least `min_criteria` of the 4 are
    observed, since an average of one or two criteria is not comparable.
    """
    d = prepare(df)
    met = compliance(d)
    sc = scores(d)

    out = d[ID_COLS].copy()
    out["n_observed"] = d[CRITERIA].notna().sum(axis=1)
    out["n_met"] = met[CRITERIA].sum(axis=1).astype(int)
    out["all_met"] = (out["n_met"] == 4)
    composite = sc[CRITERIA].mean(axis=1, skipna=True)
    out["composite_score"] = composite.where(out["n_observed"] >= min_criteria)
    out["complete_data"] = out["n_observed"] == 4

    # Qualification: all 4 criteria met for SUSTAIN_YEARS consecutive years.
    out = out.sort_values(ID_COLS)
    out["sustained_all_met"] = (
        out.groupby("country")["all_met"]
        .transform(lambda x: x.astype(int).rolling(SUSTAIN_YEARS).sum() == SUSTAIN_YEARS)
    )

    met = met.add_suffix("_met").rename(columns={"country_met": "country", "year_met": "year"})
    sc = sc.add_suffix("_score").rename(columns={"country_score": "country", "year_score": "year"})
    return (d.merge(met, on=ID_COLS).merge(sc, on=ID_COLS).merge(out, on=ID_COLS)
            .sort_values(ID_COLS).reset_index(drop=True))


def regional_index(ci, min_countries=4):
    """EAC-wide summary per year from the country table.

    Averages are only reported when at least `min_countries` countries have
    a composite score. The set of countries changes from year to year as
    data become available, so read the n_countries column with the mean.
    """
    g = ci.groupby("year")
    reg = pd.DataFrame({
        "n_countries": g["composite_score"].count(),
        "mean_composite": g["composite_score"].mean(),
        "countries_all_met": g["all_met"].sum(),
    })
    for col in CRITERIA:
        reg[f"share_meeting_{col}"] = g[f"{col}_met"].mean()
        reg[f"n_{col}"] = g[col].count()
    reg.loc[reg["n_countries"] < min_countries, "mean_composite"] = np.nan
    return reg.reset_index()


def sigma_convergence(df, min_countries=4):
    """Cross-country dispersion of each indicator by year (sigma convergence).

    Falling dispersion over time means the economies are becoming more alike
    (Barro & Sala-i-Martin, 1992). Standard deviation is used rather than the
    coefficient of variation because fiscal balances change sign. Dispersion
    is set to missing in years with fewer than `min_countries` observations.
    """
    d = prepare(df)
    rows = []
    for col in CRITERIA:
        g = d.groupby("year")[col]
        t = pd.DataFrame({"indicator": col, "n": g.count(), "mean": g.mean(),
                          "median": g.median(), "std": g.std()})
        t.loc[t["n"] < min_countries, ["std"]] = np.nan
        rows.append(t.reset_index())
    return pd.concat(rows, ignore_index=True)[["indicator", "year", "n", "mean", "median", "std"]]


def sigma_trend(sigma):
    """Linear slope of the dispersion series per indicator (per year).

    A negative slope is evidence of sigma convergence over the period
    covered. Only years with a dispersion value are used.
    """
    out = []
    for ind, t in sigma.dropna(subset=["std"]).groupby("indicator"):
        x = t["year"].str[:4].astype(int).to_numpy()
        slope = np.polyfit(x, t["std"].to_numpy(), 1)[0] if len(t) >= 5 else np.nan
        out.append({"indicator": ind, "first_year": t["year"].min(),
                    "last_year": t["year"].max(), "n_years": len(t),
                    "std_slope_per_year": slope,
                    "sigma_converging": bool(slope < 0) if pd.notna(slope) else None})
    return pd.DataFrame(out)
