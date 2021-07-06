import os.path
import sqlite3
import re
import sys
import constants
import nltk
from nltk.corpus import stopwords

INPUT_DIR OUTPUT_DIR = constants.INPUT_DIR, constants.OUTPUT_DIR
YEAR_1, YEAR_2 = 2015, 2020

TRUMP_KEYWORDS = ['trump']
BLM_KEYWORDS = ['#blm']

def count_transitions(KEYWORDS, skip_pronouns=False):

	counts = {} # Will be a dict of dicts: { keyword_0: {token_0: count_0, token_1: count_1... token_i: count_i}, ... , keyword_n: {...} }

	y2_conn = sqlite3.connect(INPUT_DIR + "one_bio_per_year_" + YEAR_2 + ".sqlite")
	y2_cursor = y2_conn.cursor()

	y1_conn = sqlite3.connect(INPUT_DIR + "one_bio_per_year_" + YEAR_1 + ".sqlite")
	y1_cursor = y1_conn.cursor()

	for keyword in KEYWORDS:
		y2_cursor.execute(f"SELECT user_id_str, bio FROM one_bio_per_user_per_year WHERE bio LIKE ('%{keyword}%');")
		for row in y2_cursor:
			user_id_str = row[0]
			y2_bio_text = row[1] if row[1] else ""

			y1_cursor.execute(f"SELECT bio FROM one_bio_per_user_per_year WHERE user_id_str={user_id_str};")
			y1_row = y1_cursor.fetchone()
			if y1_row:
				y1_bio_text = row[0]
				tokens = re.split(r"\s+|[.,\/!$%\^&\*;:{}=\-_`~()|\[\]\u2022]", y1_bio_text)
				tokens = set(tokens)
				
				stop_words = set(stopwords.words('english')).union(["com", "http", "https", "www"])
				if not skip_pronouns:
					stop_words = [stop_word for stop_word in stop_words if not stop_word in ["he","him","his","she","her","hers","they","them","theirs"]]
				tokens = [token for token in tokens if not token in stop_words]
				
				for token in tokens:
					if token == "":
						continue
					if token not in counts:
						counts[keyword][token] = 1
					else:
						counts[keyword][token] += 1

	return counts