from csv import DictReader
import numpy as np
import geocoder
from fuzzywuzzy import fuzz
from fuzzywuzzy import process


# building_record is a dictionary
# sample for testing
building_record = {
    "Proj_Name": "1130 7th St Apartment",
    "Proj_Addre": "1330 7th Street",
}
# project_array is numpy array converted from Project.csv
# sample for testing
project_array = np.array(
    [
        [
            "NL000001",
            "1330 7th St Apts (Immaculate Conception)",
            "1330 7th Street NW",
            38.90811789,
            -77.0221966,
        ],
        ["NL000004", "Parkfair Apts", "1611 Park Road NW", 38.93209086, -77.03705918],
        ["NL000006", "1728 W St SE", "1728 W Street SE", 38.862912, -76.97960778],
        [
            "NL000008",
            "2721 Pennsylvania Ave SE",
            "2721 Pennsylvania Avenue SE",
            38.87214315,
            -76.96816372,
        ],
    ]
)


# Convert project addresses to lat/longitude data by using google geocode.
# This function only needs to be run and saved once.
def geocode_latlng_producer(proj_add_arr):
    # assuming column 3 of project_array contains project addresses.
    proj_add_arr = project_array[:, 2]
    proj_geocode_latlng = []

    for i in range(len(proj_add_arr)):
        temp = geocoder.google(proj_add_arr[i]).latlng
        proj_geocode_latlng.append(temp)

    return proj_geocode_latlng


def location_matcher(building_record, project_array, proj_geocode_latlng):
    # converting the building_record proj_Addre and proj_name to string value
    # Assumption: dictionary value of the proj_addre is "Proj_Addre"
    new_bldg_addre = building_record["Proj_Addre"]
    # Assumption: dictionary value of the proj_name is "Proj_Name"
    new_bldg_name = building_record["Proj_Name"]

    # Covert the numpy array into individual array.
    # Expected array order: [nlihc_id, name, address, lat, lon]
    id_arr = project_array[:, 0]
    proj_name_arr = project_array[:, 1]
    proj_add_arr = project_array[:, 2]
    lat_arr = project_array[:, 3]
    lng_arr = project_array[:, 4]

    result_string_checker = None
    result_geocode = None
    result_fuzzyString = None

    # string name checker for project name
    for i in range(len(proj_name_arr)):
        if proj_name_arr[i] == new_bldg_name:
            result_string_checker = []
            result_string_checker.append(id_arr[i])
            break
    # string name checker for project address
    # Not checking for duplicate ID that might have been inputed during checking for project name
    # assuming that its highly unlikely that exact string matches will work.
    for i in range(len(proj_add_arr)):
        if proj_add_arr[i] == new_bldg_addre:
            result_string_checker = []
            result_string_checker.append(id_arr[i])
            break

    # Geocoder
    # Assumption: Assuming that new address given does not have "Washington DC" added
    # string "Washington DC" is added.
    # Seems like google geocode can take "Washington DC Washington DC" and give the same Lat/lng
    # as that of "Washington DC" added once.
    bldg_rec_geocode = geocoder.google(new_bldg_addre + " Washington DC")
    # print(proj_geocode_latlng)

    for i in range(len(proj_geocode_latlng)):
        proj_geocode_latlng[i]
        if bldg_rec_geocode.latlng == proj_geocode_latlng[i]:
            result_geocode = []
            result_geocode.append(id_arr[i])
            break

    # later use for comparing lat/lng from the Project.csv
    # for i in range(len(proj_addre_array)):
    #     if (LatLng_new[0] == lat_array[i] and LatLng_new[1] == lng_array[i]):
    #         result_geocode.append(id_array[i])

    # Fuzzy String
    # Using Fuzzy String to check the APT Names.
    # score of 90 points is arbitrary. Fuzzy string is the least accurate
    # so maybe the scoring should be more lenient?
    result_fuzzyString = []
    for i in range(len(proj_name_arr)):
        score = fuzz.partial_ratio(proj_name_arr[i], new_bldg_name)
        # print(score)
        if score >= 90:
            result_fuzzyString.append(id_arr[i])
    if not result_fuzzyString:
        result_fuzzyString = None

    final_result = (result_string_checker, result_geocode, result_fuzzyString)
    return final_result


proj_geocode_latlng = geocode_latlng_producer(project_array)

print(location_matcher(building_record, project_array, proj_geocode_latlng))
