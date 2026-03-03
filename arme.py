import pygame
import math
from prerequis import obstacle

class Arme:
    def __init__(self, x, y, direction):
        self.rect = pygame.Rect(0,0,10,10)  # Rectangle tire arme
        self.rect.center = (x, y)
        self.vitesse = 25 #vitesse des balles
        # Calcul de la direction de tir
        angle = math.radians(direction)
        self.ux = math.cos(angle) * self.vitesse
        self.uy = -math.sin(angle) * self.vitesse
        #Visuel de la balle
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 200, 0), (5, 5), 5)  # Dessine une balle jaune

    def deplacer(self):
        self.rect.x += self.ux
        self.rect.y += self.uy
    
    def collisionoupas(self, carte, objets):
        # Vérifie la collision avec les murs
        o = obstacle(self.rect, carte)
        # Vérifie la collision avec les objets
        for obj in objets:
            if obj.type == "meuble":
                if self.rect.colliderect(obj.hitbox):
                    return obj
        # Vérifie la collision avec les murs et les objets
        for mur in o:
            if self.rect.colliderect(mur):
                return "mur"
        return None