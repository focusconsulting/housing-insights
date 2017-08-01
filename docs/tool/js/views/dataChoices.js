//This variable stores all the filter/layer options displayed on the map view
//TODO much of this ends up being duplicated with meta.json. We will combine the two after the ZoneFacts table is available, 
//Can't do till then because many of the fields below are only available in this not-yet-available table

 "use strict";
 var dataChoices = [
        //TODO this hard coded array of objects is just a temporary method.
        //This should be served from the API, probably from meta.json
        //""source"" is the column name from the filter table, which should match the table in the original database table.
        //  For this approach to work, it will be cleanest if we never have duplicate column names in our sql tables unless the data has
        //  the same meaning in both places (e.g. "ward" and "ward" can appear in two tables but should have same name/format)
        {   "source":"location",
            "display_name": "Location",
            "display_text": "Dropdown menu updates when selecting a new zone type. <br><br>Logic Incomplete: still need to a) clear the existing filter when new zone is selected and b) writecallback for the locationFilterControl",
            "component_type": "location",
            "data_type": "text",
            "data_level": "project"
        },

        {   "source": "proj_units_tot",
            "display_name": "Total units in project",
            "display_text": "Total count of units in the project, including both subsidized and market rate units.",
            "component_type": "continuous",
            "data_type":"integer",
            "num_decimals_displayed": 0, //0 if integer, 1 otherwise. Could also store data type instead. 
            "data_level": "project"
        },
        
        {   "source": "proj_units_assist_max",
            "display_name": "Subsidized units (max)",
            "display_text": "The number of subsidized units in the project. When a project participates in multiple subsidy programs, this number is the number of units subsidized by the program with the most units. Partially overlapping subsidies could result in more units than are reflected here.",
            "component_type": "continuous",
            "data_type":"integer",
            "num_decimals_displayed":0,
            "data_level": "project"
        },
        {   "source": "hud_own_type",
            "display_name":"Ownership Type (per HUD)",
            "display_text":"This field is only available for buildings participating in HUD programs; others are listed as 'Unknown'",
            "component_type": "categorical",
            "data_type":"text",
            "data_level": "project"
        },

        {   "source": "portfolio",
            "display_name": "Subsidy Program",
            "display_text": "Filters to buildings that participate in at least one of the selected programs. Note some larger programs are divided into multiple parts in this list",
            "component_type":"categorical",
            "data_type": "text",
            "data_level": "project"
        },
        {   "source":"poa_start",
            "display_name":"Subsidy Start Date",
            "display_text": "Filters to buildings with at least one subsidy whose start date falls between the selected dates.",
            "component_type": "date",
            "data_type": "timestamp",
            "data_level": "project"
        },
        {   "source":"poa_end",
            "display_name":"Subsidy End Date",
            "display_text": "Filters to buildings with at least one subsidy whose end date falls between the selected dates.",
            "component_type": "date",
            "data_type": "timestamp",
            "data_level": "project"
        },


//////////////////////////////////////////////////
//Data choices formerly only available in 'layers', in progress of being available as filters
//TODO display_texts and names need to be updated to reflect the combined behavior of layer/filter
//TODO integer vs. decimal
//////////////////////////////////////////////////

        {
            "source": "violent_crime_count",
            "display_name": "Crime Rate: Violent 12 months",
            "display_text": "**Filter not working**<br>Number of violent crime incidents per 100,000 people reported in the past 12 months.",
            "data_level": "zone",
            "component_type": "continuous",
            "data_type":"decimal",
            "zones": ["ward", "neighborhood_cluster", "census_tract"],
            "default_layer": "ward",
            "style": "number"
        },
        {
            "source": "non_violent_crime_rate",
            "display_name": "Crime Rate: Non-Violent 12 months",
            "display_text": "**Filter not working**<br>Number of non-violent crime incidents per 100,000 people reported in this zone in the past 12 months.",
            "data_level": "zone",
            "component_type": "continuous",
            "data_type":"decimal",
            "zones": ["ward", "neighborhood_cluster", "census_tract"],
            "default_layer": "ward",
            "style": "number"
        },
        {
            "source": "crime_rate",
            "display_name": "Crime Rate: All 3 months",
            "display_text": "**Filter not working**<br>Total number of crime incidents per 100,000 people reported in the past 12 months.",
            "data_level": "zone",
            "component_type": "continuous",
            "data_type":"decimal",
            "zones": ["ward", "neighborhood_cluster", "census_tract"],
            "default_layer": "ward",
            "style": "number"
        },
        {
            "source": "construction_permits",
            "display_name": "Building Permits: Construction 2016",
            "display_text": "**Filter not working**<br>Number of construction building permits issued in the zone during 2016. (2017 data not yet available)",
            "data_level": "zone",
            "component_type": "continuous",
            "data_type":"decimal",
            "zones": ["ward", "neighborhood_cluster", "zip"],
            "default_layer": "ward",
            "style": "number"
        },
        {
            "source": "building_permits",
            "display_name": "Building Permits: All 2016",
            "display_text": "**Filter not working**<br>Number of construction building permits issued in the zone during 2016. (2017 data not yet available)",
            "data_level": "zone",
            "component_type": "continuous",
            "data_type":"decimal",
            "zones": ["ward", "neighborhood_cluster", "zip"],
            "default_layer": "ward",
            "style": "number"
        },
        {
            "source": "poverty_rate",
            "display_name": "ACS: Poverty Rate",
            "display_text": "**Filter not working**<br>Fraction of residents below the poverty rate.",
            
            "data_level": "zone",
            "component_type": "continuous",
            "data_type":"decimal",
            "zones": ["ward", "neighborhood_cluster", "census_tract"],
            "default_layer": "census_tract",
            "style": "percent"
        },
        {
            "source": "income_per_capita",
            "display_name": "ACS: Income Per Capita",
            "display_text": "**Filter not working**<br>Average income per resident",
            "data_level": "zone",
            "component_type": "continuous",
            "data_type":"decimal",
            "zones": ["ward", "neighborhood_cluster", "census_tract"],
            "default_layer": "census_tract",
            "style": "money"
        },
        {
            "source": "labor_participation",
            "display_name": "ACS: Labor Participation",
            "display_text": "**Filter not working**<br>Percent of the population that is working",
            "data_level": "zone",
            "component_type": "continuous",
            "data_type":"decimal",
            "zones": ["ward", "neighborhood_cluster", "census_tract"],
            "default_layer": "census_tract",
            "style": "percent"
        },
        {
            "source": "fraction_single_mothers",
            "display_name": "ACS: Fraction Single Mothers",
            "display_text": "**Filter not working**<br>Percent of the total population that is a single mother",
            "data_level": "zone",
            "component_type": "continuous",
            "data_type":"decimal",
            "zones": ["ward", "neighborhood_cluster", "census_tract"],
            "default_layer": "census_tract",
            "style": "percent"
        },
        {
            "source": "fraction_black",
            "display_name": "ACS: Fraction Black",
            "display_text": "**Filter not working**<br>Proportion of residents that are black or African American",
            "data_level": "zone",
            "component_type": "continuous",
            "data_type":"decimal",
            "zones": ["ward", "neighborhood_cluster", "census_tract"],
            "default_layer": "census_tract",
            "style": "percent"
        },
        {
            "source": "fraction_foreign",
            "display_name": "ACS: Fraction Foreign",
            "display_text": "**Filter not working**<br>Percent of the population that is foreign born",
            "data_level": "zone",
            "component_type": "continuous",
            "data_type":"decimal",
            "zones": ["ward", "neighborhood_cluster", "census_tract"],
            "default_layer": "census_tract",
            "style": "percent"
        },
        {
            "source": "acs_median_rent",
            "display_name": "ACS: Median Rent",
            "display_text": "**Filter not working**<br>Filters to buildings that are in a census tract that has a median rent between the indicated levels, per the American Community Survey. ACS rent combines both subsidized and market rate rent.",
            "data_level": "zone",
            "component_type": "continuous",
            "data_type":"decimal",
            "zones": ["ward", "neighborhood_cluster", "census_tract"],
            "default_layer": "census_tract",
            "style": "number"
        }
       
    ];