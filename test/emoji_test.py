# -*- coding: utf-8 -*-
import codecs
import food_detection_root
import os

s = "1️⃣"
print(len(s))
t = '\u0031\ufe0f\u20e3'
print(t == s)


def unicode_notation(c):
    x = ord(c)
    if 32 <= x < 128:
        return c
    if x < 256:
        return '\\x{:02x}'.format(x)
    if x < 0x10000:
        return '\\u{:04x}'.format(x)
    return '\\U{:08x}'.format(x)

path = food_detection_root.ROOT_DIR + os.path.sep + 'data' + os.path.sep
unicode_emoji_list_file = codecs.open(path + "list - unicode_emojis.txt", encoding='utf-8')
emoji_list = unicode_emoji_list_file.read().splitlines()
unicode_emoji_list_file.close()
emojis_dict = {}
for aux in emoji_list:
    aux_emoji = aux.split('\t')
    emojis_dict[aux_emoji[2]] = [aux_emoji[1], aux_emoji[3]]
# print(emojis_dict)
text = "Quiero un amor q busque ser feliz, q no sea complicado y no me haga sufrir ☝🏻️🎶"
print(text)
for emoji in emojis_dict:
    if emoji in text:
        print(text)
        print(emoji)
        print(emojis_dict[emoji][0], emojis_dict[emoji][1])
        # emojis.append(emojis_dict[aux_emoji].replace('\\', ''))
        # text = text.replace('\\', '')

text = "Mi mayor felicidad , te amo mi gorda . Feliz cumpleaños 1⃣ special_entity_4 special_entity_3 special_entity_0 special_character_1"
print(text)
for emoji in emojis_dict:
    if emoji in text:
        print(text)
        print(emoji)
        print(emojis_dict[emoji][0], emojis_dict[emoji][1])
        # emojis.append(emojis_dict[aux_emoji].replace('\\', ''))
        # text = text.replace('\\', '')

print('othher')
text = "1️⃣"
new = ''.join(unicode_notation(c) for c in text)
print(new)
# Code from https://stackoverflow.com/questions/23481624/python-replace-character-by-its-unicode-representation?noredirect=1&lq=1
