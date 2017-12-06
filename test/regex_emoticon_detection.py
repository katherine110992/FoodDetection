import re
from datetime import datetime
import codecs
import spacy
from spacy.tokens import Span, Doc

date = datetime.today().strftime("%Y_%m_%d-%H_%M_%S")
path_to_file = date + " - DetectEmoticonsWithRegex_Performance.txt"
p_file = codecs.open(path_to_file, encoding='utf-8', mode='a')
p_file.write(date + " Detecting Emoticons with Regex Test - Local Execution" + "\n")
p_file.flush()

nlp = spacy.load('es')

happy_pattern = r"[:;]\)+|[:;]-\)+|([:;]\))+|[:;]=\)+|(:=\))+|(:-\))+|=\)+|(=\))+|[xX][dD]+|:D+|=D+|:-D+"
emoticon_pattern = r"([:;=]'?-?[\)D\(\C\coOpPDsS/\*\|\\]+)|[xX][dD]+|[:=][30]|:-?[\|!\$#\*vV\[]|<3|</3|" \
                   r"([\)D\(\C\coOpPDsS/\*\|\\\\]+-?'?[:;=])|\^[-_.]\^"
# emoticon_pattern = r"([:;=]-?([\)D\(\C\co]+|[xX][dD]+))|([:<][3])|(<\\3)|()"
emoticons_characters = ['X', 'x', 'd', 'D', ')', '(', ':', ';', '\'', '*', '=', '/', '$', '#', '-', 'C', 'c',
                        '<', '3', '0', 'O', 'o', 'p', 'P', '!', 's', 'S', '|', '\\', 'v', 'V']

faces_pattern = r"\^[-_.]?\^|[Oo][._][oO]"
faces_characters = ['^', '-', '_', '.', 'o', 'O']

# \| ! $
test_str = "Soy muy feliz!!!!! :-) :-) :-) :)))))):))))) )-: :\ :||| =| feliz;)=):D=)=/ xdxDXdXDxdXdxDxdxDxd =Dah! :-D " \
           "XDDDDDDDDD DE XDIOS SIXDEGREES! =). :/ :-* :\ D= D=mi :s D: D:holla :Volar :v :[ :-S :-o =/ :-! :* :0 :3 " \
           ":3000. Aunque a =P veces me da mucha melancolía :( :(((((( y " \
           "mas y mas:CCCCCCCCCC 10:00 a.m. ^^ ^.^ ^_^ ^-^ :c También C: :| :-| ;! :$ :'-( estoy como ;p :P </3 :p y como" \
           ":pelear, " \
           "pero tambien <3:P :-PDonde"

# test_str = "Te necesito en mi vida para ser feliz :) https://t.co/kcee5JDS7G"

doc = nlp(test_str)
MISC = doc.vocab.strings[u'MISC'] # get hash value of entity label

# si el siguiente después del sufijo es puntuación, entonces también se puede tomar como emoticon.
# ents = [(e.text, e.start_char, e.end_char, e.label_) for e in doc.ents]
# assert ents = [(u'Netflix', 0, 7, u'ORG')]

simple_tokens = test_str.split(' ')

emoticon_count = 0
emoticon_sequence = 0
clean_text = ''
entities = {}
final_tokens = []

for token in simple_tokens:
    p_file.write(str(emoticon_count) + '\n')
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
            p_file.write("Match {matchNum} was found at {start}-{end}: {match}\n".format(matchNum=matchNum, start=match.start(),
                                                                            end=match.end(), match=match.group()))
            doc.ents += ((MISC, match.start(), match.end()),)
            if match.group().upper() in entities.keys():
                final_em = entities[match.group().upper()]['token']
            else:
                final_em = 'special_entity_' + str(emoticon_sequence)
                emoticon_sequence += 1
            clean_text += final_em + ' '
            final_tokens.append(final_em)
            entities[match.group().upper()] = {
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
                matches = re.finditer(emoticon_pattern, token)
                clean_token = token
                for matchNum, match in enumerate(matches):
                    # matches = re.finditer(emoticon_pattern, token)
                    matchNum += 1
                    p_file.write("Match {matchNum} was found at {start}-{end}: {match}\n".format(matchNum=matchNum,
                                                                                                 start=match.start(),
                                                                                                 end=match.end(),
                                                                                                 match=match.group()))
                    emoticons.append(match.group().upper())
                    if matchNum == 1:
                        clean_token = clean_token[0:match.start()]
                        final_tokens.append(clean_token)
                    print(clean_token)
                clean_token += ' '
                print(emoticons)
                couunt = 0
                for emoticon in emoticons:
                    print(couunt)
                    couunt+=1
                    if emoticon in entities.keys():
                        print(emoticon)
                        print(entities)
                        print(match.group())
                        final_em = entities[emoticon]['token']
                    else:
                        print('Not in entities ', emoticon)
                        final_em = 'special_entity_' + str(emoticon_sequence)
                        emoticon_sequence += 1
                    clean_token += final_em + ' '
                    final_tokens.append(final_em)
                    entities[emoticon] = {
                        'token': final_em,
                        'tag_type': 'emoticon',
                        'morph': 'Polarity=1',
                        'pos': ''
                    }
                clean_text += ' ' + clean_token
                emoticon_sequence += 1
                break
            else:
                is_emoticon = False
            """
            elif token.startswith(match.group()):
                print("it is a prefix emoticon", token)
                is_emoticon = True
                matches = re.finditer(emoticon_pattern, token)
                clean_token = token
                start = 0
                end = 0
                for matchNum, match in enumerate(matches):
                    matches = re.finditer(emoticon_pattern, token)
                    matchNum += 1
                    p_file.write("Match {matchNum} was found at {start}-{end}: {match}\n".format(matchNum=matchNum,
                                                                                                 start=match.start(),
                                                                                                 end=match.end(),
                                                                                                 match=match.group()))
                    emoticons.append(match.group().upper())
                    start = match.start()
                    end = match.end()
                clean_token = clean_token[end:len(clean_text)-1]
                t = clean_token
                print(clean_token)
                clean_token += ' '
                for emoticon in emoticons:
                    if emoticon in entities.keys():
                        final_em = entities[match.group()]['token']
                    else:
                        final_em = 'special_entity_' + str(emoticon_sequence)
                        emoticon_sequence += 1
                    clean_token += final_em + ' '
                    final_tokens.append(final_em)
                    entities[emoticon] = {
                        'token': final_em,
                        'tag_type': 'emoticon',
                        'morph': 'Polarity=1',
                        'pos': ''
                    }
                final_tokens.append(t)
                clean_text += ' ' + clean_token
                emoticon_sequence += 1
                break
            """
        if not is_emoticon:
            clean_text += token + ' '
            final_tokens.append(token)
p_file.write(clean_text+'\n')
print(final_tokens)
p_file.write(str(entities)+'\n')
p_file.write(str(emoticon_count)+'\n')
for e in final_tokens:
    print(e)
print(entities)
