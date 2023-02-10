from codelists_ehrql import *
from databuilder.codes import SNOMEDCTCode
from databuilder.ehrql import Dataset, case, days, when, years
from databuilder.tables.beta import tpp
from variables_lib import (
    addresses_active_for_patient_at,
    practice_registrations_active_for_patient_at,
)

# Short alias for commonly used table
ce = tpp.clinical_events

dataset = Dataset()


index_date = "2022-09-01"
# Date household identification was run
household_ident_date = "2020-02-01"

# define the study variables

# in CIS or not
dataset.in_cis = tpp.ons_cis.take(
    tpp.ons_cis.visit_date.is_between(index_date - years(3), index_date)
).exists_for_patient()

# vaccination
vax = tpp.vaccinations
dataset.covid_vax = (
    vax.take(vax.target_disease == "SARS-2 CORONAVIRUS")
    .take(vax.date <= index_date)
    .sort_by(vax.date)
    .first_for_patient()
    .date
)


# DEMOGRAPHICS - sex, age, ethnicity

# Note possible values are now: male, female, intersex, unknown
dataset.sex = tpp.patients.sex

age = (index_date - tpp.patients.date_of_birth).years
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
    ce.take(ce.snomedct_code.is_in(ethnicity_codes))
    .sort_by(ce.date)
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

deaths = tpp.ons_deaths
dataset.died = deaths.take(deaths.date <= index_date).exists_for_patient()

practice_reg = practice_registrations_active_for_patient_at(index_date)
practice_reg_2020 = practice_registrations_active_for_patient_at(household_ident_date)

dataset.is_registered_with_tpp = practice_reg.exists_for_patient()

# registered with the practice for 90 days prior to index date
dataset.has_follow_up = practice_reg.start_date <= index_date - days(90)

# registered with TPP on date of household identification (1st Feb 2020)
dataset.is_registered_with_tpp_feb2020 = practice_reg_2020.exists_for_patient()


# HOUSEHOLD INFORMATION

household = tpp.household_memberships_2020
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
    ce.take(ce.snomedct_code.is_in(high_risk_codes))
    .sort_by(ce.date)
    .last_for_patient()
    .date
)
# ## NOT SHIELDED GROUP (medium and low risk) - only flag if later than 'shielded'
less_vulnerable_date = (
    ce.take(ce.snomedct_code.is_in(not_high_risk_codes))
    .take(ce.date.is_on_or_after(severely_clinically_vulnerable_date))
    .sort_by(ce.date)
    .first_for_patient()
    .date
)
dataset.shielded = (
    severely_clinically_vulnerable_date.is_not_null() & less_vulnerable_date.is_null()
)

# ## COVID TESTING OPENSAFELY
tests = tpp.sgss_covid_all_tests
dataset.first_positive_test_date = (
    tests.take(tests.is_positive)
    .take(tests.specimen_taken_date <= index_date)
    .sort_by(tests.specimen_taken_date)
    .first_for_patient()
    .specimen_taken_date
)

# LIFESTYLE VARIABLES

# BMI
# Definition from:
# https://github.com/opensafely-core/databuilder/issues/1011#issuecomment-1425711630
ce = tpp.clinical_events
bmi_record = (
    ce.take(
        ce.snomedct_code.is_in(
            [SNOMEDCTCode("60621009"), SNOMEDCTCode("846931000000101")]
        )
    )
    .take((ce.numeric_value > 4.0) & (ce.numeric_value < 200.0))
    .take(ce.date >= tpp.patients.date_of_birth + years(16))
    .take(ce.date.is_on_or_before("2010-03-01"))
    .sort_by(ce.date)
    .last_for_patient()
)
dataset.bmi = bmi_record.numeric_value
dataset.bmi_date_measured = bmi_record.date

# SMOKING
most_recent_smoking_record = (
    ce.take(ce.ctv3_code.is_in(clear_smoking_codes))
    .take(ce.date.is_on_or_before(index_date))
    .sort_by(ce.date)
    .last_for_patient()
)
most_recent_smoking_code = most_recent_smoking_record.ctv3_code.to_category(
    clear_smoking_codes.Category
)

ever_smoked_codes = [
    code
    for (code, category) in clear_smoking_codes.Category.items()
    if category in ("S", "E")
]
has_ever_smoked = (
    ce.take(ce.ctv3_code.is_in(ever_smoked_codes))
    .take(ce.date.is_on_or_before(index_date))
    .sort_by(ce.date)
    .exists_for_patient()
)

dataset.smoking_status = case(
    when(most_recent_smoking_code == "S").then("S"),
    when(has_ever_smoked).then("E"),
    when(most_recent_smoking_code == "N").then("N"),
    default="M",
)
dataset.smoking_status_date = most_recent_smoking_record.date


# COMORBIDITIES


# HYPERTENSION - CLINICAL CODES ONLY
dataset.hypertension = (
    ce.take(ce.ctv3_code.is_in(hypertension_codes))
    .take(ce.date.is_on_or_before(index_date))
    .sort_by(ce.date)
    .first_for_patient()
    .date
)

