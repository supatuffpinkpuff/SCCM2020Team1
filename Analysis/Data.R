

library(data.table)
library(dplyr)
library(ggplot2)
library(gdata)
library(readxl)
library(pROC)
library(geepack)

'%!in%' <- function(x,y)!('%in%'(x,y))

# eICU Derived data sets
setwd("/Users/sichenghao/Documents/GitHub/SCCM2020Team1/eICU/")
#csv<-list.files(pattern="*.csv")
cohort<-fread("FinalPatientStayIDsWithGroups.csv")
vaso<-fread("VasopressorsData.csv")
gcs<-fread("GCSdata.csv")
aki<-fread("AKIoutcome.csv")
hgb<-fread("Hgbdata.csv")
mi<-fread("MIoutcome.csv")
lct<-fread("AllLacate.csv")

#eICU
setwd("/Users/sichenghao/Desktop/eICU/")#set to local eICU database

all.csv<-list.files(pattern="*.csv")
patient<-fread(all.csv[25])
apache<-fread(all.csv[5])
apache<-apache%>%filter(apache$apacheversion=="IV")

cohort<-left_join(cohort,patient)#join with patient
cohort<-left_join(cohort,apache)#join with apache
rm(apache)
rm(patient)

#Overlook
table(cohort$actualhospitalmortality)
table(cohort$actualicumortality)
length(unique(cohort$patientunitstayid))/nrow(cohort)



#Demographic
table(cohort$gender)/nrow(cohort)
table(cohort$ethnicity)/nrow(cohort)
table(cohort$unitadmitsource)
cohort$age<-as.numeric(cohort$age)
cohort$age.group<-ifelse(cohort$age > 89," >89 ",
                         ifelse(cohort$age > 65, " 65-89",
                                ifelse(cohort$age > 45, " 45-65","18-45")))



cohort.stroke<-cohort%>%filter(vascularDisorders==T)
stroke.id<-cohort.stroke$patientunitstayid


# Adding features

#vaso

cohort<-left_join(cohort,vaso)


#GCS
#Todo GCS with time stemp
gcs<-gcs[,2:5]
gcs$verbal[gcs$verbal==-1]=NA
gcs$motor[gcs$motor==-1]=NA
gcs$eyes[gcs$eye==-1]=NA
gcs$gcs<-gcs$verbal+gcs$motor+gcs$eyes
head(gcs$gcs)

cohort<-left_join(cohort,gcs)
cohort.id<-cohort$patientunitstayid



#AKIoutcome.csv
aki<-aki%>%group_by(patientunitstayid)%>%summarise(is.aki=sum(AKI)>0)
cohort<-left_join(cohort,aki)

#MI
cohort$is.mi<-cohort$patientunitstayid%in%mi$patientunitstayid


#IntakeOutput table
ino<-fread(all.csv[16])
ino<-ino%>%filter(patientunitstayid%in%cohort.id)
ino$celllabel<-tolower(ino$celllabel)


#Bleeding and bloodloss (exclude)

#Careplan
CP<-fread(all.csv[9])#careplan general
CP$cplitemvalue<-tolower(CP$cplitemvalue)
bleeding<-CP[grep("bleed",CP$cplitemvalue),]
bleeding<-bleeding%>%filter(patientunitstayid%in%cohort.id)
bleeding.id<-unique(bleeding$patientunitstayid)

#IntakeOutput
bloodloss<-ino%>%filter(celllabel=="blood loss")
bloodloss.id<-unique(bloodloss$patientunitstayid)
length(bleeding.id)
length(bloodloss.id)-sum(bloodloss.id%in%bleeding.id)
#124 patient developed blood loss but not in bleeding group(careplan_general)


#########Exclude Bleeding and Blood Loss patients###########

cohort.new<-cohort%>%filter(patientunitstayid%!in%bloodloss.id & patientunitstayid%!in%bleeding.id)

# #Infusiondrug
# infusion<-fread(all.csv[15])
# infusion<-infusion%>%filter(patientunitstayid%in%cohort.id)


#Extract blood transfusion from intakeoutput
blood<-rbind(ino[grep("rbc",ino$celllabel),],
             ino[grep("sn total blood",ino$celllabel),])

length(unique(blood$patientunitstayid))


#Treatment table
treat<-fread(all.csv[29])
treat<-treat%>%filter(patientunitstayid%in%cohort.id)
treat$treatmentstring<-tolower(treat$treatmentstring)
#str1<-unique(blood3$treatmentstring)
#str3<-str2[-which(str2%in%str1)]
blood2<-rbind(treat[grep("packed rbc",treat$treatmentstring),],
              treat[grep("prbc",treat$treatmentstring),],
              treat[grep("packed red",treat$treatmentstring),])

length(unique(blood2$patientunitstayid))


# blood4<-rbind(treat[grep("packed rbc",treat$treatmentstring),],
#               treat[grep("prbc",treat$treatmentstring),],
#               treat[grep("packed red",treat$treatmentstring),],
#               treat[grep("blood",treat$treatmentstring),])#do not include "blood"

