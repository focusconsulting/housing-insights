

Configuring the Amazon Web Services Command Line Interface (awscli)
-------------------------------------------------------------------

Looking for instructions on downloading data from S3? These have moved to `our website <http://housinginsights.org/resources/aws-sync.html/>`_.


Getting data from APIs
======================

Using data.sh
-------------

data.sh is a command line script to pull data from external data sources. It only supports nix environments (no Windows). 
On Windows, you can call the data.py script directly using Python - see below. data.sh is a wrapper around data.py so works
similarly. 

data.sh uses modules in the housinginsights/sources directory to pull information from external data sources. It defaults
to outputing the data to a csv file (you need to specifiy one with -o or --ouput), but if you specify --outtype stdout,
it will print the raw json returned from the data source to your terminal.


1. Navigate to your root project folder: ``cd /path/to/your/housing-insights`` . Change to `python` directory. ``cd python``.

2. Make sure your vitual environment named `env` is set up. ``virtualenv env && env/bin/pip install -r requirements.txt``.

3. To see the available options, run `bin/data.sh --help`. Usage with common options would look like:
  
  ``bin/data.sh -o /path/to/some/csvfile.csv --params "key:value;key2:value2" [api] [api_method]``

As an example, to access data from the Master Address Record (MAR) using the mar.py sources module, you could run:

``bin/data.sh -o ~/csvfile --params "location:641 S St NW" mar find_location``

The available api modules are the modules in the sources directory. For example: if there was a file named `myapi.py`
which has a method in its APIConn class named `find_stuff` which takes the parameters `location` and `radius`, 
you would make the call:

``bin/data.sh -o ~/csvfile --params "location:Some Place;radius:5m" myapi find_stuff``


Using data.py
-------------
Using data.py works the same as data.sh as described above, but you'll first need to activate your virtual environment. 

1. Activate your virtual environment. Anaconda: ``activate housing-insights`` or venv: ``source bin/activate`` (may vary based on 
where you chose to put your venv setup)

2. Navigate to the ``python/cmd`` folder. 

3. Run the command with appropriate arguments: ``python data.py mar find_location --output ../../data/interim/out.csv --params "location:617123 Morton Street NW"``

