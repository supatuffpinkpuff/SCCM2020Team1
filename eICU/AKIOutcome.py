# -*- coding: utf-8 -*-
"""
Created on Sat Feb 15 11:09:14 2020

@author: Kirby
"""

# This will pull AKI outcomes, by looking at tropinin labs and MI diagnoses. 

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

# only keep creatinine
labs = labs[labs['labname'].isin(['creatinine'])]

# find AKI (greater than 0.3 mg/dL rise from baseline)
# get the baseline as the first creatinine result
labresults = labs.sort_values(['patientunitstayid','labresultoffset'])
labresults = labs[['patientunitstayid','labresult']]
cr_first = labresults.groupby(['patientunitstayid']).first()

# make dictionary out of cr_first
crDict = cr_first.to_dict()
crDict = crDict['labresult']

# find AKI (greater than 0.3 mg/dL rise from the baseline)
for row in labs.itertuples(index=True):
    index = row[0]
    currentID = row[1]
    result = row[4]
    labs.loc[index,'AKI'] = (result - crDict.get(currentID)) > 0.3 

# keep columns we want
labs = labs[['patientunitstayid','labresultoffset','AKI']]

labs.to_csv(r"C:\Users\Kirby\OneDrive\JHU\SCCM Datathon\AKIoutcome.csv",index = False)