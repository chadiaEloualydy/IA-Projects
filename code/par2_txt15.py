import re
import datetime

nbre = 1000000

motifs = (
    (
        "<http://www.polymtl.ca/profs#MichelGagnon>",
        None,
        None
    ),
    (
        "<http://www.polymtl.ca/profs#MichelGagnon>",
        re.compile("\#worksAt\>?$", re.I),
        None
    ),
)

triplets = (
    (
        "<http://www.polymtl.ca/profs#MichelGagnon>",
        "<http://www.polymtl.ca/vocab#hasHomePage>",
        "<http://www.professeurs.polymtl.ca/michel.gagnon>"
    ),
    (
        "<http://www.polymtl.ca/profs#MichelGagnon>",
        "<http://www.polymtl.ca/vocab#worksAt>",
        "<http://www.dgi.polymtl.ca>"
    ),
    (
        "<http://www.polymtl.ca/profs#MichelGagnon>",
        "<http://www.polymtl.ca/vocab#name>",
        '"Michel Gagnon"'
    )
)

def tester(motifs, triplets):
    reponses = []
    for motif in motifs:
        reponse = []
        for triplet in triplets:
            for t, m in zip(triplet, motif):
                if m is None:
                    continue
                elif type(m) == str:
                    if t != m:
                        break
                elif isinstance(m, re.Pattern):
                    if m.search(t) is None:
                        break
            else:
                reponse.append(triplet)
        reponses.append(list(reponse))
    return list(reponses)

debut = datetime.datetime.now()
for i in range(0, nbre):
    tester(motifs, triplets)
fin = datetime.datetime.now()
print("tester :", fin - debut)
