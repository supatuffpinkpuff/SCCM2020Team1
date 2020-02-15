# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 2020

@author: Kirby
"""
# This code yields a list of patientunitstayIDs that:
# had acute neuro diagnoses we care about.
# are adults (18 and older)
# had a hospital, unit number, and year with good I/O documentation. 
# were the first ICU stay for that patient. 

import numpy as np
import pandas as pd
        
# get diagnosis info
diag = pd.read_csv(r"C:\Users\Kirby\OneDrive\JHU\Precision Care Medicine\eicu\diagnosis.csv")
#pull list of diagnosis strings to search for
neuroStrings = pd.read_csv(r"C:\Users\Kirby\OneDrive\JHU\SCCM Datathon\NeuroDiagnosisStrings.csv")

# only keep stayIDs with the relevant diagnoses
neuroDiag = diag[diag['diagnosisstring'].isin(neuroStrings['DiagnosisStrings'])]
neuroDiag = neuroDiag[['patientunitstayid','diagnosisstring']]

# only keep StayIDs with that are originally part of our data set. 
StayIDs = pd.read_csv(r"C:\Users\Kirby\OneDrive\JHU\SCCM Datathon\FinalPatientStayIDs.csv")
neuroDiag = neuroDiag[neuroDiag['patientunitstayid'].isin(StayIDs['patientunitstayid'])]

# Get dataframe of each group of diagnoses
VascStays = neuroDiag[neuroDiag['diagnosisstring'].str.contains('disorders of vasculature')]
PostSurgStays = neuroDiag[neuroDiag['diagnosisstring'].str.contains('post-neurosurgery')]
TraumaStays = neuroDiag[neuroDiag['diagnosisstring'].str.contains('trauma - CNS')]

# Drop all the diagnosis strings
VascStays = VascStays.drop(columns=['diagnosisstring'])
PostSurgStays = PostSurgStays.drop(columns=['diagnosisstring'])
TraumaStays = TraumaStays.drop(columns=['diagnosisstring'])

# drop all the duplicates
VascStays = VascStays.drop_duplicates()
PostSurgStays = PostSurgStays.drop_duplicates()
TraumaStays = TraumaStays.drop_duplicates()

# Get one table with labels for each group
StayIDs['vascularDisorders'] = StayIDs['patientunitstayid'].isin(VascStays['patientunitstayid'])
StayIDs['postSurgery'] = StayIDs['patientunitstayid'].isin(PostSurgStays['patientunitstayid'])
StayIDs['Trauma'] = StayIDs['patientunitstayid'].isin(TraumaStays['patientunitstayid'])

# get overlap between the diagnosis groups
VascAndSurgStays = VascStays[VascStays['patientunitstayid'].isin(PostSurgStays['patientunitstayid'])]
VascAndTraumaStays = VascStays[VascStays['patientunitstayid'].isin(TraumaStays['patientunitstayid'])]
PostAndTraumaStays = PostSurgStays[PostSurgStays['patientunitstayid'].isin(TraumaStays['patientunitstayid'])]
VascPostAndTraumaStays = VascAndSurgStays[VascAndSurgStays['patientunitstayid'].isin(PostAndTraumaStays['patientunitstayid'])]

# save off results.
StayIDs.to_csv(r"C:\Users\Kirby\OneDrive\JHU\SCCM Datathon\FinalPatientStayIDsWithGroups.csv",index = False)
VascStays.to_csv(r"C:\Users\Kirby\OneDrive\JHU\SCCM Datathon\VascStayIDs.csv",index = False)
PostSurgStays.to_csv(r"C:\Users\Kirby\OneDrive\JHU\SCCM Datathon\PostSurgStayIDs.csv",index = False)
TraumaStays.to_csv(r"C:\Users\Kirby\OneDrive\JHU\SCCM Datathon\TraumaStayIDs.csv",index = False)
VascAndSurgStays.to_csv(r"C:\Users\Kirby\OneDrive\JHU\SCCM Datathon\VascAndSurgStayIDs.csv",index = False)
VascAndTraumaStays.to_csv(r"C:\Users\Kirby\OneDrive\JHU\SCCM Datathon\VascAndTraumaStayIDs.csv",index = False)
PostAndTraumaStays.to_csv(r"C:\Users\Kirby\OneDrive\JHU\SCCM Datathon\PostAndTraumaStayIDs.csv",index = False)
VascPostAndTraumaStays.to_csv(r"C:\Users\Kirby\OneDrive\JHU\SCCM Datathon\VascPostAndTraumaStayIDs.csv",index = False)