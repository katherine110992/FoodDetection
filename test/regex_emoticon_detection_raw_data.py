from pymongo import MongoClient
from datetime import timedelta, datetime
from collections import Counter
from time import time
import food_detection_root
import os
from configparser import ConfigParser, ExtendedInterpolation
import codecs
import spacy
from spacymoji import Emoji
from textblob import TextBlob
import ast
import copy
import re


def simple_identification():
    client_from = MongoClient()
    db_from = client_from["SSD"]
    coll_from = db_from["raw_data"]
    start_time = time()
    date = datetime.today().strftime("%Y_%m_%d-%H_%M_%S")
    path_to_file = date + " - DetectRegexEmoticonsRawData_Performance.txt"
    p_file = codecs.open(path_to_file, encoding='utf-8', mode='a')
    p_file.write(date + " Detecting Emoticons with Regex Expression Test - Local Execution" + "\n")
    p_file.flush()
    # II. Prepare data
    p_file.write("Preparing initial data ... " + "\n")
    path_to_configuration = food_detection_root.ROOT_DIR + os.path.sep + 'configuration' + os.path.sep \
                            + 'configuration.ini'
    config = ConfigParser(interpolation=ExtendedInterpolation())
    config.read_file(codecs.open(path_to_configuration, "r", "utf8"))
    # print(emoticons_dict)
    # 3. Configure Spanish POS tagger
    spanish_pipeline = spacy.load('es')
    emoji = Emoji(spanish_pipeline)
    spanish_pipeline.add_pipe(emoji, first=True)
    all_from_tweets = coll_from.find()
    count = 0
    stop = 1000
    p_file.write("Total data to process: " + str(stop) + "\n")
    emoticons = []
    emoticon_pattern = r"([:;=]-?([\)D\(\C\co]+|[xX][dD]+))|([:<][3])|(<\\3)|()"
    emoticons_characters = ['X', 'x', 'd', 'D', ')', '(', ':', ';', '\'', '*', '=', '/', '$', '#', '-', 'C', 'c', '<', '3', '0', 'O', 'o']
    texts = []
    no_texts = []
    emoticon_count = 0
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
                            raw_entities = raw_data['entities']
                            if lang == 'es':
                                results = identify_emoticons(text, raw_entities, spanish_pipeline, emoticon_count,
                                                             emoticon_pattern, emoticons_characters)
                                text = results[0]
                                clean_text = results[1]
                                emoticon_count = results[2]
                                special_entities = results[3]
                                emoticons += copy.deepcopy(results[4])
                                if len(results[4]) != 0:
                                    texts.append(text + '\t' + clean_text + '\t' + str(special_entities))
                                else:
                                    no_texts.append(text + '\t' + clean_text)
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
                                        results = identify_emoticons(text, raw_entities, spanish_pipeline,
                                                                     emoticon_count,
                                                                     emoticon_pattern, emoticons_characters)
                                        text = results[0]
                                        clean_text = results[1]
                                        emoticon_count = results[2]
                                        special_entities = results[3]
                                        emoticons += copy.deepcopy(results[4])
                                        if len(results[4]) != 0:
                                            texts.append(text + '\t' + clean_text + '\t' + str(special_entities))
                                        else:
                                            no_texts.append(text + '\t' + clean_text)
                                        count += 1
                            print(count)
                            if count == stop:
                                break
    all_from_tweets.close()
    client_from.close()
    p_file.write("Emoticons " + str(len(emoticons)) + "\n")
    emoticons_counter = Counter(emoticons).most_common()
    emoticons_counter_sorted = sorted(emoticons_counter, key=lambda tup: tup[1])
    for emoticon in emoticons_counter_sorted:
        p_file.write(str(emoticon[0]) + "\t" + str(emoticon[1]) + "\n")
    p_file.write("Total Emoticons: " + str(emoticon_count) + ". Proportion: " + str(emoticon_count / stop) + "\n")
    p_file.write("TEXTS WITH EMOTICONS: \n")
    for text in texts:
        p_file.write(text + "\n")
    p_file.write("TEXTS WITHOUT EMOTICONS: \n")
    for text in no_texts:
        p_file.write(text + "\n")
    p_file.write("Total elements in new list: " + str(count) + "\n")
    execution_time = time() - start_time
    p_file.write("Execution time: " + str(timedelta(seconds=execution_time)) + "\n")
    p_file.flush()
    p_file.close()


