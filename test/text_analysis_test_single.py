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


def complete_text_analysis(text, raw_entities):
    start_time = time()
    date = datetime.today().strftime("%Y_%m_%d-%H_%M_%S")
    path_to_file = date + " - SingleCompleteTextAnalysis_Performance.txt"
    p_file = codecs.open(path_to_file, encoding='utf-8', mode='a')
    p_file.write(date + " Single Complete Text Analysis Test - Local Execution" + "\n")
    p_file.flush()
    # II. Prepare data
    p_file.write("Preparing initial data ... " + "\n")
    path_to_configuration = food_detection_root.ROOT_DIR + os.path.sep + 'configuration' + os.path.sep \
                            + 'configuration.ini'
    config = ConfigParser(interpolation=ExtendedInterpolation())
    config.read_file(codecs.open(path_to_configuration, "r", "utf8"))
    # 01. Read emojis
    path = food_detection_root.ROOT_DIR + os.path.sep + 'data' + os.path.sep
    unicode_emoji_list_file = codecs.open(path + "list - unicode_emojis_metadata.txt", encoding='utf-8')
    emoji_list = unicode_emoji_list_file.read().splitlines()
    unicode_emoji_list_file.close()
    aux_emojis_dict = {}
    emojis_dict = {}
    for aux in emoji_list:
        aux_emoji = aux.split('\t')
        aux_emojis_dict[aux_emoji[1]] = [aux_emoji[2], aux_emoji[3]]
        emojis_dict[aux_emoji[2]] = {
            'emoji_id': aux_emoji[0],
            'unicode': aux_emoji[1],
            'name': aux_emoji[3],
            'polarity': float(aux_emoji[4]),
            'happiness': float(aux_emoji[5]),
            'anger': float(aux_emoji[6]),
            'fear': float(aux_emoji[7]),
            'replusion': float(aux_emoji[8]),
            'surprise': float(aux_emoji[9]),
            'sadness': float(aux_emoji[10]),
            'interest': aux_emoji[11]
        }
    sorted_aux_emojis_list = sorted(aux_emojis_dict.keys(), key=len, reverse=True)
    emojis_list = list()
    for aux_emoji in sorted_aux_emojis_list:
        emojis_list.append(aux_emojis_dict[aux_emoji][0])
    # print(emojis_list)
    # 02. Read complementary characters
    complementary_characters_list_file = codecs.open(path + "list - complementary_characters.txt", encoding='utf-8')
    complementary_characters_list = complementary_characters_list_file.read().splitlines()
    complementary_characters_list_file.close()
    complementary_characters_dict = {}
    for aux in complementary_characters_list:
        aux_char = aux.split('\t')
        complementary_characters_dict[aux_char[2]] = [aux_char[1], aux_char[3]]
    # print(complementary_characters_dict)
    # 03. Read emoticons patterns
    text_type = 'Twitter'
    emotions = ast.literal_eval(config.get(text_type, 'emotions'))
    emoticons_metadata = ast.literal_eval(config.get(text_type, 'emoticons_metadata'))
    emotions_polarity = ast.literal_eval(config.get(text_type, 'emotions_polarity'))
    # 04. Configure Google_Universal_POS_Tags
    tags = config.options("Google_Universal_POS_Tags")
    google_universal_tags = {}
    for tag in tags:
        google_universal_tags[tag.upper()] = config.get('Google_Universal_POS_Tags', tag)
    # 05. Read special characters (#, @, https, etc.)
    special_characters = ast.literal_eval(config.get('TextAnalysis', 'special_characters'))
    additional_symbols = ast.literal_eval(config.get('TextAnalysis', 'additional_symbols'))
    variation_selectors = ast.literal_eval(config.get('TextAnalysis', 'variation_selectors'))
    # 06. Configure Spanish POS tagger
    nlp = Spanish()
    tag_map = spacy.lang.es.TAG_MAP
    emoticons = []
    emojis = []
    complementary_characters = []
    texts = []
    emojis_count = 0
    emoticon_count = 0
    complementary_characters_count = 0
    original_text = text.replace('\n', ' ')
    results = identify_special_characters(original_text, raw_entities, nlp,
                                          tag_map, emotions, emoticons_metadata,
                                          emotions_polarity, emojis_dict, emojis_list,
                                          variation_selectors, complementary_characters_dict,
                                          emoticon_count, emojis_count,
                                          complementary_characters_count)

    spaced_text = results[0]
    final_clean_text = results[1]
    emoticons += copy.deepcopy(results[2])
    emojis += copy.deepcopy(results[3])
    complementary_characters += copy.deepcopy(results[4])
    emoticon_count = results[5]
    emojis_count = results[6]
    complementary_characters_count = results[7]
    special_entities = results[8]
    execution_time = time() - start_time
    p_file.write("Execution time: " + str(timedelta(seconds=execution_time)) + "\n")
    texts.append(spaced_text + '\t' + final_clean_text + '\t' + str(special_entities))
    p_file.write("Texts with: " + "\n")
    for text in texts:
        p_file.write(text + "\n")
    p_file.flush()
    p_file.close()


