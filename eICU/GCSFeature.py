# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 15:57:53 2020

@author: Kirby
"""
#get the worst GCS score in the first 24 hours from the apache variables

import numpy as np
import pandas as pd

# Pull list of relevant IDs
StayIDs = pd.read_csv(r"C:\Users\Kirby\OneDrive\JHU\SCCM Datathon\FinalPatientStayIDs.csv")

predvar = pd.read_csv(r"C:\Users\Kirby\OneDrive\JHU\Precision Care Medicine\eicu\apachepredvar.csv")

#only keep rows we care about
predvar = predvar[predvar['patientunitstayid'].isin(StayIDs['patientunitstayid'])]

# only keep columns we care about
predvar = predvar[['patientunitstayid','verbal','motor','eyes']]

predvar.to_csv(r"C:\Users\Kirby\OneDrive\JHU\SCCM Datathon\GCSdata.csv")


