import nltk
# from nltk.corpus import stopwords
from langdetect import detect
from langdetect import lang_detect_exception
import numpy as np
import random
import string # to process standard python strings
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import key
import tweepy
import time
import unicodedata, re
import emoji
# import os

SLEEPTIME = 60*15
COUNT = 50
NUM_FOLLOWERS = 30
TOTAL_FOLLOWERS = 5000
ALL_DATA = '.\\cachedData\\test.txt'
CURRENT_SET = 'currentSet.txt'
USED_SET = ALL_DATA
RUN_BOT = True
COLLECT_DATA = True

consumer_key = key.consumer_key
consumer_secret = key.consumer_secret
access_token = key.access_token
access_secret = key.access_secret
auth = tweepy.OAuthHandler(consumer_key,consumer_secret)
auth.set_access_token(access_token,access_secret)
api = tweepy.API(auth)


# nltk.download('stopwords')
nltk.download('punkt') # first-time use only
nltk.download('wordnet') # first-time use only
# nltk.download('words')
GREETING_INPUTS = ("hello", "hi", "greetings", "sup", "what's up","hey",)
GREETING_RESPONSES = ["hi", "hey", "*nods*", "hi there", "hello", "I am glad! You are talking to me"]
remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)
# stop = stopwords.words('english') + list(string.punctuation)

def limit_handled(cursor):
    while True:
        try:
            yield cursor.next()
        except tweepy.RateLimitError:
        	print("RATE ERROR 15 Minute Break")
        	time.sleep(SLEEPTIME)
        	continue
        except tweepy.TweepError:
        	print("TWEEP ERROR")
        	break
        except StopIteration:
        	break

def get_follower_tweets():
	count = 0
	with open(ALL_DATA,'a',encoding='utf-8-sig') as f:
		with open(CURRENT_SET,'w',encoding='utf-8-sig') as f2:
			accountvar = 'realDonaldTrump'
			for follower in limit_handled(tweepy.Cursor(api.followers,screen_name=accountvar,count=NUM_FOLLOWERS).items()):
				print(follower.screen_name)
				for status in limit_handled(tweepy.Cursor(api.user_timeline, 
					screen_name=follower.screen_name,count=COUNT,include_rts=True,
					tweet_mode='extended').items()):
					stat = ""
					try:
						if status.retweeted_status:
							stat = status.retweeted_status.full_text
					except:
						stat = status.full_text
					e_str = emoji.emojize(stat)
					filtered_string = re.sub(r"http\S+", "", e_str)
					eng_tweet = re.sub(r"@", "", filtered_string)
					eng_tweet = re.sub(r"#", "", eng_tweet)
					try:
						if len(eng_tweet.split()) > 5:
							if detect(eng_tweet) == 'en':
								f.write(eng_tweet + "\n\n")
								f2.write(eng_tweet + "\n\n")
					except lang_detect_exception.LangDetectException:
						continue
				count += NUM_FOLLOWERS
				if count >= TOTAL_FOLLOWERS:
					break
	# os.startfile('test.htm')

def LemTokens(tokens):
    return [lemmer.lemmatize(token) for token in tokens]
def LemNormalize(text):
    return LemTokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))
def greeting(sentence):
    for word in sentence.split():
        if word.lower() in GREETING_INPUTS:
            return random.choice(GREETING_RESPONSES)

def response(user_response):
    robo_response=''
    sent_tokens.append(user_response)
    TfidfVec = TfidfVectorizer(tokenizer=LemNormalize, stop_words='english')
    tfidf = TfidfVec.fit_transform(sent_tokens)
    vals = cosine_similarity(tfidf[-1], tfidf)
    idx=vals.argsort()[0][-2]
    flat = vals.flatten()
    flat.sort()
    req_tfidf = flat[-2]
    if(req_tfidf==0):
        robo_response=robo_response+"I am sorry! I don't understand you"
        return robo_response
    else:
        robo_response = robo_response+sent_tokens[idx]
        return robo_response


if COLLECT_DATA:
	get_follower_tweets()
f=open(USED_SET,'r',errors = 'ignore')
raw=f.read()
raw=raw.lower()# converts to lowercase
raw = re.sub(r"@", "", raw)
raw = re.sub(r"#", "", raw)
words = set(nltk.corpus.words.words())
raw = " ".join(w for w in nltk.wordpunct_tokenize(raw) \
     if w.lower() in words or not w.isalpha()) 
sent_tokens = nltk.sent_tokenize(raw)# converts to list of sentences 
word_tokens = nltk.word_tokenize(raw)# converts to list of words

lemmer = nltk.stem.WordNetLemmatizer()
#WordNet is a semantically-oriented dictionary of English included in NLTK.

flag=RUN_BOT
print("ROBO: My name is Robo. I will answer your queries about Chatbots. If you want to exit, type Bye!")
while(flag==True):
    user_response = input()
    user_response=user_response.lower()
    if(user_response!='bye'):
        if(user_response=='thanks' or user_response=='thank you' ):
            flag=False
            print("ROBO: You are welcome..")
        else:
            if(greeting(user_response)!=None):
                print("ROBO: "+greeting(user_response))
            else:
                print("ROBO: ",end="")
                print(response(user_response))
                sent_tokens.remove(user_response)
    else:
        flag=False
        print("ROBO: Bye! take care..")
