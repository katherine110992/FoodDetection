
emoticon = ':))))))))))))))))))'
last_character = emoticon[len(emoticon)-1]
before_last_character = emoticon[len(emoticon) - 2]
if last_character == before_last_character:
    # there is an intensifier
    intensifier = emoticon.count(last_character)
    print(intensifier)
    to_remove = last_character * intensifier
    print(to_remove)
    detected_emoticon = emoticon.replace(to_remove, last_character)
    print(detected_emoticon)
else:
    intensifier = 1


