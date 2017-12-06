import spacy
from spacy.matcher import Matcher

nlp = spacy.load('es')
matcher = Matcher(nlp.vocab)
# add match ID "HelloWorld" with no callback and one pattern
pattern = [{'LOWER': 'hola'}, {'IS_PUNCT': True}, {'LOWER': 'mundo'}]
matcher.add('HolaMundo', None, pattern)

doc = nlp(u'Hola, mundo! Hola Mundo!')
matches = matcher(doc)