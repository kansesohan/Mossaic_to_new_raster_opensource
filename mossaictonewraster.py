

import os
import rasterio
from rasterio.merge import merge
from rasterio.mask import mask
from shapely.geometry import box
import geopandas as gpd
import numpy as np

# List of input raster paths
input_raster_paths = [
    r"G:\1.Remote_Sensing_Data\2.Tiff\T43PCT_20180115T053151_B02.tif",
    r"G:\1.Remote_Sensing_Data\2.Tiff\T43PDT_20180115T053151_B02.tif",
    r"G:\1.Remote_Sensing_Data\2.Tiff\T43QCU_20180115T053151_B02.tif",
    r"G:\1.Remote_Sensing_Data\2.Tiff\T43QDU_20180115T053151_B02.tif",
]

# Output mosaic file path
output_mosaic_path = r"G:\1.Remote_Sensing_Data\6.Compiled_Dataset\7.Blue_Band\2018\1\Blue_Band_compiled_20180115.tif"

# Path to the shapefile for clipping
shapefile_path = r"E:\Crop_Water_Stress_Condition_Western_Maharashtra\Shapefiles\Kolhapur_Upper_Krishna_Basin.shp"

# Separate directory for clipped output
output_clip_dir = r"G:\1.Remote_Sensing_Data\6.Compiled_Dataset\7.Blue_Band\2018\1\clip"

# Ensure the output directory exists
os.makedirs(output_clip_dir, exist_ok=True)

# Mosaic the input rasters with progress updates
def mosaic_with_progress(input_paths, output_path):
    num_rasters = len(input_paths)
    print(f"Starting mosaic of {num_rasters} rasters.")

    # Read the raster data
    src_files_to_mosaic = [rasterio.open(path) for path in input_paths]
    mosaic, out_transform = merge(src_files_to_mosaic)
    
    # Update metadata
    out_meta = src_files_to_mosaic[0].meta.copy()
    out_meta.update({
        "driver": "GTiff",
        "height": mosaic.shape[1],
        "width": mosaic.shape[2],
        "transform": out_transform
    })


    # Save the mosaic
    with rasterio.open(output_path, "w", **out_meta) as dest:
        dest.write(mosaic)

    # Close the raster files
    for src_file in src_files_to_mosaic:
        src_file.close()

    print("Mosaic completed successfully!")

# Function to clip the mosaic using the shapefile
def clip_raster(input_path, output_path, shapefile_path):
    with rasterio.open(input_path) as src:
        shapefile = gpd.read_file(shapefile_path)
        
        # Reproject shapefile to match raster CRS if necessary
        if shapefile.crs != src.crs:
            shapefile = shapefile.to_crs(src.crs)
        
        # Get the bounding box of the shapefile in the raster's coordinate system
        shapefile_bbox = shapefile.total_bounds
        window = src.window(*shapefile_bbox)
        
        # Read data using the window
        raster_data = src.read(window=window, boundless=True)
        
        # Calculate the transform for the clipped data
        out_transform = rasterio.windows.transform(window, src.transform)
        
        # Save the clipped raster
        with rasterio.open(output_path, "w", driver="GTiff", height=raster_data.shape[1],
                           width=raster_data.shape[2], count=src.count, dtype=raster_data.dtype,
                           crs=src.crs, transform=out_transform) as dest:
            dest.write(raster_data)

# Clip the mosaic using the shapefile with progress updates
def clip_with_progress(input_path, output_path, shapefile_path):
    print("Clipping the mosaic using the shapefile.")
    clip_raster(input_path, output_path, shapefile_path)
    print("Clipping completed successfully!")

# Mosaic the input rasters
mosaic_with_progress(input_raster_paths, output_mosaic_path)

# Clip the mosaic using the shapefile
output_clip_path = os.path.join(output_clip_dir, "Blue_Band_compiled_clip_20180115.tif")
clip_with_progress(output_mosaic_path, output_clip_path, shapefile_path)


