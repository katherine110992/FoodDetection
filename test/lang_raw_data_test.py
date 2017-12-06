from pymongo import MongoClient
from datetime import timedelta, datetime
from collections import Counter
from time import time
import food_detection_root
import os
from configparser import ConfigParser, ExtendedInterpolation
import codecs
import spacy
from textblob import TextBlob
import ast
import copy
import re


def simple_identification():
    client_from = MongoClient()
    db_from = client_from["SSD"]
    coll_from = db_from["raw_data"]
    start_time = time()
    date = datetime.today().strftime("%Y_%m_%d-%H_%M_%S")
    path_to_file = date + " - DetectLanguage_Performance.txt"
    p_file = codecs.open(path_to_file, encoding='utf-8', mode='a')
    p_file.write(date + " Detecting Language Test - Local Execution" + "\n")
    p_file.flush()
    l_file = codecs.open(date + " - LanguageDetection.txt", encoding='utf-8', mode='a')
    # II. Prepare data
    p_file.write("Preparing initial data ... " + "\n")
    path_to_configuration = food_detection_root.ROOT_DIR + os.path.sep + 'configuration' + os.path.sep \
                            + 'configuration.ini'
    all_from_tweets = coll_from.find()
    t_lang_count = 0
    tb_lang_count = 0
    country_count = 0
    stop = 10000
    count = 0
    p_file.write("Total data to process: " + str(stop) + "\n")
    for raw_data in all_from_tweets:
        if 'text' in raw_data:
            if "place" in raw_data.keys():
                place = raw_data["place"]
                if place is not None:
                    if "country_code" in place.keys():
                        raw_data_country_code = raw_data["place"]["country_code"]
                        print(raw_data_country_code)
                        print(count)
                        count += 1
                        if raw_data_country_code in ["CO"]:
                            country_count += 1
                            lang = raw_data["lang"]
                            text = raw_data['text']
                            if lang == 'es':
                                l_file.write(lang + ';;' + text.replace('\n', '') + "\n")
                                l_file.flush()
                                t_lang_count += 1
                            else:
                                if len(text) >= 3:
                                    blob = TextBlob(text)
                                    detected_language = blob.detect_language()
                                    l_file.write(lang + ';' + detected_language + ';' + text.replace('\n', '') + "\n")
                                    l_file.flush()
                                    if detected_language == 'es':
                                        tb_lang_count += 1
                        if count == stop:
                            break
    all_from_tweets.close()
    client_from.close()
    l_file.close()
    p_file.write("Tweets: " + str(count) + "\n")
    p_file.write("Colombian tweets: " + str(country_count) + "\n")
    p_file.write("Spanish tweets by Twitter: " + str(t_lang_count) + "\n")
    p_file.write("Spanish tweets by TextBlob: " + str(tb_lang_count) + "\n")
    p_file.write("Twitter Ratio: " + str(t_lang_count/country_count) + "\n")
    p_file.write("TextBlob Ratio: " + str(tb_lang_count/country_count) + "\n")
    execution_time = time() - start_time
    p_file.write("Execution time: " + str(timedelta(seconds=execution_time)) + "\n")
    p_file.flush()
    p_file.close()


simple_identification()
