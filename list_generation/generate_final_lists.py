from collections import Counter
from datetime import timedelta
from time import time
import csv
import datetime
import food_detection_root
import os


def generate_csv_files(start_time, performance_file):
    # Create finals CSV
    path = food_detection_root.ROOT_DIR + os.path.sep + 'temporal_files' + os.path.sep
    final_path = food_detection_root.ROOT_DIR + os.path.sep + 'final_files' + os.path.sep
    # Open anagrams file
    anagrams_with_food_words_file = open(path + "anagrams_with_food_words.txt")
    anagrams_with_food_words = anagrams_with_food_words_file.read().splitlines()
    final_anagrams_with_food_words = []
    # Calculate frequencies for anagrams_with_food_words
    for anagram_line in anagrams_with_food_words:
        fields = anagram_line.split("\t")
        if len(fields) > 1:
            final_anagrams_with_food_words.append(fields[2])
    anagrams_with_food_words_counter = Counter(final_anagrams_with_food_words).most_common()
    anagrams_with_food_words_sorted = sorted(anagrams_with_food_words_counter, key=lambda tup: tup[0])
    # Save into csv
    date = datetime.datetime.today().strftime("%Y_%m_%d-%H_%M_%S")
    with open(final_path + date + " - anagrams_with_food_words", 'w', encoding='utf-8-sig', newline='') as csv_file:
        header = ["anagram", "frequency"]
        writer = csv.DictWriter(csv_file, fieldnames=header, delimiter=';', quoting=csv.QUOTE_ALL, doublequote=True)
        writer.writeheader()
        for anagram in anagrams_with_food_words_sorted:
            row = {
                "anagram": anagram[0],
                "frequency": anagram[1]
            }
            writer.writerow(row)
        csv_file.close()
    anagrams_with_food_words_file.close()
    execution_time = time() - start_time
    performance_file.write("Write anagrams_with_food_words.cvs time: " + str(timedelta(seconds=execution_time)) + "\n")
    performance_file.flush()
    # Open user_mentions_about_food file
    user_mentions_about_food_file = open(path + "user_mentions_about_food.txt")
    user_mentions_about_food = user_mentions_about_food_file.read().splitlines()
    # Calculate frequencies for user_mentions_about_food
    user_mentions_about_food_counter = Counter(user_mentions_about_food).most_common()
    user_mentions_about_food_sorted = sorted(user_mentions_about_food_counter, key=lambda tup: tup[0])
    # Save into csv
    date = datetime.datetime.today().strftime("%Y_%m_%d-%H_%M_%S")
    with open(final_path + date + " - user_mentions_about_food", 'w', encoding='utf-8-sig', newline='') as csv_file:
        header = ["alias", "frequency"]
        writer = csv.DictWriter(csv_file, fieldnames=header, delimiter=';', quoting=csv.QUOTE_ALL, doublequote=True)
        writer.writeheader()
        for anagram in user_mentions_about_food_sorted:
            row = {
                "alias": anagram[0],
                "frequency": anagram[1]
            }
            writer.writerow(row)
        csv_file.close()
    user_mentions_about_food_file.close()
    execution_time = time() - start_time
    performance_file.write("Write user_mentions_about_food.cvs time: " + str(timedelta(seconds=execution_time)) + "\n")
    performance_file.flush()
    # Open user_mentions_with_food_words file
    user_mentions_with_food_file = open(path + "user_mentions_with_food_words.txt")
    user_mentions_with_food_words = user_mentions_with_food_file.read().splitlines()
    # Calculate frequencies for user_mentions_with_food_words
    user_mentions_with_food_words_counter = Counter(user_mentions_with_food_words).most_common()
    user_mentions_with_food_words_sorted = sorted(user_mentions_with_food_words_counter, key=lambda tup: tup[0])
    # Save into csv
    date = datetime.datetime.today().strftime("%Y_%m_%d-%H_%M_%S")
    with open(final_path + date + " - user_mentions_with_food_words", 'w', encoding='utf-8-sig', newline='') as csv_file:
        header = ["alias", "frequency"]
        writer = csv.DictWriter(csv_file, fieldnames=header, delimiter=';', quoting=csv.QUOTE_ALL, doublequote=True)
        writer.writeheader()
        for anagram in user_mentions_with_food_words_sorted:
            row = {
                "alias": anagram[0],
                "frequency": anagram[1]
            }
            writer.writerow(row)
        csv_file.close()
    user_mentions_with_food_file.close()
    execution_time = time() - start_time
    performance_file.write(
        "Write user_mentions_with_food_words.cvs time: " + str(timedelta(seconds=execution_time)) + "\n")
    performance_file.flush()
    # Open hashtags_about_food file
    hashtags_about_food_file = open(path + "hashtags_about_food.txt")
    hashtags_about_food = hashtags_about_food_file.read().splitlines()
    # Calculate frequencies for hashtags_about_food
    hashtags_about_food_counter = Counter(hashtags_about_food).most_common()
    hashtags_about_food_sorted = sorted(hashtags_about_food_counter, key=lambda tup: tup[0])
    # Save into csv
    date = datetime.datetime.today().strftime("%Y_%m_%d-%H_%M_%S")
    with open(final_path + date + " - hashtags_about_food", 'w', encoding='utf-8-sig', newline='') as csv_file:
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
    # Open hashtags_with_food_words file
    hashtags_with_food_words_file = open(path + "hashtags_with_food_words.txt")
    hashtags_with_food_words = hashtags_with_food_words_file.read().splitlines()
    # Calculate frequencies for hashtags_with_food_words
    hashtags_with_food_words_counter = Counter(hashtags_with_food_words).most_common()
    hashtags_with_food_words_sorted = sorted(hashtags_with_food_words_counter, key=lambda tup: tup[0])
    # Save into csv
    date = datetime.datetime.today().strftime("%Y_%m_%d-%H_%M_%S")
    with open(final_path + date + " - hashtags_with_food_words", 'w', encoding='utf-8-sig', newline='') as csv_file:
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
    performance_file.write("Write hashtags_with_food_words.cvs time: " + str(timedelta(seconds=execution_time)) + "\n")
    performance_file.flush()
    # Open what_words file
    what_words_file = open(path + "what_words.txt")
    what_words = what_words_file.read().splitlines()
    # Calculate frequencies for what_words
    what_words_counter = Counter(what_words).most_common()
    what_words_sorted = sorted(what_words_counter, key=lambda tup: tup[0])
    # Save into csv
    date = datetime.datetime.today().strftime("%Y_%m_%d-%H_%M_%S")
    with open(final_path + date + " - what_words", 'w', encoding='utf-8-sig', newline='') as csv_file:
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
    execution_time = time() - start_time
    performance_file.write("Write text_not_about_food.cvs time: " + str(timedelta(seconds=execution_time)) + "\n")
    performance_file.flush()
    execution_time = time() - start_time
    performance_file.write("Total execution time: " + str(timedelta(seconds=execution_time)) + "\n")
    performance_file.flush()
    performance_file.close()

start_time = time()
date = datetime.datetime.today().strftime("%Y_%m_%d-%H_%M_%S")
path_to_file = date + " - SeedListGenerator_Performance.txt"
performance_file = open(path_to_file, 'a')
generate_csv_files(start_time, performance_file)
