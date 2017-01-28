

Configuring the Amazon Web Services Command Line Interface (awscli)
==================================================================

First off you can install the Command Line Interface with pip:

``pip install awscli``


.. code:: python

   # The aws configure command at the command line pulls up an interactive 
   # session. Press <enter> after each line. Values needed can be found in 
   # secrets.json, which you will need to request directly from the project team. 

   # This command configures a awscli profile called 'housinginsights', 
   # which means you will be required to add the argument "--profile 
   # housinginsights" to every awscli command. You can optionally omit 
   # this if housinginsights is the only project you want to use awscli for.

   $ aws configure --profile housinginsights
   AWS Access Key ID [None]: <use secrets.json.s3.access_key_id>
   AWS Secret Access Key [None]: <use secrets.json.s3.secret_access_key>
   Default region name [None]: us-east-1
   Default output format [None]: <none>



Using AWS Sync
--------------
Because our raw data is large, we don't store it in our GitHub repository (it has a 1Gb total limit on repository size). The sync command of the awscli acts like Dropbox or similar services, but manually using the command line. There is only ever one copy of the data (unlike Git), and you can download changes from S3 or push your own changes to S3. S3 is a file storage service from Amazon Web Services.


Getting the latest data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Do this before you add/download new files to the /data folder, to make sure you're up to date. 

1. Navigate to the root project folder ``path\to\your\housing-insights\``, Type `ls` (`dir` on windows) and **make sure you see the `data` folder.**
2. See if there are any updates to fetch: ``aws s3 sync s3://housinginsights data --profile housinginsights --dryrun``  
  * syntax for the sync command is sync <from folder> <to folder>. This command tells aws to sync all the contents of our S3 bucket to the folder named "data" located in your current directory. 
  * ``--dryrun`` flag lists all the actions that would be performed (e.g. 'download: /data/newfile.txt'). If none, no action needed. If there are some, make sure they will not cause any conflicts with changes you have made locally since you last synced.
3. Download the data: ``aws s3 sync s3://housinginsights data --profile housinginsights``


If you add or update any data files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Make sure you download updates before you start working.  

2.  Navigate to the root project folder ``path\to\your\housing-insights\`` Type `ls` (`dir` on Windows) and check for the `data` folder

3. Test push your changes: 
``aws s3 sync data s3://housinginsights --profile housinginsights --dryrun`` Note, this is the same command as above, but with the order of the two folders reversed. 

4. Make sure it all is what you want, then do it for real:
``aws s3 sync data s3://housinginsights --profile housinginsights`` This pushes your folder contents *to* S3.

If you delete files
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
The sync command only updates or adds files by default. If you deleted a file and actually want it to be deleted (e.g. it was moved to another folder), add the ``--delete`` flag

1. Same as above, but add the `--delete` flag.
