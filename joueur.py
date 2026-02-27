import pygame
import math
from prerequis import *
from prerequis import obstacle, angletrace

class Joueur:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.rect.center = (x, y)

        self.angle = 0
        self.angleactuel = 0
        self.dernierkx = 1
        self.dernierky = 0

        self.animation = 0
        self.time = 0
        self.vitesseanim = 5
        self.lumiereallumee = False
    
    def deplacer(self, keys, nb_frame):
        #Commande
        kx, ky = 0,0
        if keys[pygame.K_LEFT] or keys[pygame.K_q]:
            kx = -VITESSEJOUEUR
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            kx = VITESSEJOUEUR
        if keys[pygame.K_UP] or keys[pygame.K_z]:
            ky = -VITESSEJOUEUR
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            ky = VITESSEJOUEUR

        #Diagonale meme vitesse
        if kx !=0 and ky !=0:
            kx *=0.707
            ky *=0.707

        #Mise a jour angle
        if kx !=0 or ky != 0:
            self.dernierkx, self.dernierky=kx,ky
        
        anglecible = math.degrees(math.atan2(-self.dernierky, self.dernierkx))
        self.angleactuel = angletrace(self.angleactuel,anglecible,0.15)

        if kx!=0 or ky!=0:
            self.time +=1
            if self.time > self.vitesseanim:
                self.time = 0
                self.animation = (self.animation+1)%nb_frame
        else:
            self.animation = 0
            self.time = 0

        #Calcul angle pour perso
        anglejoueur = math.degrees(math.atan2(-self.dernierky, self.dernierkx))
        angleactuellejoueur = angletrace(self.angleactuel, anglejoueur, 0.15)
        #Rotation image joueur
        self.angle = angleactuellejoueur +90
        return kx, ky
    
    def collision(self, kx, ky, carte, objets):
        #Collision X
            self.rect.x += kx
            o = obstacle(self.rect,carte)
            for obj in objets:
                if obj.type == "meuble":
                    o.append(obj.hitbox)
            for mur in o:
                if self.rect.colliderect(mur):
                    if kx >0:
                        self.rect.right = mur.left
                    if kx <0:
                        self.rect.left = mur.right

            #Collision Y
            self.rect.y += ky
            o = obstacle(self.rect,carte)
            for obj in objets:
                if obj.type == "meuble":
                    o.append(obj.hitbox)
            for mur in o:
                if self.rect.colliderect(mur):
                    if ky >0:
                        self.rect.bottom = mur.top
                    if ky <0:
                        self.rect.top = mur.bottom