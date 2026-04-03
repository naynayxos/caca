import pygame

TEXTE       = (255, 255, 255)
GRIS        = (160, 160, 160)
VERT        = (80,  200,  80)
ROUGE       = (200,  60,  60)
OR          = (255, 200,  50)
INTERFACE   = (20,  22,  38, 230)
BORDURE     = (90,  90, 130)
BORDURE_OR  = (180, 150,  50)
HOVER       = (55,  75, 115)
NOIR_TRANSP = (0,   0,   0, 160)

ARTICLES = [
    {"id": 2,      "nom": "Fusil a pompe",  "prix": 150, "desc": "5 balles, lent mais puissant", "type": "arme"},
    {"id": 3,      "nom": "Fusil d'assaut", "prix": 250, "desc": "Rapide, recul aleatoire",       "type": "arme"},
    {"id": "pile", "nom": "Pile lampe",     "prix": 50,  "desc": "Recharge la pile a 100%",       "type": "pile"},
    {"id": "lampe","nom": "Lampe torche",   "prix": 100, "desc": "Indispensable dans le noir",    "type": "lampe"},
]

PRIX_NIVEAUX = {2: 100, 3: 200, 4: 350, 5: 500, 6: 750}

class Boutique:
    def __init__(self, largeur, hauteur):
        self.L = largeur
        self.H = hauteur
        self.font_titre  = pygame.font.Font("ressource/titre.ttf",  28)
        self.font_normal = pygame.font.Font("ressource/police.ttf", 18)
        self.font_petit  = pygame.font.Font("ressource/police.ttf", 14)

    def update(self, L, H):
        self.L = L
        self.H = H

    def dessiner(self, ecran, joueur, nb_joueurs=1):
        limite   = 2 if nb_joueurs <= 2 else 3
        restants = max(0, limite - joueur.achatjour)

        # Dimensions adaptees a l'ecran
        menuL = min(620, self.L - 60)
        menuH = min(580, self.H - 60)
        x = (self.L - menuL) // 2
        y = (self.H - menuH) // 2

        PAD  = 18   # marge interieure horizontale
        LINH = 72   # hauteur d'une ligne article

        # Fond principal
        fond = pygame.Surface((menuL, menuH), pygame.SRCALPHA)
        fond.fill(INTERFACE)
        ecran.blit(fond, (x, y))
        pygame.draw.rect(ecran, BORDURE, pygame.Rect(x, y, menuL, menuH), 2, border_radius=10)

        # Titre
        titre = self.font_titre.render("BOUTIQUE DU VAISSEAU", True, OR)
        ecran.blit(titre, titre.get_rect(center=(x + menuL // 2, y + 22)))
        pygame.draw.line(ecran, BORDURE_OR, (x + PAD, y + 42), (x + menuL - PAD, y + 42), 1)

        # Solde + achats restants sur la meme ligne
        solde_txt = self.font_normal.render(f"Pieces : {joueur.pieces}", True, OR)
        ecran.blit(solde_txt, (x + PAD, y + 50))
        coul_restant = VERT if restants > 0 else ROUGE
        achat_txt = self.font_petit.render(f"Achats restants : {restants}/{limite}", True, coul_restant)
        ecran.blit(achat_txt, achat_txt.get_rect(topright=(x + menuL - PAD, y + 53)))

        # Section articles
        cursor_y = y + 72
        lbl_art = self.font_petit.render("EQUIPEMENT", True, GRIS)
        ecran.blit(lbl_art, (x + PAD, cursor_y))
        cursor_y += 18

        boutons  = []
        mouse    = pygame.mouse.get_pos()
        inner_w  = menuL - PAD * 2

        for article in ARTICLES:
            ay       = cursor_y
            rect_art = pygame.Rect(x + PAD, ay, inner_w, LINH)
            type_art = article["type"]

            deja = (
                joueur.arsenal_achete.get(article["id"], False) if type_art == "arme"
                else joueur.possedelampe                          if type_art == "lampe"
                else False
            )
            peut  = joueur.pieces >= article["prix"] and restants > 0 and not deja
            hover = rect_art.collidepoint(mouse) and peut

            fond_art = pygame.Surface((rect_art.w, rect_art.h), pygame.SRCALPHA)
            if deja and type_art != "pile":
                fond_art.fill((15, 55, 15, 180))
            elif hover:
                fond_art.fill((*HOVER, 210))
            else:
                fond_art.fill(NOIR_TRANSP)
            ecran.blit(fond_art, rect_art.topleft)
            pygame.draw.rect(ecran, BORDURE, rect_art, 1, border_radius=6)

            nom_surf = self.font_normal.render(article["nom"], True, TEXTE)
            ecran.blit(nom_surf, (rect_art.x + 12, rect_art.y + 10))
            desc_surf = self.font_petit.render(article["desc"], True, GRIS)
            ecran.blit(desc_surf, (rect_art.x + 12, rect_art.y + 34))

            if deja and type_art != "pile":
                etat = self.font_normal.render("DEJA ACHETE", True, VERT)
                ecran.blit(etat, etat.get_rect(midright=(rect_art.right - 12, rect_art.centery)))
            else:
                coul_prix = VERT if peut else ROUGE
                prix_surf = self.font_normal.render(f"{article['prix']} pcs", True, coul_prix)
                ecran.blit(prix_surf, prix_surf.get_rect(midright=(rect_art.right - 12, rect_art.centery)))
                boutons.append((rect_art, article))

            cursor_y += LINH + 6

        # Section niveaux
        cursor_y += 4
        pygame.draw.line(ecran, BORDURE, (x + PAD, cursor_y), (x + menuL - PAD, cursor_y), 1)
        cursor_y += 8
        lbl_niv = self.font_petit.render("DEBLOQUER DES NIVEAUX", True, GRIS)
        ecran.blit(lbl_niv, (x + PAD, cursor_y))
        cursor_y += 20

        nb_niv = len(PRIX_NIVEAUX)
        btn_w  = (inner_w - (nb_niv - 1) * 8) // nb_niv
        btn_h  = 36

        for idx, (niveau, prix) in enumerate(PRIX_NIVEAUX.items()):
            bx       = x + PAD + idx * (btn_w + 8)
            btn_rect = pygame.Rect(bx, cursor_y, btn_w, btn_h)
            debloque  = niveau in joueur.niveaudebloque
            peut_niv  = joueur.pieces >= prix and restants > 0 and not debloque
            hover_niv = btn_rect.collidepoint(mouse) and peut_niv

            if debloque:
                coul_fond = (15, 60, 15, 200)
                coul_bord = VERT
                coul_txt  = VERT
                label     = f"-{niveau}  OK"
            elif peut_niv:
                coul_fond = (*HOVER, 210) if hover_niv else NOIR_TRANSP
                coul_bord = BORDURE_OR
                coul_txt  = OR
                label     = f"-{niveau}  {prix}p"
            else:
                coul_fond = (25, 25, 25, 160)
                coul_bord = (60, 60, 70)
                coul_txt  = (70, 70, 70)
                label     = f"-{niveau}  {prix}p"

            fond_btn = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
            fond_btn.fill(coul_fond)
            ecran.blit(fond_btn, btn_rect.topleft)
            pygame.draw.rect(ecran, coul_bord, btn_rect, 1, border_radius=5)
            txt = self.font_petit.render(label, True, coul_txt)
            ecran.blit(txt, txt.get_rect(center=btn_rect.center))

            if not debloque:
                boutons.append((btn_rect, {
                    "id": f"niveau_{niveau}", "prix": prix,
                    "type": "niveau", "niveau": niveau
                }))

        # Aide en bas
        aide = self.font_petit.render("Clic gauche pour acheter  —  E pour fermer", True, (80, 80, 100))
        ecran.blit(aide, aide.get_rect(center=(x + menuL // 2, y + menuH - 12)))

        return boutons

    def clique(self, mouse_pos, boutons, joueur, nb_joueurs=1):
        limite = 2 if nb_joueurs <= 2 else 3
        if joueur.achatjour >= limite:
            return False
        for rect, article in boutons:
            if not rect.collidepoint(mouse_pos):
                continue
            if joueur.pieces < article["prix"]:
                return False
            type_art = article["type"]
            if type_art == "arme":
                if joueur.arsenal_achete.get(article["id"], False):
                    return False
                joueur.pieces -= article["prix"]
                joueur.arsenal_achete[article["id"]] = True
                joueur.achatjour += 1
                return True
            elif type_art == "pile":
                joueur.pieces -= article["prix"]
                joueur.pile = joueur.pilemax
                joueur.achatjour += 1
                return True
            elif type_art == "lampe":
                if joueur.possedelampe:
                    return False
                joueur.pieces -= article["prix"]
                joueur.possedelampe = True
                joueur.pile = joueur.pilemax
                joueur.achatjour += 1
                return True
            elif type_art == "niveau":
                niv = article["niveau"]
                if niv in joueur.niveaudebloque:
                    return False
                joueur.pieces -= article["prix"]
                joueur.niveaudebloque.add(niv)
                joueur.achatjour += 1
                return True
        return False