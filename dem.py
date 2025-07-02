dem = rioxarray.open_rasterio("/content/USGS_1_n52w119_20130911.tif")
dem = dem.coarsen(x=3, boundary='trim').mean().coarsen(y=3, boundary='trim').mean()
dem.squeeze().plot.imshow()
