import pygame
import random
import math
from prerequis import *
from prerequis import texture

class Objet:
    def __init__(self,x,y,name,type,size=None):
        self.rect = pygame.Rect(x,y,ZOOM,ZOOM)
        self.texture=texture(name,size,transparente=True)
        self.type = type   
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
    types = [{'nom': 'caisse.png', 'type': 'meuble', 'proba': 0.2},
            {'nom': 'plante.png', 'type': 'plante', 'proba': 0.2},
            {'nom': 'meuble.png', 'type': 'meuble', 'proba': 0.2},
            {'nom': 'munition.png', 'type': 'munition', 'proba':0.1}]
    
    for salle in salles:
        for y in range(salle.top, salle.bottom):
            for x in range(salle.left, salle.right):
                if grille[y][x] == SOL:
                    mur = False
                    if grille[y+1][x] == MUR:
                        mur = True
                    elif grille[y-1][x] == MUR:
                        mur = True
                    elif grille[y][x+1] == MUR:
                        mur = True
                    elif grille[y][x-1] == MUR:
                        mur = True
                    if mur:
                        if random.random() < 0.2: # 20% de chance un objet
                            t = random.choice(types)
                            if random.random() < t['proba']:
                                if t['type'] != 'munition':
                                    taillemun = (ZOOM, ZOOM)
                                else:
                                    taillemun = (ZOOM//2, ZOOM//2)
                                obj = Objet(x*ZOOM, y*ZOOM, t['nom'], t['type'], size=taillemun)
                                objets.append(obj)
    #Carte acces ascenceur dans la derniere salle
    dersalle = salles[-1]
    dx, dy = dersalle.centerx, dersalle.centery
    carte = Objet(dx*ZOOM+ZOOM//4, dy*ZOOM+ZOOM//4, "carte.png", "carte", size=(ZOOM//2, ZOOM//2))
    objets.append(carte)
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
    grille = [[VIDE for x in range(LARGEURMAP)] for y in range(HAUTEURMAP)]
    salles=[]
    distance_min =7
    distance_max = 10#Dstance entre les salles
    for i in range(80): #Nombre de salles a essayer de generer
        w = random.randint(5,9)
        h = random.randint(5,9)
        if not salles:
            x = LARGEURMAP//2 - w//2
            y = HAUTEURMAP//2 - h//2
            suivant = False
        else:
            suivant = random.choice(salles)
            place = False
            for _ in range(10):
                angle = random.uniform(0, 2*math.pi)
                distance = random.randint(distance_min, distance_max)
                kx = int(suivant.centerx+ math.cos(angle)*distance) - (w//2)
                ky = int(suivant.centery + math.sin(angle)*distance) - (h//2)
                if 2<kx<LARGEURMAP-w-2 and 2<ky<HAUTEURMAP-h-2:
                    nouvelle_salle = pygame.Rect(kx,ky,w,h)
                    if not any(nouvelle_salle.inflate(2,2).colliderect(s) for s in salles):
                        x,y = kx, ky
                        place = True
            if not place:
                continue

        nouvelle_salle = pygame.Rect(x,y,w,h)
        salles.append(nouvelle_salle)

        for k in range(nouvelle_salle.top, nouvelle_salle.bottom):
            for v in range(nouvelle_salle.left, nouvelle_salle.right):
                grille[k][v] = SOL

        if suivant:
            #On creuse couloir jusqu'a la salle precedente
            prec = suivant.center
            proc = nouvelle_salle.center
            x1, y1 = int(prec[0]), int(prec[1])
            x2, y2 = int(proc[0]), int(proc[1])
            if random.choice([True, False]):
                c_horizontal(grille, x1, x2, y1)
                c_vertical(grille, y1, y2, x2)
            else:
                c_vertical(grille, y1, y2, x1)
                c_horizontal(grille, x1, x2, y2)
    
    salle_depart = salles[0]
    px,py = int(salle_depart.centerx), int(salle_depart.centery)
    grille[py][px] = ASCENCEUR
    
    #On ajoute des murs a chaque sol touchant une case vide
    grille_fin = [row[:] for row in grille]
    for y in range(1, HAUTEURMAP-1):
        for x in range(1, LARGEURMAP-1):
            if grille[y][x]==VIDE:
                #On regarde donc ses voisins
                voisin = False
                if grille[y+1][x]==SOL or grille[y-1][x]==SOL or grille[y][x+1]==SOL or grille[y][x-1]==SOL:
                    voisin = True
                if voisin:
                    grille_fin[y][x] = MUR
    return grille_fin, salles, salles[0].center