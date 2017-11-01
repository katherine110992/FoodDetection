import spacy
from datetime import timedelta, datetime
from time import time

start_time = time()
date = datetime.today().strftime("%Y_%m_%d-%H_%M_%S")
path_to_file = date + " - SpacyTagMap_Performance.txt"
p_file = open(path_to_file, 'a')
p_file.write(date + " spaCy Tag Map Generation - Local Execution" + "\n")
p_file.flush()

nlp = spacy.load('es')

execution_time = time() - start_time
p_file.write("Load Spanish Model Execution time: " + str(timedelta(seconds=execution_time)) + "\n")
p_file.flush()

tag_map = spacy.es.TAG_MAP
print(tag_map)
tags = set()
for tag in tag_map:
    tags.add(tag_map[tag]['pos'])

p_file.write(" Tags: \n")
p_file.flush()

for tag in tags:
    p_file.write(tag + "\n")
    p_file.flush()


execution_time = time() - start_time
p_file.write("Total Execution time: " + str(timedelta(seconds=execution_time)) + "\n")
p_file.flush()