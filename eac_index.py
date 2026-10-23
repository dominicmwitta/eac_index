#%% import libraries
import pandas as pd
import re

from tools.data_loader import load_convergence_data

#%% Load data
FILENAME = "Macroeconomic Convergence Criteria_Submitted.xlsx"
SHEET_NAME = "Data_EAC_Submitted and online"
df_raw = pd.read_excel(FILENAME, sheet_name= SHEET_NAME,header=None)


# df = load_convergence_data("Macroeconomic Convergence Criteria_Submitted.xlsx",
#                            "Data_EAC_Submitted and online", long=False)

df_raw.head(10)

# %% identify the position of header row
hits = df_raw.isin(["Partner State"])
if not hits.any().any():
    raise ValueError(f"No 'Partner State' header found in sheet {SHEET_NAME!r}")

header_row = hits.any(axis=1).idxmax()
country_col = hits.loc[header_row].idxmax()
indicator_col = country_col - 1

header = df_raw.loc[header_row]
year_cols = {col: str(val).strip() for col, val in header.items() 
         if col > country_col and re.search(r"^\d{4}/\d{2}$", str(val).strip())}

body = df_raw.loc[header_row+1:, [indicator_col, country_col, *year_cols]].copy()
body.columns = ["indicator","country",*year_cols.values()]
body.dropna(axis=0,how='all',inplace=True)
body.dropna(subset='country', inplace=True)
body['indicator'] = body["indicator"].ffill()

#%% Reshape to long
long = body.melt(id_vars=["indicator", "country"],value_vars=[*year_cols.values()], 
                 var_name='year', value_name='value')
long.reset_index(drop=True, inplace=True)

long.tail()
# print(*year_cols)

# %%
header

# %%
{c:v for c, v in header.items()}
# %%
