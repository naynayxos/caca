import pygame
import sys
import time

def ecran_chargement(fenetre, WIDTH, HEIGHT):
    # Couleurs
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    # Police
    FONT_TITLE = pygame.font.Font("ressource/police.ttf", 70)   
    
    logo = pygame.image.load("ressource/Chargement.png").convert_alpha()
    logo = pygame.transform.scale(logo, (WIDTH, HEIGHT))

    clock = pygame.time.Clock()
    start_time = time.time()
    duration = 1.5  # Durée
    
    while True:
        clock.tick(60)
        tamps = time.time() - start_time
        progress = min(tamps/ duration, 1.0)
        
        if progress >= 1.0:
            if logo is not None:
                fenetre.blit(logo, (0,0))
                title = FONT_TITLE.render("CHARGEMENT...", True, WHITE)
                title_rect = title.get_rect(bottomright=(WIDTH - 50, HEIGHT - 50))
                fenetre.blit(title, title_rect)
                pygame.display.flip()
                return
        fenetre.fill(BLACK)
        if logo is not None:
            fenetre.blit(logo, (0,0))
        title = FONT_TITLE.render("CHARGEMENT...", True, WHITE)
        title_rect = title.get_rect(bottomright=(WIDTH - 50, HEIGHT - 50))
        fenetre.blit(title, title_rect)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        pygame.display.flip()