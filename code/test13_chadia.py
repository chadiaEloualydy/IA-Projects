async def executer(self):
    if hasattr(self, "cmd_%s" % self.methode):
        await getattr(self, "cmd_%s" % self.methode)()
    else:
        return await self.repondre(codeHTTP=400, messageHTTP="bad request")
