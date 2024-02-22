import asyncio
import re
import os

class CommandeHTTP:

    ressources = {
        re.compile(r"\/page\/?$"): r"./page.html"
    }

    expReg_requete = re.compile(r"([a-z]+)\s+(.*)\s+HTTP\/1.[01]$", re.I)
    expReg_entete = re.compile(r"([^\:]+)\s*\:\s*(.*)$", re.I)

    def __init__(self, client):
        self.client = client
        self.methode = None
        self.chemin = None
        self.entetes = {}
        self.reponse = []

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
        for rExpReg in self.ressources:
            r = rExpReg.match(self.chemin)
            if r is not None:
                await self.repondreFichier(self.ressources[rExpReg], r)
                return True
        return False

    async def repondreFichier(self, chemin, resultat):
        if os.path.isfile(chemin):
            with open(chemin, "r") as f:
                await self.repondre(corps=f.read())
                return True
        return await self.repondre(codeHTTP=404, messageHTTP="bad ressource")

    async def repondre(self, codeHTTP=200, messageHTTP="OK", entetes={}, corps=None):
        reponse = [
            f"HTTP/1.0 {codeHTTP} {messageHTTP}"
        ]
        for cle in entetes:
            reponse.append(f"{cle}: {entetes[cle]}")
        if corps is not None:
            reponse.append(f"content-length: {len(corps)}")
        reponse.append("")
        reponse.append(corps)
        self.client.ecrivain.write(("\n".join(reponse)).encode("utf-8"))
        await self.client.ecrivain.drain()

    async def executer(self):
        if hasattr(self, f"cmd_{self.methode}"):
            await getattr(self, f"cmd_{self.methode}")()
        else:
            await self.repondre(codeHTTP=400, messageHTTP="bad request")

    async def attendre(self):
        self.enAttente = True
        while self.enAttente:
            print("un client attend", self)
            await asyncio.sleep(1)

    async def cmd_get(self):
        global ObjSilo
        ObjSilo.requetes.append(self)
        await self.attendre()
        await self.repondre(corps="\n".join(self.reponse))

class Client:
    def __init__(self, lecteur, ecrivain, formatDialogue):
        self.lecteur, self.ecrivain = lecteur, ecrivain
        self.formatDialogue = formatDialogue

    async def recupereLigne(self):
        return (await self.lecteur.readline()).decode("utf-8").strip()

    async def dialoguer(self):
        commande = self.formatDialogue(self)
        while True:
            ligne = await self.recupereLigne()
            if ligne == "":
                break
            if commande.traiterLigne(ligne) is False:
                return await commande.repondre(codeHTTP=400, messageHTTP="bad request")
            if await commande.traiterChemin() is False:
                await commande.executer()
        print("Close the connection", self)

async def handle_echo(reader, writer):
    c = Client(reader, writer, CommandeHTTP)
    await c.dialoguer()
    writer.close()

####################################################

ObjSilo = None

async def main(_silos):
    global ObjSilo
    server = await asyncio.start_server(handle_echo, '127.0.0.1', 8888)
    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')
    ObjSilo = _silos()
    async with server:
        await server.serve_forever()

class Silo:
    nbreMaxRequetesSimultanee = 10

    def __init__(self):
        self.requetes = []
        self.transactions = []
        self.fSilo = open("silo.test.txt", "r")
        self.tache = asyncio.create_task(self.executer())

    async def executerRequete(self, commande, portion):
        if portion % 2 == 0:
            commande.reponse.append(str(portion))

    def recupererRequetes(self):
        _requetes = []
        for requete in self.requetes:
            _requetes.append(requete)
            self.requetes.remove(requete)
            if len(_requetes) >= self.nbreMaxRequetesSimultanee:
               break
        return _requetes

    async def recupererPortion(self):
        return self.fSilo.readline()

    async def executer(self):
        while True:
            try:
                if len(self.requetes) == 0:
                    print("Silo : pas encore de client à exécuter")
                    await asyncio.sleep(0.5)
                else:
                    self.fSilo.seek(0)  # début du fichier
                    requetes = self.recupererRequetes()
                    print("Silo : requêtes en cours de réalisation", requetes)
                    while True:
                        p = (await self.recupererPortion())
                        if p == "":
                            break  # la fin du fichier détectée
                        else:
                            p = int(p)
                            for requete in requetes:
                                await self.executerRequete(requete, p)
                            for requete in requetes:
                                requete.enAttente = False
            except Exception as err:
                print(err)

if __name__ == "__main__":
    try:
        m = main(Silo)
        asyncio.run(m)
    except KeyboardInterrupt:
        pass

