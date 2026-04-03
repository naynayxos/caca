import pygame

TEXTE = (255,255,255)
GRIS = (180,180,180)
ROUGE = (200,60,60)
VERT = (80,200,80)

class Sommeil:
    def __init__(self, largeur, hauteur):
        self.L = largeur
        self.H = hauteur
        self.fonttitre = pygame.font.Font("ressource/titre.ttf", 36)
        self.fonttexte = pygame.font.Font("ressource/police.ttf", 22)
        self.fontpetit = pygame.font.Font("ressource/police.ttf", 16)

    def update(self, L, H):
        self.L = L
        self.H = H
    
    def nuit(self, ecran, joueur, jour):
        clock = pygame.time.Clock()
        #Fondu nuit
        fondu = pygame.Surface((self.L, self.H))
        fondu.fill((0,0,0))
        for i in range(0,256,6):
            fondu.set_alpha(i)
            ecran.blit(fondu,(0,0))
            pygame.display.flip()
            clock.tick(60)
        #Ecran de nuit
        nouveaujour = jour +1
        self.dessinerecran(ecran, joueur, jour, nouveaujour)
        pygame.display.flip()
        pygame.time.delay(2000)
        #Recharche oxygene
        joueur.oxygene = joueur.oxygenemax
        #Guerison pendant la nuit
        soin = int(joueur.hpmax*0.30)
        joueur.hp = min(joueur.hpmax, joueur.hp+soin)
        #Fondu retour
        for i in range(255, -1, -6):
            ecran.fill((0,0,0))
            self.dessinerecran(ecran,joueur,jour,nouveaujour)
            fondu.set_alpha(i)
            ecran.blit(fondu,(0,0))
            pygame.display.flip()
            clock.tick(60)
        return nouveaujour
    
    def dessinerecran(self, ecran, joueur, ancienjour, nouveaujour):
        ecran.fill((5,5,20))
        y = self.H//2-90
        #Titre
        titre = self.fonttitre.render(f"NUIT du {ancienjour} au {nouveaujour}", True, TEXTE)
        ecran.blit(titre, titre.get_rect(center = (self.L//2,y)))
        y+=60
        #Separation ligne
        pygame.draw.line(ecran, (60,60,80), (self.L//2-200, y),(self.L//2+200,y),1)
        y+=20
        #Recharge oxy
        oxygene = self.fonttexte.render("Bouteille d'oxygene recharge", True, VERT)
        ecran.blit(oxygene, oxygene.get_rect(center = (self.L//2,y)))
        y+=40
        #Vie recharge nuit
        soin = int(joueur.hpmax*0.30)
        soinpris = min(soin, joueur.hpmax-joueur.hp)
        sointexte = self.fonttexte.render(f"Recupartion de {soinpris}HP", True, VERT)
        ecran.blit(sointexte, sointexte.get_rect(center=(self.L//2,y)))

