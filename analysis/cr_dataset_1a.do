********************************************************************************
*	Do-file:		cr_dataset_1a.do
*	Project:		Bias
*	Programmed by:	Emily Herrett
*	Data used:		Data in memory (from input.csv)
*	Data created:	analysis_dataset.dta  (main analysis dataset)
*	Other output:	None
*
********************************************************************************
*	Purpose:		This do-file creates the variables required for the 
*					main analysis and saves into Stata datasets.
********************************************************************************

*set filepaths
    global projectdir `c(pwd)'
    dis "$projectdir"
    global outdir $projectdir/output
    dis "$outdir"
    cap mkdir $projectdir/output/tables
    global tables $projectdir/output/tables
    dis "$tables"
    global logs $projectdir/logs
    dis "$logs"


* Open a log file
cap log close
cap log using "$outdir/cr_dataset_1a.txt", replace t

clear
import delimited "$outdir/input"

****************************
*Create required cohort
****************************
* DROP IF DIED ON/BEFORE STUDY START DATE
	noi di "DIED ON/BEFORE STUDY START DATE:" 

* Age: Exclude children
	noi di "DROPPING AGE<18:" 
	drop if age<18

* Age: Exclude those with implausible ages
	assert age<.
	noi di "DROPPING AGE<105:" 
	drop if age>105

* Sex: Exclude categories other than M and F
	assert inlist(sex, "M", "F", "I", "U")
	noi di "DROPPING GENDER NOT M/F:" 
	drop if inlist(sex, "I", "U")
	 
*Emily - other checks to cohort inclusion criteria

******************************
*Convert strings to dates
******************************

noi di "CONVERT DATES TO STATA DATES" 
sum

foreach var of varlist covid_vax first_positive_test_date bmi_date_measured smoking_status_date ///
hypertension bp_sys_date_measured bp_dias_date_measured dementia diabetes hba1c_mmol_per_mol_date ///
hba1c_percentage_date copd other_respiratory cancer haem_cancer permanent_immunodeficiency transplant ///
asplenia aplastic_anaemia temporary_immunodeficiency heart_failure stroke tia myocardial_infarct ///
heart_disease pad vte af systemic_lupus_erythematosus rheumatoid_arthritis psoriasis ///
chronic_liver_disease other_neuro creatinine_date dialysis {
	gen year = substr(`var',1,4)
	gen month=substr(`var',6,2)
	gen day=substr(`var',9,2)
	replace day="1" if month!="" & day==""
	destring year month day, replace
	gen edate = mdy(month, day, year)
	drop `var'
	rename edate `var'
	format `var' %td
	drop year month day
}

rename systemic_lupus_erythematosus sle

noi di "For each date variable indicating a comorbidity, define whether morbidity onset was prior to index date"

	display d(01September2022) /// 22889 
	
	local indexdate "22889"
	foreach var of varlist covid_vax - dialysis {
		gen `var'_index=1 if `var'<=`indexdate' & `var'!=.
		rename `var' `var'
	}

*******************************
*RECODE IMPLAUSIBLE VALUES
*******************************
* BMI 
	sum bmi
	replace bmi = . if !inrange(bmi, 15, 50)
	
*BLOOD PRESSURE
	sum bp_sys
	sum bp_dias
	replace bp_sys=. if bp_sys>300
	replace bp_sys=. if bp_sys<20

*emily - check any more implausible values?
	
*******************************	
*DESTRING KEY VARIABLES - SMOKING, AGE GROUP, SEX, ETHNICITY, STP, REGION
*******************************
	*SMOKING S=SMOKER, E=EX SMOKER, N=NON-SMOKER, M-MISSING
		tab smoking_status
		gen smok_status=.
		replace smok_status=1 if smoking_status=="N"
		replace smok_status=2 if smoking_status=="E"
		replace smok_status=3 if smoking_status=="S"
		tab smok_status smoking_status, m
		drop smoking_status
		
	*AGE GROUP 
		tab ageband_broad
		gen agegroup=.
		replace agegroup=1 if ageband_broad=="18-39"
		replace agegroup=2 if ageband_broad=="40-49"
		replace agegroup=3 if ageband_broad=="50-59"
		replace agegroup=4 if ageband_broad=="60-69"
		replace agegroup=5 if ageband_broad=="70-79"
		replace agegroup=6 if ageband_broad=="80+"
		tab agegroup ageband_broad, m
		drop ageband_broad
	
	*SEX
		tab sex
		gen sex2=.
		replace sex2=1 if sex=="M"
		replace sex2=2 if sex=="F"
		tab sex sex2, m
		drop sex
		rename sex2 sex
	
	*ETHNICITY
		tab ethnicity
		gen eth5=.
		replace eth5=1 if ethnicity=="White"
		replace eth5=2 if ethnicity=="Black"
		replace eth5=3 if ethnicity=="South Asian"
		replace eth5=4 if ethnicity=="Mixed"
		replace eth5=5 if ethnicity=="Other"
		tab eth5 ethnicity, m
		drop ethnicity
		
	*STP
		tab stp
		gen stp2=substr(stp,4,2)
		destring stp2, replace	
		drop stp 
		rename stp2 stp 
		
	*REGION 
		tab region
		gen region_n=.
		replace region_n=1 if region=="East Midlands"
		replace region_n=2 if region=="East of England"
		replace region_n=3 if region=="London"
		replace region_n=4 if region=="North East"
		replace region_n=5 if region=="North West"
		replace region_n=6 if region=="South East"
		replace region_n=7 if region=="West Midlands"
		replace region_n=8 if region=="Yorkshire and the Humber"
		tab region region_n, m
		drop region
		rename region_n region
		
	*IMD
		rename index_of_multiple_deprivation imd_o
		egen imd = cut(imd_o), group(5) icodes
		replace imd = imd + 1
		replace imd = . if imd_o==-1
		drop imd_o
		* Reverse the order (so high is more deprived)
		recode imd 5=1 4=2 3=3 2=4 1=5 .=.

		noi di "DROPPING IF NO IMD" 
		drop if imd>=.
	
