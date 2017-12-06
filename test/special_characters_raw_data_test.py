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
import ast
import copy
import re


def simple_identification():
    client_from = MongoClient()
    db_from = client_from["SSD"]
    coll_from = db_from["raw_data"]
    start_time = time()
    date = datetime.today().strftime("%Y_%m_%d-%H_%M_%S")
    path_to_file = date + " - DetectSpecialCharacters_Performance.txt"
    p_file = codecs.open(path_to_file, encoding='utf-8', mode='a')
    p_file.write(date + " Detecting Special Characters Test - Local Execution" + "\n")
    p_file.flush()
    # II. Prepare data
    p_file.write("Preparing initial data ... " + "\n")
    path_to_configuration = food_detection_root.ROOT_DIR + os.path.sep + 'configuration' + os.path.sep \
                            + 'configuration.ini'
    config = ConfigParser(interpolation=ExtendedInterpolation())
    config.read_file(codecs.open(path_to_configuration, "r", "utf8"))
    all_from_tweets = coll_from.find()
    count = 0
    stop = 1000
    p_file.write("Total data to process: " + str(stop) + "\n")
    texts = {}
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
                            service_text = text
                            if 'entities' in raw_data.keys():
                                count += 1
                                entities = []
                                # entity_type: symbol
                                for symbol in raw_data['entities']['symbols']:
                                    symbol_entity = {
                                        "entity_type": "symbol",
                                        "entity": symbol['text']
                                    }
                                    entities.append(symbol_entity)
                                # entity_type: url and removal from text
                                urls = raw_data["entities"]["urls"]
                                for url in urls:
                                    url_entity = {
                                        "entity_type": "url",
                                        "entity": url['url']
                                    }
                                    entities.append(url_entity)
                                    service_text = service_text.replace(url["url"], "")
                                # entity_type: hashtag and removal from text
                                hashtags = raw_data["entities"]["hashtags"]
                                for hashtag in hashtags:
                                    hashtag_entity = {
                                        "entity_type": "hashtag",
                                        "entity": hashtag['text']
                                    }
                                    entities.append(hashtag_entity)
                                    service_text = service_text.replace(hashtag["text"], "")
                                    service_text = service_text.replace("#", "")
                                # entity_type: user_mention and removal from text
                                user_mentions = raw_data['entities']['user_mentions']
                                for user_mention in user_mentions:
                                    user_mention_entity = {
                                        "entity_type": "user_mention",
                                        "entity": user_mention['screen_name']
                                    }
                                    entities.append(user_mention_entity)
                                    service_text = service_text.replace(user_mention["screen_name"], "")
                                    service_text = service_text.replace("@", "")
                                texts[text] = [service_text, entities, raw_data['entities']]
                            print(count)
                            if count == stop:
                                break
    all_from_tweets.close()
    client_from.close()
    p_file.write("Texts with entities: " + "\n")
    for text in texts:
        p_file.write(text + "\n" + str(texts[text][0]) + "\n" + str(texts[text][1]) + "\n" + str(texts[text][2]) + "\n")
    p_file.write("Total raw data: " + str(count) + "\n")
    execution_time = time() - start_time
    p_file.write("Execution time: " + str(timedelta(seconds=execution_time)) + "\n")
    p_file.flush()
    p_file.close()


