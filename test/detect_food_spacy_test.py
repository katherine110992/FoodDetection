from nltk.stem.snowball import SnowballStemmer
import sklearn.feature_extraction.text
from datetime import timedelta, datetime
import unicodedata
from time import time
import food_detection_root
from configparser import ConfigParser, ExtendedInterpolation
import ast
import os
from nltk.corpus import stopwords
import codecs
import spacy
import re


def detect_food(text):
    # I. Create performance file
    start_time = time()
    date = datetime.today().strftime("%Y_%m_%d-%H_%M_%S")
    path_to_file = date + " - DetectFoodWithSpacyTest_Performance.txt"
    p_file = open(path_to_file, 'a')
    p_file.write(date + " Detect Food With spaCy POS Singular Test - Local Execution" + "\n")
    p_file.flush()
    # II. Prepare data
    p_file.write("Preparing initial data ... " + "\n")
    path_to_configuration = food_detection_root.ROOT_DIR + os.path.sep + 'configuration' + os.path.sep \
                            + 'configuration.ini'
    config = ConfigParser(interpolation=ExtendedInterpolation())
    config.read_file(codecs.open(path_to_configuration, "r", "utf8"))
    # 1. Configure Google_Universal_POS_Tags
    tags = config.options("Google_Universal_POS_Tags")
    google_universal_tags = {}
    for tag in tags:
        google_universal_tags[tag.upper()] = config.get('Google_Universal_POS_Tags', tag)
    # 2. Read special characters (#, @, https, etc.)
    special_characters = ast.literal_eval(config.get('TextAnalysis', 'special_characters'))
    additional_symbols = ast.literal_eval(config.get('TextAnalysis', 'additional_symbols'))
    # 3. Configure Spanish POS tagger
    spanish_pos_tagger = spacy.load('es')
    tag_map = spacy.es.TAG_MAP
    # 4. Configure Snowball Stemmer
    snowball_stemmer = SnowballStemmer("spanish")
    path = food_detection_root.ROOT_DIR + os.path.sep + 'data' + os.path.sep
    # 5. Initiate final data
    what_words = set()
    hashtags_with_what_words = []
    user_mentions_with_words = []
    food_n_grams_with_stopwords = {}
    food_n_grams = {}
    # 6. Read list
    what_food_list_file = codecs.open(path + "list - original_stemmed_what_food.txt", encoding='utf-8')
    what_food_list = what_food_list_file.read().splitlines()
    what_food_list_file.close()
    what_food = {}
    for line in what_food_list:
        data = line.split("\t")
        stem = data[1]
        word = data[0]
        what_food[word] = stem
    not_wanted_pos = ast.literal_eval(config.get('TextAnalysis', 'not_wanted_pos'))
    # III. TEXT ANALYSIS
    p_file.write("Analyzing text ... " + "\n")
    # 1. Text to lower
    text = text.lower()
    # 2. Proper encoding
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore')
    text = text.decode("utf-8")
    # -. Remove patterns - Not for the final script
    pattern_free_text = re.sub('(ja){2,}', '', text)
    pattern_free_text = re.sub('(ha){2,}', '', pattern_free_text)
    # 3. Identify and remove #, @, urls from text
    results = get_hashtags_and_user_mentions(special_characters, pattern_free_text)
    clean_text = results['clean_text']
    hashtags_about_food = results['#']
    user_mentions_about_food = results['@']
    # 4. POS - Tokenize - Stopwords - Stemming
    pos_results = part_of_speech(spanish_pos_tagger, tag_map, google_universal_tags, clean_text, snowball_stemmer)
    tokenized_text_with_stopwords = pos_results[0]
    tokenized_text = pos_results[1]
    full_tagged_text = pos_results[2]
    tagged_text_with_stopwords = pos_results[3]
    tagged_text = pos_results[4]
    stemmed_text = pos_results[5]
    spaced_text_with_stopwords = pos_results[6]
    spaced_text = pos_results[7]
    clean_text_no_spaces = pos_results[8]
    # 5. Detect Food in Hashtags
    i = 0
    while len(hashtags_about_food) > i >= 0:
        hashtag = hashtags_about_food[i]
        removed = False
        for word in what_food.keys():
            if word in hashtag:
                what_words.add(word)
                hashtags_with_what_words.append(hashtag)
                hashtags_about_food.remove(hashtag)
                removed = True
                break
        if not removed:
            i += 1
    # 6. Detect Food in User Mentions
    while len(user_mentions_about_food) > i >= 0:
        alias = user_mentions_about_food[i]
        removed = False
        for word in what_food.keys():
            if word in alias:
                what_words.add(word)
                user_mentions_with_words.append(alias)
                user_mentions_about_food.remove(alias)
                removed = True
                break
        if not removed:
            i += 1
    # 7. Detect Food in text
    new_what_words = []
    detected_what_food = {}
    for i in range(0, len(stemmed_text)):
        stem = stemmed_text[i]
        if stem in what_food.values():
            word = tokenized_text[i]
            if word in what_food.keys():
                what_words.add(word)
                detected_what_food[word] = stem
            else:
                # Check if the word is plural
                word_morph = tagged_text[word]['morph']
                if 'Plur' in word_morph:
                    for aux_word, aux_stem in what_food.items():
                        if aux_stem == stem and aux_word in word:
                            what_words.add(aux_word)
                            detected_what_food[aux_word] = aux_stem
                            break
                else:
                    new_what_words.append({word: stem})
    print(detected_what_food)
    if len(detected_what_food) != 0 and len(tagged_text_with_stopwords) > 1:
        # 8.1. Create n-grams with stop_words
        final_n_grams = create_n_grams(spaced_text_with_stopwords, tagged_text_with_stopwords)
        # 8.1.1 Detect Food in n-grams
        for n_gram in final_n_grams:
            n_gram_stems = final_n_grams[n_gram]['stem'].split(" ")
            for stem in n_gram_stems:
                if stem in detected_what_food.values():
                    food_n_grams_with_stopwords[n_gram] = {
                        'pos': final_n_grams[n_gram]['pos'],
                        'stem': final_n_grams[n_gram]['stem'],
                        'length': final_n_grams[n_gram]['length']
                    }
        # 8.2. Create n-grams with stop_words
        no_stopwords_n_grams = create_n_grams(spaced_text, tagged_text)
        # 8.2.1. Detect Food in no stopwords n-grams
        for n_gram in no_stopwords_n_grams:
            n_gram_stems = no_stopwords_n_grams[n_gram]['stem'].split(" ")
            for stem in n_gram_stems:
                if stem in detected_what_food.values():
                    food_n_grams[n_gram] = {
                        'pos': no_stopwords_n_grams[n_gram]['pos'],
                        'stem': no_stopwords_n_grams[n_gram]['stem'],
                        'length': no_stopwords_n_grams[n_gram]['length']
                    }
    # IV. Write results
    p_file.write("##################  RESULTS  ##################\n")
    if len(what_words) != 0:
        p_file.write("-> TEXT ABOUT FOOD: \n")
        p_file.write("12356 - " + clean_text_no_spaces + "\n")
        p_file.write("-> WHAT WORDS: \n")
        for word in what_words:
            p_file.write(word + "\n")
        p_file.write("-> FOOD N-GRAMS: \n")
        for n_gram in food_n_grams_with_stopwords:
            p_file.write("12356 - " + clean_text_no_spaces + " - WithStopWords - " + spaced_text_with_stopwords + " - "
                         + n_gram + " - " + food_n_grams_with_stopwords[n_gram]['stem'] + " - " + food_n_grams_with_stopwords[n_gram]['pos']
                         + " - " + str(food_n_grams_with_stopwords[n_gram]['length']) + "\n")
        for n_gram in food_n_grams:
            p_file.write("12356 - " + clean_text_no_spaces + " - NoStopWords - " + spaced_text + " - "
                         + n_gram + " - " + food_n_grams[n_gram]['stem'] + " - "
                         + food_n_grams[n_gram]['pos'] + " - "
                         + str(food_n_grams[n_gram]['length']) + "\n")
        if len(hashtags_with_what_words) != 0:
            p_file.write("-> HASHTAGS WITH FOOD WORDS: \n")
            for hashtag in hashtags_with_what_words:
                p_file.write(hashtag + "\n")
        if len(user_mentions_with_words) != 0:
            p_file.write("-> USER MENTIONS WITH FOOD WORDS: \n")
            for alias in user_mentions_with_words:
                p_file.write(alias + "\n")
        if len(hashtags_about_food) != 0:
            p_file.write("-> HASHTAGS ABOUT FOOD: \n")
            for hashtag in hashtags_about_food:
                p_file.write(hashtag + "\n")
        if len(user_mentions_about_food) != 0:
            p_file.write("-> USER MENTIONS ABOUT FOOD: \n")
            for alias in user_mentions_about_food:
                p_file.write(alias + "\n")
    else:
        p_file.write("-> TEXT NOT ABOUT FOOD: \n")
        p_file.write("12356 - " + clean_text_no_spaces + "\n")
    execution_time = time() - start_time
    p_file.write("Execution time: " + str(timedelta(seconds=execution_time)) + "\n")
    p_file.flush()


