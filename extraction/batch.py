import calendar
import copy
import csv
import datetime
import os
from collections import Counter
from datetime import timedelta
from time import time

from food_detector.food_detector_thread import FoodDetectorThread

import food_detection_root
from dao_semi_structured_data_access.semi_structured_data_access import SemiStructuredDataAccess


def detect_food_in_batch():
    start_time = time()
    date = datetime.datetime.today().strftime("%Y_%m_%d-%H_%M_%S")
    path_to_file = date + " - FoodDetection_Performance.txt"
    p_file = open(path_to_file, 'a')
    p_file.write(date + " Food Detection - Local Execution" + "\n")
    p_file.flush()
    # 2. Create SemiStructuredAccess
    process_name = "FoodDetection"
    semi_structured_access = SemiStructuredDataAccess(process_name, ["database"])
    path = food_detection_root.ROOT_DIR + os.path.sep + 'temporal_files' + os.path.sep
    anagrams_with_food_words_file = open(path + "anagrams_with_food_words.txt", 'a')
    user_mentions_about_food_file = open(path + "user_mentions_about_food.txt", 'a')
    user_mentions_with_food_words_file = open(path + "user_mentions_with_food_words.txt", 'a')
    hashtags_about_food_file = open(path + "hashtags_about_food.txt", 'a')
    hashtags_with_food_words_file = open(path + "hashtags_with_food_words.txt", 'a')
    what_words_file = open(path + "what_words.txt", 'a')
    text_about_food_file = open(path + "text_about_food.txt", 'a')
    text_not_about_food_file = open(path + "text_not_about_food.txt", 'a')
    years = [2016, 2017]
    int_months = [8, 9]
    char_months = ["Aug", "Sep"]
    # Process each month from each year
    for year in years:
        month_index = 0
        month_execution_time = 0
        p_file.write("------------------------  YEAR " + str(year) + "  ------------------------\n")
        p_file.flush()
        for month in int_months:
            days = calendar.monthrange(year, month)[1]
            start_day = 1
            raw_data_month = char_months[month_index]
            p_file.write("------------------------  MONTH " + raw_data_month + "  ------------------------\n")
            p_file.flush()
            p_file.write("Processing " + str(days) + " days from month " + raw_data_month
                                   + " starting with the " + str(start_day) + "th day\n")
            p_file.flush()
            for day in range(start_day, days + 1):
                day_start_time = time()
                if day in range(1, 10):
                    date_expression = raw_data_month + " 0" + str(day) + ".* " + str(year)
                else:
                    date_expression = raw_data_month + " " + str(day) + ".* " + str(year)
                p_file.write("Processing day: " + date_expression + "\n")
                p_file.flush()
                semi_structured_access.clear_data_from_database("raw_data_per_date", "all", None)
                raw_data = semi_structured_access.get_from_database("raw_data", "all_by_date_expression",
                                                                    [date_expression])
                for data in raw_data:
                    # Save in auxiliary collection
                    semi_structured_access.insert_into_database("raw_data_per_date", data)
                raw_data.close()
                day_results = generate_food_detector_threads(semi_structured_access, p_file)
                p_file.write("Saving results for DAY" + "\n")
                p_file.flush()
                aux_anagrams_with_food_words = copy.deepcopy(day_results[0])
                for word in aux_anagrams_with_food_words:
                    anagrams_with_food_words_file.write(word + "\n")
                    anagrams_with_food_words_file.flush()
                aux_user_mentions_about_food = copy.deepcopy(day_results[1])
                for word in aux_user_mentions_about_food:
                    user_mentions_about_food_file.write(word + "\n")
                    user_mentions_about_food_file.flush()
                aux_user_mentions_with_food_words = copy.deepcopy(day_results[2])
                for word in aux_user_mentions_with_food_words:
                    user_mentions_with_food_words_file.write(word + "\n")
                    user_mentions_with_food_words_file.flush()
                aux_hashtags_about_food = copy.deepcopy(day_results[3])
                for word in aux_hashtags_about_food:
                    hashtags_about_food_file.write(word + "\n")
                    hashtags_about_food_file.flush()
                aux_hashtags_with_food_words = copy.deepcopy(day_results[4])
                for word in aux_hashtags_with_food_words:
                    hashtags_with_food_words_file.write(word + "\n")
                    hashtags_with_food_words_file.flush()
                aux_what_words = copy.deepcopy(day_results[5])
                for word in aux_what_words:
                    what_words_file.write(word + "\n")
                    what_words_file.flush()
                aux_text_about_food = copy.deepcopy(day_results[6])
                for word in aux_text_about_food:
                    text_about_food_file.write(word + "\n")
                    text_about_food_file.flush()
                aux_text_not_about_food = copy.deepcopy(day_results[7])
                for word in aux_text_not_about_food:
                    text_not_about_food_file.write(word + "\n")
                    text_not_about_food_file.flush()
                day_execution_time = time() - day_start_time
                p_file.write("Saving results for DAY " + date_expression + ". Execution time "
                                       + str(timedelta(seconds=day_execution_time)) + "\n")
                p_file.flush()
                day_execution_time = time() - day_start_time
                month_execution_time += day_execution_time
                p_file.write("DAY " + date_expression + " processed successfully. Execution time "
                                    + str(timedelta(seconds=day_execution_time)) + "\n")
                p_file.flush()
            month_index += 1
            p_file.write("From " + str(start_day) + " to " + str(days) + " in month " + raw_data_month
                                   + " have been processed successfully.\n")
            p_file.flush()
    # Close database connection
    semi_structured_access.close_database_connection(process_name)
    generate_csv_files(start_time, p_file)