def identify_special_characters(text, raw_entities, nlp, tag_map, emotions, emoticons_metadata,
                                emotions_polarity, emojis_dict, emojis_list, variation_selectors,
                                complementary_characters_dict, emoticon_count, emojis_count,
                                complementary_characters_count):
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
                                                                                                 nlp,
                                                                                                 ['http'],
                                                                                                 ordered_special_entities,
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
            indices = user_mention['indices']
            sp_name = 'special_entity_' + str(sp_id)
            ordered_special_entities.append(sp_name)
            token = clean_text[indices[0]:indices[1]]
            simple_special_entities[sp_name] = token
            special_entities[sp_name] = {
                'token': token,
                'tag_type': 'user_mention',
                'stem': user_mention["screen_name"]
            }
            clean_text = clean_text.replace(token, sp_name)
            sp_id += 1
    aux_text = clean_text
    i = len(ordered_special_entities) - 1
    while i >= 0:
        entity_id = ordered_special_entities[i]
        entity_token = special_entities[entity_id]['token']
        aux_text = aux_text.replace(entity_id, entity_token)
        i -= 1

    # Emoticons: Moment 1
    final_emoticons = list()
    for pattern_type in emoticons_metadata:
        emotions = emoticons_metadata[pattern_type]
        for emotion in emotions:
            pattern = emotions[emotion]['pattern']
            if 1 in emotions[emotion]['time']:
                matches = re.search(pattern, clean_text)
                if matches:
                    matches = re.finditer(pattern, clean_text)
                    for matchNum, match in enumerate(matches):
                        # detect intensifier
                        detected_emoticon = match.group()
                        intensifier = 1
                        entity_found = False
                        for entity in special_entities:
                            if detected_emoticon == special_entities[entity]['token']:
                                final_em = entity
                                entity_found = True
                                break
                        if not entity_found:
                            final_em = 'special_entity_' + str(sp_id)
                            sp_id += 1
                            simple_special_entities[final_em] = detected_emoticon
                        # print(final_em)
                        ordered_special_entities.append(final_em)
                        special_entities[final_em] = {
                            'token': detected_emoticon,
                            'tag_type': 'emoticon',
                            'stem': detected_emoticon.upper(),
                            'pos': final_em,
                            'morph': {
                                'intensifier': intensifier,
                                'polarity': emotions_polarity[emotion]
                            }
                        }
                        special_entities[final_em]['morph'][emotion] = 1
                        clean_text = clean_text.replace(detected_emoticon, ' ' + final_em + ' ')

    clean_text = delete_spaces(clean_text)
    raw_tagged_text = clean_text.split(' ')
    aux_clean_text = ''
    for token in raw_tagged_text:
        aux_clean_text += token + ' '
    aux_clean_text = delete_spaces(aux_clean_text)
    # Emoticons: Moment 2
    sp_id, clean_text, final_text, emoticon_count, special_entities, final_emoticons = identify_emoticons(
        aux_clean_text,
        sp_id, ordered_special_entities,
        special_entities,
        simple_special_entities,
        emotions,
        emoticons_metadata,
        emotions_polarity,
        emoticon_count, final_emoticons, 2)

    clean_text = delete_spaces(clean_text)
    print(clean_text)
    raw_tagged_text = clean_text.split(' ')
    print('after moment 2 ', raw_tagged_text)
    # 5. Identify emojis and complementary
    final_clean_text = ''
    emojis = []
    complementary_characters = []
    symbol_count = 0
    for tag_text in raw_tagged_text:
        if 'special_entity' not in tag_text:
            # initial_morph = tag.tag_
            # pos_morph = tag_map[initial_morph]
            # Identify emojis
            # check for variation selectors
            for variation_selector in variation_selectors:
                if variation_selector in tag_text:
                    # print('find variation_selector on ', tag_text)
                    tag_text = tag_text.replace(variation_selector, '')
                    # print('new tag_text', tag_text)
            emoji_in = False
            no_emoji_text = tag_text
            complete_tag_text = tag_text
            for emoji in emojis_list:
                emoji_count = complete_tag_text.count(emoji)
                if emoji_count > 0:
                    # print('emoji find: ', emojis_dict[emoji]['name'])
                    emojis_count += 1
                    while emoji_count > 0:
                        sp_name = 'special_character_' + str(sp_id)
                        emojis.append(emojis_dict[emoji]['name'])
                        complete_tag_text = complete_tag_text.replace(emoji, ' ' + emojis_dict[emoji]['unicode'] + ' ')
                        # print(tag_text)
                        no_emoji_text = no_emoji_text.replace(emoji, ' ' + sp_name + ' ')
                        # print(no_emoji_text)
                        special_entities[sp_name] = {
                            'token': emojis_dict[emoji]['unicode'],
                            'tag_type': 'emoji',
                            'stem': emojis_dict[emoji]['name'],
                            'pos': sp_name,
                            'morph': emojis_dict[emoji]
                        }
                        emoji_in = True
                        emoji_count = complete_tag_text.count(emoji)
                        sp_id += 1
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
                        sp_name = 'special_character_' + str(sp_id)
                        complementary_characters.append(complementary_characters_dict[c_c][1])
                        complete_tag_text = complete_tag_text.replace(c_c, ' ' +
                                                                      complementary_characters_dict[c_c][0]
                                                                      + ' ')
                        # print(tag_text)
                        no_complementary_characters_text = no_complementary_characters_text.replace(c_c, ' ' + sp_name + ' ')
                        # print(no_emoji_text)
                        special_entities[sp_name] = {
                            'token': complementary_characters_dict[c_c][0],
                            'tag_type': 'complementary_character',
                            'pos': complementary_characters_dict[c_c][1],
                            'morph': '-'
                        }
                        complementary_characters_in = True
                        c_c_count = complete_tag_text.count(c_c)
                        sp_id += 1
            if complementary_characters_in:
                final_clean_text += no_complementary_characters_text + ' '
            if not emoji_in and not complementary_characters_in:
                final_clean_text += complete_tag_text + ' '
        else:
            final_clean_text += tag_text + ' '

    print(final_clean_text)
    aux_clean_text = ''
    token_text = nlp(final_clean_text)
    for tag in token_text:
        aux_clean_text += tag.text + ' '
    aux_clean_text = delete_spaces(aux_clean_text)
    print(aux_clean_text)
    # 4. Identify emoticons
    sp_id, clean_text, final_text, emoticon_count, special_entities, final_emoticons = identify_emoticons(
                                                                                    aux_clean_text,
                                                                                    sp_id, ordered_special_entities,
                                                                                    special_entities,
                                                                                    simple_special_entities,
                                                                                    emotions,
                                                                                    emoticons_metadata,
                                                                                    emotions_polarity,
                                                                                    emoticon_count, final_emoticons, 3)
    print(clean_text)
    print(final_text)
    print(special_entities)
    spaced_text = delete_spaces(clean_text)
    for sp_name in special_entities.keys():
        token = special_entities[sp_name]['token']
        token_count = spaced_text.count(sp_name)
        spaced_text = spaced_text.replace(sp_name, token)
        special_entities[sp_name]['count'] = token_count
        if special_entities[sp_name]['tag_type'] == 'emoticon':
            intensifier = special_entities[sp_name]['morph']['intensifier']
            emoticon_count += token_count * intensifier
            for i in range(0, token_count * intensifier):
                final_emoticons.append(special_entities[sp_name]['stem'])
    print(text)
    print(spaced_text)
    print(clean_text)
    print(special_entities)
    return spaced_text, clean_text, final_emoticons, emojis, complementary_characters, emoticon_count, \
           emojis_count, complementary_characters_count, special_entities


