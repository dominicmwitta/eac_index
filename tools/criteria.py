"""EAC Monetary Union (EAMU) primary macroeconomic convergence criteria.

Source for every threshold below:
  Protocol on the Establishment of the EAC Monetary Union (signed Nov 2013),
  as summarised by the IMF: Clara Mira, "New Pacts Ease Path Toward East
  African Single Currency", IMF Survey, 30 Dec 2013.
  https://www.imf.org/en/News/Articles/2015/09/28/04/53/socar123013a

  - Headline inflation: ceiling of 8 percent
  - Fiscal deficit including grants: ceiling of 3 percent of GDP
  - Gross public debt: ceiling of 50 percent of GDP in NPV terms
  - Reserve coverage: floor of 4.5 months of imports
  - Qualification: meet the criteria and comply for at least three years

The indicative (non-binding) criteria are core inflation 5%, fiscal deficit
excluding grants 6% of GDP, and tax/GDP 25%. They are not in the dataset, so
they are not used here.
"""

# column -> (threshold, "ceiling" | "floor", label)
PRIMARY_CRITERIA = {
    "inflation":      (8.0,  "ceiling", "Headline inflation (%)"),
    "fiscal_deficit": (3.0,  "ceiling", "Fiscal deficit incl. grants (% of GDP)"),
    "public_debt":    (50.0, "ceiling", "Gross public debt, NPV (% of GDP)"),
    "reserves":       (4.5,  "floor",   "FX reserves (months of imports)"),
}

# Years a country must keep meeting all criteria before qualifying.
SUSTAIN_YEARS = 3

SOURCES = [
    ("EAMU primary criteria and 3-year rule",
     "IMF Survey (C. Mira, 30 Dec 2013), 'New Pacts Ease Path Toward East African Single Currency'",
     "https://www.imf.org/en/News/Articles/2015/09/28/04/53/socar123013a"),
    ("Criteria and the 2021 deadline being missed",
     "Institute of Public Finance Kenya, Policy Brief 2: EAC Convergence (2023)",
     "https://ipfglobal.or.ke/wp-content/uploads/2023/10/Policy-Brief-2-EAC-Convergence.pdf"),
    ("Monetary union timeline moved from 2024 to 2031 (press report)",
     "The Citizen, 'East African Community postpones single currency to 2031'",
     "https://thecitizen.co.tz/tanzania/news/east-africa-news/-east-african-community-postpones-single-currency-to-2031-4733704"),
    ("Monetary union timeline moved to 2031 (press report)",
     "Daily Monitor, 'EAC pushes single currency deadline to 2031'",
     "https://www.monitor.co.ug/uganda/news/national/eac-pushes-single-currency-deadline-to-2031-4735370"),
    ("Sigma/beta convergence concepts",
     "Barro, R. & Sala-i-Martin, X. (1992), 'Convergence', Journal of Political Economy 100(2): 223-251, doi:10.1086/261816",
     "https://doi.org/10.1086/261816"),
    ("Comparable index: ARII macroeconomic dimension uses each country's inflation gap to the regional target",
     "AUC / AfDB / UNECA, Africa Regional Integration Index (2016 report; 2019 ARIIP User Guide, section 4.1.1.3)",
     "https://arii.uneca.org/Reports/en_ARII_UserGuide_2019.pdf"),
    ("General guidance on normalisation, weighting and missing data in composite indices",
     "OECD/JRC (2008), Handbook on Constructing Composite Indicators: Methodology and User Guide",
     "https://www.oecd.org/en/publications/handbook-on-constructing-composite-indicators-methodology-and-user-guide_9789264043466-en.html"),
]
