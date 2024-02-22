import re

 # pour mémoire, re.I indique lors de la compilation de l’expression régulière,
 # de ne pas prendre en compte la casse
expReg_requete = re.compile(
    r"([a-z]+)\s+.*\s+HTTP\/1.[01]$",
    re.I
 )

expReg_entete = re.compile(
    r"([^\:]+)\s*\:\s*(.*)$", 
    re.I
 )