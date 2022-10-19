	
*RECREATING FIZZ'S NATURE TABLE
***********************************************************************************
*an_table_PublicationDescriptivesTable_1a
*************************************************************************
*Purpose: Create content that is ready to paste into a pre-formatted Word 
* shell "Table 1" (main cohort descriptives) for the Risk Factors paper
*create a table to compare those in CIS to those not in CIS, in terms of demographics and comorbidities

*Requires: final analysis dataset (cr_dataset_1a.dta)
*Coding: Krishnan Bhaskaran, updated to this study by Emily_Herrett
*
*Date drafted: 19/10/2022
*************************************************************************
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

import delimited "$outdir/cr_dataset_1b.csv", clear

*label variables
		label define smok 1 "Non-smoker" 2 "Ex-smoker" 3 "Current smoker"
		label values smok_status smok 
		label define age 1 "18-39" 2 "40-49" 3 "50-59" 4 "60-69" 5 "70-79" 6 "80+"
		label values agegroup age 
		label define sex 1 "Male" 2 "Female"
		label values sex sex
		label define eth 1 "White" 2 "Black" 3 "Asian" 4 "Mixed" 5 "Other"
		label values eth5 eth  
		label define reg 1 "East Midlands" 2 "East of England" 3 "London" 4 "North East" 5 "North West" 6 "South East" 7 "West Midlands" 8 "Yorkshire and the Humber"
		label values region reg
		label define imd 1 "1 least deprived" 2 "2" 3 "3" 4 "4" 5 "5 most deprived" 
		label values imd imd 
		label define obese 0 "<18.5" 1 "18.5-24.9" 2 "25-29.9" 3 "30-34.9 (obese class I)" 4 "35-39.9 (obese class II)" 5 ">=40 (obese class III)"
		label values obese4cat obese 
		label define bplevel 1 "Normal" 2 "Elevated" 3 "Stage 1 hypertension" 4 "Stage 2 hypertension"
		label values bp_cat bplevel 
		label def immun 1 "Temporary immunodeficiency" 2 "Permanent immunodeficiency"
		label values immunodeficiency immun 

		label define wave 0 "Wave 1, 23/03/20-30/05/20" 1 "Easing 1, 31/05/20-06/09/20" 2 "Wave 2, 07/09/20-23/04-21" 3 "Easing 2, 24/04/21 to 27/05/21" 4 "Wave 3, 28/05/21-13/12/21" 5 "Easing 3, 14/12/21-01/09/22"	
	label values wave_test wave  

		rename first_positive_test_date_index covid 
		tab covid 
		replace covid=0 if covid==.

