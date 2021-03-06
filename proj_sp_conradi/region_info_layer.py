# -----------------------------------------------------------
# This script provides functions for adding additional
# information to OSM street graph.
#
#
# Johannes Conradi, 2020 ETH Zuerich
# email: conradij@ethz.ch
# -----------------------------------------------------------

import numpy as np
import math
import geopandas as gpd
import os
import shapefile
from shapely.geometry.polygon import Polygon
import pandas as pd
import censusdata


def velocity_from_type(velocities_list, key, maxspeed):
    """
    This function matches roadsegment type with a speed limit.
    """
    if math.isnan(maxspeed):
        if key in velocities_list:
            return kph2ms(velocities_list[key])
        else:
            print('The velocity for the road type ' + key + ' is not defined.')
            return kph2ms(20.0)
    else:
        return kph2ms(maxspeed)


def kph2ms(v):
    """
    This function converts velocity from kph to m/s.
    """
    return v / 3.6


def get_speed_time(edges):
    """
    This function appends the speed limit and the travel time for each road-segment.
    """
    v_dict = {'motorway': 60,
              'trunk_link': 50,
              'primary': 50.0,
              'primary_link': 50.0,
              'secondary': 50.0,
              'secondary_link': 50.0,
              'tertiary': 50.0,
              'tertiary_link': 50.0,
              'unclassified': 30.0,
              'residential': 30.0,
              'living_street': 20.0,
              'service': np.nan,
              'motorway_link': 50.0,
              'trunk': 80.0,
              # 'road': 25.0,
              # additional: doesnt work like this..
              '[residential, tertiary]': 25.0,
              '[residential, unclassified]': 25.0,
              '[secondary, tertiary]': 25.0,
              '[primary, secondary]': 25.0,
              'junction': 15.0,
              '[residential, living_street]': 15.0,
              '[motorway, motorway_link]': 35.0,
              '[unclassified, tertiary]': 25.0,
              '[motorway_link, trunk_link]': 20.0,
              '[secondary, motorway_link]': 25.0,
              '[residential, secondary_link]': 25.0,
              '[primary, motorway_link]': 30.0,
              '[residential, unclassified]': 30.0,
              'bus_guideway ': 15.0,
              'invalid': np.nan}

    speed = []  # In m/s
    time = []  # In sec
    types = edges['highway']
    length = edges['length']
    maxspeed = edges['maxspeed']

    for i in range(len(types)):
        e = types[i]
        if isinstance(maxspeed[i], list):
            maxs = 20  # TODO exceptions?
        else:
            maxs = maxspeed[i]
        speed.append(velocity_from_type(v_dict, str(e), float(maxs)))
        time.append(length[i] / float(speed[i]))
    edges['speed'] = speed
    edges['time'] = time

    return edges

def build_parking(edges, city, dirname):
    """
    This function adds the number of parking spots available at each road segment to egdes. Currently only for ZH.
    """

    # Directories
    addtional_info_path = 'resources/additional_info'
    open_parking_house_filename = 'oeffentliche_parkhaeser_' + city + '.json'
    open_parking_filename = 'oeffentliche_parkplätze_' + city + '.json'
    output_filename = 'parking_' + city + '.csv'
    folder_path = os.path.join(dirname, addtional_info_path)
    open_parking_house_file_path = os.path.join(folder_path, open_parking_house_filename)
    open_parking_file_path = os.path.join(folder_path, open_parking_filename)
    output_path = os.path.join(folder_path, output_filename)
    open_parking_df = gpd.read_file(open_parking_file_path)
    open_parking_house = gpd.read_file(open_parking_house_file_path)
    edges['parking'] = np.zeros((len(edges['geometry'])))

    print('adding parking spots to edges, this may take a while...')

    # Find closest edge to parking spot for open parking
    for i in range(len(open_parking_df['geometry'])):
        dist = (edges['geometry']).distance(open_parking_df['geometry'][i])
        edges.loc[dist.idxmin(), 'parking'] += 1
    # Find closest edge to parking spot for parking houses
    for i in range(len(open_parking_house['geometry'])):
        dist = (edges['geometry']).distance(open_parking_house['geometry'][i])
        edges.loc[dist.idxmin(), 'parking'] += open_parking_house['anzahl_oeffentliche_pp'][i]

    parking = edges['parking']
    parking.to_csv(output_path)
    return edges


def get_parking(edges, dirname, city):
    """
    This function adds the number of parking spots available at each road segment to egdes. It reads in from a
    pre-computed csv. See get_parking.py for creation of csv.
    """

    # Directories
    addtional_info_path = 'resources/additional_info'
    output_filename = 'parking_' + city + '.csv'
    folder_path = os.path.join(dirname, addtional_info_path)
    output_path = os.path.join(folder_path, output_filename)

    # Read in parking from csv
    if os.path.isfile(output_path):
        parking = pd.read_csv(output_path)
        edges['parking'] = parking['0.0']
        return edges
    else:
        return build_parking(edges, city, dirname)


