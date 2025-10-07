#!/bin/csh -f

## NOTE: To run this script, run "conda activate /proj/ie/proj/GSA-EMBER/BlueSky/BSP"

set sf2py_out = /proj/ie/proj/GSA-EMBER/BlueSky/sf2py/outputs/2024
set outdir = /proj/ie/proj/GSA-EMBER/BlueSky/ember_2024/inputs
set year = 2024

./set_offset.py ${year}0101 ${year}1031 $sf2py_out $outdir
set loc = ${outdir}/fire_locations_${year}.csv
head -1 ${outdir}/fire_locations_${year}0101_utc_wf.csv > $loc
grep -hv ^id ${outdir}/fire_locations_${year}*utc*.csv >> $loc
set event = ${outdir}/fire_events_${year}.csv
head -1 ${sf2py_out}/events_${year}0101.csv > $event
grep -hv ^id ${sf2py_out}/events_${year}*.csv >> $event
./source_summary.py $loc $event ${outdir}/fire_${year}_source_summary.csv
./source_fips_month_summary.py $loc $event ${outdir}/fire_${year}_county_month_source_summary.csv
