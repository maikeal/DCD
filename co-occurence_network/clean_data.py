import constants
import os.path
import sqlite3
import re
import sys
from nltk import ngrams
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords

INPUT_DIR = constants.INPUT_DIR

REGEX_SEPARATORS = r"\s+|[.,\/!$%\^&\*;:{}=\-_`~()|\[\]\u2022]" # currently not including # or @ because of their relevance to Twitter text/functionality
liberal_pattern = r'(?i)(\w+[.,\/!$%\^&\*;:{}=\-_`~()|\[\]\u2022]|\w+\s+|#){0,3}(?:\s+|[.,\/!$%\^&\*;:{}=\-_`~()|\[\]\u2022])?(liberal|progressive|democrat|socialist|voteblue|blm|blacklivesmatter|black.lives.matter|feminist|free.palestine|feelthebern|biden)(?:\s+|[.,\/!$%\^&\*;:{}=\-_`~()|\[\]\u2022])?(\w+)\b'
conservative_pattern =r'(?i)(\w+)?(?:[\b.,\/!$%\^&\*;:{}=\-_`~()|\[\]\u2022\s]+)?#?(conservative|republican|libertarian|trump|maga|kag|deplorable|backtheblue|bluelivesmatter|alllivesmatter|wwg1wga|qanon|nra|cancel.culture|pro.life)[\b.,\/!$%\^&\*;:{}=\-_`~()|\[\]\u2022\s]?(\w+)?[\.,\/!$%\^&\*;:{}=\-_`~()|\[\]\u2022\s]'

n = 3

KEEP_DUPLICATES = True

# ONLY FOR SEPARATING BY PUNCTATION (not including @ or #) -- NOT BY WHITESPACE. i.e. if you want to tokenize by "sentence," not word
#REGEX_SEPARATE_BY_PUNCTUATION = r"[.,\/!$%\^&\*;:{}=\-_`~()|\[\]\u2022]"

EXPLICIT_LIBERAL_KEYWORDS = ('liberal', 'progressive', 'democrat', 'socialist', 'voteblue')
IMPLICIT_LIBERAL_KEYWORDS = ('blm', 'blacklivesmatter', 'black%lives%matter', 'feminist', 'free%palestine', '%feelthebern%', 'bidenharris', 'biden')
LIBERAL_KEYWORDS = EXPLICIT_LIBERAL_KEYWORDS + IMPLICIT_LIBERAL_KEYWORDS

EXPLICIT_CONSERVATIVE_KEYWORDS = ('conservative', 'republican', 'libertarian')
IMPLICIT_CONSERVATIVE_KEYWORDS = ('trump', 'maga', 'kag', 'deplorable', 'backtheblue', 'bluelivesmatter', 'alllivesmatter', 'wwg1wga', 'qanon', 'nra', 'cancel culture', 'pro%life')
CONSERVATIVE_KEYWORDS = EXPLICIT_CONSERVATIVE_KEYWORDS + IMPLICIT_CONSERVATIVE_KEYWORDS

POLITICAL_KEYWORDS = LIBERAL_KEYWORDS + CONSERVATIVE_KEYWORDS

conservative_token_sentiment_counts = {}
liberal_token_sentiment_counts = {}

users_to_label_as_liberal = []
users_to_label_as_conservative = []

sia = SentimentIntensityAnalyzer()

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

conn = sqlite3.connect(f"{INPUT_DIR}bios_six_year.sqlite")
cursor = conn.cursor()
# First, we'll loop through bios labelled as conservative and count the number of times conservative tokens are found within negative sentimental contexts
cursor.execute("SELECT user_id_str, bio_2020, ideology FROM political_bios WHERE ideology == 1")
data = cursor.fetchall()
for row in data:
	bio = row[1].casefold() if row[0] else ""
	bio_tokens = tokenize(bio)
	ideology = row[2]
	overall_political_sentiment = 0
	#bio_ngrams = ngrams(bio.split(), n)
	bio_trigrams = [(bio_tokens[i], bio_tokens[i+1], bio_tokens[i+2]) for i in range(0, len(bio_tokens)-2)]
	for trigram in bio_trigrams:
		#if any(political_kw in token for token in trigram for political_kw in POLITICAL_KEYWORDS):
		if any(political_kw in token for token in trigram for political_kw in CONSERVATIVE_KEYWORDS):
			sentiment = sia.polarity_scores(' '.join(trigram))
			overall_political_sentiment += sentiment['compound']
	if overall_political_sentiment < 0:
		print(f"Bio: {bio} | Ideology: {ideology}| Compound Sentiment: {sentiment['compound']}")
