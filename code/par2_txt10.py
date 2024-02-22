valeurInitiale = 14855069183

representation = bin(valeurInitiale)[2:]

print(representation)

modulo = len(representation) % 7
tailleNecessaire = (len(representation) - modulo) / 7
tailleNecessaire = int(tailleNecessaire)  # pas de float !

if modulo > 0:
    tailleNecessaire + 1

valeurs = []
for i in range(0, tailleNecessaire):
    if i == (tailleNecessaire - 1):
        _v = "0b0" + representation[i * 7:(i * 7) + 7]
    else:
        _v = "0b1" + representation[i * 7:(i * 7) + 7]
    valeurs.append(int(_v, 2))

dernier = valeurs.pop()

print(valeurs)
