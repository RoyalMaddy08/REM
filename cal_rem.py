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
