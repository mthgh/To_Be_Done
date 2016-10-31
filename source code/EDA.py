################ connect to sql ######################################

import MySQLdb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

db = MySQLdb.connect(host="localhost",    
                     user="root",         
                     passwd="1228",  
                     db="chicago_crime")  
cur = db.cursor()

############# data exploration ########################################

### 1. iucr and primary_description both categorize crime, which one ###
### should be involved as label? #######################################

## create iucr and primary_description bar chart to explore this

## obtain iucr data from database
cur.execute("select * from iucr_disp_ct")
iucr_disp_count = cur.fetchall()
iucr = np.array([x[0] for x in iucr_disp_count])
disp = np.array([x[1] for x in iucr_disp_count])
count = np.array([x[2] for x in iucr_disp_count])

## plot iucr bar chart
fig1, ax1 = plt.subplots(figsize=(15, 10))
ax1.bar(range(len(iucr)), count, linewidth=0.2, color="r", width=0.8)
ax1.set_xticks(np.arange(0,len(iucr),20))
ax1.set_xticklabels(np.array(iucr[np.arange(0,len(iucr),20)]))
ax1.set_ylabel('case_count')
ax1.set_xlabel("iucr_code")
max10_index = count.argsort()[::-1][:10]
for i in max10_index:
    ax1.text(i, count[i]+1000, iucr[i]+": "+disp[i])
ax1.set_title('Count of Crime by IUCR code (24 NA removed)')
plt.savefig("iucr_bar.pdf", format="pdf")
plt.show()

## obtain description data from database
cur.execute("select primary_disp, sum(ct) from iucr_disp_ct group by primary_disp")
disp_count = cur.fetchall()
disp = np.array([x[0] for x in disp_count])
count = np.array([x[1] for x in disp_count])

## plot primary description bar chart
fig2, ax2 = plt.subplots(figsize=(15, 10))
ax2.bar(range(len(disp)), count, linewidth=0.3, color="r", width=0.8)
ax2.set_xticks(np.arange(len(disp))+0.4)
ax2.set_xticklabels(disp, rotation=90)
ax2.set_ylabel('case_count')
ax2.set_xlabel("discription")
ax2.set_title('Count of Crime by Primary_Discription (24 NA removed)')
plt.savefig("description_bar.pdf", format='pdf')
plt.show()

### summary: iucr contains too much detail, primary_discription looks nice.
### the label is skewered (some have really high count, others have very small
### count). there are in tatol 32 categories, depending on how the correlation
### between other variables with this label, we may further group the labels
### to reduce category.

### 2. how community area relate to crime? ###################################

### obtain community data from database
cur.execute("select CommunityArea, count(*) from crime group by CommunityArea order by communityarea")
comm_count = cur.fetchall()
comm_count_v = comm_count[1:]
comm_count_v = np.array([(int(x), y) for (x, y) in comm_count_v])
comm_count_v = sorted(comm_count_v, key=lambda entry: entry[0])
comm = np.array([x[0] for x in comm_count_v])
count = np.array([x[1] for x in comm_count_v])

### draw bar chart
fig3, ax3 = plt.subplots(figsize=(15, 10))
ax3.bar(range(len(comm)), count, linewidth=0.3, color="r", width=0.8)
ax3.set_xticks(np.arange(len(comm))+0.4)
ax3.set_xticklabels(comm, rotation=90)
ax3.set_ylabel('case_count')
ax3.set_xlabel("community")
ax3.set_title('Count of Crime by community (NA Removed)')
plt.savefig("community_bar.pdf", format='pdf')
plt.show()

### summary: there is clearly some pattern between community and count of
### crime, since the neighboring community in graph (already sorted) also 
### mean that they are close geographically, we can clearly see the clustering 
### pattern.

### 3. how it looks like if from the above community bar chart, a third #######
### variable, uric or primary_description added to it? ########################

## fetch data from database and process it to dataframe
cur.execute("""
select communityarea, c.iucr, primary_disp, ct
from comm_iucr_ct c, iucr_code i
where c.iucr = i.iucr""")
comm_iucr_disp_ct = cur.fetchall()
comm_iucr_disp_ct_df = pd.DataFrame(np.array(comm_iucr_disp_ct), columns=["community", "iucr", "disp", "count"])
comm_iucr_disp_ct_df_dropNA = comm_iucr_disp_ct_df.dropna().reset_index(drop=True)

comm_iucr_disp_ct_df_dropNA.loc[:,"disp"] = \
comm_iucr_disp_ct_df_dropNA.loc[:,"disp"].map(lambda entry: entry.strip())
comm_iucr_disp_ct_df_dropNA.loc[:,"community"] = \
comm_iucr_disp_ct_df_dropNA.loc[:,"community"] .map(lambda entry: int(entry))

