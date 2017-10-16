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

    def detect_food_from_raw_data(self, raw_data):
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
                                    return self.result_generator(raw_data_id, result)

    def detect_food_from_conversation(self, conversation):
        text = conversation['conversation']['from_platform']['text']
        result = self.food_detector.detect_food_from_text(text)
        conversation_id = conversation['_id']
        return self.result_generator(conversation_id, result)

    def result_generator(self, id_result, parcial_results):
        final_food_anagrams = []
        for word in parcial_results["food_anagrams"]:
            final_food_anagrams.append(id_result + "\t" + parcial_results['clean_text'] + "\t"
                                       + parcial_results['final_text'] + "\t"
                                       + word + "\t" + parcial_results["food_anagrams"][word])
        final_result = {
            "about_food": parcial_results['about_food'],
            "text": parcial_results["text"] + "\t" + parcial_results["clean_text"],
            "what_words": parcial_results['what_words'],
            "food_anagrams": final_food_anagrams,
            "user_mentions": parcial_results["user_mentions"],
            "user_mentions_with_words": parcial_results["user_mentions_with_words"],
            "hashtags": parcial_results["hashtags"],
            "hashtags_with_what_words": parcial_results["hashtags_with_what_words"]
        }
        return final_result

