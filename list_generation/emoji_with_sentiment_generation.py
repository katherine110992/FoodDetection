import food_detection_root
import os
import codecs
from time import time
import datetime
from datetime import timedelta

start_time = time()
date = datetime.datetime.today().strftime("%Y_%m_%d-%H_%M_%S")
path_to_file = date + " - EmojiSentimentListGeneration_Performance.txt"
p_file = open(path_to_file, 'a')
p_file.write(date + " Emoji Sentiment List Generation - Local Execution" + "\n")
p_file.flush()

path = food_detection_root.ROOT_DIR + os.path.sep + 'data' + os.path.sep
emoji_sentiment_list_file = codecs.open(path + "list - emoji_sentiment_data.csv", encoding='utf-8')
emoji_sentiment_list = emoji_sentiment_list_file.read().splitlines()
emoji_sentiment_list_file.close()

unicode_emoji_list_file = codecs.open(path + "list - unicode_emojis.txt", encoding='utf-8')
emoji_list = unicode_emoji_list_file.read().splitlines()
unicode_emoji_list_file.close()
aux_emojis_dict = {}
emojis_dict = {}
for aux in emoji_list:
    aux_emoji = aux.split('\t')
    emojis_dict[aux_emoji[2]] = [aux_emoji[0], aux_emoji[1], aux_emoji[3]]
unicode_emoji_list_file.close()
complementary_characters_list_file = codecs.open(path + "list - complementary_characters.txt", encoding='utf-8')
complementary_characters_list = complementary_characters_list_file.read().splitlines()
complementary_characters_list_file.close()
complementary_characters_dict = {}
for aux in complementary_characters_list:
    aux_char = aux.split('\t')
    complementary_characters_dict[aux_char[2]] = [aux_char[0], aux_char[1], aux_char[3]]

final_emoji_sentiment_list_file = codecs.open(path + "list - emojis_sentiment.csv", encoding='utf-8', mode='a')
count = 0
for text in emoji_sentiment_list:
    spaces = text.split(",")
    print(spaces)
    if 'Emoji' not in spaces:
        emoji = spaces[0]
        occurrences = spaces[2]
        position = spaces[3]
        negative = spaces[4]
        neutral = spaces[5]
        positive = spaces[6]
        if emoji in emojis_dict.keys():
            emoji_type = 'Emoji'
            unicode = emojis_dict[emoji][1]
            emoji_id = emojis_dict[emoji][0]
            emoji_name = emojis_dict[emoji][2]
        else:
            if emoji in complementary_characters_dict.keys():
                emoji_type = 'Additional Character'
                unicode = complementary_characters_dict[emoji][1]
                emoji_id = complementary_characters_dict[emoji][0]
                emoji_name = complementary_characters_dict[emoji][2]
            else:
                emoji_type = 'Not identified'
                unicode = ''
                emoji_id = ''
                emoji_name = ''
        final_emoji_sentiment_list_file.write(emoji_id + ";" + emoji + ";" + unicode + ";" + emoji_type
                                              + ";" + occurrences + ";" + position + ";" + negative
                                              + ";" + neutral + ";" + positive
                                              + ";" + emoji_id + ";" + emoji_name + "\n")
        count += 1
unicode_emoji_list_file.close()

p_file.write("Total elements in new list: " + str(count) + "\n")
execution_time = time() - start_time
p_file.write("Execution time: " + str(timedelta(seconds=execution_time)) + "\n")
p_file.flush()
