import asyncio
import io
import uuid

class Silo:
    index = {
        "actif": 1,
        "groupe": 16,
        "uid": 16,
        "taille": 4
    }

    enregistrement = {
        "sujet": 3,
        "predicat": 3,
        "objet": 3
    }

    def __init__(self, f):
        self.f = f
        self.f.seek(0)
        self.indexTaille = 0
        for cle in self.index:
            self.indexTaille += self.index[cle]

    async def ajouter(self, enregistrement, groupe=0, uid=0, f=None):
        if f is None:
            f = self.f
        parties = {}
        tailleEnreg = 0
        for cle in self.enregistrement:
            partie = enregistrement[cle].encode("utf-8")
            parties[cle] = (
                len(partie).to_bytes(self.enregistrement[cle], "big"),
                partie
            )
            tailleEnreg += len(partie) + self.enregistrement[cle]
        index = bytearray()
        index += (1).to_bytes(self.index["actif"], "big")
        index += groupe.to_bytes(self.index["groupe"], "big")
        index += uid.to_bytes(self.index["uid"], "big")
        index += tailleEnreg.to_bytes(self.index["taille"], "big")
        f.seek(0, 2)
        f.write(index)
        for cle in self.enregistrement:
            f.write(parties[cle][0])
            f.write(parties[cle][1])
        f.flush()
        return True

    async def supprimer(self, groupe=None, uid=None, filtrer=None):
        i = 0
        for positionIndex, enregistrement in await self.trouver(
            groupe=groupe,
            uid=uid,
            filtrer=filtrer
        ):
            self.f.seek(positionIndex)
            self.f.write(bytearray(1))
            i += 1
        return i

    async def trouver(self, groupe=None, uid=None, filtrer=None):
        self.f.seek(0)
        r = []
        while True:
            enregistrement = await self.suivant(
                groupe=groupe,
                uid=uid
            )
            if enregistrement is None:
                break
            elif enregistrement is False:
                continue
            else:
                positionIndex, index, enregistrement = enregistrement
                if filtrer is not None:
                    if not await filtrer(enregistrement):
                        continue
                r.append((positionIndex, enregistrement))
        return r

    async def suivant(self, groupe=None, uid=None, filtreActif=True):
        positionIndex = self.f.tell()
        portion = self.f.read(self.indexTaille)
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
            if groupe is not None:
                if index["groupe"] != groupe:
                    c = False
            if uid is not None:
                if index["uid"] != uid:
                    c = False
        if c is False:
            self.f.seek(positionIndex + self.indexTaille + index["taille"])
            return False
        partiesBin = self.f.read(index["taille"])
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

    async def modifier(self, enregistrement, groupe=None, uid=None):
        r = await self.trouver(groupe=groupe, uid=uid)
        if len(r) == 0:
            return False
        positionIndex, parties = r[0]
        for cle in enregistrement:
            parties[cle] = enregistrement[cle]
        r = await self.supprimer(groupe=groupe, uid=uid)
        if r == 0:
            return False
        await self.ajouter(enregistrement=parties, groupe=groupe, uid=uid)
        return True

    async def optimiser(self, fDestination=None):
        fDestination.seek(0)
        self.f.seek(0)
        i = 0
        while True:
            r = await self.suivant()
            if r is None:
                break
            elif r is False:
                continue
            else:
                positionIndex, index, enregistrement = r
                await self.ajouter(
                    enregistrement=enregistrement,
                    groupe=index["groupe"],
                    uid=index["uid"],
                    f=fDestination
                )
                i += 1
        self.f = fDestination
        return i

    async def statistiquer(self):
        self.f.seek(0)
        inactifs = 0
        actifs = 0
        tailleCharge = 0
        while True:
            r = await self.suivant(filtreActif=False)
            if r is None:
                break
            elif r is False:
                continue
            else:
                positionIndex, index, enregistrement = r
                tailleCharge += index["taille"]
                if index["actif"] == 0:
                    inactifs += 1
                else:
                    actifs += 1
        return actifs, inactifs, tailleCharge


async def main():
    f1 = io.BytesIO()
    s = Silo(f1)
    groupe = uuid.uuid4().int
    uid1 = uuid.uuid4().int
    uid2 = uuid.uuid4().int
    uid3 = uuid.uuid4().int
    uid4 = uuid.uuid4().int
    await s.ajouter(
        enregistrement={
            "sujet": "pouetpouet",
            "predicat": "truc",
            "objet": "machin"
        },
        groupe=groupe,
        uid=uid1
    )
    await s.ajouter(
        enregistrement={
            "sujet": "1",
            "predicat": "2",
            "objet": "3"
        },
        groupe=groupe,
        uid=uid2
    )
    await s.ajouter(
        enregistrement={
            "sujet": "#Julien",
            "predicat": "est",
            "objet": "rdf:Personne"
        },
        groupe=groupe,
        uid=uid3
    )
    await s.supprimer(groupe=groupe, uid=uid2)
    await s.ajouter(
        enregistrement={
            "sujet": "fjdfljds",
            "predicat": "manque d'imagination",
            "objet": "²&é\"'(-è_çà)='"
        },
        groupe=groupe,
        uid=uid4
    )
    await s.modifier(
        enregistrement={
            "sujet": "je",
            "objet": "parfois"
        },
        groupe=groupe,
        uid=uid4
    )
    r = await s.trouver(groupe=groupe)
    print("total de ", len(r), " triplets -(détails)> ", r)
    nbreActifs, nbreInactifs, tailleEstimee = await s.statistiquer()
    ratio = nbreActifs / (nbreActifs + nbreInactifs)
    print(
        "\n-- Informations: \n\tactifs:", nbreActifs,
        "\n\tinactifs:", nbreInactifs,
        "\n\tratio:", ratio,
        "\n\ttaille de la charge utile:", tailleEstimee,
        "\n--- --- ---\n"
    )
    if ratio < 0.75:
        f2 = io.BytesIO()
        await s.optimiser(f2)
        r = await s.trouver(groupe=groupe)
        print("total de ", len(r), " triplets -(détails)> ", r)
        nbreActifs, nbreInactifs, tailleEstimee = await s.statistiquer()
        ratio = nbreActifs / (nbreActifs + nbreInactifs)
        print(
            "\n-- Informations: \n\tactifs:", nbreActifs,
            "\n\tinactifs:", nbreInactifs,
            "\n\tratio:", ratio,
            "\n\ttaille de la charge utile:", tailleEstimee,
            "\n--- --- ---\n"
        )
    print("--- Finalement : ")
    print("taille de f1 =", f1.getbuffer().nbytes)
    print("taille de f2 =", f2.getbuffer().nbytes)
    print("---")


asyncio.run(main())
