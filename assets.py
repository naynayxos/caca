import pygame
from prerequis import texture, ZOOM

def charger_assets(largeur, hauteur):
    assets = {}
    #Charger les textures
    assets['img_sol'] = texture("sol.png",(ZOOM+1,ZOOM+1))
    assets['img_ascenseur'] = texture("ascenseur.png",(ZOOM+1,ZOOM+1))
    assets['img_murface'] = texture("murface.png", (ZOOM+1, ZOOM+1))
    assets['img_murtop'] = texture("murtop.png", (ZOOM+1, ZOOM+1))
    assets['img_load'] = texture("Chargement.png", (largeur, hauteur))
    assets['img_munition'] = texture("munitionoverlay.png", (80,80), transparente=True)
    assets['img_ballevol'] = texture("balle.png", (45,45), transparente=True)
    assets['img_lit'] = texture("lit.png", (ZOOM+1, ZOOM+1))
    assets['img_boutique'] = texture("boutique.png", (ZOOM+1, ZOOM+1))
    assets['img_piece'] = texture("piece.png", (40,40), transparente=True)
    assets['img_arme'] = {
        1: texture("pistolet.png",(250,80), transparente= True),
        2: texture("pompe.png",(250,80), transparente= True),
        3: texture("fusil.png",(250,80), transparente= True)
    }
    assets['animationjoueur'] = [
    texture("joueur.png",(100,100), transparente=True),
    texture("joueurgauche.png",(100,100), transparente=True),
    texture("joueurdroit.png",(100,100), transparente=True)
    ]

    #Charger les sons
    assets['son_munition'] = pygame.mixer.Sound("ressource/ESM_Handful_of_Bullet_Shell_Drop_2_Gun_Military_Pistol_Shot_Machine_Rifle_Metal.wav")
    assets['son_munition'].set_volume(0.8)
    assets['son_pistolet'] = pygame.mixer.Sound("ressource/GunshotRevolver_BW.57313.wav")
    assets['son_pompe'] = pygame.mixer.Sound("ressource/STCR2_PHONK_Kit_One_Shot_TurboCharger_Gunshot (1) (mp3cut.net).mp3")
    assets['son_assaut'] = pygame.mixer.Sound("ressource/GunshotRifle_BW.57890.wav")
    assets['son_pistolet'].set_volume(0.6)
    assets['son_pompe'].set_volume(0.6)
    assets['son_assaut'].set_volume(0.6)
    
    #Charger les musiques
    assets['musique_menu'] = "ressource/Musique.mp3"
    assets['musique_jeu'] = "ressource/explo.mp3"
    assets['musique_combat'] = "ressource/horrorfight.mp3"
    
    img_etoile = pygame.Surface((ZOOM+1,ZOOM+1))
    img_etoile.fill((5,5,20))
    pygame.draw.circle(img_etoile, (255,255,255), (ZOOM//2,ZOOM//2), 2)
    img_flamme = pygame.Surface((ZOOM+1,ZOOM+1))
    img_flamme.fill((255,69,0))
    assets['img_etoile'] = img_etoile
    assets['img_flamme'] = img_flamme

    return assets
ASSETS = None