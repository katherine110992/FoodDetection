import urllib.request
import unidecode

text = '😐 Hola Juanito, cómo>:[ vas? 😐 :(. Yo melancólico. Me gusta la lasaña'
encodedText = urllib.parse.quote(text.encode("utf-8"))
print(encodedText)