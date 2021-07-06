import os.path
import sqlite3
import re
import sys
import nltk
from nltk.corpus import stopwords
#from nltk.tokenize import TweetTokenizer
#from pprint import pprint
import numpy as np
import matplotlib
#matplotlib.use('TkAgg') 
import matplotlib.pyplot as plt
import networkx as nx
from networkx_viewer import Viewer
from pyvis.network import Network
import math
import constants

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
	G = nx.Graph()
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
			stop_words = set(stopwords.words('english')).union(["com", "http", "https", "www"])
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
						counts_dict[token_i] = 0
					counts_dict[token_i] += 1
					continue
				if token_j not in cooccurrence_dict[token_i]:
					cooccurrence_dict[token_i][token_j] = 1
					G.add_edge(token_i, token_j, weight=1)
				else:
					cooccurrence_dict[token_i][token_j] += 1
					G[token_i][token_j]['weight'] += 0.5

	# Close the connection to the input DB.
	input_conn.close()
	input_cursor = None

	#print("end of func")

	return cooccurrence_dict, counts_dict, G

#pprint(count_cooccurrences())
#with open('output.txt', 'wt') as out:
#	pprint(count_cooccurrences(), stream=out)

cooccurrence_dict, counts_dict, G = count_cooccurrences()

def recordsGenerator():
	#cooccurrence_dict = count_cooccurrences()
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

def threshold(T):
	thresholded_edges = [(u,v, {'weight': w, 'title': int(w)}) for u,v,w in G.edges(data='weight') if w > T]
	G_thresholded = nx.Graph()
	G_thresholded.add_edges_from(thresholded_edges)

	print("Number of nodes: ", G_thresholded.number_of_nodes())
	print("Number of edges: ", G_thresholded.number_of_edges())

	pos = nx.spring_layout(G_thresholded, k=100/np.sqrt(len(G_thresholded.nodes())))
	nx.draw_networkx(G_thresholded, node_color='pink', font_color='black', font_size=8)  # networkx draw()
	ax= plt.gca()
	ax.collections[0].set_edgecolor("#808080")
	plt.draw()  # pyplot draw()
	plt.show()

	nt = Network('600px', '800px')
	nt.from_nx(G_thresholded)
	nt.show_buttons(filter_=['physics', 'layout','selection', 'renderer'])
	nt.show('nxt.html')

def filter_on_token1(INTERESTING_WORDS, T=1, greater_than_median=False):
	G_interesting = nx.Graph()
	
	if greater_than_median:
		weights = []
		for iw in INTERESTING_WORDS:
			if iw not in G.nodes():
				print(iw)
				continue
			for n in G.neighbors(iw):
				if G[iw][n]['weight'] != 1:
					weights.append(G[iw][n]['weight'])
		weights.sort()
		T = weights[int(len(weights)/2)]
		print(T)

	for iw in INTERESTING_WORDS:
		if iw not in G.nodes():
			counts_dict[iw] = -math.inf
			continue
		for n in G.neighbors(iw):
			if G[iw][n]['weight'] > T:
				G_interesting.add_edge(iw, n, weight=G[iw][n]['weight'], title=G[iw][n]['weight'])		

	print("Number of edges: ", G_interesting.number_of_edges())

	pos = nx.spring_layout(G_interesting, k=1/np.sqrt(len(G_interesting.nodes())))
	nx.draw_networkx(G_interesting, node_color='pink', font_color='black', node_size=[ counts_dict[n]-min([abs(counts_dict[iw]) for iw in INTERESTING_WORDS]) / max([counts_dict[iw] for iw in INTERESTING_WORDS]) * 20 + 980 for n in G_interesting.nodes()], font_size=8)  # networkx draw()
	ax= plt.gca()
	ax.collections[0].set_edgecolor("#808080")
	plt.draw()  # pyplot draw()
	plt.show()

	nt = Network('600px', '800px')
	nt.from_nx(G_interesting)
	nt.show_buttons(filter_=['physics', 'layout','selection', 'renderer'])
	nt.show('nx1.html')

