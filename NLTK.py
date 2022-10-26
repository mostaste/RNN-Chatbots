import nltk
import numpy as np
import random
import string

f = open('Chatbot.txt','r', errors = 'ignore')
raw = f.read()
raw = raw.lower()
nltk.download('punkt') 
nltk.download('wordnet') 
sent_tokens = nltk.sent_tokenize(raw)
word_tokens = nltk.word_tokenize(raw)

print(sent_tokens[:])
print(word_tokens[:])
