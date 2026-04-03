import pygame
import random
import math
from prerequis import obstacle, texture



#lst des mouvement pour que le random choisissent
move = [-1, 0, 1]
larry=None
def init_texture():
    global larry
    larry= texture("Larryv2.png", (250,250), transparente=True)
class Monstre:
    def __init__(self,x, y, speed, hp):
        #Hitbox et pos
        self.rect = pygame.Rect(x, y, 200, 200)
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
        #Texture
        self.texture= larry
    #Calcul du deplacement en fct de la position du joueur
    def deplacement(self, joueur_x=None, joueur_y = None):
        kx= self.pos_x * self.speed
        ky = self.pos_y * self.speed
        if joueur_x != None and joueur_y != None :
            dx = joueur_x -self.rect.centerx
            dy = joueur_y - self.rect.centery
            #Distance avec le joueur calcul
            distance =math.sqrt(dx*dx + dy*dy)
            #Lorsque le joueur est proche
            if distance <500 and distance >0:
                kx = (dx/distance) *self.speed
                ky = (dy/distance) *self.speed
                return (kx, ky)
        #sinon ça fait des choses aléatoires 
        if(random.random()<0.02):
            self.pos_x= random.choice(move)
            self.pos_y= random.choice(move)
        else:
            kx= self.pos_x*self.speed
            ky= self.pos_y * self.speed      

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
#affichage de l'image
    def affichage(self, ecran, camera_x, camera_y):
        fenetre_x=self.rect.x + camera_x
        fenetre_y = self.rect.y + camera_y
        ecran.blit(self.texture, (fenetre_x, fenetre_y))
    
    def take_damage(self, degats):
        self.hp_cur -= degats
        if self.hp_cur<= 0:
            self.hp_cur= 0
            self.mort= True
            self.loot = random.randint(50, 100) #loot aléatoire entre 50 et 100 pièces
        else:
            self.loot = 0
