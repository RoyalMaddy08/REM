import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# Your beautiful color palette
colors = ['#f2f7fb', '#81a8cb', '#37123d']

print(f"REM data range: {rem.min().values:.2f} to {rem.max().values:.2f}")
print(f"DEM data range: {dem.min().values:.2f} to {dem.max().values:.2f}")

# =============================================================================
# Option 1: Fix your original code with correct REM span
# =============================================================================
print("\n=== Option 1: Fixed version of your original code ===")

try:
    # Create hillshade
    a = shade(xrspatial.hillshade(dem.squeeze(), angle_altitude=1, azimuth=310), 
              cmap=['black', 'white'], how='linear')
    
    # Fix the REM span to use actual data range
    b = shade(rem.squeeze(), cmap=colors, 
              span=[rem.min().values, rem.max().values], how='linear', alpha=200)
    
    # Stack them
    combined = stack(a, b)
    print("Original code fixed - using actual REM data range")
    
except NameError as e:
    print(f"xrspatial functions not available: {e}")
    print("Using matplotlib alternatives below...")

# =============================================================================
# Option 2: Alternative approach with matplotlib
# =============================================================================
print("\n=== Option 2: Matplotlib implementation ===")

# Create hillshade effect manually
def simple_hillshade(dem_data, azimuth=315, altitude=45):
    """Simple hillshade calculation"""
    # Calculate gradients
    dy, dx = np.gradient(dem_data)
    
    # Convert to radians
    azimuth_rad = np.radians(azimuth)
    altitude_rad = np.radians(altitude)
    
    # Calculate slope and aspect
    slope = np.arctan(np.sqrt(dx**2 + dy**2))
    aspect = np.arctan2(-dx, dy)
    
    # Calculate hillshade
    hillshade = np.sin(altitude_rad) * np.sin(slope) + \
                np.cos(altitude_rad) * np.cos(slope) * \
                np.cos(azimuth_rad - aspect)
    
    return np.clip(hillshade, 0, 1)

# Create hillshade
hillshade_data = simple_hillshade(dem.values.squeeze(), azimuth=310, altitude=1)

# Create the combined visualization
fig, axes = plt.subplots(2, 2, figsize=(16, 14))

# 1. DEM hillshade only
axes[0,0].imshow(hillshade_data, cmap='gray', alpha=1)
axes[0,0].set_title('DEM Hillshade (Azimuth=310°, Altitude=1°)')
axes[0,0].axis('off')

# 2. REM only with correct range
custom_cmap = LinearSegmentedColormap.from_list("custom", colors)
rem_img = axes[0,1].imshow(rem.values.squeeze(), cmap=custom_cmap, 
                          vmin=rem.min().values, vmax=rem.max().values, alpha=0.8)
axes[0,1].set_title('REM (Actual Range)')
axes[0,1].axis('off')
plt.colorbar(rem_img, ax=axes[0,1], fraction=0.046, pad=0.04)

# 3. Combined - hillshade + REM (actual range)
axes[1,0].imshow(hillshade_data, cmap='gray', alpha=0.7)
rem_overlay = axes[1,0].imshow(rem.values.squeeze(), cmap=custom_cmap, 
                              vmin=rem.min().values, vmax=rem.max().values, 
                              alpha=0.6)
axes[1,0].set_title('Combined: Hillshade + REM (Actual Range)')
axes[1,0].axis('off')
plt.colorbar(rem_overlay, ax=axes[1,0], fraction=0.046, pad=0.04)

# 4. Combined - hillshade + REM (upper range focus)
upper_percentile = np.percentile(rem.values, 85)
axes[1,1].imshow(hillshade_data, cmap='gray', alpha=0.7)
rem_upper = axes[1,1].imshow(rem.values.squeeze(), cmap=custom_cmap, 
                            vmin=upper_percentile, vmax=0, alpha=0.6)
axes[1,1].set_title('Combined: Hillshade + REM (Upper 15%)')
axes[1,1].axis('off')
plt.colorbar(rem_upper, ax=axes[1,1], fraction=0.046, pad=0.04)

plt.suptitle('DEM Hillshade + REM Visualizations', fontsize=16)
plt.tight_layout()
plt.show()

# =============================================================================
# Option 3: Different hillshade parameters for better visualization
# =============================================================================
print("\n=== Option 3: Multiple hillshade angles ===")

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Different lighting conditions
angles = [(315, 45, 'Standard (NW, 45°)'), 
          (310, 1, 'Low angle (NW, 1°)'),
          (135, 30, 'SE lighting (30°)'),
          (270, 60, 'West lighting (60°)')]

for i, (azimuth, altitude, title) in enumerate(angles):
    row, col = i // 2, i % 2
    
    # Create hillshade
    hs = simple_hillshade(dem.values.squeeze(), azimuth=azimuth, altitude=altitude)
    
    # Combine with REM
    axes[row, col].imshow(hs, cmap='gray', alpha=0.7)
    rem_img = axes[row, col].imshow(rem.values.squeeze(), cmap=custom_cmap, 
                                   vmin=rem.min().values, vmax=rem.max().values, 
                                   alpha=0.6)
    axes[row, col].set_title(f'Hillshade + REM: {title}')
    axes[row, col].axis('off')

plt.suptitle('Different Hillshade Lighting Conditions', fontsize=16)
plt.tight_layout()
plt.show()

# =============================================================================
# Corrected versions of your original code
# =============================================================================
print("\n=== Corrected versions for your xrspatial code ===")
print("# Version 1: Use actual REM range")
print("a = shade(xrspatial.hillshade(dem.squeeze(), angle_altitude=1, azimuth=310), cmap=['black', 'white'], how='linear')")
print(f"b = shade(rem.squeeze(), cmap={colors}, span=[{rem.min().values:.2f}, {rem.max().values:.2f}], how='linear', alpha=200)")
print("stack(a, b)")

print("\n# Version 2: Focus on upper REM values")
upper_bound = np.percentile(rem.values, 90)
print("a = shade(xrspatial.hillshade(dem.squeeze(), angle_altitude=1, azimuth=310), cmap=['black', 'white'], how='linear')")
print(f"b = shade(rem.squeeze(), cmap={colors}, span=[{upper_bound:.2f}, 0.0], how='linear', alpha=200)")
print("stack(a, b)")

print("\n# Version 3: Normalize REM to 0-10 first")
print("rem_normalized = ((rem - rem.min()) / (rem.max() - rem.min())) * 10")
print("a = shade(xrspatial.hillshade(dem.squeeze(), angle_altitude=1, azimuth=310), cmap=['black', 'white'], how='linear')")
print(f"b = shade(rem_normalized.squeeze(), cmap={colors}, span=[0, 10], how='linear', alpha=200)")
print("stack(a, b)")

# Show data ranges for reference
print(f"\nData Reference:")
print(f"REM range: {rem.min().values:.2f} to {rem.max().values:.2f}")
print(f"REM 90th percentile: {np.percentile(rem.values, 90):.2f}")
print(f"DEM range: {dem.min().values:.2f} to {dem.max().values:.2f}")
