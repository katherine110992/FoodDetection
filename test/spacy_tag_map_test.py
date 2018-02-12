from datetime import timedelta, datetime
from time import time
import spacy.lang.es.tag_map
from spacy.lang.es import Spanish

start_time = time()
date = datetime.today().strftime("%Y_%m_%d-%H_%M_%S")
path_to_file = date + " - SpacyTagMap_Performance.txt"
p_file = open(path_to_file, 'a')
p_file.write(date + " spaCy Tag Map Generation - Local Execution" + "\n")
p_file.flush()

nlp = spacy.load('es')

text = 'este es un texto de prueba 100% & al 100 también prueba'
doc = nlp(text)

for token in doc:
    print(token.text, token.lemma_, token.pos, token.pos_, token.tag_, token.dep_,
          token.shape_, token.is_alpha, token.is_stop, token.sentiment)


execution_time = time() - start_time
p_file.write("Load Spanish Model Execution time: " + str(timedelta(seconds=execution_time)) + "\n")
p_file.flush()

tag_map = spacy.lang.es.TAG_MAP
print(tag_map)

execution_time = time() - start_time
p_file.write("Total Execution time: " + str(timedelta(seconds=execution_time)) + "\n")
p_file.flush()