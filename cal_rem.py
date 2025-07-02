# Create separate plots to better understand your data
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))

# Plot 1: DEM only
dem_clipped.squeeze().plot.imshow(ax=ax1, cmap='terrain')
ax1.set_title("DEM Elevation")

# Plot 2: River raster only
river_raster.squeeze().plot.imshow(ax=ax2, cmap='Blues')
ax2.set_title("River Raster Values")

# Plot 3: Combined with river threshold
dem_clipped.squeeze().plot.imshow(ax=ax3, cmap='terrain', alpha=0.8)

# Create a mask for high river values (assuming higher values = more flow)
river_threshold = river_raster.quantile(0.9)  # Top 10% of values
river_mask = river_raster > river_threshold
river_mask.squeeze().plot.imshow(ax=ax3, cmap='Blues', alpha=0.7)

ax3.set_title("DEM with River Network (Top 10% Flow)")

plt.tight_layout()
plt.show()

print(f"River values range from {river_raster.min().values:.1f} to {river_raster.max().values:.1f}")


import numpy as np
from shapely.geometry import Point, LineString
from sklearn.cluster import DBSCAN

# Extract river pixels above a threshold (assuming higher values = river channels)
river_threshold = river_raster.quantile(0.95)  # Top 5% of values
river_pixels = river_raster > river_threshold

# Get coordinates of river pixels
y_coords, x_coords = np.where(river_pixels.squeeze().values)

# Convert array indices to actual coordinates
x_real = river_raster.x.values[x_coords]
y_real = river_raster.y.values[y_coords]

# Create points
river_points = [Point(x, y) for x, y in zip(x_real, y_real)]

# Convert to coordinate arrays for sampling
xs = xr.DataArray(x_real, dims='z')
ys = xr.DataArray(y_real, dims='z')

print(f"Extracted {len(xs)} river points")


from sklearn.neighbors import KDTree

# Use dem_clipped instead of dem, and make sure to squeeze it
sampled = dem_clipped.squeeze().interp(x=xs, y=ys, method='nearest').dropna(dim='z')

print(f"Sampled {len(sampled)} elevation values along river")

# Sampled river coordinates
c_sampled = np.vstack([sampled.coords[c].values for c in ('x', 'y')]).T

# All (x, y) coordinates of the clipped DEM
c_x, c_y = [dem_clipped.squeeze().coords[c].values for c in ('x', 'y')]
c_interpolate = np.dstack(np.meshgrid(c_x, c_y)).reshape(-1, 2)

# Sampled elevation values
values = sampled.values.ravel()

print(f"Interpolating {len(c_sampled)} sample points to {len(c_interpolate)} grid points")

# Build KDTree
tree = KDTree(c_sampled)

# IWD interpolation - query 5 nearest neighbors
distances, indices = tree.query(c_interpolate, k=5)

# Calculate inverse distance weights
weights = 1 / (distances + 1e-10)  # Add small value to avoid division by zero
weights = weights / weights.sum(axis=1).reshape(-1, 1)

# Interpolate values
interpolated_values = (weights * values[indices]).sum(axis=1)

# Create DataArray from interpolated values
elevation_raster = xr.DataArray(
    interpolated_values.reshape((len(c_y), len(c_x))), 
    dims=('y', 'x'), 
    coords={'x': c_x, 'y': c_y}
)

print(f"Created elevation raster with shape: {elevation_raster.shape}")

# Plot the interpolated elevation raster
fig, ax = plt.subplots(figsize=(12, 8))
elevation_raster.plot.imshow(ax=ax, cmap='terrain')

# Overlay river points (sample some for visibility)
if len(xs) > 10000:  # If too many points, sample some for display
    sample_idx = np.random.choice(len(xs), 5000, replace=False)
    ax.scatter(xs.values[sample_idx], ys.values[sample_idx], 
               c='red', s=0.1, alpha=0.5, label='River points')
else:
    ax.scatter(xs.values, ys.values, c='red', s=0.1, alpha=0.5, label='River points')

ax.set_title("Interpolated River Elevation")
ax.legend()
plt.show()