def identify_emoticons(text, raw_entities, spanish_pipeline, emoticon_count, emoticon_pattern, emoticons_characters,
                       faces_pattern, faces_characters):
    special_entities = {}
    sp_id = 0
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
    # Remove special entities
    # entity_type: url and removal from text
    clean_text = text
    urls = raw_entities["urls"]
    if len(urls) != 0:
        for url in urls:
            sp_name = 'special_entity_' + str(sp_id)
            token = url['url']
            special_entities[token] = {
                'token': sp_name,
                'type': 'special_character',
                'pos': 'url',
                'morph': 'http'
            }
            clean_text = clean_text.replace(token, "")
            sp_id += 1
    # Identify additional urls
    sp_id, clean_text, aux_sp_text = identify_first_special_characters(clean_text, sp_id, spanish_pipeline, ['http'])
    for sp_name in aux_sp_text:
        special_entities[sp_name] = aux_sp_text[sp_name]
    # entity_type: hashtag and removal from text
    hashtags = raw_entities["hashtags"]
    if len(hashtags) != 0:
        for hashtag in hashtags:
            sp_name = 'special_entity_' + str(sp_id)
            token = '#' + hashtag['text']
            special_entities[token] = {
                'token': sp_name,
                'type': 'special_character',
                'pos': 'hashtag',
                'morph': '#'
            }
            clean_text = clean_text.replace(token, "")
            sp_id += 1
    # entity_type: user_mention and removal from text
    user_mentions = raw_entities['user_mentions']
    if len(user_mentions) != 0:
        for user_mention in user_mentions:
            sp_name = 'special_entity_' + str(sp_id)
            token = '@' + user_mention["screen_name"]
            special_entities[token] = {
                'token': sp_name,
                'type': 'special_character',
                'pos': 'user_mention',
                'morph': '@'
            }
            clean_text = clean_text.replace(token, "")
            sp_id += 1

    # doc = spanish_pipeline(service_text)

    simple_tokens = clean_text.split(' ')

    final_text = ''
    final_tokens = []
    final_emoticons = []

    for token in simple_tokens:
        matches = re.finditer(emoticon_pattern, token)
        is_emoticon = True
        emoticons = list()
        for char in token:
            if char not in emoticons_characters:
                # is not a emoticon
                is_emoticon = False
                break
        if is_emoticon:
            for matchNum, match in enumerate(matches):
                emoticon_count += 1
                matchNum += 1
                if match.group().upper() in special_entities.keys():
                    final_em = special_entities[match.group().upper()]['token']
                else:
                    final_em = 'special_entity_' + str(sp_id)
                    sp_id += 1
                final_emoticons.append(match.group().upper())
                final_text += final_em + ' '
                final_tokens.append(final_em)
                special_entities[match.group().upper()] = {
                    'token': final_em,
                    'tag_type': 'emoticon',
                    'morph': 'Polarity=1',
                    'pos': ''
                }
        else:
            # Try to look up for a suffix
            for matchNum, match in enumerate(matches):
                if token.endswith(match.group()):
                    print("it is a suffix emoticon", token)
                    is_emoticon = True
                    emoticon_count += 1
                    matches = re.finditer(emoticon_pattern, token)
                    clean_token = token
                    for matchNum, match in enumerate(matches):
                        matchNum += 1
                        emoticons.append(match.group().upper())
                        final_emoticons.append(match.group().upper())
                        if matchNum == 1:
                            clean_token = clean_token[0:match.start()]
                            final_tokens.append(clean_token)
                        print(clean_token)
                    clean_token += ' '
                    for emoticon in emoticons:
                        if emoticon in special_entities.keys():
                            final_em = special_entities[match.group()]['token']
                        else:
                            final_em = 'special_entity_' + str(sp_id)
                            sp_id += 1
                        final_text += final_em + ' '
                        final_tokens.append(final_em)
                        special_entities[emoticon] = {
                            'token': final_em,
                            'tag_type': 'emoticon',
                            'morph': 'Polarity=1',
                            'pos': ''
                        }
                    final_text += ' ' + clean_token
                    sp_id += 1
                    break
                else:
                    is_emoticon = False
            if not is_emoticon:
                clean_text += token + ' '
                final_tokens.append(token)
    for e in final_tokens:
        print(e)
    return text, final_text, emoticon_count, special_entities, final_emoticons


def identify_first_special_characters(text, sp_id, spanish_pos_tagger, first_special_characters):
    raw_tagged_text = spanish_pos_tagger(text)
    sp_text = {}
    clean_text = text
    for tag in raw_tagged_text:
        for sp in first_special_characters:
            if sp in tag.text:
                # print("identify sp", tag.text)
                sp_name = 'special_character_' + str(sp_id)
                clean_text = clean_text.replace(tag.text, sp_name)
                sp_text[tag.text] = {
                    'token': sp_name,
                    'type': 'special_character',
                    'pos': 'url',
                    'morph': sp
                }
                sp_id += 1
    # for sp in sp_text:
    #     text = text.replace(sp, sp_text[sp]['token'])
    return sp_id, clean_text, sp_text


def delete_spaces(text):
    text = text.strip(' ')
    text = ' '.join(text.split())
    return text


simple_identification()
