import asyncio

__all__ = ["Silo", "EnregistrementComposition"]

EnregistrementComposition = {
    "sujet": 3,
    "predicat": 3,
    "objet": 3
}

class Silo:
    index = {
        "actif": 1,
        "uid": 16,
        "taille": 4
    }

    enregistrement = {}

    nbreMaxRequetesSimultanee = 10

    def __init__(self, fChemin):
        global EnregistrementComposition
        for cle in EnregistrementComposition:
            self.enregistrement[cle] = EnregistrementComposition[cle]
        self.indexTaille = 0
        for cle in self.index:
            self.indexTaille += self.index[cle]
        self.fSiloChemin = fChemin
        self.fSilo = open(fChemin, "rb+")
        self.requetes = []
        self.transactions = []

    async def executer(self):
        while True:
            try:
                if len(self.requetes) == 0:
                    await asyncio.sleep(0.1)
                else:
                    self.fSilo.seek(0)
                    requetes = await self.recupererRequetes()
                    print("(info) Silo->exécuter : nouvelles requêtes en cours de réalisation")
                    while True:
                        triplet = await self.suivant()
                        if triplet is None:
                            break
                        elif triplet is False:  # théoriquement impossible
                            pass
                        else:
                            positionInitiale, index, enregistrement = triplet
                            for requete in requetes:
                                if await requete.filtre.deduire(requete, index, enregistrement) is True:
                                    requete.reponse.write(
                                        (("".join(enregistrement.values())) + "\n").encode("utf-8")
                                    )
                            for requete in requetes:
                                requete.enAttente = False
            except Exception as err:
                print("(err) Silo->exécuter (requêtes) :", err)
            finally:
                while len(self.transactions) > 0:
                    try:
                        typeTransaction, transaction = self.transactions.pop()
                        await getattr(self, "executerTransaction_%s" % typeTransaction)(transaction)
                        transaction.etat = True
                    except Exception as err:
                        print("(err) Silo->exécuter (transactions) :", err)
                        transaction.etat = False
                    finally:
                        transaction.enAttente = False

    async def recupererRequetes(self):
        _requetes = []
        for requete in self.requetes:
            _requetes.append(requete)
            self.requetes.remove(requete)
            if len(_requetes) >= self.nbreMaxRequetesSimultanee:
                break
        return _requetes

    async def executerTransaction_suppression(self, transaction):
        i = 0
        self.fSilo.seek(0)
        while True:
            triplet = await self.suivant()
            if triplet is None or triplet is False:
                break
            positionInitiale, index, enregistrement = triplet
            if await transaction.filtre.deduire(transaction, index, enregistrement) is True:
                await self.supprimer(positionInitiale)
                i += 1
                transaction.reponse.write(
                    ("suppressions = %s" % i).encode("utf-8")
                )

    async def executerTransaction_ecriture(self, transaction):
        for triplet in transaction.corps.liste:
            await self.ajouter(triplet, transaction.uid)

    async def ajouter(self, enregistrement, uid, f=None):
        try:
            if f is None:
                f = self.fSilo
            f.seek(0, 2)
            positionInitiale = f.tell()
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
            f.seek(positionInitiale)
            _index = (1, uid, tailleEnreg)
            for i, cle in enumerate(self.index):
                f.write(_index[i].to_bytes(self.index[cle], "big"))
            f.flush()
            return True
        except Exception as err:
            print("(err) Silo-> ajouter :", err)

    async def supprimer(self, positionIndex):
        self.fSilo.seek(positionIndex)
        self.fSilo.write(bytearray(1))

    async def suivant(self, uid=None, filtreActif=True):
        positionIndex = self.fSilo.tell()
        portion = self.fSilo.read(self.indexTaille)
        if portion == b"":
            return None
        index = {}
        position = 0
        for cle in self.index:
            index[cle] = int.from_bytes(
                portion[position:position + self.index[cle]],
                "big"
            )
            position += self.index[cle]
        c = True
        if filtreActif is True:
            if index["actif"] == 0:
                c = False
            if uid is not None:
                if index["uid"] != uid:
                    c = False
            if c is False:
                self.fSilo.seek(positionIndex + self.indexTaille + index["taille"])
                return False
        partiesBin = self.fSilo.read(index["taille"])
        parties = {}
        position = 0
        for cle in self.enregistrement:
            taillePartie = int.from_bytes(
                partiesBin[position:position + self.enregistrement[cle]],
                "big"
            )
            position += self.enregistrement[cle]
            parties[cle] = partiesBin[position:position + taillePartie].decode("utf-8")
            position += taillePartie
        return (positionIndex, index, parties)
