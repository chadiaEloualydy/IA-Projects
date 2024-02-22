async def traiterChemin(self):
    for rExpReg in self.ressources:
        r = rExpReg.match(self.chemin)
        if r is not None:
            await self.repondreFichier(self.ressources[rExpReg], r)
            return True
    return False

async def repondreFichier(self, chemin, resultat):
    if os.path.isfile(chemin):  # pensez à ajouter « import os »
        with open(chemin, "r") as f:
            r = f.read().encode("utf-8")
            await self.repondre(200, "correct ressource")
            # les quelques lignes ci-dessous peuvent poser problème :
            # nous verrons plus tard pourquoi
            self.client.ecrivain.write(
                ("Content-length: %s\n" % len(r)).encode("utf-8")
            )
            self.client.ecrivain.write("\n".encode("utf-8"))
            self.client.ecrivain.write(r)
            await self.client.ecrivain.drain()
            return True
    return (await self.repondre(404, "bad ressource"))
    return True
