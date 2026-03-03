import pygame
import filtre

police=pygame.font.Font("ressource/police.ttf", 40)
def mode_texte(fenetre, m_combat):
    if m_combat==True:
        Texte= "Mode : Combat"
    else:
        Texte="MODE : Exploration"
    surface=police.render(Texte, False, (255,255,255))
    fenetre.blit(surface,(20,20))