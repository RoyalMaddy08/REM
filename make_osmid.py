# River OSM ID Finder from TIF File
# This notebook processes a TIF file of a river segment and finds its OSM ID

# Install required packages
!pip install rasterio geopandas shapely osmnx requests folium
!pip install --upgrade overpy

import rasterio
import geopandas as gpd
import numpy as np
from shapely.geometry import Point, Polygon, box
import osmnx as ox
import requests
import json
import folium
from google.colab import files
import overpy
import matplotlib.pyplot as plt
from rasterio.plot import show
from rasterio.features import shapes
from rasterio.transform import from_bounds
import warnings
warnings.filterwarnings('ignore')

print("All packages installed successfully!")

# Function to upload TIF file
def upload_tif_file():
    """Upload TIF file from local system"""
    print("Please upload your TIF file:")
    uploaded = files.upload()
    
    if uploaded:
        filename = list(uploaded.keys())[0]
        print(f"File '{filename}' uploaded successfully!")
        return filename
    else:
        print("No file uploaded.")
        return None

# Function to extract geographic bounds from TIF
def extract_bounds_from_tif(tif_path):
    """Extract geographic bounds from TIF file"""
    try:
        with rasterio.open(tif_path) as src:
            bounds = src.bounds
            crs = src.crs
            
            print(f"File CRS: {crs}")
            print(f"Bounds: {bounds}")
            
            # Convert bounds to lat/lon if needed
            if crs != 'EPSG:4326':
                print("Converting bounds to WGS84 (EPSG:4326)...")
                # Create a polygon from bounds
                minx, miny, maxx, maxy = bounds
                polygon = box(minx, miny, maxx, maxy)
                
                # Create GeoDataFrame and reproject
                gdf = gpd.GeoDataFrame([1], geometry=[polygon], crs=crs)
                gdf = gdf.to_crs('EPSG:4326')
                
                # Get new bounds
                bounds = gdf.total_bounds
                print(f"Converted bounds (WGS84): {bounds}")
            
            return bounds, crs
            
    except Exception as e:
        print(f"Error reading TIF file: {e}")
        return None, None

# Function to visualize TIF file
def visualize_tif(tif_path):
    """Visualize the TIF file"""
    try:
        with rasterio.open(tif_path) as src:
            fig, ax = plt.subplots(figsize=(12, 8))
            show(src, ax=ax, title="River TIF Image")
            plt.show()
            
            # Print basic info
            print(f"Image shape: {src.shape}")
            print(f"Number of bands: {src.count}")
            print(f"Data type: {src.dtypes[0]}")
            
    except Exception as e:
        print(f"Error visualizing TIF: {e}")

