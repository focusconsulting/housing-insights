//This variable stores all the filter/layer options displayed on the map view
//TODO much of this ends up being duplicated with meta.json. We will combine the two after the ZoneFacts table is available, 
//Can't do till then because many of the fields below are only available in this not-yet-available table

// "short_names" below are the abbreviations for use in the URL encoding of the state of filters. should add unit test to
// ensure no duplicates. -JO
/*



*/
 "use strict";
 var dataChoices = [
        //TODO this hard coded array of objects is just a temporary method.
        //This should be served from the API, probably from meta.json
        //""source"" is the column name from the filter table, which should match the table in the original database table.
        //  For this approach to work, it will be cleanest if we never have duplicate column names in our sql tables unless the data has
        //  the same meaning in both places (e.g. "ward" and "ward" can appear in two tables but should have same name/format)

        {   "source":"proj_name_addre",
            "display_name": "Search",
            "display_text": "This is the searchbar",
            "component_type": "searchbar",
            "data_type": "text",
            "data_level": "project",
            "short_name": "na"
        },
        
        {   "source":"location",
            "display_name": "Specific Zone",
            "display_text": "View only projects in a specific zone of the city. The choices in this filter depend on the Zone Type selected, and the filter is cleared when the Zone Type is changed.",
            "component_type": "location",
            "data_type": "text",
            "data_level": "project",
            "short_name": "l"
        },
        {   "source":"proj_name",
            "display_name": "Project name",
            "display_text": "Filter to a specific building by searching for its name",
            "component_type": "categorical",
            "data_type": "text",
            "data_level": "project",
            "short_name": "n"
        },
        {   "source":"proj_addre",
            "display_name": "Project address",
            "display_text": "Filter to a specific building by searching for its address",
            "component_type": "categorical",
            "data_type": "text",
            "data_level": "project",
            "short_name": "a"
        },
        {   "source": "proj_units_tot",
            "display_name": "Total units in project",
            "display_text": "Total count of units in the project, including both subsidized and market rate units.",
            "component_type": "continuous",
            "data_type":"integer",
            "num_decimals_displayed": 0, //0 if integer, 1 otherwise. Could also store data type instead. 
            "data_level": "project",
            "short_name": "pu"
        },
        
        {   "source": "proj_units_assist_max",
            "display_name": "Subsidized units (max)",
            "display_text": "The number of subsidized units in the project. When a project participates in multiple subsidy programs, this number is the number of units subsidized by the program with the most units. Partially overlapping subsidies could result in more units than are reflected here.",
            "component_type": "continuous",
            "data_type":"integer",
            "num_decimals_displayed":0,
            "data_level": "project",
            "short_name": "pa"
        },
        {   "source": "proj_own_type",
            "display_name":"Ownership Type",
            "display_text":"This field is currenly only available for projects that come from the Preservation Catalog",
            "component_type": "categorical",
            "data_type":"text",
            "data_level": "project",
            "short_name": "hud"
        },

        {   "source": "portfolio",
            "display_name": "Subsidy Program",
            "display_text": "Filters to buildings that participate in at least one of the selected programs. Note some larger programs are divided into multiple parts in this list",
            "component_type":"categorical",
            "data_type": "text",
            "data_level": "project",
            "short_name": "sp"
        },
        {
            "source": "portfolio",
            "display_name": "Subsidy Program",
            "display_text": "Filters to buildings that participate in at least one of the selected programs. Note some larger programs are divided into multiple parts in this list",
            "component_type":"categorical",
            "data_type": "text",
            "data_level": "project",
            "short_name": "sp"
        },
        {   "source":"poa_start",
            "display_name":"Subsidy Start Date",
            "display_text": "Filters to buildings with at least one subsidy whose start date falls between the selected dates.",
            "component_type": "date",
            "data_type": "timestamp",
            "data_level": "project",
            "short_name": "ps"
        },
        {   "source":"poa_end",
            "display_name":"Subsidy End Date",
            "display_text": "Filters to buildings with at least one subsidy whose end date falls between the selected dates.",
            "component_type": "date",
            "data_type": "timestamp",
            "data_level": "project",
            "short_name": "pe"
        },
        {   "source":"topa_count",
            "display_name":"Number of TOPA notices",
            "display_text": "Quanitity of TOPA records identified as associated with the property. Most useful to distinguish properties that do or do not have relevant TOPA notices.",
            "component_type": "continuous",
            "data_type": "integer",
            "data_level": "project",
            "short_name": "topac"
        },
        
        {   "source":"most_recent_topa_date",
            "display_name":"Most Recent TOPA Date",
            "display_text": "Date of the most recent TOPA notice associated with the property, if there is one.",
            "component_type": "date",
            "data_type": "timestamp",
            "data_level": "project",
            "short_name": "topad"
        },
        {   "source":"most_recent_reac_score_num",
            "display_name":"Most Recent REAC Score",
            "display_text": "The numeric value of the most recent REAC inspection to occur at the property, if a REAC inspection exists. See the specific property page for full inspection history. ",
            "component_type": "continuous",
            "data_type": "integer",
            "data_level": "project",
            "short_name": "reacn"
        },
        {   "source":"most_recent_reac_score_date",
            "display_name":"Most Recent REAC Date",
            "display_text": "Date of the most recent REAC inspection to occur at the property, if a REAC inspection exists. See the specific property page for full inspection history.",
            "component_type": "date",
            "data_type": "timestamp",
            "data_level": "project",
            "short_name": "reacd"
        },
        {   "source":"sum_appraised_value_current_total",
            "display_name":"Project Taxable Value",
            "display_text": "This field is the sum of the current appraised value in the DC property tax database. When we are not able to accurately capture all the individual street addresses associated with a project, this field can sometimes undercount the full value.",
            "component_type": "continuous",
            "data_type": "integer",
            "data_level": "project",
            "short_name": "txtot"
        },
        


//////////////////////////////////////////////////
//Data choices formerly only available in 'layers', in progress of being available as filters
//TODO display_texts and names need to be updated to reflect the combined behavior of layer/filter
//TODO integer vs. decimal
//////////////////////////////////////////////////

        {
            "source": "violent_crime_count",
            "display_name": "Crime Rate: Violent 12 months",
            "display_text": "Number of violent crime incidents per 100,000 people reported in the past 12 months.",
            "data_level": "zone",
            "component_type": "continuous",
            "data_type":"decimal",
            "zones": ["ward", "neighborhood_cluster", "census_tract"],
            "default_layer": "ward",
            "style": "number",
            "short_name": "cv"
        },
        {
            "source": "non_violent_crime_rate",
            "display_name": "Crime Rate: Non-Violent 12 months",
            "display_text": "Number of non-violent crime incidents per 100,000 people reported in this zone in the past 12 months.",
            "data_level": "zone",
            "component_type": "continuous",
            "data_type":"decimal",
            "zones": ["ward", "neighborhood_cluster", "census_tract"],
            "default_layer": "ward",
            "style": "number",
            "short_name": "cn"
        },
        {
            "source": "crime_rate",
            "display_name": "Crime Rate: All 3 months",
            "display_text": "Total number of crime incidents per 100,000 people reported in the past 12 months.",
            "data_level": "zone",
            "component_type": "continuous",
            "data_type":"decimal",
            "zones": ["ward", "neighborhood_cluster", "census_tract"],
            "default_layer": "ward",
            "style": "number",
            "short_name": "ca"
        },
        {
            "source": "construction_permits",
            "display_name": "Building Permits: Construction 2016",
            "display_text": "Number of construction building permits issued in the zone during 2016. (2017 data not yet available)",
            "data_level": "zone",
            "component_type": "continuous",
            "data_type":"decimal",
            "zones": ["ward", "neighborhood_cluster", "zip"],
            "default_layer": "ward",
            "style": "number",
            "short_name": "bpc"
        },
        {
            "source": "building_permits",
            "display_name": "Building Permits: All 2016",
            "display_text": "Number of construction building permits issued in the zone during 2016. (2017 data not yet available)",
            "data_level": "zone",
            "component_type": "continuous",
            "data_type":"decimal",
            "zones": ["ward", "neighborhood_cluster", "zip"],
            "default_layer": "ward",
            "style": "number",
            "short_name": "bpa"
        },
        {
            "source": "poverty_rate",
            "display_name": "ACS: Poverty Rate",
            "display_text": "Fraction of residents below the poverty rate.",
            
            "data_level": "zone",
            "component_type": "continuous",
            "data_type":"decimal",
            "zones": ["ward", "neighborhood_cluster", "census_tract"],
            "default_layer": "census_tract",
            "style": "percent",
            "short_name": "pov"
        },
        {
            "source": "income_per_capita",
            "display_name": "ACS: Income Per Capita",
            "display_text": "Average income per resident",
            "data_level": "zone",
            "component_type": "continuous",
            "data_type":"decimal",
            "zones": ["ward", "neighborhood_cluster", "census_tract"],
            "default_layer": "census_tract",
            "style": "money",
            "short_name": "inc"
        },
        {
            "source": "labor_participation",
            "display_name": "ACS: Labor Participation",
            "display_text": "Percent of the population that is working",
            "data_level": "zone",
            "component_type": "continuous",
            "data_type":"decimal",
            "zones": ["ward", "neighborhood_cluster", "census_tract"],
            "default_layer": "census_tract",
            "style": "percent",
            "short_name": "lp"
        },
        {
            "source": "fraction_single_mothers",
            "display_name": "ACS: Fraction Single Mothers",
            "display_text": "Percent of the total population that is a single mother",
            "data_level": "zone",
            "component_type": "continuous",
            "data_type":"decimal",
            "zones": ["ward", "neighborhood_cluster", "census_tract"],
            "default_layer": "census_tract",
            "style": "percent",
            "short_name": "sm"
        },
        /*
        {
            "source": "fraction_black",
            "display_name": "ACS: Fraction Black",
            "display_text": "Proportion of residents that are black or African American",
            "data_level": "zone",
            "component_type": "continuous",
            "data_type":"decimal",
            "zones": ["ward", "neighborhood_cluster", "census_tract"],
            "default_layer": "census_tract",
            "style": "percent",
            "short_name": "fb"
        },
        */
        {
            "source": "fraction_foreign",
            "display_name": "ACS: Fraction Foreign",
            "display_text": "Percent of the population that is foreign born",
            "data_level": "zone",
            "component_type": "continuous",
            "data_type":"decimal",
            "zones": ["ward", "neighborhood_cluster", "census_tract"],
            "default_layer": "census_tract",
            "style": "percent",
            "short_name": "ff"
        },
        {
            "source": "acs_median_rent",
            "display_name": "ACS: Median Rent",
            "display_text": "Filters to buildings that are in a census tract that has a median rent between the indicated levels, per the American Community Survey. ACS rent combines both subsidized and market rate rent.",
            "data_level": "zone",
            "component_type": "continuous",
            "data_type":"decimal",
            "zones": ["ward", "neighborhood_cluster", "census_tract"],
            "default_layer": "census_tract",
            "style": "number",
            "short_name": "rnt"
        }
    ];

