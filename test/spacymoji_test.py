from pymongo import MongoClient
from datetime import timedelta, datetime
from time import time
import food_detection_root
import os
from configparser import ConfigParser, ExtendedInterpolation
import codecs
import spacy
import spacy.es
from spacymoji import Emoji
from textblob import TextBlob


def simple_identification():
    client_from = MongoClient()
    db_from = client_from["SSD"]
    coll_from = db_from["raw_data"]
    start_time = time()
    date = datetime.today().strftime("%Y_%m_%d-%H_%M_%S")
    path_to_file = date + " - DetectEmojisWithSpacymoji_Performance.txt"
    p_file = codecs.open(path_to_file, encoding='utf-8', mode='a')
    p_file.write(date + " Detecting Emojis with Spacymoji Test - Local Execution" + "\n")
    p_file.flush()
    # II. Prepare data
    p_file.write("Preparing initial data ... " + "\n")
    path_to_configuration = food_detection_root.ROOT_DIR + os.path.sep + 'configuration' + os.path.sep \
                            + 'configuration.ini'
    config = ConfigParser(interpolation=ExtendedInterpolation())
    config.read_file(codecs.open(path_to_configuration, "r", "utf8"))
    path = food_detection_root.ROOT_DIR + os.path.sep + 'data' + os.path.sep
    # Read complementary characters
    complementary_characters_list_file = codecs.open(path + "list - complementary_characters.txt", encoding='utf-8')
    complementary_characters_list = complementary_characters_list_file.read().splitlines()
    complementary_characters_list_file.close()
    complementary_characters_dict = {}
    for aux in complementary_characters_list:
        aux_char = aux.split('\t')
        complementary_characters_dict[aux_char[2]] = [aux_char[1], aux_char[3]]
    # print(complementary_characters_dict)
    # 3. Configure Spanish POS tagger
    spanish_pipeline = spacy.load('es')
    emoji = Emoji(spanish_pipeline)
    spanish_pipeline.add_pipe(emoji, first=True)
    tag_map = spacy.es.TAG_MAP
    # start
    all_from_tweets = coll_from.find()
    count = 0
    stop = 1000
    p_file.write("Total data to process: " + str(stop) + "\n")
    for raw_data in all_from_tweets:
        if 'text' in raw_data.keys() and 'lang' in raw_data.keys():
            if "place" in raw_data.keys():
                place = raw_data["place"]
                if place is not None:
                    if "country_code" in place.keys():
                        raw_data_country_code = raw_data["place"]["country_code"]
                        if raw_data_country_code in ["CO"]:
                            lang = raw_data["lang"]
                            text = raw_data['text']
                            if lang == 'es':
                                identify_special_characters(text, spanish_pipeline, tag_map, p_file)
                                count += 1
                            else:
                                if len(text) >= 3:
                                    blob = TextBlob(text)
                                    detection = True
                                    detected_language = ''
                                    while detection:
                                        try:
                                            detected_language = blob.detect_language()
                                            detection = False
                                        except:
                                            print('error while getting detected language')
                                    if detected_language == 'es':
                                        identify_special_characters(text, spanish_pipeline, tag_map, p_file)
                                        count += 1
                            print(count)
                            if count == stop:
                                break
    all_from_tweets.close()
    client_from.close()
    p_file.write("Total elements in new list: " + str(count) + "\n")
    execution_time = time() - start_time
    p_file.write("Execution time: " + str(timedelta(seconds=execution_time)) + "\n")
    p_file.flush()
    p_file.close()


def identify_special_characters(text, spanish_pipeline, tag_map, p_file):
    # 1. Parse html symbols
    html_symbols = {'&lt;': '<',
                    '&gt;': '>',
                    '&amp;': '&',
                    '&quot;': '"',
                    '&nbsp;': ' ',
                    '&apos;': '\''}
    for html_symbol in html_symbols:
        if html_symbol in text:
            text = text.replace(html_symbol, html_symbols[html_symbol])
    # 5. POS - Tokenize
    p_file.write(text + '\n')
    p_file.flush()
    doc = spanish_pipeline(text)
    if doc._.has_emoji:
        print('It has emoji', text)
        for token in doc:
            if token._.is_emoji is True:
                print(token.pos_, token._.emoji_desc)
                text = text.replace(token.text, 'emoji')
        print('Clean text', text)
    else:
        print('It does not have')


def test():
    import spacy
    from spacymoji import Emoji

    nlp = spacy.load('es')
    emoji = Emoji(nlp)
    nlp.add_pipe(emoji, first=True)

    doc = nlp(u"This is a test 😻 👍🏿")
    assert doc._.has_emoji == True
    assert doc[2:5]._.has_emoji == True
    assert doc[0]._.is_emoji == False
    assert doc[4]._.is_emoji == True
    assert doc[5]._.emoji_desc == u'thumbs up dark skin tone'
    assert len(doc._.emoji) == 2
    assert doc._.emoji[1] == (u'👍🏿', 5, u'thumbs up dark skin tone')

# test()
simple_identification()
