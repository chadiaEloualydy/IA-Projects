import random

valeurs = []
for i in range(0, 10):
    valeurs.append(random.randint(0, 255))

print(valeurs)
_valeursPertinentes = ["0b"]
for v in valeurs:
    if v > 128 :
# on continue : le bit de poids élevé vaut Vrai
        _valeursPertinentes.append(bin(v)[3:])
    else:  # on s'arrête : le bit de poids élevé vaut Faux
        break

try:
    print(_valeursPertinentes)

    valeurFinale = int("".join(_valeursPertinentes), 2)

    print(valeurFinale)
except ValueError:
    print("pas assez de valeurs en entrée pour calculer - le hasard a mal fait la chose !")
