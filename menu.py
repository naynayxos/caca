import pygame
import webbrowser
import jeu
import option
import dl
import rejoindre

pygame.init()

#Fénétre jeu
fenetre = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
WIDTH, HEIGHT = fenetre.get_size()

#Titre et logo de la fenêtre
pygame.display.set_caption("D-RED")
pygame.display.set_icon(pygame.image.load("ressource/logo.png"))

#Musique de fond
pygame.mixer.music.load("ressource/Musique.mp3")
pygame.mixer.music.play(-1) #Musique en boucle

#image de fond
backgroundori = pygame.image.load("ressource/images.png").convert()
background = pygame.transform.scale(backgroundori, (WIDTH, HEIGHT)) 
imgsite = pygame.image.load("ressource/site.png").convert_alpha()
img_site = pygame.transform.scale(imgsite, (100, 100))
rect_site = img_site.get_rect()

#Couleur
WHITE = (255,255,255)
SHADOW = (0,0,0,150)
BLACK = (0,0,0)
GLASS_BORDER = (255, 255, 255, 150)
GOLD = (255, 215, 0)
GOLD_BRILLANT = (218, 179, 10)
GOLD_TRANSPARENT = (255, 215, 0, 100)

#Police
FONT_TITLE = pygame.font.Font("ressource/PoliceFarland2.ttf", 80)
FONT_BUTTON = pygame.font.Font("ressource/police.ttf", 28)

class Button:
    def __init__(self,text, action):
        self.text = text
        self.action = action
        self.width = 0
        self.height = 0
        self.rect = pygame.Rect((0,0,0,0))
        self.led = 0
        self.dore = 0
    
    def update_pos(self, x, y, L, H): #met a jour les boutons si on change de res
        self.width = L
        self.height = H
        self.rect = pygame.Rect(x, y, L, H)
    
    def draw(self, win, mouse_pos):
        is_hover = self.rect.collidepoint(mouse_pos) #Sur rectangle ou pas ?
        #Effet lumineux
        if is_hover:
            self.led = min(255,self.led + 15)
            self.dore = min(255,self.dore + 20)
        else:
            self.led = max(0,self.led - 15)
            self.dore = max(0,self.dore - 20)

        # Effet doré lors du survol
        if is_hover:
            gold_rect = self.rect.inflate(10, 10) #Rectangle contour
            pygame.draw.rect(win, GOLD_BRILLANT, gold_rect, width=3, border_radius=20)

        # Dessiner le bouton avec effet de verre
        if is_hover:
            color = GOLD_TRANSPARENT
        else:
            color = GLASS_BORDER
        #Transparence
        button_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(button_surface, color, (0, 0, self.width, self.height), border_radius=15)
        pygame.draw.rect(button_surface, GLASS_BORDER, (0, 0, self.width, self.height), width=1, border_radius=15)

        # Effet de lueur
        if self.led > 0:
            pygame.draw.rect(button_surface, (*GOLD, self.led), (20, self.height - 6, self.width - 40, 4), border_radius=15)
        
        win.blit(button_surface, self.rect)

        #Texte et ombre
        text_surf = FONT_BUTTON.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        shadow = FONT_BUTTON.render(self.text, True, SHADOW)

        #Decale ombre pour relief
        win.blit(shadow, (text_rect.x + 1, text_rect.y + 1))
        win.blit(text_surf, text_rect)

    def is_clicked(self, mouse_pos, mouse_pressed):
        #True si souris survol et clic gauche
        return self.rect.collidepoint(mouse_pos) and mouse_pressed[0] #Clic gauche

