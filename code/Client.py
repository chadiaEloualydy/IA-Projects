__all__ = ["Client",]

class Client:

    def __init__(self, silo, lecteur, ecrivain, formatDialogue):
        self.silo = silo
        self.lecteur = lecteur
        self.ecrivain = ecrivain
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
                return (await commande.repondre(codeHTTP=400, messageHTTP="bad request"))
            if (await commande.traiterChemin()) is False:
                await commande.executer()
