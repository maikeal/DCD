import os.path
import sqlite3
import re
import sys
import constants
import numpy as np
from nltk.corpus import stopwords
import time

INPUT_DIR, OUTPUT_DIR = constants.INPUT_DIR, constants.OUTPUT_DIR
REGEX_SEPARATORS = r"\s+|[.,\/!$%\^&\*;:{}=\-_`~()|\[\]\u2022]" # currently not including # or @ because of their relevance to Twitter text/functionality

TRUMP_TOKENS = ('trump', 'maga', 'trump2020')
BLM_TOKENS = ('blm', 'blacklivesmatter')

conn = sqlite3.connect(f"{INPUT_DIR}bios_2015_2020.sqlite")
cursor = conn.cursor()

def bernoulli_naive_bayes(bio_text):

	tokens = tuple(set(re.split(REGEX_SEPARATORS, bio_text.casefold())))
	trump_probability_calc = []
	blm_probability_calc = []
	
	#cursor.execute("SELECT COUNT(*) FROM all_common_users")
	#TOTAL_BIOS = cursor.fetchone()[0]
	TOTAL_BIOS = 1909399

	#cursor.execute(f"SELECT COUNT(DISTINCT user) FROM tokens20 WHERE token IN {str(TRUMP_TOKENS)}")
	#TRUMP_DENOMINATOR = cursor.fetchone()[0]
	TRUMP_DENOMINATOR = 5734

	#cursor.execute(f"SELECT COUNT(DISTINCT user) FROM tokens20 WHERE token IN {str(BLM_TOKENS)}")
	#BLM_DENOMINATOR = cursor.fetchone()[0]
	BLM_DENOMINATOR = 3846

	trump_prior = TRUMP_DENOMINATOR / TOTAL_BIOS # prior
	blm_prior = BLM_DENOMINATOR / TOTAL_BIOS # prior

	cursor.execute(f"SELECT SUM(transition_count) FROM transitions WHERE t15 IN {str(tokens).replace(',)', ')', 1)} AND t20 IN {str(TRUMP_TOKENS)} GROUP BY t15")
	for row in cursor:
		print(row[0])
		trump_probability_calc.append(row[0])

	cursor.execute(f"SELECT SUM(transition_count) FROM transitions WHERE t15 IN {str(tokens).replace(',)', ')', 1)} AND t20 IN {str(BLM_TOKENS)} GROUP BY t15")
	for row in cursor:
		print(row[0])
		blm_probability_calc.append(row[0])

	while len(trump_probability_calc) < len(tokens):
		trump_probability_calc.append(1)
		TRUMP_DENOMINATOR += 1
	while len(blm_probability_calc) < len(tokens):
		blm_probability_calc.append(1)
		BLM_DENOMINATOR += 1

	#trump_probability_calc = np.array(trump_probability_calc)
	#blm_probability_calc = np.array(blm_probability_calc)

	prob_trump = trump_prior * np.prod(np.true_divide(trump_probability_calc, TRUMP_DENOMINATOR))
	prob_blm = blm_prior * np.prod(np.true_divide(blm_probability_calc, BLM_DENOMINATOR))

	print(prob_trump)
	print(prob_blm)

	if prob_trump > prob_blm:
		prediction = 'trump' 
	elif prob_trump == prob_blm:
		prediction = 'equal' # this really shouldn't happen
	else: 
		prediction = 'blm'

	print(f"P(trump 2020 | bio={bio_text}) = { (prob_trump * 100) / (prob_trump + prob_blm)} %")
	print(f"P(blm | bio={bio_text}) = { (prob_blm * 100) / (prob_trump + prob_blm)} %")
	print(f"Prediction: {prediction}")

	#conn.close()

while True:
	bio = input("Enter a bio, or type 'stop' to quit: ")
	if bio == 'stop':
		break
	bernoulli_naive_bayes(bio)

conn.close()