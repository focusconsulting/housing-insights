from csv import DictReader
import numpy as np
import geocoder
from fuzzywuzzy import fuzz
from fuzzywuzzy import process


#building_record is a dictionary
#sample for testing
# building_record = {"Proj_Name": "1330 7th St Apts", "Proj_Addre": "1330 7th Street NW"}
#project_array is numpy array converted from Project.csv
#sample for testing
# project_array = np.array([["NL000001", "1330 7th St Apts (Immaculate Conception)", "1330 7th Street NW", 38.90811789, -77.0221966],
                        # ["NL000004", "Parkfair Apts", "1611 Park Road NW", 38.93209086, -77.03705918],
                        # ["NL000006", "1728 W St SE", "1728 W Street SE", 38.862912, -76.97960778],
                        # ["NL000008", "2721 Pennsylvania Ave SE", "2721 Pennsylvania Avenue SE", 38.87214315, -76.96816372]])



def location_matcher(building_record, project_array):
    #converting the building_record proj_Addre and proj_name to string value
    #Assumption: dictionary value of the proj_addre is "Proj_Addre"
    new_bldg_addre = building_record['Proj_Addre']
    #Assumption: dictionary value of the proj_name is "Proj_Name"
    new_bldg_name = building_record['Proj_Name']

    #Covert the numpy array into "ID array", "Proj_name array", "Proj_Addre array"
    #Assumption: Nlihc_id is located in column 0 of the project_array
    id_array = project_array[:, 0]
    #Assumption: proj_name is located in column 1 of the project_array
    proj_name_array = project_array[:, 1]
    #Assumption: proj_addre is located in column 2 of the project_array
    proj_addre_array = project_array[:, 2]
    #Assumption: latitude is located in column 3
    lat_array = project_array[:, 3]
    #Assumption: longitude is locatedin column 4
    lng_array = project_array[:, 4]

    result_string_checker = []
    result_geocode = []
    result_fuzzyString = []

    #string name checker for project name
    for i in range(len(proj_name_array)):
        if(proj_name_array[i] == new_bldg_name):
            result_string_checker.append(id_array[i])
    #string name checker for project address
    #Not checking for duplicate ID that might have been inputed during checking for project name
    #assuming that its highly unlikely that exact string matches will work.
    for i in range(len(proj_addre_array)):
        if(proj_addre_array[i] == new_bldg_addre):
            result_string_checker.append(id_array[i])


    #Geocoder
    #Assumption: Assuming that new address given does not have "Washington DC" added
    #string "Washington DC" is added.
    #Seems like google geocode can take "Washington DC Washington DC" and give the same Lat/lng
    #as that of "Washington DC" added once.
    newGeocode = geocoder.google(new_bldg_addre + " Washington DC")

    for i in range(len(proj_addre_array)):
        temp = geocoder.google(proj_addre_array[i]).latlng
        if(newGeocode.latlng == temp):
            result_geocode.append(id_array[i])

    #later use for comparing lat/lng from the Project.csv
    # for i in range(len(proj_addre_array)):
    #     if (LatLng_new[0] == lat_array[i] and LatLng_new[1] == lng_array[i]):
    #         result_geocode.append(id_array[i])


    #Fuzzy String
    #Using Fuzzy String to check the APT Names.
    #score of 90 points is arbitrary. Fuzzy string is the least accurate
    #so maybe the scoring should be more lenient?
    for i in range(len(proj_name_array)):
        print proj_name_array[i]
        print new_bldg_name
        score = fuzz.partial_ratio(proj_name_array[i], new_bldg_name)
        print score
        if(score >= 90):
            result_fuzzyString.append(id_array[i])


    # Will need to change this
    final_result = None

    if(result_string_checker and result_geocode and result_fuzzyString):
        final_result = (result_string_checker, result_geocode, result_fuzzyString)
    elif(result_geocode and result_string_checker):
        final_result = (result_string_checker, result_geocode)
    elif(result_geocode and result_fuzzyString):
        final_result = (result_geocode, result_fuzzyString)
    elif(result_string_checker and result_fuzzyString):
        final_result = (result_string_checker, result_fuzzyString)
    elif(result_geocode):
        final_result = (result_geocode, [])
    elif(result_string_checker):
        final_result = (result_string_checker, [])
    elif(result_fuzzyString):
        final_result = (result_fuzzyString, [])

    return final_result

print location_matcher(building_record, project_array)