def filter_on_both_tokens(INTERESTING_WORDS, T=1, greater_than_median=False, labels_on=False):
	G_interesting = nx.Graph()

	if greater_than_median:
		weights = []
		for i in range(len(INTERESTING_WORDS)):
			if INTERESTING_WORDS[i] not in counts_dict:
				counts_dict[INTERESTING_WORDS[i]] = -math.inf
				continue
			for j in range(i+1, len(INTERESTING_WORDS)):
				if G.has_edge(INTERESTING_WORDS[i], INTERESTING_WORDS[j]):
					weights.append(G[INTERESTING_WORDS[i]][INTERESTING_WORDS[j]]['weight'])
		weights.sort()
		T = weights[int(len(weights)/2)]
		print("median weight: ", T)

	for i in range(len(INTERESTING_WORDS)):
		for j in range(i+1, len(INTERESTING_WORDS)):
			if INTERESTING_WORDS[i] not in counts_dict:
				counts_dict[INTERESTING_WORDS[i]] = -math.inf
				continue
			if G.has_edge(INTERESTING_WORDS[i], INTERESTING_WORDS[j]):
				if G[INTERESTING_WORDS[i]][INTERESTING_WORDS[j]]['weight'] > T:
					G_interesting.add_edge(INTERESTING_WORDS[i], INTERESTING_WORDS[j], weight=G[INTERESTING_WORDS[i]][INTERESTING_WORDS[j]]['weight'], title=G[INTERESTING_WORDS[i]][INTERESTING_WORDS[j]]['weight'])
					#G_interesting.add_edge(INTERESTING_WORDS[i], INTERESTING_WORDS[j], weight=G[INTERESTING_WORDS[i]][INTERESTING_WORDS[j]]['weight'], label=G[INTERESTING_WORDS[i]][INTERESTING_WORDS[j]]['weight'])

	print("Number of edges: ", G_interesting.number_of_edges())

	pos = nx.spring_layout(G_interesting, k=1/np.sqrt(len(G_interesting.nodes())))
	#pos = nx.circular_layout(G_interesting)
	#pos = nx.spectral_layout(G_interesting)
	plt.rcParams["figure.figsize"] = [8, 6]
	nx.draw_networkx(G_interesting, node_color='pink', font_color='black', node_size=[ counts_dict[n]-min([abs(counts_dict[iw]) for iw in INTERESTING_WORDS]) / max([counts_dict[iw] for iw in INTERESTING_WORDS]) * 20 + 980 for n in G_interesting.nodes()], font_size=8)  # networkx draw()
	ax= plt.gca()
	ax.collections[0].set_edgecolor("#808080")
	plt.draw()  # pyplot draw()
	plt.show()

	#nx.write_graphml(G_interesting,'so.graphml')
	
	
	nt = Network('600px', '800px')
	nt.from_nx(G_interesting)
	nt.show_buttons(filter_=['physics', 'layout','selection', 'renderer'])
	nt.show('nx.html')
	


EXPLICIT_POLITICAL = ['socialist', 'communist','marxist','anarchist','leftist','liberal','progressive','democrat','conservative','republican', 'gop', 'libertarian' , 'trump']
IMPLICIT_POLITICAL = ['feminist', 'woke', 'activist', 'deplorable', 'lgbtq', '#blacklivesmatter', '#blm', 'blm', 'backtheblue', 'alllivesmatter', 'maga', '#maga']
PRONOUNS = ['he', 'him', 'she', 'her', 'they', 'them'] #add more later 

FANDOM = ['fan', 'lover', 'fanatic','sports', 'music', 'film', 'movies']
SPORTS_TEAMS = [] #add some of these later
MUSIC_GENRES = [] #add some of these later

RELATIONS = ['mother', 'father', 'mom', 'dad', 'wife', 'husband']

#SEARCH_TERMS = EXPLICIT_POLITICAL + IMPLICIT_POLITICAL + PRONOUNS + FANDOM + RELATIONS
SEARCH_TERMS = EXPLICIT_POLITICAL + IMPLICIT_POLITICAL

#filter_on_both_tokens(['mother', 'father', 'mom', 'dad', 'conservative', 'liberal', 'trump', 'god', 'love', 'dog', 'and'], greater_than_median=True)
#filter_on_both_tokens(SEARCH_TERMS, greater_than_median=True)
filter_on_token1(SEARCH_TERMS, greater_than_median=True)
#threshold(T=15)
