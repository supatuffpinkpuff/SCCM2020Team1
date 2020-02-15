# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 11:38:30 2020

@author: Kirby
"""
# This will pull MI outcomes, by looking at tropinin labs and MI diagnoses. 

import numpy as np
import pandas as pd


# Pull list of relevant IDs
StayIDs = pd.read_csv(r"C:\Users\Kirby\OneDrive\JHU\SCCM Datathon\FinalPatientStayIDs.csv")

# Checking troponin
labs = pd.read_csv(r"C:\Users\Kirby\OneDrive\JHU\Precision Care Medicine\eicu\lab.csv",dtype={'labresult':float})

# filter out labs that aren't on relevant StayIDs
labs = labs[labs['patientunitstayid'].isin(StayIDs['patientunitstayid'])]

# only keep columns we care about
labs = labs[['patientunitstayid','labresultoffset','labname','labresult']]

# only keep troponin
labs = labs[labs['labname'].str.contains('troponin')]

# filter out troponin > 0.04 
labs = labs[((labs['labresult'] > 0.10) & (labs['labname'] == 'troponin - I')) | ((labs['labresult'] > 0.04) & (labs['labname'] == 'troponin - T'))]

# keep columns we want
labs = labs[['patientunitstayid','labresultoffset','labname']]

# rename columns
labs = labs.rename(columns = {'labresultoffset':'diagnosisoffset','labname':'diagnosisstring'})

# pull diagnoses list
diag = pd.read_csv(r"C:\Users\Kirby\OneDrive\JHU\Precision Care Medicine\eicu\diagnosis.csv")

# keep rows with our patient stays
diag = diag[diag['patientunitstayid'].isin(StayIDs['patientunitstayid'])]

# keep rows with MI
diag = diag[diag['diagnosisstring'].str.contains('myocardial infarction')]

# keep columns we care about
diag = diag[['patientunitstayid','diagnosisoffset','diagnosisstring']]

# Combine the labs and diagnosis indicators for MI
MyoInfarc = pd.concat(objs=[diag,labs],ignore_index = True,sort=True)
# reordering columns
MyoInfarc = MyoInfarc[['patientunitstayid','diagnosisoffset','diagnosisstring']]

# sort all values by time
MyoInfarc = MyoInfarc.sort_values(by = ['patientunitstayid','diagnosisoffset'])

#save off data
MyoInfarc.to_csv(r"C:\Users\Kirby\OneDrive\JHU\SCCM Datathon\MIoutcome.csv",index = False)
