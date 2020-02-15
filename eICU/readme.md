The code in this folder was written at the SCCM 2020 Datathon, by Team 1. 

We investigated the effects of blood transfusions on neurological patients with anemia. 

Members: 
Dragos Galusca
Donna Lee Armaignac
J. Steven Hata
Steve Kelleher
Sicheng Hao
Qiheng Zhao
Kirby Gong
Jamie Lynn Sturgill

Python code generally pulls from hardcoded file paths on Kirby's computer, which should be changed if run elsewhere.
Sicheng wrote the R code, which handles modelling. He'll add to this later.

The first step was to get our patient dataset. 
Our clinicians first defined a list of diagnoses that would be considered neurological. The list of diagnoses strings can be found in NeuroDiagnosisStrings.csv

GeneratingDatasetPatientUnitStayIDs.py uses that list to only keep patient stay IDs that:
- had one of those neurological diagnoses
- were at least 18 years of age
- were in a hospital, ward, and year that was considered to have good I/O documentation (per ReliableHospitalICUYearFilterForSentryAlert.csv)
- were the patient's first ICU admission

Then HemoglobinCheck.py takes that output, and pulls all hemoglobin lab values between -24 and +72 hours for those patients. If a patient unit stay doesn't have any, it drops them. 

APACHEInfo.py further filters out patient stays that did not have APACHE data, which was used for severity adjustment later. 

From there, GCSfeature.py,VasopressorsFeature.py,TroponinFeature.py,and SplittingPatientIDsbyDiagnosisGroups.py all pulled more features. File names are pretty much self-explanatory. 

Sicheng and Qiheng wrote the analysis code. 

R was used to compare outcomes from APACHE like mortality, across patient groups with differing levels of hemoglobin and differing amounts of blood administrations. Outcomes were adjusted for vasopressor use and APACHE scores. 


MIOutcome.py and AKIOutcome.py was used to generate features for those complications, given time constraints were not used. 







