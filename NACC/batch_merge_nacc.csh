#!/bin/csh

# Set environment variables
setenv IOAPI $SMKDEV/ioapi-3.2.github/Linux2_x86_64ifx
setenv WRKDIR /proj/ie/proj/GSA-EMBER/NACC/data
setenv INPDIR /proj/ie/proj/GSA-EMBER/NACC/data/outputs/EMBER_2022
setenv OUTDIR /proj/ie/proj/GSA-EMBER/NACC/data/outputs/mcip/redo
#setenv INPDIR /proj/ie/proj/GSA-EMBER/s3bucket/NACC_MCIP
#setenv OUTDIR /proj/ie/proj/GSA-EMBER/NACC/data/outputs/mcip_fromEPA

mkdir -p $OUTDIR

# File list
set mrglist = ( metbdy3d metcro3d soicro metcro2d metdot3d ) # List of files to be merged
set renlist = ( grdbdy2d grddot2d grdcro2d lufraccro )       # List of files to be renamed only

# Set date range
setenv SDATE 20220405
setenv EDATE 20220405

# Convert to Julian dates
set SJJJ = `$IOAPI/greg2jul $SDATE`
set EJJJ = `$IOAPI/greg2jul $EDATE`

set jday = $SJJJ

while ( $jday <= $EJJJ ) 
  
  setenv CDATE `$IOAPI/jul2greg $jday`    # Current date, containing data from 12:00 Today to 11:00 Next day
  setenv kday  `$IOAPI/julshift $jday -1`
  setenv PDATE `$IOAPI/jul2greg $kday`    # Previous date, containing data from 12:00 Previous day to 11:00 Today

  foreach ftyp ( $mrglist )

      setenv INFILE1 $INPDIR/$PDATE/aqm.t12z.${ftyp}.${PDATE}.ncf
      setenv INFILE2 $INPDIR/$CDATE/aqm.t12z.${ftyp}.${CDATE}.ncf
#     setenv INFILE1 $INPDIR/aqm.t12z.${ftyp}_${PDATE}.ncf
#     setenv INFILE2 $INPDIR/aqm.t12z.${ftyp}_${CDATE}.ncf

      set UPPCASE = `echo $ftyp | tr '[:lower:]' '[:upper:]'` 
      set OUTFILE = "$OUTDIR/${UPPCASE}_${CDATE}"

#     $WRKDIR/merge_nacc.csh $INFILE1 $INFILE2 $OUTFILE $jday
      $WRKDIR/merge.sh $INFILE1 $INFILE2 $OUTFILE $jday

  end
  
  foreach ftyp ( $renlist )
      setenv INFILE1 $INPDIR/$CDATE/aqm.t12z.${ftyp}.${CDATE}.ncf
#     setenv INFILE1 $INPDIR/aqm.t12z.${ftyp}_${CDATE}.ncf

      set UPPCASE = `echo $ftyp | tr '[:lower:]' '[:upper:]'`  # Fixed variable name
      set OUTFILE = "$OUTDIR/${UPPCASE}_${CDATE}"

      cp $INFILE1 $OUTFILE
  end

  @ jday = $jday + 1

end
