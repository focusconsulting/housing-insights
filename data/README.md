# /data notes
This folder is not stored in Git, because the data file sizes are too large. Instead, they are synced to S3.

Most users will not need to have access to the source files in this folder, as they are loaded into our Postgres database once and then can be accessed from there. 

```
/raw 		#source data as downloaded, grouped by source location
/interim    #for holding non-final output files and one-off analyses
/processed	#holds all our flat files for our D3 team. 
			#This folder should be pruned regularly to have one copy of 
			#the most up to date data when needed. 
```


For updating the manifest that corresponds to this file, you can list all files in the directory with this terminal command (Windows):
dir /b /s /a:-D > data_filepaths.txt
