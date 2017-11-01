# import nltk

# nltk.download('averaged_perceptron_tagger')

from datetime import timedelta
from time import time
from textblob import TextBlob

start_time = time()
blob = TextBlob("cuanto le pago la alcaldia de @ficogutierrez al fan de pablo escobar que vino, dizque nos insulto y vendio?")
print('Lenguaje detectado: ' + blob.detect_language())
print ('Word    |   POS')
print('=================')
for word, pos in blob.tags:
    print (word + " |   "+pos)

execution_time = time() - start_time
print(str(timedelta(seconds=execution_time)))
print()