#Recalcul de la resolution après le menu des options
def update_resolution(L, H):
    #Pour modif variable global
    global background, FONT_TITLE, FONT_BUTTON, WIDTH, HEIGHT, rect_site
    WIDTH,HEIGHT = L,H
    #Redimensionner l'image de fond
    background = pygame.transform.scale(backgroundori, (L, H))
    #Taille police par nouvelle resolution
    tailletitre = int(80*H/1080)
    taillebutoon=int(28*H/1080)
    FONT_TITLE = pygame.font.Font("ressource/PoliceFarland2.ttf", tailletitre)
    FONT_BUTTON = pygame.font.Font("ressource/police.ttf", taillebutoon)
    #Redimensionner l'image du site
    rect_site = img_site.get_rect(bottomright=(L-30, H-30))
    #Repositionner les boutons
    btnespace = (int(H*0.02))
    #Largeur et hauteur des boutons en fonction de la résolution
    btnL=(int(L*0.19))
    btnH=(int(H*0.05))
    startX = (int(L*0.75))-(btnL//2)
    startY= (int(H*0.38))
    #Met à jour la position des boutons
    for i, button in enumerate(buttons):
        posy = startY+i*(btnH+btnespace)
        button.update_pos(startX, posy, btnL, btnH)

def retourmenu():
    #Recharge menu apres partie
    pygame.event.clear()
    #Remet res
    nouvres = pygame.display.get_surface()
    nouvlard, nouvhaut = nouvres.get_size()
    update_resolution(nouvlard, nouvhaut)
    #Remet musique
    pygame.mixer.music.load("ressource/Musique.mp3")
    pygame.mixer.music.play(-1)

#Les boutons
buttons = [
    Button("Nouvelle Partie","new"),
    Button("Charger Partie", "load"),
    Button("Heberger Partie", "hote"),
    Button("Rejoindre Partie", "rejoindre"),
    Button("Options", "options"),
    Button("Quitter", "quit")
]

#On l'appelle une première fois pour initialiser les positions
update_resolution(WIDTH, HEIGHT)

running = True
clock = pygame.time.Clock()

while running:
    clock.tick(60)  # Limite à 60 FPS
    #Fermeture du jeu
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    #Fond de depart
    fenetre.blit(background, (0,0))
    #Titre et ombre
    title1 = FONT_TITLE.render("FarLand", True, WHITE)
    shadow1= FONT_TITLE.render("FarLand", True, SHADOW)
    title2 = FONT_TITLE.render("Venture", True, WHITE)
    shadow2 = FONT_TITLE.render("Venture", True, SHADOW)

    #Coordonnées du titre1
    x1 = (int(WIDTH*0.75)) - (title1.get_width()//2)
    y1= (int(HEIGHT*0.20))
    #Coordonnées du titre2
    y2 = y1+ title1.get_height() - 10
    x2 = (int(WIDTH*0.75)) - (title2.get_width()//2)
    #Affichage sur ecran
    fenetre.blit(shadow1, (x1 + 3, y1 + 3))
    fenetre.blit(title1, (x1, y1))
    fenetre.blit(shadow2, (x2 + 3, y2 + 3))
    fenetre.blit(title2, (x2, y2))
    fenetre.blit(img_site, rect_site)
    #Coordonne souris et action
    mouse_pos = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()
    #Ouvrir le site web en cliquant sur l'image du site
    if rect_site.collidepoint(mouse_pos) and mouse_pressed[0]:
        pygame.time.delay(200)  # eviter les clics multiples
        webbrowser.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    #Logique et affichage boutons
    for button in buttons:
        button.draw(fenetre, mouse_pos)
        if button.is_clicked(mouse_pos, mouse_pressed):
            pygame.time.delay(200) #Pause missclick
            #Nouvelle partie
            if button.action == "new":
                print("Nouvelle Partie")
                pygame.mixer.music.fadeout(500) #Baisse en fondu le son
                #lance le Chagement
                dl.ecran_chargement(fenetre, WIDTH, HEIGHT)
                #lance le Mode Hote
                jeu.lancer(fenetre, mode = "solo")
                retourmenu()
            #Mode host
            elif button.action == "hote":
                print("Lancement du serveur")
                pygame.mixer.music.fadeout(500)
                #Chargement
                dl.ecran_chargement(fenetre, WIDTH, HEIGHT)
                #Mode Hote
                jeu.lancer(fenetre, mode = "hote")
                retourmenu()
            #Charger Partie
            elif button.action == "load":
                print("Charger Partie")
            #Options
            elif button.action == "options":
                print("Options")
                # Lancer le menu des options
                fenetre=option.option_menu(fenetre, WIDTH, HEIGHT)
                retourmenu()
                pygame.time.delay(300)
            #Rejoindre
            elif button.action == "rejoindre":
                print("Rejoindre")
                ip = rejoindre.rejoindre(fenetre, WIDTH,HEIGHT) #OUvre ecran pour rentrer IP
                if ip: #Si l'IP est rentré
                    pygame.mixer.music.fadeout(500)
                    #Chargement
                    dl.ecran_chargement(fenetre, WIDTH, HEIGHT)
                    #Mode Client
                    jeu.lancer(fenetre, mode = "client", ip=ip)
                    retourmenu()
            #Quitter le jeu
            elif button.action == "quit":
                running = False
    #Met ajour affichage
    pygame.display.flip()
pygame.quit()
print("Fermeture du jeu.")