# HIGH BLOOD PRESSURE
# Most recent date with a blood pressure record
bp_date = (
    ce.take(ce.ctv3_code.is_in(systolic_blood_pressure_codes))
    .take(ce.date.is_on_or_before(index_date))
    .sort_by(ce.date)
    .last_for_patient()
    .date
)
# Average systolic blood pressure on that day
dataset.bp_sys = (
    ce.take(ce.ctv3_code.is_in(systolic_blood_pressure_codes))
    .take(ce.date == bp_date)
    .numeric_value.mean_for_patient()
)
# Average diastolic blood pressure on that day
dataset.bp_dias = (
    ce.take(ce.ctv3_code.is_in(diastolic_blood_pressure_codes))
    .take(ce.date == bp_date)
    .numeric_value.mean_for_patient()
)
# Assign the blood pressure date to the columns the existing analysis code is expecting
dataset.bp_sys_date_measured = bp_date
dataset.bp_dias_date_measured = bp_date

# DEMENTIA
dataset.dementia = (
    ce.take(ce.ctv3_code.is_in(dementia_codes))
    .take(ce.date.is_on_or_before(index_date))
    .sort_by(ce.date)
    .first_for_patient()
    .date
)

# DIABETES
dataset.diabetes = (
    ce.take(ce.ctv3_code.is_in(diabetes_codes))
    .take(ce.date.is_on_or_before(index_date))
    .sort_by(ce.date)
    .first_for_patient()
    .date
)

hba1c_measurement = (
    ce.take(ce.ctv3_code.is_in(hba1c_new_codes))
    .take(ce.date.is_on_or_before(index_date))
    .sort_by(ce.date)
    .last_for_patient()
)
dataset.hba1c_mmol_per_mol = hba1c_measurement.numeric_value
dataset.hba1c_mmol_per_mol_date = hba1c_measurement.date

hba1c_percentage = (
    ce.take(ce.ctv3_code.is_in(hba1c_old_codes))
    .take(ce.date.is_on_or_before(index_date))
    .sort_by(ce.date)
    .last_for_patient()
)
dataset.hba1c_percentage = hba1c_percentage.numeric_value
dataset.hba1c_percentage_date = hba1c_percentage.date

# COPD
dataset.copd = (
    ce.take(ce.ctv3_code.is_in(copd_codes))
    .take(ce.date.is_on_or_before(index_date))
    .sort_by(ce.date)
    .first_for_patient()
    .date
)

# OTHER RESPIRATORY DISEASES
dataset.other_respiratory = (
    ce.take(ce.ctv3_code.is_in(other_respiratory_codes))
    .take(ce.date.is_on_or_before(index_date))
    .sort_by(ce.date)
    .first_for_patient()
    .date
)

# asthma
latest_asthma_code_date = (
    ce.take(ce.ctv3_code.is_in(asthma_codes))
    .take(ce.date.is_on_or_before(index_date))
    .sort_by(ce.date)
    .last_for_patient()
    .date
)
recent_asthma_code = latest_asthma_code_date >= index_date - days(3 * 365)
asthma_code_ever = latest_asthma_code_date.is_not_null()
copd_code_ever = ce.take(
    ce.ctv3_code.is_in(chronic_respiratory_disease_codes)
).exists_for_patient()

meds = tpp.medications
prednisolone_last_year = (
    meds.take(meds.dmd_code.is_in(pred_codes))
    .take(meds.date.is_on_or_between(index_date - days(365), index_date))
    .count_for_patient()
)

dataset.asthma = case(
    when(~recent_asthma_code & (~asthma_code_ever | copd_code_ever)).then("0"),
    when((prednisolone_last_year == 0) | (prednisolone_last_year > 4)).then("1"),
    when((prednisolone_last_year > 0) & (prednisolone_last_year < 5)).then("2"),
    default="0",
)

# CANCER - 3 TYPES
# TODO: Union needs to be natively supported by the Codelist class
combined_cancer_codes = lung_cancer_codes.codes | other_cancer_codes.codes
dataset.cancer = (
    ce.take(ce.ctv3_code.is_in(combined_cancer_codes))
    .take(ce.date.is_on_or_before(index_date))
    .sort_by(ce.date)
    .first_for_patient()
    .date
)
dataset.haem_cancer = (
    ce.take(ce.ctv3_code.is_in(haem_cancer_codes))
    .take(ce.date.is_on_or_before(index_date))
    .sort_by(ce.date)
    .first_for_patient()
    .date
)

# IMMUNOSUPPRESSION

# ### PERMANENT
combined_immune_codes = (
    hiv_codes.codes | permanent_immune_codes.codes | sickle_cell_codes.codes
)
dataset.permanent_immunodeficiency = (
    ce.take(ce.ctv3_code.is_in(combined_immune_codes))
    .take(ce.date.is_on_or_before(index_date))
    .sort_by(ce.date)
    .last_for_patient()
    .date
)

