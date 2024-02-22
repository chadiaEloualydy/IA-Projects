async def ajouter(self, enregistrement, groupe=0, uid=0, f=None):
    if f is None:
        f = self.f
    f.seek(0, 2)
    f.write(bytes(self.indexTaille))
    tailleEnreg = 0
    for cle in self.enregistrement:
        f.write(bytes(self.enregistrement[cle]))
        if type(enregistrement[cle]) == str:
            taillePartie = f.write(enregistrement[cle].encode("utf-8"))
        else:
            taillePartie = f.write(enregistrement[cle])
        f.seek(0 - taillePartie - self.enregistrement[cle], 2)
        f.write(taillePartie.to_bytes(self.enregistrement[cle], "big"))
        f.seek(f.tell() + taillePartie)
        tailleEnreg += taillePartie + self.enregistrement[cle]
    _index = (1, groupe, uid, tailleEnreg)
    f.seek(0 - tailleEnreg - self.indexTaille, 2)
    for i, cle in enumerate(self.index):
        f.write(_index[i].to_bytes(self.index[cle], "big"))
    f.flush()
    return True
