#%% import libraries
import pandas as pd
import re


#%% Load data
FILENAME = "Macroeconomic Convergence Criteria_Submitted.xlsx"
SHEET_NAME = "Data_EAC_Submitted and online"

def read_data(filename=FILENAME, sheet = SHEET_NAME):
    df_raw = pd.read_excel(filename, sheet_name=sheet, header=None)
    # %% identify the position of header row
    hits = df_raw.isin(["Partner State"])
    if not hits.any().any():
        raise ValueError(f"No 'Partner State' header found in sheet {sheet!r}")

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

    long['value'] = pd.to_numeric(long['value'])
    # long.dropna(subset=['value'], inplace=True)
    long.reset_index(drop=True, inplace=True)
    

    #%%
    # long['indicator'].unique()

    indicators = {'Headline inflation (annual avg, %)':'inflation',
    'Official FX reserves (months of import cover)':'reserves',
    'Overall fiscal deficit incl. grants (% of GDP)':'fiscal_deficit',
            'Gross public debt, NPV terms (% of GDP)':'public_debt'}

    long['indicator'] = long['indicator'].map(indicators)

    wide = long.pivot(columns='indicator', values='value',
                      index=['country', 'year']).reset_index().rename_axis(columns=None)
    return wide

# print(*year_cols)

# %%

