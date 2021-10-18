from shapely.geometry import Polygon

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

def extract_polygon(dms_str):
    """
    Return sector Polygon from sectors data
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
