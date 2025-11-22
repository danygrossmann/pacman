# Pacman - Jeu Simple en Python

Un jeu Pacman simple créé avec Python et Pygame.

## Installation

1. Installer les dépendances :
```bash
pip install -r requirements.txt
```

## Lancement

Pour lancer le jeu :
```bash
python pacman.py
```

## Contrôles

- **Flèches directionnelles** : Déplacer Pacman (↑ ↓ ← →)
- **R** : Redémarrer le jeu (après une partie terminée)

## Règles

- Collectez tous les points jaunes et les pacgommes pour passer au niveau suivant
- Évitez les fantômes rouges, roses et cyan
- Chaque point collecté rapporte 10 points
- Les pacgommes (grosses pastilles) rapportent 50 points
- Manger une pacgomme rend tous les fantômes vulnérables pendant 5 secondes
- Quand les fantômes sont vulnérables (bleus), vous pouvez les manger pour 200 points chacun
- Les fantômes vulnérables fuient Pacman au lieu de le poursuivre
- Quand un fantôme est mangé, il se transforme en yeux et retourne à sa base pour se régénérer
- Les yeux ne peuvent pas toucher Pacman - ils retournent directement à la base
- Vous avez **2 vies** au début du jeu
- Si un fantôme normal vous touche, vous perdez une vie et réapparaissez à la position de départ
- Le jeu se termine seulement quand vous n'avez plus de vies

## Système de Niveaux

- **Niveaux multiples** : Le jeu continue indéfiniment avec des niveaux de plus en plus difficiles
- **4 cartes différentes** : Le jeu alterne entre 4 labyrinthes différents à chaque niveau
  - Carte 1 : Labyrinthe classique avec passages symétriques
  - Carte 2 : Labyrinthe avec grandes zones ouvertes
  - Carte 3 : Labyrinthe avec passages verticaux
  - Carte 4 : Labyrinthe avec zones centrales
  - Les cartes alternent en boucle (Carte 1 → 2 → 3 → 4 → 1 → ...)
- **Difficulté progressive** :
  - Niveau 1 : 2 fantômes
  - Niveau 2-3 : 3 fantômes
  - Niveau 4+ : 4 fantômes (maximum)
  - La vitesse augmente lentement avec chaque niveau
- **Transition entre niveaux** : Un message s'affiche pendant 2 secondes indiquant le niveau et la carte
- **Score cumulatif** : Votre score est conservé entre les niveaux

## Fonctionnalités

- **4 labyrinthes différents** qui alternent entre les niveaux
- Pacman animé avec bouche qui s'ouvre et se ferme
- **Système de niveaux multiples** avec difficulté progressive
- Fantômes qui se déplacent de manière aléatoire (2 à 4 selon le niveau, moins agressifs)
- **Pacgommes** : grosses pastilles qui rendent les fantômes vulnérables
- Fantômes vulnérables (bleus) qui fuient Pacman
- Système de score avec bonus pour manger les fantômes
- Téléportation aux bords du labyrinthe
- Détection de collision avec les fantômes
- Affichage du niveau actuel et du nombre de vies à l'écran
- **Système de vies** : 2 vies au début, réapparition après perte de vie

Bon jeu !