*******************************************************
*CATEGORISE VARIABLES TO MATCH FIZZ AND KRISHNAN'S PAPER
*******************************************************
	*BMI
		 gen obese4cat=.
		 replace obese4cat=0 if bmi<18.5
		 replace obese4cat=1 if bmi>=18.5 & bmi<24.99999
		 replace obese4cat=2 if bmi>=25 & bmi<29.99999
		 replace obese4cat=3 if bmi>=30 & bmi<34.99999
		 replace obese4cat=4 if bmi>=35 & bmi<39.99999	 
		 replace obese4cat=5 if bmi>=40 & bmi!=.
		 bysort obese4cat: sum bmi
		 drop bmi
		
	*RESPIRATORY DISEASE
		tab asthma
		gen chronic_respiratory_disease=1 if other_respiratory_index==1 | copd_index==1
		replace chronic_respiratory_disease=0 if chronic_respiratory_disease==.
		drop other_respiratory_index copd_index
	
	*CANCER - HAEM (0=no, 1=diagnosed<1 year ago, 2=diagnosed 1-4.9 years ago, 3=diagnosed 5+ years ago)
		gen distance=`indexdate'-haem_cancer
		replace distance=. if haem_cancer>`indexdate'
		gen haemcancer=.
		replace haemcancer=1 if distance<365
		replace haemcancer=2 if distance>=365 & distance<1826
		replace haemcancer=3 if distance>=1826 & distance!=.
		drop distance
		
	*CANCER - NON-HAEM (0=no, 1=diagnosed<1 year ago, 2=diagnosed 1-4.9 years ago, 3=diagnosed 5+ years ago)
		gen distance=`indexdate'-cancer
		replace distance=. if cancer>`indexdate'
		gen cancer2=.
		replace cancer2=1 if distance<365
		replace cancer2=2 if distance>=365 & distance<1826
		replace cancer2=3 if distance>=1826 & distance!=.
		drop distance cancer
		rename cancer2 cancer 
		
	*EGFR
	
	
	*BLOOD PRESSURE CATEGORIES (1=normal <130mmHg, 2=elevated 130-140mmHg, stage 1 140-159mmHg, stage 2 160mmHg+)
		gen bp_cat=.
		replace bp_cat=1 if bp_sys<130
		replace bp_cat=2 if bp_sys>=130 & bp_sys<140
		replace bp_cat=3 if bp_sys>=140 & bp_sys<160
		replace bp_cat=4 if bp_sys>=160 & bp_sys!=.
		
	*HIGH BLOOD PRESSURE OR HYPERTENSION
		gen highbp_hyper=1 if hypertension_index==1 | (bp_sys>=140 & bp_sys!=.)
		drop hypertension_index bp_sys bp_dias
		
	*RA, PSORIASIS, SLE
		gen ra_p_sle=1 if sle_index==1 | rheumatoid_arthritis_index==1 | psoriasis_index==1
		drop sle_index rheumatoid_arthritis_index psoriasis_index
		
	*DIABETES WITH HBA1C WITHIN 15 MONTHS (450 DAYS)
		gen distance=`indexdate'-hba1c_mmol_per_mol_date
		replace hba1c_mmol_per_mol=. if distance<0
		replace hba1c_mmol_per_mol=. if distance>450
		
		gen diab=.
		replace diab=1 if diabetes_index==1 & hba1c_mmol_per_mol<58
		replace diab=2 if diabetes_index==1 & hba1c_mmol_per_mol>=58 & hba1c_mmol_per_mol!=.
		replace diab=3 if diabetes_index==1 & hba1c_mmol_per_mol==.
		drop distance hba1c_mmol_per_mol hba1c_mmol_per_mol_date
		
	*STROKE OR DEMENTIA
		gen strokedementia=1 if dementia_index==1 | stroke_index==1
		drop stroke_index dementia_index
	
	*HEART DISEASE INCLUDING MYOCARDIAL INFARCTION
		gen chd=1 if heart_disease_index==1 | myocardial_infarct_index==1
		drop heart_disease_index myocardial_infarct_index
	
	*OTHER IMMUNOSUPPRESSIVE CONDITION (HUMAN IMMUNODEFICIENCY VIRUS (HIV) OR A CONDITION INDUCING PERMANENT IMMUNODEFICIENCY EVER DIAGNOSED, OR APLASTIC ANAEMIA OR TEMPORARY IMMUNODEFICIENCY RECORDED WITHIN THE LAST YEAR) HIV SICKLE CELL
		gen distance=`indexdate'-temporary_immunodeficiency
		replace temporary_immunodeficiency_index=. if distance<0
		replace temporary_immunodeficiency_index=. if distance>365
		gen immunodeficiency=.
		replace immunodeficiency=1 if temporary_immunodeficiency_index==1
		replace immunodeficiency=2 if permanent_immunodeficiency_index==1
		drop temporary_immunodeficiency_index permanent_immunodeficiency_index
		
	foreach var of varlist covid_vax - dialysis {
		drop `var'
	}

export delimited using "$outdir/cr_dataset_1a.csv", replace	