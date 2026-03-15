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
        if self.hover:
            dessus = GOLD 
        else:
            dessus = BLACK
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

    def repositionner(self, x, y):
        self.rect.x= x
        self.rect.y = y
        self.cercley = y + 5 #Position verticale de la boule
        self.cerclex = self.rect.x + (self.rect.width * self.volume) #Position de la boule en x

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
    fonttitle = pygame.font.SysFont(None, 60)
    fonttext = pygame.font.SysFont(None, 30)

    L,H = fenetre.get_size()
    pleinecran = (fenetre.get_flags() & pygame.FULLSCREEN) != 0

    #Charge image de fond
    imgori = pygame.image.load("ressource/option.png").convert()
    imgfond = pygame.transform.scale(imgori, (L, H))

    #Créer les boutons
    #Bouton plein écran
    btn_pleinecran = Button("MODE: FENETRE", 0,0,300,50)
    if pleinecran:
        btn_pleinecran.text = "MODE: PLEIN ECRAN"
    #Bouton Résolution
    resolutions = [(1280,720),(1600,900),(1920,1080),(1920,1200),(2560,1440),(2560,1600),(3840,2160)]
    index = 0 #Index de la résolution premiere
    #Trouve l'index de la résolution actuelle
    if (L,H) in resolutions:
        index = resolutions.index((L,H))
    btn_resolution = Button(f"RESOLUTION: {L}x{H}", 0,0,300,50)
    #Barre de volume
    volumeactuel = pygame.mixer.music.get_volume()
    if volumeactuel > 0:
        posboule = pow(volumeactuel, 1/3)
    else:
        posboule = 0
    volume_barre = VolumeBar(0,0,300,posboule)
    #Bouton retour
    btn_retour = Button("RETOUR",0,0, 200, 50)

    def update_dimensions(newlargeur, newhauteur):
        nonlocal imgfond, fonttitle, fonttext
        imgfond = pygame.transform.scale(imgori, (newlargeur, newhauteur))
        #Texte se regle en fonction de la res
        taille_titre = max(30, int(newhauteur*0.08))
        taille_texte = max(15, int(newhauteur*0.03))
        fonttitle = pygame.font.Font("ressource/titre.ttf", taille_titre)
        fonttext = pygame.font.Font("ressource/police.ttf", taille_texte)
        #Bouton se regle en fontion de res
        btnw = max(250, int(newlargeur*0.35))
        btnh = max(40, int(newhauteur*0.07))
        center_x = newlargeur // 2 - btnw//2
        btn_pleinecran.rect.width = btnw
        btn_pleinecran.rect.height = btnh
        btn_pleinecran.rect.x = center_x
        btn_pleinecran.rect.y = int(newhauteur*0.15)
        if pleinecran:
            btn_pleinecran.text = "MODE: PLEIN ECRAN"
        else:
            btn_pleinecran.text = "MODE: FENETRE"
        btn_pleinecran.rect.width = btnw
        btn_pleinecran.rect.height = btnh
        btn_resolution.rect.width = btnw
        btn_resolution.rect.height = btnh
        btn_resolution.rect.x = center_x
        btn_resolution.rect.y = int(newhauteur*0.25)
        btn_resolution.text = f"RESOLUTION: {newlargeur}x{newhauteur}"
        volume_barre.rect.width = btnw
        volume_barre.repositionner(center_x, int(newhauteur*0.40))
        btn_retour.rect.width = max(150, int(newlargeur*0.15))
        btn_retour.rect.height = btnh
        btn_retour.rect.y = newhauteur - btnh - int(newhauteur*0.05)
        btn_retour.rect.x = int(newlargeur*0.05)
    
    update_dimensions(L,H)

    running = True
    while running:
        pos = pygame.mouse.get_pos()
        clique = False
        actionclique = pygame.mouse.get_pressed()[0]
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
                if not pleinecran:
                    L,H = event.w, event.h
                    fenetre = pygame.display.set_mode((L,H), pygame.RESIZABLE)
                    update_dimensions(L,H)
                else:
                    L,H = event.w, event.h
                    update_dimensions(L,H)
        #Bouton plein écran
        if btn_pleinecran.is_clicked(pos, clique):
            pygame.time.delay(200)
            pleinecran = not pleinecran
            if pleinecran:
                #Si mode plein écran on passe a la résolution de l'ecran
                fenetre = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
            else:
                #Si mode fenetre on passe a cette résolution
                fenetre = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
            L,H = fenetre.get_size()
            update_dimensions(L,H)
        #Bouton résolution
        if not pleinecran:
            if btn_resolution.is_clicked(pos, clique):
                pygame.time.delay(200)
                #Change la résolution par la suivante de la liste
                index = (index + 1) % len(resolutions)
                new_res = resolutions[index]
                fenetre = pygame.display.set_mode(new_res, pygame.RESIZABLE)
                L,H = new_res
                update_dimensions(L,H)
        #Clique ou non sur la barre de volume
        nouveau_volume = volume_barre.actualise(pos, actionclique)
        if nouveau_volume is not None:
            pygame.mixer.music.set_volume(nouveau_volume**1.5) #Volume pour un volume plus rapide
        #Clique sur le bouton retour
        if btn_retour.is_clicked(pos, clique):
            running = False
        fenetre.blit(imgfond, (0, 0))
        #Affiche le mot "Options"
        titre = fonttitle.render("OPTIONS", True, WHITE)
        fenetre.blit(titre, (L//2 - titre.get_width()//2, int(H*0.05)))
        #Dessine les boutons
        btn_pleinecran.draw(fenetre, fonttext)
        if not pleinecran:
            btn_resolution.draw(fenetre, fonttext)
        else:
            #En plein ecran on met Resolution désactivée
            txtpleinecran= fonttext.render("RESOLUTION DESACTIVE", True, (100,100,100))
            fenetre.blit(txtpleinecran, (L//2 - txtpleinecran.get_width()//2, int(H*0.25)+10))
        #Dessine la barre de volume
        dessin_volume = fonttext.render("VOLUME MUSIQUE", True, WHITE)
        fenetre.blit(dessin_volume, (L//2 - dessin_volume.get_width()//2, int(H*0.35)))
        volume_barre.draw(fenetre)
        #Tableau de touche du 
        tableauy = int(H*0.50)
        tabw = max(350, int(L*0.35))
        tabh = max(250, int(H*0.40))
        tableau_touche = pygame.Rect(L//2 - tabw//2, tableauy, tabw, tabh)
        pygame.draw.rect(fenetre, (50,50,50), tableau_touche, border_radius=15)
        pygame.draw.rect(fenetre, GOLD, tableau_touche, 2, border_radius=15)
        commande = ["COMMANDES DU JEU:","AVANCER: Z","RECULER: S","GAUCHE: Q","DROITE: D","PAUSE: ECHAP","LUMIERE: H","FILTRE: T", "ARME: 1,2,3","TIR: CLIQUE GAUCHE"]
        espacement = tabh // (len(commande)+1)
        for i, ligne in enumerate(commande):
            #Titre en or le reste en blanc
            if i == 0:
                titre_couleur = GOLD
            else:
                titre_couleur = WHITE
            texte = fonttext.render(ligne, True, titre_couleur)
            #Affichage des lignes
            fenetre.blit(texte,(L//2 - texte.get_width()//2, tableauy+10+(i*espacement)))
        btn_retour.draw(fenetre, fonttext)
        pygame.display.flip()
        clock.tick(60)
    return fenetre