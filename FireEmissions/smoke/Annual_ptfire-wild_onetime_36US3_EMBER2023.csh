#!/bin/csh -f
#SBATCH --export=NONE

limit stacksize unlimited

setenv SECTOR "ptfire-wild-us"

if ($?SLURM_SUBMIT_DIR) then
  cd $SLURM_SUBMIT_DIR
endif

## Definitions for case name, directory structures, etc, that are used
#  by every sector in the case
#  Anything defined in directory_definitions can be overridden here
#  if desired
source ./directory_definitions.csh

## Months for emissions processing, and spinup duration
#  In the EPA emissions modeling platforms, the only sectors that use
#    SPINUP_DURATION are biogenics and the final sector merge (Mrggrid).
#  Elsewhere, SPINUP_DURATION = 0, and when Mrggrid runs for spinup days,
#    base year emissions are used for the spinup year for all sectors except
#    biogenics.
#  Effective Jan 2019, SPINUP_DURATION now should work for all months.
#  SPINUP_MONTH_END (new for Jan 2019) specifies whether the last $SPINUP_DURATION
#    days of quarter 2/3/4 should be run at the end of a quarter (Y), or at the start
#    of the next quarter (N). For example, if runningwith SPINUP_DURATION = 10:
#    When N (old behavior), Q1 will include 10 day spinup and end on 3/21; Q2 will
#    cover 3/22 through 6/20. When Y, Q1 will include 10 day spinup and end on 3/31
#    (including all of March), remaining quarters will function as if spinup = 0.
setenv RUN_MONTHS "4 5 6 7 8 9 10"
setenv SPINUP_DURATION "0"
setenv SPINUP_MONTH_END "Y"

## Emissions modeling year
#  (i.e. meteorological year, not necessarily the inventory year"
setenv BASE_YEAR "2024"
setenv EPI_STDATE_TIME "${BASE_YEAR}-01-01 00:00:00.0"
setenv EPI_ENDATE_TIME "${BASE_YEAR}-12-31 23:59:00.0"

## Inventory case name, if inventories are coming from a different case (they usually aren't)
#  CASEINPUTS is defined in directory_definitions and optionally overridden here
#setenv INVENTORY_CASE "2011ek_cb6v2_v6_11g"
#setenv CASEINPUTS "$INSTALL_DIR/$INVENTORY_CASE/inputs"


