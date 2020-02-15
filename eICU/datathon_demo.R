library(dplyr)
library(ggplot2)
library(readr)
require(descr)
library(car)

team1 <- read_csv("~/Downloads/team1.csv")

table(team1$age.group, team1$gender)

table(team1$hgb.min, team1$label)
mid <- team1 %>%
  filter(team1$hgb.min =='mid')

Trauma <- team1 %>% filter(Trauma == TRUE)

summary(Trauma$label, Trauma$hgb.min)

trauma_mid <- Trauma %>% filter(isTRUE(Trauma['hgb.min']=="mid"))
trauma_high <- Trauma %>% filter(Trauma['hgb.min']=='high')
t.test(trauma_high$label, trauma_mid$label)

group_by(Trauma, hgb.min) %>%
  summarise(
    count = n(),
    mean = mean(label, na.rm = TRUE),
    sd = sd(label, na.rm = TRUE)
  )

table(Trauma$hgb.min, Trauma$label)
table(Trauma$actualhospitalmortality)

vascular <- team1 %>% filter(vascularDisorders == TRUE)
post <- team1 %>% filter(postSurgery == TRUE)

TBI_high<- team1 %>% filter(Trauma==TRUE, hgb.min=='high')
TBI_mid<- team1 %>% filter(Trauma==TRUE, hgb.min=='mid')
TBI_mid$icu[TBI_mid$actualicumortality=='ALIVE'] <- 1
TBI_mid$icu[TBI_mid$actualicumortality=='EXPIRED'] <- 0

TBI_high_notrans <- team1 %>% filter(Trauma==TRUE, hgb.min=='high')

t.test(icu ~ label, data = Trauma, var.equal = TRUE)

vas_high<- team1 %>% filter(vascularDisorders==TRUE, hgb.min=='high')
vas_mid<- team1 %>% filter(vascularDisorders==TRUE, hgb.min=='mid')
vas_high$icud[vas_high$actualicumortality=='ALIVE'] <- 1
vas_high$icud[vas_high$actualicumortality=='EXPIRED'] <- 0


post_high<- team1 %>% filter(postSurgery==TRUE, hgb.min=='high')
post_mid<- team1 %>% filter(postSurgery==TRUE, hgb.min=='mid')
post_high$icud[post_high$actualicumortality=='ALIVE'] <- 1
post_high$icud[post_high$actualicumortality=='EXPIRED'] <- 0

