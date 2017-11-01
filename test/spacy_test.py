import spacy
from datetime import timedelta
from time import time

start_time = time()
nlp = spacy.load('es')
execution_time = time() - start_time
print(str(timedelta(seconds=execution_time)))
print()

# import es_core_web_md

# nlp = es_core_web_md.load()
print(spacy.es.TAG_MAP)

print(spacy.es.STOP_WORDS)

start_time = time()
doc = nlp('no \\ entiendo a \' " % ; ¿? ! ¡ : \# $ & > < - _ ° | ¬ \\ * + [ ] { } = \n &amp &gt &lt @esas mujeres (y hombres) que les gusta que le lleguen con flores a mi que me enamoren con comida como torta, pizza, hamburguesas etc')
for word in doc:
    print(word.text, word.tag_, word.pos_)
execution_time = time() - start_time
print(str(timedelta(seconds=execution_time)))
print()
