#!/usr/bin/env python

""""------------------------------------------------------------------------------
name:         		split_feature_class.py
arguments/inputs:   No. of polylines for each feature class
			  
version:            python 2.7

dependencies: 		Input Geodatabase that has a feature class of polyline and a feature class of point
			  
description:    	This script splits a polyline feature class of large volume into multiple feature classes of polylines of small volume, 
which are then stored in separate geodatabases with the point feature class. Finally it zipped all those geodatabases and delete the unzipped geodatabases.
-------------------------------------------------------------------------------"""
# Import os and sys python modules which allow python to use file based functions
# and utilities.
import os,sys
import shutil
from shutil import rmtree,make_archive
from zipfile import ZipFile
from glob import glob

# Import ArcGIS modules
import arcpy 

# Where Input Geodatabase with feature classes, python scripts and condor
# submission file resides
workingFolderPath = "" 
	
# A temporary output folder created to store temporary geodatabase
tempFolderPath = "temp\\" 	


# Ask user to input geodatabase file name, the polyline featureclass, and
# the points feature class. Also, ask the user how many observations
# for each subset of the polyline feacture class. 
inGeodatabase = raw_input('Enter filename of geodatabase: ')
if not inGeodatabase:
	inGeodatabase = "Task_SF.gdb"
	
if (os.path.isdir(inGeodatabase) == False):
	print('Geodatabase, %s can not be found' % inGeodatabase)
	quit(-1)
else:
	# Set the working Geodatabase
	arcpy.env.workspace = workingFolderPath + inGeodatabase

# Input polyline feature class.
polygonFC = raw_input('Enter Polygon feature class name: ')
if not polygonFC:
	polygonFC = "watersources_th"
	
if arcpy.Exists(polygonFC):
	# Get total number of entries in poly-line feature class.
	result = arcpy.GetCount_management(polygonFC)
	numObservations = int(result.getOutput(0))
else:
	print('Feature Class, %s does not exist in %s' % (polygonFC,inGeodatabase))
	quit(-1)
	
# Get a count of the observations
strSubsetEntries = raw_input('Enter number of entries per polyline subset: ')
if not strSubsetEntries:
	subsetEntries = 5000
else:
    subsetEntries = int(strSubsetEntries)


###############################################################################
# Create subset feature classes 

print('total count of feature class, %s = %i' % (polygonFC, numObservations))

# No. of feature classes after spliting (i.e. integer)
# The '//' divides the numbers and returns a number without the remainder.
numNewFeatureClasses = (numObservations // subsetEntries) + 1   


print("numNewFeatureClasses for feature class, %s = %i" % (polygonFC,numNewFeatureClasses))

# Set flag, deleteAll to False.
if (len(sys.argv) > 1):
	if (sys.argv[1].lower() == "del"):
		deleteExisting = "del"
else:
	deleteExisting = ""


# start loop to create subsets...
for i in range(1, (numNewFeatureClasses + 1)):

	# Set up the SQL Where clause that will be used to select certain rows of the large feature class.
	subsetFC = polygonFC + '_' + str(i)
	print('subsetFC = %s' % subsetFC)
	outGeodatabase = subsetFC + '.gdb'
	
	obsIdx = (i-1) * subsetEntries
	whereClause = '"OBJECTID" > ' + str(obsIdx) + ' AND "OBJECTID" <= ' + str((obsIdx + subsetEntries))
	print('whereClause = %s' % whereClause)

	subsetExists = arcpy.Exists(subsetFC)
	if subsetExists or (deleteExisting == "del"):
		if ((deleteExisting != "nall") and (deleteExisting != "yall") and (deleteExisting != "del")):
			print('\nThis subset feature class already exists in %s. Do you \
wish to recreate it?' % inGeodatabase)
			print('y/n/yall/nall/del...')
			print('"yall" will recreate this and all other existing \
subsets without prompting')
			print('"nall" will not delete nor recreate this and all other existing \
subsets.')
			print('"del" will only delete and not recreate this and all other \
existing subsets.')
			deleteExisting = raw_input('\n? :').lower()
		if ((deleteExisting == "y") or (deleteExisting == "yall") or (deleteExisting == "del")):
			# Delete the subset feature class 
			print('Deleting subset, %s...' % subsetFC)
			if (arcpy.Exists(subsetFC)):
				arcpy.Delete_management(subsetFC)
				subsetExists = False
			if (os.path.isdir(tempFolderPath + outGeodatabase) == True):
				rmtree(tempFolderPath + outGeodatabase)
			if (os.path.isfile(outGeodatabase + '.zip') == True):
				os.unlink(outGeodatabase + '.zip')
	if ((subsetExists == False) and (deleteExisting != "del")):
		# Create new feature class from range of rows.
		print('Creating subset feature class...')
		arcpy.Select_analysis(polygonFC, subsetFC, whereClause)

		# Create Geodatabase
		print('Creating new geodatabase, %s' % outGeodatabase)
		arcpy.CreateFileGDB_management(tempFolderPath, outGeodatabase)

		# Export newly created feature class and feature class: Station_Points
		print('Exporting feature class %s' % subsetFC)
		#arcpy.FeatureClassToGeodatabase_conversion([subsetFC, pointsFC], (tempFolderPath + outGeodatabase))
		arcpy.FeatureClassToGeodatabase_conversion(subsetFC, (tempFolderPath + outGeodatabase))
		
	
		# Delete newly created subset feature class from inGeodatabase		
		arcpy.Delete_management(subsetFC)
		
		# Zip up newly created geodatabase
		z = outGeodatabase
		print('zipping %s...' % z)
		make_archive('%s' % z, 'zip', tempFolderPath, z) #Archiving zipped geodatabases into working directory
		print('done zipping %s' % z)
	
# Delete unzipped geodatabase from temporary output folder
os.chdir(tempFolderPath)
print('Removing unzipped Files in temporary directory')
for e in glob('*.gdb'): 
  rmtree(e)



