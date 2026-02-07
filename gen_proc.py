import pygame
import sys
import os
import random
import math
import option
import ascenseur

ZOOM = 180
LARGEURMAP,HAUTEURMAP= 50,50
VITESSEJOUEUR = 10
VIDE = 2
MUR = 1
SOL = 0
NUIT = (15,15,25)
ASCENCEUR = 3

pygame.init()

ecran = pygame.display.Info()
pygame.display.set_caption("D-RED")
clock = pygame.time.Clock()

#assets
def texture(nom,taille = None, transparente = False):
    chemin = os.path.join("ressource", nom)
    try:
        img= pygame.image.load(chemin)
        if transparente:
            img.set_colorkey((255,255,255))
        if taille:
            w,h= taille
            img= pygame.transform.scale(img, (w, h))
        return img.convert_alpha()
    except:
        return None

class Objet:
    def __init__(self,x,y,name,type,size=None):
        self.rect = pygame.Rect(x,y,ZOOM,ZOOM)
        self.texture=texture(name,size,transparente=True)
        self.type = type   
        if type == "meuble":
            self.hitbox = self.rect.inflate(-20,-20)
        else:
            self.hitbox = self.rect
        
    def draw(self,surface, camera_x, camera_y):
        fenetre_x = self.rect.x + camera_x
        fenetre_y = self.rect.y + camera_y
        if self.texture:
            surface.blit(self.texture, (fenetre_x, fenetre_y))
        return fenetre_y+self.rect.height

def generer_objets(grille, salles):
    objets = []
    types = [{'nom': 'caisse.png', 'type': 'meuble', 'proba': 0.2},
            {'nom': 'plante.png', 'type': 'plante', 'proba': 0.2},
            {'nom': 'meuble.png', 'type': 'meuble', 'proba': 0.2}]
    for salle in salles:
        for y in range(salle.top, salle.bottom):
            for x in range(salle.left, salle.right):
                if grille[y][x] == SOL:
                    mur = False
                    if grille[y+1][x] == MUR:
                        mur = True
                    elif grille[y-1][x] == MUR:
                        mur = True
                    elif grille[y][x+1] == MUR:
                        mur = True
                    elif grille[y][x-1] == MUR:
                        mur = True
                    if mur:
                        if random.random() < 0.2: # 20% de chance un objet
                            t = random.choice(types)
                            if random.random() < t['proba']:
                                obj = Objet(x*ZOOM, y*ZOOM, t['nom'], t['type'], size=(ZOOM, ZOOM))
                                objets.append(obj)
    return objets

