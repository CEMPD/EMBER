#!/bin/tcsh -f

source /proj/ie/proj/GSA-EMBER/BlueSky/ember_2024/smoke/scripts/directory_definitions.csh

#set sectorlst = ( ptfire-wild-us ptfire-rx-us ptfire-canada )
#set sectorlst = ( ptfire-wild-us )
set sectorlst = ( ptfire-mx )
set month = ( 'apr' 'may' 'jun' 'jul' 'aug' 'sep' 'oct' )

setenv WRKDIR $cwd

setenv OUTDIR $OUT_ROOT/ember_2024/gen_reports_v2
if ( ! -e $OUTDIR ) mkdir -p $OUTDIR

setenv rptyp temporal
#setenv rptyp annual

setenv PROMPTFLAG N


setenv COSTCY "${GE_DAT}/costcy_for_2017platform_08mar2023_nf_v8.txt"

foreach sector ( $sectorlst )

  setenv PGMAT $IMD_ROOT/$sector/pgmat_${sector}_36US3_ember_2024.ncf

  if ( $sector == 'ptfire-mx' ) then
    #setenv REPCONFIG $WRKDIR/reconfig_point_temporal_scc_ptfire-mx.txt
    setenv REPCONFIG $WRKDIR/reconfig_point_temporal_scc_gridding_ptfire-mx.txt
  else
    #setenv REPCONFIG $WRKDIR/reconfig_point_temporal_scc.txt
    setenv REPCONFIG $WRKDIR/reconfig_point_temporal_scc_gridding.txt
  endif

  foreach mon ( $month )

    setenv PNTS  $IMD_ROOT/$sector/pnts_map_${sector}_ember_2024.txt
    setenv PDAY  $IMD_ROOT/$sector/pday_${sector}_${mon}_ember_2024.ncf

    foreach file ( $IMD_ROOT/$sector/ptmp_${sector}_${mon}_ember_2024_*.ncf )
      setenv PTMP $file
      set base=`basename $file`
      setenv REPORT1 $OUTDIR/smkreport_${base}.txt
      $SMOKE_LOCATION/smkreport
    end

  end
end
