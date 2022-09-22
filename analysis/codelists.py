from cohortextractor import (
    codelist_from_csv,
    combine_codelists,
    codelist,
)

# DEMOGRAPHIC CODELISTS
ethnicity_codes_6 = codelist_from_csv(
    "codelists/opensafely-ethnicity.csv",
    system="ctv3",
    column="Code",
    category_column="Grouping_6",
)
# SHIELDING CODELISTS
# High risk and not high risk codes, to define clinical vulnerability to complications from COVID-19 infection/shielding
high_risk_codes = codelist(
    ['1300561000000107'], 
    system="snomed",
    )

not_high_risk_codes = codelist(
    ['1300591000000101', '1300571000000100'], 
    system="snomed",
    )

# SMOKING

# BLOOD PRESSURE
systolic_blood_pressure_codes = codelist(
    ["2469."], 
    system="ctv3",
    )

diastolic_blood_pressure_codes = codelist(
    ["246A."], 
    system="ctv3",
    )


# COMORBIDITIES
# diabetes hba1c codes
hba1c_new_codes = codelist(
    ["XaPbt", "Xaeze", "Xaezd"], 
    system="ctv3",
    )

hba1c_old_codes = codelist(
    ["X772q", "XaERo", "XaERp"], 
    system="ctv3",
    )




