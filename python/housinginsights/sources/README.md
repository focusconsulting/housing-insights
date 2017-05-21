SOURCES DIRECTORY
-----------------

This directory is to be used to store modules to access various external APIs.
To be compatible with get_api_data.py, use the following conventions. See get_api_data.py for detailed 
instructions on how to run and parameters. 

STRUCTURE:
---------
( * is used to represent an important class)
/sources
    /base.py - - stores the base connection classes. Your module should use one of these
                  as its self.conn attribute. If you need authentication, inherit from BaseAPIConn
                  and extend the base class, but for open apis, it should be sufficient.
            
                * BaseApiConn -- base connection to use as the self.conn attribute for your api module.

   /mar.py - - an example api module. Inside should be a class with the convention of the module name 
                (with first letter in caps) + ApiConn. So in this case it would be MarApiConn. This is the
                class that data.sh will try to import. 

                * MarApiConn -- API connection class import/used by data.sh. Each PUBLIC method should be available
                for use by data.sh. For example _read_to_csv is private and you should not expect a user to want to use
                it through data.sh.

