import pygame
import random
import joueur
import filtre

#intialisation des éléments;
def overlay_HUD():
    police=pygame.font.Font("ressource/police.ttf", 40)
    hudmode= pygame.image.load("ressource/HUD_mc_V2.png").convert_alpha()
    hudinventaire=pygame.image.load("ressource/HUD_inventaire.png").convert_alpha()
    coeur= pygame.image.load("ressource/coeur_hp.png").convert_alpha()
    coeur= pygame.transform.scale(coeur, (110,110))
    inventaire=False  #Ferme de base
    return police, hudmode, hudinventaire, inventaire, coeur

def onventaire(fenetre, inventaire, hudinventaire, LARGEUR, HAUTEUR):
    if inventaire:
        #Centre l'inventaire
        surf= hudinventaire.get_rect()
        surf.center=(LARGEUR//2,HAUTEUR//2)
        fenetre.blit(hudinventaire, surf)

#Mode HUD texte & élément;
def mode_texte(fenetre, m_combat, enpause, police, hudmode, inventaire):
    fenetre.blit(hudmode,(10,10))
    if enpause :
        Texte = "PAUSE"
    elif inventaire:
        Texte= "INVENTAIRE"
    elif m_combat==True:
        Texte= "COMBAT"
    else:
        Texte="EXPLORATION"
    surface=police.render(Texte, False, (255,255,255))
    surf_rec=surface.get_rect()
    surf_rec.center=(10+hudmode.get_width()//2, 10+hudmode.get_height()//2)
    fenetre.blit(surface, surf_rec)

def munition(fenetre, joueur, police, img, HAUTEUR):
    #Si on a balle texte blanc, sinon rouge
    if joueur.munition > 0:
        texte = police.render(f"x{joueur.munition}", True, (255,255,255))
    else:
        texte = police.render("x0", True, (230,10,10))
    posx = 10
    posy = HAUTEUR - 175
    if img is not None:
        fenetre.blit(img, (posx, posy))
    #Afficher texte a coté
    fenetre.blit(texte, (posx + 75, posy+15))

def endurance(fenetre, joueur, course, img, HAUTEUR, LARGEUR, fondu):
    if fondu <= 0:
        return
    largeur = 200
    hauteur = 20
    #Position sur l'ecran
    posecranx = LARGEUR - 250
    posecrany = HAUTEUR - 65
    #Surface pour la barre
    barre = pygame.Surface((300, 60), pygame.SRCALPHA)
    posx = 10
    posy = 20

    #Calcul largeur de la barre
    largeurbarre = (joueur.endurance / joueur.maxcourse)*largeur
    if largeurbarre < 0:
        largeurbarre = 0
    #Couleur
    couleurfond = (40,40,45,fondu)
    couleurbord = (200,200,200,fondu)
    #Barre rouge si endurance <=25
    if joueur.endurance > 25:
        couleur = (0,200,255, fondu)
    else:
        couleur = (255,50,50, fondu) 
    
    #Dessine barre avec fond et bordure
    pygame.draw.rect(barre, couleurfond, (posx, posy, largeur, hauteur), border_radius=8)
    #Dessine jauge de la barre
    if largeurbarre > 0:
        pygame.draw.rect(barre, couleur, (posx, posy, largeurbarre, hauteur), border_radius=8)
    #Dessine contour
    pygame.draw.rect(barre, couleurbord, (posx, posy, largeur, hauteur), 2, border_radius=8)
    
    #Effet flamme quand course
    if course and largeurbarre > 0:
        for i in range(10): #10 etincelle
            x = random.randint(0,25)
            y = random.randint(-5, hauteur+5)
            taille=random.randint(2,4)
            #Choix entre ces couleurs
            couleurflamme = random.choice([(255,150,0),(255,200,0),(0,200,255),(255,255,255)])
            cflamme = (couleurflamme[0],couleurflamme[1],couleurflamme[2],fondu)
            #Dessine flamme sur la barre
            flammex = posx + largeurbarre + x - 10
            flammey = posy + y
            pygame.draw.circle(barre, couleurflamme, (int(flammex), int(flammey)), taille)
    
    #Le joueur invisible
    if img is not None and largeurbarre > 0:
        taillejoueur = 28
        joueur = pygame.transform.scale(img, (taillejoueur, taillejoueur)).convert_alpha()
        joueur.set_alpha(min(170, fondu)) #Transparent
        #Au niveau de la jauge
        joueurx = posx + largeurbarre - (taillejoueur//2)
        joueury = posy + (hauteur//2) - (taillejoueur//2)
        barre.blit(joueur, (joueurx, joueury))
    fenetre.blit(barre, (posecranx, posecrany))

def arme_overlay(fenetre, joueur, image, HAUTEUR, present):
    posx = 10+present
    posy = HAUTEUR - 95
    #Recupere l'image adapté a l'arme utilisé du dictionnaire
    imgarme = image.get(joueur.arsenal)
    if imgarme is not None:
        fenetre.blit(imgarme, (posx, posy))

def lampe(fenetre, joueur, police, HAUTEUR):
    x = 10
    y = HAUTEUR - 230
    if not joueur.possedelampe:
        texte = police.render("Pas de lampe", True, (150,15,0,150))
        fenetre.blit(texte, (x, y))
        return
    p = int((joueur.pile / joueur.pilemax) * 100)
    if p > 50:
        couleur = (100,220,100)
    elif p > 20:
        couleur = (255,180,30)
    else:
        couleur = (220,50,50)
    if joueur.lumiereallumee:
        etat = "ON"
    else:
        etat = "OFF"
    texte = police.render(f"Lampe: {etat} ({p}%)", True, couleur)
    fenetre.blit(texte, (x, y))
    largeur = 120
    hauteur = 8
    barre = pygame.Surface((largeur, hauteur), pygame.SRCALPHA)
    pygame.draw.rect(barre, (40,40,40,180), (0, 0, largeur, hauteur), border_radius=4)
    largeurbarre = int(p/100 * largeur)
    if largeurbarre > 0:
        pygame.draw.rect(barre, (*couleur, 220), (0, 0, largeurbarre, hauteur), border_radius=4)
    pygame.draw.rect(barre, (200,200,200,180), (0, 0, largeur, hauteur), 1, border_radius=4)
    fenetre.blit(barre, (x, y+28))


#creation de la barre de vie
def hud_life(fenetre, LARGEUR, HAUTEUR, hp_cur, hp_max, police, coeur):
    #données
    x= LARGEUR -460
    y= 50
    Cyan= (122,252,194)
    Gris= (60,70,70)
    #création de rectangle
    rect_nb_totale= 25
    rect_H= 32
    rect_L= 10
    rect_positif= int((hp_cur/hp_max)*rect_nb_totale)

    texte_sante= police.render("LIFE", True, Cyan)
    fenetre.blit(texte_sante,(x, y-40))

    for i in range(rect_nb_totale):
        rect_pos_x= x+ (i*(rect_L+ 5))
        if i< rect_positif:
            couleur= Cyan
        else:
            couleur = Gris

        pygame.draw.rect(fenetre, couleur,(rect_pos_x, y, rect_L, rect_H))
    
    L_tt= rect_nb_totale*(rect_L+5)
    #Ligne horizontale
    pygame.draw.line(fenetre, Cyan,(x, y + rect_H+5), (x+L_tt+55, y+rect_H+5),2)
    #texte pourcentage
    texte_hp = police.render(f"{int(hp_cur)}/{int(hp_max)}", True, Cyan)
    fenetre.blit(texte_hp,(x + L_tt-50, y + rect_H+10))
    #coeur affichage
    fenetre.blit(coeur,(x+L_tt-32, y-40))

def oxygene(fenetre, joueur, police, LARGEUR, HAUTEUR):
    largeur = 200
    hauteur = 16
    x = LARGEUR //2 - largeur//2
    y = HAUTEUR - 60
    CYAN = (122,252,194)
    oxy = max(0, joueur.oxygene/joueur.oxygenemax)
    #Texte O²
    texteoxy = police.render("O²", True, (180,180,255))
    fenetre.blit(texteoxy, (x-45, y-4))
    #Surface pour la barre
    barre = pygame.Surface((largeur, hauteur), pygame.SRCALPHA)
    #Fond de la barre
    pygame.draw.rect(barre, (30,30,60,180), (0, 0, largeur, hauteur), border_radius=6)
    #Remplissage de la barre
    if oxy > 0.3:
        couleur = (50,120,220, 220)
    elif oxy > 0.1:
        couleur = (220,150,30, 220)
    else:
        couleur = (200,30,30, 220)
    largeurbarre = int(oxy * largeur)
    if largeurbarre > 0:
        pygame.draw.rect(barre, couleur, (0, 0, largeurbarre, hauteur), border_radius=6)
    #Bordure de la barre
    pygame.draw.rect(barre, (180,180,255,200), (0, 0, largeur, hauteur), 2, border_radius=6)
    fenetre.blit(barre, (x, y))
    if oxy <= 0 and pygame.time.get_ticks() % 800 < 400: #Clignote quand à sec
        alerte = police.render("ASPHYXIE", True, (255,50,50))
        fenetre.blit(alerte, alerte.get_rect(center=(LARGEUR//2, y-35)))

def horloge(fenetre, police, heure, LARGEUR):
    DUREE = 28800 #Durée d'une journée en secondes
    heure = min(heure, DUREE)
    heurejeu = 6+ (heure / DUREE) * 14 #Commence à 6h
    heures = int(heurejeu)
    minutes = int((heurejeu - heures) * 60)
    #Couleur du texte qui change en fonction de l'heure
    restant = DUREE - heure
    if restant > 7200:
        couleur = (255,220,100)
    elif restant > 2880:
        couleur = (255,140,30)
    else:
        couleur = (255,50,50)
    texte = police.render(f"{heures:02d}:{minutes:02d}", True, couleur)
    texte_rect = texte.get_rect(topright=(LARGEUR-20, 60))
    fond = pygame.Surface((texte_rect.width + 20, texte_rect.height + 10), pygame.SRCALPHA)
    fond.fill((0,0,0,140))
    fenetre.blit(fond, (texte_rect.x - 10, texte_rect.y - 5))
    fenetre.blit(texte, texte_rect)
    if heurejeu >= 18 and pygame.time.get_ticks() % 1000 < 500: #Clignote quand il fait nuit
        alerte = police.render("RENTRER AU VAISSEAU !", True, (255,50,50))
        fenetre.blit(alerte, alerte.get_rect(center=(LARGEUR//2, 30)))