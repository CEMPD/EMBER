#!/bin/csh

# This script defines case names, directory structures and locations,
#   and defines other environment variables that are used by all sectors
#   and should not need to be changed on a sector-by-sector basis.
# All sector scripts call this "assigns" script at the very top.

# Eventually, this script will also check that some or all SMOKE inputs
#   are actually in the directories as defined by this script. 
#   This functionality is a future feature.

# Root directory where you unzipped all .zips
setenv INSTALL_DIR "/proj/ie/proj/EDF-OG/SMOKE/platform_2020ha2"

# Full path of MCIP (meteorology) files
# Prior platforms automatically appended $GRID/mcip_out onto the MET_ROOT; however,
#   starting with this platform, MET_ROOT should be the FULL path, including mcip_out
#   if that's where the MCIP happens to be.
#setenv MET_ROOT "${INSTALL_DIR}/met_for_emissions/12US1/METCRO2D"
#setenv MET_ROOT "/proj/ie/proj/EDF-OG/CMAQ/CMAQv5.4/data/CMAQ_Modeling_Platform_2018/2018_12US1/met"
setenv MET_ROOT /proj/ie/proj/EDF-OG/SMOKE/platform_2020ha2/mcip_for_beis4

# Location of full layered METCRO3D files if different than MET_ROOT directory; 
# These are only needed if running fires with 3-D plume rise for CAMx modeling;
#   you may be able to set this equal to $MET_ROOT
setenv MET_ROOT_3D /proj/ie/proj/EDF-OG/SMOKE/platform_2020ha2 #"/work/EMIS/met/from_Ramboll/2017NEI_12US1"

if ( $?SECTOR ) then
  if ($SECTOR == ptfire3D || $SECTOR == ptfire_othna3D || $SECTOR == ptagfire3D) setenv MET_ROOT $MET_ROOT_3D
endif

# Case name
setenv CASE "ember_2024"

## Grid name
setenv REGION "Continental US 36km"
setenv REGION_ABBREV "36US3"
setenv REGION_IOAPI_GRIDNAME "36US3"

## Speciation mechanism name
setenv EMF_SPC "cmaq_cb6ae7"

## Location of SMOKE executables
#  If SMOKE_LOCATION definition is commented out, scripts use default location, 
#  which on EPA systems is $INSTALL_DIR/smoke4.7/Linux2_x86_64ifort
#  Use this parameter to optionally override the default executable location
setenv BIN Linux2_x86_64ifort_static
#setenv BIN Linux2_x86_64
#setenv SMOKE_LOCATION $INSTALL_DIR/smoke4.7/Linux2_x86_64ifort
#setenv SMOKE_LOCATION /proj/ie/proj/SMOKE/htran/SMOKE_DEV/Linux2_x86_64ifort.no_debug.tmpbeis4_orig.chkgrid_orig
#setenv SMOKE_LOCATION /proj/ie/proj/SMOKE/htran/SMOKE_DEV/Linux2_x86_64ifort.no_debug.tmpbeis4_simplified.chkgrid_orig
#setenv SMOKE_LOCATION /proj/ie/proj/SMOKE/htran/SMOKE_DEV/Linux2_x86_64ifort.no_debug.tmpbeis4_carlie.chkgrid_orig
#setenv SMOKE_LOCATION /proj/ie/proj/SMOKE/htran/SMOKE_DEV/Linux2_x86_64ifort.no_debug.tmpbeis4_master.chkgrid_orig
#setenv SMOKE_LOCATION /proj/ie/proj/SMOKE/htran/SMOKE_DEV/Linux2_x86_64ifort.check_bounds_flag.tmpbeis4_orig.chkgrid_orig
setenv SMOKE_LOCATION /proj/ie/proj/SMOKE/htran/SMOKE_INSTALL/$BIN
#setenv SMOKE_LOCATION /proj/ie/proj/SMOKE/htran/SMOKE_DEV/Linux2_x86_64ifx.check_bounds_flag.tmpbeis4_orig.chkgrid_orig
#setenv SMOKE_LOCATION $SMKDEV/training_20231003/smoke5.0/Linux2_x86_64ifort
#setenv SMOKE_LOCATION $SMKDEV/training_20231003/traning.smoke5.0/Linux2_x86_64ifort

## Location of I/O API utilities, such as juldate and m3xtract
#  If IOAPI_LOCATION definition is commented out, scripts use default location,
#  which on EPA systems is $INSTALL_DIR/ioapi
#  Use this parameter to optionally override the default executable location
#setenv IOAPI_LOCATION $INSTALL_DIR/ioapi
 setenv IOAPI_LOCATION /proj/ie/proj/SMOKE/htran/ioapi-3.2.github/$BIN

## SMOKE version - leave this alone, even if not using SMOKE 4.7
## SMOKE 4.7 or newer is required for this emissions platform, but
#  if not using SMOKE 4.7, use SMOKE_LOCATION parameter above 
#  to define the location of the SMOKE executables; do not change
#  MODEL_LABEL because this is also used to reference the run scripts
#  in some helper scripts
setenv MODEL_LABEL "SMOKE5.0"

## Defines the SMOKE input/output directory structure
setenv PROJECT "$CASE"
setenv OUT_ROOT "/work/users/t/r/tranhuy"
setenv PROJECT_ROOT "/proj/ie/proj/GSA-EMBER/BlueSky/ember_2024/smoke"
setenv IMD_ROOT "/work/users/t/r/tranhuy/ember_2024/smoke/intermed"
setenv DAT_ROOT $PROJECT_ROOT
setenv SMK_HOME "/proj/ie/proj/EDF-OG/SMOKE/platform_2020ha2"
setenv CASEINPUTS "/proj/ie/proj/GSA-EMBER/BlueSky/ember_2024/smoke/inputs"
setenv GE_DAT "/proj/ie/proj/EDF-OG/SMOKE/platform_2020ha2/ge_dat"
setenv CASESCRIPTS "/proj/ie/proj/GSA-EMBER/BlueSky/ember_2024/smoke/scripts"
setenv RUNSCRIPTS "/proj/ie/proj/EDF-OG/SMOKE/platform_2020ha2/smoke5.0/scripts"
setenv RUNSET "$CASESCRIPTS/run_settings.txt"
setenv ASSIGNS_FILE "/proj/ie/proj/EDF-OG/SMOKE/platform_2020ha2/smoke5.0/assigns/ASSIGNS.emf"

## On EPA systems, run scripts interface with the Emissions Modeling Framework (EMF).
#  Setting EMF_CLIENT to "false" is the easiest way to disable this interaction, 
#  allowing these scripts to run on other systems
setenv EMF_CLIENT false

## Other variables related to the EMF; these are not used by SMOKE 
#  but may be required by the scripts to at least exist; leave these alone
setenv EMF_AQM "CMAQ v5.2"
setenv EMF_JOBNAME "Annual_area"
setenv EMF_SCRIPTDIR "${CASESCRIPTS}"
setenv EMF_SCRIPTNAME "${CASESCRIPTS}/${EMF_JOBNAME}.csh"
setenv EMF_LOGNAME "${CASESCRIPTS}/logs/$EMF_SCRIPTNAME.log"
setenv EMF_JOBKEY "28310_1312400444602"
setenv EMF_QUEUE_OPTIONS_C "--mem-per-cpu=20g -n 1 -p compute -A emis --gid=emis-hpc -t 168:00:00"
setenv EMF_LOGGERPYTHONDIR "$EMF_SCRIPTDIR/case_logs_python"
setenv EMF_JOBID "1"
