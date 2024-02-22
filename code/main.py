import asyncio
from Client import Client
from CommandHTTP import CommandeHTTP
from Silo import Silo, EnregistrementComposition

async def connexion_acceptee(lecteur, ecrivain):
    global ObjSilo
    try:
        c = Client(
            ObjSilo,
            lecteur,
            ecrivain,
            CommandeHTTP
        )
        await c.dialoguer()
    except Exception as err:
        print("exception non-gérée pour un client : ", err)
    finally:
        try:
            ecrivain.close()
        except Exception:
            pass

async def lancement(classeSilos, fChemin):
    global ObjSilo, Serveur
    ObjSilo = classeSilos(fChemin)
    Serveur = await asyncio.start_server(
        connexion_acceptee,
        '127.0.0.1',
        8888
    )
    print("Service sur %s:%s " % Serveur.sockets[0].getsockname())
    async with Serveur:
        ObjSilo.tache = asyncio.create_task(ObjSilo.executer())
        await Serveur.serve_forever()

if __name__ == "__main__":
    try:
        m = lancement(
            Silo,
            "./silo.prod"  # penser à le créer avant de démarrer le serveur
        )
        asyncio.run(m)
    except KeyboardInterrupt:
        pass