def get_geom(dirname, city):
    """
    This function reads geografic regions and additional information for Zurich city and returns merged DataFrame
    """
    # Directories
    addtional_info_path = 'resources/additional_info'
    folder_path = os.path.join(dirname, addtional_info_path)
    dir_pop = 'population_' + city + '.csv'
    dir_geom = 'geo_' + city + '.json'
    dir_income = 'income_' + city + '.csv'
    dir_housing = 'housing_' + city + '.csv'
    dir_pop = os.path.join(folder_path, dir_pop)
    print(dir_pop)
    dir_geom = os.path.join(folder_path, dir_geom)
    dir_income = os.path.join(folder_path, dir_income)
    dir_housing = os.path.join(folder_path, dir_housing)

    merges = 0

    # Get geographic regions
    if os.path.isfile(dir_geom):
        geomdf = gpd.read_file(dir_geom)

        # Get income data for most recent year. These are quantil values in thousand franks/year.
        if os.path.isfile(dir_income):
            incomedf = pd.read_csv(dir_income)
            incomedf2017 = incomedf[incomedf['SteuerJahr'] == 2017]
            SteuerEInkommen_p50_G = incomedf2017[['SteuerEInkommen_p50', 'QuarSort']][incomedf2017['SteuerTarifSort'] == 0]
            SteuerEInkommen_p50_G = SteuerEInkommen_p50_G.rename(
                columns={"SteuerEInkommen_p50": "SteuerEInkommen_p50_Grundtarif"})
            SteuerEInkommen_p50_V = incomedf2017[['SteuerEInkommen_p50', 'QuarSort']][incomedf2017['SteuerTarifSort'] == 1]
            SteuerEInkommen_p50_V = SteuerEInkommen_p50_V.rename(
                columns={"SteuerEInkommen_p50": "SteuerEInkommen_p50_Verheiratetentarif"})
            SteuerEInkommen_p50_EF = incomedf2017[['SteuerEInkommen_p50', 'QuarSort']][incomedf2017['SteuerTarifSort'] == 2]
            SteuerEInkommen_p50_EF = SteuerEInkommen_p50_EF.rename(
                columns={"SteuerEInkommen_p50": "SteuerEInkommen_p50_Einelternfamilientarif"})

            # Map income data to geographic regions
            merges = geomdf.merge(SteuerEInkommen_p50_G, left_on='qnr', right_on='QuarSort')
            merges = merges.drop('QuarSort', axis=1)
            merges = merges.merge(SteuerEInkommen_p50_V, left_on='qnr', right_on='QuarSort')
            merges = merges.drop('QuarSort', axis=1)
            merges = merges.merge(SteuerEInkommen_p50_EF, left_on='qnr', right_on='QuarSort')
            merges = merges.drop('QuarSort', axis=1)
            merges = merges.set_index('qnr')

        # Get population data for most recent year
        if os.path.isfile(dir_pop):
            populationdf = pd.read_csv(dir_pop)
            populationdf2019 = populationdf[populationdf['StichtagDatJahr'] == 2019]
            pop_QuarSort = populationdf2019.groupby('QuarSort').sum()
            pop_QuarSort = pop_QuarSort['AnzBestWir']

            # Map population data to geographic region

            merges = merges.join(pop_QuarSort)
            merges = merges.rename(columns={"AnzBestWir": "AnzBev"})

        # Get housing data for most recent year
        if os.path.isfile(dir_housing):
            housingdf = pd.read_csv(dir_housing)
            housingdf2019 = housingdf[housingdf['Jahr'] == 2019]
            housingdf2019 = housingdf2019.set_index('Quartier_Nummer')
            housingdf2019 = housingdf2019['Medianqmp']

            # Map housing data to geographic regions
            merges = merges.join(housingdf2019, rsuffix='Medianqmp')
    else:
        print('Error: No geographic information found')

    return merges

def get_geom_us(dirname, city, county, state, var):
    """
    This function reads geografic regions and gets additional information for US cities and returns merged DataFrame
    """

    geo = censusdata.censusgeo([('state', state), ('county', county), ('tract', '*')])
    # var comes from user input, if not user did not input var
    if var:
        var = var.split(",")
    # Default options
    var = ['B01001_001E', 'B06011_001E', 'B25064_001E'] + var
    # Download data from US Census Bureau
    add_info = censusdata.download('acs5', 2015, geo, var)
    # Get Tractindex from text
    tractindex = []
    for i in range(len(add_info)):
        tract = str(add_info.index[i])
        tractindex.append(tract.rsplit('tract:', 1)[1])
    # Construct df with correct naming
    add_info['tractindex'] = tractindex
    add_info = add_info.rename(columns={'B01001_001E': 'population'})
    add_info = add_info.rename(columns={'B06011_001E': 'income $/year'})
    add_info = add_info.rename(columns={'B25064_001E': 'median gross rent $/month'})
    return add_info

def get_geo_node_us(dirname, points, state, county, simplify):
    """
        This function maps a each node to a geographic region. For US only.
    """
    # Directories
    shapepath = dirname + '/resources/additional_info/state_'+ state + '/cb_2015_'+state+'_tract_500k'
    # Read in shapefile
    sf = shapefile.Reader(shapepath)
    Polygons = []
    Tracts = []
    shapes = sf.shapes()
    records = sf.records()
    tract = np.zeros(len(points))

    # Map each node to a tract
    for i in range(len(shapes)):
        shape = shapes[i]
        rec = records[i]
        if rec[0] == state and rec[1] == county:
            Polygons.append(Polygon(shape.points))
            Tracts.append(rec[2])
    if simplify:
        for i, point in enumerate(points):
            for j, poly in enumerate(Polygons):
                if poly.contains(point):
                    tract[i] = Tracts[j]
    else:
        for i, point in enumerate(points['geometry']):
            for j, poly in enumerate(Polygons):
                if poly.contains(point):
                    tract[i] = Tracts[j]

    points['tract'] = tract
    return points


def get_geo_node(points, geomdf, simplify):
    """
    This function maps a each node to a geographic region.
    """
    polygons = geomdf['geometry']
    qnr = geomdf.index
    tract = np.zeros(len(points))

    if simplify:
        for i, point in enumerate(points):
            for j, poly in enumerate(polygons):
                if poly.contains(point):
                    tract[i] = qnr[j]
    else:
        for i, point in enumerate(points['geometry']):
            for j, poly in enumerate(polygons):
                if poly.contains(point):
                    tract[i] = qnr[j]
    points['qnr'] = tract
    return points