## Inputs for all sectors
setenv GRIDDESC "${GE_DAT}/gridding/griddesc_lambertonly_18jan2019_v7.txt"
setenv COSTCY "${GE_DAT}/costcy_for_2017platform_08mar2023_nf_v8.txt"
setenv SCCDESC "${GE_DAT}/smkreport/sccdesc_2014platform_08mar2023_nf_v7.txt"
setenv ATREF "${GE_DAT}/temporal/amptref_general_2017platform_02mar2023_nf_v13"
setenv SRGDESC "${GE_DAT}/gridding/srgdesc_CONUS12_2020NEI_03mar2023_10mar2023_nf_v1.txt"
setenv ARTOPNT "${GE_DAT}/artopnt_2002detroit_20aug2019_v2.txt"
setenv HOLIDAYS "${GE_DAT}/temporal/holidays_01feb2021_v3.txt"
setenv PELVCONFIG "${GE_DAT}/point/pelvconfig_elevate_everything_17apr2020_v0.txt"
setenv ORISDESC "${GE_DAT}/smkreport/orisdesc_04dec2006_v0.txt"
setenv PSTK "${GE_DAT}/point/pstk_13nov2018_v1.txt"
setenv AGREF "${GE_DAT}/gridding/agref_us_2020platform_10mar2023_nf_v2.txt"
#setenv PTREF "${GE_DAT}/temporal/amptref_general_2017platform_02mar2023_nf_v13"
setenv MTREF "${GE_DAT}/temporal/mtref_onroad_MOVES3_2017NEI_08nov2021_v2"
setenv NAICSDESC "${GE_DAT}/smkreport/naicsdesc_20220222_22feb2022_v0.txt"
#setenv SRGPRO "${GE_DAT}/gridding/surrogates/CONUS12_2020NEI_03mar2023/USA_100_NOFILL.txt"
setenv SRGPRO "/proj/ie/proj/SMOKE/htran/Emission_Modeling_Platform/2022v1/ge_dat/gridding/surrogates/CONUS36_2020NEI_25may2023/2022_oilgas/USA_100_NOFILL.txt"
setenv EFTABLES "${CASEINPUTS}/onroad/eftables/rateperdistance_smoke_nata_20210219_2019-20211020_10003_1.csv"
setenv MTPRO_MONTHLY "${GE_DAT}/temporal/mtpro_monthly_MOVES_03aug2016_v1"
setenv ATPRO_MONTHLY "${GE_DAT}/temporal/amptpro_general_2011platform_tpro_monthly_6nov2014_27oct2022_nf_v11"
setenv ATPRO_WEEKLY "${GE_DAT}/temporal/amptpro_general_2011platform_tpro_weekly_6nov2014_09sep2016_v2"
setenv ATPRO_HOURLY "${GE_DAT}/temporal/amptpro_general_2011platform_tpro_hourly_6nov2014_18apr2022_v11"
setenv PTPRO_WEEKLY "${GE_DAT}/temporal/amptpro_general_2011platform_tpro_weekly_6nov2014_09sep2016_v2"
setenv PTPRO_MONTHLY "${GE_DAT}/temporal/amptpro_general_2011platform_tpro_monthly_6nov2014_12oct2021_v9"
setenv PTPRO_HOURLY "${GE_DAT}/temporal/amptpro_general_2011platform_tpro_hourly_6nov2014_18apr2022_v11"
setenv MTPRO_WEEKLY "${GE_DAT}/temporal/mtpro_weekly_MOVES_2014v2_25feb2021_nf_v3"
setenv MTPRO_HOURLY "${GE_DAT}/temporal/mtpro_hourly_MOVES_2014v2_25feb2021_nf_v3"
setenv MRGDATE_FILES "${INSTALL_DIR}/smoke5.0/scripts/smk_dates/2020/smk_merge_dates_201912.txt"
setenv GSCNV "${GE_DAT}/speciation/gscnv_SPECIATE_5_2_fromS2S_20221213_19dec2022_nf_v1.txt"
setenv ATPRO_HOURLY_NCF "${GE_DAT}/temporal/Gentpro_TPRO_HOUR_HOURLY_BASH_NH3.agNH3_bash_2020NEI_12US1.ncf"


