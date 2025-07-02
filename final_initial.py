import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# Your beautiful color palette
colors = ['#f2f7fb', '#81a8cb', '#37123d']

# Create a custom colormap
custom_cmap = LinearSegmentedColormap.from_list("custom", colors)

# Check your data range
print(f"REM data range: {rem.min().values:.2f} to {rem.max().values:.2f}")

# Option 1: Use the actual data range
print("\n=== Option 1: Visualizing with actual data range ===")
plt.figure(figsize=(12, 10))
im1 = plt.imshow(rem.squeeze(), cmap=custom_cmap, 
                 vmin=rem.min().values, vmax=rem.max().values)
plt.colorbar(im1, label='REM Values')
plt.title('REM Visualization - Full Range')
plt.axis('off')
plt.tight_layout()
plt.show()

# Option 2: Focus on a specific range (e.g., upper values)
print("\n=== Option 2: Focusing on upper range ===")
upper_percentile = np.percentile(rem.values, 90)  # Top 10% of values
plt.figure(figsize=(12, 10))
im2 = plt.imshow(rem.squeeze(), cmap=custom_cmap, 
                 vmin=upper_percentile, vmax=0)
plt.colorbar(im2, label='REM Values (Upper Range)')
plt.title('REM Visualization - Upper Range Focus')
plt.axis('off')
plt.tight_layout()
plt.show()

# Option 3: Normalize the data to 0-10 range if that's what you want
print("\n=== Option 3: Normalized to 0-10 range ===")
# Normalize to 0-10 range
rem_normalized = ((rem - rem.min()) / (rem.max() - rem.min())) * 10
plt.figure(figsize=(12, 10))
im3 = plt.imshow(rem_normalized.squeeze(), cmap=custom_cmap, 
                 vmin=0, vmax=10)
plt.colorbar(im3, label='Normalized REM Values (0-10)')
plt.title('REM Visualization - Normalized Range')
plt.axis('off')
plt.tight_layout()
plt.show()

# Option 4: Using your original shade function with correct span
print("\n=== Option 4: Using shade function with correct parameters ===")
try:
    # With actual range
    shade(rem.squeeze(), cmap=colors, span=[rem.min().values, rem.max().values], how='linear')
    
    # Or with normalized data
    # shade(rem_normalized.squeeze(), cmap=colors, span=[0, 10], how='linear')
except NameError:
    print("shade function not available, using matplotlib instead")

# Option 5: Beautiful subplot comparison
print("\n=== Option 5: Comparison subplot ===")
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

# Full range
im1 = axes[0].imshow(rem.squeeze(), cmap=custom_cmap, 
                     vmin=rem.min().values, vmax=rem.max().values)
axes[0].set_title('Full Range')
axes[0].axis('off')
plt.colorbar(im1, ax=axes[0], fraction=0.046, pad=0.04)

# Upper range
upper_percentile = np.percentile(rem.values, 85)
im2 = axes[1].imshow(rem.squeeze(), cmap=custom_cmap, 
                     vmin=upper_percentile, vmax=0)
axes[1].set_title('Upper 15% Range')
axes[1].axis('off')
plt.colorbar(im2, ax=axes[1], fraction=0.046, pad=0.04)

# Normalized
im3 = axes[2].imshow(rem_normalized.squeeze(), cmap=custom_cmap, 
                     vmin=0, vmax=10)
axes[2].set_title('Normalized (0-10)')
axes[2].axis('off')
plt.colorbar(im3, ax=axes[2], fraction=0.046, pad=0.04)

plt.suptitle('REM Data Visualizations', fontsize=16, y=1.02)
plt.tight_layout()
plt.show()

# Show some statistics
print(f"\nData Statistics:")
print(f"Shape: {rem.shape}")
print(f"Min: {rem.min().values:.2f}")
print(f"Max: {rem.max().values:.2f}")
print(f"Mean: {rem.mean().values:.2f}")
print(f"Std: {rem.std().values:.2f}")
print(f"25th percentile: {np.percentile(rem.values, 25):.2f}")
print(f"75th percentile: {np.percentile(rem.values, 75):.2f}")
print(f"90th percentile: {np.percentile(rem.values, 90):.2f}")
