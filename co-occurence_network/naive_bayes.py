import os.path
import sqlite3
import re
import sys
import argparse
import constants
from nltk.corpus import stopwords
from random import randrange
import time
from pprint import pprint
from collections import OrderedDict

INPUT_DIR, OUTPUT_DIR = constants.INPUT_DIR, constants.OUTPUT_DIR

EXPLICIT_LIBERAL_KEYWORDS = ('liberal', 'progressive', 'democrat', 'socialist', 'voteblue')
IMPLICIT_LIBERAL_KEYWORDS = ('blm', 'blacklivesmatter', 'black lives matter', 'feminist', 'free palestine', 'feelthebern', 'bidenharris', 'biden')
LIBERAL_KEYWORDS = EXPLICIT_LIBERAL_KEYWORDS + IMPLICIT_LIBERAL_KEYWORDS

EXPLICIT_CONSERVATIVE_KEYWORDS = ('conservative', 'republican', 'libertarian', 'tcot')
IMPLICIT_CONSERVATIVE_KEYWORDS = ('trump', 'maga', 'deplorable', 'backtheblue', 'bluelivesmatter', 'alllivesmatter', 'wwg1wga', 'qanon', 'nra', 'cancel culture', 'pro-life', '#draintheswamp')
CONSERVATIVE_KEYWORDS = EXPLICIT_CONSERVATIVE_KEYWORDS + IMPLICIT_CONSERVATIVE_KEYWORDS

POLITICAL_KEYWORDS = LIBERAL_KEYWORDS + CONSERVATIVE_KEYWORDS

parser = argparse.ArgumentParser()
#parser.add_argument('--year1', '-y1', help="specify year 1", type=int, default=2015)
#parser.add_argument('--year2', '-y2', help="specify year 2", type=int, default=2020)
parser.add_argument('--balanced', '-b', help="specify whether to use political_bios_balanced instead of political_bios", action='store_true')
parser.add_argument('--keepduplicates', '-keepdups', help="specify whether to consider duplicate tokens", type=bool, default=True)
parser.add_argument('--details', '-d', action='store_true')
parser.add_argument('--details_wrong', '-dw', action='store_true')
parser.add_argument('--details_political', '-dp', action='store_true')
parser.add_argument('--details_nonpolitical', '-dnp', action='store_true')
parser.add_argument('--conditional_probs', '-cp', action='store_true')

args = parser.parse_args()
#YEAR_1, YEAR_2 = args.year1, args.year2

REGEX_SEPARATORS = r"\s+|[.,\/!$%\^&\*;:{}=\-_`~()|\[\]\u2022]" # currently not including # or @ because of their relevance to Twitter text/functionality

BALANCED = args.balanced
KEEP_DUPLICATES = args.keepduplicates
PRINT_EACH_TEST = args.details
PRINT_WRONG = args.details_wrong
PRINT_POLITICAL = args.details_political
PRINT_NONPOLITICAL = args.details_nonpolitical
PRINT_CONDITIONAL_PROBS = args.conditional_probs

conn = sqlite3.connect(f"{INPUT_DIR}bios_six_year.sqlite")
cursor = conn.cursor()

TABLE_NAME = 'political_bios_balanced' if BALANCED else 'political_bios'
if BALANCED:
	cursor.execute(""" CREATE TEMP VIEW political_bios_balanced AS 
						SELECT *
						FROM ( SELECT * FROM political_bios WHERE ideology=-1 ORDER BY RANDOM() LIMIT 16064)
						UNION
						SELECT *
						FROM ( SELECT * FROM political_bios WHERE ideology = 1 ORDER BY RANDOM());
					""")

