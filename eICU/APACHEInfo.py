# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 14:33:34 2020

@author: Kirby
"""
import numpy as np
import pandas as pd

# get apache data, and the number of patient stays that have complete apache data. 

# Pull list of relevant IDs
StayIDs = pd.read_csv(r"C:\Users\Kirby\OneDrive\JHU\SCCM Datathon\FirstNeuroAdultReliableHgbStayIDs.csv")

apache = pd.read_csv(r"C:\Users\Kirby\OneDrive\JHU\Precision Care Medicine\eicu\apachepatientresult.csv")

#only keep APACHE rows with a list of IDs we care about.
apache = apache[apache['patientunitstayid'].isin(StayIDs['patientunitstayid'])]

# only keep apache columns we care about, APS, apache, predicted mortalities, predicted LOSs, ventilator,vent days
apache = apache.drop(columns=['apachepatientresultsid','physicianspeciality','physicianinterventioncategory','preopmi','preopcardiaccath','ptcawithin24h'])

# only keep apache version IV
apache = apache[apache['apacheversion']=='IVa']
apache.to_csv(r"C:\Users\Kirby\OneDrive\JHU\SCCM Datathon\ApacheData.csv",index=False)

# generate list of IDs with them
IDs = apache[['patientunitstayid']]
IDs = IDs.drop_duplicates()
IDs.to_csv(r"C:\Users\Kirby\OneDrive\JHU\SCCM Datathon\FinalPatientStayIDs.csv",index=False)

# final cohort is 4768 patient stays. These patient stays:
# had acute neuro diagnoses we care about.
# are adults (18 and older)
# had a hospital, unit number, and year with good I/O documentation. 
# were the first ICU stay for that patient. 
# had hemoglobin between -24 to 72 hour of ICU admission
# has apache results
