###Goal:
The dataset is [chicago crime records](https://data.cityofchicago.org/Public-Safety/Crimes-2001-to-present/ijzp-q8t2/data) from 2001 to 2016.
The time, place and type of crime are described in detail over 21 field. Upon analysing this dataset, the goal is to build a model which could predict the probability of certain type of crime based on time and place information. The model will be helpful to warn people about dangerous places and time, help to reduce the risk of being attacked. It would also be helpful to police officers by predicting where might be dangerous and what they might want to pay more attention to.

###Approach:
The variables in the dataset will be categoried to time related information (year, month, time, weekdays, etc), location related information (neighborhood, beat, police district, location description (restaurant, parking lot, etc), latitude, longitude,etc) and labels (type of crime by iucr code, FBI-code, if domestic, if arrested, etc). The goal is to be able to predict the labels based on time and location.

The correlation of each variable with labels, and correlation between variables could be computed through chi-square or t test, to evaluate their relationship with the labels and the variable interactions. multiple factor analysis could also be conducted to help understand the structure and correlations between all features.This process will be helpful to identify highly related features and engine new features based on findings.

After proper features selection, the selected feature will be applyed to supervised learning. Dataset split into training set and testing set. Different algrithms, like svc, logistic regression, decision tree, etc could be tested with cross validtion using training set (with proper selection of evaluation metrics). This process, together with feature selection could go back and forth to find better model. Eventually, test set could be used to evaluate the final model.

###Initial process and findings:
1. the data was loaded into mysql using ```chicago_crime_database_build_up.sql```, together with the crime records data, some other relevant dataset, including [iucr code](https://data.cityofchicago.org/d/c7ck-438e), [beat_code](https://data.cityofchicago.org/d/aerh-rz74) are also loaded into the database for use.

2. the data was clearned using ```data_process.sql```, field cleaned including "iucr", "communityarea", "year", etc. some new tables were also created by grouping and join. The new tables will be used to do EDA analysis.

3. using ```EDA.py```, several variables were investigated through plot.  

the label variable "iucr" and "primary_description" were visualized using bar chart. "iucr" is a code categorize the type of crime, and there are around 400 categories in total in the dataset. "primary_description" is also used to categorize the type of crime, there are 32 categories in total, through the bar chart, it was clearly that "iucr" contains too much detail and looks not very suitable for prediction. On the other hand, it is more proper to use "primary_description" as the label for prediction. It could be seen from the bar chart that this label is skewed (some categories' counting are very high whereas some categories' counting really low). Depending on how the predictors correlate to this label, the label may need to be further grouped to reduce the number of categories.

the bar chart of communityarea variable clearly show a pattern between community and crime numbers. since the communityarea was pre-processed and sorted, the neighboring community also mean that they are close geograpycally. there is a clear clustering among communities close together.

two heatmap was plotted: first involves communityarea vs iucr_code using color to indicte number of crime, second involves communityarea vs primary_description using color to indicate number of crime. Through comparasion of the two heatmap, it was clear the latter resolves much better than the former, indicated by clear clustering patterns. since the description of crime is highly skewered, the latter heat map was also split to give better look.

for the year varialbe, a bar chart was also plotted, it looks like that over the years, the total number of crime kept decreasing and it was quite linear. the count of crime in 2001 was unusual small, also 2002 seems a litter bit unusual as well. it was probably because the dataset started from 2001 and the system was not very consistance at that time (for example, sometimes, police input data, sometimes not), although it does look like the dataset started from Jan 1st. For this inconsistancy, in the modeling, the 2001, 2002 data might need to be removed. The 2016 data is not yet complete (the latest records was oct), one might want to remember this while doing modeling.

the heatmap of year vs primary_description using color to indicte number of crime was also plotted. Overall, it looks like all the different type of crime decrease over the years, whereas some of the crime type acturally increase slightly, like "THEFT" and "BATTERY". These might serve as important features for predicting label.

4.using ```EDA.R```, variables bar charts and the chi-square test results with label(crime description) were given.

other than year and commnity crime which talked above, month, time, beat were investigated. all of them show high correlation to description of crime based on chi-square test.

month bar char seems to be very uniform, it looks like that in summer, the number of crime is higher than in winter, that makes sense, since cold weather and snow makes outdoor activity hard. Febrary seems have the least amount of crime, it is probably relate to the total days in Febrary. This feature could be further grouped (winter vs summer) to see the correlation.

time was extract from the database as hour, however, a hour bar chart indictated some patterns (early to midnight, the count of crime is high, in the morning the count of crime is low, etc.), therefore, the hour features were grouped according to the patterns and a new bar chart was shown, which clearly indicated pattern between time and crime count.

beat is a smaller place variable than communityarea. from the bar chart, there are certainly differences between different beat. It would be valuable if they can be combined with communityarea together on the map to show crime patterns.

###Initial EDA summary
1. "iucr" and "primary_description" are both label variables, the former seems to contain too much detail, and the latter will be better to be used as a label. The latter label was highly skewed, further grouping migh be needed to reduce category.
2. through the heatmap of communityarea vs primary_description using color to indicte amount of crime, a clear clustering of communityarea and primary_description of crime could be observed (the neighboring communityarea also indicate that they are close together geograpyically).
3. investigation into year variable show that 2001,2002 and 2016 data were unusual, they might need to be taken special care while doing modeling, the heatmap show that for most type of crimes, the number decrease over the years, while in a few cases, they are acutally increasing in recent years, like "THEFT" and "BATTERY".
4. month bar chart show summer have more crime then winter, the feature could be further grouped to winter vs summer to see the correlation.
5. time was extracted from the dataset as hour, they were grouped according to initial hour bar chart. count of crime is high at early to midnight, and low in the morning.

