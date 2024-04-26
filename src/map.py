# %%
import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import shapely
import pygeos
from shapely.geometry import Point, Polygon
import folium

df = pd.read_csv("out/tesco_stores.csv")

df["Name"].replace({"Baker Street": "Baker Street Express", 
                    "Barnes Church Road": "Barnes Church Road Express", 
                    "Beckton Extra Gallions Reach": "Beckton Extra Gallions Reach Extra",
                    "Bristol Hatchet Rd": "Bristol Hatchet Rd Express",
                    "Chiswell St Express GetGo": "Chiswell St GetGo Express",
                    "Crookston Road": "Crookston Road Express",
                    "Denmark Hill": "Denmark Hil Express",
                    "Fulham Reach Express GetGo": "Fulham Reach GetGo Express",
                    "High Holborn Express GetGo": "High Holborn GetGo Express",
                    "Ilford Superstore (Barkingside)": "Ilford (Barkingside) Superstore",
                    "Islington": "Islington Express",
                    "Lichfield": "Lichfield Express",
                    "Liverpool Cargo": "Liverpool Cargo Express",
                    "Liverpool Edge Hill": "Liverpool Edge Hill Superstore",
                    "Liverpool Skelhorne": "Liverpool Skelhorne Express",
                    "Narrow Hall Meadow": "Narrow Hall Meadow Express",
                    "New Road Chingford": "New Road Chingford Express",
                    "Nightingale Excel Express (Excel staff only)": "Nightingale Excel Express",
                    "Nightingale NEC Express (NEC staff only)": "Nightingale NEC Express",
                    "North Cornelly": "North Cornelly Express",
                    "Northern Moor": "Northern Moor Express",
                    "Quartz Way": "Quartz Way Express",
                    "Reading Green Park": "Reading Green Park Express",
                    "Romsey Rd Southampton": "Romsey Rd Southampton Express",
                    "Shire Park Express GetGo": "Shire Park GetGo Express",
                    "Southampton Central Station": "Southampton Central Station Express",
                    "Swansea Fabian Way": "Swansea Fabian Way Express",
                    "Swindon Pinehurst": "Swindon Pinehurst Express",
                    "Takeley": "Takeley Express",
                    "Tesco Rawtenstall": "Tesco Rawtenstall Superstore",
                    "Toothill Village Centre": "Toothill Village Centre Express",
                    "Wakefield": "Wakefield Superstore",
                    "Watford North Approach": "Watford North Approach Express",
                    "West Street Horsham": "West Street Horsham Express",
                    "Windsor Peascod": "Windsor Peascod Express"
                    },
                    inplace=True)

df["Name"] = df["Name"].str.title()
df["Type"] = df["Name"].apply(lambda x: x.split()[-1])
df["Type"] = df["Type"].replace({"EXPRESS": "Express", "EXP": "Express", "Exp": "Express"})
type_dict = {"Express":1,
             "Superstore":2,
             "Extra":3}
df["Ordinal_type"] = df["Type"].map(type_dict)
df["Ordinal_type"] = df["Ordinal_type"].astype(np.int64)

df1 = df[["Name", "Ordinal_type", "Postcode", "Geo_position"]]
extra = df1[df1["Ordinal_type"] == 3].reset_index(drop=True)
superstore = df1[df1["Ordinal_type"] == 2].reset_index(drop=True)
express = df1[df1["Ordinal_type"] == 1].reset_index(drop=True)
df1[["Latitude", "Longitude"]] = df["Geo_position"].apply(lambda x : pd.Series(str(x).split(",")))
df1 = df1.drop(columns="Geo_position")

gdf = gpd.GeoDataFrame(df1, geometry=gpd.points_from_xy(df1.Longitude, df1.Latitude))
gdf_all = gdf
gdf_extra = gdf[gdf["Ordinal_type"] == 3].reset_index(drop=True)
gdf_other = gdf[gdf["Ordinal_type"] != 3].reset_index(drop=True)
# %%
from scipy.spatial import cKDTree
from shapely.geometry import Point

geometry_other = np.array(list(gdf_other.geometry.apply(lambda x: (x.x, x.y))))
geometry_extra = np.array(list(gdf_extra.geometry.apply(lambda x: (x.x, x.y))))

