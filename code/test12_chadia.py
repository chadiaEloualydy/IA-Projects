import asyncio
import re
import os

class CommandeHTTP:
    ressources = {
        re.compile(r"\/page\/?$"): "./page.html"
    }

    expReg_requete = re.compile(r"([a-z]+)\s+(.*)\s+HTTP\/1.[01]$", re.I)
    expReg_entete = re.compile(r"([^\:]+)\s*\:\s*(.*)$", re.I)

    def __init__(self, client):
        self.client = client
        self.methode = None
        self.chemin = None
        self.entetes = {}

    def traiterLigne(self, ligne):
        if self.methode is None:
            r = self.expReg_requete.match(ligne)
            if r is None:
                return False
            else:
                self.methode, self.chemin = r.groups()
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
        return await self.repondre(codeHTTP=404, messageHTTP="bad resource")

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
        print(reponse)
        self.client.ecrivain.write(("\n".join(reponse)).encode("utf-8"))
        await self.client.ecrivain.drain()

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
                await commande.repondre()
        print("Close the connection")

async def handle_echo(reader, writer):
    c = Client(reader, writer, CommandeHTTP)
    await c.dialoguer()
    writer.close()

async def main():
    server = await asyncio.start_server(handle_echo, '127.0.0.1', 8888)
    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')
    async with server:
        await server.serve_forever()

asyncio.run(main())