def identify_special_characters(text, spanish_pos_tagger, tag_map, emoticons_dict, emojis_dict, emojis_list,
                                variation_selectors, complementary_characters_dict, emoticon_count, emojis_count,
                                complementary_characters_count):
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
    # 2. Delete multiple sequential special characters
    first_special_characters = {
        'http': 'url'
    }
    for character in first_special_characters.keys():
        text = re.sub('(' + character + ')+', ' ' + character, text)
    second_special_characters = {
        '@': 'user_mention',
        '#': 'hashtag'
    }
    for character in second_special_characters.keys():
        text = re.sub('(' + character + ')+', ' ' + character, text)
    # 3. Identify urls
    sp_counter, text, clean_text, sp_text = identify_first_special_characters(text, spanish_pos_tagger,
                                                                              first_special_characters)
    # 4. Identify emoticons
    sp_counter, text, clean_text, sp_text, emoticons, emoticon_count = identify_emoticons(sp_counter, text, clean_text,
                                                                                          sp_text, emoticons_dict,
                                                                                          emoticon_count)
    # 5. POS - Tokenize
    raw_tagged_text = spanish_pos_tagger(clean_text)
    sc_detected = False
    sc_text = ''
    final_clean_text = ''
    emojis = []
    complementary_characters = []
    p_detected = False
    p_side = ''
    symbol_count = 0
    for tag in raw_tagged_text:
        # check for variation selectors
        tag_text = tag.text
        for variation_selector in variation_selectors:
            if variation_selector in tag_text:
                # print('find variation_selector on ', tag_text)
                tag_text = tag_text.replace(variation_selector, '')
                # print(tag_text)
        general_sc_detected = False
        initial_morph = tag.tag_
        pos_morph = tag_map[initial_morph]
        pos = pos_morph['pos']
        for sp in second_special_characters:
            if sp in tag_text:
                general_sc_detected = True
                if len(tag_text) != 1:
                    sp_name = 'special_character_' + str(sp_counter)
                    final_clean_text += sp_name + ' '
                    sp_text[sp_name] = {
                        'token': tag_text,
                        'type': 'special_character',
                        'pos': second_special_characters[sp],
                        'morph': sp
                    }
                    sp_counter += 1
                else:
                    sc_detected = True
                    sc_text = tag_text
        if not general_sc_detected:
            if sc_detected:
                sp_name = 'special_character_' + str(sp_counter)
                complete_tag_text = sc_text + tag_text
                final_clean_text += sp_name + ' '
                sp_text[sp_name] = {
                    'token': complete_tag_text,
                    'type': 'special_character',
                    'pos': second_special_characters[sc_text],
                    'morph': sc_text
                }
                sc_detected = False
                sc_text = ''
                sp_counter += 1
            else:
                if pos != 'SP' and pos != 'SPACE':
                    emoji_in = False
                    no_emoji_text = tag_text
                    complete_tag_text = tag_text
                    for emoji in emojis_list:
                        emoji_count = complete_tag_text.count(emoji)
                        if emoji_count > 0:
                            emojis_count += 1
                            sp_name = 'special_character_' + str(sp_counter)
                            complete_tag_text = complete_tag_text.replace(emoji, ' ' + emojis_dict[emoji][0] + ' ')
                            # print(tag_text)
                            no_emoji_text = no_emoji_text.replace(emoji, ' ' + sp_name + ' ')
                            # print(no_emoji_text)
                            sp_text[sp_name] = {
                                'token': emojis_dict[emoji][0],
                                'type': 'emoji',
                                'pos': emojis_dict[emoji][1],
                                'morph': 'emoji'
                            }
                            emoji_in = True
                            sp_counter += 1
                            while emoji_count > 0:
                                emojis.append(emojis_dict[emoji][1])
                                emoji_count -= 1
                    if emoji_in:
                        final_clean_text += no_emoji_text + ' '
                    complementary_characters_in = False
                    no_complementary_characters_text = tag_text
                    for c_c in complementary_characters_dict.keys():
                        c_c_count = complete_tag_text.count(c_c)
                        if c_c_count > 0:
                            # print('get in complementary_characters')
                            complementary_characters_count += 1
                            sp_name = 'special_character_' + str(sp_counter)
                            complete_tag_text = complete_tag_text.replace(c_c, ' ' +
                                                                          complementary_characters_dict[c_c][0]
                                                                          + ' ')
                            # print(tag_text)
                            no_complementary_characters_text = no_complementary_characters_text.replace(c_c, ' ' + sp_name + ' ')
                            # print(no_emoji_text)
                            sp_text[sp_name] = {
                                'token': complementary_characters_dict[c_c][0],
                                'type': 'complementary_character',
                                'pos': complementary_characters_dict[c_c][1],
                                'morph': '-'
                            }
                            complementary_characters_in = True
                            sp_counter += 1
                            while c_c_count > 0:
                                complementary_characters.append(complementary_characters_dict[c_c][1])
                                c_c_count -= 1
                    if complementary_characters_in:
                        final_clean_text += no_complementary_characters_text + ' '
                    if not emoji_in and not complementary_characters_in:
                        if pos == 'PUNCT':
                            final_clean_text = final_clean_text[0:len(final_clean_text) - 1] + tag_text + " "
                            p_side = pos_morph['morph']
                        else:
                            if 'PunctSide=Ini' in p_side:
                                final_clean_text = final_clean_text[0:len(final_clean_text) - 1] + complete_tag_text + " "
                            else:
                                final_clean_text += complete_tag_text + ' '
                            p_side = ''

    final_clean_text = delete_spaces(final_clean_text)
    spaced_text = final_clean_text
    for sp in sp_text:
        spaced_text = spaced_text.replace(sp, sp_text[sp]['token'])
    # print(text)
    # print(spaced_text)
    print(final_clean_text)
    # print(sp_text)
    return spaced_text, final_clean_text, emoticons, emojis, complementary_characters, emoticon_count, emojis_count, \
           complementary_characters_count