btree = cKDTree(geometry_extra)
dist, idx = btree.query(geometry_other, k=1)

extra_nearest = gdf_extra.iloc[idx].drop(columns="geometry").reset_index(drop=True)
gdf = pd.concat([gdf_other.reset_index(drop=True), extra_nearest, pd.Series(dist, name='dist')], axis=1)

# %%
extragdf = gpd.GeoDataFrame(extra_nearest, geometry=gpd.points_from_xy(extra_nearest.Longitude, extra_nearest.Latitude))
gdf.columns = ["other_name", "ordinal_type_other", "other_pc", "other_lat", "other_long", "geometry", "extra_name", "ordinal_type_extra", "extra_pc", "extra_lat", "extra_long", "dist"]
gdf_sorted = gdf.sort_values(by="extra_pc").reset_index(drop=True)
gdf_sorted['check'] = gdf_sorted["extra_pc"].eq(gdf_sorted["extra_pc"].shift())

polygon = []
n = 0
for x in gdf_sorted["check"]:
    if x == False:
        n += 1
    polygon.append(n)
gdf_sorted["polygon"] = polygon

just_extra = gdf_sorted[['ordinal_type_other','ordinal_type_extra', 'extra_name', 'extra_pc', 'extra_lat','extra_long', 'polygon', "geometry", "check", "dist"]]
just_extra = just_extra.drop_duplicates(subset=["extra_pc"], keep="first").reset_index(drop=True)

just_extra["other_name"] = just_extra["extra_name"]
just_extra["other_pc"] = just_extra["extra_pc"]
just_extra["other_lat"] = just_extra["extra_lat"]
just_extra["other_long"] = just_extra["extra_long"]
just_extra["ordinal_type_other"] = "3"

just_extra = just_extra[['ordinal_type_other', 'other_name', 'other_pc', 'other_lat', 'other_long', 'geometry',
       'ordinal_type_extra', 'extra_name', 'extra_pc', 'extra_lat', 'extra_long', 'dist',
       'check', 'polygon']]

joined = pd.concat([gdf_sorted, just_extra])
joined[["ordinal_type_other"]] = joined[["ordinal_type_other"]].astype(int)
joined = joined.sort_values(by=["polygon", "ordinal_type_other"], ascending = [True, False]).reset_index(drop=True)

joined = joined[['ordinal_type_other', 'other_name', 'other_pc', 'other_lat', 'other_long', 'geometry', 'polygon']]
joined = joined.rename(columns={"ordinal_type_other": "ordinal_type", 'other_name':'store_name', "other_pc": "post_code", "other_lat": "latitude", "other_long": "longitude"})
joined['check'] = joined["polygon"].eq(joined["polygon"].shift())
joined["polygon_joins"] = joined.dissolve("polygon").convex_hull
joined = joined[['ordinal_type', 'store_name', 'post_code', 'latitude', 'longitude',
       'geometry', 'polygon']]

eighty_percentile = gdf_sorted[['other_name', 'ordinal_type_other', 'other_pc', 'other_lat',
       'other_long', 'geometry', 'extra_name', 'ordinal_type_extra',
       'extra_pc', 'extra_lat', 'extra_long', 'dist', 'polygon']]

eighty_percentile = eighty_percentile.sort_values(by=["polygon", "dist"], ascending=[True, True]).reset_index(drop=True)

eighty_percentile_list = []
for label, group in eighty_percentile.groupby('polygon'):
        max_dist = group["dist"].max()
        eighty_percentile_dist = (max_dist * 0.8)
        
        subset = group.loc[group["dist"] <= eighty_percentile_dist]

        eighty_percentile_list.append(subset)

eighty_percentile = pd.concat(eighty_percentile_list).sort_values(by=["polygon", "dist"], ascending=[True, True]).reset_index(drop=True)

just_extra1 = eighty_percentile[['ordinal_type_other','ordinal_type_extra', 'extra_name', 'extra_pc', 'extra_lat','extra_long', 'polygon', "geometry", "dist"]]

just_extra1 = just_extra1.drop_duplicates(subset=["extra_pc"], keep="first").reset_index(drop=True)

just_extra1["other_name"] = just_extra1["extra_name"]
just_extra1["other_pc"] = just_extra1["extra_pc"]
just_extra1["other_lat"] = just_extra1["extra_lat"]
just_extra1["other_long"] = just_extra1["extra_long"]
just_extra1["ordinal_type_other"] = "3"

