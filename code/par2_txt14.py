import re
import datetime
import time
import queue
import threading

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

def tester_thread_travailler_unique(motifs, triplets):
    reponses = []
    for motif in motifs:
        reponse = []
        for triplet in triplets:
            if tester(motif, triplet):
                reponse.append(triplet)
        reponses.append(reponse)
    return reponses

def tester_thread_travailler(i, queue_a_traiter, verrou):
    print("thread n°%s" % i)
    y = 0
    while verrou.is_set():
        # je triche un peu... je ne garde pas les résultats !
        try:
            tester_thread_travailler_unique(*queue_a_traiter.get(timeout=0.1))
            y += 1
            if y % 10013 == 0:
                print("thread n°%s - pallier : %s" % (i, y))
        except queue.Empty:
            time.sleep(0.5)

debut = datetime.datetime.now()
queue_a_traiter = queue.Queue()
Threads = []
verrou = threading.Event()
verrou.set()

for i in range(0, 25):  # 25 travailleurs sans relâche, travaillent…
    t = threading.Thread(
        target=tester_thread_travailler,
        args=(i, queue_a_traiter, verrou)
    )
    t.start()
    Threads.append(t)

for i in range(0, nbre):
    queue_a_traiter.put(
        (
            motifs,
            triplets
        )
    )
verrou.clear()

for t in Threads:
    t.join()

fin = datetime.datetime.now()
print("tester avec des threads :", fin - debut)
