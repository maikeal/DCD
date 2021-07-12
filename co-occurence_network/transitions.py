import os.path
import sqlite3
import re
import sys
import constants
#import nltk
from nltk.corpus import stopwords
from pprint import pprint
import networkx as nx
#from pyvis.network import Network

INPUT_DIR, OUTPUT_DIR = constants.INPUT_DIR, constants.OUTPUT_DIR
YEAR_1, YEAR_2 = '2015', '2020'

REGEX_SEPARATORS = r"\s+|[.,\/!$%\^&\*;:{}=\-_`~()|\[\]\u2022]" # currently not including # or @ because of their relevance to Twitter text/functionality

TRUMP_KEYWORDS = ['trump', 'maga']
BLM_KEYWORDS = ['blm', 'blacklivesmatter', 'black%%lives matter']


def count_transitions(include_pronouns=True):
	
	trump_counts = {'__total__': 0}
	blm_counts = {'__total__': 0}

	trump_graph = nx.DiGraph()
	blm_graph = nx.DiGraph() 

	conn = sqlite3.connect(f"{INPUT_DIR}bios_{YEAR_1}_{YEAR_2}.sqlite")
	cursor = conn.cursor()

	cursor.execute("""SELECT bio_2015, bio_2020 FROM trump""")
	for row in cursor:
		trump_counts['__total__'] += 1
		bio_2015 = row[0].casefold() if row[0] else ""
		bio_2020 = row[1].casefold() if row[1] else ""

		if "" in [bio_2015, bio_2020]:
			continue

		tokens_2015 = set(re.split(REGEX_SEPARATORS, bio_2015))
		stop_words = set(stopwords.words('english')).union(["com", "http", "https", "www"])
		if include_pronouns:
			stop_words = [stop_word for stop_word in stop_words if not stop_word in ["he","him","his","she","her","hers","they","them","theirs"]]
		tokens_2015 = [token for token in tokens_2015 if not token in stop_words]

		keywords_present_2020 = [kw for kw in TRUMP_KEYWORDS if kw in bio_2020]
		if len(keywords_present_2020) == 0:
			continue
		for token in tokens_2015:
			if token == "":
				continue
			if token not in trump_counts:
				trump_counts[token] = {'__count__': 0}
			trump_counts[token]['__count__'] += 1
			for kw in keywords_present_2020:
				if kw not in trump_counts[token]:
					trump_counts[token][kw] = 0
					trump_graph.add_edge(token, kw, weight=0)
				trump_counts[token][kw] += 1
				trump_graph[token][kw]['weight'] += 1


	cursor.execute("""SELECT bio_2015, bio_2020 FROM blm""")
	for row in cursor:
		blm_counts['__total__'] += 1
		bio_2015 = row[0].casefold() if row[0] else ""
		bio_2020 = row[1].casefold() if row[1] else ""

		if "" in [bio_2015, bio_2020]:
			continue

		tokens_2015 = set(re.split(REGEX_SEPARATORS, bio_2015))
		stop_words = set(stopwords.words('english')).union(["com", "http", "https", "www"])
		if include_pronouns:
			stop_words = [stop_word for stop_word in stop_words if not stop_word in ["he","him","his","she","her","hers","they","them","theirs"]]
		tokens_2015 = [token for token in tokens_2015 if not token in stop_words]

		keywords_present_2020 = [kw for kw in BLM_KEYWORDS if kw in bio_2020]
		if len(keywords_present_2020) == 0:
			continue
		for token in tokens_2015:
			if token == "":
				continue
			if token not in blm_counts:
				blm_counts[token] = {'__count__': 0}
			blm_counts[token]['__count__'] += 1
			for kw in keywords_present_2020:
				if kw not in blm_counts[token]:
					blm_counts[token][kw] = 0
					blm_graph.add_edge(token, kw, weight=0)
				blm_counts[token][kw] += 1
				blm_graph[token][kw]['weight'] += 1


	conn.close()
	cursor = None

	#nx.write_graphml(trump_graph,'trump.graphml')
	#nx.write_graphml(blm_graph, 'blm.graphml')

	return trump_counts, blm_counts
	#return trump_graph, blm_graph

