xmin, ymin, xmax, ymax = -120, 47, -118, 49
bounds = box(xmin, ymin, xmax, ymax)

river = river.clip(bounds)

if not river.empty:
    river_geom = river.geometry.iloc[0]
else:
    print("No river geometry found within the specified bounds.")
    river_geom = None # Or handle the empty case as needed

dem = dem.sel(y=slice(ymax, ymin), x=slice(xmin, xmax))

import rasterio
import xarray as xr
import rioxarray as rxr

# Load the river TIFF as raster data
river_raster = rxr.open_rasterio("/content/USGS_1_n52w119_20130911.tif")

# Check what's in the river raster
print("River raster info:")
print(f"Shape: {river_raster.shape}")
print(f"Data type: {river_raster.dtype}")
print(f"CRS: {river_raster.rio.crs}")
print(f"Bounds: {river_raster.rio.bounds()}")
print(f"Has data: {not river_raster.isnull().all()}")

# Check coordinate ranges
print(f"\nCoordinate ranges:")
print(f"X range: {river_raster.x.min().values} to {river_raster.x.max().values}")
print(f"Y range: {river_raster.y.min().values} to {river_raster.y.max().values}")

# Look at the data values
print(f"\nData value range:")
print(f"Min: {river_raster.min().values}")
print(f"Max: {river_raster.max().values}")
print(f"Unique values: {len(river_raster.values[~np.isnan(river_raster.values)])}")