local outcome `1' 
*******************************************************************************
*Generic code to output one row of table
cap prog drop generaterow
program define generaterow
syntax, variable(varname) condition(string)
	
	*put the varname and condition to left so that alignment can be checked vs shell
	file write tablecontent ("`variable'") _tab ("`condition'") _tab
	
	*do an overall count of patients and put the overall denominator in a local macro
	count
	local overalldenom=r(N)
	
	*count if the variable is equal to a certain level, put in a local
	cou if `variable' `condition'
	local nwithcondition = r(N)
	local roundednwithcondition=round(`nwithcondition',5)
	*make another local of the n at each level divided by the total (percent)
	local colpct = 100*(`roundednwithcondition'/`overalldenom')
	*write that into a table with the n at each level and the percent
	file write tablecontent (`roundednwithcondition') _tab (" (") %3.1f (`colpct') (")") _tab

	*count the number with the outcome (covid==yes) and make a local
	cou if covid==1 
	local covid=r(N)
	local rcovid=round(`covid',5)
	*count the number with the outcome at each level of each variable, put in local
	cou if covid==1 & `variable' `condition'
	local covidwithcondition = r(N)
	local roundedcovidwithcondition=round(`covidwithcondition',5)

	*generate the percent of those with the outcome at each level over the total with the outcome
	local pct = 100*(`roundedcovidwithcondition'/`rcovid')
	*write it to the table 
	file write tablecontent (`roundedcovidwithcondition') _tab (" (") %4.2f  (`pct') (")") _tab

	*count those without the outcome and put in a local
	cou if covid==0 
	local not_covid=r(N)
	local rnot_covid=round(`not_covid',5)
	*count the number without the outcome at each level of each variable, put in local
	cou if covid==0 & `variable' `condition'
	local not_covidwithcondition = r(N)
	local rnot_covidwithcondition=round(`not_covidwithcondition',5)
	*generate the percent of those with the outcome at each level over the total with the outcome
	local pct = 100*(`rnot_covidwithcondition '/`rnot_covid')
	*write it to the table 
	file write tablecontent (`rnot_covidwithcondition') _tab (" (") %4.2f  (`pct') (")") _n
	
end

*******************************************************************************
*Generic code to output one section (variable) within table (calls above)
cap prog drop tabulatevariable
prog define tabulatevariable
syntax, variable(varname) start(real) end(real) [missing] 

*for each level of each variable, looking at how many categories are in that variable (WITH LOWEST=START AND HIGHEST=END)
*generate a row of data for that variable and that that level 
*if the missing syntax is specified, add that the level must be greater than missing
	foreach varlevel of numlist `start'/`end'{ 
		generaterow, variable(`variable') condition("==`varlevel'") 
	}
	if "`missing'"!="" generaterow, variable(`variable') condition(">=.") 

end

*******************************************************************************

*Set up output file
cap file close tablecontent
file open tablecontent using $tables/an_table_PublicationDescriptivesTable_1b_os.tsv, write text replace

file write tablecontent "variable" _tab "level" _tab "Total N" _tab "Total percent" _tab "Had COVID, N" _tab "Had COVID, percent" _tab "No COVID, N" _tab "No COVID, percent" _n

gen byte cons=1
tabulatevariable, variable(cons) start(1) end(1) 
file write tablecontent 

tabulatevariable, variable(agegroup) start(1) end(6) 
file write tablecontent 

tabulatevariable, variable(sex) start(1) end(2) 
file write tablecontent 

tabulatevariable, variable(obese4cat) start(0) end(5) missing
file write tablecontent 

tabulatevariable, variable(smok_status) start(1) end(3) missing
file write tablecontent 

tabulatevariable, variable(eth5) start(1) end(5) missing 
file write tablecontent 

tabulatevariable, variable(imd) start(1) end(5) 
file write tablecontent 

tabulatevariable, variable(region) start(1) end(8) 
file write tablecontent 

tabulatevariable, variable(in_cis) start(0) end(1) 
file write tablecontent 

tabulatevariable, variable(wave_test) start(0) end(5) 
file write tablecontent 

tabulatevariable, variable(covid_vax_index) start(1) end(1) 
file write tablecontent 

tabulatevariable, variable(bp_cat) start(1) end(4) missing 

tabulatevariable, variable(highbp_hyper) start(1) end(1) 			

**COMORBIDITIES
*RESPIRATORY - excluding asthma, including copd ***
tabulatevariable, variable(chronic_respiratory_disease) start(1) end(1) 
*ASTHMA
tabulatevariable, variable(asthma) start(1) end(2)  /*no ocs, then with ocs*/
*CARDIAC - chronic heart disease ***
tabulatevariable, variable(chd) start(1) end(1) 
*DIABETES
tabulatevariable, variable(diab) start(1) end(3)  /*controlled, then uncontrolled, then missing a1c*/
file write tablecontent 
*CANCER EX HAEM
tabulatevariable, variable(cancer) start(1) end(3)  /*<1, 1-4.9, 5+ years ago*/
file write tablecontent 
*CANCER HAEM
tabulatevariable, variable(haemcancer) start(1) end(3)  /*<1, 1-4.9, 5+ years ago*/
file write tablecontent 
*REDUCED KIDNEY FUNCTION*****
*tabulatevariable, variable(reduced_kidney_function_cat2) start(2) end(4) 
*DIALYSIS
tabulatevariable, variable(dialysis_index) start(1) end(1) 
*LIVER
tabulatevariable, variable(chronic_liver_disease_index) start(1) end(1) 
*DEMENTIA/STROKE
tabulatevariable, variable(strokedementia) start(1) end(1) 
*OTHER NEURO
tabulatevariable, variable(other_neuro_index) start(1) end(1) 
*ORGAN TRANSPLANT
tabulatevariable, variable(transplant_index) start(1) end(1) 
*SPLEEN
tabulatevariable, variable(asplenia_index) start(1) end(1) 
*RA_SLE_PSORIASIS
tabulatevariable, variable(ra_p_sle) start(1) end(1) 
*OTHER IMMUNOSUPPRESSION****
tabulatevariable, variable(immunodeficiency) start(1) end(2) 


cou
local denom = r(N)
cou if bmi==.
local bmimissing=r(N)
cou if smok_status==.
local smokmissing=r(N)
file write tablecontent _n ("*missing could be included in 'not obese' (n = ") (`bmimissing') (" (") %3.1f (100*`bmimissing'/`denom') ("%); missing smoking could be included in 'never smoker' (n = ") (`smokmissing') (" (") %3.1f (100*`smokmissing'/`denom') ("%))") 
*/

file close tablecontent

*REDACT VALUES OF 5 OR LOWER, INCLUDING ZEROES (ZEROES MAY HAVE BEEN ROUNDED TO FROM COUNTS OF 1 OR 2; FIVES MAY HAVE BEEN ROUNDED DOWN FROM COUNTS OF 6 OR 7)
clear
import delimited $tables/an_table_PublicationDescriptivesTable_1b_os.tsv
	*redact if number is 5 or 0
	local columns " "total" "hadcovid" "nocovid" "
	foreach col in `columns' {
		replace `col'n=. if `col'n<=5
		replace `col'percent="redacted" if `col'n==.
		
	}
	
export delimited "$tables/an_table_PublicationDescriptivesTable_1b_os_redacted.tsv", replace
