import os
import sys
import json
import pygame
from enum import Enum

"""
Sokoban - Version complète
Un jeu de réflexion où le joueur doit pousser des boîtes vers des objectifs
Fonctionnalités:
- Menu principal stylisé
- Sélecteur de niveaux
- Suivi des niveaux complétés
- Compteur de mouvements et de poussées
- Interface moderne et esthétique
"""

class Symbol(Enum):
    """
    Symboles utilisés pour représenter chaque élément dans le niveau
    • Utilisation d'une énumération pour éviter les erreurs de frappe et standardiser 
      les symboles à travers tout le code
    • Ces symboles correspondent aux caractères utilisés dans les fichiers de niveau .xsb
    """
    BOX = "$"
    BOX_ON_GOAL = "*"
    PLAYER = "@"
    PLAYER_ON_GOAL = "+"
    GOAL = "."
    WALL = "#"
    FLOOR = "-"


class MoveResponse(Enum):
    """
    Messages de retour pour les tentatives de mouvement
    • Permet de communiquer clairement la raison d'un échec de mouvement
    • Sépare la logique du jeu de l'affichage des messages d'erreur
    """
    INVALID_WALL = "Impossible de pousser les murs"
    INVALID_BOX = "Impossible de pousser cette boîte"
    VALID = "valid"


class GameState(Enum):
    """
    États possibles du jeu
    • Permet de gérer facilement les différents écrans et modes de jeu
    • Centralise la gestion du flux d'application
    """
    MAIN_MENU = 0
    LEVEL_SELECT = 1
    PLAYING = 2
    LEVEL_COMPLETE = 3
    GAME_COMPLETE = 4


