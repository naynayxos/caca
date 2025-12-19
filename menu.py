import pygame
import sys
import subprocess

pygame.init()

#Fénétre jeu
WIDTH = 1920
HEIGHT = 1080
fenetre = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("FarLand Venture")
pygame.display.set_icon(pygame.image.load("ressource/logo.png"))

#Musique de fond
pygame.mixer.music.load("ressource/Musique.mp3")
pygame.mixer.music.play(-1) #Musique en boucle

#image de fond
background = pygame.image.load("ressource/images.jpg")
background = pygame.transform.scale(background, (WIDTH, HEIGHT)) 

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
    FONT_TITLE = pygame.font.Font("ressource/titre.ttf", 72)
    FONT_BUTTON = pygame.font.Font("ressource/police.ttf", 36)

except:
    FONT_TITLE = pygame.font.SysFont(None, 72)
    FONT_BUTTON = pygame.font.SysFont(None, 36)

class Button:
    def __init__(self,text,center_x,center_y, action):
        self.text = text
        self.action = action
        self.center_y = center_y
        self.width = 380
        self.height = 60
        self.rect = pygame.Rect((center_x,center_y,self.width,self.height))
        self.led = 0
        self.dore = 0
    
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

#Position des boutons
button_y = HEIGHT - 120
button_spacing = 60
button_width = 380
tot_width = (button_width * 4) + (button_spacing*3)
button_x = (WIDTH - tot_width) // 2
    
#Les boutons
buttons = [
    Button("Nouvelle Partie", button_x, button_y,"new"),
    Button("Charger Partie", button_x + button_width + button_spacing, button_y, "load"),
    Button("Options", button_x + (button_width + button_spacing) * 2, button_y, "options"),
    Button("Quitter", button_x + (button_width + button_spacing) * 3, button_y, "quit")
]

running = True
clock = pygame.time.Clock()

while running:
    clock.tick(60)  # Limite à 60 FPS
    fenetre.blit(background, (0,0))

    mouse_pos = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()

    title = FONT_TITLE.render("FarLand Venture", True, WHITE)
    shadow = FONT_TITLE.render("FarLand Venture", True, SHADOW)
    fenetre.blit(shadow, (WIDTH//2 - title.get_width()//2 + 3, 103))
    fenetre.blit(title, (WIDTH//2 - title.get_width()//2, 100))

    for button in buttons:
        button.draw(fenetre, mouse_pos)
        if button.is_clicked(mouse_pos, mouse_pressed):
            pygame.time.delay(200)
            if button.action == "new":
                print("Nouvelle Partie")
                pygame.quit()
                subprocess.run(["python", "game.py"])
                sys.exit()
            elif button.action == "load":
                print("Charger Partie")
            elif button.action == "options":
                print("Options")
            elif button.action == "quit":
                running = False
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    pygame.display.flip()
pygame.quit()
print("Fermeture du jeu.")