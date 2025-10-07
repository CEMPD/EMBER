#!/bin/csh -f

set workpath = /proj/ie/proj/GSA-EMBER/BlueSky/ember_2024
set year = 2024
set case = "2024"
set bsp = "/proj/ie/proj/GSA-EMBER/BlueSky/BSPv4.4.1/bin/bsp"
#source $workpath/setup.csh
#source $workpath/setup.csh
#source /work/EMIS/tools/bsp/bin/activate.csh

set dimon = (31 28 31 30 31 30 31 31 30 31 30 31)
set startd = 1
foreach mon ( 3 4 5 6 7 8 9 10 )
#foreach mon ( 7 )
    if ($mon < 10) then
        set MM = 0${mon}
    else
        set MM = ${mon}
    endif
    set day = $startd
    while ($day <= $dimon[$mon])
        if ($day < 10) then
            set DD = 0${day}
        else
            set DD = ${day}
        endif
        set date = ${year}${MM}${DD}
        echo $date
        set log = $workpath/logs/${case}/fire_bsp_${date}_log.csv
        set bsfin = $workpath/inputs/fire_locations_${date}.csv
        set utcadj = $workpath/inputs/fire_locations_${date}_utc
        #$workpath/./set_offset.py $bsfin $utcadj
        #foreach label (rx wf)
        foreach label (wf)
            set typeadj = $workpath/inputs/fire_locations_${date}_utc_${label}.csv
            #set config = $workpath/bsp_config_${label}.json
            set config = $workpath/bsp_config_v4_${label}.json
            date
            #bsp load filter fuelbeds ecoregion consumption emissions timeprofile extrafiles --config-file=$config --today=${date} \
            #  --indent=2 --no-input -J load.sources='[{"name": "bsf", "format":"CSV", "type": "file", "file": "'${typeadj}'"}]' -o json/us/fire_process_${date}_${label}.json #--log-level=debug
            bsp load filter fuelbeds ecoregion consumption emissions timeprofile extrafiles --config-file=$config --today=${date} \
              --indent=2 --no-input -J load.sources='[{"name": "bsf", "format":"CSV", "type": "file", "file": "'${typeadj}'"}]' -o json/us_v4/fire_process_${date}_${label}.json # --log-level=debug  
            date
        end
        @ day++
    end
end
