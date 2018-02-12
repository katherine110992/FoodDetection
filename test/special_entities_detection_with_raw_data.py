from pymongo import MongoClient
from datetime import timedelta, datetime
from collections import Counter
from time import time
import food_detection_root
import os
from configparser import ConfigParser, ExtendedInterpolation
import codecs
import spacy
from textblob import TextBlob
import copy
import re
import ast
from spacy.lang.es import Spanish


def simple_identification():
    client_from = MongoClient()
    db_from = client_from["SSD"]
    coll_from = db_from["raw_data"]
    start_time = time()
    date = datetime.today().strftime("%Y_%m_%d-%H_%M_%S")
    path_to_file = date + " - DetectRegexSpecialEntitiesRawData_Performance.txt"
    p_file = codecs.open(path_to_file, encoding='utf-8', mode='w')
    p_file.write(date + " Detecting Special Entities with Regex Expression Test - Local Execution" + "\n")
    p_file.flush()
    # II. Prepare data
    p_file.write("Preparing initial data ... " + "\n")
    path_to_configuration = food_detection_root.ROOT_DIR + os.path.sep + 'configuration' + os.path.sep \
                            + 'configuration.ini'
    config = ConfigParser(interpolation=ExtendedInterpolation())
    config.read_file(codecs.open(path_to_configuration, "r", "utf8"))
    # print(emoticons_dict)
    # 3. Configure Spanish POS tagger
    spanish_pipeline = Spanish()
    all_from_tweets = coll_from.find()
    count = 0
    stop = 100
    p_file.write("Total data to process: " + str(stop) + "\n")
    emoticons = []
    text_type = 'Twitter'
    emotions = ast.literal_eval(config.get(text_type, 'emotions'))
    emoticons_metadata = ast.literal_eval(config.get(text_type, 'emoticons_metadata'))
    emotions_polarity = ast.literal_eval(config.get(text_type, 'emotions_polarity'))
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
                            original_text = raw_data['text']
                            raw_entities = raw_data['entities']
                            original_text = original_text.replace('\n', ' ')
                            if lang == 'es':
                                results = identify_special_entities(original_text, raw_entities, spanish_pipeline,
                                                                    emoticon_count, emotions, emoticons_metadata,
                                                                    emotions_polarity)
                                text = results[0]
                                clean_text = results[1]
                                emoticon_count = results[2]
                                special_entities = results[3]
                                emoticons += copy.deepcopy(results[4])
                                if len(results[4]) != 0:
                                    texts.append(original_text + '\t' + text + '\t' + clean_text + '\t' + str(special_entities))
                                else:
                                    no_texts.append(original_text + '\t' + text + '\t' + clean_text)
                                count += 1
                            else:
                                if len(original_text) >= 3:
                                    blob = TextBlob(original_text)
                                    detection = True
                                    detected_language = ''
                                    while detection:
                                        try:
                                            detected_language = blob.detect_language()
                                            detection = False
                                        except:
                                            print('error while getting detected language')
                                    # print(detected_language)
                                    if detected_language == 'es':
                                        results = identify_special_entities(original_text, raw_entities, spanish_pipeline,
                                                                            emoticon_count, emotions, emoticons_metadata,
                                                                            emotions_polarity)
                                        text = results[0]
                                        clean_text = results[1]
                                        emoticon_count = results[2]
                                        special_entities = results[3]
                                        emoticons += copy.deepcopy(results[4])
                                        if len(results[4]) != 0:
                                            texts.append(original_text + '\t' + text + '\t' + clean_text + '\t' +
                                                         str(special_entities))
                                        else:
                                            no_texts.append(original_text + '\t' + text + '\t' + clean_text)
                                        count += 1
                            print(count)
                            print(emoticon_count)
                            if emoticon_count >= stop:
                                break
    all_from_tweets.close()
    client_from.close()
    p_file.write("Emoticons " + str(len(emoticons)) + "\n")
    emoticons_counter = Counter(emoticons).most_common()
    emoticons_counter_sorted = sorted(emoticons_counter, key=lambda tup: tup[1])
    for emoticon in emoticons_counter_sorted:
        p_file.write(str(emoticon[0]) + "\t" + str(emoticon[1]) + "\n")
    p_file.write("Total Emoticons: " + str(emoticon_count) + ". Total data: " + str(count) +
                 ". Proportion: " + str(emoticon_count / count) + "\n")
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


