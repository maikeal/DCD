import os.path
import sys
import constants
import sqlite3
import time
import numpy as np
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
from sklearn import metrics
from pprint import pprint
from sklearn.neighbors import KNeighborsClassifier

INPUT_DIR, OUTPUT_DIR = constants.INPUT_DIR, constants.OUTPUT_DIR
KEEP_PRONOUNS = True if '-kp' in sys.argv else False
K = 5

BALANCED = '-b' in sys.argv
TABLE_NAME = 'political_bios_balanced' if BALANCED else 'political_bios'

conn = sqlite3.connect(f"{INPUT_DIR}bios_six_year.sqlite")
cursor = conn.cursor()

if BALANCED:
	cursor.execute(""" CREATE TEMP VIEW political_bios_balanced AS 
						SELECT *
						FROM ( SELECT * FROM political_bios WHERE ideology=-1 ORDER BY RANDOM() LIMIT 16064)
						UNION
						SELECT *
						FROM ( SELECT * FROM political_bios WHERE ideology = 1 ORDER BY RANDOM());
					""")

sw = set(stopwords.words('english')).union(["com", "http", "https", "www"])
if KEEP_PRONOUNS:
	sw = [stop_word for stop_word in sw if not stop_word in ["he","him","his","she","her","hers","they","them","theirs"]]

EXPLICIT_LIBERAL_KEYWORDS = ('liberal', 'progressive', 'democrat', 'socialist', 'voteblue')
IMPLICIT_LIBERAL_KEYWORDS = ('blm', 'blacklivesmatter', 'black lives matter', 'feminist', 'free palestine', 'feelthebern', 'bidenharris', 'biden')
LIBERAL_KEYWORDS = EXPLICIT_LIBERAL_KEYWORDS + IMPLICIT_LIBERAL_KEYWORDS

EXPLICIT_CONSERVATIVE_KEYWORDS = ('conservative', 'republican', 'libertarian')
IMPLICIT_CONSERVATIVE_KEYWORDS = ('trump', 'maga', 'deplorable', 'backtheblue', 'bluelivesmatter', 'alllivesmatter', 'wwg1wga', 'qanon', 'nra', 'cancel culture', 'pro life')
CONSERVATIVE_KEYWORDS = EXPLICIT_CONSERVATIVE_KEYWORDS + IMPLICIT_CONSERVATIVE_KEYWORDS

POLITICAL_KEYWORDS = LIBERAL_KEYWORDS + CONSERVATIVE_KEYWORDS

cursor.execute(f"SELECT bio_2015, bio_2016, bio_2017, bio_2018, bio_2019, bio_2020, ideology FROM {TABLE_NAME} WHERE ideology != 0 ORDER BY RANDOM()")

