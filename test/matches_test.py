import re

pattern = r"[uU]_[uU]|._."
character = ['U', 'u', '_', '.']
final_text = "Y nueva #vida brota de entre la #hojarasca 🌱  _______________________ #laromera #sabaneta… https://t.co/JDr2QZzvsi"
simple_tokens = final_text.split(' ')
for token in simple_tokens:
    it_matches = True
    matches = re.match(pattern, token)
    print(matches)
    emoticons = list()
    if matches:
        for char in token:
            if char not in character:
                # is not a emoticon
                matches = False
                break
    if matches:
        print('it matches ', token, pattern)