def generate_food_detector_threads(semi_structured_access, p_file):
    # 3. Initialize accumulation variables
    anagrams_with_food_words = []
    user_mentions_about_food = []
    user_mentions_with_food_words = []
    hashtags_about_food = []
    hashtags_with_food_words = []
    what_words = []
    text_about_food = []
    text_not_about_food = []
    # 3. Get all raw data per date
    raw_data = semi_structured_access.get_from_database("raw_data_per_date", "all", None)
    total_raw_data = raw_data.count()
    p_file.write("Total raw data per date: " + str(total_raw_data) + "\n")
    p_file.flush()
    # 4. Calculate thread numbers
    thread_number = 15
    if total_raw_data != 0:
        fill_number = int(total_raw_data / thread_number)
        threads_number = int(total_raw_data / fill_number)
    else:
        fill_number = 0
        threads_number = 0
    # 5. Create threads names
    raw_data_count_start = 0
    raw_data_count_end = fill_number
    filling_counter = 2
    threads_names = []
    threads_raw_data_range = []
    aux_count_name = 0
    for aux_count_name in range(0, threads_number):
        threads_names.append("Thread_" + str(aux_count_name))
        if raw_data_count_end == total_raw_data:
            raw_data_count_end -= 1
        threads_raw_data_range.append((raw_data_count_start, raw_data_count_end))
        raw_data_count_start = raw_data_count_end + 1
        raw_data_count_end = fill_number * filling_counter
        filling_counter += 1
    if raw_data_count_end - fill_number < total_raw_data:
        threads_names.append("Thread_" + str(aux_count_name + 1))
        threads_raw_data_range.append((raw_data_count_start, total_raw_data - 1))
        threads_number += 1
    # 7. Initialize threads
    # Performance file -- Delete
    p_file.write("Total threads: " + str(threads_number) + "\n")
    p_file.flush()
    p_file.write("Raw data per thread: " + str(fill_number) + "\n")
    p_file.flush()
    # Performance file -- Delete
    raw_data_threads = []
    t_range_count = threads_number - 1
    for i in range(0, threads_number):
        t_name = threads_names[i]
        t_range = threads_raw_data_range[t_range_count]
        thread = FoodDetectorThread(i, t_name, raw_data, t_range, p_file)
        # 8. Start thread
        thread.start()
        raw_data_threads.append(thread)
        t_range_count -= 1
    # Wait to thread end
    for thread in raw_data_threads:
        thread.join()
    raw_data.close()
    p_file.write("Accumulating values\n")
    p_file.flush()
    for thread in raw_data_threads:
        anagrams_with_food_words += thread.anagrams_with_food_words
        user_mentions_about_food += thread.user_mentions_about_food
        user_mentions_with_food_words += thread.user_mentions_with_food_words
        hashtags_about_food += thread.hashtags_about_food
        hashtags_with_food_words += thread.hashtags_with_food_words
        what_words += thread.what_words
        text_about_food += thread.text_about_food
        text_not_about_food += thread.text_not_about_food
    results = [anagrams_with_food_words, user_mentions_about_food, user_mentions_with_food_words,
               hashtags_about_food, hashtags_with_food_words, what_words, text_about_food,
               text_not_about_food]
    return results


