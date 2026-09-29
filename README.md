# Care Compare processing pipeline

Data Source

[CMS Provider Data Catalog](https://data.cms.gov/provider-data/topics/hospitals/)


## Repository environment
`% python3 -m venv .venv`
`% source .venv/bin/activate`
`% pip install -r requirements.txt`


## Raw data issues
In the Archives, the Snapshot Dates across years aren't always on the same day of year.

'Complications and Deaths - National' filename changes throughout the years, 
and the 2020 filenames are unrecognizable.

Hospital Wide Mortality (HWM) only reported for 2025 and 2026.

The following Measure IDs are only used in 2019 and 2020:

PSI_10_POST_KIDNEY
PSI_11_POST_RESP
PSI_12_POSTOP_PULMEMB_DVT
PSI_13_POST_SEPSIS
PSI_14_POSTOP_DEHIS
PSI_15_ACC_LAC
PSI_3_ULCER
PSI_4_SURG_COMP
PSI_6_IAT_PTX
PSI_8_POST_HIP
PSI_90_SAFETY
PSI_9_POST_HEM

The PSI_# is used for the rest of the years, so the Measure IDs above are mapped to those.

Besides NaN, "Not Available" is also used to represent missing data in a column,
even for columns with numerical values.

Start Date and End Date vary within a datafile.

Start Date and End Date are Month/Day/Year.

Most rates are % (inclucing HWB), except PSI_4, which is deaths per 1,000 eligible
surgical cases.  PSI_4 is "Death rate among surgical inpatients wih serious treatable 
complications."