COMPLETE_DATA = cursor.fetchall()
TRAINING_DATA = COMPLETE_DATA[:4*len(COMPLETE_DATA)//5]
TEST_DATA = COMPLETE_DATA[4*len(COMPLETE_DATA)//5:]

accuracy_comparison = {
						2015: {'Naive Bayes': {}, 'Naive Bayes with n-grams': {}, 'Support Vector Machine': {}, f'K-Nearest Neighbors (k={K})': {}}, 
						2016: {'Naive Bayes': {}, 'Naive Bayes with n-grams': {}, 'Support Vector Machine': {}, f'K-Nearest Neighbors (k={K})': {}},
						2017: {'Naive Bayes': {}, 'Naive Bayes with n-grams': {}, 'Support Vector Machine': {}, f'K-Nearest Neighbors (k={K})': {}},
						2018: {'Naive Bayes': {}, 'Naive Bayes with n-grams': {}, 'Support Vector Machine': {}, f'K-Nearest Neighbors (k={K})': {}},
						2019: {'Naive Bayes': {}, 'Naive Bayes with n-grams': {}, 'Support Vector Machine': {}, f'K-Nearest Neighbors (k={K})': {}}
					}

naive_bayes = Pipeline([
    ('vect', CountVectorizer(stop_words=sw)),
    ('tfidf', TfidfTransformer()),
    ('clf', MultinomialNB()),
])

naive_bayes_ngrams = Pipeline([
    ('vect', CountVectorizer(stop_words=sw, ngram_range=(1,5))),
    ('tfidf', TfidfTransformer()),
    ('clf', MultinomialNB()),
])

svm = Pipeline([
    ('vect', CountVectorizer(stop_words=sw)),
    ('tfidf', TfidfTransformer()),
    ('clf', SGDClassifier(loss='hinge', penalty='l2',
                          alpha=1e-3, random_state=42,
                          max_iter=5, tol=None)),
])

knn = Pipeline([
    ('vect', CountVectorizer(stop_words=sw)),
    ('tfidf', TfidfTransformer()),
    ('clf', KNeighborsClassifier(n_neighbors=K)),
])

for i in range(5):

	YEAR = 2015 + i

	TRAINING_CORPUS = [r[i] for r in TRAINING_DATA]
	TRAINING_TARGET = [r[6] for r in TRAINING_DATA]

	TEST_CORPUS = [r[i] for r in TEST_DATA]
	TEST_TARGET = [r[6] for r in TEST_DATA]

	TEST_CORPUS_POLITICAL = [r[i] for r in TEST_DATA if any(political_kw in r[i] for political_kw in POLITICAL_KEYWORDS)]
	TEST_TARGET_POLITICAL =[r[6] for r in TEST_DATA if any(political_kw in r[i] for political_kw in POLITICAL_KEYWORDS)]

	TEST_CORPUS_NON_POLITICAL = [r[i] for r in TEST_DATA if not any(political_kw in r[i] for political_kw in POLITICAL_KEYWORDS)]
	TEST_TARGET_NON_POLITICAL =[r[6] for r in TEST_DATA if not any(political_kw in r[i] for political_kw in POLITICAL_KEYWORDS)]

	for classifer, label in zip( (naive_bayes, naive_bayes_ngrams, svm, knn), ("Naive Bayes", "Naive Bayes with n-grams", "Support Vector Machine", f"K-Nearest Neighbors (k={K})") ):
		print(f"Training {label} on bios from {YEAR}...")
		start_time = time.time()
		classifer.fit(TRAINING_CORPUS, TRAINING_TARGET)
		print(f"Finished training in {time.time()-start_time}")
		
		print(f"OVERALL: ")
		predicted_overall = classifer.predict(TEST_CORPUS)
		accuracy_overall = 100 * np.mean(predicted_overall == TEST_TARGET)
		accuracy_comparison[YEAR][label]['Overall'] = str(accuracy_overall) + '%'
		print(f"Accuracy: {str(accuracy_overall) + '%'}")
		print(metrics.classification_report(TEST_TARGET, predicted_overall, target_names=['liberal', 'conservative']))
		print(metrics.confusion_matrix(y_true=TEST_TARGET, y_pred=predicted_overall))

		print('-'*5)

		print(f"ALREADY POLITICAL: ")
		predicted_political = classifer.predict(TEST_CORPUS_POLITICAL)
		accuracy_political = 100 * np.mean(predicted_political == TEST_TARGET_POLITICAL)
		accuracy_comparison[YEAR][label]['Already Political'] = str(accuracy_political) + '%'
		print(f"Accuracy: {str(accuracy_political) + '%'}")
		print(metrics.classification_report(TEST_TARGET_POLITICAL, predicted_political, target_names=['liberal', 'conservative']))
		print(metrics.confusion_matrix(y_true=TEST_TARGET_POLITICAL, y_pred=predicted_political))
		
		print('-'*5)

		print(f"NON_POLITICAL: ")
		predicted_non_political = classifer.predict(TEST_CORPUS_NON_POLITICAL)
		accuracy_non_political = 100 * np.mean(predicted_non_political == TEST_TARGET_NON_POLITICAL)
		accuracy_comparison[YEAR][label]['Non-Political'] = str(accuracy_non_political) + '%'
		print(f"Accuracy: {str(accuracy_non_political) + '%'}")
		print(metrics.classification_report(TEST_TARGET_NON_POLITICAL, predicted_non_political, target_names=['liberal', 'conservative']))
		print(metrics.confusion_matrix(y_true=TEST_TARGET_NON_POLITICAL, y_pred=predicted_non_political))

		print('-'*10)

	print('=' * 20)

print('~' * 40)
print("ACCURACY REPORT: \n")
pprint(accuracy_comparison)

