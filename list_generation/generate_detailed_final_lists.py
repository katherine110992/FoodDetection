from collections import Counter
from datetime import timedelta
from time import time
import csv
import datetime
import food_detection_root
import os
import codecs


def generate_csv_files():
    # Paths
    path = food_detection_root.ROOT_DIR + os.path.sep + 'temporal_files' + os.path.sep
    what_food_path = food_detection_root.ROOT_DIR + os.path.sep + 'data' + os.path.sep
    final_path = food_detection_root.ROOT_DIR + os.path.sep + 'final_files' + os.path.sep
    # Read what words
    what_food_list_file = codecs.open(what_food_path + "list - original_stemmed_what_food.txt", encoding='utf-8')
    what_food_list = what_food_list_file.read().splitlines()
    what_food_list_file.close()
    what_food = {}
    for line in what_food_list:
        data = line.split("\t")
        stem = data[1]
        word = data[0]
        what_food[word] = stem

    """
    # User mentions with food
    user_mentions_with_food_file = open(path + "user_mentions_with_food.txt")
    detailed_user_mentions_with_food_file = open(path + "detailed_user_mentions_with_food.txt", 'a')
    user_mentions_with_food_words = user_mentions_with_food_file.read().splitlines()
    for alias in user_mentions_with_food_words:
        for word in what_food.keys():
            if word in alias:
                detailed_user_mentions_with_food_file.write(alias + '\t' + word + '\n')
                print(alias + '\t' + word)
                break
    user_mentions_with_food_file.close()
    detailed_user_mentions_with_food_file.close()
    detailed_user_mentions_with_food_file = open(path + "detailed_user_mentions_with_food.txt")
    detailed_user_mentions_with_food_words = detailed_user_mentions_with_food_file.read().splitlines()

    detailed_user_mentions_with_food_words_counter = Counter(detailed_user_mentions_with_food_words).most_common()
    detailed_user_mentions_with_food_words_sorted = sorted(detailed_user_mentions_with_food_words_counter,
                                                           key=lambda tup: tup[0])
    # Save into csv
    date = datetime.datetime.today().strftime("%Y_%m_%d-%H_%M_%S")
    with open(final_path + date + " - detailed_user_mentions_with_food.csv", 'w', encoding='utf-8-sig', newline='') as csv_file:
        header = ["alias", "word", "frequency"]
        writer = csv.DictWriter(csv_file, fieldnames=header, delimiter=';', quoting=csv.QUOTE_ALL, doublequote=True)
        writer.writeheader()
        for anagram in detailed_user_mentions_with_food_words_sorted:
            complete = anagram[0].split('\t')
            alias = complete[0]
            word = complete[1]
            row = {
                "alias": alias,
                "word": word,
                "frequency": anagram[1]
            }
            writer.writerow(row)
        csv_file.close()
    """

    # Hashtags with food
    hashtags_with_food_file = open(path + "hashtags_with_food.txt")
    detailed_hashtags_with_food_file = open(path + "detailed_hashtags_with_food.txt", 'a')
    hashtags_with_food_words = hashtags_with_food_file.read().splitlines()
    for hashtag in hashtags_with_food_words:
        for word in what_food.keys():
            if word in hashtag:
                detailed_hashtags_with_food_file.write(hashtag + '\t' + word + '\n')
                print(hashtag + '\t' + word)
                break
    hashtags_with_food_file.close()
    detailed_hashtags_with_food_file.close()
    detailed_hashtags_with_food_file = open(path + "detailed_hashtags_with_food.txt")
    detailed_hashtags_with_food_words = detailed_hashtags_with_food_file.read().splitlines()

    detailed_hashtags_with_food_words_counter = Counter(detailed_hashtags_with_food_words).most_common()
    detailed_hashtags_with_food_words_sorted = sorted(detailed_hashtags_with_food_words_counter,
                                                           key=lambda tup: tup[0])
    # Save into csv
    date = datetime.datetime.today().strftime("%Y_%m_%d-%H_%M_%S")
    with open(final_path + date + " - detailed_hashtags_with_food.csv", 'w', encoding='utf-8-sig',
              newline='') as csv_file:
        header = ["hashtag", "word", "frequency"]
        writer = csv.DictWriter(csv_file, fieldnames=header, delimiter=';', quoting=csv.QUOTE_ALL, doublequote=True)
        writer.writeheader()
        for anagram in detailed_hashtags_with_food_words_sorted:
            complete = anagram[0].split('\t')
            hashtag = complete[0]
            word = complete[1]
            row = {
                "hashtag": hashtag,
                "word": word,
                "frequency": anagram[1]
            }
            writer.writerow(row)
        csv_file.close()

    """
    user_mentions_with_food_file.close()
    execution_time = time() - start_time
    performance_file.write(
        "Write user_mentions_with_food.cvs time: " + str(timedelta(seconds=execution_time)) + "\n")
    performance_file.flush()
    # Open hashtags_about_food file
    hashtags_about_food_file = open(path + "hashtags_about_food.txt")
    hashtags_about_food = hashtags_about_food_file.read().splitlines()
    # Calculate frequencies for hashtags_about_food
    hashtags_about_food_counter = Counter(hashtags_about_food).most_common()
    hashtags_about_food_sorted = sorted(hashtags_about_food_counter, key=lambda tup: tup[0])
    # Save into csv
    date = datetime.datetime.today().strftime("%Y_%m_%d-%H_%M_%S")
    with open(final_path + date + " - hashtags_about_food.csv", 'w', encoding='utf-8-sig', newline='') as csv_file:
        header = ["hashtag", "frequency"]
        writer = csv.DictWriter(csv_file, fieldnames=header, delimiter=';', quoting=csv.QUOTE_ALL, doublequote=True)
        writer.writeheader()
        for anagram in hashtags_about_food_sorted:
            row = {
                "hashtag": anagram[0],
                "frequency": anagram[1]
            }
            writer.writerow(row)
        csv_file.close()
    hashtags_about_food_file.close()
    execution_time = time() - start_time
    performance_file.write("Write hashtags_about_food.cvs time: " + str(timedelta(seconds=execution_time)) + "\n")
    performance_file.flush()
    # Open hashtags_with_food file
    hashtags_with_food_words_file = open(path + "hashtags_with_food.txt")
    hashtags_with_food_words = hashtags_with_food_words_file.read().splitlines()
    # Calculate frequencies for hashtags_with_food
    hashtags_with_food_words_counter = Counter(hashtags_with_food_words).most_common()
    hashtags_with_food_words_sorted = sorted(hashtags_with_food_words_counter, key=lambda tup: tup[0])
    # Save into csv
    date = datetime.datetime.today().strftime("%Y_%m_%d-%H_%M_%S")
    with open(final_path + date + " - hashtags_with_food.csv", 'w', encoding='utf-8-sig', newline='') as csv_file:
        header = ["hashtag", "frequency"]
        writer = csv.DictWriter(csv_file, fieldnames=header, delimiter=';', quoting=csv.QUOTE_ALL, doublequote=True)
        writer.writeheader()
        for anagram in hashtags_with_food_words_sorted:
            row = {
                "hashtag": anagram[0],
                "frequency": anagram[1]
            }
            writer.writerow(row)
        csv_file.close()
    hashtags_with_food_words_file.close()
    execution_time = time() - start_time
    performance_file.write("Write hashtags_with_food.cvs time: " + str(timedelta(seconds=execution_time)) + "\n")
    performance_file.flush()
    # Open what_words file
    what_words_file = open(path + "what_words.txt")
    what_words = what_words_file.read().splitlines()
    # Calculate frequencies for what_words
    what_words_counter = Counter(what_words).most_common()
    what_words_sorted = sorted(what_words_counter, key=lambda tup: tup[0])
    # Save into csv
    date = datetime.datetime.today().strftime("%Y_%m_%d-%H_%M_%S")
    with open(final_path + date + " - what_words.csv", 'w', encoding='utf-8-sig', newline='') as csv_file:
        header = ["word", "frequency"]
        writer = csv.DictWriter(csv_file, fieldnames=header, delimiter=';', quoting=csv.QUOTE_ALL, doublequote=True)
        writer.writeheader()
        for anagram in what_words_sorted:
            row = {
                "word": anagram[0],
                "frequency": anagram[1]
            }
            writer.writerow(row)
        csv_file.close()
    what_words_file.close()
    execution_time = time() - start_time
    performance_file.write("Write what_words.cvs time: " + str(timedelta(seconds=execution_time)) + "\n")
    performance_file.flush()
    # Open new_what_words file
    new_what_words_file = open(path + "new_what_words.txt")
    new_what_words = new_what_words_file.read().splitlines()
    # Save new_what_words csv
    date = datetime.datetime.today().strftime("%Y_%m_%d-%H_%M_%S")
    with open(final_path + date + " - new_what_words.csv", 'w', encoding='utf-8-sig', newline='') as csv_file:
        header = ["stem", "word"]
        writer = csv.DictWriter(csv_file, fieldnames=header, delimiter=';', quoting=csv.QUOTE_ALL, doublequote=True)
        writer.writeheader()
        for aux in new_what_words:
            new = aux.split("\t")
            row = {
                "stem": new[0],
                "word": new[1]
            }
            writer.writerow(row)
        csv_file.close()
    new_what_words_file.close()
    execution_time = time() - start_time
    performance_file.write("Write what_words.cvs time: " + str(timedelta(seconds=execution_time)) + "\n")
    performance_file.flush()
    execution_time = time() - start_time
    performance_file.write("Write text_not_about_food.cvs time: " + str(timedelta(seconds=execution_time)) + "\n")
    performance_file.flush()
    execution_time = time() - start_time
    performance_file.write("Total execution time: " + str(timedelta(seconds=execution_time)) + "\n")
    performance_file.flush()
    performance_file.close()
    """


start_time = time()
generate_csv_files()
