from spacy.language_data.emoticons import EMOTICONS
from spacy.matcher import Matcher

from spacy.es import Spanish
nlp = Spanish()
doc = nlp(u'Apple busca vender emprendimiento de U.K. por $1 billones')

for ent in doc.ents:
    print(ent.text, ent.start_char, ent.end_char, ent.label_)

print(EMOTICONS)
print(type(EMOTICONS))

from emojipedia import Emojipedia # installation: pip install emojipedia
messyData = "lol that is rly funny :) This is gr8 i rate it 8/8!!!"
parsedData = nlp(messyData)
for token in parsedData:
    print(token.orth_, token.text, token.pos_, token.lemma_)

"""
def label_sentiment(matcher, doc, i, matches):
    match_id, start, end = matches[i]
    if doc.vocab.strings[match_id] == 'HAPPY': # don't forget to get string!
        doc.sentiment += 0.1 # add 0.1 for positive sentiment
    elif doc.vocab.strings[match_id] == 'SAD':
        doc.sentiment -= 0.1 # subtract 0.1 for negative sentiment
    span = doc[start : end]
    emoji = Emojipedia.search(span[0].text)  # get data for emoji
    span.merge(norm=emoji.title)  # merge span and set NORM to emoji title
"""

IS_HASHTAG = nlp.vocab.add_flag(lambda text: False)

def merge_hashtag(matcher, doc, i, matches):
    match_id, start, end = matches[i]
    span = doc[start : end]
    span.merge() # merge hashtag
    span.set_flag(IS_HASHTAG, True) # set IS_HASHTAG to True

# nlp = English() # we only want the tokenizer, so no need to load a model
matcher = Matcher(nlp.vocab)

pos_emoji = [u'🍷', u'😃', u'😂', u'🤣', u'😊', u'😍'] # positive emoji
neg_emoji = [u'🍱', u'😠', u'😩', u'😢', u'😭', u'😒'] # negative emoji

# add patterns to match one or more emoji tokens
pos_patterns = [[{'ORTH': emoji}] for emoji in pos_emoji]
neg_patterns = [[{'ORTH': emoji}] for emoji in neg_emoji]

matcher.add('HAPPY', None, *pos_patterns) # add positive pattern
matcher.add('SAD', None, *neg_patterns) # add negative pattern

# add pattern to merge valid hashtag, i.e. '#' plus any ASCII token
matcher.add('HASHTAG', merge_hashtag, [{'ORTH': '#'}, {'IS_ASCII': True}])

LOTS_OF_TWEETS = 'Bienvenido @JCamilOrt. ¿🍷🍻🍜🌯🍱? ¡Por favor! Abrazo.'

docs = nlp.pipe(LOTS_OF_TWEETS)
matches = matcher.pipe()
print(matches)

