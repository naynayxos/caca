import pygame
import sys
import subprocess
import gen_proc
import option

pygame.init()

fenetre = pygame.display.set_mode((0,0),pygame.FULLSCREEN)

#Fénétre jeu
WIDTH, HEIGHT = fenetre.get_size()
pygame.display.set_caption("FarLand Venture")
pygame.display.set_icon(pygame.image.load("ressource/logo.png"))

#Musique de fond
pygame.mixer.music.load("ressource/Musique.mp3")
pygame.mixer.music.play(-1) #Musique en boucle

#image de fond
backgroundori = pygame.image.load("ressource/images.png").convert()
background = pygame.transform.scale(backgroundori, (WIDTH, HEIGHT)) 

#Couleur
WHITE = (255,255,255)
SHADOW = (0,0,0,150)
BLACK = (0,0,0)
GLASS_HOVER = (255, 255, 255, 100)
GLASS_BASE = (255, 255, 255, 50)
GLASS_BORDER = (255, 255, 255, 150)
GLOW_COLOR = (100, 200, 255)
GOLD = (255, 215, 0)
GOLD_BRILLANT = (218, 179, 10)
GOLD_TRANSPARENT = (255, 215, 0, 100)

#Police
try:
    FONT_TITLE = pygame.font.Font("ressource/PoliceFarland2.ttf", 80)
    FONT_BUTTON = pygame.font.Font("ressource/police.ttf", 28)

except:
    FONT_TITLE = pygame.font.SysFont(None, 72)
    FONT_BUTTON = pygame.font.SysFont(None, 36)

class Button:
    def __init__(self,text, action):
        self.text = text
        self.action = action
        self.width = 0
        self.height = 0
        self.rect = pygame.Rect((0,0,0,0))
        self.led = 0
        self.dore = 0
    
    def update_pos(self, x, y, L, H):
        self.width = L
        self.height = H
        self.rect = pygame.Rect(x, y, L, H)
    
    def draw(self, win, mouse_pos):
        is_hover = self.rect.collidepoint(mouse_pos)
        if is_hover:
            self.led = min(255,self.led + 15)
            self.dore = min(255,self.dore + 20)
        else:
            self.led = max(0,self.led - 15)
            self.dore = max(0,self.dore - 20)

        # Effet doré lors du survol
        if is_hover:
            gold_rect = self.rect.inflate(10, 10)
            pygame.draw.rect(win, GOLD_BRILLANT, gold_rect, width=3, border_radius=20)

        # Dessiner le bouton avec effet de verre
        color = GOLD_TRANSPARENT if is_hover else GLASS_BORDER
        button_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(button_surface, color, (0, 0, self.width, self.height), border_radius=15)
        pygame.draw.rect(button_surface, GLASS_BORDER, (0, 0, self.width, self.height), width=1, border_radius=15)

        # Effet de lueur
        if self.led > 0:
            pygame.draw.rect(button_surface, (*GOLD, self.led), (20, self.height - 6, self.width - 40, 4), border_radius=15)
        
        win.blit(button_surface, self.rect)

        text_surf = FONT_BUTTON.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)

        shadow = FONT_BUTTON.render(self.text, True, SHADOW)
        win.blit(shadow, (text_rect.x + 1, text_rect.y + 1))
        win.blit(text_surf, text_rect)

    def is_clicked(self, mouse_pos, mouse_pressed):
        return self.rect.collidepoint(mouse_pos) and mouse_pressed[0] #Clic gauche
    
#Les boutons
buttons = [
    Button("Nouvelle Partie","new"),
    Button("Charger Partie", "load"),
    Button("Options", "options"),
    Button("Quitter", "quit")
]

#Recalcul de la resolution après le menu des options
def update_resolution(L, H):
    global background, FONT_TITLE, FONT_BUTTON, WIDTH, HEIGHT
    WIDTH,HEIGHT = L,H
    #Redimensionner l'image de fond
    background = pygame.transform.scale(backgroundori, (L, H))
    #Taille police 
    tailletitre = int(80*H/1080)
    taillebutoon=int(28*H/1080)
    FONT_TITLE = pygame.font.Font("ressource/PoliceFarland2.ttf", tailletitre)
    FONT_BUTTON = pygame.font.Font("ressource/police.ttf", taillebutoon)
    #Repositionner les boutons
    btnespace = (int(H*0.03))
    #Largeur et hauteur des boutons en fonction de la résolution
    btnL=(int(L*0.15))
    btnH=(int(H*0.05))
    startX = (int(L*0.75))-(btnL//2)
    startY= (int(H*0.40))
    #Met à jour la position des boutons
    for i, button in enumerate(buttons):
        posy = startY+i*(btnH+btnespace)
        button.update_pos(startX, posy, btnL, btnH)

#On l'appelle une première fois pour initialiser les positions
update_resolution(WIDTH, HEIGHT)

running = True
clock = pygame.time.Clock()

while running:
    clock.tick(60)  # Limite à 60 FPS
    fenetre.blit(background, (0,0))

    mouse_pos = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()

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

    fenetre.blit(shadow1, (x1 + 3, y1 + 3))
    fenetre.blit(title1, (x1, y1))
    fenetre.blit(shadow2, (x2 + 3, y2 + 3))
    fenetre.blit(title2, (x2, y2))

    for button in buttons:
        button.draw(fenetre, mouse_pos)
        if button.is_clicked(mouse_pos, mouse_pressed):
            pygame.time.delay(200)
            if button.action == "new":
                print("Nouvelle Partie")
                pygame.mixer.music.fadeout(500)
                gen_proc.lancer(fenetre)
                print("Retour au menu")
                pygame.event.clear()
                WIDTH, HEIGHT = fenetre.get_size()
                update_resolution(WIDTH, HEIGHT)
                pygame.mixer.music.load("ressource/Musique.mp3")
                pygame.mixer.music.play(-1)
            elif button.action == "load":
                print("Charger Partie")
            elif button.action == "options":
                print("Options")
                # Lancer le menu des options
                fenetre=option.option_menu(fenetre, WIDTH, HEIGHT)
                #Actualiser la taille de la fenêtre après le menu des options
                WIDTH, HEIGHT = fenetre.get_size()
                update_resolution(WIDTH, HEIGHT)
                #Pour eviter missvkivk entre retour et nouvelle partie
                pygame.event.clear()
                pygame.time.delay(300)
            elif button.action == "quit":
                running = False
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    pygame.display.flip()
pygame.quit()
print("Fermeture du jeu.")