"""
Helper functions that should probably come from airtools when it is initiated.
Could also go somewhere else.
"""
#from numpy import float
from typing import Dict
import pandas as pd
from shapely.geometry import Polygon, Point, box #polygon#, box
#from sector_shape import NewSectorShape

def decimal_degrees(dms_str):
    '''
    Convert the DMS format into decimal degrees for longitude and latitude
    '''
    if dms_str is None:
        return None

    len_str=len(dms_str)
    dms_sec=float(dms_str[-3:-1])/3600
    dms_min=float(dms_str[-5:-3])/60
    dms_deg=float(dms_str[-len_str:-5])
    dec_deg=dms_sec+dms_min+dms_deg
    if dms_str[len_str-1] == 'W' or dms_str[len_str-1] == 'S':
        dec_deg = dec_deg* -1.0
    return dec_deg

def lat_long(dms_str):
    '''
    Get the lat and long from the data
    '''
    if dms_str is None:
        return None

    ll_coords = dms_str.split(',')
    if ll_coords[0][-1]=='W' or ll_coords[0][-1]=='E':
        long=ll_coords[0]
        lat=ll_coords[1]
    else:
        long=ll_coords[1]
        lat=ll_coords[0]
    return[decimal_degrees(lat),decimal_degrees(long)]

def one_shot(dms_str):
    """
    Putting the first two functions together
    """
    lat_r=[]
    long_r=[]
    l_split=dms_str.split(";")
    for i in l_split:
        tmp=lat_long(i)
        lat_r.append(tmp[0])
        long_r.append(tmp[1])
    polygon_geom = Polygon(zip(long_r, lat_r))
    return polygon_geom

def load_sector(file_path="sectors.csv", sector_name: str =None, sector_part: int =None):
    """
    Load sectors data, convert units to decimal degrees, save shape as Polygon.
    and return as a shapely polygon, and the upper and lower flight levels
    """
    if sector_name is None:
        sector_name = True
    if sector_part is None:
        sector_part = True
    ip_sectors = pd.read_csv(file_path)
    sectors=ip_sectors.copy()
    sectors = sectors[~sectors['sectorname'].isin(['27/32', 'MORAY LOW'])]
    sectors['geometry'] = sectors['vertices_deg_min_sec'].apply(one_shot)
    sector_polygon = sectors[(sectors['sectorname'] == sector_name) &
                    (sectors['part'] == sector_part)]
    # Return the polygon object, upper and lower flight limits
    op_polygon = sector_polygon['geometry'].values[0]
    op_floor = sector_polygon['floor_fl'].values[0]
    op_ceiling = sector_polygon['ceiling_fl'].values[0]
    return op_polygon, op_floor, op_ceiling

def load_waypoints():
    """
    Just load all the waypoints which are a list of 3/5 character names and coordinates
    Use a seperate method to identify which ones fall within the sector defined.
    """
    wpts = pd.read_csv("waypoints.csv")
    wpts['lat_dd'] = wpts['lat'].apply(decimal_degrees)
    wpts['long_dd'] = wpts[' long'].apply(decimal_degrees)
    wpts['geometry'] = [Point(lon,lat) for lon,lat in zip(wpts['long_dd'], wpts['lat_dd'])]
    return wpts


sector_poly, floor, ceiling = load_sector(sector_name="11", sector_part=1)
# print("sector poly = ", sector_poly)
# print("floor = ", floor)
# print("ceiling = ", ceiling)

waypoints = load_waypoints()

def get_boundary_waypoints(boundary_polygon: Polygon, waypoints: Dict):
    """
    Method to return a dictionary of all waypoints in a given boundary
    """
    boundary_waypoints = {}
    for index, row in waypoints.iterrows():
        if boundary_polygon.contains(row['geometry']) or boundary_polygon.intersects(row['geometry']):
            boundary_waypoints[row['waypointname']]=row['geometry']
    
    return boundary_waypoints


def make_bound_box(sector_polygon: Polygon, boundlim: float):
    """
    Take in an arbitary sector shape (polygon with long and lat)
    Output a bounding quadrilateral based on polygon boundaries
    Buffer zone is calculated in degrees
    """
    #longitude = E/W (or x) London longitude = 0 degrees ish
    #latitude = N/S (or y) London latitude = 51 degrees ish
    bounding_box = list(sector_polygon.bounds)
    bounding_box[0]=bounding_box[0]-boundlim
    bounding_box[1]=bounding_box[1]-boundlim
    bounding_box[2]=bounding_box[2]+boundlim
    bounding_box[3]=bounding_box[3]+boundlim
    op_bb = box(bounding_box[0], bounding_box[1], bounding_box[2], bounding_box[3])
    return op_bb

field_of_view = make_bound_box(sector_poly, 0.25)

sector_waypoints = get_boundary_waypoints(sector_poly, waypoints)
fov_waypoints = get_boundary_waypoints(field_of_view, waypoints)

print(len(sector_waypoints), len(fov_waypoints), len(waypoints))

# with open('test.svg', 'w') as f:
#     f.write(sector_poly._repr_svg_())
# with open('rect.svg', 'w') as f:
#     f.write(field_of_view._repr_svg_())