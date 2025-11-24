#!/bin/csh -f
# Prepare the WFIGS perimeters for SF2 modeling

set YYYY = 2024

set ingpkg = WFIGS_Interagency_Perimeters_toDate_15May2025.gpkg

set tbl = wfig_active_perimeters_15May2025

rm -f ${tbl}.*
cp $ingpkg ${tbl}.gpkg

set PROCTBL = 'Y'
set EXTRYR  = 'Y' 

## Process data for entire package
if ( $PROCTBL == 'Y' ) then

    ## Print out column names of ${tbl}.gpkg for QA
    ogrinfo -dialect sqlite -sql "PRAGMA table_info(Perimeters)" ${tbl}.gpkg

    # Add sdate column
    ogrinfo -dialect sqlite -sql "ALTER TABLE Perimeters ADD COLUMN sdate date" ${tbl}.gpkg
    ogrinfo -dialect sqlite -sql "UPDATE Perimeters SET sdate = coalesce(attr_FireDiscoveryDateTime, attr_ICS209RptForTimePeriodFrom, poly_PolygonDateTime, poly_CreateDate)" ${tbl}.gpkg

    # Add edate column
    ogrinfo -dialect sqlite -sql "ALTER TABLE Perimeters ADD COLUMN edate date" ${tbl}.gpkg
    ogrinfo -dialect sqlite -sql "UPDATE Perimeters SET edate = coalesce(attr_ContainmentDateTime, attr_ControlDateTime, attr_FireOutDateTime, attr_ICS209ReportDateTime, attr_ModifiedOnDateTime_dt, poly_CreateDate)" ${tbl}.gpkg

    # Add acres column
    ogrinfo -dialect sqlite -sql "ALTER TABLE Perimeters ADD COLUMN acres float" ${tbl}.gpkg
    ogrinfo -dialect sqlite -sql "UPDATE Perimeters SET acres = coalesce(poly_Acres_AutoCalc, poly_GISAcres)" ${tbl}.gpkg

    # Add firename column
    ogrinfo -dialect sqlite -sql "ALTER TABLE Perimeters ADD COLUMN firename string" ${tbl}.gpkg
    ogrinfo -dialect sqlite -sql "UPDATE Perimeters SET firename = coalesce(attr_IncidentName, poly_IncidentName)" ${tbl}.gpkg

    # Add firetype column
    ogrinfo -dialect sqlite -sql "ALTER TABLE Perimeters ADD COLUMN firetype string" ${tbl}.gpkg
    ogrinfo -dialect sqlite -sql "UPDATE Perimeters SET firetype = coalesce(attr_IncidentTypeCategory, 'WF')" ${tbl}.gpkg

    # Add fireid column
    ogrinfo -dialect sqlite -sql "ALTER TABLE Perimeters ADD COLUMN fireid string" ${tbl}.gpkg
    ogrinfo -dialect sqlite -sql "UPDATE Perimeters SET fireid = attr_UniqueFireIdentifier" ${tbl}.gpkg

    # Check which data entry has null geometry
    #ogrinfo ${tbl}.gpkg Perimeters -al -so
    #ogrinfo -sql "SELECT * FROM gpkg_geometry_columns" ${tbl}.gpkg
    #exit(1)
    #ogr2ogr -f CSV null_geometry_rows.csv ${tbl}.gpkg -dialect sqlite -sql "SELECT * FROM Perimeters WHERE SHAPE IS NULL"
    #ogrinfo ${tbl}.gpkg Perimeters -dialect sqlite -sql "SELECT COUNT(*) FROM Perimeters WHERE SHAPE IS NULL"

    # Drop record with null geometries
    #ogr2ogr -f GPKG cleaned_${tbl}.gpkg ${tbl}.gpkg Perimeters -dialect sqlite -sql "SELECT * FROM Perimeters WHERE SHAPE IS NOT NULL"
    #ogr2ogr -f GPKG cleaned_${tbl}.gpkg ${tbl}.gpkg Perimeters -nln Perimeters -dialect sqlite -sql "SELECT * FROM Perimeters WHERE SHAPE IS NOT NULL"
    
    # Export to shapefile
    echo "Exporting to ${tbl}.shp"
    ogr2ogr -f "ESRI Shapefile" ${tbl}.shp ${tbl}.gpkg Perimeters

    ## Write Attribute table to csv file for QA/QC
    echo "Exporting to ${tbl}.csv"
    ogr2ogr -f "CSV" ${tbl}.csv ${tbl}.gpkg -dialect sqlite -sql "SELECT * FROM Perimeters"

endif

## Extract only fires started in target year
if ( $EXTRYR == 'Y' ) then
    ogr2ogr -f "ESRI Shapefile" ${tbl}_${YYYY}.shp ${tbl}.gpkg -dialect sqlite -sql "SELECT SHAPE, * FROM Perimeters WHERE strftime('%Y', sdate) = '${YYYY}' AND SHAPE IS NOT NULL"
    ogr2ogr -f "CSV" ${tbl}_${YYYY}.csv ${tbl}.gpkg -dialect sqlite -sql "SELECT SHAPE, * FROM Perimeters WHERE strftime('%Y', sdate) = '${YYYY}' AND SHAPE IS NOT NULL"
endif

rm -rf ${tbl}.gpkg