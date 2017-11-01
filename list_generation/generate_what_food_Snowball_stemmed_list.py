from nltk.stem.snowball import SnowballStemmer
import food_detection_root
import os
import codecs
from time import time
import datetime
from datetime import timedelta

start_time = time()
date = datetime.datetime.today().strftime("%Y_%m_%d-%H_%M_%S")
path_to_file = date + " - StemmedFoodListGeneration_Performance.txt"
p_file = open(path_to_file, 'a')
p_file.write(date + " Snowball Stemmed Food List Generation - Local Execution" + "\n")
p_file.flush()

stemmer = SnowballStemmer(language='spanish')
path = food_detection_root.ROOT_DIR + os.path.sep + 'data' + os.path.sep
what_food_list_file = codecs.open(path + "list - what_food.txt", encoding='utf-8')
what_food_list = what_food_list_file.read().splitlines()
stemmed_list = list()
what_food_list_file.close()
for word in what_food_list:
    stemmed_word = stemmer.stem(word)
    stemmed_list.append(stemmed_word)
what_food_stemmed_list_file = codecs.open(path + "list - stemmed_what_food.txt", encoding='utf-8', mode='a')
count = 0
for word in stemmed_list:
    what_food_stemmed_list_file.write(word + "\n")
    count+= 1
what_food_stemmed_list_file.close()

p_file.write("Total elements in new list: " + str(count) + "\n")
execution_time = time() - start_time
p_file.write("Execution time: " + str(timedelta(seconds=execution_time)) + "\n")
p_file.flush()