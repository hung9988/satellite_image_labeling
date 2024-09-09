# If you are not inside a QGIS console you first need to import
# qgis and PyQt classes you will use in this script as shown below:
from email.policy import default
from qgis.core import QgsProject
import os
from qgis.core import QgsDataSourceUri, QgsCoordinateTransformContext, QgsVectorFileWriter

categories = ['unidentifiable','bamboo','forest','rice_field','residential','water']

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

tiff_paths=[
    path for path in tiff_paths if \
        ("ndvi" not in path["name"].lower())\
        and ("evi" not in path["name"].lower())\
        and ("ndmi" not in path["name"].lower())
]

tiff_paths= sorted(tiff_paths, key=lambda x: x["name"])

root=project.layerTreeRoot()

def add_layer_to_group(layer, group, root, visibility):
    project.addMapLayer(layer)
    vl=QgsProject.instance().mapLayersByName(layer.name())[0]
    myvl=root.findLayer(vl.id())
    myvlclone=myvl.clone()
    parent=myvl.parent()
    group.insertChildNode(0,myvlclone)
    parent.removeChildNode(myvl)
    root.findLayer(vl.id()).setItemVisibilityChecked(visibility)
    
for element in tiff_paths:
    existing_layers = project.mapLayersByName(element["name"])
    if existing_layers:
        print("Layer with the same name already exists!")
        continue
    
    
    group = root.addGroup(f'{element["name"]}_label')
    ## init groups for each raster layer
    raster_layer = QgsRasterLayer(element["path"], element["name"])
    
    add_layer_to_group(raster_layer, group, root, True)

    for cat in categories:
        vlayer = QgsVectorLayer(f"polygon?crs=epsg:4326", f"{element['name']}_{cat}", "memory")
        shapefile_path = os.path.join(path_to_your_project, "data", f"{element['name']}_{cat}.shp")
        error = QgsVectorFileWriter.writeAsVectorFormat(vlayer, shapefile_path, "UTF-8", vlayer.crs(), "ESRI Shapefile")
        saved_layer = QgsVectorLayer(shapefile_path, f"{element['name']}_{cat}", "ogr")
        
        add_layer_to_group(saved_layer, group, root, True)

project.write()
  
    
    
    
    





        