def get_hashtags_and_user_mentions(special_characters, text, wanted_characters=['#', '@']):
    # Identify hashtags, user mentions and remove urls
    results = {}
    for character in special_characters:
        text = re.sub('(' + character + ')+', ' ' + character, text)
        count_character = text.count(character)
        if count_character > 0:
            while count_character > 0:
                start = text.find(character)
                print(text.find(" ", start))
                print(text.find("\n", start))
                if text.find(" ", start) <= text.find("\n", start):
                    end = text.find(" ", start)
                else:
                    end = text.find("\n", start)
                if end == -1:
                    end = len(text)
                text_to_remove = text[start:end]
                print(text_to_remove)
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


def part_of_speech(spanish_pos_tagger, tag_map, google_universal_tags, clean_text, snowball_stemmer):
    additional_symbols = {'/', '%', '#', '$', '&', '>', '<', '-', '_', '°', '|', '¬', '\\',
                          '*', '+', '=', '&amp', '&gt', '&lt'}
    raw_tagged_text = spanish_pos_tagger(clean_text)
    complete_tagged_text = []
    tagged_text = {}
    no_stopwords_tagged_text = {}
    tokenized_text = []
    no_stopwords_tokenized_text = []
    stemmed_text = []
    spaced_text = ""
    no_stopwords_spaced_text = ""
    clean_text_no_spaces = ""
    not_wanted_pos = {
        'puntuación': 'punctuation',
        'numérico': 'numeral',
        'símbolo': 'symbol',
        'otro': 'other'
    }
    for tag in raw_tagged_text:
        initial_morph = tag.tag_
        pos_morph = tag_map[initial_morph]
        pos = google_universal_tags[pos_morph['pos']]
        if pos != 'espacio':
            if pos == 'puntuación':
                clean_text_no_spaces = clean_text_no_spaces[0:len(clean_text_no_spaces) - 1] + tag.text + " "
            else:
                clean_text_no_spaces += tag.text + " "
            if pos not in not_wanted_pos.keys():
                if tag.text not in additional_symbols:
                    stemmed_word = snowball_stemmer.stem(tag.text)
                    if tag.text not in stopwords.words("spanish"):
                        tag_type = "word"
                        no_stopwords_tagged_text[tag.text] = {
                            'pos': pos,
                            'stem': stemmed_word,
                            'morph': pos_morph['morph']
                        }
                        no_stopwords_tokenized_text.append(tag.text)
                        no_stopwords_spaced_text += tag.text + " "
                        stemmed_text.append(stemmed_word)
                    else:
                        tag_type = "stop_word"
                    tagged_text[tag.text] = {
                            'pos': pos,
                            'stem': stemmed_word,
                            'morph': pos_morph['morph']
                    }
                    tokenized_text.append(tag.text)
                    spaced_text += tag.text + " "
                else:
                    tag_type = "symbol"
                    pos = "símbolo"
            else:
                tag_type = not_wanted_pos[pos]
            final_tag = {
                'token': tag.text,
                'pos': pos,
                'morph': pos_morph['morph'],
                'type': tag_type
            }
            complete_tagged_text.append({tag.text: final_tag})
    print(complete_tagged_text)
    return tokenized_text, no_stopwords_tokenized_text, complete_tagged_text, tagged_text, no_stopwords_tagged_text,\
           stemmed_text, spaced_text[0:len(spaced_text) - 1], no_stopwords_spaced_text[0:len(no_stopwords_spaced_text) - 1],\
           clean_text_no_spaces


