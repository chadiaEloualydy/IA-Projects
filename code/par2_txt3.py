import datetime

nbre = 1000000

def extraireCle(partie, triplet):
    return triplet[triplet[0].index(partie) + 1]

debut = datetime.datetime.now()
for i in range(0, nbre):
    a = (
        ("sujet", "prédicat", "objet"),
        0,
        1,
        2
    )
    b = extraireCle("prédicat", a)
fin = datetime.datetime.now()
print("tuple-complexe :", fin - debut)

debut = datetime.datetime.now()
for i in range(0, nbre):
    a = {"sujet": 0, "predicat": 1, "objet": 2}
    b = a["predicat"]
fin = datetime.datetime.now()
print("dict :", fin - debut)