dataset.transplant = (
    ce.take(ce.ctv3_code.is_in(organ_transplant_codes))
    .take(ce.date.is_on_or_before(index_date))
    .sort_by(ce.date)
    .last_for_patient()
    .date
)
dataset.asplenia = (
    ce.take(ce.ctv3_code.is_in(spleen_codes))
    .take(ce.date.is_on_or_before(index_date))
    .sort_by(ce.date)
    .last_for_patient()
    .date
)
dataset.aplastic_anaemia = (
    ce.take(ce.ctv3_code.is_in(aplastic_codes))
    .take(ce.date.is_on_or_between(index_date - days(365), index_date))
    .sort_by(ce.date)
    .last_for_patient()
    .date
)

# ### TEMPORARY
dataset.temporary_immunodeficiency = (
    ce.take(ce.ctv3_code.is_in(temp_immune_codes))
    .take(ce.date.is_on_or_between("2019-03-01", index_date))
    .sort_by(ce.date)
    .last_for_patient()
    .date
)

# CARDIOVASCULAR DISEASE

# HEART FAILURE
dataset.heart_failure = (
    ce.take(ce.ctv3_code.is_in(heart_failure_codes))
    .take(ce.date.is_on_or_before(index_date))
    .sort_by(ce.date)
    .first_for_patient()
    .date
)
# stroke
dataset.stroke = (
    ce.take(ce.ctv3_code.is_in(stroke_codes))
    .take(ce.date.is_on_or_before(index_date))
    .sort_by(ce.date)
    .last_for_patient()
    .date
)
# Transient ischaemic attack
dataset.tia = (
    ce.take(ce.ctv3_code.is_in(tia_codes))
    .take(ce.date.is_on_or_before(index_date))
    .sort_by(ce.date)
    .last_for_patient()
    .date
)
# Myocardial infarction
dataset.myocardial_infarct = (
    ce.take(ce.ctv3_code.is_in(mi_codes))
    .take(ce.date.is_on_or_before(index_date))
    .sort_by(ce.date)
    .last_for_patient()
    .date
)
# Chronic heart disease
dataset.heart_disease = (
    ce.take(ce.ctv3_code.is_in(chd_codes))
    .take(ce.date.is_on_or_before(index_date))
    .sort_by(ce.date)
    .last_for_patient()
    .date
)
# Peripheral artery disease
dataset.pad = (
    ce.take(ce.ctv3_code.is_in(pad_codes))
    .take(ce.date.is_on_or_before(index_date))
    .sort_by(ce.date)
    .last_for_patient()
    .date
)
# Venous thromboembolism
dataset.vte = (
    ce.take(ce.ctv3_code.is_in(vte_codes))
    .take(ce.date.is_on_or_before(index_date))
    .sort_by(ce.date)
    .last_for_patient()
    .date
)
# Atrial fibrillation
dataset.af = (
    ce.take(ce.ctv3_code.is_in(af_codes))
    .take(ce.date.is_on_or_before(index_date))
    .sort_by(ce.date)
    .last_for_patient()
    .date
)
# Lupus
dataset.systemic_lupus_erythematosus = (
    ce.take(ce.ctv3_code.is_in(sle_codes))
    .take(ce.date.is_on_or_before(index_date))
    .sort_by(ce.date)
    .last_for_patient()
    .date
)
# rheumatoid arthritis
dataset.rheumatoid_arthritis = (
    ce.take(ce.ctv3_code.is_in(rheumatoid_arthritis_codes))
    .take(ce.date.is_on_or_before(index_date))
    .sort_by(ce.date)
    .last_for_patient()
    .date
)
# psoriasis
dataset.psoriasis = (
    ce.take(ce.ctv3_code.is_in(psoriasis_codes))
    .take(ce.date.is_on_or_before(index_date))
    .sort_by(ce.date)
    .last_for_patient()
    .date
)
# liver disease
dataset.chronic_liver_disease = (
    ce.take(ce.ctv3_code.is_in(liver_codes))
    .take(ce.date.is_on_or_before(index_date))
    .sort_by(ce.date)
    .last_for_patient()
    .date
)
# other neurological disease
dataset.other_neuro = (
    ce.take(ce.ctv3_code.is_in(other_neuro_codes))
    .take(ce.date.is_on_or_before(index_date))
    .sort_by(ce.date)
    .last_for_patient()
    .date
)
# CKD
creatinine = (
    ce.take(ce.snomedct_code.is_in(creatinine_codes))
    .take(ce.date.is_on_or_before(index_date))
    .sort_by(ce.date)
    .last_for_patient()
)
dataset.creatinine = creatinine.numeric_value
dataset.creatinine_date = creatinine.date
# kidney dialysis
dataset.dialysis = (
    ce.take(ce.ctv3_code.is_in(dialysis_codes))
    .take(ce.date.is_on_or_before(index_date))
    .sort_by(ce.date)
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
