import spacy
import food_detection_root
import os
import codecs
from time import time
import datetime
from datetime import timedelta


start_time = time()
date = datetime.datetime.today().strftime("%Y_%m_%d-%H_%M_%S")
path_to_file = date + " - TaggedFoodListGeneration_Performance.txt"
p_file = open(path_to_file, 'a')
p_file.write(date + " Tagged Food List Generation - Local Execution" + "\n")
p_file.flush()
nlp = spacy.load('es')
path = food_detection_root.ROOT_DIR + os.path.sep + 'data' + os.path.sep
what_food_list_file = codecs.open(path + "list - what_food.txt", encoding='utf-8')
what_food_list = what_food_list_file.read().splitlines()
tagged_what_food = list()
what_food_list_file.close()

for word in what_food_list:
    doc = nlp(word)
    for word in doc:
        tagged_what_food.append([word.text, word.tag_, word.pos_])

tagged_what_food_list_file = codecs.open(path + "list - tagged_what_food.txt", encoding='utf-8', mode='a')
count = 0
for tagged_word in tagged_what_food:
    print(tagged_word)
    tagged_what_food_list_file.write(tagged_word[0] + "\t" + tagged_word[1]
                                     + "\t" + tagged_word[2] + "\n")
    count += 1
tagged_what_food_list_file.close()
p_file.write("Total elements in new list: " + str(count) + "\n")
execution_time = time() - start_time
p_file.write("Execution time: " + str(timedelta(seconds=execution_time)) + "\n")
p_file.flush()