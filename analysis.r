setwd('/Users/AntoineGarcia/Desktop/IS5126 - Hands-On Business Analytics/miniproject/NBA/NBA_salaries')
#install.packages("relaimpo")
library(relaimpo)
library(datasets)
library(ggplot2)

dfs <- read.csv(file='Season0405.csv',header=TRUE, sep=",")
salaries <- read.csv(file='salaries.csv',header=TRUE, sep=",")
totals <- read.csv(file='totals.csv',header=TRUE, sep=",")
advanced <- read.csv(file='advanced.csv',header=TRUE, sep=",")

Season0405 <- dfs
dfs <- data.frame(dfs)

#Season0405$salary<-ceiling(Season0405$salary/1000000)
ggplot(Season0405,aes(age,salary,color=team_id))+geom_point()
ggplot(Season0405,aes(pos,salary,color=team_id))+geom_point()
ggplot(Season0405,aes(team_id,salary))+geom_point()
ggplot(Season0405,aes(fg2a,salary,color=team_id))+geom_point()
ggplot(Season0405,aes(fg3a,salary,color=team_id))+geom_point()
ggplot(Season0405,aes(blk,salary,color=team_id))+geom_point()
ggplot(Season0405,aes(ast,salary,color=team_id))+geom_point()
ggplot(Season0405,aes(pts,salary,color=team_id))+geom_point()
ggplot(Season0405,aes(fg3_pct,salary,color=team_id))+geom_point()
head(Season0405)

#efg_pct, ft_pct, ts_pct, trb, ast, stl, blk, tov_pct, pf, pts, g, mp, per
fit <- lm(salary ~ g + mp + ts_pct + blk_pct + age + per +
            tov_pct + stl_pct + drb_pct + blk_pct + usg_pct, data=dfs)
summary(fit)


calc.relimp(fit,type=c("lmg","last","first","pratt"), rela=TRUE)
# Bootstrap Measures of Relative Importance (1000 samples) 
boot <- boot.relimp(fit, b = 1000,
                    type = c("lmg", "last", "first", "pratt"),
                    rank = TRUE, diff = TRUE, rela = TRUE)
booteval.relimp(boot) # print result
plot(booteval.relimp(boot,sort=TRUE)) # plot result


fit <- lm(salary ~ mp + age + per, data=dfs)




cloumnnames<-c("age","salary")
newdata<-Season0405[cloumnnames]
Cluster<-kmeans(newdata[,1:2],5,nstart=5000)
Cluster
table(Cluster$cluster)
min(Season0405$salary)
