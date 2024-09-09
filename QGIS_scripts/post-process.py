# If you are not inside a QGIS console you first need to import
# qgis and PyQt classes you will use in this script as shown below:
from email.policy import default

from pyparsing import C
from qgis.core import QgsProject
import os

path_to_your_project=os.path.dirname(os.path.realpath(__file__))
project_path = os.path.join(path_to_your_project, "labeling_project.qgs")
data_path = os.path.join(path_to_your_project, "data")

project = QgsProject.instance()
project.read(project_path)

tiff_files=os.listdir(data_path)
tiff_paths=[{
            "path":os.path.join(data_path,f),
             "name":f.split('.')[0]
            }
            for f in tiff_files if f.endswith(".tiff") or f.endswith(".tif")]

tiff_paths= sorted(tiff_paths, key=lambda x: x["name"])

root=project.layerTreeRoot()

for element in tiff_paths:

    group = root.findGroup(f'{element["name"]}_label')
    ## init groups for each raster layer
    if project.mapLayersByName(f"{element['name']}_NDVI"):
        project.removeMapLayer(project.mapLayersByName(f"{element['name']}_NDVI")[0]) 
            
     
    if project.mapLayersByName(f"{element['name']}_EVI"):
        project.removeMapLayer(project.mapLayersByName(f"{element['name']}_EVI")[0])
            
  
    if project.mapLayersByName(f"{element['name']}_NDMI"):
        project.removeMapLayer(project.mapLayersByName(f"{element['name']}_NDMI")[0])
            
for file in os.listdir(data_path):
    if ("NDMI" in file) or ("EVI" in file) or ("NDVI" in file) or ("ndmi" in file) or ("evi" in file) or ("ndvi" in file):
        file_path = os.path.join(data_path, file)
        os.remove(file_path)

project.write()
  

layers = project.mapLayers().values()

# Set up the GeoPackage file path
geopackage_path = os.path.join(path_to_your_project, "output.gpkg")
for layer in layers:
    # Skip non-vector layers
    if not isinstance(layer, QgsVectorLayer):
        continue
    # Check if the layer has a valid geometry type
    if layer.geometryType() == QgsWkbTypes.NullGeometry:
        print(f"Skipping layer '{layer.name()}' as it has no geometry.")
        continue

    # Ensure the layer has a valid CRS
    if not layer.crs().isValid():
        print(f"Skipping layer '{layer.name()}' as it has an invalid CRS.")
        continue

    # Check if the GeoPackage file exists
    if not os.path.exists(geopackage_path):
        # If it doesn't exist, create it with the first layer
        error = QgsVectorFileWriter.writeAsVectorFormat(
            layer,
            geopackage_path,
            "UTF-8",
            layer.crs(),
            "GPKG"
        )
        if error[0] != QgsVectorFileWriter.NoError:
            print(f"Error creating GeoPackage with layer '{layer.name()}': {error}")
            continue
        print(f"Created GeoPackage with layer '{layer.name()}'.")
    # Set up options for writing
    save_options = QgsVectorFileWriter.SaveVectorOptions()
    save_options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer
    save_options.layerName = layer.name()
    
    # Write the layer to the GeoPackage
    error = QgsVectorFileWriter.writeAsVectorFormatV3(
        layer,
        geopackage_path,
        QgsCoordinateTransformContext(),
        save_options
    )
    
    if error[0] == QgsVectorFileWriter.NoError:
        print(f"Successfully appended layer '{layer.name()}' to GeoPackage.")
    else:
        print(f"Error appending layer '{layer.name()}': {error}")

print("Finished appending layers to GeoPackage.")
project.write()
# Remove the current project
project.clear()
# Create a new project
new_project = QgsProject.instance()
project.write()

# Remove all files with labelling_project* pattern

labeling_project_files = [
    os.path.join(path_to_your_project, "labeling_project.qgs"),
    os.path.join(path_to_your_project, "labeling_project.qgs~"),
    os.path.join(path_to_your_project, "labeling_project_attachments.zip")
]

for file in labeling_project_files:
    if os.path.exists(file):
        os.remove(file)
        print(f"Removed file: {file}")
    else:
        print(f"File not found: {file}")
print("Finished removing labelling_project files.")
# Remove all files in the data folder
data_folder = os.path.join(path_to_your_project, "data")
tiff_files=[f for f in os.listdir(data_folder) if f.endswith(".tiff") or f.endswith(".tif")]
other_files=[f for f in os.listdir(data_folder) if f not in tiff_files and not f.endswith(".shp")]
shp_files=[f for f in os.listdir(data_folder) if f.endswith(".shp")]

for file in tiff_files:
    file_path = os.path.join(data_folder, file)
    os.remove(file_path)
    print(f"Removed TIFF file: {file_path}")

for file in shp_files:
    file_path = os.path.join(data_folder, file)
    os.remove(file_path)
    print(f"Removed shapefile: {file_path}")

for file in other_files:
    file_path = os.path.join(data_folder, file)
    os.remove(file_path)
    print(f"Removed file: {file_path}")

print("Finished removing all files in the data folder.")



    
    
    





        