class SokobanModel:
    def __init__(self, level_data):
        """
        • Utilise des ensembles (sets) pour les éléments du jeu plutôt que d'utiliser
          une seule matrice pour représenter le plateau de jeu
        • Cela simplifie la logique de déplacement et la détection des collisions
        • Réduit la complexité lors de la gestion des cases qui contiennent à la fois
          un objectif et un autre élément (joueur ou boîte)
        """
        self.walls = set()
        self.boxes = set()
        self.goals = set()
        
        # Initialiser les compteurs
        self.move_count = 0
        self.push_count = 0  # Compteur pour les poussées de boîtes

        self.size = [0, 0]
        if level_data and len(level_data) > 0:
            # Vérification de la présence de la méthode strip() pour gérer différents types d'entrées
            # (fichiers texte ou listes de chaînes)
            if hasattr(level_data[0], 'strip'):
                self.size = [len(level_data[0].strip()), len(level_data)]
            else:
                self.size = [len(level_data[0]), len(level_data)]

        # Parcourt chaque caractère du niveau pour extraire la position des éléments
        # Utilise le pattern matching (match/case) pour une meilleure lisibilité
        for y, row in enumerate(level_data):
            row_str = row.strip() if hasattr(row, 'strip') else row
            for x, symbol in enumerate(row_str):
                pos = (x, y)
                match symbol:
                    case Symbol.BOX.value:
                        self.boxes.add(pos)
                    case Symbol.BOX_ON_GOAL.value:
                        # Une boîte sur un objectif est représentée en ajoutant la position 
                        # à la fois dans l'ensemble des boîtes et dans celui des objectifs
                        self.boxes.add(pos)
                        self.goals.add(pos)
                    case Symbol.PLAYER.value:
                        self.player = pos
                    case Symbol.PLAYER_ON_GOAL.value:
                        self.player = pos
                        self.goals.add(pos)
                    case Symbol.GOAL.value:
                        self.goals.add(pos)
                    case Symbol.WALL.value:
                        self.walls.add(pos)
                    # Les cases vides (sol) ne sont pas stockées pour économiser de la mémoire

    def is_empty(self, x, y):
        """
        • Méthode auxiliaire pour vérifier si une case est vide
        • Simplifie les vérifications dans la méthode de déplacement
        • Plutôt que de vérifier ce qu'une case contient, on vérifie ce qu'elle ne contient pas
        """
        pos = (x, y)
        if pos in self.walls:
            return False
        if pos in self.boxes:
            return False
        return True

    def move(self, dx, dy):
        """
        • Implémente les règles de déplacement de Sokoban:
          1. Le joueur peut se déplacer dans un espace vide
          2. Le joueur peut pousser une boîte si l'espace derrière est vide
          3. Le joueur ne peut pas traverser les murs ou pousser des boîtes bloquées
        • Retourne un type de réponse plutôt qu'un simple booléen pour indiquer la cause 
          d'un échec de mouvement
        • Incrémente les compteurs de mouvements et de poussées
        """
        (x, y) = self.player
        (nx, ny) = (x + dx, y + dy)  # nx, ny sont où le joueur essaie d'aller
        result = None
        
        if self.is_empty(nx, ny):
            # Cas 1: Se déplacer vers une case vide
            self.player = (nx, ny)
            result = MoveResponse.VALID
        elif (nx, ny) in self.boxes:
            # Cas 2: Le joueur tente de pousser une boîte
            (nnx, nny) = (nx+dx, ny+dy)
            if self.is_empty(nnx, nny):
                # La boîte peut être poussée
                self.boxes.remove((nx, ny))
                self.boxes.add((nnx, nny))
                self.player = (nx, ny)
                self.push_count += 1  # Incrémenter le compteur de poussées
                result = MoveResponse.VALID
            else:
                # La boîte est bloquée par un mur ou une autre boîte
                result = MoveResponse.INVALID_BOX
        else:
            # Cas 3: Le joueur tente de traverser un mur
            result = MoveResponse.INVALID_WALL
            
        if result == MoveResponse.VALID:
            self.move_count += 1
            
        return result

    def get_move_count(self):
        """
        • Retourne le nombre de mouvements effectués
        • Utilisé pour calculer le score
        """
        return self.move_count
        
    def get_push_count(self):
        """
        • Retourne le nombre de poussées effectuées
        • Permet un suivi plus détaillé pour évaluer l'efficacité du joueur
        """
        return self.push_count

    def width(self):
        """
        • Accès au premier élément du tableau size pour faciliter la lisibilité du code
        • Encapsule l'accès aux données internes
        """
        return self.size[0]

    def height(self):
        """
        • Accès au second élément du tableau size pour faciliter la lisibilité du code
        • Encapsule l'accès aux données internes
        """
        return self.size[1]

    def symbol(self, x, y):
        """
        • Convertit les données internes en symboles d'affichage
        • Ordre de vérification important: d'abord les objectifs car ils peuvent 
          contenir d'autres éléments
        • Encapsule la logique d'affichage pour maintenir la séparation entre 
          données et représentation
        """
        pos = (x, y)
        if pos in self.goals:
            if pos in self.boxes:
                return Symbol.BOX_ON_GOAL
            if pos == self.player:
                return Symbol.PLAYER_ON_GOAL
            return Symbol.GOAL
        if pos in self.boxes:
            return Symbol.BOX
        if pos == self.player:
            return Symbol.PLAYER
        if pos in self.walls:
            return Symbol.WALL
        return Symbol.FLOOR
        
    def is_level_complete(self):
        """
        • Vérifie si le niveau est terminé en s'assurant que tous les objectifs 
          sont couverts par des boîtes
        • Utilise les ensembles pour une vérification efficace
        """
        # Vérifier que tous les objectifs sont couverts par des boîtes
        for goal_pos in self.goals:
            if goal_pos not in self.boxes:
                return False
    
        # S'assurer qu'il y a au moins un objectif
        return len(self.goals) > 0