def identify_emoticons(final_text, sp_id, ordered_special_entities, special_entities, simple_special_entities,
                       emotions, emoticons_metadata, emotions_polarity, emoticon_count, final_emoticons, moment):
    # Emoticons: Moment 3
    clean_text = ''
    text = ''
    for pattern_type in emoticons_metadata:
        emotions = emoticons_metadata[pattern_type]
        for emotion in emotions:
            pattern = emotions[emotion]['pattern']
            character = emotions[emotion]['characters']
            if moment in emotions[emotion]['time']:
                final_text = delete_spaces(final_text)
                simple_tokens = final_text.split(' ')
                # print(final_text)
                # print(simple_tokens)
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
                                clean_text += final_em + ' '
                                print('here ', clean_text)
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
                                print(special_entities[final_em])
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
                            print(token + ' does not match the emoticon pattern')
                            clean_text += token + ' '
                    else:
                        clean_text += token + ' '
                final_text = clean_text
                text = clean_text
                print(clean_text)
                clean_text = ''
    # hacer la cuenta al final... contar cuantas veces esta special_entity en clean_text y actualizar la cuenta en el
    # resultado final. En el mismo se puede hacer el conteo del número de emoticones.
    f_text = text
    for sp_name in special_entities.keys():
        token = special_entities[sp_name]['token']
        f_text = f_text.replace(sp_name, token)
    # print('get out')
    # print(text)
    # print(f_text)
    # print(special_entities)
    return sp_id, text, f_text, emoticon_count, special_entities, final_emoticons


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


def delete_spaces(text):
    text = text.strip(' ')
    text = ' '.join(text.split())
    return text

# text = 'Piscina 🏊🏻 (@ Centro Empresarial y Recreativo El Cubo (Colsubsidio) - @colsubsidio_ofi) https://t.co/m325PyXsQl'
# complete_text_analysis(text, {'user_mentions': [{'id': 443795193, 'name': 'Colsubsidio_Oficial', 'indices': [70, 86], 'id_str': '443795193', 'screen_name': 'Colsubsidio_Ofi'}], 'hashtags': [], 'symbols': [], 'urls': [{'indices': [88, 111], 'display_url': 'swarmapp.com/c/jZD9SBOj9qf', 'expanded_url': 'https://www.swarmapp.com/c/jZD9SBOj9qf', 'url': 'https://t.co/m325PyXsQl'}]})

complete_text_analysis("Creo que no puedo ir </3.", {'urls':[], 'user_mentions': [], 'hashtags': []})
