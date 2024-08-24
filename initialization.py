# If you are not inside a QGIS console you first need to import
# qgis and PyQt classes you will use in this script as shown below:
from qgis.core import QgsProject
import os
categories = ['unidentifiable','bamboo','forest','rice_field']
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

def set_color_ramp_raster_layer(raster_layer):
    color_ramp_shader = QgsColorRampShader()
    color_ramp_shader.setColorRampType(QgsColorRampShader.Interpolated)

    # Define the color ramp items with specific values
    color_ramp_items = [
        QgsColorRampShader.ColorRampItem(-1, QColor(255, 255, 255), 'Low'),   # White at NDMI = -1
        # QgsColorRampShader.ColorRampItem(0.2, QColor(0, 200, 0), 'Moderate'), # Yellow at NDMI = 0.2
        # QgsColorRampShader.ColorRampItem(0.4, QColor(0, 255, 0), 'High'),   # Green at NDMI = 0.5
        QgsColorRampShader.ColorRampItem(1, QColor(0, 128, 0), 'Max')    # Dark Green at NDMI = 1
    ]
    
    # Set the color ramp items to the shader
    color_ramp_shader.setColorRampItemList(color_ramp_items)

    # Create a raster shader and set the color ramp shader
    raster_shader = QgsRasterShader()
    raster_shader.setRasterShaderFunction(color_ramp_shader)

    # Create and set the renderer
    renderer = QgsSingleBandPseudoColorRenderer(raster_layer.dataProvider(), 1, raster_shader)
    raster_layer.setRenderer(renderer)
    raster_layer.renderer().setClassificationMin(-1)
    raster_layer.renderer().setClassificationMax(1)
    
    return raster_layer

def create_NDVI_layer(raster_layer: QgsRasterLayer):
    # Define the output file path for the NDVI layer
    output_ndvi_path = os.path.join(data_path, f"{raster_layer.name()}_NDVI.tif")
    
    # Define the expression for NDVI calculation
    ndvi_expr = QgsExpression("((\"B8@1\" - \"B4@1\") / (\"B8@1\" + \"B4@1\"))")
    
    # Prepare the Raster Calculator entries for NIR and Red bands
    entries = []
    
    # NIR Band (B8, typically the 4th band)
    nir_band = QgsRasterCalculatorEntry()
    nir_band.ref = 'B8@1'
    nir_band.raster = raster_layer
    nir_band.bandNumber = 4
    entries.append(nir_band)

    # Red Band (B4, typically the 3rd band)
    red_band = QgsRasterCalculatorEntry()
    red_band.ref = 'B4@1'
    red_band.raster = raster_layer
    red_band.bandNumber = 3
    entries.append(red_band)

    # Perform the NDVI calculation using QgsRasterCalculator
    ndvi_calculator = QgsRasterCalculator(
        ndvi_expr.expression(),
        output_ndvi_path,
        "GTiff",
        raster_layer.extent(),
        raster_layer.width(),
        raster_layer.height(),
        entries
    )
    
    # Run the calculation
    ndvi_calculator.processCalculation()
    
    # Load the resulting NDVI layer
    ndvi_layer = QgsRasterLayer(output_ndvi_path, f"{raster_layer.name()}_NDVI")
    
    ndvi_layer= set_color_ramp_raster_layer(ndvi_layer)

    # # Add the NDVI layer to the QGIS project
    return ndvi_layer

