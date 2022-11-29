import re
from nltk.corpus import stopwords

EXPLICIT_LIBERAL_KEYWORDS = ('liberal', 'progressive', 'democrat', 'socialist', 'voteblue')
IMPLICIT_LIBERAL_KEYWORDS = ('blm', 'blacklivesmatter', 'black%lives%matter', 'feminist', 'free%palestine', '%feelthebern%', 'bidenharris', 'biden')
LIBERAL_KEYWORDS = EXPLICIT_LIBERAL_KEYWORDS + IMPLICIT_LIBERAL_KEYWORDS

EXPLICIT_CONSERVATIVE_KEYWORDS = ('conservative', 'republican', 'libertarian')
IMPLICIT_CONSERVATIVE_KEYWORDS = ('trump', 'maga', 'kag', 'deplorable', 'backtheblue', 'bluelivesmatter', 'alllivesmatter', 'wwg1wga', 'qanon', 'nra', 'cancel culture', 'pro%life')
CONSERVATIVE_KEYWORDS = EXPLICIT_CONSERVATIVE_KEYWORDS + IMPLICIT_CONSERVATIVE_KEYWORDS

POLITICAL_KEYWORDS = LIBERAL_KEYWORDS + CONSERVATIVE_KEYWORDS

REGEX_SEPARATORS = r"\s+|[.,\/!$%\^&\*;:{}=\-_`~()|\[\]\u2022]" # currently not including # or @ because of their relevance to Twitter text/functionality

KEEP_DUPLICATES = True

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

while(True):
	x,y=0,0
	bio_y1 = input()
	tokens = tokenize(bio_y1)
	already_political = any(political_kw in token for token in tokens for political_kw in POLITICAL_KEYWORDS)
	print(already_political)
	x = x+1 if already_political else x
	y = y+1 if not already_political else y
	print(x,y)