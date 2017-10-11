from nltk.tag import StanfordPOSTagger
from nltk.stem.snowball import PorterStemmer
import sklearn.feature_extraction.text
import nltk
import food_detection_root
import configparser
import ast
import os
from nltk.corpus import stopwords
import codecs
import re


path_to_configuration = food_detection_root.ROOT_DIR + os.path.sep + 'configuration' + os.path.sep \
                                + 'configuration.ini'
config = configparser.ConfigParser()
config.read(path_to_configuration)
os.environ['JAVAHOME'] = config.get('Paths', 'JAVA_HOME')
model_path = food_detection_root.ROOT_DIR + os.path.sep + 'text_analysis' + os.path.sep + 'models'\
             + os.path.sep + 'spanish.tagger'
tagger_path = food_detection_root.ROOT_DIR + os.path.sep + 'text_analysis' + os.path.sep + 'tagger'\
             + os.path.sep + 'stanford-postagger.jar'
spanish_pos_tagger = StanfordPOSTagger(model_path, tagger_path)
tags = config.options("EAGLES_Standard")
eagles_standard = {}
for tag in tags:
    eagles_standard[tag] = ast.literal_eval(config.get('EAGLES_Standard', tag))

# text = "me gusta mucho el red bull"
# text = "no entiendo a esas mujeres que les gusta que le lleguen con flores a mi que me enamoren con comida como torta, pizza, hamburguesas etc"
# text = "Andres carne de res"
# text = "la pizza de don cangrejo es la mejor para ti y para mi"
# text = "me comi 3 pedazos con una malta con arroz"
# text = "queso con chocolate caliente."
# text = "en zamora se exhibe y comercializa desde hoy presentacion chocolate gourmet"

text = "jajajajaja $90.000 7:00pm maldita... estas lejos, baby."
import re
text = re.sub('(.:00)', '', text)

punctuation = {'/', '"', '(', ')', '.', ',', '%', ';', '?', '¿', '!', '¡', "'",
                           ':', '#', '$', '&', '>', '<', '-', '_', '°', '|', '¬', '\\', '*', '+',
                           '[', ']', '{', '}', '=', '\n', '&amp', '&gt', '&lt', '@'}
text = re.sub('(ja)+', '', text)
print(text)
tokenized_text = nltk.word_tokenize(text, "spanish")
print(tokenized_text)

stemmer = PorterStemmer()
stemmed_list = list()
for word in tokenized_text:
    stemmed_word = stemmer.stem(word)
    stemmed_list.append(stemmed_word)
print(stemmed_list)

tagged_text = sum(spanish_pos_tagger.tag_sents([stemmed_list]), [])
processed_text = []

for s in tagged_text:
    for tag in eagles_standard:
        if s[1] in eagles_standard[tag] and tag != "puntuacion":
            processed_text.append({s[0]: tag})
print(processed_text)

wanted_prepositions = ["de", "con"]

final_text = []
final_tagged_text = {}
for pos_text in processed_text:
    for word in pos_text:
        if word in wanted_prepositions:
            final_text.append(word)
            final_tagged_text[word] = pos_text[word]
        else:
            if word not in stopwords.words("spanish"):
                final_text.append(word)
                final_tagged_text[word] = pos_text[word]
print(final_tagged_text)
print(final_text)

path = food_detection_root.ROOT_DIR + os.path.sep + 'data' + os.path.sep
what_food_list_file = codecs.open(path + "list - stemmed_what_food.txt", encoding='utf-8')
what_food_list = what_food_list_file.read().splitlines()

text = ' '.join(final_text)
print(text)

# crear anagramas
text_vect = sklearn.feature_extraction.text.CountVectorizer(ngram_range=(2, 3), strip_accents='unicode',
                                                            tokenizer=lambda x: x.split(' '))
text_vect.fit([text])
final_anagrams = {}
text_anagrams = text_vect.get_feature_names()
for anagram in text_anagrams:
    words = anagram.split(" ")
    pos = ""
    for word in words:
        pos += final_tagged_text[word] + "+"
    final_anagrams[anagram] = pos[0:len(pos)-1]

print(final_anagrams)

food_anagrams = {}

for anagram in final_anagrams:
    anagram_words = anagram.split(" ")
    for word in anagram_words:
        if word in what_food_list:
            food_anagrams[anagram] = final_anagrams[anagram]

print(food_anagrams)

conversation_id = "12345"
line = conversation_id + "\t" + text
for anagram in food_anagrams:
    print(line + "\t" + anagram + "\t" + food_anagrams[anagram])