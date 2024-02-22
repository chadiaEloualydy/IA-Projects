import asyncio
import re

class ClientHTTP:

    expReg_requete = re.compile(
        r"([a-z]+)\s+.*\s+HTTP\/1.[01]$",
        re.I
    )
    expReg_entete = re.compile(
        r"([^\:]+)\s*\:\s*(.*)$",
        re.I
    )

    def __init__(self, lecteur, ecrivain):
        self.lecteur, self.ecrivain = lecteur, ecrivain
        self.methode = None
        self.entetes = {}

    async def dialoguer(self):
        while True:
            ligne = await self.lecteur.readline()
            ligne = ligne.decode("utf-8").strip()
            if ligne == "":
                break
            if self.methode is None:
                r = self.expReg_requete.match(ligne)
                if r is None:
                    return (await self.reponse(400, "bad request"))
                else:
                    self.methode = r.group(0)
            else:
                r = self.expReg_entete.match(ligne)
                if r is None:
                    return (await self.reponse(400, "bad request"))
                else:
                    cle, valeur = r.groups()
                    self.entetes[cle.lower()] = valeur
        print(self.methode, self.entetes)
        await self.reponse(200, "OK")
        print("Close the connection")

    async def reponse(self, code, message):
        self.ecrivain.write(("HTTP/1.0 %s %s" % (code, message)).encode("utf-8"))
        await self.ecrivain.drain()

async def handle_echo(reader, writer):
    c = ClientHTTP(
        reader,
        writer
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
