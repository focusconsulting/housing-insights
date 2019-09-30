# Back End of Housing Insights
This portion of the project holds the "back end" of the website implemented in python. It contains the following: 

* `app.py`: The main application file and ultimate server-side logic for the tool. 
* `mailer.py`: Contains code to send e-mails related to the tool automatically.
* `test.py`: Contains tests for the back end portion of the project. Run `python test.py` to run all tests.
* `Dockerfile`: Sets up the development environment.
* `environment.yml`: A conda environment template run by the Dockerfile
* `secrets.yml`: Holds API keys and other secret information.
* `secrets.sample.yml`: A template for `secrets.yml`.
* `ETL`: Extract, Transform, Load. Code is responsible for loading in data sources into the tool.
    * `__init__.py`: Allows specific imports for `app.py`.
    * `acs.py`: Handles American Community Suvey data. 
    * `crime.py`: Handles crime data from Open Data DC.
    * `permit.py`: Handles building permit data.
    * `project.py`: Collects projects, REAC, and TOPA information for the database.
    * `subsidy.py`: Adds subsidy data to the subsidy table in the database.
    * `utils.py`: Miscellanious functions that are needed for the ETL process.
    * `wmata.py`: Handles bus stop and rail station data.
    * `make_geographic_weights.py`: Creates weights for demographics calculations. This should only be run if the census boundaries have changed.
    * `make_zone_facts.py`: Creates the zone facts table from ACS, crime, and permit data.
    * `filter_view_query.py`: The SQL query for the filter API route.

## Data Sources

#### Downloaded From the S3
* Preservation Catalog Projects
* Preservation Catalog Subsidies
* Preservation Catalog REAC Information
* TOPA Information

#### Collected From External Source
* [American Community Survey Data]()
* [Open Data DC Crime]()
* [Open Data DC Building Permits]()
* [Open Data DC DC Affordable Housing Projects]()
* [Open Data DC Tax Information]()
* [The DC Master Address Repository]()
* [Open Data DC Census Tract Shapefiles]()
* [Open Data DC Neighborhood Cluster Shapefiles]()
* [WMATA API]()


#### ACS Detail Tables Used
| Detail Table  | Description                       |
|---------------|-----------------------------------|
| `B01003 001E` | Total population                  |
| `B02001 003E` | African American population       |
| `B17020 002E` | Population in poverty             |
| `B23025 002E` | Labor force population            |
| `B16008 019E` | Foreign born population           |
| `B09002 015E` | Single mom households             |
| `B19025 001E` | Aggregate household income        |
| `B25057 001E` | Lower rent quartile in dollars    |
| `B25058 001E` | Median rent quartile in dollars   |
| `B25059 001E` | Upper rent quartile in dollars    |

## Database Connection


## Environments / Dependencies


### Running the code
All code is ultimately called and used from `app.py`, therefore, running code should be done at this top level (`back_end`) inside the Docker container. 
To do adhock testing of code in ETL, you may need to adjust the imports, such as `import utils` rather than `from . import utils`.

### Elastic Beanstalk Deployment Information
- Install the Elastic Beanstalk Command Line Interface: `$ pip install awsebcli`
- Configure a profile that uses the AWS credentials for our Code for DC API account: `aws configure --profile codefordc`
- Enter the public and secret keys provided to you by an admin; default location and output format can be None (just press enter)

#### Normal use:
1. Navigate to the housing-insights/python folder in your local repo
2. run `eb deploy housinginsights-codefordc --profile codefordc` (here housinginsights-codefordc is the elastic beanstalk environment name, and codefordc is the name of the credentials saved in your config file above)
3. Wait a few minutes while the server restarts w/ new code
4. Test that the api urls work properly, including whichever changes you've made. Visit http://housinginsights.us-east-1.elasticbeanstalk.com/

#### Deploy to staging enviroment to test
1. Navigate to housing-insights/python folder in your local repo
2. run `eb create --profile codefordc --instance_type t2.small --single`
3. At the prompt, enter the name housinginsights-staging
4. DNS CNAME can be default (i.e. housinginsights-staging)
5. Select classic load balancer type. This will both create and deploy the current code. Wait while the server starts up, and then test the api url to make sure your changes behave as expected.
6. If you need to make any edits and deploy to a running test server, use: `eb deploy housinginsights-staging --profile codefordc`
7. **Important!** be sure to terminate the staging environment when you're done! You should only have this staging environment running while you're actively working on testing your live code. 
8. Run `eb terminate housinginsights-staging`, or visit the Elastic Beanstalk instance in the [web console](https://codefordc.signin.aws.amazon.com/console).  Note, be sure to include the name of the instance to terminate, since the default if none is specified is the production server. 
9. Use `eb list --profile codefordc` to verify that the instance has been terminated


### Temporary Notes

#### Columns needed for filter api route
These seem to be the ones needed, as you can see a few mistakes made it in to the end. These will need to be changed with the front end.
```
- nlihc_id
- census_tract
- neighborhood_cluster
- ward
- proj_name
- proj_addre
- proj_units_tot
- proj_units_assist_max
- proj_owner_type
- portfolio
- poa_end
- poa_start
- most_recent_topa_date
- topa_count
- most_recent_reac_score_num
- most_recent_reac_score_date
- sum_appraised_value_current_total
- violent_crime_count_census_tract
- violent_crime_count_neighborhood_cluster
- violent_crime_count_ward
- non_violent_crime_rate_census_tract
- non_violent_crime_rate_neighborhood_cluster
- non_violent_crime_rate_ward
- crime_rate_census_tract
- crime_rate_neighborhood_cluster
- crime_rate_ward
- construction_permits_rate_census_tract
- construction_permits_rate_neighborhood_cluster
- construction_permits_rate_ward
- building_permits_rate_census_tract
- building_permits_rate_neighborhood_cluster
- building_permits_rate_ward
- poverty_rate_census_tract
- poverty_rate_neighborhood_cluster
- poverty_rate_ward
- income_per_capita_census_tract
- income_per_capita_neighborhood_cluster
- income_per_capita_ward
- labor_participation_census_tract
- labor_participation_neighborhood_cluster
- labor_participation_ward
- fraction_single_mothers_census_tract
- fraction_single_mothers_neighborhood_cluster
- fraction_single_mothers_ward
- fraction_foreign_census_tract
- fraction_foreign_neighborhood_cluster
- fraction_foreign_ward
- acs_median_rent_census_tract
- acs_median_rent_neighborhood_cluster
- acs_median_rent_ward
```
