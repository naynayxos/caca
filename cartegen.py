import pygame
import random
import math
from prerequis import *
from prerequis import texture

class Objet:
    def __init__(self,x,y,name,type,size=None):
        #Position et taille objet
        self.rect = pygame.Rect(x,y,ZOOM,ZOOM)
        self.texture=texture(name,size,transparente=True)
        self.type = type   
        #Reduction hitbox si c'est un meuble
        if type == "meuble":
            self.hitbox = self.rect.inflate(-20,-20)
        else:
            self.hitbox = self.rect
        
    def draw(self,surface, camera_x, camera_y):
        fenetre_x = self.rect.x + camera_x
        fenetre_y = self.rect.y + camera_y
        if self.texture:
            surface.blit(self.texture, (fenetre_x, fenetre_y))
        return fenetre_y+self.rect.height

def generer_objets(grille, salles):
    objets = []
    #Dictionnaire des types et probabilité d'affichage des objets
    types = [{'nom': 'caisse.png', 'type': 'meuble', 'proba': 0.2},
            {'nom': 'plante.png', 'type': 'plante', 'proba': 0.2},
            {'nom': 'meuble.png', 'type': 'meuble', 'proba': 0.2},
            {'nom': 'munition.png', 'type': 'munition', 'proba':0.1}]
    
    for salle in salles:
        for y in range(salle.top, salle.bottom):
            for x in range(salle.left, salle.right):
                #On place des objets que sur les sols
                if grille[y][x] == SOL:
                    #Verifie si mur au tour, si oui il y a 20% de chance d'avoir objet
                    if (grille[y+1][x] == MUR or grille[y-1][x] == MUR or grille[y][x+1] == MUR or grille[y][x-1] == MUR) and random.random() < 0.2:
                        #Objet au hasard
                        t = random.choice(types)
                        #Verifie proba d'apparition
                        if random.random() < t['proba']:
                            if t['type'] != 'munition':
                                taillemun = (ZOOM//2, ZOOM//2)
                            else:
                                taillemun = (ZOOM, ZOOM)
                            #Creation de l'objet
                            obj = Objet(x*ZOOM, y*ZOOM, t['nom'], t['type'], size=taillemun)
                            objets.append(obj)
    return objets

#couloir verticale
def c_vertical(grille, y1,y2,x):
    for y in range(min(y1,y2),max(y1,y2)+1):
        grille[y][x]=SOL

#couloir horizontal
def c_horizontal(grille, x1,x2,y):
    for x in range(min(x1,x2),max(x1,x2)+1):
        grille[y][x]=SOL

#generation map
def generemap():
    #Carte rempli de vide
    grille = []
    for y in range(HAUTEURMAP):
        ligne = []
        for x in range(LARGEURMAP):
            ligne.append(VIDE)
        grille.append(ligne)
    salles=[]
    distance_min =7
    distance_max = 10#Dstance entre les salles
    #Generation salle
    for k in range(80): #Nombre de salles a essayer de generer
        #Taille aléatoire
        w = random.randint(5,9)   
        h = random.randint(5,9)
        #Toute premiere salle au centre
        if not salles:
            x = LARGEURMAP//2 - w//2
            y = HAUTEURMAP//2 - h//2
            suivant = False
        else:
            #Pour les autres salles on part de celle qui existe
            suivant = random.choice(salles)
            place = False
            #On essaie 10 fois de trouver un espace autour de cette salle
            for i in range(10):
                angle = random.uniform(0, 2*math.pi)
                distance = random.randint(distance_min, distance_max)
                #Nouvelle coordonnée
                kx = int(suivant.centerx+ math.cos(angle)*distance) - (w//2)
                ky = int(suivant.centery + math.sin(angle)*distance) - (h//2)
                #Qu'on ne sort pas de la carte
                if 2<kx<LARGEURMAP-w-2 and 2<ky<HAUTEURMAP-h-2:
                    nouvelle_salle = pygame.Rect(kx,ky,w,h)
                    #Laisse 1 ecart de vide entre les salles
                    if not any(nouvelle_salle.inflate(2,2).colliderect(s) for s in salles):
                        x,y = kx, ky
                        place = True
            #Sinon on l'a crée pas
            if not place:
                continue
        #Creation et sauvegarde de salle
        nouvelle_salle = pygame.Rect(x,y,w,h)
        salles.append(nouvelle_salle)
        #Creuse le sol pour connecter
        for k in range(nouvelle_salle.top, nouvelle_salle.bottom):
            for v in range(nouvelle_salle.left, nouvelle_salle.right):
                grille[k][v] = SOL
        #Connecte les salle par couloir
        if suivant:
            #On creuse couloir jusqu'a la salle precedente
            prec = suivant.center
            proc = nouvelle_salle.center
            x1, y1 = int(prec[0]), int(prec[1])
            x2, y2 = int(proc[0]), int(proc[1])
            #On choisis alétoirement si vertical ou pas
            if random.choice([True, False]):
                c_horizontal(grille, x1, x2, y1)
                c_vertical(grille, y1, y2, x2)
            else:
                c_vertical(grille, y1, y2, x1)
                c_horizontal(grille, x1, x2, y2)
    
    #Placement du point de depart de l'ascnecer
    salle_depart = salles[0]
    px,py = int(salle_depart.centerx), int(salle_depart.centery)
    grille[py][px] = ASCENCEUR
    
    #On fait copir de la grille pour cree mur
    grille_fin = []
    for row in grille:
        nouvligne = row[:]
        grille_fin.append(nouvligne)
    for y in range(1, HAUTEURMAP-1):
        for x in range(1, LARGEURMAP-1):
            if grille[y][x]==VIDE:
                #On regarde si case vide touche un sol alors devient MUR
                voisin = False
                if grille[y+1][x]==SOL or grille[y-1][x]==SOL or grille[y][x+1]==SOL or grille[y][x-1]==SOL:
                    grille_fin[y][x] = MUR
    return grille_fin, salles, salles[0].center