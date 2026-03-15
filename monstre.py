import pygame
import random

from prerequis import obstacle




move = [-1, 0, 1]
class monstre:
    def __init__(self,x, y, speed, hp):
        #Hitbox et pos
        self.rect = pygame.Rect(x, y, 40, 40)
        self.rect.center = (x, y)
        #vitesse
        self.speed = speed
        #La vie
        self.hp_cur= hp
        self.hp_max=hp
        self.mort=False
        #mouvement aléatoire
        self.pos_x = random.choice(move)
        self.pos_y = random.choice(move)
    #le monstres se déplace en fonction de la direction
    def deplacement(self):
        kx = self.pos_x *self.speed
        ky = self.pos_y *self.speed
        return (kx, ky)
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
                    self.pos_x= -1
                if kx <0:
                    self.rect.left = mur.right
                    self.pos_x=1

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
                    self.pos_y = -1
                if ky <0:
                    self.rect.top = mur.bottom
                    self.pos_y = 1

