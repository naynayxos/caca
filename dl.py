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
    FONT_TITLE = pygame.font.Font("ressource/police.ttf", 100)
    FONT_LOADING = pygame.font.Font("ressource/police.ttf", 30)
except:
    FONT_TITLE = pygame.font.SysFont(None, 100)
    FONT_LOADING = pygame.font.SysFont(None, 30)

logo = pygame.image.load("ressource/chargement.jpg")
logo = pygame.transform.scale(logo, (WIDTH, HEIGHT))

def ecran_chargement():
    clock = pygame.time.Clock()
    start_time = time.time()
    duration = 1.5
    
    while True:
        clock.tick(60)
        elapsed = time.time() - start_time
        progress = min(elapsed / duration, 1.0)
        
        if progress >= 1.0:
            return

        fenetre.fill(BLACK)
        
        fenetre.blit(logo, (0,0))
        
        # Barre de chargement
        bar_width = 700
        bar_height = 30
        bar_x = (WIDTH - bar_width) // 2
        bar_y = HEIGHT // 2 + 300
        
        # Fond de la barre
        bar_bg = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
        pygame.draw.rect(bar_bg, GLASS_BASE, (0, 0, bar_width, bar_height), border_radius=15)
        pygame.draw.rect(bar_bg, GOLD_DARK, (0, 0, bar_width, bar_height), width=2, border_radius=15)
        fenetre.blit(bar_bg, (bar_x, bar_y))
        
        # Progression dorée
        progress_width = int((bar_width - 8) * progress)
        if progress_width > 0:
            progress_surface = pygame.Surface((progress_width, bar_height - 8), pygame.SRCALPHA)
            pygame.draw.rect(progress_surface, GOLD, (0, 0, progress_width, bar_height - 8), border_radius=12)
            fenetre.blit(progress_surface, (bar_x + 4, bar_y + 4))
        
        # Pourcentage
        percent_text = FONT_LOADING.render(f"{int(progress * 100)}%", True, WHITE)
        percent_rect = percent_text.get_rect(center=(WIDTH // 2, bar_y + bar_height + 40))
        fenetre.blit(percent_text, percent_rect)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        pygame.display.flip()

ecran_chargement()

import menu