## draw a heat map between community area and iucr, using color to indicate how many
## crimes occur

#### helper function
def get_value(n):
    index_iucr = n/len(comm)
    index_comm = n%len(comm)
    iucr_value = iucr[index_iucr]
    comm_value = comm[index_comm]
    row = (comm_iucr_disp_ct_df_dropNA["community"] == comm_value) &\
          (comm_iucr_disp_ct_df_dropNA["iucr"] == iucr_value)
    count = comm_iucr_disp_ct_df_dropNA[row]["count"].values
    if count:
        return count[0]
    else:
        return 0

#### create data frame ready for heatmap
comm_iucr = pd.DataFrame(data=np.arange(len(comm)*len(iucr)).reshape(len(iucr), len(comm)), 
                         columns=comm, 
                         index=iucr)
comm_iucr = comm_iucr.applymap(get_value)

#### plot headmap
fig4, ax4 = plt.subplots(figsize=(15, 15))
a = ax4.pcolor(comm_iucr, cmap=plt.cm.Reds)
ax4.set_xlim(0, len(comm))
ax4.set_ylim(0, len(iucr))
ax4.set_xticks(np.arange(len(comm))+0.5)
ax4.set_xticklabels(comm, rotation=90)
ax4.set_yticks(np.arange(0.5, len(iucr)+0.5, 10))
ax4.set_yticklabels(np.array(iucr[np.arange(0,len(iucr), 10)]))
ax4.set_ylabel('iucr_code')
ax4.set_xlabel("community")
ax4.set_title('Count of Crime by IUCR and community (NA Removed)')
fig4.colorbar(a)
plt.savefig("comm_iucr_hm.pdf", format="pdf")
plt.show()

### similarly, draw heat map between communityarea and primary description


#### create data frame ready for heat map
comm_disp_count = comm_iucr_disp_ct_df_dropNA.groupby(["community","disp"])["count"].sum().reset_index()

for c in comm:
    for d in disp:
        count = comm_disp_count[(comm_disp_count["community"]==c) &
                                (comm_disp_count["disp"]==d)]["count"].values
        if not count:
            new_row = pd.DataFrame({"community":[c],
                                   "disp":[d],
                                   "count":[0]})
            comm_disp_count = comm_disp_count.append(new_row, ignore_index=True)
            
comm_disp_count = comm_disp_count.sort_values(by=["disp", "community"]).reset_index(drop=True)
count_array = comm_disp_count["count"].values.reshape(32,77)

comm_disp_count_hm = pd.DataFrame(count_array,columns=comm, index=disp)

#### community vs description heat map 
fig5, ax5 = plt.subplots(figsize=(15, 10))
f5 = ax5.pcolor(comm_disp_count_hm, cmap=plt.cm.Reds)
ax5.set_xlim(0, len(comm))
ax5.set_ylim(0, len(disp))
ax5.set_xticks(np.arange(len(comm))+0.5)
ax5.set_xticklabels(comm, rotation=90)
ax5.set_yticks(np.arange(0.5, len(disp)+0.5))
ax5.set_yticklabels(disp)
ax5.set_ylabel('primary_discription')
ax5.set_xlabel("community")
ax5.set_title('Count of Crime by Primary Description and Community (NA Removed)')
fig5.colorbar(f5)
plt.savefig("comm_description_hm.pdf", format='pdf')
plt.show()

#### now the communityarea vs description definitely looks better
#### than communityarea vs iucr code.
#### since the crime type is highly skewed, try to split the heat map
#### so that the pattern could be observed better.

#### split data frame for heat map by commonly crime type and not common
#### crime type

disp_top = []
disp_low = []
for d, c in disp_count:
    if c > 100000:
        disp_top.append(d)
    else:
        disp_low.append(d)
        
comm_disp_count_hm_top = comm_disp_count_hm.loc[disp_top,]
comm_disp_count_hm_low = comm_disp_count_hm.loc[disp_low,]

fig6 = plt.figure(figsize=(1, 10)) 
ax6_1 = plt.subplot(2,1,1)
ax6_2 = plt.subplot(2,1,2)

f6_1 = ax6_1.pcolor(comm_disp_count_hm_top, cmap=plt.cm.Reds)
ax6_1.set_xlim(0, len(comm))
ax6_1.set_ylim(0, len(disp_top))
ax6_1.set_xticks(np.arange(len(comm))+0.5)
ax6_1.set_xticklabels(comm, rotation=90)
ax6_1.set_yticks(np.arange(0.5, len(disp_top)+0.5))
ax6_1.set_yticklabels(disp_top)
ax6_1.set_ylabel('primary_discription')
ax6_1.set_xlabel("community")
ax6_1.set_title('Count of Crime by Primary Description and Community (Higher Counted, NA Removed)')
cbaxes_1 = fig6.add_axes([0.94, 0.56, 0.03, 0.33]) 
fig6.colorbar(f6_1, cax=cbaxes_1)

