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
from lumiere import Lumiere
from cartegen import generemap, generer_objets
from vaisseau import generer_vaisseau
from joueur import Joueur
from vaisseau import LIT, BOUTIQUE

class Partie:
    def __init__(self, ecran, mode="solo", ip = None, save = None):
        self.ecran = ecran
        self.LARGEUR, self.HAUTEUR = ecran.get_size()
        self.mode = mode
        if mode != "solo":
            self.multi = 5.0
        else:
            self.multi = 3.0
        #UI Son
        monstre.init_texture()
        self.police, self.mode, self.ovinventaire, self.inventaire, self.coeur = overlay.overlay_HUD
        pygame.mixer.music.load(assets.ASSETS['musique_jeu'])
        pygame.mixer.music.play(-1)
        #Serveur
        self.IPSERV = "51.38.115.211"
        self.socket_jeu = None
        self.joueursup = {}
        self.connect = False
        self.buffer = b""

        #Si on va pas en solo on lance le multi
        if mode != "solo":
            self.socket_jeu = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if mode == "hote":
                print("Mode Hote: Envoi carte au serveur {IPSERV}...")
                #Ecran d'attente
                self.ecran.fill((0,0,0))
                font = pygame.font.SysFont("ressource/police.ttf", 36)
                text = font.render("Generation de la carte...", True, (255,255,255))
                ecran.blit(text, (self.LARGEUR//2 - 200, self.HAUTEUR//2))
                pygame.display.flip()
                #Configurer le serveur
                try:
                    #Connexion au serveur
                    self.socket_jeu.connect((IPSERV, 5555))
                    #Dit au serv qu'on est host
                    self.socket_jeu.send(b"HOST")
                    self.connect = True
                    #L'hote genere la carte avec seed pour clien est meme
                    self.partie = random.randint(0, 999999)
                    random.seed(partie)
                    self.carte, self.salles, self.pos = generemap()
                    #Envoie la carte et seed au client
                    data = pickle.dumps({"carte": self.carte, "salles": self.salles, "pos": self.pos, "seed": self.partie})
                    tailledata = len(data).to_bytes(4, byteorder='big')
                    self.socket_jeu.sendall(tailledata + data)
                    #Attend confirme du serv
                    self.socket_jeu.recv(1024)
                    #Generation objet avec seed similaire
                    random.seed(self.partie)
                    self.objets = generer_objets(self.carte, self.salles, self.multi)
                    print("Carte enregistré avec succes")
                except Exception as e:
                    print(f"Erreur de reseau hote: {e}")
            elif mode == "client":
                if ip:
                    cible = ip
                else:
                    cible = self.IPSERV
                print(f"Mode Client: connexion au serveur {cible}...")
                try:
                    #Connexion au serv
                    self.socket_jeu.connect((cible, 5555))
                    #On dit au serv qu'on esy Client
                    self.socket_jeu.send(b"CLIENT")
                    self.connect = True
                    print("Chargement de la carte..")
                    #Reçoit la carte de l'hote
                    taillerecu = self.socket_jeu.recv(4)
                    tailledata = int.from_bytes(taillerecu, byteorder='big')
                    #Telechargement de la carte
                    paquets = []
                    recu = 0
                    while recu < tailledata:
                        paquet = self.socket_jeu.recv(min(4096, tailledata - recu))
                        if not paquet:
                            raise Exception("Connexion perdue")
                        paquets.append(paquet)
                        recu += len(paquet)
                    #Decodage de la carte reçue
                    data = b''.join(paquets)
                    donneesmap = pickle.loads(data)
                    self.carte = donneesmap["carte"]
                    self.salles = donneesmap["salles"]
                    self.pos = donneesmap["pos"]
                    #Application de la seed pour avoir meme objet
                    self.partie = donneesmap["seed"]
                    random.seed(partie)
                    self.objets = generer_objets(self.carte, self.salles, self.multi)
                except Exception as e:
                    print(f"Erreur de chargement de la carte: {e}")
            if self.socket_jeu:
            #Empeche le jeu de buger quand on attend un mess reseau
                self.socket_jeu.setblocking(False)
        else:
            #Partie solo
            if save:
                self.partie = save["seed"]
            else:
                self.partie = random.randint(0, 999999)
            if save:
                chargeetage = save["niveau_actuel"]
            else:
                chargeetage = 0
            if chargeetage == 0:
                self.carte, self.salles, self.pos = generer_vaisseau()
                self.objets = generer_objets(self.carte, [], 0)
            else:
                random.seed(self.partie+chargeetage)
                self.carte, self.salles, self.pos = generemap()
                self.objets = generer_objets(self.carte, self.salles, self.multi)

        #Assets et menu
        self.animationjoueur = assets.ASSETS['animationjoueur']
        self.lumieremarche = Lumiere(self.LARGEUR, self.HAUTEUR)
        self.ascenceur = ascenseur.Ascenseur(self.LARGEUR, self.HAUTEUR)
        self.pause = pause.EcranPause(self.LARGEUR, self.HAUTEUR)
        self.sommeil = nuit.Sommeil(self.LARGEUR, self.HAUTEUR)
        self.boutique = boutique.Boutique(self.LARGEUR, self.HAUTEUR)
        #Parametre Boutique
        self.surboutique = False
        self.boutiqueouverte = False
        self.piecessol = []
        #Parametre temps
        self.jour = 1
        self.heure = 0
        self.enpause = False
        #Parametre ascenceur
        self.ouvertmenu = False
        self.surascenceur = False
        self.sauvegarde_etage = {}
        self.niveau_actuel = 0
        self.modifs_etage = {}
        self.sauvegarde_etage[0] = {"carte": self.carte, "salles": self.salles, "objets": self.objets, "pos": self.pos}
        #Joueur
        px, py = int(self.pos[0]), int(self.pos[1])
        self.joueur = Joueur(px*ZOOM+(ZOOM//2), py*ZOOM+(ZOOM//2))

        #Restauration depuis une sauvegarde
        if save:
            modifs_etage = {int(k): v for k, v in save["modifs"].items()}
            self.joueur.rect.centerx = save["joueur"]["x"]
            self.joueur.rect.centery = save["joueur"]["y"]
            self.joueur.hp = save["joueur"]["hp"]
            self.joueur.munition = save["joueur"]["munition"]
            self.joueur.arsenal = save["joueur"]["arsenal"]
            self.joueur.endurance = save["joueur"]["endurance"]
            self.objets = sauvegarde.appliquer_modifs(self.objets, self.modifs_etage.get(0, {}))
            self.sauvegarde_etage[0]["objets"] = self.objets
            if save["niveau_actuel"] != 0:
                self.niveau_actuel = save["niveau_actuel"]
                random.seed(self.partie + self.niveau_actuel)
                self.carte, self.salles, self.pos = generemap()
                self.objets = generer_objets(self.carte, self.salles, self.multi)
                self.objets = sauvegarde.appliquer_modifs(self.objets, self.modifs_etage.get(self.niveau_actuel, {}))

        self.montres = []
        self.font = pygame.font.Font("ressource/police.ttf",24)
        self.fondu = 255
        self.armeprec = self.joueur.arsenal
        self.glissement = 0
        self.actionmap = {}
        self.mort = False
        self.sonnum = assets.ASSETS['son_munition']
        self.sonnum.set_volume(0.8)
        pygame.time.delay(500)
    
    def evenement(self):
        