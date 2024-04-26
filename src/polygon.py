import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import shapely
import pygeos
from shapely.geometry import Point, Polygon
import folium
from scipy.spatial import ConvexHull

joined = pd.read_csv("out/final_output.csv")

# Function to draw points in the map
def draw_points(map_object, list_of_points, layer_name, line_color, fill_color, text):

    fg = folium.FeatureGroup(name=layer_name)

    for point in list_of_points:
        fg.add_child(folium.CircleMarker(point, radius=3, color=line_color, fill_color=fill_color,
                                         popup=(folium.Popup(text))))

    map_object.add_child(fg)

# Function that takes a map and a list of points (LON,LAT tupels) and
# returns a map with the convex hull polygon from the points as a new layer

def create_convexhull_polygon(map_object, list_of_points, layer_name, line_color, fill_color, weight, text): 

    # Since it is pointless to draw a convex hull polygon around less than 3 points check len of input
    if len(list_of_points) < 3:
        return

    # Create the convex hull using scipy.spatial 
    form = [list_of_points[i] for i in ConvexHull(list_of_points).vertices]

    # Create feature group, add the polygon and add the feature group to the map 
    fg = folium.FeatureGroup(name=layer_name)
    fg.add_child(folium.vector_layers.Polygon(locations=form, color=line_color, fill_color=fill_color,
                                              weight=weight, popup=(folium.Popup(text))))
    map_object.add_child(fg)

    return(map_object)

# Define function to create convex hulls for each group
def create_grouped_convexhulls(map_object, joined, layer_name, line_color, fill_color, weight):
    for label, group in joined.groupby('polygon'):
        points = group[["latitude", "longitude"]].values.tolist()
        create_convexhull_polygon(map_object, points, layer_name=f'{layer_name} ({label})', line_color=line_color,
                                  fill_color=fill_color, weight=weight, text=f'Convex hull for {label}')

# Initialize map
my_convexhull_map = folium.Map(location=[55, -2], zoom_start=6)

points = joined[["latitude", "longitude"]].values.tolist()
list_of_points = points

#dataframe with only tesco extra
just_extra = joined[joined["ordinal_type"] == 3].reset_index(drop=True)
just_extra_points = just_extra[["latitude", "longitude"]].values.tolist()

#dataframe with non-extra stores
non_extra = joined[joined["ordinal_type"] != 3].reset_index(drop=True)
non_extra_points = non_extra[["latitude", "longitude"]].values.tolist()

# Create convex hulls for each group
create_grouped_convexhulls(my_convexhull_map, joined, layer_name="polygon", line_color='skyblue', fill_color='lightskyblue', weight=10)

# Add non-tesco extra store points as markers
draw_points(my_convexhull_map, non_extra_points, layer_name='Non-Extra stores', line_color='#7289da', fill_color='royalblue', text='Non-Tesco Extra')

# Add tesco extra store points as markers
draw_points(my_convexhull_map, just_extra_points, layer_name='Extra stores', line_color='#063970', fill_color='royalblue', text='Tesco Extra')

# Add layer control and show map
folium.LayerControl(collapsed=False).add_to(my_convexhull_map)
my_convexhull_map

