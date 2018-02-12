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
import spacy.lang.es.tag_map
from spacy.lang.es import Spanish


def complete_text_analysis():
    client_from = MongoClient()
    db_from = client_from["SSD"]
    coll_from = db_from["raw_data"]
    start_time = time()
    date = datetime.today().strftime("%Y_%m_%d-%H_%M_%S")
    path_to_file = date + " - CompleteTextAnalysisTest_Performance.txt"
    p_file = codecs.open(path_to_file, encoding='utf-8', mode='a')
    p_file.write(date + " Complete Text Analysis Test - Local Execution" + "\n")
    p_file.flush()
    # II. Prepare data
    p_file.write("Preparing initial data ... " + "\n")
    path_to_configuration = food_detection_root.ROOT_DIR + os.path.sep + 'configuration' + os.path.sep \
                            + 'configuration.ini'
    config = ConfigParser(interpolation=ExtendedInterpolation())
    config.read_file(codecs.open(path_to_configuration, "r", "utf8"))
    # Read emojis
    path = food_detection_root.ROOT_DIR + os.path.sep + 'data' + os.path.sep
    unicode_emoji_list_file = codecs.open(path + "list - unicode_emojis.txt", encoding='utf-8')
    emoji_list = unicode_emoji_list_file.read().splitlines()
    unicode_emoji_list_file.close()
    aux_emojis_dict = {}
    emojis_dict = {}
    for aux in emoji_list:
        aux_emoji = aux.split('\t')
        aux_emojis_dict[aux_emoji[1]] = [aux_emoji[2], aux_emoji[3]]
        emojis_dict[aux_emoji[2]] = [aux_emoji[1], aux_emoji[3]]
    sorted_aux_emojis_list = sorted(aux_emojis_dict.keys(), key=len, reverse=True)
    emojis_list = list()
    for aux_emoji in sorted_aux_emojis_list:
        emojis_list.append(aux_emojis_dict[aux_emoji][0])
    # print(emojis_list)
    # Read complementary characters
    complementary_characters_list_file = codecs.open(path + "list - complementary_characters.txt", encoding='utf-8')
    complementary_characters_list = complementary_characters_list_file.read().splitlines()
    complementary_characters_list_file.close()
    complementary_characters_dict = {}
    for aux in complementary_characters_list:
        aux_char = aux.split('\t')
        complementary_characters_dict[aux_char[2]] = [aux_char[1], aux_char[3]]
    # print(complementary_characters_dict)
    # Read emoticons
    emoticon_list_file = codecs.open(path + "list - emoticons.txt", encoding='utf-8')
    emoticon_list = emoticon_list_file.read().splitlines()
    emoticon_list_file.close()
    emoticons_dict = {}
    for aux in emoticon_list:
        aux_emoticon = aux.split('\t')
        # print(aux_emoticon)
        emoticons_dict[aux_emoticon[0]] = aux_emoticon[1]
    # print(emoticons_dict)
    # 1. Configure Google_Universal_POS_Tags
    tags = config.options("Google_Universal_POS_Tags")
    google_universal_tags = {}
    for tag in tags:
        google_universal_tags[tag.upper()] = config.get('Google_Universal_POS_Tags', tag)
    # 2. Read special characters (#, @, https, etc.)
    special_characters = ast.literal_eval(config.get('TextAnalysis', 'special_characters'))
    additional_symbols = ast.literal_eval(config.get('TextAnalysis', 'additional_symbols'))
    variation_selectors = ast.literal_eval(config.get('TextAnalysis', 'variation_selectors'))
    # 3. Configure Spanish POS tagger
    spanish_pos_tagger = spacy.load('es')
    tag_map = spacy.lang.es.TAG_MAP
    all_from_tweets = coll_from.find()
    count = 0
    stop = 10
    p_file.write("Total data to process: " + str(stop) + "\n")
    emoticons = []
    emojis = []
    complementary_characters = []
    texts = []
    emojis_count = 0
    emoticon_count = 0
    complementary_characters_count = 0
    for raw_data in all_from_tweets:
        if 'text' in raw_data:
            if "place" in raw_data.keys():
                place = raw_data["place"]
                if place is not None:
                    if "country_code" in place.keys():
                        raw_data_country_code = raw_data["place"]["country_code"]
                        if raw_data_country_code in ["CO"]:
                            lang = raw_data["lang"]
                            text = raw_data['text']
                            if lang == 'es':
                                results = identify_special_characters(text, spanish_pos_tagger, tag_map, emoticons_dict,
                                                                      emojis_dict, emojis_list, variation_selectors,
                                                                      complementary_characters_dict, emoticon_count,
                                                                      emojis_count, complementary_characters_count)

                                spaced_text = results[0]
                                final_clean_text = results[1]
                                emoticons += copy.deepcopy(results[2])
                                emojis += copy.deepcopy(results[3])
                                complementary_characters += copy.deepcopy(results[4])
                                emoticon_count = results[5]
                                emojis_count = results[6]
                                complementary_characters_count = results[7]
                                if len(results[2]) != 0 or len(results[3]) != 0 or len(results[4]) != 0:
                                    texts.append(spaced_text + '\t' + final_clean_text)
                                count += 1
                            else:
                                if len(text) >= 3:
                                    blob = TextBlob(text)
                                    detected_language = blob.detect_language()
                                    if detected_language == 'es':
                                        results = identify_special_characters(text, spanish_pos_tagger, tag_map,
                                                                              emoticons_dict,
                                                                              emojis_dict, emojis_list,
                                                                              variation_selectors,
                                                                              complementary_characters_dict,
                                                                              emoticon_count,
                                                                              emojis_count,
                                                                              complementary_characters_count)

                                        spaced_text = results[0]
                                        final_clean_text = results[1]
                                        emoticons += copy.deepcopy(results[2])
                                        emojis += copy.deepcopy(results[3])
                                        complementary_characters += copy.deepcopy(results[4])
                                        emoticon_count = results[5]
                                        emojis_count = results[6]
                                        complementary_characters_count = results[7]
                                        if len(results[2]) != 0 or len(results[3]) != 0 or len(results[4]) != 0:
                                            texts.append(spaced_text + '\t' + final_clean_text)
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
    p_file.write("Emojis " + str(len(emojis)) + "\n")
    emojis_counter = Counter(emojis).most_common()
    emojis_counter_sorted = sorted(emojis_counter, key=lambda tup: tup[1])
    for emoji in emojis_counter_sorted:
        p_file.write(str(emoji[0]) + "\t" + str(emoji[1]) + "\n")
    p_file.write("Total Emojis: " + str(emojis_count) + ". Proportion: " + str(emojis_count / stop) + "\n")
    p_file.write("Complementary Characters " + str(len(complementary_characters)) + "\n")
    cc_counter = Counter(complementary_characters).most_common()
    cc_counter_sorted = sorted(cc_counter, key=lambda tup: tup[1])
    for cc in cc_counter_sorted:
        p_file.write(str(cc[0]) + "\t" + str(cc[1]) + "\n")
    p_file.write("Total Complementary Characters: " + str(complementary_characters_count)
                 + ". Proportion: " + str(complementary_characters_count / stop) + "\n")
    p_file.write("Texts with: " + "\n")
    for text in texts:
        p_file.write(text + "\n")
    p_file.write("Total elements in new list: " + str(count) + "\n")
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
            # print('replace html symbol', html_symbol)
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
        # pos_morph = tag_map[initial_morph]
        pos = tag.pos_
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
                    # Identify emojis
                    emoji_in = False
                    no_emoji_text = tag_text
                    complete_tag_text = tag_text
                    for emoji in emojis_list:
                        emoji_count = complete_tag_text.count(emoji)
                        if emoji_count > 0:
                            emojis_count += 1
                            while emoji_count > 0:
                                sp_name = 'special_character_' + str(sp_counter)
                                emojis.append(emojis_dict[emoji][1])
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
                                emoji_count = complete_tag_text.count(emoji)
                                sp_counter += 1
                    if emoji_in:
                        final_clean_text += no_emoji_text + ' '
                    # Identify complementary characters
                    complementary_characters_in = False
                    no_complementary_characters_text = tag_text
                    for c_c in complementary_characters_dict.keys():
                        c_c_count = complete_tag_text.count(c_c)
                        if c_c_count > 0:
                            # print('get in complementary_characters')
                            complementary_characters_count += 1
                            while c_c_count > 0:
                                sp_name = 'special_character_' + str(sp_counter)
                                complementary_characters.append(complementary_characters_dict[c_c][1])
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
                                c_c_count = complete_tag_text.count(c_c)
                                sp_counter += 1
                    if complementary_characters_in:
                        final_clean_text += no_complementary_characters_text + ' '
                    if not emoji_in and not complementary_characters_in:
                        final_clean_text += complete_tag_text + ' '

    final_clean_text = delete_spaces(final_clean_text)
    spaced_text = final_clean_text
    for sp in sp_text:
        spaced_text = spaced_text.replace(sp, sp_text[sp]['token'])
    # print(text)
    # print(spaced_text)
    # print(final_clean_text)
    # print(sp_text)
    return spaced_text, final_clean_text, emoticons, emojis, complementary_characters, emoticon_count, emojis_count, \
           complementary_characters_count


