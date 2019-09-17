# Local Database Configuration (if Docker doesn't work)

If you have issues with Docker installation, it is also possible to set up a local database directly. For most Python coding tasks, you will need both the database engine (Postgres) and a database client. For adding documentation, Jekyll is helpful - but we recommend waiting to configure Jekyll until you actually need it. 

# Installations

## Database Server (Postgres)
The database server stores the data and responds to queries to return or alter the data. We use Postgres 9.5 as our database server. 

### Postgres 9.5
If you think you might already have Postgres installed, open
a command prompt and type `postgres --version`. If this returns "postgres
(PostgreSQL) 9.5.XXX, you can skip installation. 

Installation suggestions: 

* Use the default password of `postgres` for the postgres user if prompted 
* Skip the step for Stack Builder if prompted - it is not necessary 
* Use port 5432 unless you have another Postgres installation already, in which case you
will need to select an unused port (try 5433 or 5434)

## Database client
A database client talks to the database server, and provides you with an interface to both see what is in the database and to execute SQL queries. Choose whichever database client you prefer, as long as it is compatible with Postgres. Two options are listed below - pgAdmin is slightly easier to install, though I think Valentina has a slightly easier to understand interface. 

After installing the version appropriate to your machine (Windows/Mac etc.), follow the instructions below to connect to Postgres and to create a new local database called 'housinginsights_local'. 

### Database client (pgAdmin4)

1) On the left hand panel, expand the + sign under Servers
2) Double click PostgreSQL 9.5 to activate postgres, then drill down to Databases and postgres to activate the default database that came with your installation.
3) Click Tools -> Query Tool to open a SQL editor
4) In the SQL editor, enter `CREATE DATABASE housinginsights_local` and click the lightning bolt to execute.
5) Make sure it worked - on the left hand navigation pane, under Postgres->Databases you should be able to right-click and 'refresh' and see the housinginsights_local database listed. You're now ready to add data to the database using our Python code. 

### Database client (e.g. Valentina Studio)

1) After installation, if you Postgres installed you should see the PostgreSQL icon with localhost:5432 (postgres) underneath on the right hand side. 
2) Double click on PostgreSQL, and the 'SQL' button on the taskbar should be available. Double click
3) In the SQL editor, enter `CREATE DATABASE housinginsights_local` and click 'Execute'.
4) Click File->Connect to...
5) Select 'PostgreSQL' on the left and enter the connection info:
    * host: localhost
    * Database: housinginsights_local
    * User: postgres
    * Password: postgres
    * Port: 5432  (unless you changed this during install)
6) Select Tools -> Schema Editor on the taskbar. You should now have 'localhost' available under Connections. Double click this and housinginsights_local should show up under the Databases column.