def generate_csv_files(start_time, performance_file):
    # Create finals CSV
    # Open anagrams file
    anagrams_with_food_words_file = open("anagrams_with_food_words.txt")
    anagrams_with_food_words = anagrams_with_food_words_file.read().splitlines()
    final_anagrams_with_food_words = []
    # Calculate frequencies for anagrams_with_food_words
    for anagram_line in anagrams_with_food_words:
        fields = anagram_line.split("\t")
        final_anagrams_with_food_words.append(fields[2])
    anagrams_with_food_words_counter = Counter(final_anagrams_with_food_words).most_common()
    anagrams_with_food_words_sorted = sorted(anagrams_with_food_words_counter, key=lambda tup: tup[0])
    # Save into csv
    date = datetime.datetime.today().strftime("%Y_%m_%d-%H_%M_%S")
    with open(date + " - anagrams_with_food_words", 'w', encoding='utf-8-sig', newline='') as csv_file:
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
    user_mentions_about_food_file = open("user_mentions_about_food.txt")
    user_mentions_about_food = user_mentions_about_food_file.read().splitlines()
    # Calculate frequencies for user_mentions_about_food
    user_mentions_about_food_counter = Counter(user_mentions_about_food).most_common()
    user_mentions_about_food_sorted = sorted(user_mentions_about_food_counter, key=lambda tup: tup[0])
    # Save into csv
    date = datetime.datetime.today().strftime("%Y_%m_%d-%H_%M_%S")
    with open(date + " - user_mentions_about_food", 'w', encoding='utf-8-sig', newline='') as csv_file:
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
    user_mentions_with_food_file = open("user_mentions_with_food_words.txt")
    user_mentions_with_food_words = user_mentions_with_food_file.read().splitlines()
    # Calculate frequencies for user_mentions_with_food_words
    user_mentions_with_food_words_counter = Counter(user_mentions_with_food_words).most_common()
    user_mentions_with_food_words_sorted = sorted(user_mentions_with_food_words_counter, key=lambda tup: tup[0])
    # Save into csv
    date = datetime.datetime.today().strftime("%Y_%m_%d-%H_%M_%S")
    with open(date + " - user_mentions_with_food_words", 'w', encoding='utf-8-sig', newline='') as csv_file:
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
    hashtags_about_food_file = open("hashtags_about_food.txt")
    hashtags_about_food = hashtags_about_food_file.read().splitlines()
    # Calculate frequencies for hashtags_about_food
    hashtags_about_food_counter = Counter(hashtags_about_food).most_common()
    hashtags_about_food_sorted = sorted(hashtags_about_food_counter, key=lambda tup: tup[0])
    # Save into csv
    date = datetime.datetime.today().strftime("%Y_%m_%d-%H_%M_%S")
    with open(date + " - hashtags_about_food", 'w', encoding='utf-8-sig', newline='') as csv_file:
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
    hashtags_with_food_words_file = open("hashtags_with_food_words.txt")
    hashtags_with_food_words = hashtags_with_food_words_file.read().splitlines()
    # Calculate frequencies for hashtags_with_food_words
    hashtags_with_food_words_counter = Counter(hashtags_with_food_words).most_common()
    hashtags_with_food_words_sorted = sorted(hashtags_with_food_words_counter, key=lambda tup: tup[0])
    # Save into csv
    date = datetime.datetime.today().strftime("%Y_%m_%d-%H_%M_%S")
    with open(date + " - hashtags_with_food_words", 'w', encoding='utf-8-sig', newline='') as csv_file:
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
    what_words_file = open("what_words.txt")
    what_words = what_words_file.read().splitlines()
    # Calculate frequencies for what_words
    what_words_counter = Counter(what_words).most_common()
    what_words_sorted = sorted(what_words_counter, key=lambda tup: tup[0])
    # Save into csv
    date = datetime.datetime.today().strftime("%Y_%m_%d-%H_%M_%S")
    with open(date + " - what_words", 'w', encoding='utf-8-sig', newline='') as csv_file:
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

detect_food_in_batch()