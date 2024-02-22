async def repondre(self, codeHTTP=200, messageHTTP="OK", entetes={}, corps=None):
    reponse = [
        "HTTP/1.0 %s %s" % (codeHTTP, messageHTTP)
    ]
    for cle in entetes:
        reponse.append(
            "%s: %s" % (cle, entetes[cle])
        )
    if corps is not None:
        reponse.append(
            "content-length: %s" % len(corps)
        )
    reponse.append("")
    reponse.append(corps)
    print(reponse)
    self.client.ecrivain.write(
        ("\n".join(reponse)).encode("utf-8")
    )
    await self.client.ecrivain.drain()
