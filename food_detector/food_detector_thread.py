import copy
from datetime import timedelta
from threading import Thread
from time import time

from food_detector.food_detector_service import FoodDetectorService


class RawDataFoodDetectorThread(Thread):
    def __init__(self, thread_id, name, raw_data, raw_data_range, spanish_pos_tagger, tag_map, p_file):
        Thread.__init__(self)
        self.id = thread_id
        self.name = name
        self.raw_data = raw_data
        self.raw_data_count_start = raw_data_range[0]
        self.raw_data_count_end = raw_data_range[1]
        self.food_detector_service = FoodDetectorService(spanish_pos_tagger, tag_map)
        self.p_file = p_file
        self.food_n_grams = []
        self.user_mentions_about_food = []
        self.user_mentions_with_food = []
        self.hashtags_about_food = []
        self.hashtags_with_food = []
        self.text_about_food = []
        self.text_not_about_food = []
        self.what_words = []
        self.new_what_words = []

    def run(self):
        start_time = time()
        raw_data_count = 0
        success_count = 0
        execution_count = self.raw_data_count_start
        while execution_count <= self.raw_data_count_end:
            raw_data_to_process = self.raw_data[execution_count]
            result = self.food_detector_service.detect_food_from_raw_data(raw_data_to_process)
            if result is not None:
                if result['about_food'] is True:
                    self.food_n_grams += copy.deepcopy(result['food_n_grams'])
                    self.user_mentions_about_food += copy.deepcopy(result['user_mentions_about_food'])
                    self.user_mentions_with_food += copy.deepcopy(result['user_mentions_with_food'])
                    self.hashtags_about_food += copy.deepcopy(result['hashtags_about_food'])
                    self.hashtags_with_food += copy.deepcopy(result['hashtags_with_food'])
                    self.what_words += copy.deepcopy(result['what_words'])
                    self.text_about_food.append(result['text'])
                    self.new_what_words += copy.deepcopy(result['new_what_words'])
                    success_count += 1
                else:
                    self.text_not_about_food.append(result['text'])
            execution_count += 1
            raw_data_count += 1
        execution_time = time() - start_time
        self.p_file.write(self.name + " processed " + str(success_count)
                          + " conversations from " + str(raw_data_count)
                          + " raw data (range: " + str(self.raw_data_count_start)
                          + " - " + str(self.raw_data_count_end)
                          + ").Execution time: " + str(timedelta(seconds=execution_time)) + "\n")
        self.p_file.flush()
        return