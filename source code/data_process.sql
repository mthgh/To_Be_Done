########################## clean table ##############################
## 1. field "IUCR"
 
## compare field "IUCR" with standard IUCR code obtained from 
## https://data.cityofchicago.org/d/c7ck-438e, there are ~120 unexpected IUCR
select distinct c.IUCR
from crime c
where not exists (
select I.iucr 
from iucr_code i
where i.iucr = c.iucr
);

# found that most of the unexpected IUCRs are due to leading zero. Therefore,
# they are updated as following
SET SQL_SAFE_UPDATES = 0;
update crime
set iucr = TRIM(LEADING '0' FROM iucr)
where iucr REGEXP "^0[0-9]+$";

# still, there are other ~20 IUCR code that are unusual, but not due to leading zeros,
# some of them exists in thousands of rows. after check on their primary type, they are
# very consistant, which make me believe they are not due to typos. Maybe such code were
# used before as old versions. At last, I added some of the IUCR codes I think valid to the
# IUCR_code table and set to null for the ones only exists in a couple of rows. 
select c.IUCR, count(*)
from crime c
where not exists (
select I.iucr 
from iucr_code i
where i.iucr = c.iucr
)
group by IUCR
order by IUCR;

select iucr, PrimaryType
from crime
where iucr = "5114"

insert into iucr_code values ("499", "BATTERY", "", "");
insert into iucr_code values ("5008", "OTHER OFFENSE", "", "");
insert into iucr_code values ("5093", "NON-CRIMINAL", "", "");
insert into iucr_code values ("5114", "NON-CRIMINAL", "", "");
insert into iucr_code values ("840", "THEFT", "", "");
insert into iucr_code values ("841", "THEFT", "", "");
insert into iucr_code values ("842", "THEFT", "", "");
insert into iucr_code values ("843", "THEFT", "", "");

update crime
set iucr = null
where iucr in ("3961", "5005", "5013", "5073", "5094", "5113", "585", "830", "9901");

## 2. field "communityarea" 

# this field shoud be from 1-77 according to https://data.cityofchicago.org/d/cauq-8yn6 .
# about 150 unexpected number of communityarea like "false", "0", "831" etc were observed.
# Another problem is that there are leading zero in some of them, like "001", "025"
select communityarea, count(*)
from crime
group by communityarea;

# to fix, the unexpected values were set to null and leading zeros were removed
update crime
set communityarea=NULL
where communityarea="" or communityarea = "1812" or 
communityarea = "0813" or communityarea = "false" or
communityarea = "0";

SET SQL_SAFE_UPDATES = 0;
update crime
set communityarea=TRIM(LEADING '0' FROM communityarea)
where communityarea REGEXP "^0+[0-9]+$";

## 3. field "year" 
## year field contain so many wrong data. therefore, delete this column
## year will be obtained from data later on
select year, count(*)
from crime
group by year;

SELECT distinct YEAR(Date)
from crime;

alter table crime drop column year;

## 4. create some tables for convinient use
create table year_comm_iucr_ct as
select year(Date) as year, communityarea, iucr, count(*) as ct
from crime 
group by year(Date), communityarea, iucr;

create table MFA_T as
select year(Date) as caseyear, month(Date) as casemonth,
hour(Date) as casetime, Primary_disp, beat, communityarea
from crime c,iucr_code i
where c.iucr=i.iucr and beat REGEXP "^[0-9]+$" and 
communityarea is not null;

create table comm_iucr_ct as
select communityarea, iucr, count(*) as ct
from crime
group by communityarea, iucr
order by communityarea, iucr

create table iucr_disp_ct as
select T.iucr as iucr, primary_disp, ct
from 
(select iucr, count(*) as ct from crime group by iucr order by iucr)  T,
iucr_code i
where T.iucr = i.iucr






















