import datetime

nbre = 1000000

debut = datetime.datetime.now()
for i in range(0, nbre):
    a = "coucou".encode("utf-8")
fin = datetime.datetime.now()
print("encode :", fin - debut)

debut = datetime.datetime.now()
for i in range(0, nbre):
    a = b"coucou".decode("utf-8")
fin = datetime.datetime.now()
print("décode :", fin - debut)

debut = datetime.datetime.now()
for i in range(0, nbre):
    a = ("coucou".encode("utf-8")).decode("utf-8")
fin = datetime.datetime.now()
print("mixte :", fin - debut)
