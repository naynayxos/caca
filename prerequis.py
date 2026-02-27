import pygame
import os 
import math

ZOOM = 180
LARGEURMAP,HAUTEURMAP= 50,50
VITESSEJOUEUR = 10
VIDE = 2
MUR = 1
SOL = 0
NUIT = (15,15,25)
ASCENCEUR = 3

#assets
def texture(nom,taille = None, transparente = False):
    chemin = os.path.join("ressource", nom)
    try:
        img= pygame.image.load(chemin)
        if transparente:
            img.set_colorkey((255,255,255))
        if taille:
            w,h= taille
            img= pygame.transform.scale(img, (w, h))
        return img.convert_alpha()
    except:
        return None

#Effet Lumiere
def lumiere(rayon):
    t = rayon*2.5
    s = pygame.Surface((t,t),pygame.SRCALPHA)
    c = (t//2,t//2)
    #plusieur cercle pour tamiser
    for i in range(rayon//2,0,-2):
        a = int(100*(i/(rayon//2)))
        if a>0:
            pygame.draw.circle(s,(255,240,200,5),c,i)
    longueurcone = rayon
    angless=30
    etape = 100 #Puissance dégradé
    for i in range(etape):
        distance = (i/etape)*longueurcone
        largeur= int(distance*math.tan(math.radians(angless)))
        posx = c[0]+distance
        posy = c[1]
        p=60*(1-(i/etape))
        if largeur>0:
            brosse = pygame.Surface((largeur*2,largeur*2), pygame.SRCALPHA)
            pygame.draw.circle(brosse,(255,250,220,int(p)),(largeur,largeur),largeur)
            dist = brosse.get_rect(center=(posx,posy))
            s.blit(brosse,dist,special_flags=pygame.BLEND_RGBA_ADD)
    return s

def angletrace(c, t, f):
    d = (t-c+180)%360-180
    return c+d*f

#Collision
def obstacle(rect_joueur,grille):
    obstacle=[]
    casex=int(rect_joueur.centerx/ZOOM)
    casey=int(rect_joueur.centery/ZOOM)
    for y in range(casey-2,casey+3):
        for x in range(casex-2,casex+3):
            if 0 <= x < LARGEURMAP and 0 <= y < HAUTEURMAP:
                case = grille[y][x]
                if case == MUR or case == VIDE:
                    rect_mur = pygame.Rect(x*ZOOM,y*ZOOM,ZOOM,ZOOM)
                    obstacle.append(rect_mur)
    return obstacle