import asyncio
import os
import re
import tempfile

from Filtre import FiltreHTTP
from Triplets import TripletsHTTP
from Silo import EnregistrementComposition

__all__ = ["CommandeHTTP"]

class CommandeHTTP:

    tailleTampon = 1048576  # 1 Mo

    ressources = {
        re.compile(r"\/page\/?$"): "./page.html"  # l'outil de conception des requêtes
    }

    expReg_requete = re.compile(
        r"([a-z]+)\s+(.*)\s+HTTP\/1.[01]$", re.I
    )
    expReg_entete = re.compile(
        r"([^\:]+)\s*\:\s*(.*)$", re.I
    )

    sautLigne = "\n"
    sautLigneBin = b"\n"

    def __init__(self, client):
        self.client = client
        self.methode = None
        self.chemin = None
        self.entetes = {}
        self.reponse = tempfile.SpooledTemporaryFile(self.tailleTampon)
        self.corps = None
        self.etat = None
        self.uid = 0

    def traiterLigne(self, ligne):
        if self.methode is None:
            r = self.expReg_requete.match(ligne)
            if r is None:
                return False
            else:
                self.methode, self.chemin = r.groups()
                self.methode = self.methode.lower()
        else:
            r = self.expReg_entete.match(ligne)
            if r is None:
                return False
            else:
                cle, valeur = r.groups()
                self.entetes[cle.lower()] = valeur
        return True
    async def traiterChemin(self):
        if self.chemin is None:
            return False
        for rExpReg in self.ressources:
            r = rExpReg.match(self.chemin)
            if r is not None:
                await self.repondreFichier(self.ressources[rExpReg], r)
                return True
        return False

    async def repondreFichier(self, chemin, resultat):
        if os.path.isfile(chemin):
            with open(chemin, "r", encoding="utf-8") as f:
                await self.repondre(fichier=f)
        else:
            await self.repondre(codeHTTP=404, messageHTTP="bad ressource")
        return True

    async def repondreLigne(self, ligne, saut=True):
        if type(ligne) == str:
            ligne = ligne.encode("utf-8")
        if saut is True:
            ligne = ligne + self.sautLigneBin
        self.client.ecrivain.write(ligne)

    async def repondre(self, codeHTTP=200, messageHTTP="OK", entetes={}, fichier=None, corpsType="text/html"):
        if fichier is None:
            fichier = self.reponse
        fichier.seek(0, 2)
        tailleReponse = fichier.tell()
        await self.repondreLigne("HTTP/1.0 %s %s" % (codeHTTP, messageHTTP))
        for cle in entetes:
            await self.repondreLigne("%s: %s" % (cle, entetes[cle]))
        if corpsType is not None:
            await self.repondreLigne("content-type: %s; charset=UTF-8" % corpsType)
        if tailleReponse < 0:
            await self.repondreLigne("content-length: %s" % len(corps))
        await self.repondreLigne("")
        await self.repondreLigne("")
        await self.client.ecrivain.drain()
        i = 0
        fichier.seek(0)
        while True:
            p = fichier.read(64)
            if p == b"" or p == "":
                break
            await self.repondreLigne(p, saut=False)
            if i % 11 == 0:
                 await self.client.ecrivain.drain()
            i += 1
        await self.client.ecrivain.drain()

    async def executer(self):
        try:
            if "uid" in self.entetes:
                self.uid = int(self.entetes, 16)  # hex -> int
            if hasattr(self, "cmd_%s" % self.methode):
                if (await getattr(self, "cmd_%s" % self.methode)()) is not True:
                    await self.repondre()
            else:
                 await self.repondre(codeHTTP=400, messageHTTP="bad request")
        except Exception:
            await self.repondre(codeHTTP=400, messageHTTP="bad request")

    async def recupererCorps(self):
        if "content-length" not in self.entetes:
            return False
        else:
            taille = int(self.entetes["content-length"])
            self.corps = (await self.client.lecteur.read(taille))
        return True

    async def attendre(self):
        self.enAttente = True
        while self.enAttente:
            await asyncio.sleep(0.1)

    async def cmd_get(self):
        self.client.silo.requetes.append(self)
        try:
           self.filtre = FiltreHTTP(self.entetes)
        except Exception as err:
           print("(err) CommandeHTTP->cmd:get :", err)
        await self.attendre()
        if self.etat is False:
           await self.repondre(codeHTTP=500, messageHTTP="error during execution")
        else:
            await self.repondre(corpsType="text/triplet")
        return True

    async def cmd_delete(self):
        self.client.silo.transactions.append(("suppression", self))
        try:
           self.filtre = FiltreHTTP(self.entetes)
        except Exception as err:
           print("(err) CommandeHTTP->cmd:delete :", err)
        await self.attendre()
        if self.etat is False:
           await self.repondre(codeHTTP=500, messageHTTP="error during execution")
        return True if self.etat else False

    async def cmd_post(self):
        if "content-length" not in self.entetes:
            await self.repondre(codeHTTP=400, messageHTTP="bad request")
            return True
        self.entetes["content-length"] = int(self.entetes["content-length"])
        _triplets = TripletsHTTP(self.client)
        await _triplets.traiterCorps(self.entetes["content-length"])
        if _triplets.etat is False:
            await self.repondre(codeHTTP=400, messageHTTP="bad request")
            return True
        self.corps = _triplets
        self.client.silo.transactions.append(("ecriture", self))
        await self.attendre()
        if self.etat is False:
            await self.repondre(codeHTTP=500, messageHTTP="error during execution")
            return True
        return False

