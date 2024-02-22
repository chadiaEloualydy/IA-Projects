async def dialoguer(self):
    commande = self.formatDialogue(self)
    while True:
        ligne = await self.recupereLigne()
        if ligne == "":
            break
        if commande.traiterLigne(ligne) is False:
            return (await commande.repondre(400, "bad request"))
        if (await commande.traiterChemin()) is False:
            # print(commande.methode, commande.chemin, commande.entetes)
            await commande.repondre(200, "OK")
    print("Close the connection")
