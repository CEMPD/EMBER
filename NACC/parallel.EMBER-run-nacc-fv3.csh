#!/bin/csh
#SBATCH -J NACC
#SBATCH -o outlog.NACC.%j
#SBATCH -e error.NACC.%j
#SBATCH --mail-type=ALL
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=24
#SBATCH --nodelist=c1306ie02
##SBATCH --nodelist=c1306ie06
##SBATCH --constraint=rhel7
#SBATCH --time=24:00:00
#SBATCH --partition=cempd
##SBATCH -A rc_sarav_pi
##SBATCH --mem-per-cpu=4800
#SBATCH --mem=0
#SBATCH --mail-type=ALL,END,FAIL,TIME_LIMIT_80
#SBATCH --mail-user=tnquanghuy@gmail.com

unlimit datasize
unlimit memoryuse
unlimit stacksize

#setenv BIN Linux2_x86_64mpiifort
setenv BIN Linux2_x86_64ifx

set IOAPI = /proj/ie/proj/GSA-EMBER/NACC/lib/ioapi-3.2-large
#source ${IOAPI}/IOAPI.config.csh $BIN

module load openmpi intel/2024.1.0

# Set date range
setenv SDATE 20210801
setenv EDATE 20211001

# Convert to Julian dates
set SJJJ = `$IOAPI/${BIN}/greg2jul $SDATE`
set EJJJ = `$IOAPI/${BIN}/greg2jul $EDATE`

set jday   = $SJJJ
set bnnodeid = 6     # starting number $N of node to be run on c1306ie0$N
set ednodeid = 7     # endding number $N of node to be run on c1306ie0$N
set nodeid = $bnnodeid

while ( $jday <= $EJJJ )
  # Convert Julian day to Gregorian date
  set CYYYYMMDD = `$IOAPI/${BIN}/jul2greg $jday`
  set TODAY = `date -d "$CYYYYMMDD" +%Y-%m-%d`
  set NYYYYMMDD = `$IOAPI/${BIN}/datshift $CYYYYMMDD 1`
  set TMROW = `date -d "$NYYYYMMDD" +%Y-%m-%d`

  # Extract the year from the date
  set CYYYY = `echo $CYYYYMMDD | cut -c1-4`
  set CMM   = `echo $CYYYYMMDD | cut -c5-6`
  set CYYMMDD = `echo $CYYYYMMDD | cut -c3-8`

  set APPL=aqm.t12z
  set DataDir=/proj/ie/proj/GSA-EMBER/NACC/data
  set InMetDir=/proj/ie/proj/GSA-EMBER/NACC/data/inputs/$CYYYYMMDD
  set InGeoDir=/proj/ie/proj/GSA-EMBER/NACC/data/inputs
  set InVIIRSDir=$InMetDir
  set OutDir=/proj/ie/proj/GSA-EMBER/NACC/data/outputs/$CYYYYMMDD

  set NTIMES=24
  set NODES=1

  if ( ! -s $InMetDir ) then
    echo "No such input directory $InMetDir"
    exit 1
  endif

  if ( ! -s $InGeoDir ) then
    echo "No such input directory $InGeoDir"
    exit 1
  endif

  if ( ! -d $OutDir ) then
    echo "No such output directory...will try to create one"
    mkdir -p $OutDir
    if ( $? != 0 ) then
      echo "Failed to make output directory, $OutDir"
      exit 1
    endif
  endif

# set ProgDir=/proj/ie/proj/GSA-EMBER/NACC/develop/parallel/src
  set ProgDir=/proj/ie/proj/GSA-EMBER/NACC/parallel/src
  @ NPCOL  =  6; @ NPROW = 4
  @ NPROCS = $NPCOL * $NPROW
  setenv NPCOL_NPROW "$NPCOL $NPROW"

  if ( ! -d $ProgDir ) then
    echo "No such program directory $ProgDir"
    exit 1
  endif

  cd $OutDir

# setenv GRIDDESC $OutDir/GRIDDESC