class SokobanPygameView:
    """
    • Implémente le pattern MVC en séparant l'affichage (View) de la logique de jeu (Model)
    • Utilise Pygame pour le rendu graphique du jeu
    • Inclut un système de secours pour les images manquantes
    • Gère l'interface utilisateur améliorée avec menu principal et sélection de niveaux
    """
    def __init__(self, screen_width=800, screen_height=600, tile_size=64):
        """
        • Initialise Pygame et prépare les ressources nécessaires pour l'affichage
        • Paramètres pour la taille de l'écran et des tuiles
        • Définit les polices et couleurs pour l'interface utilisateur
        """
        pygame.init()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.tile_size = tile_size
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Sokoban Deluxe")
        
        # Polices pour différents éléments de l'interface
        self.title_font = pygame.font.SysFont('Arial', 64, bold=True)
        self.menu_font = pygame.font.SysFont('Arial', 36)
        self.level_font = pygame.font.SysFont('Arial', 28)
        self.info_font = pygame.font.SysFont('Arial', 20)
        
        # Couleurs pour les différents éléments de l'interface
        self.colors = {
            'background': (240, 240, 245),
            'title': (50, 50, 120),
            'button': (70, 130, 180),
            'button_hover': (100, 160, 220),
            'button_text': (255, 255, 255),
            'level_completed': (50, 180, 50),
            'level_locked': (150, 150, 150),
            'level_available': (70, 130, 180),
            'text_shadow': (0, 0, 0, 128)
        }
        
        # Chargement des images
        self.images = {}
        self.load_images()

    def load_images(self):
        """
        • Centralise le chargement des images en un seul endroit
        • Utilise un dictionnaire pour associer chaque symbole à son image
        • Inclut un système de secours pour gérer les erreurs de chargement d'images
        """
        image_paths = {
            Symbol.WALL: os.path.join("assets", "wall.png"),
            Symbol.BOX: os.path.join("assets", "box.png"),
            Symbol.GOAL: os.path.join("assets", "goal.png"),
            Symbol.BOX_ON_GOAL: os.path.join("assets", "box-on-goal.png"),
            Symbol.PLAYER: os.path.join("assets", "player.png"),
            Symbol.PLAYER_ON_GOAL: os.path.join("assets", "player-on-goal.png"),
            Symbol.FLOOR: os.path.join("assets", "floor.png")
        }

        for symbol, path in image_paths.items():
            try:
                image = pygame.image.load(path)
                self.images[symbol] = pygame.transform.scale(image, (self.tile_size, self.tile_size))
            except pygame.error as e:
                print(f"Couldn't load image {path}: {e}")
                fallback = pygame.Surface((self.tile_size, self.tile_size))
                fallback.fill(self.get_fallback_color(symbol))
                self.images[symbol] = fallback

    def get_fallback_color(self, symbol):
        """
        • Fournit des couleurs de secours pour chaque type d'élément
        • Permet au jeu de fonctionner même si les images sont absentes
        • Utilise des couleurs distinctives pour chaque élément afin de maintenir la jouabilité
        """
        colors = {
            Symbol.WALL: (120, 80, 50),
            Symbol.BOX: (180, 140, 60),
            Symbol.GOAL: (255, 215, 0),
            Symbol.BOX_ON_GOAL: (0, 150, 150),
            Symbol.PLAYER: (0, 100, 200),
            Symbol.PLAYER_ON_GOAL: (100, 150, 250),
            Symbol.FLOOR: (240, 240, 240)
        }
        return colors.get(symbol, (100, 100, 100))

    def setup_display(self, model=None):
        """
        • Configure la fenêtre de jeu en fonction de la taille du niveau
        • Adapte dynamiquement la taille de la fenêtre plutôt que d'utiliser une taille fixe
        • Assure que tous les éléments du niveau sont visibles
        """
        if model:
            width = max(self.screen_width, model.width() * self.tile_size)
            height = max(self.screen_height, model.height() * self.tile_size)
            if width > self.screen_width or height > self.screen_height:
                self.screen = pygame.display.set_mode((width, height))

    def render_main_menu(self):
        """
        • Affiche le menu principal avec un titre, des boutons et des instructions
        • Utilise des effets visuels (ombres, survol) pour améliorer l'esthétique
        • Retourne les rectangles des boutons pour la détection des clics
        """
        self.screen.fill(self.colors['background'])
        
        # Titre avec ombre
        title_text = "SOKOBAN DELUXE"
        title_shadow = self.title_font.render(title_text, True, (0, 0, 0))
        title_surface = self.title_font.render(title_text, True, self.colors['title'])
        
        title_rect = title_surface.get_rect(centerx=self.screen_width//2, centery=self.screen_height//4)
        shadow_rect = title_rect.copy()
        shadow_rect.x += 3
        shadow_rect.y += 3
        
        self.screen.blit(title_shadow, shadow_rect)
        self.screen.blit(title_surface, title_rect)
        
        # Boutons
        btn_width, btn_height = 300, 60
        btn_margin = 20
        
        # Bouton Jouer
        play_btn = pygame.Rect(
            (self.screen_width - btn_width) // 2,
            title_rect.bottom + 50,
            btn_width,
            btn_height
        )
        
        # Détection de la souris sur le bouton
        mouse_pos = pygame.mouse.get_pos()
        play_color = self.colors['button_hover'] if play_btn.collidepoint(mouse_pos) else self.colors['button']
        
        pygame.draw.rect(self.screen, play_color, play_btn, border_radius=10)
        pygame.draw.rect(self.screen, (255, 255, 255), play_btn, width=2, border_radius=10)
        
        play_text = self.menu_font.render("JOUER", True, self.colors['button_text'])
        play_text_rect = play_text.get_rect(center=play_btn.center)
        self.screen.blit(play_text, play_text_rect)
        
        # Bouton Quitter
        quit_btn = pygame.Rect(
            (self.screen_width - btn_width) // 2,
            play_btn.bottom + btn_margin,
            btn_width,
            btn_height
        )
        
        quit_color = self.colors['button_hover'] if quit_btn.collidepoint(mouse_pos) else self.colors['button']
        
        pygame.draw.rect(self.screen, quit_color, quit_btn, border_radius=10)
        pygame.draw.rect(self.screen, (255, 255, 255), quit_btn, width=2, border_radius=10)
        
        quit_text = self.menu_font.render("QUITTER", True, self.colors['button_text'])
        quit_text_rect = quit_text.get_rect(center=quit_btn.center)
        self.screen.blit(quit_text, quit_text_rect)
        
        # Instructions
        instructions = [
            "Utilisez les touches fléchées ou WASD pour déplacer le joueur",
            "Poussez les boîtes sur les objectifs pour terminer le niveau",
            "Appuyez sur R pour recommencer un niveau, ESC pour quitter"
        ]
        
        for i, line in enumerate(instructions):
            text = self.info_font.render(line, True, (80, 80, 80))
            text_rect = text.get_rect(centerx=self.screen_width//2, y=quit_btn.bottom + 50 + i*30)
            self.screen.blit(text, text_rect)
            
        pygame.display.flip()
        
        return play_btn, quit_btn

    def render_level_select(self, level_files, completed_levels):
        """
        • Affiche l'écran de sélection des niveaux avec progression
        • Indique visuellement les niveaux complétés et disponibles
        • Permet la navigation entre les niveaux
        """
        self.screen.fill(self.colors['background'])
        
        # Titre
        title_text = "SÉLECTION DES NIVEAUX"
        title_surface = self.menu_font.render(title_text, True, self.colors['title'])
        title_rect = title_surface.get_rect(centerx=self.screen_width//2, y=30)
        self.screen.blit(title_surface, title_rect)
        
        # Retour au menu
        back_btn = pygame.Rect(20, 20, 120, 40)
        
        mouse_pos = pygame.mouse.get_pos()
        back_color = self.colors['button_hover'] if back_btn.collidepoint(mouse_pos) else self.colors['button']
        
        pygame.draw.rect(self.screen, back_color, back_btn, border_radius=5)
        back_text = self.info_font.render("RETOUR", True, self.colors['button_text'])
        back_text_rect = back_text.get_rect(center=back_btn.center)
        self.screen.blit(back_text, back_text_rect)
        
        # Boutons de niveau
        level_buttons = []
        cols, rows = 4, 3
        btn_width, btn_height = 120, 120
        margin_x, margin_y = 30, 30
        
        total_width = cols * btn_width + (cols - 1) * margin_x
        total_height = rows * btn_height + (rows - 1) * margin_y
        
        start_x = (self.screen_width - total_width) // 2
        start_y = 100
        
        for i, level_file in enumerate(level_files):
            col = i % cols
            row = i // cols
            
            x = start_x + col * (btn_width + margin_x)
            y = start_y + row * (btn_height + margin_y)
            
            level_btn = pygame.Rect(x, y, btn_width, btn_height)
            level_buttons.append(level_btn)
            
            # Déterminer la couleur en fonction de l'état du niveau
            if i in completed_levels:
                btn_color = self.colors['level_completed']
            else:
                # Les niveaux sont disponibles dans l'ordre
                if i == 0 or (i > 0 and (i-1) in completed_levels):
                    btn_color = self.colors['level_available']
                else:
                    btn_color = self.colors['level_locked']
            
            # Effet de survol
            if level_btn.collidepoint(mouse_pos) and (i == 0 or (i > 0 and (i-1) in completed_levels) or i in completed_levels):
                btn_color = tuple(min(c + 30, 255) for c in btn_color)
                
            pygame.draw.rect(self.screen, btn_color, level_btn, border_radius=10)
            pygame.draw.rect(self.screen, (255, 255, 255), level_btn, width=2, border_radius=10)
            
            # Numéro du niveau
            level_num = i + 1
            level_text = self.level_font.render(f"Niveau {level_num}", True, (255, 255, 255))
            level_text_rect = level_text.get_rect(center=(x + btn_width//2, y + btn_height//2))
            self.screen.blit(level_text, level_text_rect)
            
            # Indicateur de niveau complété
            if i in completed_levels:
                complete_text = self.info_font.render("✓ Complété", True, (255, 255, 255))
                complete_rect = complete_text.get_rect(centerx=level_text_rect.centerx, top=level_text_rect.bottom + 5)
                self.screen.blit(complete_text, complete_rect)
        
        pygame.display.flip()
        
        return back_btn, level_buttons

    def render(self, model):
        """
        • Dessine l'état actuel du jeu à l'écran
        • Centre le niveau dans la fenêtre si nécessaire
        • Optimise le rendu en dessinant d'abord les sols puis les autres éléments
        """
        # Assurer que la taille est correcte
        self.setup_display(model)
        
        self.screen.fill((255, 255, 255))  # Fond blanc

        # Centre le niveau dans la fenêtre si nécessaire
        offset_x = max(0, (self.screen_width - model.width() * self.tile_size) // 2)
        offset_y = max(0, (self.screen_height - model.height() * self.tile_size) // 2)

        # Dessiner d'abord tous les sols
        for y in range(model.height()):
            for x in range(model.width()):
                self.screen.blit(
                    self.images[Symbol.FLOOR], 
                    (offset_x + x * self.tile_size, offset_y + y * self.tile_size)
                )

        # Puis dessiner les autres éléments
        for y in range(model.height()):
            for x in range(model.width()):
                symbol = model.symbol(x, y)
                
                if symbol != Symbol.FLOOR:  # On a déjà dessiné tous les sols
                    self.screen.blit(
                        self.images[symbol], 
                        (offset_x + x * self.tile_size, offset_y + y * self.tile_size)
                    )

        pygame.display.flip()

    def show_message(self, text, color=(0, 255, 0), duration=1500):
        """
        • Affiche des messages temporaires à l'écran (erreurs, succès, etc.)
        • Permet de personnaliser la couleur et la durée d'affichage
        • Utilise un fond semi-transparent pour améliorer la lisibilité
        """
        screen = pygame.display.get_surface()
        text_surface = self.menu_font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))

        # Fond semi-transparent pour le message
        background = pygame.Surface((text_rect.width + 20, text_rect.height + 20))
        background.set_alpha(200)  # Valeur d'alpha pour la transparence
        background.fill((0, 0, 0))
        background_rect = background.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))

        screen.blit(background, background_rect)
        screen.blit(text_surface, text_rect)
        pygame.display.flip()
        
        if duration > 0:
            pygame.time.delay(duration)
            # Redessine l'écran pour effacer le message
            pygame.display.flip()
        
    def show_score(self, score, level_number, move_count=None, push_count=None):
        """
        • Affiche le score actuel, le numéro de niveau et les compteurs en haut de l'écran
        • Utilise une police plus petite que les messages principaux
        • Ajoute les compteurs de mouvements et de poussées pour plus de détails
        """
        screen = pygame.display.get_surface()
        score_font = pygame.font.SysFont(None, 24)
        
        # Texte du score et du niveau
        score_text = f"Score: {score} | Niveau: {level_number}"
        if move_count is not None:
            score_text += f" | Mouvements: {move_count}"
        if push_count is not None:
            score_text += f" | Poussées: {push_count}"
            
        score_surface = score_font.render(score_text, True, (0, 0, 0))
        score_rect = score_surface.get_rect(topleft=(10, 10))
        
        # Fond blanc semi-transparent
        background = pygame.Surface((score_rect.width + 10, score_rect.height + 6))
        background.set_alpha(180)
        background.fill((255, 255, 255))
        background_rect = background.get_rect(topleft=(5, 5))
        
        # Dessiner sur la surface de l'écran
        screen.blit(background, background_rect)
        screen.blit(score_surface, score_rect)
        pygame.display.update(background_rect)
        
    def show_level_complete(self, level_score, total_score, move_count, push_count):
        """
        • Affiche un écran intermédiaire avec les statistiques du niveau terminé
        • Montre le score du niveau, le score total, et les compteurs
        • Ajoute une touche de célébration et d'encouragement
        """
        screen = pygame.display.get_surface()
        
        # Fond semi-transparent
        overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Titre
        complete_text = "NIVEAU TERMINÉ!"
        complete_surface = self.title_font.render(complete_text, True, (50, 255, 50))
        complete_rect = complete_surface.get_rect(centerx=screen.get_width()//2, y=screen.get_height()//4)
        screen.blit(complete_surface, complete_rect)
        
        # Statistiques
        stats = [
            f"Score du niveau: {level_score}",
            f"Score total: {total_score}",
            f"Mouvements: {move_count}",
            f"Poussées: {push_count}",
            "",
            "Appuyez sur ESPACE pour continuer"
        ]
        
        for i, stat in enumerate(stats):
            stat_surface = self.menu_font.render(stat, True, (255, 255, 255))
            stat_rect = stat_surface.get_rect(centerx=screen.get_width()//2, 
                                             y=complete_rect.bottom + 40 + i*40)
            screen.blit(stat_surface, stat_rect)
        
        pygame.display.flip()
        
    def show_game_complete(self, final_score):
        """
        • Affiche un écran de fin de jeu avec le score final
        • Utilise un design attrayant avec des couleurs vives
        • Reste affiché jusqu'à ce que le joueur ferme la fenêtre
        """
        screen = pygame.display.get_surface()
        
        # Effacer l'écran avec un fond noir
        screen.fill((0, 0, 0))
        
        # Titre avec reflet
        title_text = "FÉLICITATIONS!"
        shadow_surface = self.title_font.render(title_text, True, (100, 100, 200))
        title_surface = self.title_font.render(title_text, True, (255, 215, 0))
        
        shadow_rect = shadow_surface.get_rect(centerx=screen.get_width()//2 + 3, 
                                            centery=screen.get_height()//3 + 3)
        title_rect = title_surface.get_rect(centerx=screen.get_width()//2, 
                                          centery=screen.get_height()//3)
        
        screen.blit(shadow_surface, shadow_rect)
        screen.blit(title_surface, title_rect)
        
        # Score final
        score_text = f"Score final: {final_score}"
        score_surface = self.menu_font.render(score_text, True, (255, 255, 255))
        score_rect = score_surface.get_rect(centerx=screen.get_width()//2, 
                                           centery=screen.get_height()//2)
        screen.blit(score_surface, score_rect)
        
        # Message de félicitations
        congrats_text = "Vous avez terminé tous les niveaux!"

def main():
    """
    • Point d'entrée du programme
    • Utilise os.path.join pour la portabilité entre systèmes d'exploitation
    • Crée le contrôleur et lance la boucle de jeu
    """
    # Démarrer avec le niveau 0
    sokoban = SokobanController(level_number=0)
    sokoban.game_loop()


if __name__ == "__main__":
    """
    • Exécute la fonction main() seulement si ce fichier est exécuté directement
    • Permet au fichier d'être importé sans exécuter main()
    """
    main()