def create_EVI_layer(raster_layer: QgsRasterLayer):
    # Define the output file path for the EVI layer
    output_evi_path = f"{data_path}/{raster_layer.name()}_evi.tif"
    
    # Define the expression for EVI calculation
    evi_expr = QgsExpression("2.5 * ((\"B8@1\" - \"B4@1\") / (\"B8@1\" + 6 * \"B4@1\" - 7.5 * \"B2@1\" + 1))")
    
    # Prepare the Raster Calculator entries for NIR, Red, and Blue bands
    entries = []
    
    # NIR Band (B8, typically the 4th band)
    nir_band = QgsRasterCalculatorEntry()
    nir_band.ref = 'B8@1'
    nir_band.raster = raster_layer
    nir_band.bandNumber = 4
    entries.append(nir_band)

    # Red Band (B4, typically the 3rd band)
    red_band = QgsRasterCalculatorEntry()
    red_band.ref = 'B4@1'
    red_band.raster = raster_layer
    red_band.bandNumber = 3
    entries.append(red_band)

    # Blue Band (B2, typically the 1st band)
    blue_band = QgsRasterCalculatorEntry()
    blue_band.ref = 'B2@1'
    blue_band.raster = raster_layer
    blue_band.bandNumber = 1
    entries.append(blue_band)

    # Perform the EVI calculation using QgsRasterCalculator
    evi_calculator = QgsRasterCalculator(
        evi_expr.expression(),
        output_evi_path,
        "GTiff",
        raster_layer.extent(),
        raster_layer.width(),
        raster_layer.height(),
        entries
    )
    
    # Run the calculation
    evi_calculator.processCalculation()
    
    # Load the resulting EVI layer
    evi_layer = QgsRasterLayer(output_evi_path, f"{raster_layer.name()}_EVI")

    evi_layer = set_color_ramp_raster_layer(evi_layer)
    # Add the EVI layer to the QGIS project
    return evi_layer

def create_NDMI_layer(raster_layer: QgsRasterLayer):
    
    output_ndmi_path = f"{data_path}/{raster_layer.name()}_ndmi.tif"
    
    # Define the expression for NDMI calculation
    ndmi_expr = QgsExpression("((\"B8@1\" - \"B11@1\") / (\"B8@1\" + \"B11@1\"))")
    
    # Prepare the Raster Calculator entries for NIR and SWIR bands
    entries = []
    
    # NIR Band (B8, typically the 4th band)
    nir_band = QgsRasterCalculatorEntry()
    nir_band.ref = 'B8@1'
    nir_band.raster = raster_layer
    nir_band.bandNumber = 4
    entries.append(nir_band)

    # SWIR Band (B11, typically the 11th band)
    swir_band = QgsRasterCalculatorEntry()
    swir_band.ref = 'B11@1'
    swir_band.raster = raster_layer
    swir_band.bandNumber = 5
    entries.append(swir_band)

    # Perform the NDMI calculation using QgsRasterCalculator
    ndmi_calculator = QgsRasterCalculator(
        ndmi_expr.expression(),
        output_ndmi_path,
        "GTiff",
        raster_layer.extent(),
        raster_layer.width(),
        raster_layer.height(),
        entries
    )
    
    # Run the calculation
    ndmi_calculator.processCalculation()
    
    # Load the resulting NDMI layer
    ndmi_layer = QgsRasterLayer(output_ndmi_path, f"{raster_layer.name()}_NDMI")
    
    ndmi_layer = set_color_ramp_raster_layer(ndmi_layer)
    
    return ndmi_layer
    
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
    ndvi_layer = create_NDVI_layer(raster_layer)
    evi_layer = create_EVI_layer(raster_layer)
    ndmi_layer = create_NDMI_layer(raster_layer)

    add_layer_to_group(raster_layer, group, root, True)
    add_layer_to_group(ndvi_layer, group, root, False)
    add_layer_to_group(evi_layer, group, root, False)
    add_layer_to_group(ndmi_layer, group, root, False)
    
    for cat in categories:
        vlayer = QgsVectorLayer(f"polygon?crs=epsg:4326", f"{element['name']}_{cat}", "memory")
        shapefile_path = os.path.join(path_to_your_project, "data", f"{element['name']}_{cat}.shp")
        error = QgsVectorFileWriter.writeAsVectorFormat(vlayer, shapefile_path, "UTF-8", vlayer.crs(), "ESRI Shapefile")
        saved_layer = QgsVectorLayer(shapefile_path, f"{element['name']}_{cat}", "ogr")
        
        add_layer_to_group(saved_layer, group, root, True)

project.write()
  
    
    
    
    





        
