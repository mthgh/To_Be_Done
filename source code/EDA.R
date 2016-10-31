############# draw bar chart of each variable and test their ######
############# correlation with "crime_description" label ##########

##### connect to mysql and obtain data
library(RMySQL)
db <- dbConnect(MySQL(), params)
rs <- dbSendQuery(db, "select * from mfa_t")
crime_time_place <-fetch(rs, n=-1)

##### process data
trim <- function (x) gsub("^\\s+|\\s+$", "", x)
crime_time_place$Primary_disp <- 
    trim(crime_time_place$Primary_disp)

crime_time_place$casemonth <- factor(crime_time_place$casemonth)
crime_time_place$Primary_disp <- factor(crime_time_place$Primary_disp)
crime_time_place$beat <- factor(crime_time_place$beat)
crime_time_place$communityarea <- factor(crime_time_place$communityarea)

library(ggplot2)
# casetime range from 0-24, plot histogram to determine if want to make
# smaller bins
ggplot(aes(x=casetime), data=crime_time_place) + 
    geom_histogram(bins=24,color = I("black"), fill=I("#099DD9"))

# group casetime into smaller bins
crime_time_place$time.range <- 
    cut(crime_time_place$casetime, c(0,1,4,7,9,12,18,23,24), right=F)
levels(crime_time_place$time.range) <- 
    c("[23,1)", levels(crime_time_place$time.range)[2:7], "[23,1)")

# un-select casetime 
data <- crime_time_place[,c("caseyear", "casemonth",
                            "time.range","beat",
                            "communityarea","Primary_disp")]

##### conduct chi-square test and plot bar chart for each variable
library(MASS)
fig <- vector(mode='list', length = 6)

test1 <- chisq.test(data[,"caseyear"], data[,"Primary_disp"])
fig[[1]] <-
    ggplot(aes(x=caseyear), data=data) + 
    geom_histogram(bins=16, fill=I("#099DD9")) + 
    annotate("text",label=sprintf("p = %.2f, chi-square = %.2f", 
                                  test1$p.value, test1$statistic[[1]]),
             color="black", x = Inf, y = Inf, 
             vjust=0.9, hjust=0.9)

for (i in c(2:5)) {
    test <- chisq.test(data[,i], data[,"Primary_disp"])
    
    fig[[i]] <- ggplot(aes(x=data[,i]), data=data) +
        geom_bar(fill=I("#099DD9")) +
        xlab(sprintf("%s", colnames(data)[i])) +
        annotate("text",label=sprintf("p = %.2f, chi-square = %.2f",
                                      test$p.value, test$statistic[[1]]),
                 color="black", x = Inf, y = Inf, 
                 vjust=0.9, hjust=0.9)
}

fig[[6]] <- ggplot(aes(x=Primary_disp), data=data) +
    geom_bar(fill=I("#099DD9")) +
    theme(axis.text.x=element_blank(),
          axis.ticks.x=element_blank()) +
    xlab("Crime Description")

library(gridExtra)

grid.arrange(grobs=fig, ncol=2, top="Bar Chart of Variables and Chi-square Test Result with 'Crime Description'")
