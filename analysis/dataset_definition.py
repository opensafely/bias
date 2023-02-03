from codelists_ehrql import *
from databuilder.ehrql import Dataset, case, days, when, years
from databuilder.tables.beta import tpp as t
from variables_lib import (
    addresses_active_for_patient_at,
    clinical_events_with_codes,
    practice_registrations_active_for_patient_at,
)

dataset = Dataset()


index_date = "2022-09-01"
# Date household identification was run
household_ident_date = "2020-02-01"

# define the study variables

# in CIS or not
dataset.in_cis = t.ons_cis.take(
    t.ons_cis.visit_date.is_between(index_date - years(3), index_date)
).exists_for_patient()

# vaccination
vax = t.vaccinations
dataset.covid_vax = (
    vax.take(vax.target_disease == "SARS-2 CORONAVIRUS")
    .take(vax.date <= index_date)
    .sort_by(vax.date)
    .first_for_patient()
    .date
)


# DEMOGRAPHICS - sex, age, ethnicity

# Note possible values are now: male, female, intersex, unknown
dataset.sex = t.patients.sex

age = (index_date - t.patients.date_of_birth).years
dataset.age = age
dataset.ageband_broad = case(
    when((age >= 18) & (age < 40)).then("18-39"),
    when((age >= 40) & (age < 50)).then("40-49"),
    when((age >= 50) & (age < 60)).then("50-59"),
    when((age >= 60) & (age < 70)).then("60-69"),
    when((age >= 70) & (age < 80)).then("70-79"),
    when((age >= 80) & (age < 120)).then("80+"),
    default="0",
)


# Ethnicity
ethnicity_primary_care = (
    clinical_events_with_codes(ethnicity_codes)
    .last_for_patient()
    .snomedct_code.to_category(ethnicity_codes.Grouping_6)
)
# TODO: SUS Ethnicity is not yet available in Data Builder, see:
# https://github.com/opensafely-core/databuilder/issues/937
ethnicity_sus = None
ethnicity_combined = ethnicity_primary_care.if_null_then(ethnicity_sus)
dataset.ethnicity = ethnicity_combined.map_values(
    {
        "1": "White",
        "2": "Mixed",
        "3": "South Asian",
        "4": "Black",
        "5": "Other",
    },
    default="Missing",
)


# REGISTRATION DETAILS

dataset.died = t.ons_deaths.take(t.ons_deaths.date <= index_date).exists_for_patient()

practice_reg = practice_registrations_active_for_patient_at(index_date)
practice_reg_2020 = practice_registrations_active_for_patient_at(household_ident_date)

dataset.is_registered_with_tpp = practice_reg.exists_for_patient()

# registered with the practice for 90 days prior to index date
dataset.has_follow_up = practice_reg.start_date <= index_date - days(90)

# registered with TPP on date of household identification (1st Feb 2020)
dataset.is_registered_with_tpp_feb2020 = practice_reg_2020.exists_for_patient()


# HOUSEHOLD INFORMATION

household = t.household_memberships_2020
dataset.household_id = household.household_pseudo_id
dataset.household_size = household.household_size


# ADMINISTRATIVE INFORMATION

address = addresses_active_for_patient_at(index_date)
address_2020 = addresses_active_for_patient_at(household_ident_date)

# index of multiple deprivation, estimate of SES based on patient post code  -
dataset.index_of_multiple_deprivation = address.imd_rounded
# STP REGION
dataset.stp = practice_reg_2020.practice_stp
# URBAN/RURAL LOCATION
dataset.urban = address_2020.rural_urban_classification
# REGION NUTS1
dataset.region = practice_reg.practice_nuts1_region_name


# PRIMIS overall flag for shielded group
# ## SHIELDED GROUP - first flag all patients with "high risk" codes
severely_clinically_vulnerable_date = (
    clinical_events_with_codes(high_risk_codes).last_for_patient().date
)
# ## NOT SHIELDED GROUP (medium and low risk) - only flag if later than 'shielded'
less_vulnerable_date = (
    clinical_events_with_codes(
        not_high_risk_codes, on_or_after=severely_clinically_vulnerable_date
    )
    .first_for_patient()
    .date
)
dataset.shielded = (
    severely_clinically_vulnerable_date.is_not_null() & less_vulnerable_date.is_null()
)

