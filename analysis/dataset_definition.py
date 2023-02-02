from databuilder.ehrql import Dataset, case, days, when, years
from databuilder.tables.beta import tpp as t
from variables_lib import practice_registrations_active_for_patient_at

dataset = Dataset()

#  # STUDY DEFINITION FOR BASELINE CHARACTERISTICS
#
#  # Import necessary functions
#
#  from cohortextractor import (
#      StudyDefinition,
#      patients,
#      codelist,
#      filter_codes_by_category,
#      codelist_from_csv
#  )
#
#  # Import all codelists
#  from codelists import *
#
#
#  # Specify study definition
#  study = StudyDefinition(

index_date = "2022-09-01"

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


#          ## Ethnicity
#          ethnicity = patients.categorised_as(
#              {"Missing": "DEFAULT",
#              "White": "eth='1' OR (NOT eth AND ethnicity_sus='1')",
#              "Mixed": "eth='2' OR (NOT eth AND ethnicity_sus='2')",
#              "South Asian": "eth='3' OR (NOT eth AND ethnicity_sus='3')",
#              "Black": "eth='4' OR (NOT eth AND ethnicity_sus='4')",
#              "Other": "eth='5' OR (NOT eth AND ethnicity_sus='5')",
#              },
#              return_expectations={
#              "category": {"ratios": {"White": 0.6, "Mixed": 0.1, "South Asian": 0.1, "Black": 0.1, "Other": 0.1}},
#              "incidence": 0.4,
#              },
#
#              ethnicity_sus = patients.with_ethnicity_from_sus(
#                  returning="group_6",
#                  use_most_frequent_code=True,
#                  return_expectations={
#                      "category": {"ratios": {"1": 0.6, "2": 0.1, "3": 0.1, "4": 0.1, "5": 0.1}},
#                      "incidence": 0.4,
#                      },
#              ),
#
#              eth=patients.with_these_clinical_events(
#                  ethnicity_codes,
#                  returning="category",
#                  find_last_match_in_period=True,
#                  on_or_before="today",
#                  return_expectations={
#                      "category": {"ratios": {"1": 0.6, "2": 0.1, "3": 0.1, "4":0.1,"5": 0.1}},
#                      "incidence": 0.75,
#                  },
#              ),
#          ),
#
#


# REGISTRATION DETAILS

dataset.died = t.ons_deaths.take(t.ons_deaths.date <= index_date).exists_for_patient()

practice_reg = practice_registrations_active_for_patient_at(index_date)
dataset.is_registered_with_tpp = practice_reg.exists_for_patient()

# registered with the practice for 90 days prior to index date
dataset.has_follow_up = practice_reg.start_date <= index_date - days(90)

# registered with TPP on date of household identification (1st Feb 2020)
dataset.is_registered_with_tpp_feb2020 = practice_registrations_active_for_patient_at(
    "2020-02-01"
).exists_for_patient()


