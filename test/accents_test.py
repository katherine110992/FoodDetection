import urllib.request
import unidecode

text = '😐 Hola Juanito, cómo>:[ vas? 😐 :(. Yo melancólico. Me gusta la lasaña'
encodedText = urllib.parse.quote(text.encode("utf-8"))
print(encodedText)

accented_string = 'Hola Juanito, cómo vas? :(. Yo melancólico. Me gusta la lasaña'
# accented_string is of type 'unicode'
import unidecode
unaccented_string = unidecode.unidecode(accented_string)
print(unaccented_string)