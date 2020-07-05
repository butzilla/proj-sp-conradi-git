# -----------------------------------------------------------
# This script provides functions for the demand layer
#
#
# Johannes Conradi, 2020 ETH Zuerich
# email: conradij@ethz.ch
# -----------------------------------------------------------

import pandas as pd
from shapely.geometry import Point
import zipfile
import geopandas as gpd
from pyproj import Transformer
import numpy as np


def get_demand_trip(dirname,city, points, osm_mapping):
    """This function reads in a demand as OD trip based csv file and maps the OD coordinates to osm ids. It requires the
    demand file to be in the right directory with the right naming conventions. This function works for every country
    except Switzerland."""

    # Directories
    file_path = dirname + '/resources/demand_layer/demand_'+city+'.csv'
    results_df = pd.read_csv(file_path)
    if osm_mapping:
        dropoff_osmid = []
        pickup_osmid = []
        # Find the closest OSM-node to origin and destination of each trip:
        for i, row in results_df.iterrows():
            try:
                dropoff_osmid.append(points['geometry'].distance(
                    Point(row['Dropoff Centroid Longitude'], row['Dropoff Centroid Latitude'])).idxmin())
                pickup_osmid.append(points['geometry'].distance(
                    Point(row['Pickup Centroid Longitude'], row['Pickup Centroid Latitude'])).idxmin())
            except:
                dropoff_osmid.append(float('nan'))
                pickup_osmid.append(float('nan'))

        results_df['dropoff_osmid'] = dropoff_osmid
        results_df['pickup_osmid'] = pickup_osmid
    return results_df

def map_osm_demandgeo(dirname,points):
    """This function maps nodes of the street network to the demand layer regions. Only for Swiss cities."""

    # Directories
    file_path = dirname + '/resources/demand_layer/Verkehrszonen_Schweiz_NPVM_2017.zip'
    dir_unzip = dirname + '/resources/demand_layer'
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(dir_unzip)
    file_path = dirname + '/resources/demand_layer/Verkehrszonen_Schweiz_NPVM_2017_gpkg.zip'
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(dir_unzip)
    file_path = dirname + '/resources/demand_layer/Verkehrszonen_Schweiz_NPVM_2017.gpkg'
    # Kanton of city, change if other then ZH!
    kanton = 'ZH' # TODO ask this in the UI
    # Load data from files
    data = gpd.read_file(file_path)
    data = data[data['N_KT'] == kanton]
    data.drop_duplicates()
    # Transform coordinate frame
    transformer = Transformer.from_crs(4326, 2056)
    points_geox = np.array([point.x for point in points['geometry']])
    points_geoy = np.array([point.y for point in points['geometry']])
    transformed_p = transformer.transform(points_geox, points_geoy)
    Tracts = data['ID_Gem']
    tract = np.empty(len(points), dtype=int)
    Polygons = data['geometry']
    # Mapping of street layer nodes to regions
    for i in range(len(transformed_p[0])):
        point = Point(transformed_p[0][i], transformed_p[1][i])
        for j, poly in enumerate(Polygons):
            if poly.contains(point):
                tract[i] = Tracts[j]

    """ 
    old:
    tracts = pd.DataFrame(tract, columns=['demand_layer_region_id'])
    points_df = pd.DataFrame(points)
    points_df = points_df.reset_index(drop=True)
    objs = [points_df, tracts]
    return pd.concat(objs, axis=1)
    """
    points['demand_layer_region_id'] = tract
    return points






