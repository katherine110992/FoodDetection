import food_detection_root
import os
import codecs
from time import time
import datetime
from datetime import timedelta

start_time = time()
date = datetime.datetime.today().strftime("%Y_%m_%d-%H_%M_%S")
path_to_file = date + " - EmoticonListGeneration_Performance.txt"
p_file = open(path_to_file, 'a')
p_file.write(date + " Emoticon List Generation - Local Execution" + "\n")
p_file.flush()

path = food_detection_root.ROOT_DIR + os.path.sep + 'data' + os.path.sep
emoticon_list_file = codecs.open(path + "list - raw_emoticons.txt", encoding='utf-8')
emoticon_list = emoticon_list_file.read().splitlines()
emoticon_list_file.close()
final_emoticon_list_file = codecs.open(path + "list - emoticons.txt", encoding='utf-8', mode='a')
count = 0
i = 0
while i < len(emoticon_list):
    expression = emoticon_list[i].split('\t')[0]
    i += 1
    emoticon_aux = emoticon_list[i].split('\t')
    if len(emoticon_aux) == 1:
        emoticon = emoticon_list[i]
        i += 1
        final_emoticon_list_file.write(emoticon + "\t" + expression + "\n")
    count += 1
final_emoticon_list_file.close()

p_file.write("Total elements in new list: " + str(count) + "\n")
execution_time = time() - start_time
p_file.write("Execution time: " + str(timedelta(seconds=execution_time)) + "\n")
p_file.flush()
