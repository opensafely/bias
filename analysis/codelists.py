from cohortextractor import (
    codelist_from_csv,
    combine_codelists,
    codelist,
)

# DEMOGRAPHIC CODELISTS
ethnicity_codes = codelist_from_csv(
"codelists/opensafely-ethnicity-snomed-0removed.csv",
    system="snomed",
    column="snomedcode",
    category_column="Grouping_6",)


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

    
# Smoking - primary care only
    opensafely/smoking-clear/2020-04-29

# Cardiovascular risk factors - since they are in QOF, it's ok to use primary care only
# blood pressure uses only one code for systolic and one for diastolic - see codelists.py
    opensafely/diabetes/2020-04-15
    opensafely/hypertension/2020-04-28

# Respiratory
    # chronic resp disease excluding asthma:
    opensafely/current-copd/2020-05-06
    opensafely/other-respiratory-conditions/2020-07-21
    # asthma
    opensafely/asthma-diagnosis/2020-04-15
    opensafely/asthma-oral-prednisolone-medication/2020-04-27

# Cancer
    opensafely/cancer-excluding-lung-and-haematological/2020-04-15
    opensafely/haematological-cancer/2020-04-15
    opensafely/lung-cancer/2020-04-15

# immunosuppression
    opensafely/asplenia/2020-06-02
    opensafely/temporary-immunosuppression/2020-04-24
    opensafely/permanent-immunosuppression/2020-06-02
    opensafely/hiv/2020-07-13

# cardiovascular disease - primary and secondary care
    opensafely/atrial-fibrillation-clinical-finding/2020-07-09
    opensafely/peripheral-arterial-disease/50e915d7
    opensafely/heart-failure/2020-05-05
    opensafely/myocardial-infarction/2020-06-25
    opensafely/venous-thromboembolic-disease/2020-09-14
    opensafely/chronic-cardiac-disease/2020-04-08

# cerebrovascular disease incl dementia
    opensafely/stroke-updated/2020-06-02
    opensafely/transient-ischaemic-attack/3526e2ac
    opensafely/dementia-complete/48c76cf8


# Other required
opensafely/chronic-liver-disease/2020-06-02
opensafely/solid-organ-transplantation/2020-04-10
opensafely/other-neurological-conditions/2020-06-02
opensafely/rheumatoid-arthritis/2020-05-12
opensafely/systemic-lupus-erythematosus-sle/2020-05-12
opensafely/psoriasis/01091de1

# KIDNEY DISEASE - FROM V
user/viyaasan/dialysis/4c8d3f33
# BASELINE EGFR - FROM BANG
user/bangzheng/creatinine-value/7d319079