'''
trump_graph, blm_graph = count_transitions()
print(f"trump_graph: {trump_graph.number_of_nodes()} nodes, {trump_graph.number_of_edges()} edges")
print(f"blm_graph: {blm_graph.number_of_nodes()} nodes, {blm_graph.number_of_edges()} edges")
'''

'''
with open('trump.txt', 'w') as trump_output, open('blm.txt', 'w') as blm_output:
	trump_dict, blm_dict = count_transitions()
	pprint(trump_dict, stream=trump_output)
	pprint(blm_dict, stream=blm_output)
'''

def prob_token_x_in_2015_given_trump_in_2020(token_x, trump_counts, kw_data=False):
	if token_x not in trump_counts:
		return 0
	if kw_data:
		return {kw: trump_counts[token_x][kw] / trump_counts['__total__'] for kw in trump_counts[token_x]}
	return trump_counts[token_x]['__count__'] / trump_counts['__total__']

def prob_token_x_in_2015_given_blm_in_2020(token_x, blm_counts, kw_data=False):
	if token_x not in blm_counts:
		return 0
	if kw_data:
		return {kw: blm_counts[token_x][kw] / blm_counts['__total__'] for kw in blm_counts[token_x]}
	return blm_counts[token_x]['__count__'] / blm_counts['__total__']

def prob_trump_in_2020_given_token_x_in_2015(token_x, trump_counts, kw_data=False):
	
	if token_x not in trump_counts:
		return 0

	# get number of 2015 bios which include token_x
	conn = sqlite3.connect(f"{INPUT_DIR}bios_{YEAR_1}_{YEAR_2}.sqlite")
	cursor = conn.cursor()
	cursor.execute(f"""SELECT COUNT(*) FROM all_common_users WHERE bio_2015 LIKE '%{token_x}%';""")
	
	token_x_count = cursor.fetchone()[0]
	
	conn.close()
	cursor = None

	if token_x_count == 0:
		return 0

	if kw_data:
		return {kw: trump_counts[token_x][kw] / token_x_count for kw in trump_counts[token_x]}
	return trump_counts[token_x]['__count__'] / token_x_count

def prob_blm_in_2020_given_token_x_in_2015(token_x, blm_counts, kw_data=False):
	
	if token_x not in blm_counts:
		return 0

	# get number of 2015 bios which include token_x
	conn = sqlite3.connect(f"{INPUT_DIR}bios_{YEAR_1}_{YEAR_2}.sqlite")
	cursor = conn.cursor()
	cursor.execute(f"""SELECT COUNT(*) FROM all_common_users WHERE bio_2015 LIKE '%{token_x}%';""")
	
	token_x_count = cursor.fetchone()[0]
	
	conn.close()
	cursor = None

	if token_x_count == 0:
		return 0

	if kw_data:
		return {kw: blm_counts[token_x][kw] / token_x_count for kw in blm_counts[token_x]}
	return blm_counts[token_x]['__count__'] / token_x_count



trump_dict, blm_dict = count_transitions()

p1_trump_output_template = "{0} % of users who included 'trump' or 'maga' in their bio in 2020 had '{1}' in their bio in 2015."
p2_trump_output_template = "{0} % of users who included '{1}' in their bio in 2015 had 'trump' or 'maga' in their bio in 2020."

p1_blm_output_template = "{0} % of users who included 'black lives matter', 'blacklivesmatter', or 'blm' in their bio in 2020 had '{1}' in their bio in 2015."
p2_blm_output_template = "{0} % of users who included '{1}' in their bio in 2015 had 'black lives matter', 'blacklivesmatter', or 'blm' in their bio in 2020."

