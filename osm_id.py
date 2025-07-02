osm_id = 'R2183775' 

river = ox.geocode_to_gdf(osm_id, by_osmid=True)
river = river.to_crs(dem.rio.crs)

river.plot()
