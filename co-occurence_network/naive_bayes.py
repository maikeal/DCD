import os.path
import sqlite3
import re
import sys
import constants
from nltk.corpus import stopwords
from random import randrange
import time

INPUT_DIR, OUTPUT_DIR = constants.INPUT_DIR, constants.OUTPUT_DIR
YEAR_1, YEAR_2 = '2015', '2020'

REGEX_SEPARATORS = r"\s+|[.,\/!$%\^&\*;:{}=\-_`~()|\[\]\u2022]" # currently not including # or @ because of their relevance to Twitter text/functionality

def tokenize(x, keep_duplicates=False, keep_pronouns=True):
	tokens = re.split(REGEX_SEPARATORS, x)
	if not keep_duplicates:
		tokens = set(tokens)
	stop_words = set(stopwords.words('english')).union(["com", "http", "https", "www"])
	if keep_pronouns:
		stop_words = [stop_word for stop_word in stop_words if not stop_word in ["he","him","his","she","her","hers","they","them","theirs"]]
	tokens = [token for token in tokens if not token in stop_words]
	return tokens

conn = sqlite3.connect(f"{INPUT_DIR}bios_2015_2020.sqlite")
cursor = conn.cursor()

number_of_conservative_bios = 0
number_of_liberal_bios = 0
#number_of_political_bios = number_of_liberal_bios + number_of_conservative_bios

number_of_tokens_in_all_conservative_bios = 0
number_of_tokens_in_all_liberal_bios = 0

token_counts = {} # structure: {word_i: {liberal: x, conservative: y}}
alpha = 1 # pseudocounts: to avoid issues where a token t yields a conditional probability 0, we add alpha to the counts for each token
# we'll increment i with each row; 
# when i % 4 == skip, we'll add that row to the testing dataset and skip it so it isn't in the training dataset.
i = 0
skip = randrange(4)
testing_dataset = [] # list of tuples of the form (bio_2015, conservatism)

start_time = time.time()
print("starting training")
cursor.execute("SELECT bio_2015, conservatism FROM political_bios WHERE conservatism != 0")
for row in cursor:

	bio_2015 = row[0].casefold() if row[0] else ""
	conservatism = row[1]
	if bio_2015 == "":
		continue

	i += 1
	if i % 4 == skip:
		testing_dataset.append((bio_2015, conservatism))
		continue
	
	tokens = tokenize(bio_2015, keep_duplicates=True)
	
	if conservatism == 1:
		number_of_conservative_bios += 1
		#number_of_tokens_in_all_conservative_bios += len(tokens)
	elif conservatism == -1:
		number_of_liberal_bios += 1
		#number_of_tokens_in_all_liberal_bios += len(tokens)

	for t in tokens:
		if t not in token_counts:
			number_of_tokens_in_all_conservative_bios += alpha
			number_of_tokens_in_all_liberal_bios += alpha
			token_counts[t] = {'conservative': alpha, 'liberal': alpha}
		if conservatism == 1:
			number_of_tokens_in_all_conservative_bios += 1
			token_counts[t]['conservative'] += 1
		elif conservatism == -1:
			number_of_tokens_in_all_liberal_bios += 1
			token_counts[t]['liberal'] += 1

conditional_probabilities = {t: {'conservative': c['conservative']/number_of_tokens_in_all_conservative_bios, \
								 'liberal': c['liberal']/number_of_tokens_in_all_liberal_bios} for t, c in token_counts.items()}

print(f"finished training in {time.time()-start_time}")

prior_conservative = number_of_conservative_bios / (number_of_liberal_bios + number_of_conservative_bios)
prior_liberal = number_of_liberal_bios / (number_of_liberal_bios + number_of_conservative_bios) 

def test(testing_dataset):
	
	true_conservatives, false_conservatives = 0, 0 # row 1 of confusion matrix
	false_liberals, true_liberals = 0, 0 # row 2 of confusion matrix
	total_correct, total_incorrect = 0, 0
	
	for sample in testing_dataset:
		bio_2015 = sample[0].casefold() if sample[0] else ""
		actual_class = sample[1]
		if bio_2015 == "" or (actual_class != -1 and actual_class != 1):
			continue
		
		P_conservative = prior_conservative
		P_liberal = prior_liberal
		tokens = tokenize(bio_2015, keep_duplicates=True)
		for t in tokens:
			if t not in conditional_probabilities:
				conditional_probabilities[t] = {'conservative': 1/(number_of_tokens_in_all_conservative_bios+1), 'liberal': 1/(number_of_tokens_in_all_liberal_bios+1)}
				print(f"new token found in testing data: {t}")
			P_conservative *= conditional_probabilities[t]['conservative']
			P_liberal *= conditional_probabilities[t]['liberal']

		if P_conservative > P_liberal:
			prediction = 1
		elif P_liberal > P_conservative:
			prediction = -1

		if prediction == actual_class:
			total_correct += 1
			if actual_class == 1:
				true_conservatives += 1
			elif actual_class == -1:
				true_liberals += 1

		else:
			total_incorrect += 1
			if actual_class == 1:
				false_liberals += 1
			elif actual_class == -1:
				false_conservatives += 1

		print(f"\n{'PASS' if prediction == actual_class else 'FAIL'}\nBio: {bio_2015}\nPrediction: {'conservative' if prediction==1 else 'liberal'}\nActual: {'conservative' if actual_class==1 else 'liberal'}\n")
		print('-'*10)

	print('=' * 50)
	print(f"\nREPORT:\nTrue Conservatives: {true_conservatives} | False Conservatives: {false_conservatives}\nFalse Liberals: {false_liberals} | True Liberals: {true_liberals}\nACCURACY: {total_correct*100/(total_correct+total_incorrect)} %")

start_time2 = time.time()
print("starting testing")
test(testing_dataset)
print(f"finished testing in {time.time()-start_time2}")