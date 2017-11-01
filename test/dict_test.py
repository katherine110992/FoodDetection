s = [
    {"hola": 'soy Katherine'},
    {"adios": 'mucho gusto'}
]

"""
print(s.keys())
print(s.values())
if 'soy Katherine' in s.values():
    print("YES!!")

search_age = 'mucho gusto'
for name, age in s.items():
    if age == search_age:
        print(name)

del(s["hola"])
print(s)
"""
final = []
for aux in s:
    aux_dic = s[aux]
    final.append(stem + "\t" + new_what_words[stem])