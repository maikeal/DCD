import os.path
import sqlite3
import re
import sys

import nltk
from nltk.corpus import stopwords
#from nltk.tokenize import TweetTokenizer

from pprint import pprint

# Specify where the bio databases live.
INPUT_DIR = "data/"
OUTPUT_DIR = "data/results/"

OUTPUT_FILE_NAME = OUTPUT_DIR + "cooccurrences.sqlite"

# If output file already exists, then print an error.
if os.path.isfile(OUTPUT_FILE_NAME):
	print("Output file already exists: " + OUTPUT_FILE_NAME)
	sys.exit(1)

REGEX_SEPARATORS = r"\s+|[.,\/!$%\^&\*;:{}=\-_`~()|\[\]\u2022]" # currently not including # or @ because of their relevance to Twitter text/functionality

def count_cooccurrences(skip_stop_words=True,  skip_pronouns=False):

	cooccurrence_dict = {}
	counts_dict = {}
	denom = 0

	input_conn = sqlite3.connect(INPUT_DIR + "sample2020bios.sqlite")
	input_cursor = input_conn.cursor()
	input_cursor.execute("""SELECT bio FROM one_bio_per_user_per_year""")

	for row in input_cursor:
		denom += 1
		bioText = row[0] if row[0] else "" # This test is necessary, because empty bios get retrieved as None. re.search will error on None.
		bioText = bioText.casefold() # to lowercase

		tokens = re.split(REGEX_SEPARATORS, bioText)
		tokens = set(tokens)

		if skip_stop_words:
			stop_words = set(stopwords.words('english'))#.update(["com", "http", "https", "www"])
			if not skip_pronouns:
				stop_words = [stop_word for stop_word in stop_words if not stop_word in ["he","him","his","she","her","hers","they","them","theirs"]]
			tokens = [token for token in tokens if not token in stop_words]

		# MAIN LOOP
		for token_i in tokens:
			# First, check for empty string.  Do not count it.
			if token_i == "":
				continue
			# Next, check if token already in cooccurrence_dict
			if token_i not in cooccurrence_dict:
				cooccurrence_dict[token_i] = {}
			# NESTED LOOP
			for token_j in tokens:
				if token_j == "":
					continue
				if token_j == token_i:
					if token_i not in counts_dict:
						counts_dict[token_i] = 1
					counts_dict[token_i] += 1
					continue
				if token_j not in cooccurrence_dict[token_i]:
					cooccurrence_dict[token_i][token_j] = 1
				else:
					cooccurrence_dict[token_i][token_j] += 1

	# Close the connection to the input DB.
	input_conn.close()
	input_cursor = None

	return cooccurrence_dict

#pprint(count_cooccurrences())
#with open('output.txt', 'wt') as out:
#	pprint(count_cooccurrences(), stream=out)


def recordsGenerator():
	cooccurrence_dict = count_cooccurrences()
	for token_i in cooccurrence_dict:
		for token_j in cooccurrence_dict[token_i]:
			yield (token_i, token_j, cooccurrence_dict[token_i][token_j])

# Create an empty output DB with the correct structure and a cursor.
output_conn = sqlite3.connect(OUTPUT_FILE_NAME)
output_cursor = output_conn.cursor()

output_cursor.execute("""CREATE TABLE cooccurrences
             (token1, token2, cooccurrence)""")

INSERT_SCRIPT = """INSERT INTO cooccurrences VALUES (?,?,?)"""
output_conn.executemany(INSERT_SCRIPT, recordsGenerator())

# Save (commit) the changes
output_conn.commit()
# Close the connection
output_conn.close()
output_cursor = None