# Function to query OSM for rivers using multiple methods
def find_rivers_in_bounds(bounds, buffer_km=1):
    """Find rivers within the given bounds using OSM - multiple methods"""
    minx, miny, maxx, maxy = bounds
    
    # Add buffer to search area (convert km to degrees approximately)
    buffer_deg = buffer_km / 111.0  # Rough conversion
    
    # Create bounding box with buffer
    bbox = (miny - buffer_deg, minx - buffer_deg, 
            maxy + buffer_deg, maxx + buffer_deg)
    
    print(f"Searching for rivers in bbox: {bbox}")
    
    rivers_data = []
    
    # Method 1: Try with Overpass API (simplified query)
    try:
        print("Trying Overpass API method 1...")
        api = overpy.Overpass()
        
        # Simpler query without geometry resolution
        query = f"""
        [out:json][timeout:90];
        (
          way["waterway"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
          relation["waterway"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
        );
        out center meta;
        """
        
        result = api.query(query)
        
        # Process ways
        for way in result.ways:
            waterway_type = way.tags.get('waterway', '')
            if waterway_type in ['river', 'stream', 'creek', 'brook', 'canal']:
                river_info = {
                    'osm_id': way.id,
                    'osm_type': 'way',
                    'name': way.tags.get('name', 'Unnamed'),
                    'waterway_type': waterway_type,
                    'coordinates': [],  # Will get these separately if needed
                    'tags': dict(way.tags),
                    'method': 'overpass_simple'
                }
                rivers_data.append(river_info)
        
        # Process relations
        for relation in result.relations:
            waterway_type = relation.tags.get('waterway', '')
            if waterway_type in ['river', 'stream', 'creek', 'brook', 'canal']:
                river_info = {
                    'osm_id': relation.id,
                    'osm_type': 'relation',
                    'name': relation.tags.get('name', 'Unnamed'),
                    'waterway_type': waterway_type,
                    'coordinates': [],
                    'tags': dict(relation.tags),
                    'method': 'overpass_simple'
                }
                rivers_data.append(river_info)
        
        print(f"Method 1 found {len(rivers_data)} waterways")
        
    except Exception as e:
        print(f"Overpass API method 1 failed: {e}")
    
    # Method 2: Try with OSMnx
    if len(rivers_data) == 0:
        try:
            print("Trying OSMnx method...")
            
            # Create polygon from bounds
            north, south, east, west = bbox[2], bbox[0], bbox[3], bbox[1]
            
            # Get waterway data using OSMnx
            waterways_gdf = ox.features_from_bbox(
                north=north, south=south, east=east, west=west,
                tags={'waterway': True}
            )
            
            if not waterways_gdf.empty:
                for idx, row in waterways_gdf.iterrows():
                    waterway_type = row.get('waterway', '')
                    if waterway_type in ['river', 'stream', 'creek', 'brook', 'canal']:
                        # Extract OSM ID from the index
                        if isinstance(idx, tuple) and len(idx) >= 2:
                            osm_type = 'way' if idx[0] == 'way' else 'relation'
                            osm_id = idx[1]
                        else:
                            osm_type = 'way'
                            osm_id = idx
                        
                        river_info = {
                            'osm_id': osm_id,
                            'osm_type': osm_type,
                            'name': row.get('name', 'Unnamed'),
                            'waterway_type': waterway_type,
                            'coordinates': [],
                            'tags': {k: v for k, v in row.items() if isinstance(v, (str, int, float))},
                            'method': 'osmnx'
                        }
                        rivers_data.append(river_info)
            
            print(f"Method 2 found {len(rivers_data)} waterways")
            
        except Exception as e:
            print(f"OSMnx method failed: {e}")
    
    # Method 3: Direct HTTP request to Overpass API
    if len(rivers_data) == 0:
        try:
            print("Trying direct HTTP request method...")
            
            overpass_url = "http://overpass-api.de/api/interpreter"
            query = f"""
            [out:json][timeout:60];
            (
              way["waterway"]["name"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
              relation["waterway"]["name"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
            );
            out center;
            """
            
            response = requests.post(overpass_url, data=query, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                
                for element in data.get('elements', []):
                    if element.get('tags', {}).get('waterway') in ['river', 'stream', 'creek', 'brook', 'canal']:
                        river_info = {
                            'osm_id': element['id'],
                            'osm_type': element['type'],
                            'name': element.get('tags', {}).get('name', 'Unnamed'),
                            'waterway_type': element.get('tags', {}).get('waterway'),
                            'coordinates': [],
                            'tags': element.get('tags', {}),
                            'method': 'direct_http'
                        }
                        rivers_data.append(river_info)
            
            print(f"Method 3 found {len(rivers_data)} waterways")
            
        except Exception as e:
            print(f"Direct HTTP method failed: {e}")
    
    print(f"Total found: {len(rivers_data)} rivers/waterways in the area")
    return rivers_data, formatted_ids

# Function to create interactive map
def create_interactive_map(bounds, rivers_data):
    """Create an interactive map showing the TIF bounds and found rivers"""
    try:
        minx, miny, maxx, maxy = bounds
        center_lat = (miny + maxy) / 2
        center_lon = (minx + maxx) / 2
        
        # Create map
        m = folium.Map(location=[center_lat, center_lon], zoom_start=12)
        
        # Add TIF bounds as rectangle
        folium.Rectangle(
            bounds=[[miny, minx], [maxy, maxx]],
            color='red',
            fill=True,
            fillOpacity=0.2,
            popup='TIF File Bounds'
        ).add_to(m)
        
        # Add rivers
        colors = ['blue', 'green', 'purple', 'orange', 'darkred']
        for i, river in enumerate(rivers_data):
            if river['coordinates']:
                color = colors[i % len(colors)]
                coords_flipped = [[lat, lon] for lon, lat in river['coordinates']]
                
                folium.PolyLine(
                    coords_flipped,
                    color=color,
                    weight=3,
                    popup=f"OSM ID: {river['osm_id']}<br>Name: {river['name']}<br>Type: {river['waterway_type']}"
                ).add_to(m)
        
        return m
        
    except Exception as e:
        print(f"Error creating map: {e}")
        return None

# Function to get coordinates for a specific waterway
def get_waterway_coordinates(osm_id, osm_type='way'):
    """Get coordinates for a specific waterway"""
    try:
        if osm_type == 'way':
            overpass_url = "http://overpass-api.de/api/interpreter"
            query = f"""
            [out:json];
            way({osm_id});
            out geom;
            """
            
            response = requests.post(overpass_url, data=query, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                elements = data.get('elements', [])
                
                if elements:
                    way = elements[0]
                    if 'geometry' in way:
                        coords = [(node['lon'], node['lat']) for node in way['geometry']]
                        return coords
        
        return []
        
    except Exception as e:
        print(f"Error getting coordinates for {osm_type} {osm_id}: {e}")
        return []
def find_closest_river(bounds, rivers_data):
    """Find the river closest to the center of the TIF bounds"""
    try:
        minx, miny, maxx, maxy = bounds
        center_point = Point((minx + maxx) / 2, (miny + maxy) / 2)
        
        closest_river = None
        min_distance = float('inf')
        
        for river in rivers_data:
            if river['coordinates']:
                # Calculate distance to first point of river (simplified)
                river_point = Point(river['coordinates'][0])
                distance = center_point.distance(river_point)
                
                if distance < min_distance:
                    min_distance = distance
                    closest_river = river
        
        return closest_river, min_distance
        
    except Exception as e:
        print(f"Error finding closest river: {e}")
        return None, None

# Main execution
def main(tif_path="/content/USGS_1_n52w119_20130911.tif"):
    print("=== River OSM ID Finder ===\n")
    
    # Step 1: Check if TIF file exists
    import os
    if not os.path.exists(tif_path):
        print(f"TIF file not found at: {tif_path}")
        print("Please check the file path or upload the file.")
        return
    
    print(f"Processing TIF file: {tif_path}")
    tif_filename = tif_path
    
    # Step 2: Extract bounds from TIF
    print("\n--- Extracting geographic information from TIF ---")
    bounds, crs = extract_bounds_from_tif(tif_filename)
    if bounds is None:
        print("Failed to extract bounds from TIF file.")
        return
    
    # Step 3: Visualize TIF
    print("\n--- Visualizing TIF file ---")
    visualize_tif(tif_filename)
    
    # Step 4: Search for rivers in OSM with multiple methods
    print("\n--- Searching for rivers in OpenStreetMap (multiple methods) ---")
    rivers_data = find_rivers_in_bounds(bounds, buffer_km=5)  # Increased buffer
    
    if not rivers_data:
        print("No rivers found in the specified area.")
        return
    
    # Step 5: Display results in the required format
    print("\n--- Found Rivers (OSM ID Format) ---")
    for i, river in enumerate(rivers_data, 1):
        # Format OSM ID as W123456 or R123456
        osm_prefix = 'W' if river['osm_type'] == 'way' else 'R'
        formatted_osm_id = f"{osm_prefix}{river['osm_id']}"
        
        print(f"{i}. OSM ID: '{formatted_osm_id}'")
        print(f"   Name: {river['name']}")
        print(f"   Type: {river['waterway_type']}")
        print(f"   URL: https://www.openstreetmap.org/{river['osm_type']}/{river['osm_id']}")
        print()
    
    # Step 6: Find closest river with formatted ID
    print("--- Finding closest river to TIF center ---")
    closest_river, distance = find_closest_river(bounds, rivers_data)
    if closest_river:
        osm_prefix = 'W' if closest_river['osm_type'] == 'way' else 'R'
        formatted_closest_id = f"{osm_prefix}{closest_river['osm_id']}"
        
        print(f"Closest river: {closest_river['name']}")
        print(f"OSM ID: '{formatted_closest_id}'")
        print(f"Distance from center: {distance:.6f} degrees")
        print(f"Direct link: https://www.openstreetmap.org/{closest_river['osm_type']}/{closest_river['osm_id']}")
        
        # Return the formatted ID for easy copying
        print(f"\n🎯 READY TO USE: osm_id = '{formatted_closest_id}'")
    
    # Also create a summary list of all formatted IDs
    print(f"\n--- All OSM IDs in Required Format ---")
    formatted_ids = []
    for river in rivers_data:
        osm_prefix = 'W' if river['osm_type'] == 'way' else 'R'
        formatted_id = f"{osm_prefix}{river['osm_id']}"
        formatted_ids.append(formatted_id)
        if len(formatted_ids) <= 10:  # Show first 10
            print(f"osm_id = '{formatted_id}'  # {river['name']} ({river['waterway_type']})")
    
    if len(formatted_ids) > 10:
        print(f"... and {len(formatted_ids) - 10} more")
    
    return formatted_ids
    
    # Step 7: Create interactive map
    print("\n--- Creating interactive map ---")
    map_obj = create_interactive_map(bounds, rivers_data)
    if map_obj:
        print("Interactive map created! Check below.")
        return map_obj
    
    return rivers_data

# Run the main function with your specific file
if __name__ == "__main__":
    # Your specific TIF file path
    tif_file_path = "/content/USGS_1_n52w119_20130911.tif"
    result = main(tif_file_path)

# Additional utility functions

def get_detailed_river_info(osm_id, osm_type='way'):
    """Get detailed information about a specific river from OSM"""
    try:
        api = overpy.Overpass()
        
        if osm_type == 'way':
            query = f"""
            [out:json];
            way({osm_id});
            out geom;
            """
        else:
            query = f"""
            [out:json];
            relation({osm_id});
            out geom;
            """
        
        result = api.query(query)
        
        if osm_type == 'way' and result.ways:
            way = result.ways[0]
            return {
                'osm_id': way.id,
                'tags': dict(way.tags),
                'coordinates': [(float(node.lon), float(node.lat)) for node in way.nodes]
            }
        elif osm_type == 'relation' and result.relations:
            relation = result.relations[0]
            return {
                'osm_id': relation.id,
                'tags': dict(relation.tags),
                'members': len(relation.members)
            }
        
        return None
        
    except Exception as e:
        print(f"Error getting detailed info: {e}")
        return None

# Example usage:
# detailed_info = get_detailed_river_info(123456789, 'way')
# print(json.dumps(detailed_info, indent=2))

print("\n=== Instructions ===")
print("1. Run main() with your TIF file path:")
print("   result = main('/content/USGS_1_n52w119_20130911.tif')")
print("2. The script will process your TIF file automatically")
print("3. You'll get rivers in the area with their OSM IDs")
print("4. Use get_detailed_river_info(osm_id, osm_type) for more details")
print("\n=== Quick Start ===")
print("Simply run: main('/content/USGS_1_n52w119_20130911.tif')")
