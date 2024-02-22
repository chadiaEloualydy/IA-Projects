import re

__all__ = ["TripletsHTTP"]

class TripletsHTTP:

    sautLigne = "\n"
    expReg_triplet = re.compile(
        "^(?P<sujet>[^\t]+)\t(?P<predicat>[^\t]+)\t(?P<objet>[^\t]+)$",
        re.I
    )

    def __init__(self, client):
        self.client = client
        self.etat = None
        self.liste = []

    async def traiterCorps(self, taille):
        try:
            corps = await self.client.lecteur.read(taille)
            corps = corps.decode("utf-8")
            while True:
                if self.sautLigne not in corps:
                    break
                ligne, corps = corps.split(self.sautLigne, 1)
                self.liste.append((await self.traiterLigne(ligne)))
                if corps != "":
                    self.liste.append((await self.traiterLigne(corps)))
            self.etat = True
        except Exception as err:
            self.etat = False

    async def traiterLigne(self, portion):
        return self.expReg_triplet.match(portion).groupdict()