cat>namelist.mcip<<!
&FILENAMES
  file_gd    = 'GRIDDESC'
  file_mm    = '$InMetDir/gfs.t12z.atmf','.nc'
  file_sfc   = '$InMetDir/gfs.t12z.sfcf','.nc'
  file_geo   = '$InGeoDir/gfs.t12z.geo.${CMM}.canopy.nc'
  ioform     =  1
 &END

 &USERDEFS
  inmetmodel =  3
  dx_out      =  36000
  dy_out      =  36000
  met_cen_lat_in =  0.0
  met_cen_lon_in =  0.0
  lpv        =  1
  lwout      =  1
  luvbout    =  1
  ifdiag_pbl = .FALSE.
  ifviirs_gvf = .FALSE.
  ifviirs_lai = .FALSE.
  iffengsha_dust = .FALSE. 
  ifbioseason = .FALSE.
  ifcanopy    = .FALSE.
  mcip_start = "${TODAY}-12:00:00.0000"
  mcip_end   = "${TMROW}-11:00:00.0000"
  intvl      =  60
  coordnam   = "LAM_40N97W"
  grdnam     = "us36k_172x148"
  ctmlays    =  1.000000, 0.997500, 0.995000, 0.990000, 0.985000,
                0.980000, 0.970000, 0.960000, 0.950000, 0.940000,
	       	0.930000, 0.920000, 0.910000, 0.900000, 0.880000,
	       	0.860000, 0.840000, 0.820000, 0.800000, 0.770000,
	       	0.740000, 0.700000, 0.650000, 0.600000, 0.550000,
		0.500000, 0.450000, 0.400000, 0.350000, 0.300000,
		0.250000, 0.200000, 0.150000, 0.100000, 0.050000, 0.000000
  cutlay_collapx = 22
  btrim      =  -1
  lprt_col   =  0
  lprt_row   =  0
  ntimes     =  $NTIMES
  projparm = 2., 33.,45., -97., -97., 40.
  domains = -2952000., -2772000., 36000., 36000., 172, 148
 &END

 &WINDOWDEFS
  x0         =  1
  y0         =  1
  ncolsin    =  172
  nrowsin    =  148
 &END
!

# unlink namelist.mcip
# ln -s  namelist.${CYYYYMMDD}.mcip namelist.mcip

  setenv IOAPI_CHECK_HEADERS T
  setenv EXECUTION_ID "NACC_`id -u -n`_`date -u +%Y%m%d_%H%M%S_%N`"
  setenv GRID_NAME "us36k_172x148"

  setenv GRID_BDY_2D ${APPL}.grdbdy2d.${CYYYYMMDD}.ncf
  setenv GRID_CRO_2D ${APPL}.grdcro2d.${CYYYYMMDD}.ncf
  setenv GRID_DOT_2D ${APPL}.grddot2d.${CYYYYMMDD}.ncf
  setenv MET_BDY_3D  ${APPL}.metbdy3d.${CYYYYMMDD}.ncf
  setenv MET_CRO_2D  ${APPL}.metcro2d.${CYYYYMMDD}.ncf
  setenv MET_CRO_3D  ${APPL}.metcro3d.${CYYYYMMDD}.ncf
  setenv MET_DOT_3D  ${APPL}.metdot3d.${CYYYYMMDD}.ncf
  setenv LUFRAC_CRO  ${APPL}.lufraccro.${CYYYYMMDD}.ncf
  setenv SOI_CRO     ${APPL}.soicro.${CYYYYMMDD}.ncf
  setenv MOSAIC_CRO  ${APPL}.mosaiccro.${CYYYYMMDD}.ncf

  rm -f *.${CYYYYMMDD}.ncf

# echo `which mpirun`
if ( $nodeid == 7 ) then
sbatch -J NACC${CYYMMDD} --nodelist=c1803ie07 --nodes=1 --ntasks-per-node=$NPROCS -p cempd --mem=0 -t 24:00:00 --wrap="cd $OutDir; /usr/bin/time -p mpirun -np $NPROCS ${ProgDir}/mcip.exe"
else
sbatch -J NACC${CYYMMDD} --nodelist=c1306ie0$nodeid --nodes=1 --ntasks-per-node=$NPROCS -p cempd --mem=0 -t 24:00:00 --wrap="cd $OutDir; /usr/bin/time -p mpirun -np $NPROCS ${ProgDir}/mcip.exe"
endif

@ jday = $jday + 1
if ( $nodeid == $ednodeid ) then
@ nodeid = $bnnodeid
else
@ nodeid = $nodeid + 1
endif
end
