from nltk.stem.snowball import PorterStemmer
import food_detection_root
import os
import codecs

stemmer = PorterStemmer()
path = food_detection_root.ROOT_DIR + os.path.sep + 'data' + os.path.sep
what_food_list_file = codecs.open(path + "list - what_food.txt", encoding='utf-8')
what_food_list = what_food_list_file.read().splitlines()
stemmed_list = list()
what_food_list_file.close()
for word in what_food_list:
    stemmed_word = stemmer.stem(word)
    stemmed_list.append(stemmed_word)
what_food_stemmed_list_file = codecs.open(path + "list - stemmed_what_food.txt", encoding='utf-8', mode='a')
for word in stemmed_list:
    what_food_stemmed_list_file.write(word + "\n")
what_food_stemmed_list_file.close()
