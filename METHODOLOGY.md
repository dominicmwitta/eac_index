# EAC Macroeconomic Convergence Indicator: Methodology

Run `python run_index.py`. Output: `outputs/eac_convergence_index.xlsx`.

## 1. Criteria (official)

These are the primary criteria of the Protocol on the Establishment of the EAC
Monetary Union (2013), as summarised by the IMF [1]:

| Criterion | Threshold | Type |
|---|---|---|
| Headline inflation | 8% | ceiling |
| Fiscal deficit incl. grants | 3% of GDP | ceiling |
| Gross public debt (NPV) | 50% of GDP | ceiling |
| Reserve cover | 4.5 months of imports | floor |

To qualify, a country must meet the criteria and comply for at least three years [1].
The original 2021 convergence deadline was missed [2]. Press reports say the
monetary-union date moved from 2024 to 2031 [3][4]. I did not find the Council
decision document itself.

The indicative criteria (core inflation 5%, deficit excluding grants 6% of
GDP, tax/GDP 25%) [1] are not in the dataset, so they are not used.

## 2. What is computed

| Output | Definition | Basis |
|---|---|---|
| `*_met`, `n_met`, `all_met` | Criterion met (yes/no), count of criteria met | Official thresholds [1] |
| `sustained_all_met` | All 4 met for 3 consecutive years | Protocol qualification rule [1] |
| `*_score` | 1 if met, else `max(0, 1 − gap/threshold)` | **Project design choice** (see below) |
| `composite_score` | Equal-weighted mean of available scores, only if ≥3 of 4 observed | **Project design choice** |
| Regional mean | Mean of country composites, only if ≥4 countries | **Project design choice** |
| Sigma convergence | Cross-country standard deviation per indicator per year; a falling trend means the countries are becoming more alike | Barro & Sala-i-Martin (1992) [5] |

**Scoring by distance to threshold.** The ARII, built by the AUC, AfDB and
UNECA, also measures macroeconomic integration as each country's inflation gap
to the regional target [6]. This project's 0–1 scaling, its equal weights and
its coverage thresholds were chosen here for transparency. **They are not an
EAC, AfDB or IMF formula.** The OECD/JRC handbook [7] is the standard general
reference for these choices (normalisation, weighting, missing data). I could
not open its full text in this session, so no page or section is cited.

## 2a. SADC-method index (`tools/sadc.py`)

A second index follows the SADC Macroeconomic Convergence Index [8]
(sheets `SADC_Country_Index`, `SADC_Regional_Index`, `SADC_Weights`):

1. Winsorize each indicator per country: values beyond 3×IQR from the
   quartiles are replaced by that country's 5th/95th percentile.
2. Min-max rescale over all countries and years, 1 = best (SADC eq. 1–2).
   Inflation and debt are flipped (lower is better).
3. Primary sub-index (inflation, fiscal balance, debt) weighted by the
   first principal component of the correlation matrix (SADC eq. 3).
4. Country index = 0.7 × primary + 0.3 × secondary (SADC eq. 5).
5. Regional index = mean of country indices, if ≥4 countries.

Departures from the SADC paper, forced by the data:

- **Secondary sub-index is reserves only.** The current account, GDP growth
  and central bank credit series are not in the workbook.
- **Equal country weights**, not GDP shares, because there are no GDP data.
  The SADC paper uses equal weights as a robustness variant.
- **PCA weights** are the absolute PC1 loadings rescaled to sum to 1, so
  sub-indices stay on 0–1. Fiscal balance loads negatively on PC1 and gets a
  small weight (about 9%).
- **No imputation:** a sub-index needs all its indicators, so DR Congo (no
  debt data) and Somalia have no country index.

## 3. Data gaps: how they are handled

- **No imputation.** Missing cells stay blank, and nothing is estimated.
- `n_observed` (per country-year) and `n_countries` / `n_<indicator>`
  (per year) show how much data stands behind each number.
- `Missing_Summary` and `Missing_Detail` list every gap.
- Somalia has no fiscal, debt or reserve data, so it has no composite score.
- DR Congo has no debt data.
- Debt is the sparsest series (60% missing). Kenya has the full series,
  Rwanda starts in 2014/15, and Tanzania and Uganda start in 2018/19.
- **The countries covered change from year to year.** Regional means and
  sigma dispersion are not like-for-like across years. Before about 2010/11
  they are suppressed for most years.

## 4. Data notes

- The workbook stores the fiscal **balance** (negative = deficit). The code
  converts it to deficit = −balance before comparing with the 3% ceiling.
- The workbook notes that some values are calendar-year data placed in the
  fiscal-year column.
- The workbook's "Data Sources" sheet lists World Bank WDI and IMF WEO
  series for filling gaps. They are not merged here. WDI central-government
  debt is nominal rather than NPV, and WEO uses general government, so neither
  matches the EAC definitions exactly.

## References

1. IMF Survey (C. Mira, 30 Dec 2013), "New Pacts Ease Path Toward East African Single Currency". https://www.imf.org/en/News/Articles/2015/09/28/04/53/socar123013a
2. Institute of Public Finance Kenya (2023), Policy Brief 2: EAC Convergence. https://ipfglobal.or.ke/wp-content/uploads/2023/10/Policy-Brief-2-EAC-Convergence.pdf
3. The Citizen, "East African Community postpones single currency to 2031". https://thecitizen.co.tz/tanzania/news/east-africa-news/-east-african-community-postpones-single-currency-to-2031-4733704
4. Daily Monitor, "EAC pushes single currency deadline to 2031". https://www.monitor.co.ug/uganda/news/national/eac-pushes-single-currency-deadline-to-2031-4735370
5. Barro, R. & Sala-i-Martin, X. (1992), "Convergence", *Journal of Political Economy* 100(2): 223–251. https://doi.org/10.1086/261816
6. UNECA (2019), Africa Regional Integration Index Platform User Guide, §4.1.1.3 (index by AUC, AfDB, UNECA). https://arii.uneca.org/Reports/en_ARII_UserGuide_2019.pdf
7. OECD/JRC (2008), *Handbook on Constructing Composite Indicators: Methodology and User Guide*. https://www.oecd.org/en/publications/handbook-on-constructing-composite-indicators-methodology-and-user-guide_9789264043466-en.html
8. Bank of Tanzania (Aug 2024), *Assessing the Macroeconomic Convergence in the Southern African Development Community: A Composite Index Approach*, SADC/PRP/1/2025/4A, §3.4–3.5 and Annex 2 (`SADC_MEC_Index.pdf`).
