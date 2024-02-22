import re

expReg_requete = re.compile(
    r"([a-z]+)\s+(.*)\s+HTTP\/1.[01]$",  # j’ai rajouté les parenthèses : le groupe devient « capturant » !
    re.I
)
