# Tokenizes each bio in order to calculate the prevalence of bios containing any possible word/token.
# Counts bios (that is, accounts) on each OneBioPerUserPerYear database.
#
# Output is a sqlite database:
#   token, year, prevalence, numerator, denominator, sampleType
# sampleType will be cross for CROSS-SECTIONAL data.  This is based on six one_bio_per_year_YYYY.sqlite files.
# sampleType will be longi for LONGITUDINAL data.  This is based on the one sixyear_YAU_intersection.sqlite file.

import os.path
import sqlite3
import re
import sys

# Specify where the bio databases live.
inputDir = "/gpfs/projects/JonesSkienaGroup/jason_tw/OneBioPerUserPerYear/data/"

# Specify where output file will live.
outputDir = "/gpfs/projects/JonesSkienaGroup/jason_tw/OneBioPerUserPerYear/data/sixyear_counts/"
outputFileName = outputDir + "all_tokens_counts.sqlite"

# If output file already exists, then print an error.
if os.path.isfile(outputFileName):
	print("Output file already exists: " + outputFileName)
	sys.exit(1)

# Create a function that takes raw counts as input.
# The output is a prevalence, stated as an integer.
# The unit is "per 10,000 users."
def rawToPrev(numerator, denominator):
	returnValue = "NA"
	if (denominator == 0 or denominator == "NA"):
		return returnValue
	
	returnValue = float(numerator) / float(denominator)
	returnValue = returnValue * 10000
	returnValue = round(returnValue)
	returnValue = int(returnValue)
	
	return returnValue


# Create the list of columns.
countBiosCols = ["token", "year", "prevalence", "numerator", "denominator", "sampleType"]

# Create an empty DB with the correct structure.
conn = sqlite3.connect(outputFileName)
c = conn.cursor()

# Create the table which will contain results.
c.execute("""CREATE TABLE all_tokens_counts
             (token, year, prevalence, numerator, denominator, sampleType)""")

# We batch all the inserts and write everything at once at the end of the loop.
recordsToInsert = []
countsDict = {}

# Prepare to run a for loop over the years to count matches to the regex.

# Create the list of years.
theYears = ["2015", "2016", "2017", "2018", "2019", "2020"]

# For each year, all the steps are the same, except for the target DB to search.
for theYear in theYears:
	# We batch all the inserts and write everything at once at the end of the loop.
	recordsToInsert = []	
	countsDict = {}
	denom = 0
	sampleType = "cross"

	# Create db connection.
	getBioConn = sqlite3.connect(inputDir + "one_bio_per_year_" + theYear + ".sqlite")
	getBioCursor = getBioConn.cursor()
	
	# Walk through the bios db and get counts.
	getBioCursor.execute("""SELECT bio FROM one_bio_per_user_per_year;""") 
	for row in getBioCursor:
		# Increment the count of bios.
		denom += 1
		# Get the bio as a string.
		bioText = row[0] if row[0] else "" # This test is necessary, because empty bios get retrieved as None. re.search will error on None.
		bioText = bioText.casefold()
		# Tokenize on word boundary, regex is \b.
		#   Or any amount of whitespace \w+.
		tokens = re.split(r"\b|\s+", bioText)
		# Trim whitespace from every token.
		#   I think this is no longer necessary because I now split on whitespace.
		tokens = [eachToken.strip() for eachToken in tokens]
		# Make the tokens list into a set.
		# We only want to count 1 if present; we want bio prevalence, not word count.
		tokens = set(tokens)
		for token in tokens:
			# First, check for empty string.  Do not count it.
			if token == "":
				continue
			# Otherwise, add one to count of accounts that contain this token.
			if token in countsDict:
				countsDict[token] = countsDict[token] + 1
			else:
				countsDict[token] = 1
	
	# Prepare records to insert.
	for countedToken in countsDict:
		# Build a tuple.  It contains the values for a row.
		insertValuesTuple = ()
		insertValue = countedToken # token
		insertValuesTuple += (insertValue,)
		insertValue = theYear # year
		insertValuesTuple += (insertValue,)
		insertValue = rawToPrev(countsDict[countedToken], denom) # prevalence
		insertValuesTuple += (insertValue,)
		insertValue = countsDict[countedToken] # numerator
		insertValuesTuple += (insertValue,)
		insertValue = denom # denominator
		insertValuesTuple += (insertValue,)
		insertValue = sampleType # sampleType
		insertValuesTuple += (insertValue,)
		# Append the tuple (one row for one token) onto a list of records to insert.
		# But only if the prevalence is greater than zero.
		# NOTE that this will cut off a long tail of low-frequency, but possibly interesting (to someone) tokens.
		if (rawToPrev(countsDict[countedToken], denom) > 0):
			recordsToInsert.append(insertValuesTuple)
	
	# Execute an insert statement with the values for this run.
	insertSetup = """INSERT INTO all_tokens_counts VALUES (?,?,?,?,?,?)"""
	conn.executemany(insertSetup, recordsToInsert)
	
	# Save (commit) the changes
	conn.commit()
	
	# Close the connection.
	getBioConn.close()
	getBioCursor = None