while(True):
	token = input("Enter a token: ")

	print("-"*20)

	result1 = prob_token_x_in_2015_given_trump_in_2020(token, trump_dict) * 100
	print(p1_trump_output_template.format(result1, token))

	print("-"*20)
	
	result2 = prob_trump_in_2020_given_token_x_in_2015(token, trump_dict) * 100
	print(p2_trump_output_template.format(result2, token))

	print("-"*40)

	result3 = prob_token_x_in_2015_given_blm_in_2020(token, blm_dict) * 100
	print(p1_blm_output_template.format(result3, token))

	print("-"*20)

	result4 = prob_blm_in_2020_given_token_x_in_2015(token, blm_dict) * 100
	print(p2_blm_output_template.format(result4, token))

	print("-"*60)

'''
p1_trump_output_template = "{0} % of users who included 'trump' or 'maga' in their bio in 2020 had '{1}' in their bio in 2015."
p2_trump_output_template = "{0} % of users who included '{1}' in their bio in 2015 had 'trump' or 'maga' in their bio in 2020."
#trump_token_queries = ['christian', 'god', 'father', 'conservative']
trump_token_queries = ['trump', 'maga']
for token in trump_token_queries:

	print("-"*20)

	result1 = prob_token_x_in_2015_given_trump_in_2020(token, trump_dict) * 100
	print(p1_trump_output_template.format(result1, token))

	print("-"*20)
	
	result2 = prob_trump_in_2020_given_token_x_in_2015(token, trump_dict) * 100
	print(p2_trump_output_template.format(result2, token))

	print("-"*20)

print('+' * 40)

p1_blm_output_template = "{0} % of users who included 'black lives matter', 'blacklivesmatter', or 'blm' in their bio in 2020 had '{1}' in their bio in 2015."
p2_blm_output_template = "{0} % of users who included '{1}' in their bio in 2015 had 'black lives matter', 'blacklivesmatter', or 'blm' in their bio in 2020."
blm_token_queries = ['democrat', 'progressive', 'writer', 'blm']
for token in blm_token_queries:

	print("-"*20)

	result1 = prob_token_x_in_2015_given_blm_in_2020(token, blm_dict) * 100
	print(p1_blm_output_template.format(result1, token))

	print("-"*20)

	result2 = prob_blm_in_2020_given_token_x_in_2015(token, blm_dict) * 100
	print(p2_blm_output_template.format(result2, token))
'''
'''
pprint(prob_token_x_in_2015_given_trump_in_2020('christian', trump_dict, kw_data=True))
pprint(prob_token_x_in_2015_given_trump_in_2020('god', trump_dict, kw_data=True))
pprint(prob_token_x_in_2015_given_trump_in_2020('father', trump_dict, kw_data=True))
pprint(prob_token_x_in_2015_given_trump_in_2020('conservative', trump_dict, kw_data=True))

print('-' * 20)

pprint(prob_token_x_in_2015_given_blm_in_2020('democrat', blm_dict, kw_data=True))
pprint(prob_token_x_in_2015_given_blm_in_2020('progressive', blm_dict, kw_data=True))
pprint(prob_token_x_in_2015_given_blm_in_2020('writer', blm_dict, kw_data=True))
pprint(prob_token_x_in_2015_given_blm_in_2020('blm', blm_dict, kw_data=True))

print('+' * 20)

pprint(prob_trump_in_2020_given_token_x_in_2015('christian', trump_dict, kw_data=True))
pprint(prob_trump_in_2020_given_token_x_in_2015('god', trump_dict, kw_data=True))
pprint(prob_trump_in_2020_given_token_x_in_2015('father', trump_dict, kw_data=True))
pprint(prob_trump_in_2020_given_token_x_in_2015('conservative', trump_dict, kw_data=True))

print('-' * 20)

pprint(prob_token_x_in_2015_given_blm_in_2020('democrat', blm_dict, kw_data=True))
pprint(prob_token_x_in_2015_given_blm_in_2020('progressive', blm_dict, kw_data=True))
pprint(prob_token_x_in_2015_given_blm_in_2020('writer', blm_dict, kw_data=True))
pprint(prob_token_x_in_2015_given_blm_in_2020('blm', blm_dict, kw_data=True))

print('*' * 20)

pprint(trump_dict['christian'])
'''