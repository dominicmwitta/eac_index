"""EAC convergence index built with the SADC MCI method.

Source: Bank of Tanzania (Aug 2024), "Assessing the Macroeconomic Convergence
in the Southern African Development Community: A Composite Index Approach",
SADC/PRP/1/2025/4A (SADC_MEC_Index.pdf), sections 3.4-3.5 and Annex 2.

Steps, as in the SADC paper:
  1. Winsorize outliers.
  2. Min-max rescale each indicator over the whole panel (eq. 1-2), flipping
     indicators where lower is better, so 1 = best.
  3. Primary and secondary sub-indices, weighted by first-principal-component
     loadings (eq. 3-4).
  4. Country index = 0.7 * primary + 0.3 * secondary (eq. 5).
  5. Regional index across countries (eq. 6).

Differences from the SADC paper, forced by the EAC data:
  - Only reserves is available among the secondary indicators (no current
    account, GDP growth or central bank credit), so the secondary
    sub-index is reserves alone.
  - No GDP data, so the regional index is an equal-weighted mean (the
    paper's own equal-weight robustness variant) instead of GDP shares.
  - PCA weights are the absolute PC1 loadings rescaled to sum to 1, so each
    sub-index stays on a 0-1 scale.
  - Missing data are not imputed: a sub-index needs all its indicators.
"""
import numpy as np
import pandas as pd

ID_COLS = ["country", "year"]

# SADC Table 6. +1: higher is better; -1: lower is better.
# fiscal_deficit is stored as a balance (negative = deficit), so higher is better.
DIRECTION = {"inflation": -1, "fiscal_deficit": 1, "public_debt": -1, "reserves": 1}
PRIMARY = ["inflation", "fiscal_deficit", "public_debt"]
SECONDARY = ["reserves"]
PRIMARY_WEIGHT = 0.7  # SADC eq. 5; secondary gets 1 - this


def winsorize(df, colname, k=3, group_col="country"):
    """Within each country, replace values beyond k*IQR from the quartiles
    with that country's 5th/95th percentile."""
    df = df.copy()
    s = df[colname]
    g = s.groupby(df[group_col])
    # quantile() uses a 0-1 scale and skips NaNs
    p5, p25, p75, p95 = (g.transform("quantile", q) for q in (0.05, 0.25, 0.75, 0.95))

    iqr = p75 - p25
    lower_bound = p25 - k * iqr
    upper_bound = p75 + k * iqr

    df[colname] = s.mask(s > upper_bound, p95).mask(s < lower_bound, p5)
    return df


def minmax(df, colname, direction=1):
    """Rescale to 0-1 using the min and max over all countries and years.
    1 = best observed value, 0 = worst. NaNs stay NaN. (SADC eq. 1-2)"""
    df = df.copy()
    s = df[colname]
    lo, hi = s.min(), s.max()
    scaled = (s - lo) / (hi - lo) if hi > lo else s * 0.0
    df[colname] = scaled if direction == 1 else 1 - scaled
    return df


def pca_weights(norm, cols):
    """Weights from the first principal component of the correlation matrix,
    using rows where all `cols` are observed. Returns (weights, table)."""
    if len(cols) == 1:
        w = pd.Series(1.0, index=cols)
        return w, pd.DataFrame({"indicator": cols, "weight": w.to_numpy()})
    x = norm[cols].dropna()
    eigval, eigvec = np.linalg.eigh(np.corrcoef(x.to_numpy(), rowvar=False))
    order = np.argsort(eigval)[::-1]
    eigval, eigvec = eigval[order], eigvec[:, order]
    pc1 = eigvec[:, 0] * np.sign(eigvec[:, 0].sum())  # sign is arbitrary
    w = pd.Series(np.abs(pc1) / np.abs(pc1).sum(), index=cols)
    table = pd.DataFrame({"indicator": cols, "pc1_loading": pc1, "weight": w.to_numpy()})
    table["pc1_variance_share"] = eigval[0] / eigval.sum()
    table["n_obs"] = len(x)
    return w, table


def normalise(df):
    """Winsorize per country, then min-max over the pooled panel."""
    out = df[ID_COLS + PRIMARY + SECONDARY].copy()
    for col in DIRECTION:
        out = winsorize(out, col)
    for col, d in DIRECTION.items():
        out = minmax(out, col, d)
    return out


def country_index(df):
    """Per country-year: normalised indicators, sub-indices and country index."""
    norm = normalise(df)
    wp, tp = pca_weights(norm, PRIMARY)
    ws, ts = pca_weights(norm, SECONDARY)

    out = norm.copy()
    # weighted sum; NaN if any indicator in the group is missing
    out["primary_index"] = norm[PRIMARY].mul(wp).sum(axis=1, min_count=len(PRIMARY))
    out["secondary_index"] = norm[SECONDARY].mul(ws).sum(axis=1, min_count=len(SECONDARY))
    out["country_index"] = (PRIMARY_WEIGHT * out["primary_index"]
                            + (1 - PRIMARY_WEIGHT) * out["secondary_index"])

    weights = pd.concat([tp.assign(group="primary"), ts.assign(group="secondary")],
                        ignore_index=True)
    return out.sort_values(ID_COLS).reset_index(drop=True), weights


def regional_index(ci, min_countries=4):
    """Equal-weighted mean of country indices per year. Set to missing when
    fewer than `min_countries` countries have a score."""
    g = ci.groupby("year")
    reg = pd.DataFrame({
        "n_countries": g["country_index"].count(),
        "regional_index": g["country_index"].mean(),
        "primary_index": g["primary_index"].mean(),
        "secondary_index": g["secondary_index"].mean(),
    })
    reg.loc[reg["n_countries"] < min_countries,
            ["regional_index", "primary_index", "secondary_index"]] = np.nan
    return reg.reset_index()
