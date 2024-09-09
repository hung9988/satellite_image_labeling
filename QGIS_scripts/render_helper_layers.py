# If you are not inside a QGIS console you first need to import
# qgis and PyQt classes you will use in this script as shown below:
from email.policy import default
from qgis.core import QgsProject
import os

render_NDVI = False
render_EVI = True
render_NDMI = True

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

default_color_ramp_items = [
        QgsColorRampShader.ColorRampItem(-1.0, QColor(255, 255, 255), 'Low'),  
        QgsColorRampShader.ColorRampItem(-0.6, QColor(200, 255, 200), 'Very Low'),  
        QgsColorRampShader.ColorRampItem(-0.2, QColor(150, 255, 150), 'Low-Mid'), 
        QgsColorRampShader.ColorRampItem(0.0, QColor(100, 255, 100), 'Mid-Low'),  
        QgsColorRampShader.ColorRampItem(0.2, QColor(50, 255, 50), 'Moderate Low'),  
        QgsColorRampShader.ColorRampItem(0.3, QColor(50, 200, 50), 'Moderate'),  
        QgsColorRampShader.ColorRampItem(0.4, QColor(50, 150, 50), 'Moderate High'),  
        QgsColorRampShader.ColorRampItem(0.5, QColor(50, 100, 50), 'High'), 
        QgsColorRampShader.ColorRampItem(0.6, QColor(0, 100, 0), 'High'),  
        QgsColorRampShader.ColorRampItem(0.8, QColor(0, 75, 0), 'Very High'), 
        QgsColorRampShader.ColorRampItem(1.0, QColor(0, 50, 0), 'Max')   
    ]

def set_color_ramp_raster_layer(raster_layer, color_ramp_items=default_color_ramp_items):
    color_ramp_shader = QgsColorRampShader()
    color_ramp_shader.setColorRampType(QgsColorRampShader.Interpolated)

    # Define the color ramp items with specific values

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
    
    color_ramp_items = [
    QgsColorRampShader.ColorRampItem(-1.0, QColor(255, 255, 255), '-1.000000'),  # White at -1.000000
    QgsColorRampShader.ColorRampItem(-0.74, QColor(255, 255, 255), '-0.740000'), # White at -0.740000
    QgsColorRampShader.ColorRampItem(-0.48, QColor(255, 255, 255), '-0.480000'), # White at -0.480000
    QgsColorRampShader.ColorRampItem(-0.22, QColor(254, 254, 253), '-0.220000'), # Off-white at -0.220000
    QgsColorRampShader.ColorRampItem(0.2, QColor(151, 202, 145), '0.200000'),    # Light Green at 0.200000
    QgsColorRampShader.ColorRampItem(0.3, QColor(134, 205, 133), '0.300000'),    # Light Green at 0.300000
    QgsColorRampShader.ColorRampItem(0.56, QColor(77, 177, 99), '0.560000'),     # Medium Green at 0.560000
    QgsColorRampShader.ColorRampItem(0.8, QColor(14, 121, 54), '0.800000'),      # Dark Green at 0.800000
    QgsColorRampShader.ColorRampItem(1.0, QColor(0, 68, 27), '1.000000')         # Darkest Green at 1.000000
    ]

    ndvi_layer= set_color_ramp_raster_layer(ndvi_layer,color_ramp_items=color_ramp_items)

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
    color_ramp_items = [
    QgsColorRampShader.ColorRampItem(0, QColor(175, 175, 175), '-1.000000'),  # -1.000000
    QgsColorRampShader.ColorRampItem(0.05, QColor(191, 201, 193), '-0.740000'), # -0.740000
    QgsColorRampShader.ColorRampItem(0.1, QColor(218, 246, 225), '-0.480000'), # -0.480000
    QgsColorRampShader.ColorRampItem(0.15, QColor(179, 224, 173), '-0.220000'), # -0.220000
    QgsColorRampShader.ColorRampItem(0.02, QColor(148, 211, 145), '0.040000'),   # 0.040000
    QgsColorRampShader.ColorRampItem(0.3, QColor(80, 178, 102), '0.300000'),     # 0.300000
    QgsColorRampShader.ColorRampItem(0.54, QColor(39, 144, 72), '0.538462'),     # 0.538462
    QgsColorRampShader.ColorRampItem(0.8, QColor(0, 109, 44), '0.800000'),       # 0.800000
    QgsColorRampShader.ColorRampItem(1.0, QColor(18, 92, 54), '1.000000')        # 1.000000
   ]

    evi_layer = set_color_ramp_raster_layer(evi_layer, color_ramp_items=color_ramp_items)
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
    
    color_ramp_items = [
    QgsColorRampShader.ColorRampItem(-1.0, QColor(247, 252, 245), 'Low'),        # Low
    QgsColorRampShader.ColorRampItem(-0.6, QColor(213, 239, 207), 'Very Low'),   # Very Low
    QgsColorRampShader.ColorRampItem(-0.2, QColor(159, 216, 193), 'Low-Mid'),    # Low-Mid
    QgsColorRampShader.ColorRampItem(0.0, QColor(123, 199, 169), 'Mid-Low'),     # Mid-Low
    QgsColorRampShader.ColorRampItem(0.2, QColor(85, 181, 175), 'Moderate Low'), # Moderate Low
    QgsColorRampShader.ColorRampItem(0.3, QColor(65, 171, 182), 'Moderate'),     # Moderate
    QgsColorRampShader.ColorRampItem(0.4, QColor(53, 159, 187), 'Moderate High'),# Moderate High
    QgsColorRampShader.ColorRampItem(0.5, QColor(42, 146, 193), 'High'),         # High
    QgsColorRampShader.ColorRampItem(0.6, QColor(26, 131, 199), 'High'),         # High
    QgsColorRampShader.ColorRampItem(0.8, QColor(0, 97, 208), 'Very High'),      # Very High
    QgsColorRampShader.ColorRampItem(1.0, QColor(0, 68, 208), 'Max')             # Max
    ]

    ndmi_layer = set_color_ramp_raster_layer(ndmi_layer,color_ramp_items=color_ramp_items)
    
    return ndmi_layer
    
