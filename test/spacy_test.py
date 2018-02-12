import spacy
from datetime import timedelta
from time import time

start_time = time()
nlp = spacy.load('es')
execution_time = time() - start_time
print(str(timedelta(seconds=execution_time)))

start_time = time()

doc = nlp('El mejor buenos días es cuando uno se encuentra dinero en alguna prenda del día.*Se encuentra 10lks en un calcetín.')
clean_text = ''
for word in doc:
    print(word.text, word.tag_, word.pos_)
    clean_text += word.text + ' '
execution_time = time() - start_time
print(str(timedelta(seconds=execution_time)))
print(clean_text)

unaccented_text = 'El mejor buenos dias es cuando uno se encuentra dinero en alguna prenda del dia.*Se encuentra 10lks en un calcetin .'
terms = {}
doc = nlp(unaccented_text)
for entity in doc:
    print(entity)
