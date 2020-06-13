
import pandas as pd
from shapely.geometry import Point
from scipy.spatial import distance

def get_demand(dirname,city, points):
    file_path = dirname + '/resources/demand_layer/demand_'+city+'.csv'
    results_df = pd.read_csv(file_path)
    dropoff_osmid = []
    pickup_osmid = []
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



