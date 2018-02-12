import food_detection_root
import os
import codecs
from time import time
import datetime
from datetime import timedelta

start_time = time()
date = datetime.datetime.today().strftime("%Y_%m_%d-%H_%M_%S")
path_to_file = date + " - EmojiWithMetadataListGeneration_Performance.txt"
p_file = open(path_to_file, 'a')
p_file.write(date + " Emoji with Metadata List Generation - Local Execution" + "\n")
p_file.flush()

path = food_detection_root.ROOT_DIR + os.path.sep + 'data' + os.path.sep
emoji_sentiment_list_file = codecs.open(path + "list - emoji_consolidado.txt", encoding='utf-8')
emoji_consolidado_list = emoji_sentiment_list_file.read().splitlines()
emoji_sentiment_list_file.close()

unicode_emoji_list_file = codecs.open(path + "list - unicode_emojis.txt", encoding='utf-8')
emoji_list = unicode_emoji_list_file.read().splitlines()
unicode_emoji_list_file.close()
aux_emojis_dict = {}
emojis_dict = {}
for aux in emoji_list:
    aux_emoji = aux.split('\t')
    emojis_dict[aux_emoji[0]] = {
        'unicode': aux_emoji[1],
        'emoji': aux_emoji[2],
        'description': aux_emoji[3]
    }
unicode_emoji_list_file.close()

final_emoji_metadata_list_file = codecs.open(path + "list - unicode_emojis_metadata.txt", encoding='utf-8', mode='a')
count = 0
final_emoji_metadata_list_file.write("id\tunicode\temoji\tdescription\tpolarity\thappiness\tanger\tfear\trepulsion\t"
                                     "surprise\tsadness\tinterest\n")
for text in emoji_consolidado_list:
    spaces = text.split("\t")
    print(spaces)
    if 'Id' not in spaces:
        emoji_id = spaces[0]
        polarity = spaces[1].replace(',', '.')
        happiness = spaces[2].replace(',', '.')
        anger = spaces[3].replace(',', '.')
        fear = spaces[4].replace(',', '.')
        repulsion = spaces[5].replace(',', '.')
        surprise = spaces[6].replace(',', '.')
        sadness = spaces[7].replace(',', '.')
        interest = spaces[8]
        unicode = emojis_dict[emoji_id]['unicode']
        emoji = emojis_dict[emoji_id]['emoji']
        description = emojis_dict[emoji_id]['description']
        final_emoji_metadata_list_file.write(str(emoji_id) + "\t" + unicode + "\t" + emoji + "\t" + description
                                             + "\t" + polarity + "\t" + happiness + "\t" + anger + "\t" + fear
                                             + "\t" + repulsion + "\t" + surprise + "\t" + sadness + "\t" + interest
                                             + "\n")
        count += 1
final_emoji_metadata_list_file.close()

p_file.write("Total elements in new list: " + str(count) + "\n")
execution_time = time() - start_time
p_file.write("Execution time: " + str(timedelta(seconds=execution_time)) + "\n")
p_file.flush()