# str1<-unique(blood3$treatmentstring)
# str2<-unique(blood4$treatmentstring)
# str3<-str2[-which(str2%in%str1)]

cohort.new$transfusion<-ifelse(cohort.new$patientunitstayid%in%blood$patientunitstayid |
                             cohort.new$patientunitstayid%in%blood2$patientunitstayid,1,0)
table(cohort.new$transfusion)
transfusion.id<-cohort.new%>%filter(transfusion==1)%>%select(patientunitstayid)

blood<-blood%>%filter(patientunitstayid%in%transfusion.id$patientunitstayid)


blood2<-blood2%>%filter(patientunitstayid%in%transfusion.id$patientunitstayid)


########TODO: Transfusion Volume########



#Create a table contains both transfution and hgb measurement data

table<-NULL
for(i in 1:length(blood.id)){
  transfusion.temp<-blood%>%
    filter(patientunitstayid==blood.id[i])%>%
    transmute(patientunitstayid,offset = intakeoutputoffset,intaketotal,outputtotal,dialysistotal,nettotal,celllabel)
  transfusion.temp$hgb = NA
  
  hgb.temp<-hgb%>%
    filter(patientunitstayid==blood.id[i])%>%
    transmute(patientunitstayid,offset = labresultoffset,hgb = labresult)
  hgb.temp$intaketotal = NA
  hgb.temp$outputtotal = NA
  hgb.temp$dialysistotal = NA
  hgb.temp$nettotal = NA
  hgb.temp$celllabel = NA
  
  
  temp<-rbind(transfusion.temp,hgb.temp)
  temp<-temp[order(temp$offset),]
  table<-rbind(table,temp)
}



transfusion<-NULL
for(i in 1:length(blood.id)){
  temp<-blood%>%filter(patientunitstayid==blood.id[i])
  temp<-temp[order(temp$intakeoutputoffset,decreasing = F),]
  start.offset<-temp$intakeoutputoffset[1]
  end.offset<-temp$intakeoutputoffset[nrow(temp)]
  transfusion.vol<-sum(temp$intaketotal)
  transfusion<-rbind(transfusion,
                     data.frame(start.offset,end.offset,transfusion.vol,
                                patientunitstayid=temp$patientunitstayid[1]))
}


cohort<-left_join(cohort,transfusion)
cohort$transfusion.vol[cohort$transfusion==0]=0
cohort$transfusion.group<-ifelse(cohort$transfusion.vol<250,"low",
                            ifelse(cohort$transfusion.vol<500,"mid","high"))
cohort$transfusion.group[cohort$transfusion==0]=NA


#Hgb
cohort.id<-cohort$patientunitstayid
length(unique(hgb$patientunitstayid))

hgb.min<-NULL
for(i in 1:length(cohort.id)){
  temp<-hgb%>%filter(patientunitstayid==cohort.id[i])
  if(cohort$transfusion[i]==0|is.na(cohort$start.offset[i])){
    hgb.min[i]<-min(temp$labresult)
  } else {
    temp<-hgb%>%filter(patientunitstayid==cohort.id[i])
    temp<-temp%>%filter(labresultoffset<cohort$start.offset[i])
    hgb.min[i]<-min(temp$labresult)
  }
  
}

sum(is.infinite(hgb.min))
range(hgb.min)
cohort$hgb<-hgb.min
cohort$hgb.group<-ifelse(cohort$hgb<7,"low",
                         ifelse(cohort$hgb>9,"high","mid"))


cohort$vent<-ifelse(is.na(cohort$actualventdays),0,1)
#Data Output
setwd("/Users/sichenghao/Documents/GitHub/SCCM2020Team1/Analysis/")
fwrite(cohort,"data.csv")
fwrite(table,"transfusion&hgb.csv")

#lct
lct<-lct%>%filter(labresultoffset>-360)
length(unique(lct$patientunitstayid))








hgb$afterAD<-ifelse(hgb$labresultoffset>0,T,F)
length(unique(hgb$patientunitstayid))
hgb.afterAD<-hgb%>%filter(afterAD == T)
length(unique(hgb.afterAD$patientunitstayid))
hgb.min<-hgb.afterAD%>%group_by(patientunitstayid)%>%
  summarise(hgbmin = min(labresult),hgbfirst = min(labresultoffset),hgbmax = max(labresult))
hgb.afterAD<-left_join(hgb.afterAD,hgb.min)
hgb.afterAD<-hgb.afterAD%>%mutate(is.first=labresultoffset==hgbfirst,is.min=labresult==hgbmin)
min.hgb.afterAD<-hgb.afterAD%>%filter(is.min==T)
table(min.hgb.afterAD$is.first)
min.hgb.afterAD.stroke<-min.hgb.afterAD%>%filter(patientunitstayid%in%stroke.id)
table(min.hgb.afterAD.stroke$is.first)
#look at only transfusion people
min.hgb.afterAD.stroke$is.transfusion<-min.hgb.afterAD.stroke$patientunitstayid%in%transfusion.id
min.hgb.afterAD.stroke$delta.hgb<-min.hgb.afterAD.stroke$hgbmax-min.hgb.afterAD.stroke$hgbmin
min.hgb.afterAD.stroke.blood<-min.hgb.afterAD.stroke%>%filter(is.transfusion==T)
min.hgb.afterAD.stroke.noblood<-min.hgb.afterAD.stroke%>%filter(is.transfusion==F)

