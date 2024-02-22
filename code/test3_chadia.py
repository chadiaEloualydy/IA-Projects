import asyncio
import re

class CommandeHTTP:

    expReg_requete = re.compile(
        r"([a-z]+)\s+.*\s+HTTP\/1.[01]$",
        re.I
    )
    expReg_entete = re.compile(
        r"([^\:]+)\s*\:\s*(.*)$",
        re.I
    )

    def __init__(self, client):
        self.client = client
        self.methode = None
        self.entetes = {}

    def traiterLigne(self, ligne):
        if self.methode is None:
            r = self.expReg_requete.match(ligne)
            if r is None:
                return False
            else:
                self.methode = r.group(0)
        else:
            r = self.expReg_entete.match(ligne)
            if r is None:
                return False
            else:
                cle, valeur = r.groups()
                self.entetes[cle.lower()] = valeur
        return True

    async def repondre(self, code, message):
        self.client.ecrivain.write(("HTTP/1.0 %s %s" % (code, message)).encode("utf-8"))
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
                return (await commande.repondre(400, "bad request"))
            print(commande.methode, commande.entetes)
            await commande.repondre(200, "OK")
            print("Close the connection")

async def handle_echo(reader, writer):
    c = Client(
        reader,
        writer,
        CommandeHTTP
    )
    await c.dialoguer()
    writer.close()

async def main():
    server = await asyncio.start_server(
        handle_echo, '127.0.0.1', 8888)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()

asyncio.run(main())