start_time = time.time()
print("Fetching data...")
cursor.execute(f"SELECT bio_2015, bio_2016, bio_2017, bio_2018, bio_2019, bio_2020, ideology FROM {TABLE_NAME} WHERE ideology != 0 ORDER BY RANDOM()")
COMPLETE_DATA = cursor.fetchall()
TRAINING_SET = COMPLETE_DATA[:4*len(COMPLETE_DATA)//5]
TEST_SET = COMPLETE_DATA[4*len(COMPLETE_DATA)//5:]
print(f"Fetched data in {time.time() - start_time}")
conn.close()

def train_and_test(YEAR_1=2015, YEAR_2=2020):
	number_of_conservative_bios = 0
	number_of_liberal_bios = 0
	#number_of_political_bios = number_of_liberal_bios + number_of_conservative_bios

	number_of_tokens_in_all_conservative_bios = 0
	number_of_tokens_in_all_liberal_bios = 0

	token_counts = {} # structure: {word_i: {liberal: x, conservative: y}}
	alpha = 1 # pseudocounts: to avoid issues where a token t yields a conditional probability 0, we add alpha to the counts for each token

	start_time2 = time.time()
	print(f"Training on bios from {YEAR_1}...")
	for row in TRAINING_SET:

		bio_y1 = row[YEAR_1-2015].casefold() if row[YEAR_1-2015] else ""
		ideology = row[6]
		if bio_y1 == "" or ideology == 0:
			continue
		
		tokens = tokenize(bio_y1)
		
		if ideology == 1:
			number_of_conservative_bios += 1
			#number_of_tokens_in_all_conservative_bios += len(tokens)
		elif ideology == -1:
			number_of_liberal_bios += 1
			#number_of_tokens_in_all_liberal_bios += len(tokens)

		for t in tokens:
			if t not in token_counts:
				number_of_tokens_in_all_conservative_bios += alpha
				number_of_tokens_in_all_liberal_bios += alpha
				token_counts[t] = {'conservative': alpha, 'liberal': alpha}
			if ideology == 1:
				number_of_tokens_in_all_conservative_bios += 1
				token_counts[t]['conservative'] += 1
			elif ideology == -1:
				number_of_tokens_in_all_liberal_bios += 1
				token_counts[t]['liberal'] += 1

	prior_conservative = number_of_conservative_bios / (number_of_liberal_bios + number_of_conservative_bios)
	prior_liberal = number_of_liberal_bios / (number_of_liberal_bios + number_of_conservative_bios) 

	conditional_probabilities = {t: {'conservative': c['conservative']/number_of_tokens_in_all_conservative_bios, \
									 'liberal': c['liberal']/number_of_tokens_in_all_liberal_bios} for t, c in token_counts.items()}

	if PRINT_CONDITIONAL_PROBS:
		with open('conservative_probabilities.txt', 'wt') as out1, open('liberal_probabilities.txt', 'wt') as out2:
			ordered1 = OrderedDict(sorted(conditional_probabilities.items(), key=lambda x: x[1]['conservative']))
			pprint(ordered1, stream=out1)
			ordered2 = OrderedDict(sorted(conditional_probabilities.items(), key=lambda x: x[1]['liberal']))
			pprint(ordered2, stream=out2)
			#pprint(sorted(conditional_probabilities, key=lambda x: max(conditional_probabilities[x]['conservative'], conditional_probabilities[x]['liberal'])), stream=out)

	print(f"Finished training in {time.time()-start_time2}")

	def test(test_set):
		
		true_conservatives, false_conservatives = 0, 0 # row 1 of confusion matrix
		false_liberals, true_liberals = 0, 0 # row 2 of confusion matrix
		total_correct, total_incorrect = 0, 0

		true_conservatives_already_political, false_conservatives_already_political = 0, 0 # row 1 of confusion matrix
		false_liberals_already_political, true_liberals_already_political = 0, 0 # row 2 of confusion matrix
		total_correct_already_political, total_incorrect_already_political = 0, 0

		true_conservatives_non_political, false_conservatives_non_political = 0, 0 # row 1 of confusion matrix
		false_liberals_non_political, true_liberals_non_political = 0, 0 # row 2 of confusion matrix
		total_correct_non_political, total_incorrect_non_political = 0, 0

		for sample in test_set:
			bio_y1 = sample[YEAR_1-2015].casefold() if sample[YEAR_1-2015] else ""
			bio_y2 = sample[YEAR_2-2015] if sample[YEAR_2-2015] else ""
			actual_class = sample[6]
			if bio_y1 == "" or (actual_class != -1 and actual_class != 1):
				continue

			P_conservative = prior_conservative
			P_liberal = prior_liberal
			tokens = tokenize(bio_y1)

			already_political = any(political_kw in token for token in tokens for political_kw in POLITICAL_KEYWORDS)

			for t in tokens:
				if t not in conditional_probabilities:
					conditional_probabilities[t] = {'conservative': 1/(number_of_tokens_in_all_conservative_bios+1), 'liberal': 1/(number_of_tokens_in_all_liberal_bios+1)}
					if PRINT_EACH_TEST:
						print(f"new token found in testing data: {t}")
				P_conservative *= conditional_probabilities[t]['conservative']
				P_liberal *= conditional_probabilities[t]['liberal']

			if P_conservative > P_liberal:
				prediction = 1
			elif P_liberal > P_conservative:
				prediction = -1

			if prediction == actual_class:
				total_correct += 1
				if already_political:
					total_correct_already_political += 1
				else:
					total_correct_non_political += 1
				if actual_class == 1:
					true_conservatives += 1
					if already_political:
						true_conservatives_already_political += 1
					else:
						true_conservatives_non_political += 1
				elif actual_class == -1:
					true_liberals += 1
					if already_political:
						true_liberals_already_political += 1
					else:
						true_liberals_non_political += 1

			else:
				total_incorrect += 1
				if already_political:
					total_incorrect_already_political += 1
				else:
					total_incorrect_non_political += 1
				if actual_class == 1:
					false_liberals += 1
					if already_political:
						false_liberals_already_political += 1
					else:
						false_liberals_non_political += 1
				elif actual_class == -1:
					false_conservatives += 1
					if already_political:
						false_conservatives_already_political += 1
					else:
						false_conservatives_non_political += 1

			if PRINT_EACH_TEST:
				print(f"{'PASS' if prediction == actual_class else 'FAIL'}\nBio {YEAR_1}: {bio_y1}\nBio {YEAR_2}: {bio_y2}\nPrediction: {'conservative' if prediction==1 else 'liberal'}\nActual: {'conservative' if actual_class==1 else 'liberal'}")
				print('-'*10)
			elif PRINT_WRONG and not (PRINT_POLITICAL or PRINT_NONPOLITICAL):
				print(f"FAIL\nBio {YEAR_1}: {bio_y1}\nBio {YEAR_2}: {bio_y2}\nPrediction: {'conservative' if prediction==1 else 'liberal'}\nActual: {'conservative' if actual_class==1 else 'liberal'}")
			elif PRINT_POLITICAL and already_political:
				if PRINT_WRONG:
					if prediction != actual_class:
						print(f"FAIL\nBio {YEAR_1}: {bio_y1}\nBio {YEAR_2}: {bio_y2}\nPrediction: {'conservative' if prediction==1 else 'liberal'}\nActual: {'conservative' if actual_class==1 else 'liberal'}")
				else:
					print(f"{'PASS' if prediction == actual_class else 'FAIL'}\nBio {YEAR_1}: {bio_y1}\nBio {YEAR_2}: {bio_y2}\nPrediction: {'conservative' if prediction==1 else 'liberal'}\nActual: {'conservative' if actual_class==1 else 'liberal'}")
			elif PRINT_NONPOLITICAL and not already_political:
				if PRINT_WRONG:
					if (prediction != actual_class):
						print(f"FAIL\nBio {YEAR_1}: {bio_y1}\nBio {YEAR_2}: {bio_y2}\nPrediction: {'conservative' if prediction==1 else 'liberal'}\nActual: {'conservative' if actual_class==1 else 'liberal'}")
				else:
					print(f"{'PASS' if prediction == actual_class else 'FAIL'}\nBio {YEAR_1}: {bio_y1}\nBio {YEAR_2}: {bio_y2}\nPrediction: {'conservative' if prediction==1 else 'liberal'}\nActual: {'conservative' if actual_class==1 else 'liberal'}")


		print('=' * 50)
		print_report(YEAR_1, true_conservatives, false_conservatives, true_liberals, false_liberals, total_correct, total_incorrect)
		print('=' * 10)
		print('For bios that were already political: ')
		print_report(YEAR_1, true_conservatives_already_political, false_conservatives_already_political, true_liberals_already_political, false_liberals_already_political, total_correct_already_political, total_incorrect_already_political)
		print('=' * 10)
		print('For bios that were NOT already political: ')
		print_report(YEAR_1, true_conservatives_non_political, false_conservatives_non_political, true_liberals_non_political, false_liberals_non_political, total_correct_non_political, total_incorrect_non_political)
		print('=' * 50)

	start_time3 = time.time()
	print(f"Testing performance using bios from {YEAR_1}...")
	test(TEST_SET)
	print(f"finished testing in {time.time()-start_time3}")

def tokenize(x, keep_pronouns=True, n=1):
	tokens = re.split(REGEX_SEPARATORS, x)
	if not KEEP_DUPLICATES:
		tokens = set(tokens)
	stop_words = set(stopwords.words('english')).union(["com", "http", "https", "www"])
	if keep_pronouns:
		stop_words = [stop_word for stop_word in stop_words if not stop_word in ["he","him","his","she","her","hers","they","them","theirs"]]
	tokens = [token for token in tokens if not token in stop_words]
	if n > 1:
		tokens = [token]
	return tokens

def print_report(year1, true_conservatives, false_conservatives, true_liberals, false_liberals, total_correct, total_incorrect):
	print(f"\nREPORT ({year1}):\n")
	total = total_correct + total_incorrect
	matrix = [
	   [f"n={total}",  "Predicted Conservatives", "Predicted Liberals"],
	   ["Actual Conservatives", f"{true_conservatives}", f"{false_liberals}"],
	   ["Actual Liberals",  f"{false_conservatives}", f"{true_liberals}"]
	]

	s = [[str(e) for e in row] for row in matrix]
	lens = [max(map(len, col)) for col in zip(*s)]
	fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
	table = [fmt.format(*row) for row in s]
	print('\n'.join(table))

	accuracy = 100 * total_correct / total
	print(f"\nACCURACY: {accuracy} % ({total_correct} / {total})\n")

for year in range(2015, 2020):
	train_and_test(YEAR_1=year, YEAR_2=2020)