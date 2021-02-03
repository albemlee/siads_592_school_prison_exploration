# Education Justice Exploration

# Data
The data used to run the notebooks in this repository are located in `data/`.

### Incarceration Trends ([Source](https://github.com/vera-institute/incarceration-trends)), `data/incarcerationtrends`
The Incarceration Trends Dataset was compiled by the Vera Institute.  The dataset was compiled by collecting information from the National Corrections Reporting Program (NCRP), Deaths in Custody Reporting Program: Jail Populations (DCRP), the Annual Survey of Jails (ASJ), and the Census of Jails (COJ).  It contains data for prisons and jails, by county level, such as race/ethnicity, gender, and age.  It contains county- and jurisdiction-level jail data for 1970-2018 and county-level prison data for 1983-2016.

### Common Core of Data ([Source API](https://educationdata.urban.org/api/v1)), `from helper import EducationData_API`
The Common Core of Data is collected by the National Center for Education Statistics (NCES). It contains data for specific schools, school districts, and states including enrollment, revenue and expenditures, and geographic location. The data is a large dataset, for example, the 2016 finance dataset contains 18,680 rows (for each school district) and 133 columns.

### Civil Rights Data Collection ([Source API](https://educationdata.urban.org/api/v1)), `from helper import EducationData_API`
The CRDC contains data on civil rights indicators related to access and barriers to educational opportunity at early childhood through grade 12.  This dataset contains data for the 2017-2018 school year only.

### State and Local Government Expenditures on Police Protection in the U.S. 2000-2017 ([Source](https://www.bjs.gov/index.cfm?ty=pbdetail&iid=6927)), `data/slgeppus0017`
The State and Local Government Expenditures on Police Protection in the U.S. (SLGEPPUS) contains data on state and local government expenditures on police protection, which includes the cost of running the jails and prisons.  It provides a total expenditure amount and is not broken down into the specific police protection functions, therefore we may still search for additional datasets specific to incarceration expenditures (time permitting).  The expenditures are provided in inflation-adjusted and not inflation-adjusted values.  

### State-by-State Spending on Kids ([Source](https://datacatalog.urban.org/dataset/state-state-spending-kids-dataset)), `data/statebystatespending`
The State-by-State Spending on Kids dataset provides the amount of public spending on children from 1997-2016.  It was created by the Urban Institute and compiled data from the Census Bureau’s Survey of State and Local Government Finances and other federal and non-census sources.  The key variables that will be used in our analysis include the expenditure data on elementary and secondary education, subsidies, special services, and the Head Start program. 

### Property Tax Rates ([Source](https://www.lincolninst.edu/research-data/data-toolkits/significant-features-property-tax/access-property-tax-database/property-tax-rates)), `data/PropertyTaxDF.csv`
The Property Tax Rates dataset provides data on property taxes for all 50 states as well as the District of Columbia.  The dataset was developed by the Lincoln Institute of Land Policy and the George Washington Institute of Public Policy.

# Notebooks

### 01_gather_education_data
This notebook contains code used to access the education data portal API and extract data related to school finance and discipline.

### 02_statebystate_wrangling
This notebook contains code used to convert the original Excel document with state by state spending data to csv files.

### 03_education_wrangling
This notebook contains code used to merge finance data from Common Core of Data, discipline data from the Civil Rights Data Collection, and the Incarceration Trends from the Vera Institute.

### 04_incarceration_trends
This notebook contains the visual exploration of the Inceration Trends data from the Vera Institute.

### 05_police_vs_education_spending
This notebook contains a comparison of police spending and education spending.

### 06_state_local_police_expenditures
This notebook contains a comparison of state and local expenditures on police protetions

### 07_state_spending
This notebook contains a visual exploration of each state's education spending

### 08_map_generator
This notebook contains the code used to generate maps

### 09_pca
This notebook contains PCA analysis which was used to determine most important variables in the Common Core of Data Finance dataset.

### 10_correlations
This notebook contains correlations analysis between incarceration rates and education data.