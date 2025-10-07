#!/bin/csh -f

setenv AWS_REGION "us-east-1"

setenv IOAPI /proj/ie/proj/SMOKE/htran/ioapi-3.2.github/Linux2_x86_64ifx

set aws = /nas/longleaf/rhel8/apps/aws/2.15.19/bin/aws

##> Area sources

# Set date range
setenv SDATE 20210801
setenv EDATE 20210801
#setenv SDATE 20230331
#setenv EDATE 20230331

# Convert to Julian dates
set SJJJ = `$IOAPI/greg2jul $SDATE`
set EJJJ = `$IOAPI/greg2jul $EDATE`

set jday = $SJJJ

while ( $jday <= $EJJJ )
  # Convert Julian day to Gregorian date
  set CYYYYMMDD = `$IOAPI/jul2greg $jday`

  # Extract the year from the date
  set CYYYY = `echo $CYYYYMMDD | cut -c1-4`

  # Set the disk path and create the directory
  setenv DISK /proj/ie/proj/GSA-EMBER/NACC/data/inputs/$CYYYYMMDD
  mkdir -p $DISK

  foreach ityp ( atmf sfcf )
  foreach ihr  (`seq -f "%03g" 0 25`) # loop between 000 - 025

    # Define file name and url
    set  ifile = gfs.t12z.${ityp}${ihr}.nc
#   set  jfile = gfs.t12z.${ityp}.${CYYYYMMDD}_${ihr}.nc
    set  iurl  = "s3://noaa-oar-arl-nacc-pds/inputs/${CYYYYMMDD}"

    if ( ! -e $DISK/$ifile ) then # if this file has not been downloaded earlier
      # Use AWS CLI to copy data from S3
      echo "Downloading $ifile"
      $aws --no-sign-request s3 cp --recursive --exclude "*" --include ${ifile} $iurl /$DISK

      # Rename files in the destination directory
#     mv $DISK/$ifile $DISK/$jfile
    endif

  end
  end

  # Increment the Julian day
  @ jday = $jday + 1
end
