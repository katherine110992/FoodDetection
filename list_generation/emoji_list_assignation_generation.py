import food_detection_root
import os
import codecs
from time import time
import datetime
from datetime import timedelta

start_time = time()
date = datetime.datetime.today().strftime("%Y_%m_%d-%H_%M_%S")
path_to_file = date + " - AssignationEmojisListClassification_Performance.txt"
p_file = open(path_to_file, 'a')
p_file.write(date + " Assignation of Unicode Emoji List Classification - Local Execution" + "\n")
p_file.flush()

path = food_detection_root.ROOT_DIR + os.path.sep + 'data' + os.path.sep
emoji_list_file = codecs.open(path + "list - raw_emojis.txt", encoding='utf-8')
emoji_list = emoji_list_file.read().splitlines()
emoji_list_file.close()
count = 0
p_file.write("Parameters: " + "\n")
people = 7
p_file.write("Total people: " + str(people) + "\n")
person_per_emoji = 3
p_file.write("Emojis per person: " + str(person_per_emoji) + "\n")
unicode_emoji_list_file = codecs.open(path + "list - assignation_of_" + str(people) + "_to_review_" + str(person_per_emoji)
                                      + "_unicode_emojis.txt", encoding='utf-8', mode='a')
person_id = 0
static_person_per_emoji = 3
emoji_per_person = [0] * people
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
            line = emoji_id + ";" + final_unicodes + ";" + emoji + ";" + name + ";"
            assignation = [0] * people
            person_count = 0
            i = person_id
            while i < person_per_emoji and i < len(assignation):
                assignation[i] = 1
                i += 1
                person_count += 1
            person_id += 1
            person_per_emoji += 1
            missing = static_person_per_emoji - person_count
            print(missing)
            if missing >= 1:
                print('Get here')
                j = 0
                while j < len(assignation) and j+1 <= missing:
                    assignation[j] = 1
                    j += 1
            if missing == static_person_per_emoji - 1:
                person_id = 0
                person_per_emoji = static_person_per_emoji
            print(assignation)
            str_assignation = ""
            for i in range(0, len(assignation)):
                str_assignation += str(assignation[i]) + ";"
                emoji_per_person[i] += assignation[i]
            unicode_emoji_list_file.write(line + str_assignation[0:len(str_assignation)-1] + "\n")
            count += 1
p_file.write("Total elements in new list: " + str(count) + "\n")
unicode_emoji_list_file.close()
p_file.write("Statistics per person: \n")
for i in range(0, len(emoji_per_person)):
    p_file.write("Person :" + str(i) + ": " + str(emoji_per_person[i]) + "\n")
execution_time = time() - start_time
p_file.write("Execution time: " + str(timedelta(seconds=execution_time)) + "\n")
p_file.flush()
