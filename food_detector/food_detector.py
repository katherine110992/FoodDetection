import re
import unicodedata
from u_logging.logging import Logging
import sys

from text_analysis.text_analysis import TextAnalysis


class FoodDetector:

    def __init__(self, what_food_list, spanish_pos_tagger, tag_map, config_file):
        self.what_food = what_food_list
        self.text_analysis = TextAnalysis(spanish_pos_tagger, tag_map, config_file)

    def detect_food_from_text(self, text):
        try:
            # 1. Initiate final data
            what_words = set()
            hashtags_with_food = []
            user_mentions_with_food = []
            food_n_grams_with_stopwords = {}
            food_n_grams = {}
            new_what_words = []
            # 2. Perform text analysis
            analyzed_text = self.analyze_text(text)
            tokenized_text = analyzed_text['tokenized_text']
            tagged_text_with_stopwords = analyzed_text['tagged_text_with_stopwords']
            tagged_text = analyzed_text['tagged_text']
            stemmed_text = analyzed_text['stemmed_text']
            spaced_text_with_stopwords = analyzed_text['spaced_text_with_stopwords']
            spaced_text = analyzed_text['spaced_text']
            clean_text = analyzed_text['clean_text']
            hashtags_about_food = analyzed_text['hashtags_about_food']
            user_mentions_about_food = analyzed_text['user_mentions_about_food']
            # 3. Detect Food in Hashtags
            i = 0
            while len(hashtags_about_food) > i >= 0:
                hashtag = hashtags_about_food[i]
                removed = False
                for word in self.what_food.keys():
                    if word in hashtag:
                        what_words.add(word)
                        hashtags_with_food.append(hashtag)
                        hashtags_about_food.remove(hashtag)
                        removed = True
                        break
                if not removed:
                    i += 1
            # 4. Detect Food in User Mentions
            while len(user_mentions_about_food) > i >= 0:
                alias = user_mentions_about_food[i]
                removed = False
                for word in self.what_food.keys():
                    if word in alias:
                        what_words.add(word)
                        user_mentions_with_food.append(alias)
                        user_mentions_about_food.remove(alias)
                        removed = True
                        break
                if not removed:
                    i += 1
            # 5. Detect Food in text
            for i in range(0, len(stemmed_text)):
                stem = stemmed_text[i]
                if stem in self.what_food.values():
                    word = tokenized_text[i]
                    if word in self.what_food.keys():
                        what_words.add(word)
                    else:
                        # Check if the word is plural
                        word_morph = tagged_text[word]['morph']
                        if 'Plur' in word_morph:
                            for aux_word, aux_stem in self.what_food.items():
                                if aux_stem == stem:
                                    what_words.add(aux_word)
                                    break
                        else:
                            new_what_words.append({stem: word})
            if len(what_words) != 0 and len(tagged_text_with_stopwords) > 1 and len(tagged_text) > 1:
                # 5.1. Create n-grams with stop_words
                n_grams_with_stopwords = self.text_analysis.create_n_grams(spaced_text_with_stopwords,
                                                                           tagged_text_with_stopwords)
                # 5.1.1 Detect Food in n-grams with stopwords
                for n_gram in n_grams_with_stopwords:
                    n_gram_stems = n_grams_with_stopwords[n_gram]['stem'].split(" ")
                    for stem in n_gram_stems:
                        if stem in self.what_food.values():
                            food_n_grams_with_stopwords[n_gram] = {
                                'pos': n_grams_with_stopwords[n_gram]['pos'],
                                'stem': n_grams_with_stopwords[n_gram]['stem'],
                                'length': n_grams_with_stopwords[n_gram]['length']
                            }
                # 8.2. Create n-grams without stop_words
                n_grams = self.text_analysis.create_n_grams(spaced_text, tagged_text)
                # 8.2.1. Detect Food in n-grams without stop_words
                for n_gram in n_grams:
                    n_gram_stems = n_grams[n_gram]['stem'].split(" ")
                    for stem in n_gram_stems:
                        if stem in self.what_food.values():
                            food_n_grams[n_gram] = {
                                'pos': n_grams[n_gram]['pos'],
                                'stem': n_grams[n_gram]['stem'],
                                'length': n_grams[n_gram]['length']
                            }
            if len(what_words) != 0:
                about_food = True
            else:
                about_food = False
            result = {
                "about_food": about_food,
                "clean_text": clean_text,
                "spaced_text": spaced_text,
                "spaced_text_with_stopwords": spaced_text_with_stopwords,
                "what_words": what_words,
                "new_what_words": new_what_words,
                "food_n_grams_with_stopwords": food_n_grams_with_stopwords,
                "food_n_grams": food_n_grams,
                "hashtags_with_food": hashtags_with_food,
                "hashtags_about_food": hashtags_about_food,
                "user_mentions_with_food": user_mentions_with_food,
                "user_mentions_about_food": user_mentions_about_food
            }
        except:
            Logging.write_standard_error(sys.exc_info())
            result = {
                "about_food": False,
                "clean_text": '',
                "spaced_text": "",
                "spaced_text_with_stopwords": "",
                "what_words": [],
                "new_what_words": [],
                "food_n_grams_with_stopwords": {},
                "food_n_grams": {},
                "hashtags_with_food": [],
                "hashtags_about_food": [],
                "user_mentions_with_food": [],
                "user_mentions_about_food": []
            }
        return result

    @staticmethod
    def proper_encoding(data):
        text = unicodedata.normalize('NFD', data)
        text = text.encode('ascii', 'ignore')
        text = text.decode("utf-8")
        return text

    def analyze_text(self, text):
        # 1. Lower text
        text = text.lower()
        # 2. Encode properly
        text = self.proper_encoding(text)
        # 3. Remove patterns - Not for the final script
        pattern_free_text = re.sub('(ja){2,}', '', text)
        pattern_free_text = re.sub('(ha){2,}', '', pattern_free_text)
        # 4. Identify special characters (# and @. Remove urls)
        results = self.text_analysis.identify_special_characters(pattern_free_text)
        clean_text = results['clean_text']
        hashtags_about_food = results['#']
        user_mentions_about_food = results['@']
        # 5. POS - Tokenize - Stopwords - Stemming
        results = self.text_analysis.complete_text_analysis(clean_text)
        # 6. Add special characters identification results
        results['hashtags_about_food'] = hashtags_about_food
        results['user_mentions_about_food'] = user_mentions_about_food
        return results