#      # HOUSEHOLD INFORMATION
#
#          ## household ID
#          household_id=patients.household_as_of(
#              "2020-02-01",
#              returning="pseudo_id",
#              return_expectations={
#                  "int": {"distribution": "normal", "mean": 1000, "stddev": 200},
#                  "incidence": 1,
#              },
#          ),
#
#           ## household size
#          household_size=patients.household_as_of(
#              "2020-02-01",
#              returning="household_size",
#              return_expectations={
#                  "int": {"distribution": "normal", "mean": 3, "stddev": 1},
#                  "incidence": 1,
#              },
#          ),
#
#
#      # ADMINISTRATIVE INFORMATION
#
#          ## index of multiple deprivation, estimate of SES based on patient post code  -
#          index_of_multiple_deprivation=patients.address_as_of(
#              "index_date",
#              returning="index_of_multiple_deprivation",
#              round_to_nearest=100,
#              return_expectations={
#              "rate": "universal",
#              "category": {"ratios": {"100": 0.1, "200": 0.2, "300": 0.7}},
#              },
#          ),
#
#          ## STP REGION
#          stp=patients.registered_practice_as_of(
#              "2020-02-01",
#              returning="stp_code",
#              return_expectations={
#                  "rate": "universal",
#                  "category": {
#                      "ratios": {
#                          "STP1": 0.1,
#                          "STP2": 0.1,
#                          "STP3": 0.1,
#                          "STP4": 0.1,
#                          "STP5": 0.1,
#                          "STP6": 0.1,
#                          "STP7": 0.1,
#                          "STP8": 0.1,
#                          "STP9": 0.1,
#                          "STP10": 0.1,
#                      }
#                  },
#              },
#          ),
#
#          ## URBAN/RURAL LOCATION
#          urban=patients.address_as_of(
#              "2020-02-01",
#              returning="rural_urban_classification",
#              return_expectations={
#                  "rate": "universal",
#                  "category": {"ratios": {1: 0.125, 2: 0.125, 3: 0.125, 4: 0.125, 5: 0.125, 6: 0.125, 7: 0.125, 8: 0.125}},
#              }
#          ),
#
#          ## REGION NUTS1
#          region=patients.registered_practice_as_of(
#              "index_date",
#            returning="nuts1_region_name",
#              return_expectations={
#               "rate": "universal",
#               "category": {
#                  "ratios": {
#                      "North East": 0.1,
#                      "North West": 0.1,
#                      "Yorkshire and the Humber": 0.1,
#                      "East Midlands": 0.1,
#                      "West Midlands": 0.1,
#                      "East of England": 0.1,
#                      "London": 0.2,
#                      "South East": 0.2,
#                      },
#                  },
#              },
#          ),
#
#      # PRIMIS overall flag for shielded group
#
#      shielded=patients.satisfying(
#              """ severely_clinically_vulnerable
#              AND NOT less_vulnerable""",
#          return_expectations={
#              "incidence": 0.01,
#                  },
#
#              ### SHIELDED GROUP - first flag all patients with "high risk" codes
#          severely_clinically_vulnerable=patients.with_these_clinical_events(
#              high_risk_codes, # note no date limits set
#              find_last_match_in_period = True,
#              return_expectations={"incidence": 0.02,},
#          ),
#
#          # find date at which the high risk code was added
#          date_severely_clinically_vulnerable=patients.date_of(
#              "severely_clinically_vulnerable",
#              date_format="YYYY-MM-DD",
#          ),
#
#          ### NOT SHIELDED GROUP (medium and low risk) - only flag if later than 'shielded'
#          less_vulnerable=patients.with_these_clinical_events(
#              not_high_risk_codes,
#              on_or_after="date_severely_clinically_vulnerable",
#              return_expectations={"incidence": 0.01,},
#          ),
#      ),
#
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
#      # COMORBIDITIES
#
#          # HYPERTENSION - CLINICAL CODES ONLY
#          hypertension=patients.with_these_clinical_events(
#              hypertension_codes,
#              on_or_before="index_date",
#              returning="date",
#              find_first_match_in_period=True,
#              date_format="YYYY-MM-DD",
#              return_expectations={"date": {"latest": "index_date"}},
#          ),
#
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
#          # DEMENTIA
#          dementia=patients.with_these_clinical_events(
#              dementia_codes,
#              on_or_before="index_date",
#              returning="date",
#              find_first_match_in_period=True,
#              date_format="YYYY-MM-DD",
#              return_expectations={"date": {"latest": "index_date"}},
#          ),
#
#          # DIABETES
#          diabetes=patients.with_these_clinical_events(
#              diabetes_codes,
#              on_or_before="index_date",
#              returning="date",
#              find_first_match_in_period=True,
#              date_format="YYYY-MM-DD",
#              return_expectations={"date": {"latest": "index_date"}},
#          ),
#          hba1c_mmol_per_mol=patients.with_these_clinical_events(
#              hba1c_new_codes,
#              find_last_match_in_period=True,
#              on_or_before="index_date",
#              returning="numeric_value",
#              include_date_of_match=True,
#              include_month=True,
#              return_expectations={
#                  "date": {"latest": "index_date"},
#                  "float": {"distribution": "normal", "mean": 40.0, "stddev": 20},
#                  "incidence": 0.95,
#              },
#          ),
#          hba1c_percentage=patients.with_these_clinical_events(
#              hba1c_old_codes,
#              find_last_match_in_period=True,
#              on_or_before="index_date",
#              returning="numeric_value",
#              include_date_of_match=True,
#              include_month=True,
#              return_expectations={
#                  "date": {"latest": "index_date"},
#                  "float": {"distribution": "normal", "mean": 5, "stddev": 2},
#                  "incidence": 0.95,
#              },
#          ),
#
#          # COPD
#          copd=patients.with_these_clinical_events(
#              copd_codes,
#              on_or_before="index_date",
#              returning="date",
#              find_first_match_in_period=True,
#              date_format="YYYY-MM-DD",
#              return_expectations={"date": {"latest": "index_date"}},
#          ),
#
#          # OTHER RESPIRATORY DISEASES
#          other_respiratory=patients.with_these_clinical_events(
#              other_respiratory_codes,
#              on_or_before="index_date",
#              returning="date",
#              find_first_match_in_period=True,
#              date_format="YYYY-MM-DD",
#              return_expectations={"date": {"latest": "index_date"}},
#          ),
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
#
#          # CANCER - 3 TYPES
#          cancer=patients.with_these_clinical_events(
#              combine_codelists(lung_cancer_codes, other_cancer_codes),
#              on_or_before="index_date",
#              returning="date",
#              find_first_match_in_period=True,
#              date_format="YYYY-MM-DD",
#              return_expectations={"date": {"latest": "index_date"}},
#          ),
#
#          haem_cancer=patients.with_these_clinical_events(
#              haem_cancer_codes,
#              on_or_before="index_date",
#              returning="date",
#              find_first_match_in_period=True,
#              date_format="YYYY-MM-DD",
#              return_expectations={"date": {"latest": "index_date"}},
#          ),
#
#          # IMMUNOSUPPRESSION
#          #### PERMANENT
#          permanent_immunodeficiency=patients.with_these_clinical_events(
#              combine_codelists(
#                  hiv_codes,
#                  permanent_immune_codes,
#                  sickle_cell_codes,
#              ),
#              on_or_before="index_date",
#              returning="date",
#              find_last_match_in_period=True,
#              date_format="YYYY-MM-DD",
#              return_expectations={"date": {"latest": "index_date"}},
#          ),
#
#          transplant=patients.with_these_clinical_events(
#              organ_transplant_codes,
#              on_or_before="index_date",
#              returning="date",
#              find_last_match_in_period=True,
#              date_format="YYYY-MM-DD",
#              return_expectations={"date": {"latest": "index_date"}},
#          ),
#
#          asplenia=patients.with_these_clinical_events(
#              spleen_codes,
#              on_or_before="index_date",
#              returning="date",
#              find_last_match_in_period=True,
#              date_format="YYYY-MM-DD",
#              return_expectations={"date": {"latest": "index_date"}},
#          ),
#
#          aplastic_anaemia=patients.with_these_clinical_events(
#              aplastic_codes,
#              between=["index_date - 365 days", "index_date"],
#              returning="date",
#              find_last_match_in_period=True,
#              date_format="YYYY-MM-DD",
#              return_expectations={
#                  "date": {"earliest": "2019-03-01", "latest": "index_date"}
#              },
#          ),
#          #### TEMPORARY
#          temporary_immunodeficiency=patients.with_these_clinical_events(
#              temp_immune_codes,
#              between=["2019-03-01", "index_date"],
#              returning="date",
#              find_last_match_in_period=True,
#              date_format="YYYY-MM-DD",
#              return_expectations={
#                  "date": {"earliest": "2019-03-01", "latest": "index_date"}
#              },
#          ),
#
#          # CARDIOVASCULAR DISEASE
#              # HEART FAILURE
#              heart_failure=patients.with_these_clinical_events(
#                  heart_failure_codes,
#                  on_or_before="index_date",
#                  returning="date",
#                  find_first_match_in_period=True,
#                  date_format="YYYY-MM-DD",
#                  return_expectations={"date": {"latest": "index_date"}},
#              ),
#
#              # stroke
#              stroke=patients.with_these_clinical_events(
#                  stroke_codes,
#                  on_or_before="index_date",
#                  returning="date",
#                  find_last_match_in_period=True,
#                  date_format="YYYY-MM-DD",
#                  return_expectations={"date": {"latest": "index_date"}},
#              ),
#              # Transient ischaemic attack
#              tia=patients.with_these_clinical_events(
#                  tia_codes,
#                  on_or_before="index_date",
#                  returning="date",
#                  find_last_match_in_period=True,
#                  date_format="YYYY-MM-DD",
#                  return_expectations={"date": {"latest": "index_date"}},
#              ),
#              # Myocardial infarction
#              myocardial_infarct=patients.with_these_clinical_events(
#                  mi_codes,
#                  on_or_before="index_date",
#                  returning="date",
#                  find_last_match_in_period=True,
#                  date_format="YYYY-MM-DD",
#                  return_expectations={"date": {"latest": "index_date"}},
#              ),
#              # Chronic heart disease
#              heart_disease=patients.with_these_clinical_events(
#                  chd_codes,
#                  on_or_before="index_date",
#                  returning="date",
#                  find_last_match_in_period=True,
#                  date_format="YYYY-MM-DD",
#                  return_expectations={"date": {"latest": "index_date"}},
#              ),
#              # Peripheral artery disease
#              pad=patients.with_these_clinical_events(
#                  pad_codes,
#                  on_or_before="index_date",
#                  returning="date",
#                  find_last_match_in_period=True,
#                  date_format="YYYY-MM-DD",
#                  return_expectations={"date": {"latest": "index_date"}},
#              ),
#              # Venous thromboembolism
#              vte=patients.with_these_clinical_events(
#                  vte_codes,
#                  on_or_before="index_date",
#                  returning="date",
#                  find_last_match_in_period=True,
#                  date_format="YYYY-MM-DD",
#                  return_expectations={"date": {"latest": "index_date"}},
#              ),
#
#              # Atrial fibrillation
#              af=patients.with_these_clinical_events(
#                  af_codes,
#                  on_or_before="index_date",
#                  returning="date",
#                  find_last_match_in_period=True,
#                  date_format="YYYY-MM-DD",
#                  return_expectations={"date": {"latest": "index_date"}},
#              ),
#
#          # Lupus
#          systemic_lupus_erythematosus=patients.with_these_clinical_events(
#              sle_codes,
#              on_or_before="index_date",
#              returning="date",
#              find_last_match_in_period=True,
#              date_format="YYYY-MM-DD",
#              return_expectations={"date": {"latest": "index_date"}},
#          ),
#
#          # rheumatoid arthritis
#          rheumatoid_arthritis=patients.with_these_clinical_events(
#              rheumatoid_arthritis_codes,
#              on_or_before="index_date",
#              returning="date",
#              find_last_match_in_period=True,
#              date_format="YYYY-MM-DD",
#              return_expectations={"date": {"latest": "index_date"}},
#          ),
#
#          # psoriasis
#          psoriasis=patients.with_these_clinical_events(
#              psoriasis_codes,
#              on_or_before="index_date",
#              returning="date",
#              find_last_match_in_period=True,
#              date_format="YYYY-MM-DD",
#              return_expectations={"date": {"latest": "index_date"}},
#          ),
#
#          # liver disease
#          chronic_liver_disease=patients.with_these_clinical_events(
#              liver_codes,
#              on_or_before="index_date",
#              returning="date",
#              find_last_match_in_period=True,
#              date_format="YYYY-MM-DD",
#              return_expectations={"date": {"latest": "index_date"}},
#          ),
#
#          # other neurological disease
#          other_neuro = patients.with_these_clinical_events(
#              other_neuro_codes,
#              on_or_before="index_date",
#              returning="date",
#              find_last_match_in_period=True,
#              date_format="YYYY-MM-DD",
#              return_expectations={"date": {"latest": "index_date"}},
#          ),
#
#          # CKD
#          creatinine=patients.with_these_clinical_events(
#              creatinine_codes,
#              find_last_match_in_period=True,
#              on_or_before="index_date",
#              returning="numeric_value",
#              include_date_of_match=True,
#              include_month=True,
#              return_expectations={
#                  "float": {"distribution": "normal", "mean": 60.0, "stddev": 30},
#                  "date": {"earliest": "2019-02-28", "latest": "index_date"},
#                  "incidence": 0.95,
#              },
#          ),
#
#          creatinine_date = patients.with_these_clinical_events(
#              creatinine_codes,
#              find_last_match_in_period = True,
#              returning = "date",
#              date_format = "YYYY-MM-DD",
#          ),
#
#          # kidney dialysis
#          dialysis=patients.with_these_clinical_events(
#              dialysis_codes,
#              on_or_before="index_date",
#              returning="date",
#              find_last_match_in_period=True,
#              date_format="YYYY-MM-DD",
#              return_expectations={"date": {"latest": "index_date"}},
#          ),


dataset.set_population(
    (dataset.age >= 18)
    & (dataset.age < 120)
    & dataset.is_registered_with_tpp
    & ~dataset.died
    & dataset.has_follow_up
    & dataset.is_registered_with_tpp_feb2020
)
