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

# First, load your DEM data
# Replace "your_dem_file.tif" with your actual DEM filename
dem = rxr.open_rasterio("/content/USGS_1_n52w119_20130911.tif")

# Use the river bounds to clip the DEM
river_bounds = river_raster.rio.bounds()
buffer = 0.01

xmin = river_bounds[0] - buffer
ymin = river_bounds[1] - buffer  
xmax = river_bounds[2] + buffer
ymax = river_bounds[3] + buffer

print(f"Clipping DEM with bounds: {xmin}, {ymin}, {xmax}, {ymax}")

# Clip DEM to match river area
dem_clipped = dem.sel(x=slice(xmin, xmax), y=slice(ymax, ymin))

print(f"DEM clipped shape: {dem_clipped.shape}")
print(f"DEM has data: {not dem_clipped.isnull().all()}")

# Plot both DEM and river data
fig, ax = plt.subplots(figsize=(12, 10))

# Plot DEM as background
dem_clipped.squeeze().plot.imshow(ax=ax, cmap='terrain', alpha=0.7)

# Plot river data on top
river_raster.plot.imshow(ax=ax, cmap='Blues', alpha=0.8)

ax.set_title("DEM with River Data")
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
plt.show()
