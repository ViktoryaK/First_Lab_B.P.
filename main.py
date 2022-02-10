"""
This is a main module of the project.
"""
from functools import lru_cache
import folium
import argparse
from geopy import ArcGIS
import pandas as pd
from edit_file import d_f
from geopy.geocoders import Nominatim
import haversine

def reading_input():
    """
    This function is made for reading the input and returning needed information.
    The input looks like this:
    2000 49.83826 24.02324 path_to_dataset
    """
    parser = argparse.ArgumentParser(description='Works with the input from the user')
    parser.add_argument('y', help='Year', type=int)
    parser.add_argument('la', help='Latitude', type=float)
    parser.add_argument('lo', help='Longitude', type=float)
    parser.add_argument('way', help='Path to dataset')
    args = parser.parse_args()
    return [args.y, args.la, args.lo, args.way]

@lru_cache(maxsize=None)
def geocode(address):
    """
    This function turns the address into the location and returns its latitude and longitude.
    Can be used only with main.
    >>> geocode('Coventry,  West Midlands,  England')
    (52.40772367500006, -1.5068478819999314)
    """
    i = 0
    try:
        location = geocoders[i].geocode(address)
        if location != None:
            return location.latitude, location.longitude
        i += 1
        location = geocoders[i].geocode(address)
        if location != None:
            return location.latitude, location.longitude
    except:
        return None


def year_sorting(year, df):
    """
    This function returns DataFrame with films only filmed in the year user did input.
    """
    city = []
    location = []
    country = []
    film_name = []
    for i, row in df.iterrows():
        if int(row['Year']) == year:
            city.append(row['City'])
            location.append(row['Location'])
            country.append(row['Country'])
            film_name.append(row['Film Name'])
    data = {'City': city, 'Location': location, 'Country': country, 'Film Name': film_name}
    new_df = pd.DataFrame(data)
    return new_df

def distance(lo, user_la, user_lo):
    """
    This is a function that calculates the distance between two spots on a map
    by latitude and longitude.
    >>> distance((52.40772367500006, -1.5068478819999314), 49.83826, 24.02324)
    1794.844903444289
    """
    loc_1 = tuple([user_la, user_lo])
    distan = haversine.haversine(lo, loc_1)
    return distan

def step_by_step(first_layer: bool):
    """
    This is a function that puts together all the previous ones and returns sorted final DataFrame
    """
    if first_layer:
        df = year_sorting(reading_input()[0], d_f)
    else:
        df = d_f
    coord = []
    for i, row in df.iterrows():
        address = ", ".join([row['City'], row['Location'], row['Country']])
        coord.append(geocode(address))
    df['Coordinates'] = coord
    distance_list = []
    for i, row in df.iterrows():
        try:
            distant = distance(row['Coordinates'], reading_input()[1], reading_input()[2])
            print(row['Coordinates'])
            print(reading_input()[1])
            print(reading_input()[2])
            print(distant)
            distance_list.append(distant)
        except TypeError:
            distance_list.append(None)
    df['Distance'] = distance_list
    sorted_df = df.sort_values(by='Distance')
    return sorted_df

def create_map(df1, df2):
    """
    This function doesn't return anything, it just creates a map
    """
    map = folium.Map(location=[reading_input()[1], reading_input()[2]], zoom_start=5)
    year = reading_input()[0]
    fg = folium.FeatureGroup(name=f"The nearest films of {year} year")
    fg2 = folium.FeatureGroup(name="The nearest films of all years")
    df1 = df1.drop_duplicates(subset="Coordinates")
    df2 = df2.drop_duplicates(subset='Coordinates')
    coordinate = list(df1['Coordinates'])[:10]
    first_layer = list(df1['Film Name'])[:10]
    coordinate2 = list(df2['Coordinates'])[:15]
    first_layer2 = list(df2['Film Name'])[:15]
    for i in range(len(first_layer)):
        fg.add_child(folium.Marker(location=coordinate[i], popup=first_layer[i], icon=folium.Icon(color='green')))
        map.add_child(fg)
    for i in range(len(first_layer2)):
        fg2.add_child(folium.Marker(location=coordinate2[i], popup=first_layer2[i], icon=folium.Icon(color='red')))
        map.add_child(fg2)
    map.add_child(folium.LayerControl())
    map.save('Map.html')


if __name__ == "__main__":
    arcgis = ArcGIS(timeout=10)
    nominatim = Nominatim(timeout=10, user_agent="justme")
    geocoders = [arcgis, nominatim]
    first_layer = step_by_step(True)
    second_layer = step_by_step(False)
    create_map(first_layer, second_layer)