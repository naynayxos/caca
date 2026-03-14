import pygame
import sys
import time

def ecran_chargement(fenetre, WIDTH, HEIGHT):
    # Couleurs
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    # Police
    FONT_TITLE = pygame.font.Font("ressource/police.ttf", 70)   
    #Logo
    logo = pygame.image.load("ressource/Chargement.png").convert_alpha()
    logo = pygame.transform.scale(logo, (WIDTH, HEIGHT))

    clock = pygame.time.Clock()
    start_time = time.time() #Temps depuis lancement
    duration = 1.5  # Durée de temps du chargement
    
    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        fenetre.fill(BLACK)
        #Met l'image
        if logo is not None:
            fenetre.blit(logo, (0,0))
        #Afffiche le texte 
        title = FONT_TITLE.render("CHARGEMENT...", True, WHITE)
        title_rect = title.get_rect(bottomright=(WIDTH - 50, HEIGHT - 50))
        fenetre.blit(title, title_rect)
        pygame.display.flip()
        #Gestion du temps du chargement
        #calcul combien de temps depuis lancement
        tamps = time.time() - start_time
        #Si temps > 1.5 on passe
        if tamps >= duration:
            return
