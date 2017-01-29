import logging

#Configure logging
logging_filename = "../logs/example.log"
logging.basicConfig(filename=logging_filename, level=logging.DEBUG)


#----------------
# Example logging
#----------------
# When you are writing code, instead of using the 'print' statement (which only
# is shown on the command line), you can instead use logging to write stuff to the log
# files. 
#	Benefit: 	Easier to sort through complex stuff, when you want to print lots of things
#				as you work through a bug.
#   Downside:	Don't forget to delete your log files from time to time - they will get big
#				They will be recreated next time you start the program.


# To see logging in action, run this file and then look in the newly created example.log file
# Every time you re-run this file, messages will be *added* to the log file
# Every time you delete the log file, and then re-run this file it will be created fresh.
logging.warning("--------------------starting module------------------")
logging.error("My error message")
logging.critical("My super bad error message")
logging.warning("This is a message that would always be written to logs")
logging.info("This message only comes through when level=logging.DEBUG")

#adding stack_info=True makes a log also report where it was called from (e.g. line 29), like a regular python error
logging.debug("this is a debug message", stack_info=True)

print("Example logging complete! Open example.log to see what happened.")
