from nltk.stem.snowball import SnowballStemmer
import os
import food_detection_root
from nltk.corpus import stopwords
import ast
import codecs
from sklearn.feature_extraction.text import CountVectorizer
import re


class TextAnalysis:

    def __init__(self, pos_tagger, tag_map, config_file):
        tags = config_file.options("Google_Universal_POS_Tags")
        self.google_universal_tags = {}
        for tag in tags:
            self.google_universal_tags[tag.upper()] = config_file.get('Google_Universal_POS_Tags', tag)
        # 2. Read special characters (#, @, https, etc.)
        self.special_characters = ast.literal_eval(config_file.get('TextAnalysis', 'special_characters'))
        # 3. Configure Spanish POS tagger
        self.spanish_pos_tagger = pos_tagger
        self.tag_map = tag_map
        # 4. Configure Stemmer
        self.stemmers = ast.literal_eval(config_file.get('TextAnalysis', 'stemmers'))
        self.snowball_stemmer = SnowballStemmer("spanish")
        # 5. Get configuration data
        self.not_wanted_pos = ast.literal_eval(config_file.get('TextAnalysis', 'not_wanted_pos'))
        self.additional_symbols = ast.literal_eval(config_file.get('TextAnalysis', 'additional_symbols'))
        # 6. Read original_stemmed_what_food list
        path = food_detection_root.ROOT_DIR + os.path.sep + 'data' + os.path.sep
        what_food_list_file = codecs.open(path + "list - original_stemmed_what_food.txt", encoding='utf-8')
        what_food_list = what_food_list_file.read().splitlines()
        what_food_list_file.close()
        self.what_food = {}
        for line in what_food_list:
            data = line.split("\t")
            stem = data[1]
            word = data[0]
            self.what_food[word] = stem
        # 7. Configure n-gram generator
        minimum = int(config_file.get('TextAnalysis', 'minimum_n_gram'))
        maximum = int(config_file.get('TextAnalysis', 'maximum_n_gram'))
        self.n_gram_generator = CountVectorizer(ngram_range=(minimum, maximum), strip_accents='unicode',
                                                tokenizer=lambda x: x.split(' '))

    def spanish_tokenizer(self, text, stopwords=False):
        result = self.complete_text_analysis(text)
        if stopwords:
            return result['tokenized_text_with_stopwords']
        else:
            return result['tokenized_text']

    def spanish_stemmer(self, text, stemmer="snowball"):
        if stemmer in self.stemmers:
            result = self.complete_text_analysis(text)
            return result['stemmed_text']
        else:
            return 'The stemmer: ' + stemmer + ' is not supported'

    def part_of_speech(self, text, mode='complete'):
        result = self.complete_text_analysis(text)
        if mode == 'with_stopwords':
            return result['tagged_text_with_stopwords']
        elif mode == 'no_stopwords':
            return result['tagged_text']
        else:
            return result['complete_tagged_text']

    def remove_stop_words(self, text):
        result = self.complete_text_analysis(text)
        return result['spaced_text']

    def remove_punctuation(self, text):
        result = self.complete_text_analysis(text)
        return result['clean_text']

    def complete_text_analysis(self, text, stemmer="snowball"):
        raw_tagged_text = self.spanish_pos_tagger(text)
        complete_tagged_text = []
        tagged_text_with_stopwords = {}
        tagged_text = {}
        tokenized_text_with_stopwords = []
        tokenized_text = []
        stemmed_text = []
        spaced_text_with_stopwords = ""
        spaced_text = ""
        clean_text = ""
        for tag in raw_tagged_text:
            pos_morph = self.tag_map[tag.tag_]
            pos = self.google_universal_tags[pos_morph['pos']]
            if pos != 'espacio':
                if pos == 'puntuación':
                    clean_text = clean_text[0:len(clean_text) - 1] + tag.text + " "
                else:
                    clean_text += tag.text + " "
                if pos not in self.not_wanted_pos.keys():
                    if tag.text not in self.additional_symbols:
                        if stemmer == "snowball":
                            stemmed_word = self.snowball_stemmer.stem(tag.text)
                        else:
                            stemmed_word = "Undefined stemmer"
                        if tag.text not in stopwords.words("spanish"):
                            tag_type = "word"
                            tagged_text[tag.text] = {
                                'pos': pos,
                                'stem': stemmed_word,
                                'morph': pos_morph['morph']
                            }
                            tokenized_text.append(tag.text)
                            spaced_text += tag.text + " "
                            stemmed_text.append(stemmed_word)
                        else:
                            tag_type = "stop_word"
                        tagged_text_with_stopwords[tag.text] = {
                            'pos': pos,
                            'stem': stemmed_word,
                            'morph': pos_morph['morph']
                        }
                        tokenized_text_with_stopwords.append(tag.text)
                        spaced_text_with_stopwords += tag.text + " "
                    else:
                        tag_type = "symbol"
                        pos = "símbolo"
                else:
                    tag_type = self.not_wanted_pos[pos]
                final_tag = {
                    'token': tag.text,
                    'pos': pos,
                    'morph': pos_morph['morph'],
                    'type': tag_type
                }
                complete_tagged_text.append({tag.text: final_tag})
        result = {
            'complete_tagged_text': complete_tagged_text,
            'tagged_text_with_stopwords': tagged_text_with_stopwords,
            'tagged_text': tagged_text,
            'tokenized_text_with_stopwords': tokenized_text_with_stopwords,
            'tokenized_text': tokenized_text,
            'stemmed_text': stemmed_text,
            'spaced_text_with_stopwords': spaced_text_with_stopwords[0:len(spaced_text_with_stopwords) - 1],
            'spaced_text': spaced_text[0:len(spaced_text) - 1],
            'clean_text': clean_text[0:len(clean_text) - 1]
        }
        return result

    def create_n_grams(self, text, tagged_text):
        self.n_gram_generator.fit([text])
        text_n_grams = self.n_gram_generator.get_feature_names()
        n_grams = {}
        for n_gram in text_n_grams:
            words = n_gram.split(" ")
            pos = ""
            stem = ""
            for word in words:
                pos += tagged_text[word]['pos'] + "+"
                stem += tagged_text[word]['stem'] + " "
            n_grams[n_gram] = {
                'pos': pos[0:len(pos) - 1],
                'stem': stem[0:len(stem) - 1],
                'length': len(words)
            }
        return n_grams

    def identify_special_characters(self, text, wanted_characters=None):
        if wanted_characters is None:
            wanted_characters = ['#', '@']
        results = {}
        for character in self.special_characters:
            text = re.sub('(' + character + ')+', ' ' + character, text)
            count_character = text.count(character)
            if count_character > 0:
                while count_character > 0:
                    start = text.find(character)
                    end = text.find(" ", start)
                    if end == -1:
                        end = len(text)
                    text_to_remove = text[start:end]
                    if len(text_to_remove) > 2:
                        if character in wanted_characters:
                            if character in results.keys():
                                results[character].append(text_to_remove)
                            else:
                                results[character] = [text_to_remove]
                    text = text.replace(text_to_remove, "")
                    text = ' '.join(text.split())
                    count_character = text.count(character)
        for wanted_character in wanted_characters:
            if wanted_character not in results.keys():
                results[wanted_character] = []
        text = text.strip(' ')
        text = ' '.join(text.split())
        results['clean_text'] = text
        return results