#      ### COVID TESTING OPENSAFELY
#      first_positive_test_date=patients.with_test_result_in_sgss(
#              pathogen="SARS-CoV-2",
#              test_result="positive",
#              on_or_before="index_date",
#              find_first_match_in_period=True,
#              returning="date",
#              date_format="YYYY-MM-DD",
#              return_expectations={
#                  "date": {"earliest": "2020-03-01"},
#                  "rate": "exponential_increase",
#              },
#          ),
#
#      # LIFESTYLE VARIABLES
#          # BMI
#          bmi=patients.most_recent_bmi(
#                  on_or_before="2010-03-01",
#                  minimum_age_at_measurement=16,
#                  include_measurement_date=True,
#                  include_month=True,
#                  return_expectations={
#                      "incidence": 0.6,
#                      "float": {"distribution": "normal", "mean": 35, "stddev": 10},
#                  },
#              ),
#
#
#          # SMOKING
#          smoking_status=patients.categorised_as(
#              {
#                  "S": "most_recent_smoking_code = 'S'",
#                  "E": """
#                          most_recent_smoking_code = 'E' OR (
#                          most_recent_smoking_code = 'N' AND ever_smoked
#                          )
#                      """,
#                  "N": "most_recent_smoking_code = 'N' AND NOT ever_smoked",
#                  "M": "DEFAULT",
#              },
#              return_expectations={
#                  "incidence": 0.9,
#                 "category": {"ratios": {"S": 0.6, "E": 0.1, "N": 0.2, "M": 0.1}}
#              },
#              most_recent_smoking_code=patients.with_these_clinical_events(
#                  clear_smoking_codes,
#                  find_last_match_in_period=True,
#                  on_or_before="index_date",
#                  returning="category",
#              ),
#              ever_smoked=patients.with_these_clinical_events(
#                  filter_codes_by_category(clear_smoking_codes, include=["S", "E"]),
#                  on_or_before="index_date",
#              ),
#          ),
#          smoking_status_date=patients.with_these_clinical_events(
#              clear_smoking_codes,
#              on_or_before="index_date",
#              returning="date",
#              find_last_match_in_period=True,
#              date_format="YYYY-MM-DD",
#              return_expectations={"date": {"latest": "index_date"}},
#          ),
#


# COMORBIDITIES


# HYPERTENSION - CLINICAL CODES ONLY
dataset.hypertension = (
    clinical_events_with_codes(hypertension_codes, on_or_before=index_date)
    .first_for_patient()
    .date
)

#          # HIGH BLOOD PRESSURE
#          # https://github.com/ebmdatalab/tpp-sql-notebook/issues/35
#          bp_sys=patients.mean_recorded_value(
#              systolic_blood_pressure_codes,
#              on_most_recent_day_of_measurement=True,
#              on_or_before="index_date",
#              include_measurement_date=True,
#              include_month=True,
#              return_expectations={
#                  "float": {"distribution": "normal", "mean": 80, "stddev": 10},
#                  "date": {"latest": "index_date"},
#                  "incidence": 0.95,
#              },
#          ),
#          bp_dias=patients.mean_recorded_value(
#              diastolic_blood_pressure_codes,
#              on_most_recent_day_of_measurement=True,
#              on_or_before="2020-02-01",
#              include_measurement_date=True,
#              include_month=True,
#              return_expectations={
#                  "float": {"distribution": "normal", "mean": 120, "stddev": 10},
#                  "date": {"latest": "2020-02-15"},
#                  "incidence": 0.95,
#              },
#          ),
#

# DEMENTIA
dataset.dementia = (
    clinical_events_with_codes(dementia_codes, on_or_before=index_date)
    .first_for_patient()
    .date
)

# DIABETES
dataset.diabetes = (
    clinical_events_with_codes(diabetes_codes, on_or_before=index_date)
    .first_for_patient()
    .date
)

hba1c_measurement = clinical_events_with_codes(
    hba1c_new_codes, on_or_before=index_date
).last_for_patient()
dataset.hba1c_mmol_per_mol = hba1c_measurement.numeric_value
dataset.hba1c_mmol_per_mol_date = hba1c_measurement.date

hba1c_percentage = clinical_events_with_codes(
    hba1c_old_codes, on_or_before=index_date
).last_for_patient()
dataset.hba1c_percentage = hba1c_percentage.numeric_value
dataset.hba1c_percentage_date = hba1c_percentage.date

# COPD
dataset.copd = (
    clinical_events_with_codes(copd_codes, on_or_before=index_date)
    .first_for_patient()
    .date
)

# OTHER RESPIRATORY DISEASES
dataset.other_respiratory = (
    clinical_events_with_codes(other_respiratory_codes, on_or_before=index_date)
    .first_for_patient()
    .date
)

#
#          # asthma
#          asthma=patients.categorised_as(
#              {
#                  "0": "DEFAULT",
#                  "1": """
#                      (
#                      recent_asthma_code OR (
#                          asthma_code_ever AND NOT
#                          copd_code_ever
#                      )
#                      ) AND (
#                      prednisolone_last_year = 0 OR
#                      prednisolone_last_year > 4
#                      )
#                  """,
#                  "2": """
#                      (
#                      recent_asthma_code OR (
#                          asthma_code_ever AND NOT
#                          copd_code_ever
#                      )
#                      ) AND
#                      prednisolone_last_year > 0 AND
#                      prednisolone_last_year < 5
#
#                  """,
#              },
#              return_expectations={
#                  "category": {"ratios": {"0": 0.6, "1": 0.1, "2": 0.3}}
#              },
#              recent_asthma_code=patients.with_these_clinical_events(
#                  asthma_codes, between=["index_date - 3 years", "index_date"],
#              ),
#              asthma_code_ever=patients.with_these_clinical_events(asthma_codes),
#              copd_code_ever=patients.with_these_clinical_events(
#                  chronic_respiratory_disease_codes
#              ),
#              prednisolone_last_year=patients.with_these_medications(
#                  pred_codes,
#                  between=["index_date - 365 days", "index_date"],
#                  returning="number_of_matches_in_period",
#              ),
#          ),

