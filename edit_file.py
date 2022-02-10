"""
This module reads and transforms the given locations.list file and returns a pandas DataFrame
"""
import pandas as pd
import re
import warnings
warnings.filterwarnings('ignore')

d_f = pd.read_csv("locations.list", error_bad_lines=False, skiprows=14, nrows=1000, encoding_errors='ignore',
                 names=["Film Name", "City", "Location", "Country"])


def location_handler(row):
    """
    This function sorts locations
    """
    try:
        city = row["Film Name"].split("\t")[-1]
        row["Country"] = row["Location"]
        row["Location"] = row["City"]
        row["City"] = city
    except (IndexError, AttributeError):
        return None

def country_cleaner(row):
    """
    This function makes the country string readable
    """
    try:
        row['Country'] = row["Country"].split("\t")[0]
    except (IndexError, AttributeError):
        return None

def date_handler(row):
    """
    This function separates data
    """
    try:
        return  re.findall(r"\([0-9]{4}\)", row["Film Name"])[0][1:][:-1]
    except (IndexError, TypeError):
        return None

def date_spliter(row):
    """
    This function separates the film name
    """
    try:
        return re.split(r"\([0-9]{4}/?\w*?\)", row["Film Name"])[0]
    except (IndexError, TypeError):
        return None

d_f.apply(location_handler, axis=1)
d_f.apply(country_cleaner, axis=1)
d_f['Year'] = d_f.apply(date_handler, axis=1)
d_f['Film Name'] = d_f.apply(date_spliter, axis=1)
d_f = d_f.dropna()