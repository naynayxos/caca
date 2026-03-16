import pygame
import sys
import option
import ascenseur
import pause
import socket
import pickle
import filtre
import overlay
import monstre
import random  
import math

from prerequis import *
from prerequis import texture
from lumiere import Lumiere
from cartegen import generemap, generer_objets
from joueur import Joueur
from arme import Arme

pygame.init()
ecran = pygame.display.Info()
pygame.display.set_caption("D-RED")

def lancer(ecran, mode = "solo", ip=None):
    monstre.init_texture()
    LARGEUR, HAUTEUR = ecran.get_size()
    clock = pygame.time.Clock()
    #Asset musque ..
    police, hudmode, hudinventaire, inventaire, coeur =overlay.overlay_HUD()
    pygame.mixer.music.load("ressource/explo.mp3")
    pygame.mixer.music.play(-1)

    #Serveur
    IPSERV = "51.38.115.211"
    #Reseaux
    socket_jeu = None
    joueursup = {} #Dico qui stock id et tout le reste
    connect = False
    buffer = b"" #Memoire pour les messages reseauwx
    #Si on va pas en solo on lance le multi
    if mode != "solo":
        socket_jeu = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if mode == "hote":
            print("Mode Hote: Envoi carte au serveur {IPSERV}...")
            #Ecran d'attente
            ecran.fill((0,0,0))
            font = pygame.font.SysFont("ressource/police.ttf", 36)
            text = font.render("Generation de la carte...", True, (255,255,255))
            ecran.blit(text, (LARGEUR//2 - 200, HAUTEUR//2))
            pygame.display.flip()
            #Configurer le serveur
            try:
                #Connexion au serveur
                socket_jeu.connect((IPSERV, 5555))
                #Dit au serv qu'on est host
                socket_jeu.send(b"HOST")
                connect = True
                #L'hote genere la carte avec seed pour clien est meme
                partie = random.randint(0, 999999)
                random.seed(partie)
                carte, salles, pos = generemap()
                #Envoie la carte et seed au client
                data = pickle.dumps({"carte": carte, "salles": salles, "pos": pos, "seed": partie})
                tailledata = len(data).to_bytes(4, byteorder='big')
                socket_jeu.sendall(tailledata + data)
                #Attend confirme du serv
                socket_jeu.recv(1024)
                #Generation objet avec seed similaire
                random.seed(partie)
                objets = generer_objets(carte, salles)
                idjoueur = "HOTE"
                print("Carte enregistré avec succes")
            except Exception as e:
                print(f"Erreur de reseau hote: {e}")
                return
        elif mode == "client":
            if ip:
                cible = ip
            else:
                cible = IPSERV
            print(f"Mode Client: connexion au serveur {cible}...")
            try:
                #Connexion au serv
                socket_jeu.connect((cible, 5555))
                #On dit au serv qu'on esy Client
                socket_jeu.send(b"CLIENT")
                connect = True
                idjoueur = "CLIENT"
                print("Chargement de la carte..")
                #Reçoit la carte de l'hote
                taillerecu = socket_jeu.recv(4)
                tailledata = int.from_bytes(taillerecu, byteorder='big')
                #Telechargement de la carte
                paquets = []
                recu = 0
                while recu < tailledata:
                    paquet = socket_jeu.recv(min(4096, tailledata - recu))
                    if not paquet:
                        raise Exception("Connexion perdue")
                    paquets.append(paquet)
                    recu += len(paquet)
                #Decodage de la carte reçue
                data = b''.join(paquets)
                donneesmap = pickle.loads(data)
                carte = donneesmap["carte"]
                salles = donneesmap["salles"]
                pos = donneesmap["pos"]
                #Application de la seed pour avoir meme objet
                partie = donneesmap["seed"]
                random.seed(partie)
                objets = generer_objets(carte, salles)
            except Exception as e:
                print(f"Erreur de chargement de la carte: {e}")
                return
        #Empeche le jeu de buger quand on attend un mess reseau
        socket_jeu.setblocking(False)
    else:
        #Partie solo
        partie = random.randint(0, 999999)
        random.seed(partie)
        carte, salles, pos = generemap()
        random.seed(partie)
        objets = generer_objets(carte, salles)

    #Chargement assets
    img_sol = texture("sol.png",(ZOOM+1,ZOOM+1))
    img_ascenseur = texture("ascenseur.png",(ZOOM+1,ZOOM+1))
    img_murface = texture("murface.png", (ZOOM+1, ZOOM+1))
    img_murtop = texture("murtop.png", (ZOOM+1, ZOOM+1))
    img_load = texture("Chargement.png", (LARGEUR, HAUTEUR))
    img_munition = texture("munitionoverlay.png", (80,80), transparente=True)
    img_ballevol = texture("balle.png", (45,45), transparente=True)
    img_arme = {
        1: texture("pistolet.png",(250,80), transparente= True),
        2: texture("pompe.png",(250,80), transparente= True),
        3: texture("fusil.png",(250,80), transparente= True)
    }
    animationjoueur = [
    texture("joueur.png",(100,100), transparente=True),
    texture("joueurgauche.png",(100,100), transparente=True),
    texture("joueurdroit.png",(100,100), transparente=True)
    ]
    #Calque de lumiere
    lumieremarche = Lumiere(LARGEUR, HAUTEUR)

    #Menu Ascenseur
    menu = ascenseur.Ascenseur(LARGEUR, HAUTEUR)
    #Menu pause
    menupause = pause.EcranPause(LARGEUR, HAUTEUR)

    enpause = False
    ouvertemenu = False
    surascenceur = False #Pour savoir si on peut interagir avec l'ascenseur

    #Dictionnaire pour sauvegarder les etages déjà visités
    sauvegarde_etage =  {}
    niveau_actuel = 1
    #Sauvegarde niveau 1 pour pas le perdre
    sauvegarde_etage[1] = {"carte":carte,"salles":salles,"objets":objets}

    #Joueur
    px, py = int(salles[0].centerx), int(salles[0].centery)
    joueur = Joueur(px*ZOOM+(ZOOM//2), py*ZOOM+(ZOOM//2))
    #lst de monstres
    monstres=[]

    #Variable interface
    font = pygame.font.Font("ressource/police.ttf", 24)
    fondu = 255
    #Detecte changement donc animation diff
    armeprec = joueur.arsenal
    glissement = 0
    actionmap = {} #Reactualise quand caisse cassé et mun recup
    running = True
    while running:
        LARGEUR, HAUTEUR = ecran.get_size()
        #Vérifie si le joueur est sur un ascenseur
        casex = int(joueur.rect.centerx/ZOOM)
        casey = int(joueur.rect.centery/ZOOM)
        surascenceur = False
        #Si joueur on verifie ou il est
        if 0 <= casex < LARGEURMAP and 0 <= casey < HAUTEURMAP:
            if carte[casey][casex] == ASCENCEUR:
                surascenceur = True
        #Si on s'eloigne de l'ascenseur alors on ferme le menu
        if not surascenceur:
            ouvertemenu = False
        #Evenement clavier
        click = False
        for event in pygame.event.get():
            filtre.activation_mc(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                #Ouvre inventaire
                if event.key == pygame.K_LCTRL and not enpause:
                    inventaire= not inventaire
                 #Larry spawn
                if event.key == pygame.K_l:
                    m= monstre.Monstre(joueur.rect.centerx+100, joueur.rect.centery, 3, 100)
                    monstres.append(m)
                    print(f"Larry va te toucher la nuit")
                #Allume ou eteindre lampe
                if event.key == pygame.K_h:
                    joueur.lumiereallumee = not joueur.lumiereallumee
                    if (joueur.lumiereallumee or not joueur.lumiereallumee) and filtre.m_combat:
                        filtre.m_combat = False
                        joueur.lumiereallumee = True
                #Pause ou ferme
                if event.key == pygame.K_ESCAPE:
                    if ouvertemenu:
                        ouvertemenu = False
                    else:
                        enpause = not enpause
                #Menu ascenceur
                if event.key == pygame.K_e and surascenceur:
                    ouvertemenu = not ouvertemenu
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: #Clic gauche
                    click = True
           

       
        if not ouvertemenu and not enpause:
            keys = pygame.key.get_pressed()
            #Deplacement joueur et collision
            kx, ky = joueur.deplacer(keys, len(animationjoueur))
            joueur.collision(kx, ky, carte, objets)
            #Changement arme
            if keys[pygame.K_1]:
                joueur.changerarme(1)
            if keys[pygame.K_2]:
                joueur.changerarme(2)
            if keys[pygame.K_3]:
                joueur.changerarme(3)
            #Ramasser munition
            objetsreste = []
            for obj in objets:
                if obj.type == "munition" and joueur.rect.colliderect(obj.rect):
                    joueur.munition = joueur.munition + 15
                    #On dit au reseau qu'elle sont supp
                    actionmap[f"{obj.rect.x}-{obj.rect.y}"] = "S"
                else:
                    objetsreste.append(obj)
            objets = objetsreste #Met a jour les objets restants
            #Tir
            if keys[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]:
                joueur.tirer()
            #Deplacement balle et acutalisation caisse cassé
            casse = joueur.updatetir(carte, objets, monstres)
            if casse:
                for c in casse:
                    #On dit au réseau que ca devient munition
                    actionmap[f"{c.rect.x}-{c.rect.y}"] = "M"
            #Deplacement provisoire
            for m in monstres:
                if joueur.god>0:
                    joueur.god -=1
                if not m.mort :
                    kx, ky = m.deplacement(joueur.rect.centerx, joueur.rect.centery)
                    m.collision(kx, ky, carte, objets)
                    #le monstre touche le joueur
                    if m.rect.colliderect(joueur.rect) and joueur.god<=0:
                        joueur.hp -=10
                        joueur.god= 60
                
                        

        #Reseaux
        if connect:
            #position balle
            balle = "vide"
            if len(joueur.tir) > 0:
                balle = "_".join([f"{int(b.rect.x)}={int(b.rect.y)}" for b in joueur.tir])
            #Modification de la map sauvegarde
            modifmap = "vide"
            if len(actionmap) > 0:
                modifmap = "_".join([f"{coordonne}={etat}" for coordonne, etat in actionmap.items()])
                actionmap.clear() #Vide liste
            try:
                #Envoie la position du joueur
                message = f"{joueur.rect.centerx},{joueur.rect.centery},{niveau_actuel},{joueur.angle},{joueur.animation},{balle},{modifmap}\n"
                socket_jeu.send(message.encode('utf-8'))
            except BlockingIOError: pass
            except Exception as e: pass
            #Reçoit la position de l'autre joueur
            try:
                data = socket_jeu.recv(4096)
                if data:
                    buffer += data
                    if b"\n" in buffer:
                        texte = buffer.decode('utf-8')
                        paquetss = texte.split("\n")
                        dernier = paquetss[-2] #Isole dernier paquet
                        try:
                            #On traite les anciens
                            for paquet in paquetss[:-1]:
                                if paquet:
                                    listejoueur = paquet.split('|')
                                    for j in listejoueur:
                                        if j:
                                            jid, jinfos = j.split(':', 1)
                                            v = jinfos.split(',')
                                            #Si modif de carte
                                            if len(v)>=7 and v[6] != "vide":
                                                for m in v[6].split('_'):
                                                    coordonne, etat = m.split('=')
                                                    mx, my = coordonne.split('-')
                                                    mx, my = int(mx), int(my)
                                                    #Maintenant on ajoute la modif sur notre map
                                                    objsup = None
                                                    for obj in objets:
                                                        if obj.rect.x == mx and obj.rect.y == my:
                                                            if etat == "S":
                                                                objsup = obj
                                                            elif etat == "M" and getattr(obj, "type", "") != "munition":
                                                                #Caisse devient mun
                                                                obj.type = "munition"
                                                                obj.texture = texture("munition.png", (90,90), transparente=True)
                                                                obj.hitbox = obj.rect
                                                    #Objet ramassé
                                                    if objsup in objets:
                                                        objets.remove(objsup)
                            #Met a jour pos des joueur
                            if dernier:
                                listejoueur = dernier.split('|')
                                for j in listejoueur:
                                        if j:
                                            jid, jinfos = j.split(':', 1)
                                            v = jinfos.split(',')
                                            if len(v) >= 7:
                                                #Si nouveau joueur on l'ajoute au dico
                                                if jid not in joueursup:
                                                    joueursup[jid] = Joueur(int(v[0]), int(v[1]))
                                                #Met a jour stat
                                                autre = joueursup[jid]
                                                autre.rect.centerx = int(v[0])
                                                autre.rect.centery = int(v[1])
                                                autre.etage = int(v[2])
                                                autre.angle = float(v[3])
                                                autre.animation = int(v[4])
                                                #Lecture des balles
                                                autre.balles_reseau = []
                                                if v[5] != "vide":
                                                    for b in v[5].split('_'):
                                                        ballex, balley = b.split('=')
                                                        autre.balles_reseau.append((int(ballex), int(balley)))
                        except Exception as e:
                            pass
                        buffer = paquetss[-1].encode('utf-8')
            except BlockingIOError: pass
            except Exception: pass

        #Suivi joueur
        camera_x = (LARGEUR//2)-joueur.rect.centerx
        camera_y = (HAUTEUR//2)-joueur.rect.centery

        #Dessin sol
        ecran.fill((0,0,0))
        for y in range(HAUTEURMAP):
            for x in range(LARGEURMAP):
                case = carte[y][x]
                screen_x = x * ZOOM + camera_x
                screen_y= y*ZOOM+camera_y
                #Dessine que ce qui est visible
                if -ZOOM<screen_x<LARGEUR and -ZOOM< screen_y<HAUTEUR:
                    if case == SOL and img_sol is not None:
                        ecran.blit(img_sol, (screen_x,screen_y))
                    elif case == ASCENCEUR and img_ascenseur is not None:
                        ecran.blit(img_ascenseur, (screen_x, screen_y))
        
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
                        img_mur = img_murtop
                        #On regarsde si il y a du sol en dessous
                        if y+1<HAUTEURMAP and (carte[y+1][x]==SOL or carte[y+1][x] == ASCENCEUR):
                            img_mur = img_murface
                        if img_mur:
                            pos_y = screen_y + ZOOM
                            adessiner.append((pos_y, img_mur,(screen_x,screen_y)))
                        
        #Dessin objets
        for obj in objets:
            fenetre_x = obj.rect.x + camera_x
            fenetre_y = obj.rect.y + camera_y
            if -ZOOM<fenetre_x<LARGEUR and -ZOOM<fenetre_y<HAUTEUR:
                pos_y = fenetre_y + obj.rect.height
                adessiner.append((pos_y, obj.texture, (fenetre_x, fenetre_y)))
        #Dessin monstres
        for m in monstres:
            if not m.mort:
                fenetre_x = m.rect.x + camera_x
                fenetre_y = m.rect.y + camera_y
                if -ZOOM<fenetre_x<LARGEUR and -ZOOM<fenetre_y<HAUTEUR:
                    pos_y = fenetre_y + m.rect.height
                    adessiner.append((pos_y, m.texture, (fenetre_x, fenetre_y)))
        
        #Dessin balle
        for tir in joueur.tir:
            ix = tir.rect.x + camera_x
            iy = tir.rect.y + camera_y
            if -ZOOM<ix<LARGEUR and -ZOOM<iy<HAUTEUR:
                angleballe = math.atan2(tir.dy, tir.dx)
                angle = -math.degrees(angleballe)
                balleangle = pygame.transform.rotate(img_ballevol, angle)
                rectballe = balleangle.get_rect(center=(ix,iy))
                adessiner.append((rectballe.bottom, balleangle, rectballe.topleft))

        img_autrejoueur = animationjoueur[joueur.animation]
            
        #Dessin autre joueur
        if connect:
            for idjoueur, autre in joueursup.items():
                if getattr(autre, "etage", 1) == niveau_actuel:
                    #Dessine ses balles
                    if hasattr(autre, "balles_reseau"):
                        for ballex, balley in autre.balles_reseau:
                            ix = ballex+camera_x
                            iy = balley + camera_y
                            if -ZOOM<ix<LARGEUR and -ZOOM<iy<HAUTEUR:
                                #On crée la balle
                                img_balle = pygame.Surface((10,10), pygame.SRCALPHA)
                                pygame.draw.circle(img_balle,(255,200,0),(5,5),5)
                                adessiner.append((iy+10, img_balle, (ix,iy)))
                    #Dessine son perso
                    xjoueur2 = autre.rect.centerx + camera_x
                    yjoueur2 = autre.rect.centery + camera_y
                    #On dessine que si il est visible
                    if -100<xjoueur2<LARGEUR and -100<yjoueur2<HAUTEUR:
                        img_autrejoueur = animationjoueur[autre.animation]
                        img_autrejoueur = pygame.transform.rotate(img_autrejoueur, autre.angle)
                        rect_aff = img_autrejoueur.get_rect(center=(xjoueur2, yjoueur2))
                        adessiner.append((rect_aff.bottom, img_autrejoueur, rect_aff.topleft))

        #Dessin joueur
        img_joueur = animationjoueur[joueur.animation]
        if img_joueur is not None:
            joueurtourne = pygame.transform.rotate(img_joueur, joueur.angle)
            rectaffiche = joueurtourne.get_rect()
            xjoueur = joueur.rect.centerx + camera_x
            yjoueur = joueur.rect.centery + camera_y
            rectaffiche.center = (xjoueur, yjoueur)
            pos_y= rectaffiche.bottom
            adessiner.append((pos_y, joueurtourne, rectaffiche.topleft))

        #Tri la liste a dessiner par ordre Y
        adessiner.sort(key=lambda x: x[0])
        for i in adessiner:
            ecran.blit(i[1], i[2]) #image, position

        #Effet Lumiere quand activé
        lumieremarche.appliquer(ecran, joueur, filtre.m_combat)

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
                    menu.ecran_charge(ecran, img_load, etage_choisi)
                    niveau_actuel = etage_choisi
                    #Si l'étage a déjà été visité, on charge la sauvegarde
                    if etage_choisi in sauvegarde_etage:
                        carte = sauvegarde_etage[etage_choisi]["carte"]
                        salles = sauvegarde_etage[etage_choisi]["salles"]
                        objets = sauvegarde_etage[etage_choisi]["objets"]
                    else:
                        random.seed(partie+etage_choisi)
                        carte, salles, pos = generemap()
                        objets = generer_objets(carte, salles)
                    #Repositionne le joueur sur la nouvelle carte a l"ascenseur
                    start = salles[0]
                    joueurx = start.centerx * ZOOM + (ZOOM//2)
                    joueury = start.centery * ZOOM + (ZOOM//2)
                    joueur.rect.center = (joueurx, joueury)
                    ouvertemenu = False
                    pygame.event.clear()

        #Menu pause
        if enpause:
            boutons = menupause.dessiner(ecran)
            if click:
                mouse_pos = pygame.mouse.get_pos()
                action = menupause.clique(mouse_pos, boutons)
                if action == "REPRENDRE":
                    enpause = False
                elif action == "SAUVEGARDER":
                    sauvegarde_etage[niveau_actuel] = {
                        "carte": carte,
                        "salles": salles,
                        "objets": objets,
                    }
                    print("Partie sauvegardée")
                elif action == "OPTIONS":
                    ecran = option.option_menu(ecran, LARGEUR, HAUTEUR)
                    LARGEUR, HAUTEUR = ecran.get_size()
                    #Met a jour les res de tout le jeu
                    menupause.update_dimensions(LARGEUR, HAUTEUR)
                    menu.update_dimensions(LARGEUR, HAUTEUR)
                    img_load = texture("Chargement.png", (LARGEUR, HAUTEUR))
                elif action == "MENU PRINCIPAL":
                    return #Revenir au menu principal
                elif action == "QUITTER":
                    pygame.quit()
                    sys.exit()

        #Overlay
        if not enpause:
            #Barre endurance
            #Il court ?
            touche = pygame.key.get_pressed()
            mouvement = touche[pygame.K_LEFT] or touche[pygame.K_RIGHT] or touche[pygame.K_UP] or touche[pygame.K_DOWN] or touche[pygame.K_z] or touche[pygame.K_s] or touche[pygame.K_q] or touche[pygame.K_d]
            course = mouvement and touche[pygame.K_LSHIFT] and joueur.endurance > 0
            #Apparition fondu de la barre
            if not course and joueur.endurance >= joueur.maxcourse:
                fondu = max(0, fondu-5)
            else:
                fondu = min(255, fondu+25)                
            joueurimage = animationjoueur[joueur.animation]
            overlay.endurance(ecran, joueur, course, joueurimage, HAUTEUR, LARGEUR, fondu)
        
            #Compteur munition
            overlay.munition(ecran, joueur, police, img_munition, HAUTEUR)

            #Arme overlay
            #Si changement d'arme on glisse image
            if joueur.arsenal != armeprec:
                armeprec = joueur.arsenal
                glissement = -400
            if glissement < 0:
                glissement += 35
                if glissement > 0:
                    glissement = 0
            overlay.arme_overlay(ecran, joueur, img_arme, HAUTEUR, glissement)
            
            #affichage de l'image de l'inventaire
            overlay.onventaire(ecran, inventaire, hudinventaire, LARGEUR, HAUTEUR)
            #activation du filtre
            filtre.filtre(ecran)

        #texte mode overlay
        overlay.mode_texte(ecran, filtre.m_combat, enpause, police, hudmode, inventaire)
        if not enpause :
            overlay.hud_life(ecran, LARGEUR, HAUTEUR, joueur.hp, joueur.hpmax, police, coeur)
        pygame.display.flip()
        clock.tick(60)
    
    if socket_jeu:
        socket_jeu.close()  