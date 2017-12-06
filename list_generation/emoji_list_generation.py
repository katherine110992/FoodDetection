import food_detection_root
import os
import codecs
from time import time
import datetime
from datetime import timedelta

start_time = time()
date = datetime.datetime.today().strftime("%Y_%m_%d-%H_%M_%S")
path_to_file = date + " - EmojisUnicodeListGeneration_Performance.txt"
p_file = open(path_to_file, 'a')
p_file.write(date + " Unicode Emoji List Generation - Local Execution" + "\n")
p_file.flush()

path = food_detection_root.ROOT_DIR + os.path.sep + 'data' + os.path.sep
emoji_list_file = codecs.open(path + "list - raw_emojis.txt", encoding='utf-8')
emoji_list = emoji_list_file.read().splitlines()
emoji_list_file.close()
unicode_emoji_list_file = codecs.open(path + "list - unicode_emojis.txt", encoding='utf-8', mode='a')
count = 0
for text in emoji_list:
    spaces = text.split("\t")
    if len(spaces) != 1:
        if 'Code' not in spaces:
            emoji_id = spaces[0]
            unicode = spaces[1]
            emoji = spaces[2]
            name = spaces[14]
            final_unicodes = ""
            codes = unicode.split(" ")
            for code in codes:
                special_case = False
                code = code[1: len(code)]
                code = code.lower()
                if '+1' in code:
                    code = code.replace('+', '000')
                else:
                    code = code.replace('+', '')
                    special_case = True
                code = '\\U' + code
                if special_case:
                    code = code.replace('\\U', '\\u')
                final_unicodes += code
            unicode_emoji_list_file.write(emoji_id + "\t" + final_unicodes + "\t" + emoji + "\t" + name + "\n")
            count += 1
unicode_emoji_list_file.close()

p_file.write("Total elements in new list: " + str(count) + "\n")
execution_time = time() - start_time
p_file.write("Execution time: " + str(timedelta(seconds=execution_time)) + "\n")
p_file.flush()
