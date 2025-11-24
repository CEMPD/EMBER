#!/bin/csh -f
# Download the Canada NBAC hotspot perimeters and prepare for SF2 import
#setenv GETTYP "realtime"
setenv GETTYP "archive"
setenv YYYY 2024

if (! -d tmp) then
    mkdir tmp
endif
rm tmp/*

if ( $GETTYP == "realtime" ) then

set hotspots = https://cwfis.cfs.nrcan.gc.ca/downloads/hotspots/

wget -P tmp $hotspots/perimeters.dbf
wget -P tmp $hotspots/perimeters.prj
wget -P tmp $hotspots/perimeters.shp
wget -P tmp $hotspots/perimeters.shx

set today = `date +%d%b%y`
set tbl = canada_active_perimeters_${today}
rename perimeters $tbl tmp/*
mv tmp/${tbl}.* .

endif

if ( $GETTYP == "archive") then

wget -P tmp "https://cwfis.cfs.nrcan.gc.ca/downloads/hotspots/archive/${YYYY}_perimeters.zip"
unzip  tmp/${YYYY}_perimeters.zip -d tmp/
set tbl = canada_active_perimeters_${YYYY}
rename cc_apt_buf $tbl tmp/*
mv tmp/${tbl}.* .

endif

ogrinfo -sql "ALTER TABLE $tbl ADD sdate date" ${tbl}.shp
ogrinfo -dialect sqlite -sql "update $tbl set sdate=date(substr(replace(FIRSTDATE,'/','-'),1,10))" ${tbl}.shp
ogrinfo -sql "ALTER TABLE $tbl ADD edate date" ${tbl}.shp
ogrinfo -dialect sqlite -sql "update $tbl set edate=date(substr(replace(LASTDATE,'/','-'),1,10))" ${tbl}.shp
ogrinfo -sql "ALTER TABLE $tbl ADD acres float" ${tbl}.shp
ogrinfo -dialect sqlite -sql "update $tbl set acres=(st_area(geometry)/4046.86)" ${tbl}.shp
ogrinfo -sql "ALTER TABLE $tbl ADD fname string" ${tbl}.shp
ogrinfo -dialect sqlite -sql "update $tbl set fname=cast(UID as string)" ${tbl}.shp
ogrinfo -sql "ALTER TABLE $tbl ADD firetype string" ${tbl}.shp
ogrinfo -dialect sqlite -sql "update $tbl set firetype='WF'" ${tbl}.shp

## Extract only fires started in target year
ogrinfo -dialect sqlite -sql "SELECT * FROM ${tbl} WHERE strftime('%Y', sdate) = '${YYYY}'" ${tbl}.shp

## Write Attribute table to csv file for QA/QC
ogr2ogr -f "CSV" ${tbl}.csv ${tbl}.shp -dialect sqlite -sql "SELECT * FROM ${tbl}"