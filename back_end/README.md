# Back End of Housing Insights
This portion of the project holds the "back end" of the website implemented in python. It contains the following:

* `app.py`: The main application file and ultimate server-side logic for the tool.
* `mailer.py`: Contains code to send e-mails related to the tool automatically.
* `test.py`: Contains tests for the back end portion of the project. Run `python test.py` to run all tests.
* `Dockerfile`: Sets up the deployment environment.
* `Dockerfile-development`: Sets up the development environment.
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
    * `wmata_helper.py`: Handles bus stop and rail station data grouping for the API output format.
    * `make_geographic_weights.py`: Creates weights for demographics calculations. This should only be run if the census boundaries have changed.
    * `make_zone_facts.py`: Creates the zone facts table from ACS, crime, and permit data.
    * `filter_view_query.py`: The SQL query for the filter API route.

## Reference and Common Changes
* E-mail functionality can be changed `mailer.py`
* API routes can be added to `app.py`
* User table loading routes can be added to `app.py`
* Raw data ingestion occurs in a file within `ETL`
* Specific columns are sent to the database via `ETL` as well
* `ETL` functions can be exposed to the app in `ELT/__init__.py`

## Data Sources

#### Downloaded From the S3
* Preservation Catalog Projects
* Preservation Catalog Subsidies
* Preservation Catalog REAC Information
* TOPA Information

#### Collected From External Source
* [American Community Survey Data](https://www.census.gov/programs-surveys/acs/data.html)
* [Open Data DC Crime](https://opendata.dc.gov/datasets/crime-incidents-in-2019)
* [Open Data DC Building Permits](https://opendata.dc.gov/datasets/building-permits-in-2019)
* [Open Data DC Affordable Housing Projects](https://opendata.dc.gov/datasets/34ae3d3c9752434a8c03aca5deb550eb_62)
* [Open Data DC Integrated Tax System Public Extract](https://opendata.dc.gov/datasets/integrated-tax-system-public-extract)
* [The DC Master Address Repository](https://opendata.dc.gov/datasets/address-points)
* [Open Data DC Census Tract Shapefiles](https://opendata.dc.gov/datasets/census-tracts-by-population-2000)
* [Open Data DC Neighborhood Cluster Shapefiles](https://opendata.dc.gov/datasets/neighborhood-clusters)
* [WMATA API](https://developer.wmata.com/)
* [Bus Stops](https://opendata.dc.gov/datasets/e85b5321a5a84ff9af56fd614dab81b3_53)
* [Rail Stations](https://opendata.dc.gov/datasets/metro-stations-in-dc)


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

## API Routes
* `new_project`: Returns all projects.
* `new_project/nlihc_id`: Returns project information for a single project.
* `new_project/<nlihc_id>/subsidies/`: Returns subsidies for a single project.
* `projects/<dist>`: Returns projects within half a mile of a set of coordinates.
* `new_filter`: For the filter view, returns just about everything.
* `new_wmata/<nlihc_id>`: Returns transit information for all transit within half a mile of a project.
* `new_zone_facts/<column_name>/<grouping>`: Returns the zone fact for a specific zone type.

## Database Connection
This project uses a PostgreSQL database, with the development version using a Docker image and the production database hosted on AWS.
Connecting to the database happens two ways:

1. A SQLAlchemy engine sent through pandas functions. The pandas function `to_sql` allows clean and simple data loading for entire tables as
they are crafted in `ETL`. The function only takes a SQLAlchemy engine object or SQLite connection, so this was necessary.
2. The API creates a new `psycopg2` connection with each call and closes it appropriately. This ensures there are no hung connections to the production database.

**Why not SQLAlchemy throughout?**

An earlier of this project used SQLAlchemy to reflect the database, but did not consistently use the ORM for querying. It actually had the data loading process entirely separate from the Flask application, so
having the ORM and infrastructure to make migrations did not exists. After consideration, it was revealed the front end required a flat and wide return of data that made using the ORM over raw SQL
a little cumbersome. If this changes in the future, refactoring using an ORM may be more appropriate.

## Environments / Dependencies
The Dockerfile creates and maintains a conda enviroment with the necessary python dependencies. While this set up was used in a previous iteration of the project, it is required moving forward.
As this project uses the `geopandas` package, conda allows the collection and use of non-python dependencies that would be more difficult to set up without it.

The following packages are used in this project:
- `sqlalchemy`
- `numpy`
- `pandas`
- `geopandas`
- `flask`
- `pyyaml`
- `requests`
- `xlrd`
- `flask-cors`
- `flask-sqlalchemy`
- `flask-restless`
- `flask-marshmallow`
- `psycopg2-binary`
- `flask-apscheduler`

### Running the code
All code is ultimately called and used from `app.py`, therefore, running code should be done at this top level (`back_end`) inside the Docker container.
To do adhock testing of code within ETL, you may need to adjust the imports, such as `import utils` rather than `from . import utils`.

For development do the following.
1. Use the appropriate `docker-compose` command to start the containers.
2. Run `docker-compose exec sandbox bash` to enter the python container.
3. Navigate to the application by running `cd /repo/back_end/`.
4. Run `python app.py` to start the application.

### Elastic Beanstalk Deployment Setup
- Install the Elastic Beanstalk Command Line Interface: `$ pip install awsebcli`
- Configure a profile that uses the AWS credentials for our Code for DC API account: `aws configure --profile codefordc`
- Enter the public and secret keys provided to you by an admin; default location and output format can be None (just press enter)

### Elastic Beanstalk Deployment Overview 
1. Reference the [documentation](https://docs.aws.amazon.com/en_pv/elasticbeanstalk/latest/dg/single-container-docker.html#single-container-docker.deploy-local) 
2. Navigate to the `back_end` folder in your local repo
3. Create the environment with `eb init -p docker housinginsights-codefordc` 
4. Test it locally with `eb local run --port 5000`
3. Actually deploy with `eb deploy housinginsights-codefordc --profile codefordc` 
4. Wait a few minutes while the server restarts with the new version of the project.
5. Double check your work at [http://housinginsights.us-east-1.elasticbeanstalk.com/](http://housinginsights.us-east-1.elasticbeanstalk.com/)

#### Deploy to staging enviroment to test
1. Do steps 1 - 3 above.
2. run `eb create --profile codefordc --instance_type t2.small --single`
3. At the prompt, enter the name housinginsights-staging
4. DNS CNAME can be default (i.e. housinginsights-staging)
5. Select classic load balancer type. This will both create and deploy the current code. Wait while the server starts up, and then test the api url to make sure your changes behave as expected.
6. If you need to make any edits and deploy to a running test server, use: `eb deploy housinginsights-staging --profile codefordc`
7. **Important!** be sure to terminate the staging environment when you're done! You should only have this staging environment running while you're actively working on testing your live code.
8. Run `eb terminate housinginsights-staging`, or visit the Elastic Beanstalk instance in the [web console](https://codefordc.signin.aws.amazon.com/console).  Note, be sure to include the name of the instance to terminate, since the default if none is specified is the production server.
9. Use `eb list --profile codefordc` to verify that the instance has been terminated
