# Name:
# Description: 

# Import system modules
import os,sys
import arcpy

from shutil import make_archive,rmtree
from zipfile import ZipFile
from glob import glob

print('argv[1] = %s' % sys.argv[1])
print('argv[2] = %s' % sys.argv[2])

for z in glob('*.zip'):
	print ('for z in glob: %s', z)
	ZipFile(z).extractall()

# Set the working Geodatabase
arcpy.env.workspace = sys.argv[1] + ".gdb"

# Set parameters to be used in the intersect analysis function
inFeatureClass = sys.argv[1]
print ('inFeatureClass = %s', inFeatureClass)
bufferDist = sys.argv[2]

# Parse bufferDist for multiple distances and convert to ints
tempDistList = bufferDist.split("/")
bufferDistList = list(map(int, tempDistList))

#parse naming
distRangeStr = tempDistList[0] + "_to_" + tempDistList[-1]

outBufferFeatureClass = "buffer_" + distRangeStr + "_" + sys.argv[1]
print ('outBufferFeatureClass = %s', outBufferFeatureClass)

# Run the intersect analysis function
arcpy.MultipleRingBuffer_analysis(inFeatureClass, outBufferFeatureClass, bufferDistList)

# Zip up the geodatabase
for z in glob((inFeatureClass + '.gdb')):
  print ('zipping %s...' % z)
  make_archive('%s' % z, 'zip', os.getcwd(), z)
  print ('done zipping %s' % z)
  
# Delete the overlay.txt file
for f in glob('Overlay.txt'):
  os.unlink(f)

for e in glob('*.gdb'):
  rmtree(e)