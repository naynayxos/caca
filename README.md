# JEU DRED
Jeu de survie avec une vue du dessus developpé en Python avec Pygame 60FPS. Vous explorerez des donjons générés aléatoirement, il faut survivre dans l'obscurité ; tirez sur les monstres seul ou à plusieurs dans le mode multijoueur.

# Presentation
DRED est un jeu d'exploration dans lequel vous incarnez un personnage armé qui doit explorer des salles réparties sur 6 etages. Chacun des étages est différent des autres, ses etages sont rempli de meubles, de munitions à récupérer et d'une ambiance à suspense. La lumière permet d'être plongée dans le jeu. 

Dans DRED, vous pouvez jouer en solo, en tant qu'hebergeur ou en tant que joueur d'une partie en ligne. 

# Prerequis
Pour pouvoir lancer ce jeu vous avez besoins :
- De Python 
- De Pygame
- Telecharger le jeu

```bash
pip install pygame
```

```bash
git clone https://github.com/floriansfo/SAE.git
```

```bash
python demarrage.py
```

Voila le jeu sera fonctionnel

# Commande
|  Touche  |  Action  | 
|----------|----------|
| `Z ou ↑` |  Avancer |
| `S ou ↓` |  Reculer |
| `Q ou ←` |  Gauche  |
| `D ou →` |  Droite  |
| `Shift`  | Sprinter |
| `1/2/3`  | Choix arme |
| `Clic gauche` | Tirer |
| `H` | Allumer/Eteindre lampe |
| `T` | Activer/Desactiver mode combat |
| `E` | Utiliser l'ascenseur |
| `Ctrl gauche` | Ouvrir/Fermer inventaire |
| `Echap` | Pause |

# Gameplay
## Arme
Trois armes sont possible dans le jeu avec les touches 1, 2 et 3:

|  Arme  |  Principe  |
|--------|------------|
| `1: Pistolet` | Tir précis, balle par balle |
| `2: Fusil à pompe` | 5 balles d'affiler, cadence lente |
| `3: Fusil d'assaut` | Tir rapide, recule |

## Munition
Il est possible de gagner en munition en marchant dessus ou en cassant des caisses, cela rajoutera 15 balle à l'inventaire.

## Vie
Le joueur commence a 100HP et pourra perdre de la vie lors d'une attaque avec des monstres.

## Endurance
Le joueur possede un sprint limité, visible grâce a la barre d'endurance, elle se recharge quand le joueur ne bouge pas.

## Eclairage
Le joueur possede une lampe qu'il peut allumer avec la touche H, pour voir les monstres, il peut activer le mode combat pour les voirs.

## Ascenceur
Le jeu a un ascenceur pour naviguer entre les etages, il peut y acceder en appuyant sur la touche E lorsqu'il est dessus.

## Multijoueur
2 mode multijoueur:
**Mode Hote:** Se connecte, il genere la carte et l'envoie au client quand il se connecte.
**Mode client:** Se connecte, en saisissant l'IP le serveur envoie la carte au joueur.

## Options
Notre jeu, permet de régler la résolution ainsi que le volume de la musique mais aussi d'acceder au touche permettant de commander le jeu.