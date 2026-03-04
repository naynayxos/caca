import pygame
import sys
import option
import ascenseur
import pause
import socket
import pickle
import filtre
import overlay

from prerequis import *
from prerequis import texture, lumiere
from cartegen import generemap, generer_objets
from joueur import Joueur
from arme import Arme

pygame.init()
ecran = pygame.display.Info()
pygame.display.set_caption("D-RED")

def lancer(ecran, mode = "solo", ip=None):
    LARGEUR, HAUTEUR = ecran.get_size()
    police, hudmode =overlay.overlay_HUD()
    clock = pygame.time.Clock()
    pygame.mixer.music.load("ressource/explo.mp3")
    pygame.mixer.music.play(-1)

    #Reseaux
    socket_jeu = None
    joueursup = {} #Dico qui stock id et tout le reste
    connect = False
    buffer = b""
    if mode != "solo":
        socket_jeu = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if mode == "hote":
            print("Mode Hote: en attente de joueur...")
            #Ecran d'attente
            ecran.fill((0,0,0))
            font = pygame.font.SysFont("ressource/police.ttf", 36)
            text = font.render("En attente de joueur...", True, (255,255,255))
            ecran.blit(text, (LARGEUR//2 - 150, HAUTEUR//2))
            pygame.display.flip()
            #Configurer le serveur
            try:
                socket_jeu.bind(('0.0.0.0', 5555))
                socket_jeu.listen(10)
                conn, addr = socket_jeu.accept()
                socket_jeu = conn
                connect = True
                idjoueur = str(addr)
                print(f"Joueur connecté depuis {addr}")

                #L'hote genere la carte
                carte, salles, pos = generemap()
                #Envoie la carte au client
                data = pickle.dumps({"carte": carte, "salles": salles, "pos": pos})
                tailledata = len(data).to_bytes(4, byteorder='big')
                socket_jeu.sendall(tailledata + data)
                objets = generer_objets(carte, salles)
            except Exception as e:
                print(f"Erreur de reseau hote: {e}")
                return
        elif mode == "client":
            print(f"Mode Client: connexion au serveur {ip}...")
            try:
                socket_jeu.connect((ip, 5555))
                connect = True
                idjoueur = "SERVEUR"
                print("Connecté au serveur")
                #Reçoit la carte de l'hote
                taillerecu = socket_jeu.recv(4)
                tailledata = int.from_bytes(taillerecu, byteorder='big')
                #Reçoit les données de la carte
                paquets = []
                recu = 0
                while recu < tailledata:
                    paquet = socket_jeu.recv(min(4096, tailledata - recu))
                    if not paquet:
                        raise Exception("Connexion perdue")
                    paquets.append(paquet)
                    recu += len(paquet)
                data = b''.join(paquets)
                donneesmap = pickle.loads(data)
                carte = donneesmap["carte"]
                salles = donneesmap["salles"]
                pos = donneesmap["pos"]
                objets = generer_objets(carte, salles)
            except Exception as e:
                print(f"Erreur de reseau client: {e}")
                return
        socket_jeu.setblocking(False)
    else:
        #Partie solo
        carte, salles, pos = generemap()
        objets = generer_objets(carte, salles)

    #Chargement assets
    img_sol = texture("sol.png",(ZOOM+1,ZOOM+1))
    img_ascenseur = texture("ascenseur.png",(ZOOM+1,ZOOM+1))
    img_murface = texture("murface.png", (ZOOM+1, ZOOM+1))
    img_murtop = texture("murtop.png", (ZOOM+1, ZOOM+1))
    img_load = texture("Chargement.png", (LARGEUR, HAUTEUR))
    animationjoueur = [
    texture("joueur.png",(100,100), transparente=True),
    texture("joueurgauche.png",(100,100), transparente=True),
    texture("joueurdroit.png",(100,100), transparente=True)
    ]
    lumierefin = lumiere(450)

    #Ascenseur
    menu = ascenseur.Ascenseur(LARGEUR, HAUTEUR)

    #Menu pause
    menupause = pause.EcranPause(LARGEUR, HAUTEUR)
    enpause = False
    ouvertemenu = False
    surascenceur = False #Pour savoir si on peut interagir avec l'ascenseur

    #Dictionnaire pour sauvegarder les etages déjà visités
    sauvegarde_etage =  {}
    niveau_actuel = 1

    #Joueur
    px, py = int(salles[0].centerx), int(salles[0].centery)
    joueur = Joueur(px*ZOOM+(ZOOM//2), py*ZOOM+(ZOOM//2))

    font = pygame.font.Font("ressource/police.ttf", 24)
    running = True
    while running:
        LARGEUR, HAUTEUR = ecran.get_size()
        #Vérifie si le joueur est sur un ascenseur
        casex = int(joueur.rect.centerx/ZOOM)
        casey = int(joueur.rect.centery/ZOOM)
        surascenceur = False
        if 0 <= casex < LARGEURMAP and 0 <= casey < HAUTEURMAP:
            if carte[casey][casex] == ASCENCEUR:
                surascenceur = True

        #Si on s'eloigne de l'ascenseur alors on ferme le menu
        if not surascenceur:
            ouvertemenu = False

        click = False
        for event in pygame.event.get():
            filtre.activation_mc(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    joueur.lumiereallumee = not joueur.lumiereallumee
                if event.key == pygame.K_ESCAPE:
                    if ouvertemenu:
                        ouvertemenu = False
                    else:
                        enpause = not enpause
                if event.key == pygame.K_e and surascenceur:
                    ouvertemenu = not ouvertemenu
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: #Clic gauche
                    click = True
       
        if not ouvertemenu and not enpause:
            keys = pygame.key.get_pressed()
            #Reanimation
            if keys[pygame.K_e]:
                joueur.rea = 1
            else:
                joueur.rea = 0
            #Deplacement joueur
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
                else:
                    objetsreste.append(obj)
            objets = objetsreste
            #Tir
            if keys[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]:
                joueur.tirer()
            #Deplacement balle
            joueur.updatetir(carte, objets)

        #Reseaux
        if connect:
            try:
                #Envoie la position du joueur
                message = f"{joueur.rect.centerx},{joueur.rect.centery},{niveau_actuel},{joueur.angle},{joueur.animation}\n"
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
                        dernier = paquetss[-2]
                    try:
                        valeur = dernier.split(",")
                        if len(valeur) == 5:
                            if idjoueur not in joueursup:
                                joueursup[idjoueur] = Joueur(int(valeur[0]), int(valeur[1]))
                            autre = joueursup[idjoueur]
                            autre.rect.centerx = int(valeur[0])
                            autre.rect.centery = int(valeur[1])
                            autre.etage = int(valeur[2])
                            autre.angle = float(valeur[3])
                            autre.animation = int(valeur[4])
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

        #Dessin balles
        for tir in joueur.tir:
            ix = tir.rect.x + camera_x
            iy = tir.rect.y + camera_y
            if -ZOOM<ix<LARGEUR and -ZOOM<iy<HAUTEUR:
                adessiner.append((iy+tir.rect.height, tir.image, (ix, iy)))

        img_autrejoueur = animationjoueur[joueur.animation]
            
        #Dessin autre joueur
        if connect:
            for idjoueur, autre in joueursup.items():
                if getattr(autre, "etage", 1) == niveau_actuel:
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
        if joueur.lumiereallumee:
            #Maque sombre autoru
            masque = pygame.Surface((LARGEUR,HAUTEUR))
            masque.fill(NUIT)
            #Tourne lumiere
            lumieretourne = pygame.transform.rotate(lumierefin,joueur.angleactuel)
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
                    menu.ecran_charge(ecran, img_load, etage_choisi)
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
                    menupause.update_dimensions(LARGEUR, HAUTEUR)
                    menu.update_dimensions(LARGEUR, HAUTEUR)
                    img_load = texture("Chargement.png", (LARGEUR, HAUTEUR))
                elif action == "MENU PRINCIPAL":
                    return
                elif action == "QUITTER":
                    pygame.quit()
                    sys.exit()

        #Barre endurance
        pygame.draw.rect(ecran, (50,50,50), (20, HAUTEUR-40, 200, 20))
        largeurbarre = (joueur.endurance/joueur.maxcourse)*200
        if largeurbarre>0:
            if joueur.endurance > 20:
                couleur = (0,200,0)
            else:
                couleur = (200,0,0)
            pygame.draw.rect(ecran, couleur, (20, HAUTEUR-40, largeurbarre,20))
        
        #Compteur munition
        if joueur.munition > 0:
            textemun = font.render(f"Balles: {joueur.munition}", True, (255,255,255))
        else:
            textemun = font.render(f"Chargeur Vide !", True, (255,50,50))
        ecran.blit(textemun,(20,HAUTEUR-80))

        #Arme actuelle
        noms = {1: "Pistolet", 2:"Fusil A Pompe", 3:"Fusil d'Assaut"}
        textearme = font.render(f"Arme: {noms[joueur.arsenal]}", True, (200,200,255))
        ecran.blit(textearme, (20, HAUTEUR-120))
        #texte mode overlay
        overlay.mode_texte(ecran, filtre.m_combat, police, hudmode)
        
        filtre.filtre(ecran)
        pygame.display.flip()
        clock.tick(60)
    
    if socket_jeu:
        socket_jeu.close()  