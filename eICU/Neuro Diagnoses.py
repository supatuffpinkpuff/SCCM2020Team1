# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 2020

@author: Kirby
"""
# This code yields a list of patientunitstayIDs that:
# had acute neuro diagnoses we care about.
# are adults (18 and older)


import numpy as np
import pandas as pd
        
# get diagnosis info
diag = pd.read_csv(r"C:\Users\Kirby\OneDrive\JHU\Precision Care Medicine\eicu\diagnosis.csv")
#pull list of diagnosis strings to search for
neuroStrings = pd.read_csv(r"C:\Users\Kirby\OneDrive\JHU\SCCM Datathon\NeuroDiagnosisStrings.csv")

#convert neuroStrings to a list
neuroStringsList = neuroStrings.values.astype(str).tolist()
neuroStringsList = [item for sublist in neuroStringsList for item in sublist]
neuroDiag  = diag[diag['diagnosisstring'].isin(neuroStringsList)]
neuroDiag = neuroDiag.drop(columns = ['diagnosisid','activeupondischarge','diagnosisoffset','diagnosisstring','icd9code','diagnosispriority'])
neuroDiag = neuroDiag.drop_duplicates()

# Remove pediatric cases
pat = pd.read_csv(r"C:\Users\Kirby\OneDrive\JHU\Precision Care Medicine\eicu\patient.csv")
pat = pat[['patientunitstayid','age']]
# convert age to numeric, and get nans for non numbers
pat['age'] = pd.to_numeric(pat['age'], errors='coerce')
# make nans 90
pat.fillna(90)
# only keep the adults
pat = pat[pat['age'] >= 18]
#get a list of adult's patient unit stay ids
pat = pat.drop(columns = ['age'])
patAdultsList = pat.values.astype(str).tolist()
patAdultsList = [item for sublist in patAdultsList for item in sublist]

# filters neuroDiag further by the adults list. 
neuroDiag = neuroDiag[neuroDiag['patientunitstayid'].isin(patAdultsList)]

neuroDiag.to_csv(r"C:\Users\Kirby\OneDrive\JHU\SCCM Datathon\NeuroDiagnosisPatientStayIDs.csv",index=False)

