import pygame
import sys
import time

pygame.init()

# Fenêtre
WIDTH = 1920
HEIGHT = 1080
fenetre = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("D-RED")

# Couleurs
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)
GOLD_DARK = (200, 170, 0)
GLASS_BASE = (255, 255, 255, 30)
# Police
try:
    FONT_TITLE = pygame.font.Font("ressource/police.ttf", 70)
    FONT_LOADING = pygame.font.Font("ressource/police.ttf", 30)
except:
    FONT_TITLE = pygame.font.SysFont(None, 100)
    FONT_LOADING = pygame.font.SysFont(None, 30)

logo = pygame.image.load("ressource/Chargement.png").convert_alpha()
logo = pygame.transform.scale(logo, (WIDTH, HEIGHT))

def ecran_chargement():
    clock = pygame.time.Clock()
    start_time = time.time()
    duration = 2
    
    while True:
        clock.tick(60)
        elapsed = time.time() - start_time
        progress = min(elapsed / duration, 1.0)
        
        if progress >= 1.0:
            return

        fenetre.fill(BLACK)
        fenetre.blit(logo, (0,0))
        title_surf = FONT_TITLE.render("CHARGEMENT...", True, WHITE)
        title_rect = title_surf.get_rect(bottomright=(WIDTH - 50, HEIGHT - 50))
        fenetre.blit(title_surf, title_rect)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        pygame.display.flip()

ecran_chargement()

import menu