## Inputs specific to this sector and/or job
setenv REPCONFIG_INV "${GE_DAT}/smkreport/repconfig/repconfig_area_inv_2016beta_15nov2021_nf_v3.txt"
setenv REPCONFIG_GRID "${GE_DAT}/smkreport/repconfig/repconfig_area_inv_grid_2016beta_15nov2021_nf_v2.txt"
setenv GSPROTMP_A "${GE_DAT}/speciation/gspro_standard/gspro_static_cmaq_21feb2012_v13.txt"
setenv GSPROTMP_B "${GE_DAT}/speciation/gspro_standard/gspro_sulf_29jun2007_v1.txt"
setenv GSREFTMP_A "${GE_DAT}/speciation/gsref_static_cap_pf4_2014v1_platform_23jan2017_v0.txt"
setenv GSREFTMP_C "${GE_DAT}/speciation/gsref_static_nox_hono_pf4_2014v1_platform_02aug2022_v2.txt"
setenv GSREFTMP_B "${GE_DAT}/speciation/gsref_sulf__2014v1_platform_23jan2017_v0.txt"
setenv GSPROTMP_I "${GE_DAT}/speciation/gspro_standard/gspro_speciated_voc_cb6cmaq_21jul2017_v1.txt"
setenv GSPROTMP_G "${GE_DAT}/speciation/gspro_standard/gspro_nox_hono_pf4_06aug2008_v0.txt"
setenv GSPROTMP_F "${GE_DAT}/speciation/gspro_standard/gspro_haps_2014v1_cb6cmaq_11oct2016_v0.txt"
setenv GSREFTMP_K "${GE_DAT}/speciation/gsref_alaska_onroad_26sep2017_nf_v2.txt"
setenv GSREFTMP_X1 "${GE_DAT}/speciation/gsref_metals_chromium_stationary_2014v1_platform_17jan2017_v0.txt"
setenv GSREFTMP_X5 "${GE_DAT}/speciation/gsref_hg_2017platform_10mar2023_nf_v4.txt"
setenv GSREFTMP_X4 "${GE_DAT}/speciation/gsref_dieselpm_2014v1_platform_15apr2020_nf_v2.txt"
setenv GSREFTMP_X1A "${GE_DAT}/speciation/gsref_minnesota_metals_05dec2017_v0.txt"
setenv GSREFTMP_X5B "${GE_DAT}/speciation/gsref_hg_2017platform_geothermal_06apr2020_v0.txt"
setenv GSPROTMP_C "${GE_DAT}/speciation/gspro_standard/gspro_PM2_5_AE6_Spec_5_2_S2S_20221213_15dec2022_v0.txt"
setenv GSPROTMP_E "${GE_DAT}/speciation/gspro_standard/gspro_CB6R3_AE7_integrate_Spec_5_2_S2S_20221213_01mar2023_nf_v1.txt"
setenv GSPROTMP_E1 "${GE_DAT}/speciation/gspro_standard/gspro_CB6R3_AE7_integrate_tracer_Spec_5_2_S2S_20221213_15dec2022_nf_v1.txt"
setenv GSPROTMP_M "${GE_DAT}/speciation/gspro_standard/gspro_NMOG_HAPs_only_22dec2022_v1.txt"
setenv GSREFTMP_E "${GE_DAT}/speciation/gsref_pm25_2018_platform_08mar2023_nf_v8.txt"
setenv GSREFTMP_F "${GE_DAT}/speciation/gsref_voc_2018_platform_08mar2023_nf_v8.txt"
setenv GSREFTMP_H "${GE_DAT}/speciation/gsref_nonhapvoc_2018_platform_08mar2023_nf_v6.txt"
setenv GSREFTMP_F1 "${GE_DAT}/speciation/gsref_voc_WR711_2020_oilgas_basin_specific_ramboll_26oct2022_v0.txt"
setenv GSREFTMP_F2 "${GE_DAT}/speciation/gsref_voc_WR711_2020_oilgas_combo_ERG_26oct2022_v0.txt"
setenv GSREFTMP_H1 "${GE_DAT}/speciation/gsref_nonhapvoc_WR711_2020_oilgas_basin_specific_ramboll_26oct2022_v0.txt"
setenv GSREFTMP_H2 "${GE_DAT}/speciation/gsref_nonhapvoc_WR711_2020_oilgas_combo_ERG_26oct2022_v0.txt"
setenv PELVCONFIG "${GE_DAT}/point/pelvconfig_ptfire_inline_pf31_03may2011_v1.txt"
#setenv NHAPEXCLUDE "${GE_DAT}/nhapexclude/nhapexclude_2020ha_ptfire_21mar2023_v0.txt"
setenv NHAPEXCLUDE "/proj/ie/proj/GSA-EMBER/BlueSky/ember_2024/smoke/scripts/nhapexclude_ember_2024.txt"
setenv REPCONFIG_INV "${GE_DAT}/smkreport/repconfig/repconfig_point_inv_2016beta_15nov2021_nf_v2.txt"
setenv REPCONFIG_TEMP "${GE_DAT}/smkreport/repconfig/repconfig_point_temporal_2016beta_15nov2021_nf_v1.txt"
setenv REPCONFIG_INV2 "${GE_DAT}/smkreport/repconfig/repconfig_point_inv_nonhapvocprof_2016beta_15nov2021_nf_v1.txt"
setenv REPCONFIG_GRID "${GE_DAT}/smkreport/repconfig/repconfig_point_invgrid_2011platform_11aug2014_v0.txt"
setenv EMISDAY_Z "${CASEINPUTS}/ptfire-wild/ptday_2020_allfires_ff10_prevdec_21mar2023_nf_v3"
setenv REPCONFIG_INV3 "${GE_DAT}/smkreport/repconfig/repconfig_point_inv_vocprof_2016beta_15nov2021_nf_v1.txt"
setenv EMISDAY_Z1 "${CASEINPUTS}/ptfire-wild/ptday_2020_allfires_haps_ff10_prevdec_21mar2023_nf_v3"
#setenv INVTABLE "${GE_DAT}/speciation/invtable_standard/invtable_2014platform_integrate_21dec2018_v3.txt"
setenv GSPROTMP_D "${GE_DAT}/speciation/gspro_standard/gspro_CB6R3_AE7_criteria_Spec_5_2_S2S_20221213_15dec2022_v0.txt"
setenv GSPROTMP_D1 "${GE_DAT}/speciation/gspro_standard/gspro_CB6R3_AE7_criteria_tracer_Spec_5_2_S2S_20221213_01feb2023_nf_v2.txt"
setenv INVTABLE "${GE_DAT}/speciation/invtable_hapcap/invtable_2017_NATA_CMAQ_22feb2023_nf_v7.txt"
#setenv INVTABLE "/work/EMIS/em_v9/hapcap/2020ha_cb6_20k/inputs/../../../ge_dat/invtable_2017_NATA_CMAQ_22feb2023_nf_v7.txt" ## Inventory Table - NBAFM integration

