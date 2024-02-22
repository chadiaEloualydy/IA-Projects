import test16_chadia
async def attendre(self):
    self.enAttente = True
    while self.enAttente:
        print("un client attend", self)
        await asyncio.sleep(1)

async def cmd_get(self):
    global ObjSilo
    ObjSilo.commandes.append(self)
    await self.attendre()
    await self.repondre(corps="youpi tralala")

