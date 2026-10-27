#%%
from tools.load_data import read_data
from tools.missing import missing_report
import re
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

#%%
df = read_data()
df



# # %%
# df[df['country'].str.contains('Tanzania|Kenya|Uganda',case=False)]


# %%
summary, missing = missing_report(df)

# %% Summary Statistics
df.describe()

# %%
df.groupby('country').describe()

# %%
fig, axs = plt.subplots(ncols=4, figsize = (8,3))

for ax, col in zip(axs, df.columns[2:]):
    ax.boxplot(df[col].dropna())
    ax.set_xticks([1], [col])
plt.tight_layout()
plt.show()


# %% Winsorize data
from tools.missing import ID_COLS
INDICATOR_COLS = [c for c in df.columns if c not in ID_COLS]



