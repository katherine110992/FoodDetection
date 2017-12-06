import food_detection_root
import os
import codecs
from time import time
import datetime
from datetime import timedelta

start_time = time()
date = datetime.datetime.today().strftime("%Y_%m_%d-%H_%M_%S")
path_to_file = date + " - ComplementaryCharactersListGeneration_Performance.txt"
p_file = open(path_to_file, 'a')
p_file.write(date + " Complementary Characters List Generation - Local Execution" + "\n")
p_file.flush()

path = food_detection_root.ROOT_DIR + os.path.sep + 'data' + os.path.sep
complementary_characters_list_file = codecs.open(path + "list - raw_complementary_characters.txt", encoding='utf-8')
complementary_characters_list = complementary_characters_list_file.read().splitlines()
complementary_characters_list_file.close()
complementary_characters_list_file = codecs.open(path + "list - complementary_characters.txt", encoding='utf-8', mode='a')
unicode_emoji_list_file = codecs.open(path + "list - unicode_emojis.txt", encoding='utf-8')
emoji_list = unicode_emoji_list_file.read().splitlines()
unicode_emoji_list_file.close()
emojis_dict = {}
for aux in emoji_list:
    aux_emoji = aux.split('\t')
    emojis_dict[aux_emoji[1]] = [aux_emoji[2], aux_emoji[3]]
character_id = 1
emoji_count = 0
for text in complementary_characters_list:
    spaces = text.split("\t")
    if len(spaces) != 1:
        unicode = spaces[0]
        character = spaces[2]
        name = spaces[1]
        special_case = False
        code = unicode[1: len(unicode)]
        code = code.lower()
        if '+1' in code:
            code = code.replace('+', '000')
        else:
            code = code.replace('+', '')
            special_case = True
        code = '\\U' + code
        if special_case:
            code = code.replace('\\U', '\\u')
        if code not in emojis_dict.keys():
            complementary_characters_list_file.write(str(character_id) + "\t" + code + "\t" + character + "\t" + name + "\n")
            character_id += 1
        else:
            emoji_count += 1
complementary_characters_list_file.close()
p_file.write("Total elements in new list: " + str(character_id) + "\n")
p_file.write("Total already elements in new list: " + str(emoji_count) + "\n")
execution_time = time() - start_time
p_file.write("Execution time: " + str(timedelta(seconds=execution_time)) + "\n")
p_file.flush()
