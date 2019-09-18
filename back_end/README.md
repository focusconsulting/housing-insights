# Back End of Housing Insights
This portion of the project holds the "back end" of the website implemented in python. It contains three main things:

1. `application.py`: This is the main application file and ultimate server-side logic for the tool.
2. `ETL`: Extract, Transform, Load. This set of code is responsible for loading in data sources into the tool.
3. `API`: Application Programming Interface. This set of code is responsible for the routes accessible to the front end of the website.

Both `ETL` and `API` have their own `README` documents with details of their implementation.

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