def identify_emoticons(sp_counter, text, clean_text, sp_text, emoticons_dict, global_emoticon_count):
    emoticons = []
    numbers = list(range(0, 9))
    new_emoticon = ''
    for emoticon in emoticons_dict.keys():
        original_emoticon = emoticon
        for number in numbers:
            if str(number) in emoticon:
                new_emoticon = ' ' + emoticon + ' '
                break
            else:
                new_emoticon = emoticon
        emoticon_count = clean_text.count(new_emoticon)
        if emoticon_count > 0:
            # print("identify emoticon", new_emoticon)
            global_emoticon_count += 1
            while emoticon_count > 0:
                sp_name = 'special_character_' + str(sp_counter)
                emoticons.append(original_emoticon)
                clean_text = clean_text.replace(emoticon, ' ' + sp_name + ' ')
                sp_text[sp_name] = {
                    'token': original_emoticon,
                    'type': 'emoticon',
                    'pos': emoticons_dict[original_emoticon],
                    'morph': 'emoticon'
                }
                emoticon_count = clean_text.count(new_emoticon)
                sp_counter += 1
    for sp in sp_text:
        token = sp_text[sp]['token']
        if sp_text[sp]['type'] == 'emoticon':
            token = ' ' + token + ' '
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


complete_text_analysis()