def add_layer_to_group(layer, group, root, visibility, position=4):
    project.addMapLayer(layer)
    vl=QgsProject.instance().mapLayersByName(layer.name())[0]
    myvl=root.findLayer(vl.id())
    myvlclone=myvl.clone()
    parent=myvl.parent()
    group.insertChildNode(position, myvlclone)
    parent.removeChildNode(myvl)
    root.findLayer(vl.id()).setItemVisibilityChecked(visibility)

switch_layer=True
project.write()
for element in tiff_paths:
    existing_layers = project.mapLayersByName(element["name"])
    if not existing_layers:
        print("Layer does not exists!")
        continue
    group = root.findGroup(f'{element["name"]}_label')
    ## init groups for each raster layer
    raster_layer=existing_layers[0]

    if render_NDVI:
        if project.mapLayersByName(f"{element['name']}_NDVI"):
            print("NDVI layer already exists!")
        else:   
            ndvi_layer = create_NDVI_layer(raster_layer)
            add_layer_to_group(ndvi_layer, group, root, False)
    if render_EVI:
        if project.mapLayersByName(f"{element['name']}_EVI"):
            print("EVI layer already exists!")
        else:
            evi_layer = create_EVI_layer(raster_layer)
            add_layer_to_group(evi_layer, group, root, False, position=3 if switch_layer else 4)
            switch_layer=False
    if render_NDMI:
        if project.mapLayersByName(f"{element['name']}_NDMI"):
            print("NDMI layer already exists!")
        else:
            ndmi_layer = create_NDMI_layer(raster_layer)
            add_layer_to_group(ndmi_layer, group, root, False)

project.write()
  
    
    
    
    





        
