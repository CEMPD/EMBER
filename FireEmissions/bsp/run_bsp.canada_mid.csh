#!/bin/csh -f

set workpath = /proj/ie/proj/GSA-EMBER/BlueSky/ember_2024
set year = 2024
#source $workpath/setup.csh
#source /work/EMIS/tools/bsp/bin/activate.csh
set bsp = "/proj/ie/proj/GSA-EMBER/BlueSky/BSPv4.4.1/bin/bsp"

set dimon = (31 28 31 30 31 30 31 31 30 31 30 31)
foreach mon (3 4 5 6 7 8 9 10)
#foreach mon (3)
    if ($mon < 10) then
        set MM = 0${mon}
    else
        set MM = ${mon}
    endif
    set day = 1 
    while ($day <= $dimon[$mon])
        if ($day < 10) then
            set DD = 0${day}
        else
            set DD = ${day}
        endif
        set date = ${year}${MM}${DD}
        echo $date
        set bsfin  = $workpath/inputs/fire_locations_${date}.csv
        set utcadj = $workpath/inputs/fire_locations_${date}_utc
        #$workpath/./set_offset.py $bsfin $utcadj
        foreach label (wf)
            set typeadj = $workpath/inputs/fire_locations_${date}_utc_${label}.csv
            set config = $workpath/bsp_config_v4_${label}_canada_mid.json
            set log = $workpath/logs/fire_bsp_canada_${date}_log.csv
            echo $typeadj
            date
            bsp load filter fuelbeds ecoregion consumption emissions timeprofile extrafiles --config-file=$config --today=${date} \
              --indent=2 --no-input -J load.sources='[{"name": "bsf", "format":"CSV", "type": "file", "file": "'${typeadj}'"}]' -o json/canada_v4/fire_process_${date}_${label}_canada_mid.json 
            date
        end
        @ day++
    end
end
