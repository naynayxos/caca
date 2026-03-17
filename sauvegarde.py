import json
from prerequis import texture

FICHIER = "sauvegarde.json"

def sauvegarder(partie, niveau_actuel, modifs_etage, joueur):  # collecte les données et les sauvegarde dans un fichier json
    data = {
        "seed": partie, 
        "niveau_actuel": niveau_actuel,
        "joueur": {
            "x": joueur.rect.centerx,
            "y": joueur.rect.centery,
            "hp": joueur.hp,
            "munition": joueur.munition,
            "arsenal": joueur.arsenal,
            "endurance": joueur.endurance,
        },
        "modifs": {str(k): v for k, v in modifs_etage.items()} # convertit les clés en chaînes de caractères pour être compatibles avec le fornmat
    }
    f = open(FICHIER, "w")
    json.dump(data, f, indent=2) # indent=2 pour ajouter des espaces pour la lisibilité
    f.close()
    print("Partie sauvegardée.")

def charger():
    try:
        f = open(FICHIER, "r")
        data = json.load(f)
        f.close()
        return data
    except FileNotFoundError:
        return None

def appliquer_modifs(objets, modifs):
    if not modifs:
        return objets
    objetsreste = []
    for obj in objets:
        key = f"{obj.rect.x}-{obj.rect.y}"
        if key in modifs:
            if modifs[key] == "S":
                continue
            if modifs[key] == "M":
                obj.type = "munition"
                obj.texture = texture("munition.png", (90, 90), transparente=True)
                obj.hitbox = obj.rect
        objetsreste.append(obj)
    return objetsreste
