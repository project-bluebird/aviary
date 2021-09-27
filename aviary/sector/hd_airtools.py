"""
Helper functions that should probably come from airtools when it is initiated.
Could also go somewhere else.
"""
#from numpy import float
from typing import Dict
from numpy.core.numeric import cross
import pandas as pd
from shapely.geometry import Polygon, Point, box, LineString, linestring #polygon#, box
import shapely.geometry as geom
from shapely.prepared import prep
from aviary.sector.route import Route
import numpy as np

# !---! From sector_shape.py !--!
def create_fixes(fix_names, fix_points):
    if len(fix_names) != len(fix_points):
        raise ValueError(f'fix_names must have length {len(fix_points)}')
    return dict(zip([fix_name.upper() for fix_name in fix_names],
                            [fix for fix in fix_points]))


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

def load_sector(file_path="sectors.csv", sector_name: str = None, sector_part: int = None):
    """
    Load sectors data, convert units to decimal degrees, save shape as Polygon.
    and return as a shapely polygon, and the upper and lower flight levels
    """
    if sector_name is None:
        sector_name = True
    # Default sector part is 1
    if sector_part is None:
        sector_part = 1
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
    Returns a pandas dataframe with the waypoint information, and a list of fix names
    as strings and a list of fix coordinates as shapely.geometry.point.Point objects
    whose indexes match
    Also returns a fix dictionary
    """
    wpts = pd.read_csv("waypoints.csv")
    wpts['lat_dd'] = wpts['lat'].apply(decimal_degrees)
    wpts['long_dd'] = wpts[' long'].apply(decimal_degrees)
    wpts['geometry'] = [Point(lon,lat) for lon,lat in zip(wpts['long_dd'], wpts['lat_dd'])]
    fix_names = list(wpts['waypointname'].values)
    fix_points = list(wpts['geometry'].values)

    fix_dict={}
    for index, row in wpts.iterrows():
        fix_dict[row['waypointname']]=row['geometry']
    
    return wpts, fix_names, fix_points, fix_dict


# Generate a sector polygon
ip_sectorname="11"
sector_poly, floor, ceiling = load_sector(sector_name=ip_sectorname, sector_part=1)

# Load the waypoints (fixes)
waypoints, all_fix_names, all_fix_points, all_fix_dict = load_waypoints()

def get_boundary_waypoints(boundary_polygon: Polygon, waypoints: Dict):
    """
    Method to return a dictionary of all waypoints in a given boundary
    Also returns the fix_name and the fix_points
    """
    boundary_waypoints = {}
    for index, row in waypoints.iterrows():
        if boundary_polygon.contains(row['geometry']) or boundary_polygon.intersects(row['geometry']):
            boundary_waypoints[row['waypointname']]=row['geometry']
    
    boundary_fix_names = list(boundary_waypoints.keys())
    boundary_fix_points = list(boundary_waypoints.values())
    return boundary_waypoints, boundary_fix_names, boundary_fix_points


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

# Generate the rectanguar field of view
field_of_view = make_bound_box(sector_poly, 0.25)

# Get all waypoints in a sector 
sector_waypoints, sector_fix_names, sector_fix_points = get_boundary_waypoints(sector_poly, waypoints)
# Get all waypoints in the rectangular field of view (fov)
fov_waypoints, fov_fix_names, fov_fix_points = get_boundary_waypoints(field_of_view, waypoints)

# print("For this particular sector, the 3 waypoints, FOV waypoints and total waypoints = ")
# print(len(sector_waypoints), len(fov_waypoints), len(waypoints))

# with open('test.svg', 'w') as f:
#     f.write(sector_poly._repr_svg_())
# with open('rect.svg', 'w') as f:
#     f.write(field_of_view._repr_svg_())


hd_all_fixes = create_fixes(all_fix_names, all_fix_points)
sector_all_fixes = create_fixes(sector_fix_names, sector_fix_points)



def get_boundary_routes(boundary_fix_name: str, all_fix_dict):
    """
    Read and load the routes data for all sectors and output a fix list
    for those that appear within the boundary that has been given (either
    the sector or the bounding box)
    Save each route as a list of (str, shapely.point.Point) pairs and return
    in format [Route(fix_list), Route(fix_list),…]
    """
    if len(boundary_fix_name) == 0:
        raise ValueError(f'There are no waypoints within the specified boundary')
    all_routes = pd.read_csv("routes.csv")
    # Split the list of waypoints to the split_points column
    # This might be overkill but I don't want to accidentally pick up an erroneous 3 character string from a 5 character point
    all_routes['split_points']=all_routes['Route_Points'].apply(split_fixes)
    #Check to see if any of the boundary_fix_names appear in the split_points column
    mask = all_routes['split_points'].apply(lambda x: any([k in x for k in boundary_fix_name]))
    bounded_routes = all_routes[mask]
    # print(bounded_routes)
    num_routes=len(bounded_routes)

    # Get the shapely point for each of the fixes(split points)
    op_bounded_routes = []
    for index, row in bounded_routes.iterrows():
        fix_list = []
        fix_points = []
        fix_names=row['split_points']
        for names in fix_names:
            fix_point = all_fix_dict.get(names)
            fix_points.append(fix_point)
            entry=(names, fix_point)
            fix_list.append(entry)
        op_bounded_routes.append(Route(fix_list))
    # print("num routes = ", num_routes)
    return op_bounded_routes

def split_fixes(delimited_fix_list: str):
    op=[]
    ssplit=delimited_fix_list.split(';')
    for i in ssplit:
        op.append(i)
    return op

print('************')
print("There are ", len(sector_fix_names), " fixes in sector ", ip_sectorname, " = ", sector_fix_names)
get_boundary_routes(sector_fix_names, all_fix_dict)
# eg_fix_list=['DVR', 'LONAM']
# eg_route_list = get_boundary_routes(eg_fix_list, all_fix_dict)
# print("bounded routes = " , eg_route_list)
sector_route_list = get_boundary_routes(sector_fix_names, all_fix_dict)
print("There are ", len(sector_route_list), " routes in sector ", ip_sectorname)

print("There are ", len(fov_fix_names), " fixes in the sector and surrounding field of view for ", ip_sectorname, " = ", fov_fix_names)
fov_route_list = get_boundary_routes(fov_fix_names, all_fix_dict)
print("There are ", len(fov_route_list), " routes in the field of view surrounding sector ", ip_sectorname)

def get_pseudo_fix(boundary_polygon, boundary_route_list):
    """
    Generate a list of psuedo fixes (waypoints) that are on routes that cross a sector boundary
    Input:
    sector polygon (to work out where the edges intecept)
    sector waypoint ??? might not need as have route list which has waypoints in it
    route list (as this in my definition includes any route that has at least 1 waypoint/fix in the polygon)
    output:
    pseudo_fixes. Naming convention = inside-poly-name_outside-poly-name

    Assumes routes are 'linear' not 'circular' 
    Ignore waypoints that are already on the sector edge
    """
    # Loop through all waypoints on each route and give them a true/false if they are inside the
    # sector polygon (waypoints on the polygon edge count as inside)
    # Then do a line/point comparison between the polygon and any adjacent True/False waypoints

    ring = LineString(list(boundary_polygon.exterior.coords))

    pseudo_fix_list=[]
    pseudo_fix_points=[]

    for i, route in enumerate(sector_route_list):
        # Get the individual route list
        ind_route_fix_list = route.__dict__.get('fix_list')
        fix, coords = zip(*ind_route_fix_list)
        # Make a boolean mask to only look at points that cross the polgon boundary
        fixmask=[]
        for point in coords:
            fixmask.append(boundary_polygon.contains(point)) # May need to add a bit here about not intersecting
        # Look for where it changes from true to false
        crossover=np.argwhere(np.diff(fixmask)).squeeze()
        for _ in range(crossover.size):
            first=crossover.item(_)
            second = first +1
            pos1=coords[first]
            pos2=coords[second]
            l=LineString([pos1, pos2])
            pseudopoint=l.intersection(ring)
            pseudoname=fix[first]+"_"+fix[second]
            pseudo_fix_list.append(pseudoname)
            pseudo_fix_points.append(pseudopoint)
            print(pseudoname, pseudopoint)
        #     print(crossover, crossover.size)

    print(pseudo_fix_list)
    print(len(pseudo_fix_points))
    return(77)
    
pseudo= get_pseudo_fix(sector_poly, sector_route_list)
print(pseudo)

# polygon = [(-1571236.8349707182, 8989180.222117377), (1599362.9654156454, 8924317.946336618), (-1653179.0745812152, 8922145.163675062), (-1626237.6614402141, 8986445.107619021)]

# Point_X = -1627875.474
# Point_Y = 8955472.968

# line = geom.LineString(polygon)
# point = geom.Point(Point_X, Point_Y)
# polygon = geom.Polygon(line)

# print(polygon.contains(point))


# for i, route in enumerate(sector_route_list):
#     ind_route_fix_list = route.__dict__.get('fix_list')
#     first,snd = zip(*ind_route_fix_list)
#     print(i, first)
    #print(i, type(route), route.__dict__.get('fix_list')(0))
# print(sector_fix_names)
# print("sector routes = ", len(sector_route_list), type(sector_route_list), sector_route_list[0])
# print("---------")
# print(sector_route_list)
# print("----------")
# print('sector contains this many waypoints', len(sector_fix_names))



# i_fix_names = ['spirt', 'air', 'water', 'earth', 'fiyre']
# aa=1.0
# bb=2.0
# cc=3.0
# dd=4.0
# ee=5.0
# i_fix_points = [geom.Point(aa, bb + cc), # top exterior
#           geom.Point(aa, bb), # top
#           geom.Point(aa, dd), # middle
#           geom.Point(aa, ee), # bottom
#           geom.Point(aa, ee - cc)] # bottom exterior
# print(Route(i_fix_points))
# i_route = Route(i_fix_points)
# print(type(i_route))
# # print(i_fix_names)
# # print(i_fix_points)