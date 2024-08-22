# If you are not inside a QGIS console you first need to import
# qgis and PyQt classes you will use in this script as shown below:
from qgis.core import QgsProject
import os

categories=['forest','water','rice']

project = QgsProject.instance()
project.read('C:/Users/hung/thanh_Hoa_Image/labeling_project.qgs')
### The path that you want to save the project
base_path="C:/Users/hung/thanh_Hoa_Image"
data_path = os.path.join(base_path, "data")
tiff_files=os.listdir(data_path)
tiff_paths=[{
            "path":os.path.join(data_path,f),
             "name":f.split('.')[0]
            }
            for f in tiff_files if f.endswith(".tiff") or f.endswith(".tif")]

tiff_paths= sorted(tiff_paths, key=lambda x: x["name"])

root=project.layerTreeRoot()

for element in tiff_paths:
    existing_layers = project.mapLayersByName(element["name"])
    if existing_layers:
        print("Layer with the same name already exists!")
        continue
    
    ## init groups for each raster layer
    raster_layer = QgsRasterLayer(element["path"], element["name"])
    project.addMapLayer(raster_layer)
    vl = QgsProject.instance().mapLayersByName(element["name"])[0]
    myvl = root.findLayer(vl.id())
    myvlclone = myvl.clone()
    group1 = root.addGroup(f'{element["name"]}_label')
    parent = myvl.parent()
    group1.insertChildNode(0, myvlclone)
    parent.removeChildNode(myvl)
    
    for cat in categories:
        vlayer = QgsVectorLayer(f"polygon?crs=epsg:4326", f"{element['name']}_{cat}", "memory")
        shapefile_path = os.path.join(base_path, "data", f"{element['name']}_{cat}.shp")
        error = QgsVectorFileWriter.writeAsVectorFormat(vlayer, shapefile_path, "UTF-8", vlayer.crs(), "ESRI Shapefile")
        saved_layer = QgsVectorLayer(shapefile_path, f"{element['name']}_{cat}", "ogr")

        project.addMapLayer(saved_layer)
        vl = QgsProject.instance().mapLayersByName(f"{element['name']}_{cat}")[0]
        myvl = root.findLayer(vl.id())
        myvlclone = myvl.clone()
        group1.insertChildNode(0, myvlclone)
        parent = myvl.parent()
        parent.removeChildNode(myvl)
        
project.write()
  
    
    
    
    





        
