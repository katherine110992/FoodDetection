from nltk.tag import StanfordPOSTagger
from nltk.stem.snowball import PorterStemmer
from nltk.stem.snowball import SnowballStemmer
import sklearn.feature_extraction.text
from nltk.stem import WordNetLemmatizer
from datetime import timedelta
from time import time
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
text = "no entiendo a esas mujeres que les gusta que le lleguen con flores a mi que me enamoren con comida como torta, pizza, hamburguesas etc"
# text = "Andres carne de res"
# text = "la pizza de don cangrejo es la mejor para ti y para mi"
# text = "me comi 3 pedazos con una malta con arroz"
# text = "queso con chocolate caliente."
# text = "en zamora se exhibe y comercializa desde hoy presentacion chocolate gourmet"
# text = "jajajajaja $90.000 7:00pm maldita... estas lejos, baby."
# text = "##kcacolombia https://t.co/9vgki1tgsu	apple re cago los emojis en ios10 beta 4\nhora de las noticias insolitas, mundo curioso en la papaya de oxigeno 100.4 \n#papayacuriosa"
# text = "@perezjhonatan17  no pienso discutir con alguien que no le gusta el aguacate pero si el jugo de mora y tomate, adios hombre horrible"
# text = "@Radioacktiva_ @juankiss67 Buena tarde @juankiss67 saludo desde el centro de Bogota, este integrante de la tropa te https://t.co/DrmuIKuqyS"
# text = "@ICETEX Buen dia. Cuando se realiza el desembolso del fondo para el acceso a educacion superior para victimas del conflicto armado? Gracias."
# text = "#almuerzo##dieta##comersaludable en En Algun Lugar Del Mundo https://t.co/0vTJafidwc"
# text = "tajada jajajaja #trabajosihay #lideres @xsalo_ @deportecali @shelsetatiana @d_ospina1"
text = text.lower()
print(text)
text = re.sub('(#)+', ' #', text)
print(text)
user_mentions = []
hashtags = []
characters = ["#", "@", "http"]
for character in characters:
    print(character)
    count_character = text.count(character)
    print(count_character)
    if count_character > 0:
        while count_character > 0:
            print(count_character)
            print(character)
            start = text.find(character)
            end = text.find(" ", start)
            if end == -1:
                end = len(text)
            text_to_remove = text[start:end]
            print(text.count(text_to_remove))
            print(text_to_remove)
            if character == "#":
                hashtags.append(text_to_remove)
            elif character == "@":
                user_mentions.append(text_to_remove)
            text = text.replace(text_to_remove, "")
            text = ' '.join(text.split())
            count_character = text.count(character)
text = text.strip(' ')
text = ' '.join(text.split())
print(text)
print(user_mentions)
print(hashtags)

path = food_detection_root.ROOT_DIR + os.path.sep + 'data' + os.path.sep
what_food_list_file = codecs.open(path + "list - what_food.txt", encoding='utf-8')
what_food_list = what_food_list_file.read().splitlines()
hashtags_with_what_words = []
for hashtag in hashtags:
    for word in what_food_list:
        if word in hashtag:
            print(word)
            hashtags_with_what_words.append(hashtag)
            about_food = True
            break
print(hashtags_with_what_words)
user_mentions_with_words = []
# 11.3. Look in user_mentions
for alias in user_mentions:
    for word in what_food_list:
        if word in alias:
            print(word)
            user_mentions_with_words.append(alias)
            about_food = True
print(user_mentions_with_words)


import re

punctuation = {'/', '"', '(', ')',  '%', ';', '?', '¿', '!', '¡', "'",
                           ':', '#', '$', '&', '>', '<', '-', '_', '°', '|', '¬', '\\', '*', '+',
                           '[', ']', '{', '}', '=', '\n', '&amp', '&gt', '&lt', '@'}
text = re.sub('(ja){2,}', '', text)
print(text)
tokenized_text = nltk.word_tokenize(text, "spanish")
print(tokenized_text)

start_time = time()
tagged_text = sum(spanish_pos_tagger.tag_sents([tokenized_text]), [])
processed_text = []
for s in tagged_text:
    for tag in eagles_standard:
        if s[1] in eagles_standard[tag] and tag != "puntuacion":
            processed_text.append({s[0]: tag})
print(processed_text)
execution_time = time() - start_time
print(str(timedelta(seconds=execution_time)))
print()


snowball_stemmer = SnowballStemmer("spanish")
porter_stemmer = PorterStemmer()
wordnet_lemmatizer = WordNetLemmatizer()
snowball_stemmed_list = list()
porter_stemmed_list = list()
lemmatized_list = list()
for word in tokenized_text:
    stemmed_word = snowball_stemmer.stem(word)
    snowball_stemmed_list.append(stemmed_word)
    stemmed_word = porter_stemmer.stem(word)
    porter_stemmed_list.append(stemmed_word)
    lemmatized_word = wordnet_lemmatizer.lemmatize(word)
    lemmatized_list.append(lemmatized_word)
print(snowball_stemmed_list)
print()
print(porter_stemmed_list)
print()
print(lemmatized_list)
print()
start_time = time()
tagged_text = sum(spanish_pos_tagger.tag_sents([snowball_stemmed_list]), [])
processed_text = []

for s in tagged_text:
    for tag in eagles_standard:
        if s[1] in eagles_standard[tag] and tag != "puntuacion":
            processed_text.append({s[0]: tag})
print(processed_text)
execution_time = time() - start_time
print(str(timedelta(seconds=execution_time)))
print()

start_time = time()
tagged_text = sum(spanish_pos_tagger.tag_sents([porter_stemmed_list]), [])
processed_text = []
for s in tagged_text:
    for tag in eagles_standard:
        if s[1] in eagles_standard[tag] and tag != "puntuacion":
            processed_text.append({s[0]: tag})
print(processed_text)
execution_time = time() - start_time
print(str(timedelta(seconds=execution_time)))
print()

start_time = time()
tagged_text = sum(spanish_pos_tagger.tag_sents([lemmatized_list]), [])
processed_text = []
for s in tagged_text:
    for tag in eagles_standard:
        if s[1] in eagles_standard[tag] and tag != "puntuacion":
            processed_text.append({s[0]: tag})
print(processed_text)
execution_time = time() - start_time
print(str(timedelta(seconds=execution_time)))
print()


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
print("here")
print(final_text)
"""
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

conversation_id = "198"
line = conversation_id + "  " + text
for anagram in food_anagrams:
    print(line + "  " + anagram + "  " + food_anagrams[anagram])
"""
