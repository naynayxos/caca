import pygame
import os

BLANC = (255, 255, 255)
NOIR_TRANSPARENT = (0, 0, 0, 180)
GRIS_CLAIR = (200, 200, 200)
GRIS_FONCE = (50, 50, 50)
VERT_FONCE = (20, 63, 24)


class EcranPause:
    def __init__(self, largeur, hauteur):
        self.largeur = largeur
        self.hauteur = hauteur
        #Police
        police = os.path.join("ressource", "police.ttf")
        self.font_titre = pygame.font.Font(police, 60)
        self.font_option = pygame.font.Font(police, 30)
        #Definition boutons    
        self.buttons = [("REPRENDRE","Reprendre"),("OPTIONS","Options"),("SAUVEGARDER","Sauvegarder"),("MENU PRINCIPAL","Menu Principal"),("QUITTER","Quitter")]
        #Caracteristique des boutons
        self.btnLargeur = 300
        self.btnHauteur = 60
        self.espacement = 20
    
    def update_dimensions(self, largeur, hauteur):
        self.largeur = largeur
        self.hauteur = hauteur
    
    def dessiner(self, fenetre):
        #Fond semi-transparent
        overlay = pygame.Surface((self.largeur, self.hauteur), pygame.SRCALPHA)
        overlay.fill(NOIR_TRANSPARENT)
        fenetre.blit(overlay, (0, 0))
        #Boutons
        mouse_pos = pygame.mouse.get_pos()
        rectbtn = []
        #Calcul hauteur total des boutons
        total_height = len(self.buttons) * self.btnHauteur + (len(self.buttons) - 1)*self.espacement
        #Placement Y des boutons
        start_y = (self.hauteur - total_height)// 2
        for i, (key, text) in enumerate(self.buttons):
            #Centre bouton sur x
            x = (self.largeur - self.btnLargeur) // 2
            #Calcul pos du bouton
            y = start_y + i * (self.btnHauteur + self.espacement)
            #hitbox du bouton
            rect = pygame.Rect(x, y, self.btnLargeur, self.btnHauteur)
            #Couleur en survol
            if rect.collidepoint(mouse_pos):
                couleur_fond = VERT_FONCE
                couleur_txt = BLANC
            else:
                couleur_fond = GRIS_FONCE
                couleur_txt = BLANC
            #Dessiner le bouton
            pygame.draw.rect(fenetre, couleur_fond, rect, border_radius=10)
            #Dessiner les texte au centre du bouon
            texte = self.font_option.render(text, True, couleur_txt)
            text_rect = texte.get_rect(center=rect.center)
            fenetre.blit(texte, text_rect)
            #Stocker les rectangles pour la détection de clic
            rectbtn.append((rect, key))
        return rectbtn
    
    def clique(self, mouse_pos, rectbtn):
        #On parcours la liste de dessiner()
        for rect, action in rectbtn:
            #Si coordonnée sont dans un rectangle
            if rect.collidepoint(mouse_pos):
                return action #Renvoie vers l'utilité du bouton 
        return None
        