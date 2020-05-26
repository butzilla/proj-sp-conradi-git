
import numpy as np
import math
import pandas as pd
import geopandas as gpd



def velocity_from_type(velocities_list, key, maxspeed):
    """
    This function looks matches roadsegment type with a speed limit.
    """
    if math.isnan(maxspeed):
        # print('Maxspeed not given')
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
            maxs = 20  # Discuss exceptions
        else:
            maxs = maxspeed[i]
        speed.append(velocity_from_type(v_dict, str(e), float(maxs)))
        time.append(length[i] / float(speed[i]))
    edges['speed'] = speed
    edges['time'] = time

    return edges


def get_parking(edges):
    """
    This function adds the number of parking spots available at each road segment to egdes. It reads in from a
    pre-computed csv. See get_parking.py for creation of csv.
    """
    dir_open_parking = '/Users/johannesconradi/proj-sp-conradi/Zurich/Output/parking.csv'
    parking = pd.read_csv(dir_open_parking)
    edges['parking'] = parking['0.0']

    return edges


def get_geom():
    """
    This function reads geografic regions and additional information for Zurich city and returns merged DataFrame
    """
    # Directories
    dir_pop = '/Users/johannesconradi/proj-sp-conradi/Zurich/censusdata/City/bev390od3903.csv'
    dir_geom = '/Users/johannesconradi/proj-sp-conradi/Zurich/Geo/stzh.adm_statistische_quartiere_v.json'
    dir_income = '/Users/johannesconradi/proj-sp-conradi/Zurich/censusdata/City/wir100od1003.csv'
    dir_housing = '/Users/johannesconradi/proj-sp-conradi/Zurich/censusdata/City/bau515od5151.csv'

    # Get geographic regions
    geomdf = gpd.read_file(dir_geom)

    # Get income data for most recent year
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
    populationdf = pd.read_csv(dir_pop)
    populationdf2019 = populationdf[populationdf['StichtagDatJahr'] == 2019]
    pop_QuarSort = populationdf2019.groupby('QuarSort').sum()
    pop_QuarSort = pop_QuarSort['AnzBestWir']

    # Map population data to geographic regions
    merges = merges.join(pop_QuarSort)
    merges = merges.rename(columns={"AnzBestWir": "AnzBev"})

    # Get housing data for most recent year
    housingdf = pd.read_csv(dir_housing)
    housingdf2019 = housingdf[housingdf['Jahr'] == 2019]
    housingdf2019 = housingdf2019.set_index('Quartier_Nummer')
    housingdf2019 = housingdf2019['Medianqmp']

    # Map housing data to geographic regions
    merges = merges.join(housingdf2019, rsuffix='Medianqmp')

    return merges


def get_geo_node(points, geomdf):
    """
    This function maps a each node to a geographic region.
    """
    polygons = geomdf['geometry']
    qnr = geomdf.index
    tract = np.zeros(len(points))

    for i, point in enumerate(points):
        for j, poly in enumerate(polygons):
            if poly.contains(point):
                tract[i] = qnr[j]