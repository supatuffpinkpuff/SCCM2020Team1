# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 20:06:18 2020

@author: Kirby
"""

import numpy as np
import pandas as pd


# get infusion drug info
infu = pd.read_csv(r"C:\Users\Kirby\OneDrive\JHU\Precision Care Medicine\eicu\infusiondrug.csv",dtype={'infusiondrugid':int,'patientunitstayid':int,'infusionoffset':int,'drugname':str,'drugrate':str,'infusionrate':str,'drugamount':str,'volumeoffluid':str,'patientweight':str})

#remove columns I don't care about.
infu = infu.drop(columns=['infusiondrugid','drugrate','infusionrate','drugamount','volumeoffluid','patientweight'])

# Get medication table info
med = pd.read_csv(r"C:\Users\Kirby\OneDrive\JHU\Precision Care Medicine\eicu\medication.csv",dtype={'medicationid':int,'patientunitstayid':int,'drugorderoffset':int,'drugstartoffset':int,'drugivadmixture':str,'drugordercancelled':str,'drugname':str,'drughiclseqno':float,'dosage':str,'routeadmin':str,'frequency':str,'loadingdose':str,'prn':str,'drugstopoffset':int,'gtc':int})
# remove cancelled orders
med = med[med['drugordercancelled']=='No']
#remove columns I don't care about.
med = med.drop(columns=['medicationid','drugorderoffset','drugivadmixture','drugordercancelled','dosage','routeadmin','frequency','loadingdose','prn','gtc'])

# Get Treatment table info
treat = pd.read_csv(r"C:\Users\Kirby\OneDrive\JHU\Precision Care Medicine\eicu\treatment.csv")
treat = treat.drop(columns=['treatmentid','activeupondischarge'])

# only keep rows with the complete list of data ids
comp = pd.read_csv(r"C:\Users\Kirby\OneDrive\JHU\SCCM Datathon\FinalPatientStayIDs.csv")
compInfu = infu[infu['patientunitstayid'].isin(comp['patientunitstayid'])]
compMed = med[med['patientunitstayid'].isin(comp['patientunitstayid'])]
compTreat = treat[treat['patientunitstayid'].isin(comp['patientunitstayid'])]

# only keep rows with relevant drugs

# import lists of drug names to search for, and make it all lowercase
# change this part to get different drug features
drug=pd.read_csv(r"C:\Users\Kirby\OneDrive\JHU\Precision Care Medicine\Medications\DrugNameLists\Vasopressors.csv")
drug = drug.applymap(lambda s:s.lower() if type(s) == str else s)
druglist = drug.values.astype(str).tolist()
druglist = [item.lower() for sublist in druglist for item in sublist]


# this csv was generated using Create HICL Drug Name Legend.py
hicl = pd.read_csv(r"C:\Users\Kirby\OneDrive\JHU\Precision Care Medicine\HICLlegend.csv")
# make it all lowercase
hicl = hicl.applymap(lambda s:s.lower() if type(s) == str else s)
# pull relevant HICL codes
hicl = hicl[hicl['drugname'].str.contains('|'.join(druglist))]
hicl = hicl.drop(columns=['drugname'])
hicl = hicl.drop_duplicates()
hicllist = hicl.values.astype(float).tolist()

# keep the rows from medication with relevant drugs. 
compMed = compMed.applymap(lambda s:s.lower() if type(s) == str else s)
drugMed = compMed[compMed['drugname'].str.contains('|'.join(druglist),na=False)]
hiclMed = compMed[compMed['drughiclseqno'].isin(hicllist)]
compMed = pd.concat([drugMed,hiclMed])
compMed = compMed.drop_duplicates()

# keep the rows from infusion with relevant drugs. 
compInfu = compInfu.applymap(lambda s:s.lower() if type(s) == str else s)
compInfu = compInfu[compInfu['drugname'].str.contains('|'.join(druglist),na=False)]
compInfu['drugstopoffset']=np.nan
compInfu['drughiclseqno']=np.nan
compInfu = compInfu.rename(columns={'infusionoffset':'drugstartoffset'})

# keep the rows from treatment with relevant drugs. 
# pull list of strings to search treatment with. 
treatStrings = pd.read_csv(r"C:\Users\Kirby\OneDrive\JHU\Precision Care Medicine\Medications\TreatmentStrings\VasopressorsTreatment.csv")
treatStrings = treatStrings.applymap(lambda s:s.lower() if type(s) == str else s)
treatStringsList = treatStrings.values.astype(str).tolist()
treatStringsList = [item.lower() for sublist in treatStringsList for item in sublist]

compTreat = compTreat.applymap(lambda s:s.lower() if type(s) == str else s)
compTreat = compTreat[compTreat['treatmentstring'].str.contains('|'.join(treatStringsList),na=False)]
compTreat['drugstopoffset']=np.nan
compTreat['drughiclseqno']=np.nan
compTreat = compTreat.rename(columns={'treatmentoffset':'drugstartoffset','treatmentstring':'drugname'})

# combine the treatment, medication, and infusion info together
compFeat = pd.concat([compMed,compInfu,compTreat],sort=False)
compFeat = compFeat.sort_values(by=['patientunitstayid','drugstartoffset','drugstopoffset'])
compFeat = compFeat[['patientunitstayid','drugstartoffset','drugstopoffset','drugname','drughiclseqno']]

# Filter by drug start offset, must be with in -1440, 4320
compFeat = compFeat[compFeat['drugstartoffset'] <= 4320]
compFeat = compFeat[compFeat['drugstartoffset'] >= -1440]

# Just get Stay IDs with the medication
compFeat = compFeat[['patientunitstayid']]
compFeat = compFeat.drop_duplicates()

# Add a row to comp with a 1 or 0 for if they had a vasopressor
comp['Vasopressor'] = comp['patientunitstayid'].isin(compFeat['patientunitstayid'])

comp.to_csv(r"C:\Users\Kirby\OneDrive\JHU\SCCM Datathon\VasopressorsData.csv",index = False)



