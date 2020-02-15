# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 11:38:30 2020

@author: Kirby
"""
# This will pull desired lab results for relevant patients, within the first week

import numpy as np
import pandas as pd

#the lab to pull for, must match the exact string used in the lab table as labname.
labName = 'Hgb'

# Pull list of relevant IDs
StayIDs = pd.read_csv(r"C:\Users\Kirby\OneDrive\JHU\SCCM Datathon\FirstNeuroAdultReliablePatientStayIDs.csv")

labs = pd.read_csv(r"C:\Users\Kirby\OneDrive\JHU\Precision Care Medicine\eicu\lab.csv")

# filter out labs that aren't on relevant StayIDs
IDList = StayIDs.values.astype(str).tolist()
IDList = [item for sublist in IDList for item in sublist]
labs = labs[labs['patientunitstayid'].isin(IDList)]

# only keep columns we care about
labs = labs[['patientunitstayid','labresultoffset','labname','labresult']]

# only keep labs we care about (Hgb,Hct,platelets x 1000,WBC x 1000,RBC)
labs = labs[labs['labname'].str.contains(labName)]

# filter out labs from after the first week
labs = labs[labs['labresultoffset'] <= 4320]
labs = labs[labs['labresultoffset'] >= -1440]

labs = labs.sort_values(by = ['patientunitstayid','labresultoffset'])

filepath = 'C:\\Users\\Kirby\\OneDrive\\JHU\\SCCM Datathon\\' + labName + 'data.csv'

labs.to_csv(filepath,index = False)

labStayIDs = labs[['patientunitstayid']]
labStayIDs = labStayIDs.drop_duplicates()

filepath = 'C:\\Users\\Kirby\\OneDrive\\JHU\\SCCM Datathon\\' + labName + 'IDs.csv'
labStayIDs.to_csv(filepath,index = False)