from text_analysis.text_analysis import TextAnalysis
import unicodedata
from sklearn.feature_extraction.text import CountVectorizer
import ast
import re


class FoodDetector:

    def __init__(self, what_list, stemmed_what_list, config_file):
        self.what_list = what_list
        self.stemmed_what_list = stemmed_what_list
        self.text_analysis = TextAnalysis(config_file)
        self.special_characters = ast.literal_eval(config_file.get('FoodDetector', 'special_characters'))
        self.minimum = int(config_file.get('FoodDetector', 'minimum_n_gram'))
        self.maximum = int(config_file.get('FoodDetector', 'maximum_n_gram'))

    def detect_food_from_text(self, text):
        # 1. Lower text
        text = text.lower()
        # 3. Encode properly
        text = self.proper_encoding(text)
        # 4. Initialize data structures
        about_food = False
        user_mentions_with_words = []
        hashtags_with_what_words = []
        # 5. Identify user_mentions, hashtags and remove urls
        clean_text, hashtags, user_mentions = self.get_hashtags_and_user_mentions(text)
        # 2. Remove ja patterns
        clean_text = re.sub('(ja)+', '', clean_text)
        clean_text = self.text_analysis.remove_puntuation(clean_text)
        # 6. Tokenize
        token_text = self.text_analysis.spanish_tokenizer(clean_text)
        # 7. Stem
        stemmed_text = self.text_analysis.spanish_stemmer(token_text)
        # 8. POS
        tagged_text = self.text_analysis.part_of_speech(stemmed_text)
        # 9. Remove stopwords
        final_token_text, final_tagged_text = self.text_analysis.remove_stop_words(tagged_text)
        # 10. Create anagrams
        final_anagrams = {}
        final_text = ' '.join(final_token_text)
        if len(final_token_text) > 1:
            anagrams_generator = CountVectorizer(ngram_range=(self.minimum, self.maximum), strip_accents='unicode',
                                                      tokenizer=lambda x: x.split(' '))
            anagrams_generator.fit([final_text])
            text_anagrams = anagrams_generator.get_feature_names()
            for anagram in text_anagrams:
                # print(anagram)
                words = anagram.split(" ")
                # print(words)
                pos = ""
                for word in words:
                    pos += final_tagged_text[word] + "+"
                final_anagrams[anagram] = pos[0:len(pos) - 1]
            # print(final_anagrams)
        # 11. Detect food
        food_anagrams = {}
        what_words = set()
        # 11.1. Look in anagrams
        for anagram in final_anagrams:
            anagram_words = anagram.split(" ")
            for word in anagram_words:
                if word in self.stemmed_what_list:
                    food_anagrams[anagram] = final_anagrams[anagram]
                    what_words.add(word)
                    about_food = True
        # print(food_anagrams)
        # 11.2. Look in hashtags
        for hashtag in hashtags:
            for word in self.what_list:
                if word in hashtag:
                    hashtags_with_what_words.append(hashtag)
                    about_food = True
                    break
        # print(hashtags_with_what_words)
        # 11.3. Look in user_mentions
        for alias in user_mentions:
            for word in self.what_list:
                if word in alias:
                    user_mentions_with_words.append(alias)
                    about_food = True
        # print(user_mentions_with_words)
        result = {
            "about_food": about_food,
            "text": text,
            "clean_text": clean_text,
            "final_text": final_text,
            "what_words": what_words,
            "food_anagrams": food_anagrams,
            "user_mentions": user_mentions,
            "user_mentions_with_words": user_mentions_with_words,
            "hashtags": hashtags,
            "hashtags_with_what_words": hashtags_with_what_words
        }
        return result

    @staticmethod
    def proper_encoding(data):
        text = unicodedata.normalize('NFD', data)
        text = text.encode('ascii', 'ignore')
        text = text.decode("utf-8")
        return text

    def get_hashtags_and_user_mentions(self, text):
        # Identify hashtags, user mentions and remove urls
        user_mentions = []
        hashtags = []
        for character in self.special_characters:
            count_character = text.count(character)
            if count_character > 0:
                for i in range(0, count_character):
                    start = text.find(character)
                    end = text.find(" ", start)
                    if end == -1:
                        end = len(text)
                    text_to_remove = text[start:end]
                    if len(text_to_remove) != 1:
                        if character == "#":
                            hashtags.append(text_to_remove)
                        elif character == "@":
                            user_mentions.append(text_to_remove)
                    text = text.replace(text_to_remove, "")
        text = text.strip(' ')
        text = ' '.join(text.split())
        return text, hashtags, user_mentions
