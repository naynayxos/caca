import pygame
import sys

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)

pygame.init()
ecran = pygame.display.Info()
taille = (ecran.current_w, ecran.current_h)

#Bouton option
class Button:
    def __init__(self, text, x, y, w, h, action=None):
        self.rect = pygame.Rect(x, y, w, h) #Rectangle du bouton
        self.text = text #Texte du bouton
        self.action = action #Action lors du clic
        self.hover = False #Survol du bouton

    def draw(self, surface, font):
        #Couleur du bouton au survol
        dessus = GOLD if self.hover else BLACK
        #Transparence
        fond = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(fond,(0,0,0,150),(0,0,self.rect.width,self.rect.height), border_radius=10)
        surface.blit(fond, self.rect.topleft)
        #Bordure du bouton
        pygame.draw.rect(surface, dessus, self.rect,2, border_radius=10)
        #Texte du bouton
        text_surf = font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, pos,clique):
        #Verirife si cliqué et survolé
        self.hover = self.rect.collidepoint(pos)
        return self.hover and clique
    
#Barre régalage volume
class VolumeBar:
    def __init__(self, x, y, w, volume=0.5):
        self.rect = pygame.Rect(x, y, w, 10) #Rectangle de la barre
        self.volume = volume #Volume Actuelle
        self.cerclex = x+(w*volume) #Position de la boule
        self.cercley = y + 5 #Position verticale de la boule
        self.dragging = False #Indique si la poignée se déplace

    def draw(self, surface):
        #Fond de la barre
        pygame.draw.rect(surface,(100,100,100),self.rect, border_radius=5)
        #Dessine la barre de volume remplie
        couleur = pygame.Rect(self.rect.x, self.rect.y, self.cerclex - self.rect.x, 10)
        pygame.draw.rect(surface, GOLD, couleur, border_radius=5)
        #Dessine la boule
        pygame.draw.circle(surface, WHITE, (int(self.cerclex), int(self.cercley)), 10)
        pygame.draw.circle(surface, GOLD, (int(self.cerclex), int(self.cercley)), 10,2)

    def actualise(self, pos, clique):
        #position entre souris et boule
        position = ((pos[0] - self.cerclex) ** 2 + (pos[1] - self.cercley) ** 2) ** 0.5
        #Vérifie si la boule est cliquée ou la barre
        if clique:
            if self.rect.collidepoint(pos) or position < 15:
                self.dragging = True #Glisser la boule
        else:
            self.dragging = False #clique relâché

        #si on glisse
        if self.dragging:
            #bloque la boule dans la barre
            self.cerclex = max(self.rect.x, min(pos[0], self.rect.right))
            #Met à jour le volume en fonction de la pos de la boule
            self.volume = (self.cerclex - self.rect.x) / self.rect.width
            return self.volume
        return None
    
