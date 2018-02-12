import re
from datetime import datetime
import codecs
import spacy


date = datetime.today().strftime("%Y_%m_%d-%H_%M_%S")
path_to_file = date + " - DetectCompleteEmoticonsWithRegex_Performance.txt"
p_file = codecs.open(path_to_file, encoding='utf-8', mode='a')
p_file.write(date + " Detecting Complete Emoticons with Regex - Local Execution" + "\n")
p_file.flush()

forward_emoticon_pattern = r"([:;=]'?-?[\)!D\(\CcoOpPDsS\/\*\|\\]+)" \
                          r"|[xX][dD]+" \
                          r"|[:=][30]" \
                          r"|:-?[\|!\$#\*vV\[]" \
                          r"|<3" \
                          r"|<\/3"
forward_emoticons_characters = ['X', 'x', 'd', 'D', ')', '(', ':', ';', '\'', '*', '=', '/', '$', '#', '-', 'C', 'c',
                                '<', '3', '0', 'O', 'o', 'p', 'P', '!', 's', 'S', '|', '\\', 'v', 'V', '[']

backward_emoticon_pattern = r"([\)D\(\C\coOpPDsS\/\*\|\\\\]+-?'?[:;=])"
backward_emoticons_characters = [')', '(', ':', ';', '\'', '*', '=', '/', '$', '#', '-', 'C', 'c', 'O', 'o', 'p', 'P',
                                 's', 'S', '|', '\\']


faces_pattern = r"\^[-_.]?\^|[Oo][._][oO]|[uU]_[uU]|\*[_-~]\*|>[._-]?<|-[_.]-|._.|=_=|\\[mo]\/"
faces_characters = ['^', '-', '_', '.', 'o', 'O', 'U', 'u', '*', '~', '<', '>', '\\', '/', 'm', '=']


patterns = [forward_emoticon_pattern, backward_emoticon_pattern, faces_pattern]
characters = [forward_emoticons_characters, backward_emoticons_characters, faces_characters]

test_str = "JAJAJAJAJAJJAJAJAJAJJAJAJAJAJAJJAJAJAJAJAJAJAJAJAJJAJAJAJAJAJJAJAJAJAJAAJAJAJAJAJAJAJAJAJJAJAJAJAJAJAJAJJAJAA HPTAXD"

# test_str = "Te necesito en mi vida para ser feliz :) https://t.co/kcee5JDS7G"

# si el siguiente después del sufijo es puntuación, entonces también se puede tomar como emoticon.


entity_sequence = 0
clean_text = ''
final_text = test_str
entities = {}
final_emoticons = []
entities_dict = {}

for i in range(0, len(patterns)):
    pattern = patterns[i]
    character = characters[i]
    simple_tokens = final_text.split(' ')
    for token in simple_tokens:
        if token not in entities_dict.keys():
            it_matches = True
            matches = re.match(pattern, token)
            emoticons = list()
            print(matches)
            if matches:
                for char in token:
                    if char not in character:
                        # is not a emoticon
                        matches = False
                        break
            if matches:
                matches = re.finditer(pattern, token)
                for matchNum, match in enumerate(matches):
                    matchNum += 1
                    # detect intensifier
                    sequence_detected = emoticon = match.group().upper()
                    last_character = sequence_detected[len(sequence_detected) - 1]
                    before_last_character = sequence_detected[len(sequence_detected) - 2]
                    if last_character == before_last_character:
                        # there is an intensifier
                        intensifier = sequence_detected.count(last_character)
                        detected_emoticon = sequence_detected.replace(last_character * intensifier, last_character)
                    else:
                        intensifier = 1
                        detected_emoticon = sequence_detected
                    entity_found = False
                    for entity in entities:
                        if emoticon == entities[entity]['pos']:
                            final_em = entity
                            entity_found = True
                            break
                    if not entity_found:
                        final_em = 'special_entity_' + str(entity_sequence)
                        entity_sequence += 1
                        entities_dict[emoticon] = final_em
                    print(final_em)
                    clean_text += final_em + ' '
                    final_emoticons.append(final_em)
                    entities[final_em] = {
                        'token': detected_emoticon,
                        'tag_type': 'emoticon',
                        'morph': 'Polarity=1',
                        'pos': emoticon,
                        'count': intensifier
                    }
            else:
                matches = re.finditer(pattern, token)
                for matchNum, match in enumerate(matches):
                    if token.endswith(match.group()):
                        print(token + ' has a suffix')
                        it_matches = True
                        matches = re.finditer(pattern, token)
                        clean_token = token
                        for matchNum, match in enumerate(matches):
                            # matches = re.finditer(emoticon_pattern, token)
                            matchNum += 1
                            p_file.write(
                                "Match {matchNum} was found at {start}-{end}: {match}\n".format(matchNum=matchNum,
                                                                                                start=match.start(),
                                                                                                end=match.end(),
                                                                                                match=match.group()))
                            emoticons.append(match.group().upper())
                            if matchNum == 1:
                                clean_token = clean_token[0:match.start()]
                                # print(clean_token)
                        clean_token += ' '
                        # print(emoticons)
                        for emoticon in emoticons:
                            sequence_detected = emoticon
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
                            entity_found = False
                            for entity in entities:
                                if emoticon == entities[entity]['pos']:
                                    final_em = entity
                                    entity_found = True
                                    break
                            if not entity_found:
                                final_em = 'special_entity_' + str(entity_sequence)
                                entity_sequence += 1
                                entities_dict[emoticon] = final_em
                            clean_token += final_em + ' '
                            final_emoticons.append(final_em)
                            entities[final_em] = {
                                'token': detected_emoticon,
                                'tag_type': 'emoticon',
                                'morph': 'Polarity=1',
                                'pos': emoticon,
                                'count': intensifier
                            }
                        clean_text += ' ' + clean_token
                        break
                    else:
                        it_matches = False
                        # print('is not suffix: ' + token)
                else:
                    it_matches = False
            if not it_matches:
                print(token + ' does not match the emoticon pattern')
                clean_text += token + ' '
        else:
            clean_text += entities_dict[token] + ' '
    aux_text = clean_text
    i = len(final_emoticons) - 1
    while i >= 0:
        entity_id = final_emoticons[i]
        entity_token = entities[entity_id]['pos']
        aux_text = aux_text.replace(entity_id, entity_token)
        i -= 1
    final_text = aux_text
    print(clean_text)
    print(final_text)
    clean_text = ''

print(entities)
p_file.write(clean_text+'\n')
# print(final_emoticons)
p_file.write(str(entities)+'\n')
# p_file.write(str(emoticon_count)+'\n')
# for e in final_emoticons:
#     print(e)
# print(entities)

