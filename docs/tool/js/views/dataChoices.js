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

        /*Awaiting update to API to make this field available
        {   "source":"status",
            "display_name": "Active or Inactive",
            "display_text": "Status classification of the property",
            "component_type": "categorical",
            "data_type": "text",
            "data_level": "project",
            "short_name": "stat",
            "sourcetable": "project"
        },
        */
        {   "source":"proj_name_addre",
            "display_name": "Search",
            "display_text": "This is the searchbar",
            "component_type": "searchbar",
            "data_type": "text",
            "data_level": "project",
            "short_name": "na",
            "sourcetable": ""
        },
        
        {   "source":"location",
            "display_name": "Specific Zone",
            "display_text": "View only projects in a specific zone of the city. The choices in this filter depend on the Zone Type selected, and the filter is cleared when the Zone Type is changed.",
            "component_type": "location",
            "data_type": "text",
            "data_level": "project",
            "short_name": "l",
            "sourcetable": ""
        },
        {   "source":"proj_name",
            "display_name": "Project name",
            "display_text": "Filter to a specific building by searching for its name",
            "component_type": "categorical",
            "data_type": "text",
            "data_level": "project",
            "short_name": "n",
            "sourcetable":"project"
        },
        {   "source":"proj_addre",
            "display_name": "Project address",
            "display_text": "Filter to a specific building by searching for its address",
            "component_type": "categorical",
            "data_type": "text",
            "data_level": "project",
            "short_name": "a",
            "sourcetable": "project"
        },
        {   "source": "proj_units_tot",
            "display_name": "Total units in project",
            "display_text": "Total count of units in the project, including both subsidized and market rate units.",
            "component_type": "continuous",
            "data_type":"integer",
            "num_decimals_displayed": 0, //0 if integer, 1 otherwise. Could also store data type instead. 
            "data_level": "project",
            "short_name": "pu",
            "sourcetable": "project"
        },
        
        {   "source": "proj_units_assist_max",
            "display_name": "Subsidized units (max)",
            "display_text": "The number of subsidized units in the project. When a project participates in multiple subsidy programs, this number is the number of units subsidized by the program with the most units. Partially overlapping subsidies could result in more units than are reflected here.",
            "component_type": "continuous",
            "data_type":"integer",
            "num_decimals_displayed":0,
            "data_level": "project",
            "short_name": "pa",
            "sourcetable": "project"
        },
        {   "source": "proj_owner_type",
            "display_name":"Ownership Type",
            "display_text":"This field is currenly only available for projects that come from the Preservation Catalog",
            "component_type": "categorical",
            "data_type":"text",
            "data_level": "project",
            "short_name": "hud",
            "sourcetable": "project"
        },

        {   "source": "portfolio",
            "display_name": "Subsidy Program",
            "display_text": "Filters to buildings that participate in at least one of the selected programs. Note some larger programs are divided into multiple parts in this list",
            "component_type":"categorical",
            "data_type": "text",
            "data_level": "project",
            "short_name": "sp",
            "sourcetable": "subsidy"
        },
        {   "source":"poa_start",
            "display_name":"Subsidy Start Date",
            "display_text": "Filters to buildings with at least one subsidy whose start date falls between the selected dates.",
            "component_type": "date",
            "data_type": "timestamp",
            "data_level": "project",
            "short_name": "ps",
            "sourcetable": "subsidy"
        },
        {   "source":"poa_end",
            "display_name":"Subsidy End Date",
            "display_text": "Filters to buildings with at least one subsidy whose end date falls between the selected dates.",
            "component_type": "date",
            "data_type": "timestamp",
            "data_level": "project",
            "short_name": "pe",
            "sourcetable": "subsidy"
        },
        {   "source":"topa_count",
            "display_name":"Number of TOPA notices",
            "display_text": "Quanitity of TOPA records identified as associated with the property. Most useful to distinguish properties that do or do not have relevant TOPA notices.",
            "component_type": "continuous",
            "data_type": "integer",
            "data_level": "project",
            "short_name": "topac",
            "sourcetable": "project"
        },
        {
            "source": "has_topa_outcome",
            "display_name": "Has TOPA outcome",
            "display_text": "Filter down to projects that have a recorded TOPA outcome",
            "component_type": "categorical",
            "data_type": "boolean",
            "data_level": "project",
            "short_name": "hto",
            "sourcetable": "project"
        },
        {   "source":"most_recent_topa_date",
            "display_name":"Most Recent TOPA Date",
            "display_text": "Date of the most recent TOPA notice associated with the property, if there is one.",
            "component_type": "date",
            "data_type": "timestamp",
            "data_level": "project",
            "short_name": "topad",
            "sourcetable": "project"
        },
        {   "source":"most_recent_reac_score_num",
            "display_name":"Most Recent REAC Score",
            "display_text": "The numeric value of the most recent REAC inspection to occur at the property, if a REAC inspection exists. See the specific property page for full inspection history. ",
            "component_type": "continuous",
            "data_type": "integer",
            "data_level": "project",
            "short_name": "reacn",
            "sourcetable": "project"
        },
        {   "source":"most_recent_reac_score_date",
            "display_name":"Most Recent REAC Date",
            "display_text": "Date of the most recent REAC inspection to occur at the property, if a REAC inspection exists. See the specific property page for full inspection history.",
            "component_type": "date",
            "data_type": "timestamp",
            "data_level": "project",
            "short_name": "reacd",
            "sourcetable": "project"
        },
        {   "source":"sum_appraised_value_current_total",
            "display_name":"Project Taxable Value",
            "display_text": "This field is the sum of the current appraised value in the DC property tax database. When we are not able to accurately capture all the individual street addresses associated with a project, this field can sometimes undercount the full value.",
            "component_type": "continuous",
            "data_type": "integer",
            "data_level": "project",
            "short_name": "txtot",
            "sourcetable": "project"
        },
        /*Awaiting update to API to make this field available
        {   "source":"nearest_metro_station",
            "display_name":"Distance to closest metro",
            "display_text": "Walking distance in miles to the nearest metro station",
            "component_type": "continuous",
            "data_type": "decimal",
            "data_level": "project",
            "short_name": "nms",
            "sourcetable": "project"
        },
        {   "source":"bus_routes_nearby",
            "display_name":"Number of accessible bus routes",
            "display_text": "Number of bus routes that have a bus stop within 0.5 miles walking distance",
            "component_type": "continuous",
            "data_type": "integer",
            "data_level": "project",
            "short_name": "brn",
            "sourcetable": "project"
        },
        */


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
            "short_name": "cv",
            "sourcetable": "zone_facts"
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
            "short_name": "cn",
            "sourcetable": "zone_facts"
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
            "short_name": "ca",
            "sourcetable": "zone_facts"
        },
        {
            "source": "construction_permits_rate",
            "display_name": "Building Permits: Construction Rate",
            "display_text": "Number of construction building permits per 1,000 residential properties issued in the zone over the past 1 year.",
            "data_level": "zone",
            "component_type": "continuous",
            "data_type":"decimal",
            "zones": ["ward", "neighborhood_cluster", "zip"],
            "default_layer": "ward",
            "style": "number",
            "short_name": "bpc",
            "sourcetable": "zone_facts"
        },
        {
            "source": "building_permits_rate",
            "display_name": "Building Permits: All Rate",
            "display_text": "Number of all building permits per 1,000 residential properties issued in the zone over the past 1 year.",
            "data_level": "zone",
            "component_type": "continuous",
            "data_type":"decimal",
            "zones": ["ward", "neighborhood_cluster", "zip"],
            "default_layer": "ward",
            "style": "number",
            "short_name": "bpa",
            "sourcetable": "zone_facts"
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
            "short_name": "pov",
            "sourcetable": "zone_facts"
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
            "short_name": "inc",
            "sourcetable": "zone_facts"
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
            "short_name": "lp",
            "sourcetable": "zone_facts"
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
            "short_name": "sm",
            "sourcetable": "zone_facts"
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
            "short_name": "ff",
            "sourcetable": "zone_facts"
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
            "short_name": "rnt",
            "sourcetable": "zone_facts"
        }
    ];