def create_n_grams(text, tagged_text):
    text_vect = sklearn.feature_extraction.text.CountVectorizer(ngram_range=(2, 3), strip_accents='unicode',
                                                                tokenizer=lambda x: x.split(' '))
    text_vect.fit([text])
    final_n_grams = {}
    text_n_grams = text_vect.get_feature_names()
    for n_gram in text_n_grams:
        words = n_gram.split(" ")
        pos = ""
        stem = ""
        for word in words:
            pos += tagged_text[word]['pos'] + "+"
            stem += tagged_text[word]['stem'] + " "
        final_n_grams[n_gram] = {
            'pos': pos[0:len(pos) - 1],
            'stem': stem[0:len(stem) - 1],
            'length': len(words)
        }
    return final_n_grams

text = "me gusta mucho el red bull"
text = "no entiendo a esas mujeres que les gusta que le lleguen con flores a mi que me enamoren con comida como torta, pizza, hamburguesas, filetes, filet, etc"
# text = "Andres carne de res"
# text = "la pizza de don cangrejo es la mejor para ti y para mi"
# text = "me comi 3 pedazos con una malta con arroz"
# text = "queso con chocolate caliente y unas empanaditas y también un crème brûlée"
# text = "en zamora se exhibe y comercializa desde hoy presentacion chocolate gourmet@clairewingrove\ntostadas me gustan un monton"
# text = "jajajajaja $90.000 7:00pm maldita... estas lejos, baby."
# text = "##kcacolombia https://t.co/9vgki1tgsu	apple re cago los emojis en ios10 beta 4\nhora de las noticias insolitas, mundo curioso en la papaya de oxigeno 100.4 \n#papayacuriosa"
# text = "@perezjhonatan17  no pienso discutir con alguien que no le gusta el aguacate pero si el jugo de mora y tomate, adios hombre horrible"
# text = "@Radioacktiva_ @juankiss67 Buena tarde @juankiss67 saludo desde el centro de Bogota, este integrante de la tropa te https://t.co/DrmuIKuqyS"
# text = "sal de aquí por favor"
# text = "@ICETEX Buen dia. Cuando se realiza el desembolso del fondo para el acceso a educacion superior para victimas del conflicto armado? Gracias."
# text = "#almuerzo##dieta##comersaludable en En Algun Lugar Del Mundo https://t.co/0vTJafidwc"
# text = "tajada jajajaja #trabajosihay #lideres @xsalo_ @deportecali @shelsetatiana @d_ospina1"
# text = "@villalobossebas hoy es el cumple de @shelsetatiana no olvides felicitarla"
# text = "me tocara almorzar mil de salchichon con dos mil de pan y cafe porque no hay pa mas jovenes, no hay pa mas :( 😐"
text = "nadie acompana a gratis, todo lo de el es mermelada $$$$"
detect_food(text)