# The previous loop counted bios from the cross-sectional dbs.
# The loop below will count bios from the longitudinal (intersection) db.

# For each year, all the steps are the same, except for the target column to search.
for theYear in theYears:
	# We batch all the inserts and write everything at once at the end of the loop.
	recordsToInsert = []	
	countsDict = {}
	denom = 0
	sampleType = "longi"
	
	# Create db connection.
	getBioConn = sqlite3.connect(inputDir + "sixyear_YAU_intersection.sqlite")
	getBioCursor = getBioConn.cursor()
	
	# Walk through the bios db and get counts.
	getBioCursor.execute("""SELECT bio_""" + theYear + """ FROM sixyear_YAU_intersection;""") 
	for row in getBioCursor:
		# Increment the count of bios.
		denom += 1
		# Get the bio as a string.
		bioText = row[0] if row[0] else "" # This test is necessary, because empty bios get retrieved as None. re.search will error on None.
		bioText = bioText.casefold()
		# Tokenize on word boundary, regex is \b.
		#   Or any amount of whitespace \w+.
		tokens = re.split(r"\b|\s+", bioText)
		# Trim whitespace from every token.
		#   I think this is no longer necessary because I now split on whitespace.
		tokens = [eachToken.strip() for eachToken in tokens]
		# Make the tokens list into a set.
		# We only want to count 1 if present; we want bio prevalence, not word count.
		tokens = set(tokens)
		for token in tokens:
			# First, check for empty string.  Do not count it.
			if token == "":
				continue
			# Otherwise, add one to count of accounts that contain this token.
			if token in countsDict:
				countsDict[token] = countsDict[token] + 1
			else:
				countsDict[token] = 1
	
	# Prepare records to insert.
	for countedToken in countsDict:
		# Build a tuple.  It contains the values for a row.
		insertValuesTuple = ()
		insertValue = countedToken # token
		insertValuesTuple += (insertValue,)
		insertValue = theYear # year
		insertValuesTuple += (insertValue,)
		insertValue = rawToPrev(countsDict[countedToken], denom) # prevalence
		insertValuesTuple += (insertValue,)
		insertValue = countsDict[countedToken] # numerator
		insertValuesTuple += (insertValue,)
		insertValue = denom # denominator
		insertValuesTuple += (insertValue,)
		insertValue = sampleType # sampleType
		insertValuesTuple += (insertValue,)
		# Append the tuple (one row for one token) onto a list of records to insert.
		# But only if the prevalence is greater than zero.
		# NOTE that this will cut off a long tail of low-frequency, but possibly interesting (to someone) tokens.
		if (rawToPrev(countsDict[countedToken], denom) > 0):
			recordsToInsert.append(insertValuesTuple)
	
	# Execute an insert statement with the values for this run.
	insertSetup = """INSERT INTO all_tokens_counts VALUES (?,?,?,?,?,?)"""
	conn.executemany(insertSetup, recordsToInsert)
	
	# Save (commit) the changes
	conn.commit()
	
	# Close the connection.
	getBioConn.close()
	getBioCursor = None

