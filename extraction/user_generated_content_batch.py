import calendar
import copy
import csv
import datetime
import os
from collections import Counter
from datetime import timedelta
from time import time
from u_generic.utils import Utils
import sys

from list_generation.generate_final_lists import generate_csv_files

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
        p_file.write("------------------------  YEAR " + str(year) + "  ------------------------\n")
        p_file.flush()
        for month in int_months:
            month_start_time = time()
            dates = Utils().get_query_dates_per_year_and_month(year, month)
            start_date = dates[0]
            finish_date = dates[1]
            generation_date = dates[2]
            clear_collection(semi_structured_access, "conversation_current_period", p_file)
            aggregate_start_time = time()
            p_file.write("Aggregating conversation_current_period by dates\n")
            p_file.flush()
            semi_structured_access.aggregate_data("conversation", "conversation_current_period",
                                                       "all_by_dates", [start_date, finish_date])
            elapsed_time = time() - aggregate_start_time
            p_file.write("Aggregate conversation_current_period time: "
                                   + str(timedelta(seconds=elapsed_time)) + '\n')
            p_file.flush()
            count = semi_structured_access.count_from_database("conversation_current_period", "all", [])
            p_file.write("Total conversations from current period: " + str(count) + "\n")
            p_file.flush()
            reindex_start_time = time()
            semi_structured_access.reindex_collection("conversation_current_period")
            elapsed_time = time() - reindex_start_time
            p_file.write("Reindex conversation_current_period time: "
                                   + str(timedelta(seconds=elapsed_time)) + '\n')
            p_file.flush()
            month_results = generate_food_detector_threads(semi_structured_access, p_file)
            p_file.write("Saving results for Month" + "\n")
            p_file.flush()
            aux_anagrams_with_food_words = copy.deepcopy(month_results[0])
            for word in aux_anagrams_with_food_words:
                anagrams_with_food_words_file.write(word + "\n")
                anagrams_with_food_words_file.flush()
            aux_user_mentions_about_food = copy.deepcopy(month_results[1])
            for word in aux_user_mentions_about_food:
                user_mentions_about_food_file.write(word + "\n")
                user_mentions_about_food_file.flush()
            aux_user_mentions_with_food_words = copy.deepcopy(month_results[2])
            for word in aux_user_mentions_with_food_words:
                user_mentions_with_food_words_file.write(word + "\n")
                user_mentions_with_food_words_file.flush()
            aux_hashtags_about_food = copy.deepcopy(month_results[3])
            for word in aux_hashtags_about_food:
                hashtags_about_food_file.write(word + "\n")
                hashtags_about_food_file.flush()
            aux_hashtags_with_food_words = copy.deepcopy(month_results[4])
            for word in aux_hashtags_with_food_words:
                hashtags_with_food_words_file.write(word + "\n")
                hashtags_with_food_words_file.flush()
            aux_what_words = copy.deepcopy(month_results[5])
            for word in aux_what_words:
                what_words_file.write(word + "\n")
                what_words_file.flush()
            aux_text_about_food = copy.deepcopy(month_results[6])
            for word in aux_text_about_food:
                text_about_food_file.write(word + "\n")
                text_about_food_file.flush()
            aux_text_not_about_food = copy.deepcopy(month_results[7])
            for word in aux_text_not_about_food:
                text_not_about_food_file.write(word + "\n")
                text_not_about_food_file.flush()
            month_execution_time = time() - month_start_time
            p_file.write("Saving results for month " + str(month) + ". Execution time "
                                   + str(timedelta(seconds=month_execution_time)) + "\n")
            p_file.flush()
            month_index += 1
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
    conversations = semi_structured_access.get_from_database('conversation_current_period', "all", [])
    total_conversations = conversations.count()
    p_file.write("Total raw data per date: " + str(total_conversations) + "\n")
    p_file.flush()
    # 4. Calculate thread numbers
    thread_number = 80
    if total_conversations != 0:
        fill_number = int(total_conversations / thread_number)
        threads_number = int(total_conversations / fill_number)
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
        if raw_data_count_end == total_conversations:
            raw_data_count_end -= 1
        threads_raw_data_range.append((raw_data_count_start, raw_data_count_end))
        raw_data_count_start = raw_data_count_end + 1
        raw_data_count_end = fill_number * filling_counter
        filling_counter += 1
    if raw_data_count_end - fill_number < total_conversations:
        threads_names.append("Thread_" + str(aux_count_name + 1))
        threads_raw_data_range.append((raw_data_count_start, total_conversations - 1))
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
        thread = FoodDetectorThread(i, t_name, conversations, t_range, p_file)
        # 8. Start thread
        thread.start()
        raw_data_threads.append(thread)
        t_range_count -= 1
    # Wait to thread end
    for thread in raw_data_threads:
        thread.join()
    conversations.close()
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


def clear_collection(semi_structured_data_access, name, performance_file):
    try:
        count = semi_structured_data_access.count_from_database(name, "all", [])
        performance_file.write("Deleting " + str(count) + " old documents from " + name + "\n")
        performance_file.flush()
        semi_structured_data_access.clear_data_from_database(name, "all", [])
        count = semi_structured_data_access.count_from_database(name, "all", [])
        performance_file.write("Documents after: " + str(count) + "\n")
        performance_file.flush()
    except:
        print(sys.exc_info())

detect_food_in_batch()