setenv PTREF "/proj/ie/proj/GSA-EMBER/BlueSky/from_EPA/ember_package/smoke/ptref_ptfire_rx_lowactivity_21mar2023_v5"

setenv EMISINV_A "/proj/ie/proj/GSA-EMBER/BlueSky/ember_2024/smoke/inputs/ptinv_sf2_2024_ember_us_wf_ff10.csv"
setenv EMISINV_B "/proj/ie/proj/GSA-EMBER/BlueSky/ember_2024/smoke/inputs/ptinv_sf2_2024_ember_us_haps_wf_ff10.csv"
#setenv EMISDAY_A "/proj/ie/proj/GSA-EMBER/BlueSky/ember_2024/smoke/inputs/ptday_sf2_2024_ember_us_wf_ff10.csv"
#setenv EMISDAY_B "/proj/ie/proj/GSA-EMBER/BlueSky/ember_2024/smoke/inputs/ptday_sf2_2024_ember_us_haps_wf_ff10.csv"

# Uncomment inputs for HAP-CAP processing
#setenv GSPROTMP_D1 "${GE_DAT}/speciation/gspro_standard/gspro_CB6R3_AE7_criteria_tracer_Spec_5_2_S2S_20221213_01feb2023_v1.txt"
#setenv GSPROTMP_D "${GE_DAT}/speciation/gspro_standard/gspro_CB6R3_AE7_nointegrate_Spec_5_2_S2S_20221213_01mar2023_nf_v1.txt"
#setenv GSPROTMP_X1 "${GE_DAT}/speciation/gspro_hapcap/gspro_hapmetals_05dec2017_nf_v2.txt"
#setenv GSPROTMP_X2 "${GE_DAT}/speciation/gspro_hapcap/gspro_chromium_05dec2017_nf_v2.txt"
#setenv GSPROTMP_X3 "${GE_DAT}/speciation/gspro_hapcap/gspro_hg_2017platform_16apr2020_nf_v1.txt"
#setenv GSPROTMP_X4 "${GE_DAT}/speciation/gspro_hapcap/gspro_pahs_2014v1_nata_02apr2020_nf_v1.txt"
#setenv GSPROTMP_X5 "${GE_DAT}/speciation/gspro_hapcap/gspro_diesel_pm_2014v1_nata_21oct2016_nf_v1.txt"


