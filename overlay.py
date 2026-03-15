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
    coeur= pygame.transform.scale(coeur, (125,125))
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
    posecrany = HAUTEUR - 80
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



#creation de la barre de vie
def hud_life(fenetre, LARGEUR, HAUTEUR, hp_cur, hp_max, police, coeur):
    #données
    x= LARGEUR -570
    y= 50
    Cyan= (122,252,194)
    Gris= (60,70,70)
    #création de rectangle
    rect_nb_totale= 25
    rect_H= 50
    rect_L= 15
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

