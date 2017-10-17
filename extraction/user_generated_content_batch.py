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
    # years = [2016, 2017]
    # int_months = [8, 9]
    years = [2016]
    int_months = [8]
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
            days = calendar.monthrange(year, month)[1]
            days_times = 1
            month_times = int(days / days_times)
            start_days_count = 4
            end_days_count = 4
            for aux_days in range(0, month_times):
                start_days_count = end_days_count
                day_start_date = start_date.replace(day=start_days_count)
                end_days_count += days_times
                if end_days_count <= days:
                    day_finish_date = day_start_date.replace(day=end_days_count)
                else:
                    day_finish_date = finish_date
                print(day_finish_date)
                # Aggregate conversations
                clear_collection(semi_structured_access, "conversation_current_period", p_file)
                aggregate_start_time = time()
                p_file.write("Aggregating conversation_current_period by dates\n")
                p_file.flush()
                semi_structured_access.aggregate_data("conversation", "conversation_current_period",
                                                      "all_by_dates", [day_start_date,
                                                                       day_finish_date])
                elapsed_time = time() - aggregate_start_time
                p_file.write("Aggregate conversation_current_period time: "
                             + str(timedelta(seconds=elapsed_time)) + '\n')
                p_file.flush()
                count = semi_structured_access.count_from_database("conversation_current_period", "all", [])
                p_file.write("Total user generated content from " + str(day_start_date) + " to "
                             + str(day_finish_date) + ": " + str(count) + "\n")
                p_file.flush()
                if count != 0:
                    reindex_start_time = time()
                    semi_structured_access.reindex_collection("conversation_current_period")
                    elapsed_time = time() - reindex_start_time
                    p_file.write("Reindex conversation_current_period time: "
                                 + str(timedelta(seconds=elapsed_time)) + '\n')
                    p_file.flush()
                    # Get conversations by hour
                    get_conversations_from_dates(day_start_date, day_finish_date,
                                                 anagrams_with_food_words_file, user_mentions_about_food_file,
                                                 user_mentions_with_food_words_file, hashtags_about_food_file,
                                                 hashtags_with_food_words_file, what_words_file, text_about_food_file,
                                                 text_not_about_food_file, p_file)
            month_execution_time = time() - month_start_time
            p_file.write("Process month " + str(month) + ". Execution time "
                                   + str(timedelta(seconds=month_execution_time)) + "\n")
            p_file.flush()
            month_index += 1
    # Close database connection
    semi_structured_access.close_database_connection(process_name)
    generate_csv_files(start_time, p_file)


def get_conversations_from_dates(day_start_date, day_finish_date, anagrams_with_food_words_file,
                                 user_mentions_about_food_file, user_mentions_with_food_words_file,
                                 hashtags_about_food_file, hashtags_with_food_words_file, what_words_file,
                                 text_about_food_file, text_not_about_food_file, p_file):
    period_time = time()
    period_results = generate_food_detector_threads(day_start_date, day_finish_date, p_file)
    p_file.write("Saving results for period" + "\n")
    p_file.flush()
    aux_anagrams_with_food_words = copy.deepcopy(period_results[0])
    for word in aux_anagrams_with_food_words:
        anagrams_with_food_words_file.write(word + "\n")
        anagrams_with_food_words_file.flush()
    aux_user_mentions_about_food = copy.deepcopy(period_results[1])
    for word in aux_user_mentions_about_food:
        user_mentions_about_food_file.write(word + "\n")
        user_mentions_about_food_file.flush()
    aux_user_mentions_with_food_words = copy.deepcopy(period_results[2])
    for word in aux_user_mentions_with_food_words:
        user_mentions_with_food_words_file.write(word + "\n")
        user_mentions_with_food_words_file.flush()
    aux_hashtags_about_food = copy.deepcopy(period_results[3])
    for word in aux_hashtags_about_food:
        hashtags_about_food_file.write(word + "\n")
        hashtags_about_food_file.flush()
    aux_hashtags_with_food_words = copy.deepcopy(period_results[4])
    for word in aux_hashtags_with_food_words:
        hashtags_with_food_words_file.write(word + "\n")
        hashtags_with_food_words_file.flush()
    aux_what_words = copy.deepcopy(period_results[5])
    for word in aux_what_words:
        what_words_file.write(word + "\n")
        what_words_file.flush()
    aux_text_about_food = copy.deepcopy(period_results[6])
    for word in aux_text_about_food:
        text_about_food_file.write(word + "\n")
        text_about_food_file.flush()
    aux_text_not_about_food = copy.deepcopy(period_results[7])
    for word in aux_text_not_about_food:
        text_not_about_food_file.write(word + "\n")
        text_not_about_food_file.flush()
    period_execution_time = time() - period_time
    p_file.write("Period execution time: " + str(timedelta(seconds=period_execution_time)) + "\n")
    p_file.flush()
    return


def generate_food_detector_threads(day_start_date, day_finish_date, p_file):
    # 3. Initialize accumulation variables
    anagrams_with_food_words = []
    user_mentions_about_food = []
    user_mentions_with_food_words = []
    hashtags_about_food = []
    hashtags_with_food_words = []
    what_words = []
    text_about_food = []
    text_not_about_food = []
    data_threads = []
    last_id = 0
    for i in range(0, 23):
        t_name = "Thread_" + str(i)
        hour_start_date = day_start_date.replace(hour=i)
        hour_end_date = day_start_date.replace(hour=i + 1)
        thread = FoodDetectorThread(i, t_name,  hour_start_date, hour_end_date, p_file, "conversation")
        # 8. Start thread
        thread.start()
        data_threads.append(thread)
        last_id = i + 1
    t_name = "Thread_" + str(last_id)
    hour_start_date = day_start_date.replace(hour=last_id)
    hour_end_date = day_finish_date
    thread = FoodDetectorThread(last_id, t_name, hour_start_date, hour_end_date, p_file, "conversation")
    # 8. Start last thread
    thread.start()
    data_threads.append(thread)
    # Wait to thread end
    for thread in data_threads:
        thread.join()
    p_file.write("Accumulating values\n")
    p_file.flush()
    for thread in data_threads:
        for message in thread.messages:
            p_file.write(message)
            p_file.flush()
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