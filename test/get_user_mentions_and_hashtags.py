text = "hola mucho gusto... no me gusta http://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html?ssSourceSiteId=otnes  #hola @hello @holamimi http://www.igi-global.com/submission/?returnurl=%2fsubmission%2fconfirm-personal-information%2f%3fprojectid%3d6d3b7fbb-e7e8-44a7-92ec-66f9390aeac4 hola otra vez"
text = "#kcacolombia https://t.co/9vgki1tgsu	apple re cago los emojis en ios10 beta 4\nhora de las noticias insolitas, mundo curioso en la papaya de oxigeno 100.4 \n#papayacuriosa"
user_mentions = []
hashtags = []
characters = ["#", "@", "http"]
for character in characters:
    count_character = text.count(character)
    if count_character > 0:
        for i in range(0, count_character):
            start = text.find(character)
            end = text.find(" ", start)
            if end == -1:
                end = len(text)
            text_to_remove = text[start:end]
            if character == "#":
                hashtags.append(text_to_remove)
            elif character == "@":
                user_mentions.append(text_to_remove)
            text = text.replace(text_to_remove, "")
            text = ' '.join(text.split())
text = text.strip(' ')
text = ' '.join(text.split())
print(text)
print(user_mentions)
print(hashtags)