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
import sauvegarde
import nuit
import boutique
import assets
import reseau
import affichage

from prerequis import *
from prerequis import texture
from lumiere import Lumiere
from cartegen import generemap, generer_objets
from vaisseau import generer_vaisseau
from joueur import Joueur
from arme import Arme
from vaisseau import LIT, BOUTIQUE

pygame.init()
ecran = pygame.display.Info()
pygame.display.set_caption("D-RED")

def lancer(ecran, mode = "solo", ip=None, save=None):
    monstre.init_texture()
    LARGEUR, HAUTEUR = ecran.get_size()
    clock = pygame.time.Clock()
    if mode != "solo":
        multi = 5.0
    else:
        multi = 3.0
    #Asset musque ..
    police, hudmode, hudinventaire, inventaire, coeur =overlay.overlay_HUD()
    pygame.mixer.music.load(assets.ASSETS['musique_jeu'])
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
                objets = generer_objets(carte, salles,multi)
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
                objets = generer_objets(carte, salles,multi)
            except Exception as e:
                print(f"Erreur de chargement de la carte: {e}")
                return
        #Empeche le jeu de buger quand on attend un mess reseau
        socket_jeu.setblocking(False)
    else:
        #Partie solo
        if save:
            partie = save["seed"]
        else:
            partie = random.randint(0, 999999)
        chargeetage = 0
        if save:
            chargeetage = save["niveau_actuel"]
        if chargeetage == 0:
            carte, salles, pos = generer_vaisseau()
            objets = generer_objets(carte, [], 0)
        else:
            random.seed(partie+chargeetage)
            carte, salles, pos = generemap()
            objets = generer_objets(carte, salles,multi)

    #Charger les textures
    img_sol = assets.ASSETS['img_sol']
    img_ascenseur = assets.ASSETS['img_ascenseur']
    img_murface = assets.ASSETS['img_murface']
    img_murtop = assets.ASSETS['img_murtop']
    img_load = assets.ASSETS['img_load']
    img_munition = assets.ASSETS['img_munition']
    img_ballevol = assets.ASSETS['img_ballevol']
    img_lit = assets.ASSETS['img_lit']
    img_boutique = assets.ASSETS['img_boutique']
    img_piece = assets.ASSETS['img_piece']
    img_arme = assets.ASSETS['img_arme']
    animationjoueur = assets.ASSETS['animationjoueur']
    img_etoile = assets.ASSETS['img_etoile']
    img_flamme = assets.ASSETS['img_flamme']
    #Calque de lumiere
    lumieremarche = Lumiere(LARGEUR, HAUTEUR)

    #Menu Ascenseur
    menu = ascenseur.Ascenseur(LARGEUR, HAUTEUR)
    #Menu pause
    menupause = pause.EcranPause(LARGEUR, HAUTEUR)
    #Menu sommeil
    menusommeil = nuit.Sommeil(LARGEUR, HAUTEUR)
    menuboutique = boutique.Boutique(LARGEUR, HAUTEUR)
    surboutique = False
    boutiqueouverte = False
    piecessol = []
    jour = 1
    heure = 0

    enpause = False
    ouvertemenu = False
    surascenceur = False #Pour savoir si on peut interagir avec l'ascenseur


    #Dictionnaire pour sauvegarder les etages déjà visités
    sauvegarde_etage = {}
    niveau_actuel = 0
    modifs_etage = {}
    #Sauvegarde niveau 1 pour pas le perdre
    sauvegarde_etage[0] = {"carte":carte,"salles":salles,"objets":objets,"pos": pos}

    #Joueur
    px, py = int(pos[0]), int(pos[1])
    joueur = Joueur(px*ZOOM+(ZOOM//2), py*ZOOM+(ZOOM//2))

    #Restauration depuis une sauvegarde
    if save:
        modifs_etage = {int(k): v for k, v in save["modifs"].items()}
        joueur.rect.centerx = save["joueur"]["x"]
        joueur.rect.centery = save["joueur"]["y"]
        joueur.hp = save["joueur"]["hp"]
        joueur.munition = save["joueur"]["munition"]
        joueur.arsenal = save["joueur"]["arsenal"]
        joueur.endurance = save["joueur"]["endurance"]
        objets = sauvegarde.appliquer_modifs(objets, modifs_etage.get(0, {}))
        sauvegarde_etage[0]["objets"] = objets
        if save["niveau_actuel"] != 0:
            niveau_actuel = save["niveau_actuel"]
            random.seed(partie + niveau_actuel)
            carte, salles, pos = generemap()
            objets = generer_objets(carte, salles, multi)
            objets = sauvegarde.appliquer_modifs(objets, modifs_etage.get(niveau_actuel, {}))
    #lst de monstres
    monstres=[]

    #Variable interface
    font = pygame.font.Font("ressource/police.ttf", 24)
    fondu = 255
    #Detecte changement donc animation diff
    armeprec = joueur.arsenal
    glissement = 0
    actionmap = {} #Reactualise quand caisse cassé et mun recup
    #Mort du joueur
    mort = False
    #Son munition
    sonmun = assets.ASSETS['son_munition']
    sonmun.set_volume(0.8)
    pygame.time.delay(500)
    #jeu fluide
    t = 1/60.0
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
        #Vérifie si le joueur est sur un lit
        surlit = False
        if 0 <= casex < LARGEURMAP and 0 <= casey < HAUTEURMAP:
            if carte[casey][casex] == LIT:
                surlit = True
        #Vérifie si le joueur est sur la boutique
        surboutique = False
        if 0 <= casex < LARGEURMAP and 0 <= casey < HAUTEURMAP:
            if carte[casey][casex] == BOUTIQUE:
                surboutique = True
        if not surboutique:
            boutiqueouverte = False
        #Si on s'eloigne de l'ascenseur alors on ferme le menu
        if not surascenceur:
            ouvertemenu = False
        #Evenement clavier
        click = False
        for event in pygame.event.get():
            if niveau_actuel != 0:
                filtre.activation_mc(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                #Ouvre inventaire
                if event.key == pygame.K_LCTRL and not enpause:
                    inventaire= not inventaire
                 #Larry spawn
                if event.key == pygame.K_l and niveau_actuel != 0:
                    m= monstre.Monstre(joueur.rect.centerx+100, joueur.rect.centery, 3, 100)
                    monstres.append(m)
                    print(f"Larry va te toucher la nuit")
                #Allume ou eteindre lampe
                if event.key == pygame.K_h:
                    joueur.toogle_lumiere()
                    if joueur.lumiereallumee and filtre.m_combat:
                        filtre.m_combat = False
                #Pause ou ferme
                if event.key == pygame.K_ESCAPE:
                    if ouvertemenu:
                        ouvertemenu = False
                    else:
                        enpause = not enpause
                #Menu ascenceur
                if event.key == pygame.K_e and surascenceur:
                    ouvertemenu = not ouvertemenu
                if event.key == pygame.K_e and surlit and niveau_actuel==0:
                    jour = menusommeil.nuit(ecran, joueur, jour)
                    heure = 0
                    joueur.achatjour = 0
                    joueur.oxygene = joueur.oxygenemax
                if event.key == pygame.K_e and surboutique and niveau_actuel == 0:
                    boutiqueouverte = not boutiqueouverte
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: #Clic gauche
                    click = True
                if boutiqueouverte:
                    achat = menuboutique.clique(pygame.mouse.get_pos(), bouton_boutique, joueur)
        
        #Mode combat desactive quand tire pas
        if niveau_actuel!=0:
            filtre.updatemode()
        
        #Le joueur est mort
        if mort:
            ecran.fill((0,0,0))
            textemort = font.render("GAME OVER", True, (255,0,0))
            ecran.blit(textemort, textemort.get_rect(center=(LARGEUR//2, HAUTEUR//2-100)))
            btn_menu = pygame.Rect(0,0,200,60)
            btn_menu.center = (LARGEUR//2,HAUTEUR//2+50)
            mouse_pos = pygame.mouse.get_pos()
            if btn_menu.collidepoint(mouse_pos):
                couleur = (100,100,100)
            else:
                couleur = (50,50,50)
            pygame.draw.rect(ecran, couleur, btn_menu)
            textebtn = font.render("MENU", True,(255,255,255))
            ecran.blit(textebtn, textebtn.get_rect(center=btn_menu.center))
            if click and btn_menu.collidepoint(mouse_pos):
                return
            pygame.display.flip()
            clock.tick(60)
            continue
       
        if not ouvertemenu and not enpause:
            keys = pygame.key.get_pressed()
            #Deplacement joueur et collision
            kx, ky = joueur.deplacer(keys, len(animationjoueur), t)
            joueur.collision(kx, ky, carte, objets)
            joueur.updatelampe(filtre.m_combat)
            #Changement arme
            if keys[pygame.K_1]:
                joueur.changerarme(1)
            if keys[pygame.K_2] and joueur.arsenal_achete.get(2, False):
                joueur.changerarme(2)
            if keys[pygame.K_3] and joueur.arsenal_achete.get(3, False):
                joueur.changerarme(3)
            #Ramasser munition
            objetsreste = []
            for obj in objets:
                if obj.type == "munition" and joueur.rect.colliderect(obj.rect):
                    joueur.munition = joueur.munition + 15
                    sonmun.play()
                    key = f"{obj.rect.x}-{obj.rect.y}"
                    actionmap[key] = "S"
                    modifs_etage.setdefault(niveau_actuel, {})[key] = "S"
                else:
                    objetsreste.append(obj)
            objets = objetsreste #Met a jour les objets restants
            #Ramasser piece
            piecesreste = []
            for p in piecessol:
                if joueur.rect.colliderect(p["rect"]):
                    joueur.pieces += p["valeur"]
                else:
                    piecesreste.append(p)
            piecessol = piecesreste #Met a jour les pieces restantes
            #Monstre loot piece
            for m in monstres:
                if m.mort and getattr(m, "loot", 0) > 0:
                    piecessol.append({"rect": pygame.Rect(m.rect.centerx-20, m.rect.centery-20, 40, 40), "valeur": m.loot})
                    m.loot = 0 #Evite de looter plusieurs fois
            #Tir
            if (keys[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]) and niveau_actuel != 0:
                joueur.tirer()
            #Deplacement balle et acutalisation caisse cassé
            casse = joueur.updatetir(carte, objets, monstres)
            if casse:
                for c in casse:
                    key = f"{c.rect.x}-{c.rect.y}"
                    actionmap[key] = "M"
                    modifs_etage.setdefault(niveau_actuel, {})[key] = "M"
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
                        if joueur.hp <= 0:
                            mort = True
                            joueur.possedelampe = False
                            joueur.lumiereallumee = False
            #Oxygene
            joueur.updateoxygene(niveau_actuel)
            if joueur.hp <=0 and not mort:
                mort = True        
            #Heure
            if niveau_actuel != 0:
                heure +=1
                if heure >= 28800:
                    if not hasattr(joueur, "time"):
                        jour.time = 0
                    jour.time +=1
                    if joueur.time >= 120:
                        joueur.time = 0
                        joueur.hp = joueur.hp - 5
                        if joueur.hp <= 0:
                            mort = True
                            joueur.possedelampe = False
                            joueur.lumiereallumee = False
        #Reseau
        if connect:
            buffer, objets, joueursup = reseau.connexion(socket_jeu, joueur, monstres, objets, actionmap, mort, niveau_actuel, buffer, joueursup)

        affichage.dessinerjeu(ecran, LARGEUR, HAUTEUR, carte, joueur, objets, piecessol, monstres, joueursup, niveau_actuel, connect, lumieremarche, filtre)
        
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
        #Message pour le lit
        if surlit and not ouvertemenu and niveau_actuel == 0:
            tx = font.render("Appuyer sur E pour dormir", True, (255,255,255))
            tx_rect = tx.get_rect(center=(LARGEUR//2, HAUTEUR-50))
            fond = pygame.Surface((tx_rect.width+20, tx_rect.height+10), pygame.SRCALPHA)
            fond.fill((0,0,0,150))
            ecran.blit(fond,(tx_rect.x-10, tx_rect.y-5))
            ecran.blit(tx, tx_rect)
        #Message pour la boutique
        if surboutique and not boutiqueouverte and niveau_actuel == 0:
            tx = font.render("Appuyer sur E pour entrer", True, (255,255,255))
            tx_rect = tx.get_rect(center=(LARGEUR//2, HAUTEUR-50))
            fond = pygame.Surface((tx_rect.width+20, tx_rect.height+10), pygame.SRCALPHA)
            fond.fill((0,0,0,150))
            ecran.blit(fond,(tx_rect.x-10, tx_rect.y-5))
            ecran.blit(tx, tx_rect)

        #Menu ascenseur
        if ouvertemenu:
            menu_boutons = menu.dessiner(ecran, niveau_actuel, joueur)
            if click:
                mouse_pos = pygame.mouse.get_pos()
                etage_choisi = menu.clique(mouse_pos, menu_boutons)
                if etage_choisi is not None:
                    sauvegarde_etage[niveau_actuel] = {
                        "carte": carte,
                        "salles": salles,
                        "objets": objets,
                        "pos": pos,
                    }
                    menu.ecran_charge(ecran, img_load, etage_choisi)
                    #Si l'étage a déjà été visité, on charge la sauvegarde
                    if etage_choisi in sauvegarde_etage:
                        carte = sauvegarde_etage[etage_choisi]["carte"]
                        salles = sauvegarde_etage[etage_choisi]["salles"]
                        objets = sauvegarde_etage[etage_choisi]["objets"]
                        pos = sauvegarde_etage[etage_choisi]["pos"]
                    else:
                        if etage_choisi == 0:
                            carte, salles, pos = generer_vaisseau()
                            objets = generer_objets(carte, [], 0)
                        elif 1<= etage_choisi <=6:
                            random.seed(partie+etage_choisi)
                            carte, salles, pos = generemap()
                            objets = generer_objets(carte, salles, multi)
                            objets = sauvegarde.appliquer_modifs(objets, modifs_etage.get(etage_choisi, {}))
                    niveau_actuel = etage_choisi
                    #Repositionne le joueur sur la nouvelle carte a l"ascenseur
                    joueurx = pos[0] * ZOOM + (ZOOM//2)
                    joueury = pos[1] * ZOOM + (ZOOM//2)
                    joueur.rect.center = (joueurx, joueury)
                    pygame.time.delay(500)
                    ouvertemenu = False
                    pygame.event.clear()

        #Menu boutique
        bouton_boutique = []
        if boutiqueouverte:
            bouton_boutique = menuboutique.dessiner(ecran, joueur)
            if click:
                menuboutique.clique(pygame.mouse.get_pos(), bouton_boutique, joueur)

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
                    sauvegarde.sauvegarder(partie, niveau_actuel, modifs_etage, joueur)
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
        
        #Musique mode combat
        if filtre.combat:
            if niveau_actuel != 0:
                if filtre.m_combat:
                    #Active nouvelle sic
                    pygame.mixer.music.load(assets.ASSETS['musique_combat'])
                    pygame.mixer.music.play(-1)
                else:
                    #Met ancienne sic
                    pygame.mixer.music.load(assets.ASSETS['musique_jeu'])
                    pygame.mixer.music.play(-1)
            filtre.combat = False

        #Overlay
        if not enpause:
            #Barre endurance
            #Il court ?
            if ouvertemenu == False: #Pas de barre si menu ouvert
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
            overlay.lampe(ecran, joueur, font, HAUTEUR)

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
            overlay.horloge(ecran, font, heure, LARGEUR)
            if niveau_actuel != 0:
                overlay.oxygene(ecran, joueur, font, LARGEUR, HAUTEUR)
            piece_hud = font.render(f"Pieces: {joueur.pieces}", True, (255,200,50))
            ecran.blit(piece_hud, piece_hud.get_rect(topright=(LARGEUR-20, 20)))
        pygame.display.flip()
        t = clock.tick(60) / 1000.0
    
    if socket_jeu:
        socket_jeu.close()  