# CANCER - 3 TYPES
# TODO: Union needs to be natively supported by the Codelist class
combined_cancer_codes = lung_cancer_codes.codes | other_cancer_codes.codes
dataset.cancer = (
    clinical_events_with_codes(combined_cancer_codes, on_or_before=index_date)
    .first_for_patient()
    .date
)
dataset.haem_cancer = (
    clinical_events_with_codes(haem_cancer_codes, on_or_before=index_date)
    .first_for_patient()
    .date
)

# IMMUNOSUPPRESSION

# ### PERMANENT
combined_immune_codes = (
    hiv_codes.codes | permanent_immune_codes.codes | sickle_cell_codes.codes
)
dataset.permanent_immunodeficiency = (
    clinical_events_with_codes(combined_immune_codes, on_or_before=index_date)
    .last_for_patient()
    .date
)

dataset.transplant = (
    clinical_events_with_codes(organ_transplant_codes, on_or_before=index_date)
    .last_for_patient()
    .date
)
dataset.asplenia = (
    clinical_events_with_codes(spleen_codes, on_or_before=index_date)
    .last_for_patient()
    .date
)
dataset.aplastic_anaemia = (
    clinical_events_with_codes(
        aplastic_codes, on_or_between=[index_date - days(365), index_date]
    )
    .last_for_patient()
    .date
)

# ### TEMPORARY
dataset.temporary_immunodeficiency = (
    clinical_events_with_codes(
        temp_immune_codes, on_or_between=["2019-03-01", index_date]
    )
    .last_for_patient()
    .date
)

# CARDIOVASCULAR DISEASE

# HEART FAILURE
dataset.heart_failure = (
    clinical_events_with_codes(heart_failure_codes, on_or_before=index_date)
    .first_for_patient()
    .date
)
# stroke
dataset.stroke = (
    clinical_events_with_codes(stroke_codes, on_or_before=index_date)
    .last_for_patient()
    .date
)
# Transient ischaemic attack
dataset.tia = (
    clinical_events_with_codes(tia_codes, on_or_before=index_date)
    .last_for_patient()
    .date
)
# Myocardial infarction
dataset.myocardial_infarct = (
    clinical_events_with_codes(mi_codes, on_or_before=index_date)
    .last_for_patient()
    .date
)
# Chronic heart disease
dataset.heart_disease = (
    clinical_events_with_codes(chd_codes, on_or_before=index_date)
    .last_for_patient()
    .date
)
# Peripheral artery disease
dataset.pad = (
    clinical_events_with_codes(pad_codes, on_or_before=index_date)
    .last_for_patient()
    .date
)
# Venous thromboembolism
dataset.vte = (
    clinical_events_with_codes(vte_codes, on_or_before=index_date)
    .last_for_patient()
    .date
)
# Atrial fibrillation
dataset.af = (
    clinical_events_with_codes(af_codes, on_or_before=index_date)
    .last_for_patient()
    .date
)
# Lupus
dataset.systemic_lupus_erythematosus = (
    clinical_events_with_codes(sle_codes, on_or_before=index_date)
    .last_for_patient()
    .date
)
# rheumatoid arthritis
dataset.rheumatoid_arthritis = (
    clinical_events_with_codes(rheumatoid_arthritis_codes, on_or_before=index_date)
    .last_for_patient()
    .date
)
# psoriasis
dataset.psoriasis = (
    clinical_events_with_codes(psoriasis_codes, on_or_before=index_date)
    .last_for_patient()
    .date
)
# liver disease
dataset.chronic_liver_disease = (
    clinical_events_with_codes(liver_codes, on_or_before=index_date)
    .last_for_patient()
    .date
)
# other neurological disease
dataset.other_neuro = (
    clinical_events_with_codes(other_neuro_codes, on_or_before=index_date)
    .last_for_patient()
    .date
)
# CKD
creatinine = clinical_events_with_codes(
    creatinine_codes, on_or_before=index_date
).last_for_patient()
dataset.creatinine = creatinine.numeric_value
dataset.creatinine_date = creatinine.date
# kidney dialysis
dataset.dialysis = (
    clinical_events_with_codes(dialysis_codes, on_or_before=index_date)
    .last_for_patient()
    .date
)


dataset.set_population(
    (dataset.age >= 18)
    & (dataset.age < 120)
    & dataset.is_registered_with_tpp
    & ~dataset.died
    & dataset.has_follow_up
    & dataset.is_registered_with_tpp_feb2020
)
