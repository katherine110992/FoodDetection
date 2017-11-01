s = {
    "hola": 'soy Katherine',
    "adios": 'mucho gusto'
}
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