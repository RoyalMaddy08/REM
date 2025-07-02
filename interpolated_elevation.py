# Calculate REM by subtracting interpolated elevation from original DEM
rem = dem_clipped.squeeze() - elevation_raster

print(f"REM shape: {rem.shape}")
print(f"REM value range: {rem.min().values:.2f} to {rem.max().values:.2f}")

# Basic REM visualization
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))

# Original DEM
dem_clipped.squeeze().plot.imshow(ax=ax1, cmap='terrain')
ax1.set_title('Original DEM')

# Interpolated river elevation
elevation_raster.plot.imshow(ax=ax2, cmap='terrain')
ax2.set_title('Interpolated River Elevation')

# REM result
rem.plot.imshow(ax=ax3, cmap='RdYlBu_r', vmin=0, vmax=50)
ax3.set_title('Relative Elevation Model (REM)')

plt.tight_layout()
plt.show()

# First, let's check your REM data
print("REM data info:")
print(f"Shape: {rem.shape}")
print(f"Data type: {rem.dtype}")
print(f"Has data: {not rem.isnull().all()}")
print(f"Min value: {rem.min().values}")
print(f"Max value: {rem.max().values}")
print(f"Number of valid values: {rem.count().values}")


# Let's check the data ranges to understand what's happening
print("Data ranges:")
print(f"DEM range: {dem_clipped.squeeze().min().values:.2f} to {dem_clipped.squeeze().max().values:.2f}")
print(f"Interpolated elevation range: {elevation_raster.min().values:.2f} to {elevation_raster.max().values:.2f}")
print(f"REM range: {rem.min().values:.2f} to {rem.max().values:.2f}")

# Plot all three to see what's happening
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))

# Original DEM
dem_clipped.squeeze().plot.imshow(ax=ax1, cmap='terrain')
ax1.set_title('Original DEM')

# Interpolated river elevation
elevation_raster.plot.imshow(ax=ax2, cmap='terrain')
ax2.set_title('Interpolated River Elevation')

# REM with full range
rem.plot.imshow(ax=ax3, cmap='RdBu_r')
ax3.set_title('REM (Full Range)')

# REM focusing on positive values (areas above river level)
rem_positive = rem.where(rem > 0)
rem_positive.plot.imshow(ax=ax4, cmap='YlOrRd', vmin=0, vmax=50)
ax4.set_title('REM (Positive Values Only)')

plt.tight_layout()
plt.show()
