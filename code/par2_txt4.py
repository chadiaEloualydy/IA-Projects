import datetime

nbre = 1000000

def extraireCle(partie, triplet):
    i = triplet[0].index(partie)
    return [item[i] for item in triplet[1:]]

# juste pour tester
a = (
    ("sujet", "prédicat", "objet"),
    (0, 1, 2),
    (0, 1, 2),
    (0, 1, 2)
)
print(extraireCle("prédicat", a))  # retourne une liste de trois "1"

debut = datetime.datetime.now() 
for i in range(0, nbre):
    a = (
        ("sujet", "prédicat", "objet"),
        (0, 1, 2),
        (0, 1, 2),
        (0, 1, 2),
        (0, 1, 2),
        (0, 1, 2),
        (0, 1, 2),
        (0, 1, 2),
        (0, 1, 2),
        (0, 1, 2),
        (0, 1, 2)
    )
    b = extraireCle("prédicat", a)
fin = datetime.datetime.now()
print("tuple-complexe :", fin - debut)

debut = datetime.datetime.now()
for i in range(0, nbre):
    a = [
        {"sujet": 0, "predicat": 1, "objet": 2},
        {"sujet": 0, "predicat": 1, "objet": 2},
        {"sujet": 0, "predicat": 1, "objet": 2},
        {"sujet": 0, "predicat": 1, "objet": 2},
        {"sujet": 0, "predicat": 1, "objet": 2},
        {"sujet": 0, "predicat": 1, "objet": 2},
        {"sujet": 0, "predicat": 1, "objet": 2},
        {"sujet": 0, "predicat": 1, "objet": 2},
        {"sujet": 0, "predicat": 1, "objet": 2},
        {"sujet": 0, "predicat": 1, "objet": 2}
    ]
    b = [item["predicat"] for item in a]
fin = datetime.datetime.now()
print("dict :", fin - debut)
