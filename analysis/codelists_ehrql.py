from databuilder.ehrql import codelist_from_csv


ethnicity_codes = codelist_from_csv(
    "codelists/opensafely-ethnicity-snomed-0removed.csv",
    column="snomedcode",
    category_column="Grouping_6",
)

high_risk_codes = ["1300561000000107"]

not_high_risk_codes = ["1300591000000101", "1300571000000100"]

clear_smoking_codes = codelist_from_csv(
    "codelists/opensafely-smoking-clear.csv",
    column="CTV3Code",
    category_column="Category",
)

systolic_blood_pressure_codes = ["2469."]

diastolic_blood_pressure_codes = ["246A."]

hba1c_new_codes = ["XaPbt", "Xaeze", "Xaezd"]

hba1c_old_codes = ["X772q", "XaERo", "XaERp"]

diabetes_codes = codelist_from_csv(
    "codelists/opensafely-diabetes.csv",
    column="CTV3ID",
)

hypertension_codes = codelist_from_csv(
    "codelists/opensafely-hypertension.csv",
    column="CTV3ID",
)

copd_codes = codelist_from_csv(
    "codelists/opensafely-current-copd.csv",
    column="CTV3ID",
)

other_respiratory_codes = codelist_from_csv(
    "codelists/opensafely-other-respiratory-conditions.csv",
    column="CTV3ID",
)

asthma_codes = codelist_from_csv(
    "codelists/opensafely-asthma-diagnosis.csv",
    column="CTV3ID",
)

chronic_respiratory_disease_codes = codelist_from_csv(
    "codelists/opensafely-chronic-respiratory-disease.csv",
    column="CTV3ID",
)

pred_codes = codelist_from_csv(
    "codelists/opensafely-asthma-oral-prednisolone-medication.csv",
    column="snomed_id",
)

lung_cancer_codes = codelist_from_csv(
    "codelists/opensafely-lung-cancer.csv",
    column="CTV3ID",
)

haem_cancer_codes = codelist_from_csv(
    "codelists/opensafely-haematological-cancer.csv",
    column="CTV3ID",
)

other_cancer_codes = codelist_from_csv(
    "codelists/opensafely-cancer-excluding-lung-and-haematological.csv",
    column="CTV3ID",
)

hiv_codes = codelist_from_csv(
    "codelists/opensafely-hiv.csv",
    column="CTV3ID",
)

permanent_immune_codes = codelist_from_csv(
    "codelists/opensafely-permanent-immunosuppression.csv",
    column="CTV3ID",
)

sickle_cell_codes = codelist_from_csv(
    "codelists/opensafely-sickle-cell-disease.csv",
    column="CTV3ID",
)

spleen_codes = codelist_from_csv(
    "codelists/opensafely-asplenia.csv",
    column="CTV3ID",
)

temp_immune_codes = codelist_from_csv(
    "codelists/opensafely-temporary-immunosuppression.csv",
    column="CTV3ID",
)

organ_transplant_codes = codelist_from_csv(
    "codelists/opensafely-solid-organ-transplantation.csv",
    column="CTV3ID",
)

aplastic_codes = codelist_from_csv(
    "codelists/opensafely-aplastic-anaemia.csv",
    column="CTV3ID",
)

af_codes = codelist_from_csv(
    "codelists/opensafely-atrial-fibrillation-clinical-finding.csv",
    column="CTV3Code",
)

pad_codes = codelist_from_csv(
    "codelists/opensafely-peripheral-arterial-disease.csv",
    column="code",
)

heart_failure_codes = codelist_from_csv(
    "codelists/opensafely-heart-failure.csv",
    column="CTV3ID",
)

mi_codes = codelist_from_csv(
    "codelists/opensafely-myocardial-infarction.csv",
    column="CTV3ID",
)

vte_codes = codelist_from_csv(
    "codelists/opensafely-venous-thromboembolic-disease.csv",
    column="CTV3Code",
)

chd_codes = codelist_from_csv(
    "codelists/opensafely-chronic-cardiac-disease.csv",
    column="CTV3ID",
)

stroke_codes = codelist_from_csv(
    "codelists/opensafely-stroke-updated.csv",
    column="CTV3ID",
)

tia_codes = codelist_from_csv(
    "codelists/opensafely-transient-ischaemic-attack.csv",
    column="code",
)

dementia_codes = codelist_from_csv(
    "codelists/opensafely-dementia-complete.csv",
    column="code",
)

liver_codes = codelist_from_csv(
    "codelists/opensafely-chronic-liver-disease.csv",
    column="CTV3ID",
)

other_neuro_codes = codelist_from_csv(
    "codelists/opensafely-other-neurological-conditions.csv",
    column="CTV3ID",
)

rheumatoid_arthritis_codes = codelist_from_csv(
    "codelists/opensafely-rheumatoid-arthritis.csv",
    column="CTV3ID",
)

sle_codes = codelist_from_csv(
    "codelists/opensafely-systemic-lupus-erythematosus-sle.csv",
    column="CTV3ID",
)

psoriasis_codes = codelist_from_csv(
    "codelists/opensafely-psoriasis.csv",
    column="code",
)

dialysis_codes = codelist_from_csv(
    "codelists/opensafely-dialysis.csv",
    column="CTV3ID",
)

creatinine_codes = codelist_from_csv(
    "codelists/user-bangzheng-creatinine-value.csv",
    column="code",
)
