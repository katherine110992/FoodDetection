import copy
from datetime import timedelta
from threading import Thread
from time import time

from food_detector.food_detector_service import FoodDetectorService

from dao_semi_structured_data_access.semi_structured_data_access import SemiStructuredDataAccess


class FoodDetectorThread(Thread):
    def __init__(self, thread_id, name, start_date, end_date, p_file, thread_type):
        Thread.__init__(self)
        self.id = thread_id
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.food_detector_service = FoodDetectorService()
        self.p_file = p_file
        self.anagrams_with_food_words = []
        self.user_mentions_about_food = []
        self.user_mentions_with_food_words = []
        self.hashtags_about_food = []
        self.hashtags_with_food_words = []
        self.text_about_food = []
        self.text_not_about_food = []
        self.what_words = []
        self.thread_type = thread_type
        self.semi_structured_access = SemiStructuredDataAccess(name, ["database"])

    def run(self):
        start_time = time()
        data_count = 0
        self.p_file.write(self.name + " getting data from " + str(self.start_date)
                          + " to " + str(self.end_date) + "\n")
        self.p_file.flush()
        data = self.semi_structured_access.get_from_database('conversation_current_period', "all_by_dates",
                                                             [self.start_date, self.end_date])
        self.p_file.write(self.name + " total data to process: " + str(data.count()) + "\n")
        self.p_file.flush()
        for data_to_process in data:
            result = self.food_detector_service.detect_food_from_conversation(data_to_process)
            if result is not None:
                if result['about_food'] is True:
                    self.anagrams_with_food_words += copy.deepcopy(result['food_anagrams'])
                    self.user_mentions_about_food += copy.deepcopy(result['user_mentions'])
                    self.user_mentions_with_food_words += copy.deepcopy(result['user_mentions_with_words'])
                    self.hashtags_about_food += copy.deepcopy(result['hashtags'])
                    self.hashtags_with_food_words += copy.deepcopy(result['hashtags_with_what_words'])
                    self.what_words += copy.deepcopy(result['what_words'])
                    self.text_about_food.append(result['text'])
                    data_count += 1
                else:
                    self.text_not_about_food.append(result['text'])
        execution_time = time() - start_time
        data.close()
        self.semi_structured_access.close_database_connection(self.name)
        self.p_file.write(self.name + " processed " + str(data_count)
                          + " from " + str(data.count()) + " data. Execution time: "
                          + str(timedelta(seconds=execution_time)) + "\n")
        self.p_file.flush()
        return
