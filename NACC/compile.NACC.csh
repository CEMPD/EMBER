#!/bin/csh

#setenv comptyp "serial"
 setenv comptyp "parallel"
 
 if ( $comptyp == "serial" ) then

     setenv NACC_HOME /proj/ie/proj/GSA-EMBER/NACC/serial/src # serial
     setenv BIN  Linux2_x86_64ifx
#    module load gcc/11.2.0
#    setenv BIN  Linux2_x86_64dbg
#    setenv BIN  Linux2_x86_64_nacc
#    setenv BIN  Linux2_x86_64
#    setenv BIN  Linux2_x86_64large
     source /proj/ie/proj/GSA-EMBER/NACC/lib/ioapi-3.2-large/IOAPI.config.csh $BIN # source IOAPI config to get same variable $BIN and libraries
     
 else if ( $comptyp == "parallel" ) then

     setenv NACC_HOME /proj/ie/proj/GSA-EMBER/NACC/parallel/src # parallel
#    setenv BIN Linux2_x86_64mpiifort
#    source /proj/ie/proj/GSA-EMBER/NACC/lib/ioapi-3.2/IOAPI.config.csh $BIN # source IOAPI config to get same variable $BIN and libraries
     setenv BIN Linux2_x86_64ifx
     source /proj/ie/proj/GSA-EMBER/NACC/lib/ioapi-3.2-large/IOAPI.config.csh $BIN # source IOAPI config to get same variable $BIN and libraries
     module load openmpi intel/2024.1.0
     setenv MPIDIR `which mpiifort | xargs dirname | xargs dirname`
     setenv IFXDIR `which ifort | xargs dirname | xargs dirname`
     setenv IFORTLIB ${IFXDIR}/lib
     setenv COMPLIB  ${MPIDIR}/lib
     setenv MPI      $MPIDIR/mpi

 endif
 
 #> source IOAPI config to get same variable $BIN and libraries that were used to compile IOAPI

 setenv IOAPI  /proj/ie/proj/GSA-EMBER/NACC/lib/ioapi-3.2-large/Linux2_x86_64ifx # $IOAPI_HOME/$BIN
 setenv WRKDIR $cwd

 cd $NACC_HOME

 unlink Makefile
#ln -s Makefile.$BIN Makefile
 ln -s Makefile.Linux2_x86_64mpiifort Makefile

#echo $NCFLIBS

 make clean
 if ( $comptyp == "serial" ) then
 make all >& $WRKDIR/LOG.compile.$comptyp
 else if ( $comptyp == "parallel" ) then
 make -j 4 all >& $WRKDIR/LOG.compile.$comptyp
 endif

