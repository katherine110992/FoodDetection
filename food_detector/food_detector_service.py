import codecs
from configparser import ConfigParser, ExtendedInterpolation
import os

import food_detection_root
from food_detector.food_detector import FoodDetector


class FoodDetectorService:

    def __init__(self, spanish_pos_tagger, tag_map):
        # 1. Read what list
        lists_path = food_detection_root.ROOT_DIR + os.path.sep + 'data' + os.path.sep
        what_food_list_file = codecs.open(lists_path + "list - original_stemmed_what_food.txt", encoding='utf-8')
        what_food_list = what_food_list_file.read().splitlines()
        what_food_list_file.close()
        what_food = {}
        for line in what_food_list:
            data = line.split("\t")
            stem = data[1]
            word = data[0]
            what_food[word] = stem
        # 2. Read configuration file
        path_to_configuration = food_detection_root.ROOT_DIR + os.path.sep + 'configuration' + os.path.sep \
                                + 'configuration.ini'
        config_file = ConfigParser(interpolation=ExtendedInterpolation())
        config_file.read_file(codecs.open(path_to_configuration, "r", "utf8"))
        self.food_detector = FoodDetector(what_food, spanish_pos_tagger, tag_map, config_file)

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

    @staticmethod
    def result_generator(id_result, results):
        clean_text = results['clean_text']
        spaced_text = results['spaced_text']
        spaced_text_with_stopwords = results['spaced_text_with_stopwords']
        food_n_grams = results['food_n_grams']
        food_n_grams_with_stopwords = results['food_n_grams_with_stopwords']
        final_food_n_grams = []
        for n_gram in food_n_grams:
            final_food_n_grams.append(id_result + "\t" + clean_text + "\t"
                                      + "NoStopWords" + "\t"
                                      + spaced_text + "\t"
                                      + n_gram + "\t"
                                      + food_n_grams[n_gram]['stem'] + "\t"
                                      + food_n_grams[n_gram]['pos'] + "\t"
                                      + str(food_n_grams[n_gram]['length']))
        for n_gram in food_n_grams_with_stopwords:
            final_food_n_grams.append(id_result + "\t" + clean_text + "\t"
                                      + "WithStopWords" + "\t"
                                      + spaced_text_with_stopwords + "\t"
                                      + n_gram + "\t"
                                      + food_n_grams_with_stopwords[n_gram]['stem'] + "\t"
                                      + food_n_grams_with_stopwords[n_gram]['pos'] + "\t"
                                      + str(food_n_grams_with_stopwords[n_gram]['length']))
        results['text'] = id_result + "\t" + clean_text
        results['food_n_grams'] = final_food_n_grams
        del (results['clean_text'])
        del (results['spaced_text'])
        del (results['spaced_text_with_stopwords'])
        del (results['food_n_grams_with_stopwords'])
        return results
