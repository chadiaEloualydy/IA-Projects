import re
from Silo import Silo , EnregistrementComposition

__all__ = ["FiltreHTTP",]

class FiltreHTTP:

    def __init__(self, entetesHTTP):
        self.liste = {}
        global EnregistrementComposition
        for cle in EnregistrementComposition:
            if cle in entetesHTTP:
                if f"{cle}_regexp" in entetesHTTP:
                    self.liste[cle] = re.compile(entetesHTTP[cle], re.I)
                else:
                    self.liste[cle] = entetesHTTP[cle]
            else:
                self.liste[cle] = None

    async def deduire(self, commande, index, enregistrement):
        try:
            if commande.uid != index["uid"]:
                return False
            for cle in enregistrement:
                if await self.tester(cle, enregistrement[cle]) is False:
                    return False
            return True
        except Exception as err:
            print("(err) Filtre->deduire :", err)
            return False

    async def tester(self, cle, chaine):
        if cle not in self.liste:
            return False
        if self.liste[cle] is None:
            return True
        if type(self.liste[cle]) == re.Pattern:
            r = self.liste[cle].search(chaine)
            if r is not None:
                return True
        else:
            if self.liste[cle] == chaine:
                return True
        return False
