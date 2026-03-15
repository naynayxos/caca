import pygame
import math
import random
from prerequis import *
from prerequis import obstacle, angletrace
from arme import Arme

class Joueur:
    def __init__(self, x, y):
        #Hitbox et pos
        self.rect = pygame.Rect(x, y, 40, 40)
        self.rect.center = (x, y)
        #Rotation
        self.angle = 0
        self.angleactuel = 0
        self.dernierkx = 1
        self.dernierky = 0
        #Animation
        self.animation = 0
        self.time = 0
        self.vitesseanim = 5
        self.lumiereallumee = False
        #Deplacement
        self.marche = 7
        self.course = 11
        self.maxcourse = 100
        self.endurance = self.maxcourse
        #Armes
        self.tir = []
        self.vitessetir = 0
        self.delaytir = 12
        self.munition = 30
        self.arsenal = 1
        #vie
        self.hpmax=100
        self.hp= self.hpmax

    def changerarme(self, num):
        self.arsenal = num
    
    def updatetir(self, carte, objets):
        objetcasse = [] #Liste obj casse pour le serveur
        #Coultdown arme
        if self.vitessetir > 0:
            self.vitessetir -=1
        #Mise a jour position des tirs
        tiractuelle = []
        for balle in self.tir:
            balle.deplacer()
            #Verifie que la balle a percuter
            touche = balle.collisionoupas(carte, objets)
            if not touche:
                tiractuelle.append(balle)
            elif touche != "mur": 
                #Touche objet destructible
                if not hasattr(touche, 'hp'):
                    touche.hp = 3
                touche.hp = touche.hp -1
                if touche.hp <= 0:
                    #La caisse se casse et se transforme en muni
                    touche.type = "munition"
                    touche.texture = texture("munition.png", (90,90), transparente=True)
                    touche.hitbox = touche.rect
                    objetcasse.append(touche)
        self.tir = tiractuelle
        return objetcasse

    def tirer(self):
        #On peut tirer que si on a des balle et que le couldown est fini
        if self.munition>0 and self.vitessetir <= 0:
            #Calcul de l'Appariton de la balle
            pangle = math.radians(self.angleactuel)
            debutx = self.rect.centerx + math.cos(pangle)*20
            debuty = self.rect.centery - math.sin(pangle)*20
            if self.arsenal == 1:
                #Pistolet Classique
                p = Arme(debutx, debuty, self.angleactuel)
                self.tir.append(p)
                self.vitessetir = 15
                self.munition -= 1
            elif self.arsenal == 2:
                #Fusil a pompe: 2 balle
                if self.munition>=2:
                    #Tire 5 balle avec angles
                    for pompe in [-16, -8, 0, 8, 16]:
                        p = Arme(debutx, debuty, self.angleactuel+pompe)
                        self.tir.append(p)
                    self.vitessetir = 40
                    self.munition = self.munition - 2
            elif self.arsenal == 3:
                #Fusil d'assaut: rapide avec recul entre -5 et 5 deg
                recul = random.uniform(-5, 5)
                p = Arme(debutx, debuty, self.angleactuel+recul)
                self.tir.append(p)
                self.vitessetir = 5
                self.munition = self.munition - 1

    def deplacer(self, keys, nb_frame):
        vitesse = self.marche
        mouvement = False
        #Verifie si se déplace
        if keys[pygame.K_LEFT] or keys[pygame.K_q] or keys[pygame.K_RIGHT] or keys[pygame.K_d] or keys[pygame.K_UP] or keys[pygame.K_z] or keys[pygame.K_DOWN] or keys[pygame.K_s]:    
            mouvement = True
        #Sprint avec shift
        if mouvement == True and keys[pygame.K_LSHIFT] and self.endurance > 0:
            vitesse = self.course
            self.endurance -= 0.5
        else:
            if self.endurance < self.maxcourse:
                self.endurance += 0.1

        #Commande et calcul de deplacement
        kx, ky = 0,0
        if keys[pygame.K_LEFT] or keys[pygame.K_q]:
            kx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            kx += 1
        if keys[pygame.K_UP] or keys[pygame.K_z]:
            ky -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            ky += 1
        
        #Direction avant de bouger
        if kx !=0 and ky !=0:
            self.dernierkx, self.dernierky = kx,ky

        #Diagonale meme vitesse
        if kx !=0 and ky !=0:
            kx *=0.707
            ky *=0.707
        
        kx *= vitesse
        ky *= vitesse

        #Mise a jour angle
        if kx !=0 or ky != 0:
            self.dernierkx, self.dernierky=kx,ky
            self.time +=1
            if self.time > self.vitesseanim:
                self.time = 0
                self.animation = (self.animation+1)%nb_frame
        else:
            self.animation = 0
            self.time = 0
        #Tourner le joueur fuldifié
        anglecible = math.degrees(math.atan2(-self.dernierky, self.dernierkx))
        if kx !=0 or ky != 0:
            #On lisse deplacement
            self.angleactuel = angletrace(self.angleactuel,anglecible,0.15)
        else:
            #Fixe son angle
            self.angleactuel = anglecible
        self.angle = self.angleactuel + 90
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