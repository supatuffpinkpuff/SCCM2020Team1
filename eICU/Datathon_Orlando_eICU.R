
library(data.table)
library(dplyr)
library(ggplot2)
library(gdata)
library(readxl)
library(pROC)
library(geepack)



setwd("/Users/sichenghao/Desktop/eICU/")

all.csv<-list.files(pattern="*.csv")
patient<-fread(all.csv[25])
apache<-fread(all.csv[5])
apache<-apache%>%filter(apache$apacheversion=="IV")
#First_Neuro<-fread("/Users/sichenghao/Desktop/FirstNeuroAdultReliablePatientStayIDs.csv")
cohort<-fread("/Users/sichenghao/Desktop/FinalPatientStayIDs.csv")
cohort<-left_join(cohort,patient)#join with patient
cohort<-left_join(cohort,apache)#join with apache
#Over look
table(cohort$actualhospitalmortality)
table(cohort$actualicumortality)


#Demograph
table(cohort$gender)/nrow(cohort)
table(cohort$ethnicity)/nrow(cohort)
table(cohort$unitadmitsource)
cohort$age<-as.numeric(cohort$age)
cohort$age.group<-ifelse(cohort$age > 89," >89 ",
                                 ifelse(cohort$age > 65, " 65-89",
                                        ifelse(cohort$age > 45, " 45-65","18-45")))

#sub_group

sub_group<-fread("/Users/sichenghao/Desktop/FinalPatientStayIDsWithGroups.csv")
cohort<-left_join(cohort,sub_group)

#Hgb
hgb<-fread("/Users/sichenghao/Desktop/Hgbdata.csv")
hgb.baseline<-hgb%>%filter(labresultoffset<-360)
hgb.patient<-hgb%>%group_by(patientunitstayid)%>%summarise(hgb=min(labresult))
hgb.patient$hgb.min<-ifelse(hgb.patient$hgb<7, "low",ifelse(hgb.patient$hgb<9,"mid","high"))
cohort<-left_join(cohort,hgb.patient)

#vaso
vaso<-fread("/Users/sichenghao/Desktop/VasopressorsData.csv")
cohort<-left_join(cohort,vaso)


#GCS
gcs<-fread("/Users/sichenghao/Desktop/GCSdata.csv")
gcs<-gcs[,2:5]
gcs$verbal[gcs$verbal==-1]=NA
gcs$motor[gcs$motor==-1]=NA
gcs$eyes[gcs$eye==-1]=NA
gcs$gcs<-gcs$verbal+gcs$motor+gcs$eyes
head(gcs$gcs)

cohort<-left_join(cohort,gcs)
cohort.id<-cohort$patientunitstayid


# Infusion
infusion<-fread(all.csv[16])
infusion$cellpath<-tolower(infusion$cellpath)
infusion<-infusion%>%filter(patientunitstayid%in%cohort.id)
blood<-infusion[grep("blood",infusion$cellpath),]
table(blood$cellpath)
table(blood$celllabel)


#In and Out
ino<-fread(all.csv[16])
ino<-ino%>%filter(patientunitstayid%in%cohort.id)
ino$cellpath<-tolower(ino$cellpath)
blood2<-ino[grep("blood",ino$cellpath),]

#treatment
treat<-fread(all.csv[29])
treat<-treat%>%filter(patientunitstayid%in%cohort.id)
treat$treatmentstring<-tolower(treat$treatmentstring)

str1<-unique(blood3$treatmentstring)
str2<-unique(blood4$treatmentstring)

str3<-str2[-which(str2%in%str1)]
blood3<-rbind(treat[grep("packed rbc",treat$treatmentstring),],
              treat[grep("prbc",treat$treatmentstring),],
              treat[grep("packed red",treat$treatmentstring),])


blood4<-rbind(treat[grep("packed rbc",treat$treatmentstring),],
              treat[grep("prbc",treat$treatmentstring),],
              treat[grep("packed red",treat$treatmentstring),],
              treat[grep("blood",treat$treatmentstring),])

str1<-unique(blood3$treatmentstring)
str2<-unique(blood4$treatmentstring)
str3<-str2[-which(str2%in%str1)]

cohort$label<-ifelse(cohort$patientunitstayid%in%blood$patientunitstayid |
                       cohort$patientunitstayid%in%blood2$patientunitstayid |
                       cohort$patientunitstayid%in%blood3$patientunitstayid,1,0)

#No adjustment
cohort$actualhospitalmortality<-as.numeric(as.factor(cohort$actualhospitalmortality))-1
bad.fit<-glm(data = cohort, actualhospitalmortality~label,family = "binomial")
summary(bad.fit)
467/(467+3609)#no treatment
149/(149+543)#treatment

#regression

rg<-glm(data = cohort, actualhospitalmortality~
         label*hgb.min+age.group+gender+Vasopressor+
          +Trauma*label+postSurgery*label+vascularDisorders*label,family = "binomial")
summary(rg)
#Propensity


fit<-glm(data = cohort, label~hgb.min+age.group+gender+Vasopressor,family = "binomial")
summary(fit)

pred<-predict(fit,type = "response",na.action = na.omit)
length(pred)
prob<-ifelse(cohort$label==0,
             1-predict(fit,type = "response"),
             predict(fit,type = "response"))
range(prob)
cohort$weight<-1/prob
hist(cohort$weight)
range(cohort$weight)

#MSM


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

#Comlication

lab<-fread(all.csv[17])

careplan<-fread(all.csv[9])
#intake output

#"packed red blood cells", "prbc","rbc", "packed cells", " blood", "blood product", "fresh frozen plasma",
"FFP", "platelets", "plt", "(blood), factor(s)"



getwd()
fwrite(cohort,"team1.csv")
