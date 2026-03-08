import pygame
import sys
import time

pygame.init()
#Fenetre en plein ecran
fenetre = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
WIDTH, HEIGHT = fenetre.get_size()
pygame.display.set_caption("D-RED")
#Cacher la souris
pygame.mouse.set_visible(False)
#Couleurs
BLACK = (0,0,0)

#Charmenent texture
logo = pygame.image.load("ressource/logormbg.png").convert_alpha()
centre_logo = logo.get_rect(center=(WIDTH//2, HEIGHT//2))

def demarrage():
    clock = pygame.time.Clock()
    start_time = time.time()
    duration = 1.5  # Durée
    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        tamps = time.time() - start_time
        arrive = min(tamps/ duration, 1.0)
        #Fond noir
        fenetre.fill(BLACK)
        #Logo fondu
        if logo is not None:
            fondu = int(arrive*255)
            logo.set_alpha(fondu)
            fenetre.blit(logo, centre_logo)
        pygame.display.flip()
        if arrive >=1.0:
            time.sleep(2) #On laisse pendant 2 sec apres l'affichage du logo 
            return
demarrage()
#Remet la souris
pygame.mouse.set_visible(True)
import menu