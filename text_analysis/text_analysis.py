from nltk.tag import StanfordPOSTagger
from nltk.stem.snowball import PorterStemmer
import nltk
import os
import food_detection_root
from nltk.corpus import stopwords
import ast


class TextAnalysis:

    def __init__(self, config_file):
        os.environ['JAVAHOME'] = config_file.get('Paths', 'JAVA_HOME')
        self.model_path = food_detection_root.ROOT_DIR + os.path.sep + 'text_analysis' + os.path.sep + 'models'\
                     + os.path.sep + 'spanish.tagger'
        self.tagger_path = food_detection_root.ROOT_DIR + os.path.sep + 'text_analysis' + os.path.sep + 'tagger'\
                     + os.path.sep + 'stanford-postagger.jar'
        self.spanish_pos_tagger = StanfordPOSTagger(self.model_path, self.tagger_path)
        tags = config_file.options("EAGLES_Standard")
        self.eagles_standard = {}
        for tag in tags:
            self.eagles_standard[tag] = ast.literal_eval(config_file.get('EAGLES_Standard', tag))
        self.wanted_prepositions = ast.literal_eval(config_file.get('TextAnalysis', 'wanted_prepositions'))
        self.not_wanted_tags = ast.literal_eval(config_file.get('TextAnalysis', 'not_wanted_tags'))
        self.stemmer = PorterStemmer()

    @staticmethod
    def spanish_tokenizer(text, lang='spanish'):
        tokenized_text = nltk.word_tokenize(text, lang)
        return tokenized_text

    def spanish_stemmer(self, tokenized_text):
        stemmed_text = list()
        for word in tokenized_text:
            stemmed_word = self.stemmer.stem(word)
            stemmed_text.append(stemmed_word)
        return stemmed_text

    def part_of_speech(self, stemmed_text):
        tagged_text = sum(self.spanish_pos_tagger.tag_sents([stemmed_text]), [])
        processed_text = []
        for s in tagged_text:
            for tag in self.eagles_standard:
                if s[1] in self.eagles_standard[tag] and tag not in self.not_wanted_tags:
                    processed_text.append({s[0]: tag})
        return processed_text

    def remove_stop_words(self, processed_text):
        clean_text = []
        final_tagged_text = {}
        for pos_text in processed_text:
            for word in pos_text:
                if word in self.wanted_prepositions:
                    clean_text.append(word)
                    final_tagged_text[word] = pos_text[word]
                else:
                    if word not in stopwords.words("spanish"):
                        clean_text.append(word)
                        final_tagged_text[word] = pos_text[word]
        return clean_text, final_tagged_text

    @staticmethod
    def remove_puntuation(text):
        punctuation = {'/', '"', '(', ')', '.', ',', '%', ';', '?', '¿', '!', '¡', "'",
                       ':', '$', '&', '>', '<', '-', '_', '°', '|', '¬', '\\', '*', '+',
                       '[', ']', '{', '}', '=', '\n', '&amp', '&gt', '&lt'}
        for sign in punctuation:
            text = text.replace(sign, ' ')
        text = text.strip().replace('     ', ' ').replace('    ', ' ').replace('   ', ' ').replace('  ', ' ')
        return text
