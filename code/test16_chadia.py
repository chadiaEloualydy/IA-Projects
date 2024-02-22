# n’oubliez pas qu’au-dessus, il y a le code vu précédemment
import asyncio
import test15_chadia
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
    def __init__(self):
        self.commandes = []
        self.tache = asyncio.create_task(self.executer())

    async def executerCommande(self, commande):
        print("attendre 3 secondes pour ", commande)
        await asyncio.sleep(3)
        commande.enAttente = False

    async def executer(self):
        while True:
            _commandes = []
            for c in self.commandes:
                _commandes.append(c)
                self.commandes.remove(c)
            for c in _commandes:
                print("traitement de", c)
                await self.executerCommande(c)
            print("silo executer")
            await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        m = main(Silo)
        asyncio.run(m)
    except KeyboardInterrupt:
        pass
