# Sokoban Game Improvement: Level Progression & Scoring System

Aperçu

Dans cette amélioration du jeu Sokoban, deux fonctionnalités clés ont été ajoutées pour améliorer l'expérience de jeu :

Progression des Niveaux
Le jeu passe maintenant au niveau suivant une fois le niveau actuel terminé. Chaque niveau est suivi d'une transition montrant la progression du joueur.


Système de Scoring
Le jeu inclut un système de points où chaque mouvement soustrait des points d'un score de base de 10 000. Le joueur peut voir ses points restants pendant qu'il joue, ce qui crée un défi de complétion des niveaux avec le moins de mouvements possible. À la fin du jeu, le score final est affiché sur une page de félicitations.

Fonctionnalités Ajoutées

Progression des Niveaux
Après avoir terminé un niveau, le jeu charge automatiquement le niveau suivant.
Si tous les niveaux sont complétés, un message de félicitations est affiché, incluant le score final du joueur.

Système de Scoring
Chaque mouvement dans le jeu soustrait 10 points du score initial de 10 000.
Cela encourage les joueurs à compléter les niveaux efficacement.
Le score est mis à jour en temps réel et visible à l'écran.

Écran de Complétion
Une fois tous les niveaux terminés, le jeu affiche un écran final félicitant le joueur et montrant son score.

Approche et Conception

Progression des Niveaux
À la fin de chaque niveau, le jeu vérifie s'il reste des niveaux.
S'il y a des niveaux suivants, le jeu passe automatiquement au niveau suivant.
Si le joueur a complété tous les niveaux, un message de félicitations est affiché.

Système de Scoring
Le jeu commence avec un score de 10 000.
À chaque mouvement du joueur, 10 points sont soustraits du score.
Le score est affiché à l'écran, permettant au joueur de voir son efficacité à résoudre les niveaux.
Le score est mis à jour et affiché en temps réel à chaque mouvement.

Message de Fin de Jeu
Une fois que le joueur termine tous les niveaux, une page affiche un message de félicitations ainsi que le score total obtenu.
Cela offre un sentiment d'accomplissement.