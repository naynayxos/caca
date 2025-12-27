import pygame
import sys
import os
import random
import math

LARGEUR = 1920
HAUTEUR = 1080
ZOOM = 180
LARGEURMAP,HAUTEURMAP= 50,50
VITESSEJOUEUR = 10
VIDE = 2
MUR = 1
SOL = 0
NUIT = (15,15,25)

pygame.init()
ecran = pygame.display.set_mode((LARGEUR,HAUTEUR))
pygame.display.set_caption("D-RED")
clock = pygame.time.Clock()

#assets
def texture(nom,taille = None):
    chemin = os.path.join("ressource", nom)
    try:
        img= pygame.image.load(chemin)
        if taille:
            img= pygame.transform.scale(img, (ZOOM, ZOOM))
        return img.convert_alpha()
    except:
        return None

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
    for i in range(50):
        w = random.randint(4,8)
        h = random.randint(4,8)
        x = random.randint(2,LARGEURMAP-w-2)
        y = random.randint(2, HAUTEURMAP-h-2)
        nouvelle_salle = pygame.Rect(x,y,w,h)

        #Touche une autre salle ou pas
        touche = False
        for i in salles:
            if nouvelle_salle.inflate(2,2).colliderect(i):
                touche = True
                break
        
        #Touche rien
        if not touche:
            salles.append(nouvelle_salle)
            for k in range(nouvelle_salle.top, nouvelle_salle.bottom):
                for v in range(nouvelle_salle.left, nouvelle_salle.right):
                    grille[k][v] = SOL

            #On creuse couloir jusqu'a la salle precedente
            if len(salles)>1:
                prec = salles[-2].center
                proc = nouvelle_salle.center
                if random.choice([True,False]):
                    c_horizontal(grille,prec[0],proc[0],prec[1])
                    c_vertical(grille,prec[1],proc[1],proc[0])
                else:
                    c_vertical(grille,prec[1],proc[1],proc[0])
                    c_horizontal(grille,prec[0],proc[0],prec[1])
    
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
    return grille_fin, salles[0].center

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

    #Chargement assets
    img_sol = texture("sol.png")
    img_murface = texture("murface.png")
    img_murtop = texture("murtop.png")
    animationjoueur = [
    texture("joueur.png",(48,48)),
    texture("joueurgauche.png",(48,48)),
    texture("joueurdroit.png",(48,48))
    ]
    lumierefin = lumiere(450)

    #Partie
    carte, pos = generemap()
    #position
    joueurx = pos[0]*ZOOM+(ZOOM//2)
    joueury = pos[1]*ZOOM+(ZOOM//2)
    #hitbox
    joueur_rect = pygame.Rect(0,0,20,20)
    joueur_rect.center = (joueurx, joueury)

    lumiereallume = False
    angle = 0
    angleactuelle = 0
    dernierkx = 1
    dernierky =0
    animation = 0
    time = 0
    vitesse = 15

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    lumiereallume = not lumiereallume

        #Commande
        keys = pygame.key.get_pressed()
        kx =0
        ky =0
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
        angle = angleactuelle+90
        anglelumiere = angleactuelle

        if kx!=0 or ky!=0:
            time +=1
            if time > vitesse:
                time = 0
                animation = (animation+1)%len(animationjoueur)
        else:
            animation = 0
            time = 0

        #Deplacement X
        joueur_rect.x += kx
        o = obstacle(joueur_rect,carte)
        for mur in o:
            if joueur_rect.colliderect(mur):
                if kx >0:
                    joueur_rect.right = mur.left
                if kx <0:
                    joueur_rect.left = mur.right
        
        #Deplacement Y
        joueur_rect.y += ky
        for mur in o:
            if joueur_rect.colliderect(mur):
                if ky >0:
                    joueur_rect.bottom = mur.top
                if ky <0:
                    joueur_rect.top = mur.bottom

        #Suivi joueur
        camera_x = (LARGEUR//2)-joueur_rect.centerx
        camera_y = (HAUTEUR//2)-joueur_rect.centery

        #Dessin map
        ecran.fill((0,0,0))
        for y in range(HAUTEURMAP):
            for x in range(LARGEURMAP):
                case = carte[y][x]
                if case == VIDE:
                    continue
                screen_x = x * ZOOM + camera_x
                screen_y= y*ZOOM+camera_y
                if -ZOOM<screen_x<LARGEUR and -ZOOM< screen_y<HAUTEUR:
                    if case == SOL and img_sol is not None:
                        ecran.blit(img_sol, (screen_x,screen_y))
                    elif case == MUR:
                        if y+1<HAUTEURMAP and carte[y+1][x] == SOL:
                            if img_murface:
                                ecran.blit(img_murface,(screen_x,screen_y))
                        else:
                            if img_murtop:
                                ecran.blit(img_murtop, (screen_x,screen_y))

        #Dessin joueur
        img_joueur = animationjoueur[animation]
        if img_joueur is not None:
            joueurtourne = pygame.transform.rotate(img_joueur, angle)
            recttourne = joueurtourne.get_rect(center=(LARGEUR//2,HAUTEUR//2))
            ecran.blit(joueurtourne, recttourne.topleft)

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

        pygame.display.flip()
        clock.tick(60)