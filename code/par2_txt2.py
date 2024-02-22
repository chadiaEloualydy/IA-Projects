import datetime

nbre = 1000000

debut = datetime.datetime.now()
for i in range(0, nbre):
    class A:
        sujet = 0
        predicat = 1
        objet = 2
    a = A()
    b = a.predicat
fin = datetime.datetime.now()
print("object :", fin - debut)

debut = datetime.datetime.now()
for i in range(0, nbre):
    a = {"sujet": 0, "predicat": 1, "objet": 2}
    b = a["predicat"]
fin = datetime.datetime.now()
print("dict :", fin - debut)

debut = datetime.datetime.now()
for i in range(0, nbre):
    a = [0, 1, 2]
    b = a[1]
fin = datetime.datetime.now()
print("list :", fin - debut)

debut = datetime.datetime.now()
for i in range(0, nbre):
    a = (0, 1, 2)
    b = a[1]
fin = datetime.datetime.now()
print("tuple :", fin - debut)
