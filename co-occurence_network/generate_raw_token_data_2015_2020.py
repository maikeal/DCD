import os.path
import sqlite3
import re
import sys
import constants
#import nltk
from nltk.corpus import stopwords
import time

INPUT_DIR, OUTPUT_DIR = constants.INPUT_DIR, constants.OUTPUT_DIR
REGEX_SEPARATORS = r"\s+|[.,\/!$%\^&\*;:{}=\-_`~()|\[\]\u2022]" # currently not including # or @ because of their relevance to Twitter text/functionality

conn = sqlite3.connect(f"{INPUT_DIR}bios_2015_2020.sqlite")
cursor = conn.cursor()
rows_to_insert = []
cursor.execute("""SELECT user_id_str, bio_2015, bio_2020 FROM all_common_users""")

start = time.time()
print("starting outer loop")
progress = 0.0
for row in cursor:
	progress += 1.0
	print(f"progress: {progress * 100 / 2250812}")

	user_id = row[0] if row[0] else ""
	bio_2015 = row[1].casefold() if row[1] else ""
	bio_2020 = row[2].casefold() if row[2] else ""

	if user_id == "" or bio_2015 == "" or bio_2020 == "":
		continue

	tokens_2015, tokens_2020 = set(re.split(REGEX_SEPARATORS, bio_2015)), set(re.split(REGEX_SEPARATORS, bio_2020))
	stop_words = set(stopwords.words('english')).union(["com", "http", "https", "www"])
	stop_words = [stop_word for stop_word in stop_words if not stop_word in ["he","him","his","she","her","hers","they","them","theirs"]]
	tokens_2015, tokens_2020 = [token for token in tokens_2015 if not token in stop_words], [token for token in tokens_2020 if not token in stop_words]

	for t15 in tokens_2015:
		if t15 == "" or t15 == " ":
			continue
		rows_to_insert.append((user_id, '2015', t15))	
	for t20 in tokens_2020:
		if t20 == "" or t20 == " ":
			continue
		rows_to_insert.append((user_id, '2020', t20))
end = time.time()
print(f"done in {end - start}")

start2 = time.time()
print("starting db insert")
cursor.execute("CREATE TABLE IF NOT EXISTS user_year_token (user TEXT NOT NULL, year TEXT NOT NULL, token TEXT NOT NULL)")
cursor.executemany("INSERT INTO user_year_token VALUES (?, ?, ?)", rows_to_insert)
end2 = time.time()
# Save (commit) the changes
conn.commit()
conn.close()
print(f"done in {end2 - start2}")

