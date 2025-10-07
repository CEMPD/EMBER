#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

if [ $# -ne 4 ]; then
  echo "Concatenates the 25 hours from 0 to 0 from NACC output 12Z to 12Z"
  echo "$0 DAY1 DAY2 OUTPATH YYYYJJJ"
  echo ""
  echo "  DAY1 : path to the first day file"
  echo "  DAY2 : path to the second day file"
  echo "  OUTPATH : path for concatenated file"
  echo "  YYYYJJJ : Julian date for start of concatenated file"
  exit 1
fi

#set ncrcat=/nas/longleaf/rhel8/apps/nco/4.8.1/bin/ncatted # No longer available since switching to RELH 9

DAY1=${1?Required DAY1 input file path}
DAY2=${2?Required DAY2 input file path}
OUTFILE=${3?Required output file path}
JDATE=${4?Required JDATE YYYYJJJ}

# Concatenate the NetCDF files using ncrcat
/nas/longleaf/home/tranhuy/software/pkg/miniconda3/bin/ncrcat -O --hst -d TSTEP,12,36 "$DAY1" "$DAY2" "$OUTFILE"

# Set attributes in the output NetCDF file
/nas/longleaf/home/tranhuy/software/pkg/miniconda3/bin/ncatted --hst -a SDATE,global,o,i,"$JDATE" -a STIME,global,o,i,0 "$OUTFILE"

# Modify Grid name GDNAM
/nas/longleaf/home/tranhuy/software/pkg/miniconda3/bin/ncatted -a GDNAM,global,o,c,"36US3" "$OUTFILE"

# Set HISTORY attribute to log the command used
/nas/longleaf/home/tranhuy/software/pkg/miniconda3/bin/ncatted --hst -a HISTORY,global,o,c,"Concatenated using $0 on $(date)" "$OUTFILE"
