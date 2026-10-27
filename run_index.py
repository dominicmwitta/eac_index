#%% Build the EAC convergence indicators and write them to Excel
from pathlib import Path

import pandas as pd

from tools.load_data import read_data
from tools.missing import missing_report
from tools.criteria import PRIMARY_CRITERIA, SUSTAIN_YEARS, SOURCES
from tools.index import country_index, regional_index, sigma_convergence, sigma_trend
from tools import sadc

OUTPUT = Path("outputs/eac_convergence_index.xlsx")

#%%
df = read_data()
summary, missing = missing_report(df, verbose=False)
ci = country_index(df)
reg = regional_index(ci)
sigma = sigma_convergence(df)
trend = sigma_trend(sigma)
sadc_ci, sadc_w = sadc.country_index(df)
sadc_reg = sadc.regional_index(sadc_ci)

#%% Methodology sheet
method = pd.DataFrame(
    [("Criterion", "Threshold", "Type", "")] +
    [(lab, lim, kind, col) for col, (lim, kind, lab) in PRIMARY_CRITERIA.items()] +
    [("", "", "", ""),
     ("Qualification", f"All 4 met for {SUSTAIN_YEARS} consecutive years", "", ""),
     ("", "", "", ""),
     ("Score (0-1)", "1 if met; else max(0, 1 - gap/threshold). Project design choice, not an EAC formula.", "", ""),
     ("Composite", "Equal-weighted mean of available scores; reported only if >= 3 of 4 criteria observed.", "", ""),
     ("Regional mean", "Mean of country composites; reported only if >= 4 countries have a score.", "", ""),
     ("Sigma convergence", "Cross-country std dev by year; reported only if >= 4 countries observed. Negative slope = converging.", "", ""),
     ("Missing data", "Not imputed. Gaps stay blank; n_observed / n columns show coverage.", "", ""),
     ("Fiscal sign", "Workbook stores the balance (negative = deficit); converted to deficit = -balance.", "", ""),
     ("Fiscal year", "Workbook note: some values are calendar-year data placed in the FY column.", "", ""),
     ("", "", "", ""),
     ("Source topic", "Reference", "Link", "")] +
    [(a, b, c, "") for a, b, c in SOURCES]
)

#%% Write
OUTPUT.parent.mkdir(exist_ok=True)
with pd.ExcelWriter(OUTPUT) as xw:
    method.to_excel(xw, sheet_name="Methodology", index=False, header=False)
    ci.to_excel(xw, sheet_name="Country_Index", index=False)
    reg.to_excel(xw, sheet_name="Regional_Index", index=False)
    sigma.to_excel(xw, sheet_name="Sigma_Dispersion", index=False)
    trend.to_excel(xw, sheet_name="Sigma_Trend", index=False)
    sadc_ci.to_excel(xw, sheet_name="SADC_Country_Index", index=False)
    sadc_reg.to_excel(xw, sheet_name="SADC_Regional_Index", index=False)
    sadc_w.to_excel(xw, sheet_name="SADC_Weights", index=False)
    summary.to_excel(xw, sheet_name="Missing_Summary")
    missing.to_excel(xw, sheet_name="Missing_Detail", index=False)
print(f"Wrote {OUTPUT}")

# %%