def identify_special_entities(text, raw_entities, spanish_pipeline, emoticon_count, emotions, emoticons_metadata,
                              emotions_polarity):
    print('get in')
    special_entities = {}
    ordered_special_entities = []
    simple_special_entities = {}
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
    punctuation_pattern = r"[\.,\?¿!¡]+"
    matches = re.match(punctuation_pattern, text)
    if matches:
        matches = re.finditer(punctuation_pattern, text)
        for matchNum, match in enumerate(matches):
            # detect intensifier
            sequence_detected = match.group()
            text = text.replace(sequence_detected, ' ' + sequence_detected + ' ')
    # Remove special entities
    # entity_type: url and removal from text
    clean_text = text
    urls = raw_entities["urls"]
    if len(urls) != 0:
        for url in urls:
            sp_name = 'special_entity_' + str(sp_id)
            ordered_special_entities.append(sp_name)
            token = url['url']
            simple_special_entities[sp_name] = token
            special_entities[sp_name] = {
                'token': token,
                'tag_type': 'url',
                'stem': token
            }
            clean_text = clean_text.replace(token, sp_name)
            sp_id += 1
    # Identify additional urls
    sp_id, clean_text, aux_sp_text, ordered_special_entities = identify_first_special_characters(clean_text, sp_id,
                                                               spanish_pipeline, ['http'], ordered_special_entities,
                                                               simple_special_entities)
    for sp_name in aux_sp_text:
        special_entities[sp_name] = aux_sp_text[sp_name]
        simple_special_entities[sp_name] = aux_sp_text[sp_name]['token']
    # entity_type: hashtag and removal from text
    hashtags = raw_entities["hashtags"]
    if len(hashtags) != 0:
        for hashtag in hashtags:
            sp_name = 'special_entity_' + str(sp_id)
            ordered_special_entities.append(sp_name)
            token = '#' + hashtag['text']
            simple_special_entities[sp_name] = token
            special_entities[sp_name] = {
                'token': token,
                'tag_type': 'hashtag',
                'stem': hashtag['text']
            }
            clean_text = clean_text.replace(token, sp_name)
            sp_id += 1
    # entity_type: user_mention and removal from text
    user_mentions = raw_entities['user_mentions']
    if len(user_mentions) != 0:
        for user_mention in user_mentions:
            sp_name = 'special_entity_' + str(sp_id)
            ordered_special_entities.append(sp_name)
            token = '@' + user_mention["screen_name"]
            simple_special_entities[sp_name] = token
            special_entities[sp_name] = {
                'token': token,
                'tag_type': 'user_mention',
                'stem': user_mention["screen_name"]
            }
            clean_text = clean_text.replace(token, sp_name)
            sp_id += 1
    print(clean_text)
    aux_clean_text = ''
    token_text = spanish_pipeline(clean_text)
    for tag in token_text:
        aux_clean_text += tag.text + ' '
    aux_clean_text = delete_spaces(aux_clean_text)
    print(aux_clean_text)
    return identify_emoticons(clean_text, sp_id, ordered_special_entities, special_entities,
                              simple_special_entities, emotions, emoticons_metadata, emotions_polarity, emoticon_count)


def identify_first_special_characters(text, sp_id, spanish_pos_tagger, first_special_characters,
                                      ordered_special_entities, simple_special_entities):
    raw_tagged_text = spanish_pos_tagger(text)
    sp_text = {}
    clean_text = text
    for tag in raw_tagged_text:
        for sp in first_special_characters:
            if sp in tag.text:
                # print("identify sp", tag.text)
                sp_name = 'special_character_' + str(sp_id)
                clean_text = clean_text.replace(tag.text, sp_name)
                sp_text[sp_name] = {
                    'token': tag.text,
                    'tag_type': 'url',
                    'stem': tag.text
                }
                sp_id += 1
                ordered_special_entities.append(sp_name)
                simple_special_entities[sp_name] = tag.text
    # for sp in sp_text:
    #     text = text.replace(sp, sp_text[sp]['token'])
    return sp_id, clean_text, sp_text, ordered_special_entities