def identify_emoticons(sp_counter, text, clean_text, sp_text, emoticons_dict, global_emoticon_count):
    emoticons = []
    numbers = list(range(0, 9))
    # print(numbers)
    new_emoticon = ''
    for emoticon in emoticons_dict.keys():
        original_emoticon = emoticon
        for number in numbers:
            if str(number) in emoticon:
                new_emoticon = emoticon + ' '
                break
            else:
                new_emoticon = emoticon
        # print(new_emoticon)
        emoticon_count = clean_text.count(new_emoticon)
        if emoticon_count > 0:
            # print("identify emoticon", new_emoticon)
            global_emoticon_count += 1
            sp_name = 'special_character_' + str(sp_counter)
            clean_text = clean_text.replace(emoticon, ' ' + sp_name + ' ')
            sp_text[sp_name] = {
                'token': original_emoticon,
                'type': 'emoticon',
                'pos': emoticons_dict[original_emoticon],
                'morph': 'emoticon'
            }
            sp_counter += 1
            while emoticon_count > 0:
                emoticons.append(original_emoticon)
                emoticon_count -= 1
    for sp in sp_text:
        token = sp_text[sp]['token']
        if sp_text[sp]['type'] == 'emoticon':
            token += ' '
        text = text.replace(sp, token)
    text = delete_spaces(text)
    clean_text = delete_spaces(clean_text)
    return sp_counter, text, clean_text, sp_text, emoticons, global_emoticon_count


def identify_first_special_characters(text, spanish_pos_tagger, first_special_characters):
    sp_counter = 1
    raw_tagged_text = spanish_pos_tagger(text)
    sp_text = {}
    clean_text = text
    for tag in raw_tagged_text:
        for sp in first_special_characters:
            if sp in tag.text:
                # print("identify sp", tag.text)
                sp_name = 'special_character_' + str(sp_counter)
                clean_text = clean_text.replace(tag.text, sp_name)
                sp_text[sp_name] = {
                    'token': tag.text,
                    'type': 'special_character',
                    'pos': first_special_characters[sp],
                    'morph': sp
                }
                sp_counter += 1
    for sp in sp_text:
        text = text.replace(sp, sp_text[sp]['token'])
    return sp_counter, text, clean_text, sp_text


def delete_spaces(text):
    text = text.strip(' ')
    text = ' '.join(text.split())
    return text


simple_identification()
