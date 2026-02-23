import pygame

# Couleurs
INTERFACE = (50, 50, 50, 200)
TEXTE = (255, 255, 255)
BORDURE = (255, 255, 255)
BUTTON_HOVER = (100,200,100)
BUTTON_BASE = (50, 150, 50)
BUTTONACTUEL = (200, 100, 100)
NOIR_TRANSPARENT = (0, 0, 0, 180)

class Ascenseur:
    def __init__(self, fenterelarge, fenetrehaute):
        self.L = fenterelarge
        self.H = fenetrehaute
        self.font = pygame.font.Font("ressource/police.ttf", 18)
        self.title = pygame.font.Font("ressource/titre.ttf", 31)
        self.sous_titre = pygame.font.Font("ressource/titre.ttf", 21)

        #Taille du menu latéral
        self.menuL = 240
        self.menuH = 320
        #Resolution du menu
        self.update_dimensions(fenterelarge, fenetrehaute)

    def update_dimensions(self, L, H):
        self.L = L
        self.H = H

    def dessiner(self, ecran, niveau):
        #Position du menu
        x = self.L - self.menuL -20
        y = self.H - self.menuH - 20
        #Fond du menu
        menurect = pygame.Rect(x, y, self.menuL, self.menuH)
        menu = pygame.Surface((self.menuL, self.menuH), pygame.SRCALPHA)
        menu.fill(INTERFACE)
        ecran.blit(menu, (x, y))

        #Cadre du menu
        pygame.draw.rect(ecran, BORDURE, menurect, 2)
        #Titre
        titre = self.sous_titre.render(f"ETAGE ACTUEL: {niveau}", True, TEXTE)
        #Centrer le titre dans le menu
        titre_rect = titre.get_rect(center=(x + self.menuL//2, y+40))
        ecran.blit(titre, titre_rect)

        #Bouton pour monter
        mouse_pos = pygame.mouse.get_pos()
        #etage
        bouton = []
        #Position du bouton
        btnx = 20
        btny = 20
        btnl = 80
        btnh = 60
        for i in range(1,7):
            col = (i-1)%2
            row = (i-1)//2
            #Position du bouton
            Positionx = x+30+col*(btnl+btnx)
            Positiony = y+80+row*(btnh+btny)
            bouton_rect = pygame.Rect(Positionx, Positiony, btnl, btnh)
            #si le bouton n'est pas celui de l'étage actuel on le dessine normalement
            if i!=niveau:
                bouton.append((bouton_rect, i))
                couleur = BUTTON_HOVER if bouton_rect.collidepoint(mouse_pos) else NOIR_TRANSPARENT
            else:
                #Bouton de l'étage actuel
                couleur = BUTTONACTUEL

            pygame.draw.rect(ecran, couleur, bouton_rect, border_radius=10)
            pygame.draw.rect(ecran, BORDURE, bouton_rect, 2, border_radius=10)
            #Texte du bouton
            texte = self.font.render(f"NIVEAU {i}", True, TEXTE)
            #Centrer le texte dans le bouton
            texte_rect = texte.get_rect(center=bouton_rect.center)
            ecran.blit(texte, texte_rect)
        return bouton
    
    def clique(self, mouse_pos, boutons):
        for rect, etage in boutons:
            if rect.collidepoint(mouse_pos):
                return etage
        return None
    
    def ecran_charge(self, ecran, img, etagechoisis):
        #Ecran de chargement noir avec texte de chargement
        ecran.fill((0,0,0))
        #TEXTE DE CHARGEMENT
        texte = self.title.render(f"CHARGEMENT DE L'ETAGE {etagechoisis}...", True, TEXTE)
        texte_rect = texte.get_rect(center=(self.L//2, self.H//2))
        ecran.blit(texte, texte_rect)
        pygame.display.flip()
        pygame.time.delay(800)  #Temps de chargement de 0.8 secondes