def identify_emoticons(final_text, sp_id, ordered_special_entities, special_entities, simple_special_entities,
                       emotions, emoticons_metadata, emotions_polarity, emoticon_count):
    clean_text = ''
    final_emoticons = []
    text = ''
    for pattern_type in emoticons_metadata:
        emotions = emoticons_metadata[pattern_type]
        for emotion in emotions:
            pattern = emotions[emotion]['pattern']
            character = emotions[emotion]['characters']
            final_text = delete_spaces(final_text)
            simple_tokens = final_text.split(' ')
            print(final_text)
            print(simple_tokens)
            for token in simple_tokens:
                if token not in simple_special_entities.keys():
                    it_matches = True
                    matches = re.match(pattern, token)
                    emoticons = list()
                    if matches:
                        for char in token:
                            if char not in character:
                                # is not a emoticon
                                matches = False
                                break
                    if matches:
                        matches = re.finditer(pattern, token)
                        for matchNum, match in enumerate(matches):
                            # detect intensifier
                            sequence_detected = emoticon = match.group().upper()
                            if pattern_type != 'faces':
                                last_character = sequence_detected[len(sequence_detected) - 1]
                                before_last_character = sequence_detected[len(sequence_detected) - 2]
                                if last_character == before_last_character:
                                    # there is an intensifier
                                    intensifier = sequence_detected.count(last_character)
                                    detected_emoticon = sequence_detected.replace(last_character * intensifier, last_character)
                                else:
                                    intensifier = 1
                                    detected_emoticon = sequence_detected
                            else:
                                intensifier = 1
                                detected_emoticon = sequence_detected
                            entity_found = False
                            for entity in special_entities:
                                if emoticon == special_entities[entity]['token']:
                                    final_em = entity
                                    entity_found = True
                                    break
                            if not entity_found:
                                final_em = 'special_entity_' + str(sp_id)
                                sp_id += 1
                                simple_special_entities[final_em] = emoticon
                            # print(final_em)
                            clean_text += final_em + ' '
                            ordered_special_entities.append(final_em)
                            special_entities[final_em] = {
                                'token': emoticon,
                                'tag_type': 'emoticon',
                                'stem': detected_emoticon,
                                'pos': final_em,
                                'morph': {
                                    'intensifier': intensifier,
                                    'polarity': emotions_polarity[emotion]
                                }
                            }
                            special_entities[final_em]['morph'][emotion] = 1
                    else:
                        matches = re.finditer(pattern, token)
                        for matchNum, match in enumerate(matches):
                            if token.endswith(match.group()):
                                # print(token + ' has a suffix')
                                it_matches = True
                                matches = re.finditer(pattern, token)
                                clean_token = token
                                for matchNum, match in enumerate(matches):
                                    # matches = re.finditer(emoticon_pattern, token)
                                    matchNum += 1
                                    emoticons.append(match.group().upper())
                                    if matchNum == 1:
                                        clean_token = clean_token[0:match.start()]
                                        # print(clean_token)
                                clean_token += ' '
                                # print(emoticons)
                                for emoticon in emoticons:
                                    sequence_detected = emoticon
                                    if pattern_type != 'faces':
                                        last_character = sequence_detected[len(sequence_detected) - 1]
                                        before_last_character = sequence_detected[len(sequence_detected) - 2]
                                        if last_character == before_last_character:
                                            # there is an intensifier
                                            intensifier = sequence_detected.count(last_character)
                                            detected_emoticon = sequence_detected.replace(last_character * intensifier,
                                                                                          last_character)
                                        else:
                                            intensifier = 1
                                            detected_emoticon = sequence_detected
                                    else:
                                        intensifier = 1
                                        detected_emoticon = sequence_detected
                                    entity_found = False
                                    for entity in special_entities:
                                        if emoticon == special_entities[entity]['token']:
                                            final_em = entity
                                            entity_found = True
                                            break
                                    if not entity_found:
                                        final_em = 'special_entity_' + str(sp_id)
                                        sp_id += 1
                                        simple_special_entities[final_em] = emoticon
                                    # print(final_em)
                                    clean_token += final_em + ' '
                                    ordered_special_entities.append(final_em)
                                    special_entities[final_em] = {
                                        'token': emoticon,
                                        'tag_type': 'emoticon',
                                        'stem': detected_emoticon,
                                        'pos': final_em,
                                        'morph': {
                                            'intensifier': intensifier,
                                            'polarity': emotions_polarity[emotion]
                                        }
                                    }
                                    special_entities[final_em]['morph'][emotion] = 1
                                clean_text += ' ' + clean_token
                                break
                        else:
                            it_matches = False
                    if not it_matches:
                        # print(token + ' does not match the emoticon pattern')
                        clean_text += token + ' '
                else:
                    clean_text += token + ' '
            final_text = clean_text
            text = clean_text
            clean_text = ''
    # hacer la cuenta al final... contar cuantas veces esta special_entity en clean_text y actualizar la cuenta en el
    # resultado final. En el mismo se puede hacer el conteo del número de emoticones.
    f_text = text
    for sp_name in special_entities.keys():
        token = special_entities[sp_name]['token']
        f_text = f_text.replace(sp_name, token)
        token_count = text.count(sp_name)
        special_entities[sp_name]['count'] = token_count
        if special_entities[sp_name]['tag_type'] == 'emoticon':
            intensifier = special_entities[sp_name]['morph']['intensifier']
            emoticon_count += token_count*intensifier
            for i in range(0, token_count*intensifier):
                final_emoticons.append(special_entities[sp_name]['stem'])
    print('get out')
    print(text)
    print(f_text)
    print(special_entities)
    return text, f_text, emoticon_count, special_entities, final_emoticons


def delete_spaces(text):
    text = text.strip(' ')
    text = ' '.join(text.split())
    return text

simple_identification()