f6_2 = ax6_2.pcolor(comm_disp_count_hm_low, cmap=plt.cm.Reds)
ax6_2.set_xlim(0, len(comm))
ax6_2.set_ylim(0, len(disp_low))
ax6_2.set_xticks(np.arange(len(comm))+0.5)
ax6_2.set_xticklabels(comm, rotation=90)
ax6_2.set_yticks(np.arange(0.5, len(disp_low)+0.5))
ax6_2.set_yticklabels(disp_low)
ax6_2.set_ylabel('primary_discription')
ax6_2.set_xlabel("community")
ax6_2.set_title('Count of Crime by Primary Description and Community (Lower Counted, NA Removed)')
cbaxes_2 = fig6.add_axes([0.94, 0.13, 0.03, 0.33]) 
fig6.colorbar(f6_2, cax=cbaxes_2)
plt.savefig("comm_description_hm_split.pdf", format='pdf')
plt.show()

### now we can start to see the community and crime type patterns

### 4. now do the same thing for year variable, draw bar chart and heat map

## obtain data from database and create data frame ready for heat map
year_comm_disp_count_df.loc[:,"disp"] = \
year_comm_disp_count_df.loc[:,"disp"].map(lambda x: x.strip())
year_comm_disp_count_df = year_comm_disp_count_df.groupby(["year", "comm", "disp"])["count"].sum().reset_index()
year_count_df = year_comm_disp_count_df.groupby(["year"])["count"].sum().reset_index()
year_disp_count_df = year_comm_disp_count_df.groupby(["year", "disp"])["count"].sum().reset_index()

for y in np.arange(2001,2017,1):
    for d in disp:
        count = year_disp_count_df[(year_disp_count_df["year"]==y) &
                                (year_disp_count_df["disp"]==d)]["count"].values
        if not count:
            new_row = pd.DataFrame({"year":[y],
                                   "disp":[d],
                                   "count":[0]})
            year_disp_count_df = year_disp_count_df.append(new_row, ignore_index=True)

year_disp_count_df = year_disp_count_df.sort_values(by=["disp", "year"])

year_count_array = year_disp_count_df["count"].values.reshape(32,16)

year_disp_count_hm = pd.DataFrame(year_count_array,columns=np.arange(2001,2017,1), index=disp)

year_disp_count_hm_top = comm_disp_count_hm.loc[disp_top,]
year_disp_count_hm_low = comm_disp_count_hm.loc[disp_low,]

### draw heat map
fig8 = plt.figure(figsize=(15, 10)) 
ax8_1 = plt.subplot(2,1,1)
ax8_2 = plt.subplot(2,1,2)

f8_1 = ax8_1.pcolor(year_disp_count_hm_top, cmap=plt.cm.Reds)
ax8_1.set_xlim(0, 16)
ax8_1.set_ylim(0, len(disp_top))
ax8_1.set_xticks(np.arange(16)+0.5)
ax8_1.set_xticklabels(np.arange(2001,2017,1))
ax8_1.set_yticks(np.arange(0.5, len(disp_top)+0.5))
ax8_1.set_yticklabels(disp_top)
ax8_1.set_ylabel('primary_discription')
ax8_1.set_xlabel("year")
ax8_1.set_title('Count of Crime by Primary Description and Year (Higher Counted, NA Removed)')
cbaxes_1 = fig8.add_axes([0.94, 0.56, 0.03, 0.33]) 
fig8.colorbar(f8_1, cax=cbaxes_1)

f8_2 = ax8_2.pcolor(year_disp_count_hm_low, cmap=plt.cm.Reds)
ax8_2.set_xlim(0, 16)
ax8_2.set_ylim(0, len(disp_low))
ax8_2.set_xticks(np.arange(16)+0.5)
ax8_2.set_xticklabels(np.arange(2001,2017,1))
ax8_2.set_yticks(np.arange(0.5, len(disp_low)+0.5))
ax8_2.set_yticklabels(disp_low)
ax8_2.set_ylabel('primary_discription')
ax8_2.set_xlabel("year")
ax8_2.set_title('Count of Crime by Primary Description and Community (Lower Counted, NA Removed)')
cbaxes_2 = fig8.add_axes([0.94, 0.13, 0.03, 0.33]) 
fig8.colorbar(f8_2, cax=cbaxes_2)
plt.savefig("year_description_hm.pdf", format='pdf')
plt.show()
