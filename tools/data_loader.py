"""Load EAC macroeconomic convergence data from the submitted Excel workbook."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

DEFAULT_FILE = Path(__file__).resolve().parent.parent / "Macroeconomic Convergence Criteria_Submitted.xlsx"
DEFAULT_SHEET = "Data_EAC_Submitted and online"

COUNTRY_ALIASES = {"DRC": "DR Congo"}
YEAR_PATTERN = re.compile(r"^\d{4}/\d{2}$")


def _clean_country(name) -> str | None:
    """Strip footnote markers (e.g. '1Kenya') and non-breaking spaces."""
    if not isinstance(name, str):
        return None
    name = re.sub(r"^\d+", "", name.replace("\xa0", " ")).strip()
    return COUNTRY_ALIASES.get(name, name) or None


def _to_number(value):
    """Convert cells such as '\xa04.5' or '-' to floats (NaN when not numeric)."""
    if isinstance(value, str):
        value = value.replace("\xa0", "").strip()
    return pd.to_numeric(value, errors="coerce")


def load_convergence_data(
    file_path: str | Path = DEFAULT_FILE,
    sheet_name: str = DEFAULT_SHEET,
    long: bool = True,
    include_eac_average: bool = False,
) -> pd.DataFrame:
    """Load an indicator-by-country block sheet from the convergence workbook.

    The sheets are laid out with the indicator name in one column (only on the
    first row of each block), the partner state in the next column and one
    column per fiscal year (e.g. '2018/19') starting on the 'Partner State'
    header row.

    Parameters
    ----------
    file_path : path to the Excel workbook.
    sheet_name : sheet to read, e.g. 'Data_EAC_Submitted',
        'Data_EAC_Submitted and online' or 'Sheet1'.
    long : if True return tidy columns [indicator, country, year, value];
        otherwise a wide frame indexed by (indicator, country) with years as columns.
    include_eac_average : keep the 'EAC average' rows when present.
    """
    raw = pd.read_excel(file_path, sheet_name=sheet_name, header=None, dtype=object)

    # Locate the header row and the 'Partner State' column.
    hits = raw.isin(["Partner State"])
    if not hits.any().any():
        raise ValueError(f"No 'Partner State' header found in sheet {sheet_name!r}")
    header_row = hits.any(axis=1).idxmax()
    country_col = hits.loc[header_row].idxmax()
    indicator_col = country_col - 1

    header = raw.loc[header_row]
    year_cols = {
        col: str(val).strip()
        for col, val in header.items()
        if col > country_col and YEAR_PATTERN.match(str(val).strip())
    }

    body = raw.loc[header_row + 1 :, [indicator_col, country_col, *year_cols]].copy()
    body.columns = ["indicator", "country", *year_cols.values()]
    body["indicator"] = body["indicator"].ffill().astype("string").str.strip()
    body["country"] = body["country"].map(_clean_country)

    # Footnote rows have text in the indicator column but no country.
    body = body.dropna(subset=["country"])
    if not include_eac_average:
        body = body[body["country"] != "EAC average"]

    years = list(year_cols.values())
    body[years] = body[years].apply(lambda col: col.map(_to_number)).astype(float)

    wide = body.set_index(["indicator", "country"])[years]
    wide.columns.name = "year"
    if not long:
        return wide

    return wide.reset_index().melt(id_vars=["indicator", "country"], var_name="year", value_name="value")


def load_all_sheets(file_path: str | Path = DEFAULT_FILE, **kwargs) -> dict[str, pd.DataFrame]:
    """Load every data sheet in the workbook that has a 'Partner State' header."""
    data = {}
    for sheet in pd.ExcelFile(file_path).sheet_names:
        try:
            data[sheet] = load_convergence_data(file_path, sheet, **kwargs)
        except ValueError:
            continue  # non-data sheets such as 'Data Sources'
    return data
