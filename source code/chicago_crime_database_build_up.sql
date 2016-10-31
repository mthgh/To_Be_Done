
/* load the main table crime cases over last 16 years in chicago */
create table crime 
(ID int, CaseNum varchar(10), Date datetime, Block varchar(50),
IUCR varchar(10), PrimaryType varchar(20), Description varchar(50), LocDesp varchar(50), 
Arrest tinyint, Domestic tinyint, Beat varchar(10), District varchar(10), Ward varchar(10),
CommunityArea varchar(10), FBICode varchar(10), X_coord varchar(20), Y_coord varchar(20),
Year int, UpdatedOn Datetime, Lat Double, Lon Double, Pos varchar(100)
);

load data infile "path/Crimes_-_2001_to_present.csv"
ignore
into table crime
fields terminated by ","
lines terminated by "\n"
ignore 1 lines
(
ID, CaseNum, @Date, Block,
IUCR, PrimaryType, Description, LocDesp, 
@Arrest, @Domestic, Beat, District, Ward,
CommunityArea, FBICode, X_coord, Y_coord,
Year, @UpdatedOn, Lat, Lon, Pos
)
set
Date = str_to_date(@date, '%m/%d/%Y %h:%i:%s %p'),
UpdatedOn = str_to_date(@UpdatedOn, '%m/%d/%Y %h:%i:%s %p'),
Arrest = IF(@Arrest='false',0,1),
Domestic = IF(@Domestic ='false',0,1);

/* load the iucr_code for clean iucr and primary description area */
create table IUCR_code
(
IUCR varchar(10) Primary key, Primary_disp varchar(100),
Secondary_disp varchar(100), Index_code varchar(10)
);

load data infile "path/Chicago_Police_Department__IUCR__Codes.csv"
ignore
into table IUCR_code
fields terminated by ","
lines terminated by "\n"
ignore 1 lines;


/* load beat code for clean the beat code area */
create table beat_code
(
the_geom text, district varchar(10),
sector varchar(10), beat varchar(10),
beat_num varchar(10)
);

load data infile "G:/cs/datacamp/challenge 16-10-27/PoliceBeatDec2012.csv"
ignore
into table beat_code
fields terminated by ","
lines terminated by "\n"
ignore 1 lines;