#Effet Lumiere
def lumiere(rayon):
    t = rayon*2.5
    s = pygame.Surface((t,t),pygame.SRCALPHA)
    c = (t//2,t//2)
    #plusieur cercle pour tamiser
    for i in range(rayon//2,0,-2):
        a = int(100*(i/(rayon//2)))
        if a>0:
            pygame.draw.circle(s,(255,240,200,5),c,i)
    longueurcone = rayon
    angless=30
    etape = 100 #Puissance dégradé
    for i in range(etape):
        distance = (i/etape)*longueurcone
        largeur= int(distance*math.tan(math.radians(angless)))
        posx = c[0]+distance
        posy = c[1]
        p=60*(1-(i/etape))
        if largeur>0:
            brosse = pygame.Surface((largeur*2,largeur*2), pygame.SRCALPHA)
            pygame.draw.circle(brosse,(255,250,220,int(p)),(largeur,largeur),largeur)
            dist = brosse.get_rect(center=(posx,posy))
            s.blit(brosse,dist,special_flags=pygame.BLEND_RGBA_ADD)
    return s

def angletrace(c, t, f):
    d = (t-c+180)%360-180
    return c+d*f

#couloir verticale
def c_vertical(grille, y1,y2,x):
    for y in range(min(y1,y2),max(y1,y2)+1):
        grille[y][x]=SOL

#couloir horizontal
def c_horizontal(grille, x1,x2,y):
    for x in range(min(x1,x2),max(x1,x2)+1):
        grille[y][x]=SOL

#generation map
def generemap():
    grille = [[VIDE for x in range(LARGEURMAP)] for y in range(HAUTEURMAP)]
    salles=[]
    distance_min =7
    distance_max = 10#Dstance entre les salles
    for i in range(80): #Nombre de salles a essayer de generer
        w = random.randint(5,9)
        h = random.randint(5,9)
        if not salles:
            x = LARGEURMAP//2 - w//2
            y = HAUTEURMAP//2 - h//2
            suivant = False
        else:
            suivant = random.choice(salles)
            place = False
            for _ in range(10):
                angle = random.uniform(0, 2*math.pi)
                distance = random.randint(distance_min, distance_max)
                kx = int(suivant.centerx+ math.cos(angle)*distance) - (w//2)
                ky = int(suivant.centery + math.sin(angle)*distance) - (h//2)
                if 2<kx<LARGEURMAP-w-2 and 2<ky<HAUTEURMAP-h-2:
                    nouvelle_salle = pygame.Rect(kx,ky,w,h)
                    if not any(nouvelle_salle.inflate(2,2).colliderect(s) for s in salles):
                        x,y = kx, ky
                        place = True
            if not place:
                continue

        nouvelle_salle = pygame.Rect(x,y,w,h)
        salles.append(nouvelle_salle)

        for k in range(nouvelle_salle.top, nouvelle_salle.bottom):
            for v in range(nouvelle_salle.left, nouvelle_salle.right):
                grille[k][v] = SOL

        if suivant:
            #On creuse couloir jusqu'a la salle precedente
            prec = suivant.center
            proc = nouvelle_salle.center
            x1, y1 = int(prec[0]), int(prec[1])
            x2, y2 = int(proc[0]), int(proc[1])
            if random.choice([True, False]):
                c_horizontal(grille, x1, x2, y1)
                c_vertical(grille, y1, y2, x2)
            else:
                c_vertical(grille, y1, y2, x1)
                c_horizontal(grille, x1, x2, y2)
    
    salle_depart = salles[0]
    px,py = int(salle_depart.centerx), int(salle_depart.centery)
    grille[py][px] = ASCENCEUR
    
    #On ajoute des murs a chaque sol touchant une case vide
    grille_fin = [row[:] for row in grille]
    for y in range(1, HAUTEURMAP-1):
        for x in range(1, LARGEURMAP-1):
            if grille[y][x]==VIDE:
                #On regarde donc ses voisins
                voisin = False
                if grille[y+1][x]==SOL or grille[y-1][x]==SOL or grille[y][x+1]==SOL or grille[y][x-1]==SOL:
                    voisin = True
                if voisin:
                    grille_fin[y][x] = MUR
    return grille_fin, salles, salles[0].center

#Collision
def obstacle(rect_joueur,grille):
    obstacle=[]
    casex=int(rect_joueur.centerx/ZOOM)
    casey=int(rect_joueur.centery/ZOOM)
    for y in range(casey-2,casey+3):
        for x in range(casex-2,casex+3):
            if 0 <= x < LARGEURMAP and 0 <= y < HAUTEURMAP:
                case = grille[y][x]
                if case == MUR or case == VIDE:
                    rect_mur = pygame.Rect(x*ZOOM,y*ZOOM,ZOOM,ZOOM)
                    obstacle.append(rect_mur)
    return obstacle

def lancer(ecran):
    LARGEUR, HAUTEUR = ecran.get_size()
    clock = pygame.time.Clock()
    pygame.mixer.music.load("ressource/explo.mp3")
    pygame.mixer.music.play(-1)

    #Chargement assets
    img_sol = texture("sol.png",(ZOOM+1,ZOOM+1))
    img_murface = texture("murface.png", (ZOOM+1, ZOOM+1))
    img_murtop = texture("murtop.png", (ZOOM+1, ZOOM+1))
    img = texture("chargement.png", (LARGEUR, HAUTEUR))
    animationjoueur = [
    texture("joueur.png",(100,100), transparente=True),
    texture("joueurgauche.png",(100,100), transparente=True),
    texture("joueurdroit.png",(100,100), transparente=True)
    ]
    lumierefin = lumiere(450)

    #Ascenseur
    menu = ascenseur.Ascenseur(LARGEUR, HAUTEUR)
    #Dictionnaire pour sauvegarder les etages déjà visités
    sauvegarde_etage =  {}
    niveau_actuel = 1

    #Partie
    carte, salles, pos = generemap()
    objets = generer_objets(carte, salles)
    #position
    joueurx = pos[0]*ZOOM+(ZOOM//2)
    joueury = pos[1]*ZOOM+(ZOOM//2)
    #hitbox
    joueur_rect = pygame.Rect(0,0,40,40)
    joueur_rect.center = (joueurx, joueury)

    lumiereallume = False
    angle = 0
    angleactuelle = 0
    dernierkx = 1
    dernierky =0
    animation = 0
    time = 0
    vitesse = 5

    ouvertemenu = False
    surascenceur = False #Pour savoir si on peut interagir avec l'ascenseur
    menu_boutons = []

    font = pygame.font.Font("ressource/police.ttf", 24)
    running = True
    while running:
        #Vérifie si le joueur est sur un ascenseur
        casex = int(joueur_rect.centerx/ZOOM)
        casey = int(joueur_rect.centery/ZOOM)
        surascenceur = False
        if 0 <= casex < LARGEURMAP and 0 <= casey < HAUTEURMAP:
            if carte[casey][casex] == ASCENCEUR:
                surascenceur = True

        #Si on s'eloigne de l'ascenseur alors on ferme le menu
        if not surascenceur:
            ouvertemenu = False

        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    lumiereallume = not lumiereallume
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_e and surascenceur:
                    ouvertemenu = not ouvertemenu
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: #Clic gauche
                    click = True
        #Commande
        kx, ky = 0,0
        if not ouvertemenu:
            keys = pygame.key.get_pressed()

            if keys[pygame.K_LEFT] or keys[pygame.K_q]:
                kx = -VITESSEJOUEUR
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                kx = VITESSEJOUEUR
            if keys[pygame.K_UP] or keys[pygame.K_z]:
                ky = -VITESSEJOUEUR
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                ky = VITESSEJOUEUR

            #Diagonale meme vitesse
            if kx !=0 and ky !=0:
                kx *=0.707
                ky *=0.707

            #Mise a jour angle
            if kx !=0 or ky != 0:
                dernierkx, dernierky=kx,ky
            anglecible = math.degrees(math.atan2(-dernierky, dernierkx))
            angleactuelle = angletrace(angleactuelle,anglecible,0.15)

            if kx!=0 or ky!=0:
                time +=1
                if time > vitesse:
                    time = 0
                    animation = (animation+1)%len(animationjoueur)
            else:
                animation = 0
                time = 0

            #Calcul angle pour perso
            anglejoueur = math.degrees(math.atan2(-dernierky, dernierkx))
            angleactuellejoueur = angletrace(angleactuelle, anglejoueur, 0.15)
            #Rotation image joueur
            angle = angleactuellejoueur +90

            #Collision X
            joueur_rect.x += kx
            o = obstacle(joueur_rect,carte)
            for obj in objets:
                if obj.type == "meuble":
                    o.append(obj.hitbox)

            for mur in o:
                if joueur_rect.colliderect(mur):
                    if kx >0:
                        joueur_rect.right = mur.left
                    if kx <0:
                        joueur_rect.left = mur.right

            #Collision Y
            joueur_rect.y += ky
            o = obstacle(joueur_rect,carte)
            for obj in objets:
                if obj.type == "meuble":
                    o.append(obj.hitbox)
            
            for mur in o:
                if joueur_rect.colliderect(mur):
                    if ky >0:
                        joueur_rect.bottom = mur.top
                    if ky <0:
                        joueur_rect.top = mur.bottom

        #Suivi joueur
        camera_x = (LARGEUR//2)-joueur_rect.centerx
        camera_y = (HAUTEUR//2)-joueur_rect.centery

        #Dessin sol
        ecran.fill((0,0,0))
        for y in range(HAUTEURMAP):
            for x in range(LARGEURMAP):
                case = carte[y][x]
                screen_x = x * ZOOM + camera_x
                screen_y= y*ZOOM+camera_y
                #Dessine que ce qui est visible
                if case == SOL and img_sol is not None:
                    if -ZOOM<screen_x<LARGEUR and -ZOOM< screen_y<HAUTEUR:
                        ecran.blit(img_sol, (screen_x,screen_y))
        
        #Liste de chosses a dessiner apres le sol
        adessiner = []

        #Dessin murs
        for y in range(HAUTEURMAP):
            for x in range(LARGEURMAP):
                case = carte[y][x]
                if case == MUR:
                    screen_x = x * ZOOM + camera_x
                    screen_y= y*ZOOM+camera_y
                    if -ZOOM<screen_x<LARGEUR and -ZOOM< screen_y< HAUTEUR:
                        img = img_murtop
                        #On regarsde si il y a du sol en dessous
                        if y+1<HAUTEURMAP and carte[y+1][x]==SOL:
                            img = img_murface
                        if img:
                            pos_y = screen_y + ZOOM
                            adessiner.append((pos_y, img,(screen_x,screen_y)))
                        
        #Dessin objets
        for obj in objets:
            fenetre_x = obj.rect.x + camera_x
            fenetre_y = obj.rect.y + camera_y
            if -ZOOM<fenetre_x<LARGEUR and -ZOOM<fenetre_y<HAUTEUR:
                pos_y = fenetre_y + obj.rect.height
                adessiner.append((pos_y, obj.texture, (fenetre_x, fenetre_y)))

        #Dessin joueur
        img_joueur = animationjoueur[animation]
        if img_joueur is not None:
            joueurtourne = pygame.transform.rotate(img_joueur, angle)
            rectaffiche = joueurtourne.get_rect()
            xjoueur = joueur_rect.centerx + camera_x
            yjoueur = joueur_rect.centery + camera_y
            rectaffiche.center = (xjoueur, yjoueur)
            pos_y= rectaffiche.bottom
            adessiner.append((pos_y, joueurtourne, rectaffiche.topleft))

        #Tri la liste a dessiner par ordre Y
        adessiner.sort(key=lambda x: x[0])
        for i in adessiner:
            ecran.blit(i[1], i[2]) #image, position

        #Effet Lumiere quand activé
        if lumiereallume:
            #Maque sombre autoru
            masque = pygame.Surface((LARGEUR,HAUTEUR))
            masque.fill(NUIT)
            #Tourne lumiere
            lumieretourne = pygame.transform.rotate(lumierefin,angleactuelle)
            rectlumiere = lumieretourne.get_rect(center =(LARGEUR//2,HAUTEUR//2))
            #Lumiere au masque
            masque.blit(lumieretourne,rectlumiere,special_flags=pygame.BLEND_ADD)
            ecran.blit(masque,(0,0),special_flags=pygame.BLEND_MULT)

        #Message sur ascenseur
        if surascenceur and not ouvertemenu:
            txt = font.render("Appuyez sur E pour interagir", True, (255,255,255))
            txt_rect = txt.get_rect(center=(LARGEUR//2, HAUTEUR-50))
            #Fond du message
            fond = pygame.Surface((txt_rect.width+20, txt_rect.height+10), pygame.SRCALPHA)
            fond.fill((0,0,0,150))
            fond.set_alpha(150)
            ecran.blit(fond, (txt_rect.x-10, txt_rect.y-5))
            ecran.blit(txt, txt_rect)

        #Menu ascenseur
        if ouvertemenu:
            menu_boutons = menu.dessiner(ecran, niveau_actuel)
            if click:
                mouse_pos = pygame.mouse.get_pos()
                etage_choisi = menu.clique(mouse_pos, menu_boutons)
                if etage_choisi:
                    sauvegarde_etage[niveau_actuel] = {
                        "carte": carte,
                        "salles": salles,
                        "objets": objets,
                    }
                    menu.ecran_charge(ecran, img, etage_choisi)
                    niveau_actuel = etage_choisi
                    #Si l'étage a déjà été visité, on charge la sauvegarde
                    if etage_choisi in sauvegarde_etage:
                        carte = sauvegarde_etage[etage_choisi]["carte"]
                        salles = sauvegarde_etage[etage_choisi]["salles"]
                        objets = sauvegarde_etage[etage_choisi]["objets"]
                    else:
                        carte, salles, pos = generemap()
                        objets = generer_objets(carte, salles)
                    #Repositionne le joueur sur la nouvelle carte a l"ascenseur
                    start = salles[0]
                    joueurx = start.centerx * ZOOM + (ZOOM//2)
                    joueury = start.centery * ZOOM + (ZOOM//2)
                    joueur_rect.center = (joueurx, joueury)
                    ouvertemenu = False
                    pygame.event.clear()

        pygame.display.flip()
        clock.tick(60)