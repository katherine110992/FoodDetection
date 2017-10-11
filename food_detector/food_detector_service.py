import codecs
import configparser
import os

import food_detection_root
from food_detector.food_detector import FoodDetector


class FoodDetectorService:

    def __init__(self):
        # Read what list
        lists_path = food_detection_root.ROOT_DIR + os.path.sep + 'data' + os.path.sep
        what_list_file = codecs.open(lists_path + 'list - what_food.txt', encoding='utf-8')
        what_list = what_list_file.read().splitlines()
        what_list_file.close()
        stemmed_what_list_file = codecs.open(lists_path + 'list - stemmed_what_food.txt', encoding='utf-8')
        stemmed_what_list = stemmed_what_list_file.read().splitlines()
        stemmed_what_list_file.close()
        path_to_configuration = food_detection_root.ROOT_DIR + os.path.sep + 'configuration' + os.path.sep \
                                + 'configuration.ini'
        config_file = configparser.ConfigParser()
        config_file.read(path_to_configuration)
        self.food_detector = FoodDetector(what_list, stemmed_what_list, config_file)

    def detect_food(self, raw_data):
        if 'text' in raw_data:
            if 'lang' in raw_data:
                language = raw_data["lang"]
                if language != "und":
                    if "place" in raw_data.keys():
                        place = raw_data["place"]
                        if place is not None:
                            if "country_code" in place.keys():
                                raw_data_country_code = raw_data["place"]["country_code"]
                                if raw_data_country_code in ["CO"]:
                                    result = self.food_detector.detect_food_from_text(raw_data['text'])
                                    raw_data_id = raw_data['id_str']
                                    final_food_anagrams = []
                                    for word in result["food_anagrams"]:
                                        final_food_anagrams.append(raw_data_id + "\t" + result['final_text'] + "\t"
                                                                   + word + "\t" + result["food_anagrams"][word])
                                    final_result = {
                                        "about_food": result['about_food'],
                                        "text": result["text"] + "\t" + result["clean_text"],
                                        "what_words": result['what_words'],
                                        "food_anagrams": final_food_anagrams,
                                        "user_mentions": result["user_mentions"],
                                        "user_mentions_with_words": result["user_mentions_with_words"],
                                        "hashtags": result["hashtags"],
                                        "hashtags_with_what_words": result["hashtags_with_what_words"]
                                    }
                                    return final_result