table(min.hgb.afterAD.stroke$is.transfusion)
hgb.baseline<-hgb%>%filter(labresultoffset<360)
hgb.patient<-hgb%>%group_by(patientunitstayid)%>%summarise(hgb=min(labresult))
hgb.patient$hgb.min<-ifelse(hgb.patient$hgb<7, "low",ifelse(hgb.patient$hgb<9,"mid","high"))
cohort<-left_join(cohort,hgb.patient)




#Model

#No adjustment
cohort$actualhospitalmortality<-as.numeric(as.factor(cohort$actualhospitalmortality))-1
bad.fit<-glm(data = cohort, actualhospitalmortality~transfusion,family = "binomial")
summary(bad.fit)
467/(467+3609)#no treatment
149/(149+543)#treatment

#regression

rg<-glm(data = cohort, actualhospitalmortality~
          transfusion*hgb.min+gender+Vasopressor+apachescore+
          +Trauma*transfusion+postSurgery*transfusion+vascularDisorders*transfusion,family = "binomial")
summary(rg)


rg1<-glm(data = cohort.intake, actualhospitalmortality~
           intake.group*hgb.min+gender+Vasopressor+apachescore+
           Trauma*intake.group+postSurgery*intake.group+vascularDisorders*intake.group,family = "binomial")
summary(rg1)
#Propensity

fit<-glm(data = cohort, transfusion~hgb.min+gender+Vasopressor+apachescore,family = "binomial")
summary(fit)

pd <- predict(fit, type = "response")
numer.fit <- glm(label ~ 1, family = binomial(), data = cohort)
summary(numer.fit)

pn<- predict(numer.fit, type = "response")
cohort$stable.weights <-
  ifelse(cohort$label == 0, ((1 - pn) / (1 - pd)),
         (pn / pd))

#Model 
msm.w <- geeglm(
  actualhospitalmortality ~ label,
  data = cohort,
  weights = weight,
  id = rownames(cohort),
  corstr = "independence"
)

beta <- coef(msm.w)
SE <- coef(summary(msm.w))[, 2]
lcl <- beta - qnorm(0.975) * SE
ucl <- beta + qnorm(0.975) * SE
cbind(beta, lcl, ucl)#Not significant



###### SUB Cohort
cohort.intake$intake.group<-as.numeric(as.factor(cohort.intake$intake.group))-1
fit<-glm(data = cohort.intake, intake.group~hgb.min+gender+Vasopressor+apachescore,family = "binomial")
summary(fit)

pd <- predict(fit, type = "response")
numer.fit <- glm(intake.group ~ 1, family = binomial(), data = cohort.intake)
summary(numer.fit)

pn<- predict(numer.fit, type = "response")
cohort.intake$stable.weights <-
  ifelse(cohort.intake$intake.group == 0, ((1 - pn) / (1 - pd)),
         (pn / pd))

#Model
msm.w <- geeglm(
  actualhospitalmortality ~ intake.group,
  data = cohort.intake,
  weights = stable.weights,
  id = rownames(cohort.intake),
  corstr = "independence"
)

beta <- coef(msm.w)
SE <- coef(summary(msm.w))[, 2]
lcl <- beta - qnorm(0.975) * SE
ucl <- beta + qnorm(0.975) * SE
cbind(beta, lcl, ucl)#Not significant


#MSM


beta <- coef(msm.w)
SE <- coef(summary(msm.w))[, 2]
lcl <- beta - qnorm(0.975) * SE
ucl <- beta + qnorm(0.975) * SE
cbind(beta, lcl, ucl)#Not significant


msm.w <- geeglm(
  actualhospitalmortality ~ label+Trauma+postSurgery+vascularDisorders,
  data = cohort,
  weights = weight,
  id = rownames(cohort),
  corstr = "independence"
)

beta <- coef(msm.w)
SE <- coef(summary(msm.w))[, 2]
lcl <- beta - qnorm(0.975) * SE
ucl <- beta + qnorm(0.975) * SE
cbind(beta, lcl, ucl)#Not significant


msm.w <- geeglm(
  actualhospitallos ~ label,
  data = cohort,
  weights = weight,
  id = rownames(cohort),
  corstr = "independence"
)

beta <- coef(msm.w)
SE <- coef(summary(msm.w))[, 2]
lcl <- beta - qnorm(0.975) * SE
ucl <- beta + qnorm(0.975) * SE
cbind(beta, lcl, ucl)#Not significant
#
#Find createnine
#Find TN

#intake output

#"packed red blood cells", "prbc","rbc", "packed cells", " blood", "blood product", "fresh frozen plasma",
#"FFP", "platelets", "plt", "(blood), factor(s)"



getwd()
setwd("/Users/sichenghao/Documents/GitHub/SCCM2020Team1/eICU/")
fwrite(cohort,"data.csv")
