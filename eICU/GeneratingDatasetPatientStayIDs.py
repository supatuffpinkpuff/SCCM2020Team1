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

#convert neuroStrings to a list
neuroStringsList = neuroStrings.values.astype(str).tolist()
neuroStringsList = [item for sublist in neuroStringsList for item in sublist]
neuroDiag  = diag[diag['diagnosisstring'].isin(neuroStringsList)]
neuroDiag = neuroDiag.drop(columns = ['diagnosisid','activeupondischarge','diagnosisoffset','diagnosisstring','icd9code','diagnosispriority'])
neuroDiag = neuroDiag.drop_duplicates()

# get any patient related info
pat = pd.read_csv(r"C:\Users\Kirby\OneDrive\JHU\Precision Care Medicine\eicu\patient.csv")
pat = pat[['patientunitstayid','age','hospitalid','wardid','hospitaldischargeyear','unitvisitnumber']]
# Remove pediatric cases
# convert age to numeric, and get nans for non numbers
pat['age'] = pd.to_numeric(pat['age'], errors='coerce')
# make nans 90
pat.fillna(90)
# only keep the adults
pat = pat[pat['age'] >= 18]
# no longer need age info
pat = pat.drop(columns = ['age'])

# Filtering out by whether they had good I/O documentation.
goodDoc = pd.read_csv(r"C:\Users\Kirby\OneDrive\JHU\SCCM Datathon\ReliableHospitalICUYearFilterForSentryAlert.csv")
pat = pat[pat['hospitalid'].isin(goodDoc['HospitalID']) & pat['wardid'].isin(goodDoc['ICUID']) & pat['hospitaldischargeyear'].isin(goodDoc['UnitAdmitYear'])]
pat = pat.drop(columns = ['hospitalid','wardid','hospitaldischargeyear'])

# Only keeping each patient's first ICU Stay
pat = pat[pat['unitvisitnumber']==1]
pat = pat.drop(columns = ['unitvisitnumber'])

patList = pat.values.astype(str).tolist()
patList = [item for sublist in patList for item in sublist]

# filters neuroDiag further by the patient info filters 
neuroDiag = neuroDiag[neuroDiag['patientunitstayid'].isin(patList)]

neuroDiag.to_csv(r"C:\Users\Kirby\OneDrive\JHU\SCCM Datathon\FirstNeuroAdultReliablePatientStayIDs.csv",index=False)