## Parameters for all sectors
setenv PLATFORM "v9" ## Platform name
setenv SPC "$EMF_SPC" ## Speciation type name
setenv FILL_ANNUAL "N" ## Fill annual values
setenv SMKINVEN_FORMULA "PMC=PM10-PM2_5" ## Formula for Smkinven
setenv SMK_DEFAULT_SRGID "100" ## Default surrogate code
setenv REPORT_DEFAULTS "Y" ## Report default profiles used
setenv SMK_AVEDAY_YN "N" ## Use average day emissions
setenv SMK_MAXWARNING "10" ## Maximum warnings printed
setenv SMK_MAXERROR "10000" ## Maximum errors printed
setenv FULLSCC_ONLY "Y" ## Match full SCCs
setenv RUN_HOLIDAYS "Y" ## Run holidays
setenv L_TYPE "mwdss" ## Temporal type
setenv M_TYPE "mwdss" ## Merge type
setenv RAW_DUP_CHECK "N" ## Check for duplicate sources
setenv SMK_SPECELEV_YN "Y" ## Laypoint uses Elevpoint to set sources for plume rise calc
setenv SMK_PING_METHOD "0" ## Plume-in-grid method
setenv INLINE_MODE "only" ## Run in "inline" mode
setenv RUN_PYTHON_ANNUAL "Y" ## Run script for Smkmerge annual totals
setenv NO_SPC_ZERO_EMIS "Y" ## Don't speciate zero emission SCCs
setenv WRF_VERSION "4" ## WRF version (affects afdust adjustments)
setenv DEFAULT_CONV_FAC_ERROR "Y" ## Error if profile missing from GSCNV
setenv OUTPUT_FORMAT "$EMF_AQM" ## Model output format
setenv SMKMERGE_CUSTOM_OUTPUT "Y" ## Custom merge output
setenv MRG_REPSTA_YN "N" ## Output state totals
setenv IOAPI_ISPH "20" ## I/O API Sphere type
setenv POLLUTANT_CONVERSION "Y" ## Use pollutant conversion
setenv RENORM_TPROF "Y" ## Renormalize temporal profiles
setenv OUTZONE "0" ## Output time zone
setenv MRG_REPCNY_YN "Y" ## Output county totals
setenv WEST_HSPHERE "Y" ## Western hemisphere?
setenv MRG_MARKETPEN_YN "N" ## Include market penetration
setenv ELEVPOINT_DAILY "Y" ## Ptfire Inline
setenv MET_ASM "N" ## Path, Met data root
setenv WRITE_ANN_ZERO "Y" ## Write zero emissions
setenv DAY_SPECIFIC_YN "Y" ## Use day-specific emission
setenv CHECK_STACKS_YN "N" ## Check stack parameters for missing
setenv FIRE_PLUME_YN "Y" ## Fire-specific plume rise calculations
setenv HOURLY_FIRE_YN "Y" ## Use hourly plume rise data
setenv ZIPOUT "Y" ## Zip POUT and INLN output files
setenv FIRE_BOTTOM_LAYER_1_YN "Y" ## Use corrected layer algorithm for fires


## Parameters specific to this sector and/or job
setenv L_TYPE "all" ## Temporal type
setenv M_TYPE "all" ## Merge type
setenv NONHAP_TYPE "VOC" ## Nonhap Type
setenv SMK_PROCESS_HAPS "PARTIAL" ## Use NHAPEXCLUDE file
setenv RENORM_TPROF "N" ## Renormalize temporal profiles

$RUNSCRIPTS/emf/smk_pt_annual_onetime_emf.csh $REGION_ABBREV $REGION_IOAPI_GRIDNAME onetime
