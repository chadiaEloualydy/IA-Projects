import io

f = io.BytesIO()
contenu = "wahou c'est trop cool ! :)"
contenu = contenu.encode("utf-8")
taille = len(contenu)
taille = taille.to_bytes(1, "big")
f.write(taille)
f.write(contenu)
f.seek(0)  # retour au début du fichier ( 0 = premier signe = premier caractère)
print("contenu du fichier :", f.read())
f.seek(0)
taille = f.read(1)
taille = int.from_bytes(taille, "big")
contenu = f.read(taille)
contenu = contenu.decode("utf-8")
print("contenu de la variable :", contenu)