just_extra1 = just_extra1[['ordinal_type_other', 'other_name', 'other_pc', 'other_lat', 'other_long', 'geometry',
       'ordinal_type_extra', 'extra_name', 'extra_pc', 'extra_lat', 'extra_long', 'dist', 'polygon']]

joined_eighty = pd.concat([eighty_percentile, just_extra1])
joined_eighty[["ordinal_type_other"]] = joined_eighty[["ordinal_type_other"]].astype(int)
joined_eighty = joined_eighty.sort_values(by=["polygon", "ordinal_type_other"], ascending = [True, False]).reset_index(drop=True)

joined_eighty = joined_eighty[['ordinal_type_other', 'other_name', 'other_pc', 'other_lat', 'other_long', 'geometry', 'polygon']]

joined_eighty = joined_eighty.rename(columns={"ordinal_type_other": "ordinal_type", 'other_name':'store_name', "other_pc": "post_code", "other_lat": "latitude", "other_long": "longitude"})

joined_eighty = joined_eighty[['ordinal_type', 'store_name', 'post_code', 'latitude', 'longitude',
       'geometry', 'polygon']]
# %%
import random
from scipy.spatial import ConvexHull

# Function to draw points in the map
def draw_points(map_object, joined_eighty, list_of_points, layer_name, line_color, fill_color):

    fg = folium.FeatureGroup(name=layer_name)

    for store in joined_eighty['store_name']:
        text = store

    for point in list_of_points:
        fg.add_child(folium.CircleMarker(point, radius=3, color=line_color, fill_color=fill_color, popup=(folium.Popup(text))))

    map_object.add_child(fg)

# Function that takes a map and a list of points (LON,LAT tupels) and
# returns a map with the convex hull polygon from the points as a new layer

def create_convexhull_polygon(map_object, list_of_points, layer_name, line_color, fill_color, weight): 

    # Since it is pointless to draw a convex hull polygon around less than 3 points check len of input
    if len(list_of_points) < 3:
        return

    # Create the convex hull using scipy.spatial 
    form = [list_of_points[i] for i in ConvexHull(list_of_points).vertices]

    # Add the polygons to the
    fg = folium.FeatureGroup(name=layer_name)
    fg.add_child(folium.vector_layers.Polygon(locations=form, color=line_color, fill_color=fill_color, weight=weight))
    map_object.add_child(fg)

    return(map_object)

#Same as above but got rid of layer control
def create_grouped_convexhulls(map_object, joined_eighty, layer_name, line_color, fill_color, weight):
    for label, group in joined_eighty.groupby('polygon'):
        points = group[["latitude", "longitude"]].values.tolist()
        create_convexhull_polygon(map_object, points, layer_name=layer_name, line_color=line_color, fill_color=fill_color, weight=weight)

# Initialize map
my_convexhull_map = folium.Map(location=[55, -2], zoom_start=6)

points = joined_eighty[["latitude", "longitude"]].values.tolist()
list_of_points = points

#dataframe with only tesco extra
just_extra = joined_eighty[joined_eighty["ordinal_type"] == 3].reset_index(drop=True)
just_extra_points = just_extra[["latitude", "longitude"]].values.tolist()

#dataframe with non-extra stores
non_extra = joined_eighty[joined_eighty["ordinal_type"] != 3].reset_index(drop=True)
non_extra_points = non_extra[["latitude", "longitude"]].values.tolist()

# Create convex hulls for each group
create_grouped_convexhulls(my_convexhull_map, joined_eighty, layer_name='Polygons', line_color='skyblue', fill_color='lightskyblue', weight=10)

# Add non-tesco extra store points as markers
draw_points(my_convexhull_map, joined_eighty, non_extra_points, layer_name='Non-Extra stores', line_color='#7289da', fill_color='royalblue')

# Add tesco extra store points as markers
draw_points(my_convexhull_map, joined_eighty, just_extra_points, layer_name='Extra stores', line_color='#063970', fill_color='royalblue')

# Add layer control and show map
folium.LayerControl(collapsed=False).add_to(my_convexhull_map)
my_convexhull_map.save('map.html')
#my_convexhull_map.save('map.html')


# %%
