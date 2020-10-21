# Chenyu Wang

# Importing BeautifulSoup, urllib, and os
import math
import os
import numpy as np
import csv

from urllib.request import urlopen

from bs4 import BeautifulSoup


def get_document(web_url, filename):
    if not os.path.exists("data"):
        os.mkdir("data")
        os.path.join(os.getcwd(), "data")
    os.chdir("data")
    try:
        with urlopen(web_url) as data_source:
            web_soup = BeautifulSoup(data_source, "html5lib")
            with open(filename, "w", errors="replace") as data_file:
                for line in web_soup.prettify():
                    data_file.write(line)
        return filename
    except Exception:
        print(f"Error. {web_url} could not be opened or file could not be created.")
        quit(1)


def extract_coordinates(city_url):
    try:
        with urlopen(city_url) as city_data:
            # Getting the coordinates for each city
            coord_soup = BeautifulSoup(city_data, "html5lib")
            geography = coord_soup.find("table", {"class": "infobox geography vcard"})
            coordinates = geography.find("a", {"class": "external text"})["href"]
            with urlopen("https:" + coordinates) as coordinate_website:
                decimal_coord_soup = BeautifulSoup(coordinate_website, "html5lib")
                geo = decimal_coord_soup.find("table")
                latitude = geo.find("span", {"class": "latitude"})
                longitude = geo.find("span", {"class": "longitude"})

            # converts the latitude and longitude to radians for the great circle distance formula
            latitude = float(latitude.text)
            longitude = float(longitude.text)
            latitude = math.radians(latitude)
            longitude = math.radians(longitude)
            coords = [latitude, longitude]
        return coords
    except Exception:
        print(f"{city_url} could not be opened. The site may be down.")
        quit(2)


def get_min_distance(latitude, longitude):
    # List to store the distances and get the minimum value
    distances = []

    # Hard code for the coordinates for the border
    san_ysidiro_latitude, san_ysidiro_longitude = math.radians(32.5549), math.radians(-117.044306)
    yuma_latitude, yuma_longitude = math.radians(32.692222), math.radians(-114.615278)
    tucson_latitude, tucson_longitude = math.radians(32.221667), math.radians(-110.926389)
    el_paso_latitude, el_paso_longitude = math.radians(31.759167), math.radians(-106.488611)
    laredo_latitude, laredo_longitude = math.radians(27.524444), math.radians(-99.490556)
    del_rio_latitude, del_rio_longitude = math.radians(29.364), math.radians(-100.9)
    brownsville_latitude, brownsville_longitude = math.radians(25.930278), math.radians(-97.484444)

    # Great Circle Formulas
    distances.append(6371 * (
        math.acos(math.sin(latitude) * math.sin(san_ysidiro_latitude) + math.cos(latitude) *
                  math.cos(san_ysidiro_latitude) * math.cos(longitude - san_ysidiro_longitude))))
    distances.append(6371 * (
        math.acos(math.sin(latitude) * math.sin(yuma_latitude) + math.cos(latitude) *
                  math.cos(yuma_latitude) * math.cos(longitude - yuma_longitude))))
    distances.append(6371 * (
        math.acos(math.sin(latitude) * math.sin(tucson_latitude) + math.cos(latitude) *
                  math.cos(tucson_latitude) * math.cos(longitude - tucson_longitude))))
    distances.append(6371 * (
        math.acos(math.sin(latitude) * math.sin(el_paso_latitude) + math.cos(latitude) *
                  math.cos(el_paso_latitude) * math.cos(longitude - el_paso_longitude))))
    # This is used to avoid math domain error
    if latitude != laredo_latitude:
        distances.append(6371 * (
            math.acos(math.sin(latitude) * math.sin(laredo_latitude) + math.cos(latitude) *
                      math.cos(laredo_latitude) * math.cos(longitude - laredo_longitude))))
    # appends 0 because laredo is at the border
    else:
        distances.append(0)
    distances.append(6371 * (
        math.acos(math.sin(latitude) * math.sin(del_rio_latitude) + math.cos(latitude) *
                  math.cos(del_rio_latitude) * math.cos(longitude - del_rio_longitude))))
    distances.append(6371 * (
        math.acos(math.sin(latitude) * math.sin(brownsville_latitude) + math.cos(latitude) *
                  math.cos(brownsville_latitude) * math.cos(longitude - brownsville_longitude))))
    return min(distances)


# If we need to go back to the original path
orig_dir = os.getcwd()
url = "https://en.wikipedia.org/wiki/List_of_United_States_cities_by_crime_rate"

# Create empty lists for the cities and crime rates in the table
cities = []
crime_rate = []
city_urls = []
city_coordinates = []
min_distance = []

doc_filename = get_document(url, "table_data.html")
soup = BeautifulSoup(open(doc_filename), "html5lib")

# Creates a list of all the rows in the table on wikipedia
table = soup.find("table").find_all("tr")

# Remove the first index until the row we want is reached and is at the beginning of the list
table.pop(0)
table.pop(0)
table.pop(0)

# For loop that creates a list of all cities and list of all crime rates. The indexes correspond to each other.
# Ex. cities[1] has a crime rate of crime_rate[1]
for rows in table:
    row_data = rows.find_all("td")
    cities.append(row_data[1].a.text)
    crime_rate.append(row_data[3].text)
    city_urls.append(row_data[1].a["href"])

# Cleans up the lists
cities = [city.strip() for city in cities if city.strip()]
crime_rate = [rate.strip() for rate in crime_rate if rate.strip()]
#These cities have no crime rate therefore they need to be removed
cities.remove("Durham")
cities.remove("Charlotte-Mecklenburg")
cities.remove("Greensboro")
cities.remove("Toledo")
city_urls.remove("/wiki/Durham,_North_Carolina")
city_urls.remove("/wiki/Charlotte")
city_urls.remove("/wiki/Greensboro,_North_Carolina")
city_urls.remove("/wiki/Toledo,_Ohio")

# Extract coordinates for each city and return a list of latitude and longitude
print("Please wait while the coordinates are getting extracted.")
for urls in city_urls:
    city_coordinates.append(extract_coordinates("https://en.wikipedia.org" + urls))
print("Done extracting.")
# Calculates the min distance from the border
for lists in city_coordinates:
    min_distance.append(get_min_distance(lists[0], lists[1]))

#write into csv file
outlist=[cities,crime_rate,min_distance]
new_list=map(list,zip(*outlist))
header=['City','CrimesRate','SmallestDistance']
with open('crimeandborder.csv','w') as csvfileOut:
    writer=csv.writer(csvfileOut)
    writer.writerow(header)
    writer.writerows(new_list)
print("the data has already written in the crimeandborder.csv")

#calculate correlation
float_crime_rate=list(map(float,crime_rate))
mat1=np.array(float_crime_rate)
mat2=np.array(min_distance)
print("correlation bewteen the crime_rate and the min_distancet is:\n",np.corrcoef(mat1,mat2))

print('All steps are finished')
