#!/bin/tcsh -f

set year = 2024

set workdir = "/proj/ie/proj/GSA-EMBER/BlueSky/BSP_post_processing"
set rootdir = "/proj/ie/proj/GSA-EMBER/BlueSky"

set case = "ember_2024"

set ff10_out = "${rootdir}/${case}/smoke/inputs"

set startDay = '20240301' # First day to include in YYYYMMDD format
set endDay   = '20241031' # Last day to include in YYYYMMDD format

set run_concat = 'Y'
set run_dupchk = 'Y'
set run_addhap = 'Y'
set run_gnff10 = 'Y'
set run_fhff10 = 'Y'
set run_fxfips = 'Y'

set us_label   = sf2_${year}_ember_us
set us_concat  = $rootdir/${case}/outputs/us/sf2_${year}_ember_us.csv
set us_nodupes = $rootdir/${case}/outputs/us/sf2_${year}_ember_us_nodupes.csv
set us_dupes   = $rootdir/${case}/outputs/us/sf2_${year}_ember_us_dupes.csv
set us_zeroe   = $rootdir/${case}/outputs/us/sf2_${year}_ember_us_zeroemiss.csv
set us_haps    = $rootdir/${case}/outputs/us/sf2_${year}_ember_us_nodupes_haps.csv

set ca_label   = sf2_${year}_ember_canada
set ca_concat  = $rootdir/${case}/outputs/canada/sf2_${year}_ember_canada.csv
set ca_nodupes = $rootdir/${case}/outputs/canada/sf2_${year}_ember_canada_nodupes.csv
set ca_dupes   = $rootdir/${case}/outputs/canada/sf2_${year}_ember_canada_dupes.csv
set ca_zeroe   = $rootdir/${case}/outputs/canada/sf2_${year}_ember_canada_zeroemiss.csv
set ca_haps    = $rootdir/${case}/outputs/canada/sf2_${year}_ember_canada_nodupes_haps.csv

## Concat fires
if ( $run_concat == 'Y' ) then

echo "Concatenating US fires..."
$workdir/concat_fires.py $rootdir/${case}/outputs/us $us_concat $startDay $endDay
echo "Concatenating Canada fires..."
$workdir/concat_fires.py $rootdir/${case}/outputs/canada $ca_concat $startDay $endDay

endif

## Duplicate checker
if ( $run_dupchk == 'Y' ) then
echo "Checking for Duplicates..."
$workdir/dupes.py $us_concat $us_nodupes $us_dupes $us_zeroe

$workdir/dupes.py $ca_concat $ca_nodupes $ca_dupes $ca_zeroe
endif

## Add HAPs
if ( $run_addhap == 'Y' ) then
echo "Adding HAPs..."

$workdir/add_haps.py $us_nodupes $us_haps

$workdir/add_haps_canada.py $ca_nodupes $ca_haps
endif

## Process FF10
if ( $run_gnff10 == 'Y' ) then
echo "Converting BSP outputs to FF10"

mkdir -p $ff10_out

python -u $workdir/gen_fire_ff10.py $us_haps $us_label $ff10_out
python -u $workdir/gen_fire_ff10.py $ca_haps $ca_label $ff10_out

endif

## Process FF10 for FlintHill
if ( $run_fhff10 == 'Y' ) then
echo "Processing FF10 for Flint Hill..."
python -u $workdir/flinthills_calc.py ${year} /proj/ie/proj/GSA-EMBER/BlueSky/HMS/hms_split/hms_${year}_us/hms_${year}_us_fccscdl_grass_fh.csv $workdir/ancillary/fh_2016_2024.csv $workdir/ancillary/sera_grass_efs_with_haps_march5_2021.csv $ff10_out
endif

## Fix wrong FIPS
if ( $run_fxfips == 'Y' ) then
echo "Fixing wrong FIPS code..."
set inpdir = $ff10_out

foreach f ($inpdir/ptinv*)
    #sed -i 's/"US","02000"/"US","06073"/g' $f
    #sed -i 's/"US","28000"/"US","48215"/g' $f
    sed -i '/^"US","02000",""/d' $f
    sed -i '/^"US","08000",""/d' $f
    sed -i 's/"US","09170"/"US","09009"/g' $f # Remap new FIPS code 09170 corresponds to the South Central Connecticut Planning Region, CT whic was created in 2022
end

foreach f ($inpdir/ptday*)
    #sed -i 's/US,02000/US,06073/g' $f
    #sed -i 's/US,28000/US,48215/g' $f
    sed -i '/^"US","02000",""/d' $f
    sed -i '/^"US","08000",""/d' $f
    sed -i 's/"US","09170"/"US","09009"/g' $f
    sed -i '/^US,02000,/d' $f
    sed -i '/^US,08000,/d' $f
    sed -i 's/US,09170/US,09009/g' $f
end
endif