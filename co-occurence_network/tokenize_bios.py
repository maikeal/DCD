import os.path
import sqlite3
import re
import sys

# Specify where the bio databases live.
inputDir = "data/"
outputDir = "data/bio_token_counts/"

outputFileName = outputDir + "token_counts_2020.sqlite"

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

# Create the list of columns for the output db.
countBiosCols = ["token", "year", "prevalence", "numerator", "denominator", "sampleType"]

# Create an empty output DB with the correct structure and a cursor.
conn_out = sqlite3.connect(outputFileName)
c_out = conn_out.cursor()

# Create the table which will contain results.
c_out.execute("""CREATE TABLE token_counts_2020
             (token, year, prevalence, numerator, denominator, sampleType)""")

# We batch all the inserts and write everything at once at the end of the loop.
recordsToInsert = []
countsDict = {}
countsDict = {}
denom = 0
sampleType = "cross"

conn_in = sqlite3.connect(inputDir + "sample2020bios.sqlite")
c_in = conn_in.cursor()

c_in.execute("""SELECT bio FROM one_bio_per_user_per_year""")
for row in c_in:
	# Increment the count of bios.
	denom += 1

	# Get the bio as a string.
	bioText = row[0] if row[0] else "" # This test is necessary, because empty bios get retrieved as None. re.search will error on None.
	bioText = bioText.casefold() # to lowercase

	# Tokenize on word boundary, regex is \b.
	#   Or any amount of whitespace \w+.
	tokens = re.split(r"\b|\s+", bioText)

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
	insertValue = "2020" # year
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
insertSetup = """INSERT INTO token_counts_2020 VALUES (?,?,?,?,?,?)"""
conn_out.executemany(insertSetup, recordsToInsert)
# Save (commit) the changes
conn_out.commit()

# Close the connection.
conn_in.close()
c_in = None