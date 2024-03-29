********************************************************************************
*	Do-file:		cr_dataset_1b.do
*	Project:		Bias
*	Programmed by:	Emily Herrett
*	Data used:		Data in memory (from cr_dataset_1a.csv)
*	Data created:	cr_dataset_1b  (1b analysis dataset)
*	Other output:	None
*
********************************************************************************
*	Purpose:		This do-file creates additional variables required for the 
*					tabulation of objective 1b
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
	cap log using "$outdir/cr_dataset_1b.txt", replace t

*import dataset from 1a
	import delimited "$outdir/cr_dataset_1a.csv", clear	

*noi di "CONVERT DATES TO STATA DATES" 
sum
foreach var of varlist covid_vax first_positive_test_date  {
gen `var'date=date(`var', "DMY")
	drop `var'
	rename `var'date `var'
	format `var' %td
}
	
	
*categorise additional variables required for objective 1b (calendar time of positive test)
	display d(23March2020)
		*21997
	display d(31May2020)
		*22066
	display d(07September2020)
		*22165
	display d(24April2021)
		*22394
	display d(28May2021)
		*22428
	display d(14December2021)
		*22628
	
	gen wave_test=.
	*wave 1, 23rd March to 30 May 2020
	replace wave_test=0 if first_positive_test_date>=21997 & first_positive_test_date<22066
	*easing 1, 31 May to 6th September
	replace wave_test=1 if first_positive_test_date>=22066 & first_positive_test_date<22165
	*wave 2, 7 sempterber 2020 to 23 April 2021
	replace wave_test=2 if first_positive_test_date>=22165 & first_positive_test_date<22394
	*easing 2 24 April to 28 May 2021
	replace wave_test=3 if first_positive_test_date>=22394 & first_positive_test_date<22428
	*wave 3 28 May to 14 December 2021
	replace wave_test=4 if first_positive_test_date>=22428 & first_positive_test_date<22628
	*easing 3
	replace wave_test=5 if first_positive_test_date>=22628 & first_positive_test_date!=.
	
	
	
	export delimited using "$outdir/cr_dataset_1b.csv", replace	
	
	
	
	
	
	
	