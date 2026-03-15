import pygame
import math

#Couleur
NUIT = (10, 10, 20)
NUIT_ALPHA = 245  #cacher la map
CONE_ANGLE  = 30
CONE_PORTEE = 480

def cone(portee, angle, couleur, couche = 80):
    #On calcul la porté de la lumiere
    taille = portee*2
    lumiere = pygame.Surface((taille,taille), pygame.SRCALPHA)
    #On dit qu'il demarre au niveau du joueur
    ix = iy = portee
    rayon = math.radians(angle)
    r,g,b =couleur
    #Donne le cote arrondi au cone
    rond = max(32, int(angle*3))
    for i in range(couche, 0, -1):
        dist = i/couche #De 1 (bout du cone) a 0 (proche du joueur)
        rayoncouche = int(portee*dist)
        #Degrade plus on est proche du joueur alors alpha = 255 sinon 0
        alpha = int(255*(1-dist))
        #Cone de rayon
        points= [(ix,iy)]
        for k in range(rond+1):
            #Angle en degres
            anglee = -rayon+(2*rayon*k/rond)
            kx = ix + math.cos(anglee)*rayoncouche
            ky = iy + math.sin(anglee)*rayoncouche
            points.append((kx,ky))
        if len(points) >= 3:
            pygame.draw.polygon(lumiere, (r, g, b, alpha), points)
    return lumiere

class Lumiere:
    def __init__(self, largeur, hauteur):
        self.largeur = largeur
        self.hauteur = hauteur
        #Calcul le cone
        self.cone = cone(CONE_PORTEE, CONE_ANGLE, (255, 240, 200))
        self.angle = None
        self.rotation = None

    def redimenssione(self, largeur, hauteur):
        self.largeur = largeur
        self.hauteur = hauteur

    def conerota(self, anglejoueur):
        #Pivote le cone vers l'endroit ou regarde le joueur
        anglerota = anglejoueur
        if anglerota != self.angle:
            self.rotation = pygame.transform.rotate(self.cone, anglerota)
            self.angle = anglerota
        return self.rotation
    
    def appliquer(self, ecran, joueur, mode_combat=False):
        #Si mode combat alors aps de masque noir
        if mode_combat:
            return
        #Active lampe apres generation map
        ex, ey = self.largeur, self.hauteur
        cx,cy = ex//2, ey//2
        masque = pygame.Surface((ex,ey), pygame.SRCALPHA)
        masque.fill((*NUIT, NUIT_ALPHA))
        if joueur.lumiereallumee:
            cone = self.conerota(joueur.angleactuel)
            rectcone = cone.get_rect(center=(cx,cy))
            #BLEND_RGBA_SUB ca retire le maque noir
            masque.blit(cone, rectcone, special_flags=pygame.BLEND_RGBA_SUB)
            masque.blit(cone, rectcone, special_flags=pygame.BLEND_RGBA_SUB)
            masque.blit(cone, rectcone, special_flags=pygame.BLEND_RGBA_SUB)
        ecran.blit(masque, (0,0))