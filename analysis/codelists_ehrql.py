from pathlib import Path

from databuilder.codes import REGISTRY, Codelist, codelist_from_csv

CODELIST_DIR = Path(__file__).parent.parent / "codelists"

# These functions will eventually be replaced by features built in to Data Builder's
# codelist library, but I don't want to commit to any particular approach yet so I'm
# defining them here.


def codelist(codes, system):
    code_class = REGISTRY[system]
    return Codelist(
        codes={code_class(code) for code in codes},
        category_maps={},
    )


def combine_codelists(*codelists):
    codes = set()
    for codelist in codelists:
        codes.update(codelist.codes)
    return Codelist(codes=codes, category_maps={})


ethnicity_codes = codelist_from_csv(
    CODELIST_DIR / "opensafely-ethnicity-snomed-0removed.csv",
    system="snomed",
    column="snomedcode",
    category_column="Grouping_6",
)

high_risk_codes = codelist(
    ["1300561000000107"],
    system="snomed",
)

not_high_risk_codes = codelist(
    ["1300591000000101", "1300571000000100"],
    system="snomed",
)

clear_smoking_codes = codelist_from_csv(
    CODELIST_DIR / "opensafely-smoking-clear.csv",
    system="ctv3",
    column="CTV3Code",
    category_column="Category",
)

systolic_blood_pressure_codes = codelist(
    ["2469."],
    system="ctv3",
)

diastolic_blood_pressure_codes = codelist(
    ["246A."],
    system="ctv3",
)

hba1c_new_codes = codelist(
    ["XaPbt", "Xaeze", "Xaezd"],
    system="ctv3",
)

hba1c_old_codes = codelist(
    ["X772q", "XaERo", "XaERp"],
    system="ctv3",
)

diabetes_codes = codelist_from_csv(
    CODELIST_DIR / "opensafely-diabetes.csv",
    system="ctv3",
    column="CTV3ID",
)

hypertension_codes = codelist_from_csv(
    CODELIST_DIR / "opensafely-hypertension.csv",
    system="ctv3",
    column="CTV3ID",
)

copd_codes = codelist_from_csv(
    CODELIST_DIR / "opensafely-current-copd.csv",
    system="ctv3",
    column="CTV3ID",
)

other_respiratory_codes = codelist_from_csv(
    CODELIST_DIR / "opensafely-other-respiratory-conditions.csv",
    system="ctv3",
    column="CTV3ID",
)

asthma_codes = codelist_from_csv(
    CODELIST_DIR / "opensafely-asthma-diagnosis.csv",
    system="ctv3",
    column="CTV3ID",
)

chronic_respiratory_disease_codes = codelist_from_csv(
    CODELIST_DIR / "opensafely-chronic-respiratory-disease.csv",
    system="ctv3",
    column="CTV3ID",
)

pred_codes = codelist_from_csv(
    CODELIST_DIR / "opensafely-asthma-oral-prednisolone-medication.csv",
    system="snomed",
    column="snomed_id",
)

lung_cancer_codes = codelist_from_csv(
    CODELIST_DIR / "opensafely-lung-cancer.csv",
    system="ctv3",
    column="CTV3ID",
)

haem_cancer_codes = codelist_from_csv(
    CODELIST_DIR / "opensafely-haematological-cancer.csv",
    system="ctv3",
    column="CTV3ID",
)

other_cancer_codes = codelist_from_csv(
    CODELIST_DIR / "opensafely-cancer-excluding-lung-and-haematological.csv",
    system="ctv3",
    column="CTV3ID",
)

hiv_codes = codelist_from_csv(
    CODELIST_DIR / "opensafely-hiv.csv",
    system="ctv3",
    column="CTV3ID",
)

permanent_immune_codes = codelist_from_csv(
    CODELIST_DIR / "opensafely-permanent-immunosuppression.csv",
    system="ctv3",
    column="CTV3ID",
)

sickle_cell_codes = codelist_from_csv(
    CODELIST_DIR / "opensafely-sickle-cell-disease.csv",
    system="ctv3",
    column="CTV3ID",
)

spleen_codes = codelist_from_csv(
    CODELIST_DIR / "opensafely-asplenia.csv",
    system="ctv3",
    column="CTV3ID",
)

temp_immune_codes = codelist_from_csv(
    CODELIST_DIR / "opensafely-temporary-immunosuppression.csv",
    system="ctv3",
    column="CTV3ID",
)

organ_transplant_codes = codelist_from_csv(
    CODELIST_DIR / "opensafely-solid-organ-transplantation.csv",
    system="ctv3",
    column="CTV3ID",
)

aplastic_codes = codelist_from_csv(
    CODELIST_DIR / "opensafely-aplastic-anaemia.csv",
    system="ctv3",
    column="CTV3ID",
)

af_codes = codelist_from_csv(
    CODELIST_DIR / "opensafely-atrial-fibrillation-clinical-finding.csv",
    system="ctv3",
    column="CTV3Code",
)

pad_codes = codelist_from_csv(
    CODELIST_DIR / "opensafely-peripheral-arterial-disease.csv",
    system="ctv3",
    column="code",
)

heart_failure_codes = codelist_from_csv(
    CODELIST_DIR / "opensafely-heart-failure.csv",
    system="ctv3",
    column="CTV3ID",
)

mi_codes = codelist_from_csv(
    CODELIST_DIR / "opensafely-myocardial-infarction.csv",
    system="ctv3",
    column="CTV3ID",
)

vte_codes = codelist_from_csv(
    CODELIST_DIR / "opensafely-venous-thromboembolic-disease.csv",
    system="ctv3",
    column="CTV3Code",
)

chd_codes = codelist_from_csv(
    CODELIST_DIR / "opensafely-chronic-cardiac-disease.csv",
    system="ctv3",
    column="CTV3ID",
)

stroke_codes = codelist_from_csv(
    CODELIST_DIR / "opensafely-stroke-updated.csv",
    system="ctv3",
    column="CTV3ID",
)

tia_codes = codelist_from_csv(
    CODELIST_DIR / "opensafely-transient-ischaemic-attack.csv",
    system="ctv3",
    column="code",
)

dementia_codes = codelist_from_csv(
    CODELIST_DIR / "opensafely-dementia-complete.csv",
    system="ctv3",
    column="code",
)

liver_codes = codelist_from_csv(
    CODELIST_DIR / "opensafely-chronic-liver-disease.csv",
    system="ctv3",
    column="CTV3ID",
)

other_neuro_codes = codelist_from_csv(
    CODELIST_DIR / "opensafely-other-neurological-conditions.csv",
    system="ctv3",
    column="CTV3ID",
)

rheumatoid_arthritis_codes = codelist_from_csv(
    CODELIST_DIR / "opensafely-rheumatoid-arthritis.csv",
    system="ctv3",
    column="CTV3ID",
)

sle_codes = codelist_from_csv(
    CODELIST_DIR / "opensafely-systemic-lupus-erythematosus-sle.csv",
    system="ctv3",
    column="CTV3ID",
)

psoriasis_codes = codelist_from_csv(
    CODELIST_DIR / "opensafely-psoriasis.csv",
    system="ctv3",
    column="code",
)

dialysis_codes = codelist_from_csv(
    CODELIST_DIR / "opensafely-dialysis.csv",
    system="ctv3",
    column="CTV3ID",
)

creatinine_codes = codelist_from_csv(
    CODELIST_DIR / "user-bangzheng-creatinine-value.csv",
    system="snomed",
    column="code",
)
