# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 16:26:18 2020

@author: Kirby
"""

#Verifying age

import numpy as np
import pandas as pd

# Pull list of relevant IDs
StayIDs = pd.read_csv(r"C:\Users\Kirby\OneDrive\JHU\SCCM Datathon\FinalPatientStayIDs.csv")
patient = pd.read_csv(r"C:\Users\Kirby\OneDrive\JHU\Precision Care Medicine\eicu\patient.csv")

patient = patient[patient['patientunitstayid'].isin(StayIDs['patientunitstayid'])]