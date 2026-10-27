#%%
import pandas as pd
import numpy as np
import re
import os

#%%
from load_data import read_data
from sadc import winsorize, minmax, DIRECTION

df = read_data(filename='../Macroeconomic Convergence Criteria_Submitted.xlsx')
df.head()

# %% Winsorize (per country; see sadc.winsorize)
from missing import ID_COLS
INDICATOR_COLS = [c for c in df.columns if c not in ID_COLS]

for col in INDICATOR_COLS:
    df = winsorize(df, col)

# %% Min-max normalise (pooled; 1 = best; see sadc.minmax / sadc.DIRECTION)
df_wins = df.copy()
for col in INDICATOR_COLS:
    df = minmax(df, col, DIRECTION[col])

#%%
df

# %%
