import spacy
from spacy.matcher import PhraseMatcher
from spacy_lookup import Entity
from spacy.lang.es import Spanish


nlp = Spanish()
entity = Entity(nlp, keywords_list=['pera en Dulce', 'manzana', 'tentacion'], label='FOOD')
nlp.add_pipe(entity, name='Food')
entity2 = Entity(nlp, keywords_list=['#mora'], label='FOOD_HASHTAGS')
nlp.add_pipe(entity2, name='FoodHashtags')
text = "Me gustan mucho la manzana y tambien la pera en dulce en salsa de #mora. También me gusta la paleta tentación."
doc = nlp(text)
for e in doc:
    print(e.text, e._.is_entity, e.ent_type_)