#Boucle du menu option
def option_menu(fenetre, largeur, hauteur):
    clock = pygame.time.Clock()
    fonttitle = pygame.font.SysFont("ressource/titre.ttf", 60)
    fonttext = pygame.font.SysFont("ressource/police.ttf", 30)

    L,H = fenetre.get_size()
    pleinecran = (fenetre.get_flags() & pygame.FULLSCREEN) != 0

    #Créer les boutons
    #Bouton plein écran
    btn_pleinecran = Button("MODE: FENETRE", L//2-150,150,300,50)
    if pleinecran:
        btn_pleinecran.text = "MODE: PLEIN ECRAN"
    #Bouton Résolution
    resolutions = [(1920,1080),(1600,900),(1280,720),(800,600)]
    index = 0 #Index de la résolution premiere
    #Trouve l'index de la résolution actuelle
    if (H,L) in resolutions:
        index = resolutions.index((L,H))
    btn_resolution = Button(f"RESOLUTION: {L}x{H}", L//2-150,220,300,50)
    #Barre de volume
    volume_barre = VolumeBar(L//2-150, 350, 300, pygame.mixer.music.get_volume())
    #Bouton retour
    btn_retour = Button("RETOUR",50, H-100, 200, 50)

    running = True
    while running:
        pos = pygame.mouse.get_pos()
        clique = False
        #Gestion de clique
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Clique gauche
                    clique = True

        #Resize de l'écran
        if event.type == pygame.VIDEORESIZE:
            H,L = event.w, event.h
            fenetre = pygame.display.set_mode((H,L), pygame.RESIZABLE)
            #Recentrage des boutons
            btn_pleinecran.rect.x = (L//2-150)
            btn_resolution.rect.x = (L//2-150)
            volume_barre.rect.x = (L//2-150)
            volume_barre.rect.y = 350
            #Position de la boule
            volume_barre.cerclex = volume_barre.rect.x + (volume_barre.rect.width * volume_barre.volume)
            btn_retour.rect.y = H-100
            btn_resolution.text = f"RESOLUTION: {L}x{H}"

        #Bouton plein écran
        if btn_pleinecran.is_clicked(pos, clique):
            pygame.time.delay(200)
            pleinecran = not pleinecran
            if pleinecran:
                #Si mode plein écran on passe a la résolution de l'ecran
                fenetre = pygame.display.set_mode(taille, pygame.FULLSCREEN)
                btn_pleinecran.text = "MODE: PLEIN ECRAN"
            else:
                #Si mode fenetre on passe a cette résolution
                fenetre = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
                btn_pleinecran.text = "MODE: FENETRE"
            L,H = fenetre.get_size()
            #Recentrage des boutons
            btn_pleinecran.rect.x = (L//2-150)
            btn_resolution.rect.x = (L//2-150)
            volume_barre.rect.x = (L//2-150)
            volume_barre.cerclex = volume_barre.rect.x + (volume_barre.rect.width * volume_barre.volume)
            volume_barre.rect.y = H-100

        #Bouton résolution
        if not pleinecran:
            if btn_resolution.is_clicked(pos, clique):
                pygame.time.delay(200)
                #Change la résolution par la suivante de la liste
                index = (index + 1) % len(resolutions)
                new_res = resolutions[index]
                fenetre = pygame.display.set_mode(new_res, pygame.RESIZABLE)
                L,H = new_res
                btn_resolution.text = f"RESOLUTION: {L}x{H}"
                #Recentrage des boutons
                btn_pleinecran.rect.x = (L//2-150)
                btn_resolution.rect.x = (L//2-150)
                volume_barre.rect.x = (L//2-150)
                volume_barre.cerclex = volume_barre.rect.x + (volume_barre.rect.width * volume_barre.volume)
                btn_retour.rect.y = H-100

        #Clique ou non sur la barre de volume
        nouveau_volume = volume_barre.actualise(pos, pygame.mouse.get_pressed()[0])
        if nouveau_volume is not None:
            pygame.mixer.music.set_volume(nouveau_volume)
        #Clique sur le bouton retour
        if btn_retour.is_clicked(pos, clique):
            running = False

        fenetre.fill((30, 30, 30)) #Fond sombre
        #Affiche le mot "Options"
        titre = fonttitle.render("OPTIONS", True, WHITE)
        fenetre.blit(titre, (H//2 - titre.get_width()//2, 50))

        #Dessine les boutons
        btn_pleinecran.draw(fenetre, fonttext)
        if not pleinecran:
            btn_resolution.draw(fenetre, fonttext)
        else:
            #En plein ecran on met Resolution désactivée
            txtpleinecran= fonttext.render("RESOLUTION ESACTIVE", True, (100,100,100))
            fenetre.blit(txtpleinecran, (H//2 - txtpleinecran.get_width()//2, 230))

        #Dessine la barre de volume
        dessin_volume = fonttext.render("VOLUME MUSIQUE", True, WHITE)
        fenetre.blit(dessin_volume, (H//2 - dessin_volume.get_width()//2, 310))
        volume_barre.draw(fenetre)

        #Tableau de touche du jeu
        tableau_touche = pygame.Rect(H//2 - 200, 450, 500, 200)
        pygame.draw.rect(fenetre, (50,50,50), tableau_touche, border_radius=15)
        pygame.draw.rect(fenetre, GOLD, tableau_touche, 2, border_radius=15)
        commande = ["COMMANDES DU JEU:","AVANCER: Z","RECULER: S","GAUCHE: Q","DROITE: D","SAUTER: ESPACE","PAUSE: ECHAP","LUMIERE: H"]
        for i, ligne in enumerate(commande):
            #Titre en or le reste en blanc
            titre_couleur = GOLD if i == 0 else WHITE
            f = fonttitle if i == 0 else fonttext
            texte = f.render(ligne, True, titre_couleur)
            #Reduction de la taille du texte si trop large
            if i == 0: texte= pygame.transform.scale(texte, (int(texte.get_width()*0.5), int(texte.get_height()*0.5)))
            #Affichage des lignes
            fenetre.blit(texte,(H//2 - texte.get_width()//2, 470+i*30))
        btn_retour.draw(fenetre, fonttext)
        pygame.display.flip()
        clock.tick(60)
    return fenetre