import spacy
from spacy.matcher import Matcher
from datetime import timedelta, datetime
import codecs
from spacy.attrs import ORTH, LEMMA, TAG
import regex as re
from spacy.tokenizer import Tokenizer

date = datetime.today().strftime("%Y_%m_%d-%H_%M_%S")
path_to_file = date + " - DetectEmoticonsWithMatch_Performance.txt"
p_file = codecs.open(path_to_file, encoding='utf-8', mode='a')
p_file.write(date + " Detecting Emoticons with spaCy's Match Test - Local Execution" + "\n")
p_file.flush()
nlp = spacy.load('es')

happy_face_re = re.compile(r''':\)+''')
sad_face_re = re.compile(r''':\(+''')


prefix_re = re.compile(r'''^[\[\("']|:\)+|[:;]\)+|[:;]-\)+|([:;]\))+|[:;]=\)+|(:=\))+|(:-\))+|=\)+|(=\))+|[xX][dD]+|(:D+|=D+|:-D+)\s|(:D+|=D+|:-D+)$''')
suffix_re = re.compile(r'''(:\)+)|[\]\)"']$''')
infix_re = re.compile(r'''[-~]''')
simple_url_re = re.compile(r'''^https?://''')


def custom_tokenizer(nlp):

    return Tokenizer(nlp.vocab, prefix_search=prefix_re.search,
                                suffix_search=suffix_re.search,
                                infix_finditer=infix_re.finditer,
                                token_match=simple_url_re.match)

nlp.tokenizer = custom_tokenizer(nlp)
doc = nlp('Estoy muy :)))))))) SIXDEGREES feliz:)))))))')
for tag in doc:
    print(tag)

"""
def on_match(matcher, doc, i, matches):
    match_id, start, end = matches[i]
    # doc.ents += (EVENT, start, end)
    print('Matched!', matches)


matcher = Matcher(nlp.vocab)
matcher.add('SadFace', on_match, [{'ORTH': ':'}, {'ORTH': '('}])
matcher.add('HappyFace', on_match, [{'ORTH': ':)+'}])
doc = nlp('Estoy muy feliz :))) ')
for tag in doc:
    print(tag)
print(doc.ents)
matches = matcher(doc)
"""
