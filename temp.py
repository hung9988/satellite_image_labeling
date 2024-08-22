# If you are not inside a QGIS console you first need to import
# qgis and PyQt classes you will use in this script as shown below:
from qgis.core import QgsProject
import os
# Get the project instance
project = QgsProject.instance()
base_path="C:/Users/hung/thanh_Hoa_Image"
# Print the current project file name (might be empty in case no projects have been loaded)
project.read('C:/Users/hung/thanh_Hoa_Image/labeling_project.qgs')
print(project.fileName())
vlayer = QgsVectorLayer(f"polygon?crs=epsg:4326", "Image0_wheat", "memory")
if not vlayer:
  print("Layer failed to load!")
# Save the shapefile to disk
shapefile_path = os.path.join(base_path, "data", "test_layer_222.shp")
error = QgsVectorFileWriter.writeAsVectorFormat(vlayer, shapefile_path, "UTF-8", vlayer.crs(), "ESRI Shapefile")
project.write()