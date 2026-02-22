import pygame
#mode combat
m_combat =False


def activation_mc(event):
    global m_combat
    if event.type == pygame.KEYDOWN and event.key == pygame.K_t:
        m_combat= not m_combat


def filtre(fenetre):
    if m_combat== True:
        L, l= fenetre.get_size()
        surface= pygame.Surface((L, l), pygame.SRCALPHA)
        surface.fill((120, 0, 0, 73))
        fenetre.blit(surface,(0,0))
    