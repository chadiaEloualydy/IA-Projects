import re
import datetime
import asyncio

nbre = 1000000

motifs = (
    ("<http://www.polymtl.ca/profs#MichelGagnon>", None, None),
    ("<http://www.polymtl.ca/profs#MichelGagnon>", re.compile("\#worksAt\>?$", re.I), None),
)

triplets = (
    ("<http://www.polymtl.ca/profs#MichelGagnon>", "<http://www.polymtl.ca/vocab#hasHomePage>",
     "<http://www.professeurs.polymtl.ca/michel.gagnon>"),
    ("<http://www.polymtl.ca/profs#MichelGagnon>", "<http://www.polymtl.ca/vocab#worksAt>",
     "<http://www.dgi.polymtl.ca>"),
    ("<http://www.polymtl.ca/profs#MichelGagnon>", "<http://www.polymtl.ca/vocab#name>", '"Michel Gagnon"')
)

def tester(motif, triplet):
    for t, m in zip(triplet, motif):
        if m is None:
            continue
        elif type(m) == str:
            if t != m:
                return False
        elif isinstance(m, re.Pattern):
            if m.search(t) is None:
                return False
    else:
        return True

async def tester_async(motif, triplet):
    return tester(motif, triplet)

debut = datetime.datetime.now()

async def travailleur(queue_a_traiter):
    while True:
        motifs, triplets = await queue_a_traiter.get()
        resultats = []
        for motif in motifs:
            resultat = []
            for triplet in triplets:
                resultat.append(
                    await tester_async(motif, triplet)
                )
            resultats.append(resultat)
        queue_a_traiter.task_done()

async def main(nbre):
    queue_a_traiter = asyncio.Queue()
    for i in range(0, nbre):
        queue_a_traiter.put_nowait(
            (
                motifs,
                triplets
            )
        )
    taches_travailleurs = []
    for i in range(0, 5):
        taches_travailleurs.append(
            asyncio.create_task(travailleur(queue_a_traiter))
        )
    await queue_a_traiter.join()

asyncio.run(main(nbre))

fin = datetime.datetime.now()
print("tester avec asyncio :", fin - debut)
