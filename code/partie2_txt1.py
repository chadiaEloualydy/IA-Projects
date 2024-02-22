import re

t = """<http://example.org/arnaud#me>\t<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>\t<http://xmlns.com/foaf/0.1/Person>
<http://example.org/arnaud#me>\t<http://xmlns.com/foaf/0.1/knows>\t<http://example.org/béatrice#me>
<http://example.org/arnaud#me>\t<http://schema.org/birthDate>\t"1990-07-14"^^<http://www.w3.org/2001/XMLSchema#date>
<http://example.org/arnaud#me>\t<http://xmlns.com/foaf/0.1/topic_interest>\t<http://www.wikidata.org/entity/Q12418>
<http://www.wikidata.org/entity/Q12418>\t<http://purl.org/dc/terms/title>\t"La Joconde"
<http://www.wikidata.org/entity/Q12418>\t<http://purl.org/dc/terms/creator>\t<http://fr.dbpedia.org/resource/Léonard_de_Vinci>
<http://data.europeana.eu/item/04802/243FA8618938F4117025F17A8B813C5F9AA4D619>\t<http://purl.org/dc/terms/subject>\t<http://www.wikidata.org/entity/Q12418>"""


def trouver(chaine):
    return re.match(
        "^(?P<subject>[^\t]+)\t(?P<predicate>[^\t]+)\t(?P<object>[^\t]+)$",
        chaine,
        re.I
    ).groupdict()

try:
    pas = 10
    position = 0
    data = ""
    triplets = []
    while True:
        d = t[position:position+pas]
        if d=="":
            break
        else:
            data += d
            if "\n" in data:
                ligne, data = data.split( "\n", 1 )
                triplets.append(
                    trouver( ligne )
                )
            position += pas

    if data!="":
        triplets.append( trouver( data ) )
    print( "requête valide :", triplets )
except Exception:
    print("requête invalide")
finally:
    print("... poursuivre ...")
