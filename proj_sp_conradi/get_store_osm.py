# -----------------------------------------------------------
# This script downloads OSM data and stores the data in graphml
# format
#
#
# Johannes Conradi, 2020 ETH Zuerich
# email: conradij@ethz.ch
# -----------------------------------------------------------

import osmnx as ox


def get_store_osm(folder_path, filename, city, n_type):
    # Get OSM layer
    G = ox.graph_from_place(city, network_type=n_type, simplify=False)

    # Save as graph ml
    ox.save_graphml(G, filename=filename, folder=folder_path, gephi=False)
