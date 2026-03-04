import pygame
import filtre
#intialisation des éléments;
def overlay_HUD():
    police=pygame.font.Font("ressource/police.ttf", 40)
    hudmode= pygame.image.load("ressource/HUD_mc_V2.png").convert_alpha()
    return police,hudmode
#Mode HUD texte & élément;
def mode_texte(fenetre, m_combat, enpause, police, hudmode):
    fenetre.blit(hudmode,(10,10))
    if enpause :
        Texte = "PAUSE"
    elif m_combat==True:
        Texte= "COMBAT"
    else:
        Texte="EXPLORATION"
    surface=police.render(Texte, False, (255,255,255))
    surf_rec=surface.get_rect()
    surf_rec.center=(10+hudmode.get_width()//2, 10+hudmode.get_height()//2)
    fenetre.blit(surface, surf_rec)
