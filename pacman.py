import pygame
import random
import sys
import math
import json
import os

# Initialisation de Pygame
pygame.init()
pygame.mixer.init()

# Constantes
CELL_SIZE = 30
GRID_WIDTH = 21
GRID_HEIGHT = 21
WINDOW_WIDTH = CELL_SIZE * GRID_WIDTH
WINDOW_HEIGHT = CELL_SIZE * GRID_HEIGHT
FPS = 10
BASE_FPS = 10

# Couleurs
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
DARK_BLUE = (0, 0, 150)

TROPHY_FIRST_LEVEL = "premier_niveau"
TROPHY_SURVIVAL_START = "survie_debut"
TROPHY_SURVIVAL_10 = "survie_10_points"
TROPHY_SURVIVAL_50 = "survie_50_points"
TROPHY_SURVIVAL_100 = "survie_100_points"
TROPHY_SURVIVAL_GHOST = "survie_fantome"
TROPHY_SURVIVAL_POWER = "survie_power_up"
TOTAL_TROPHY_COUNT = 6

# Structure de l'arbre des trophées de survie (similaire à Minecraft)
# Format: {trophy_id: {"name": "Nom", "description": "Description", "position": (x, y), "parents": [trophy_ids]}}
SURVIVAL_TROPHY_TREE = {
    TROPHY_SURVIVAL_START: {
        "name": "Premier niveau",
        "description": "Commencer une partie de survie",
        "position": (100, 200),
        "parents": []
    },
    TROPHY_SURVIVAL_10: {
        "name": "Premiers pas",
        "description": "Atteindre 10 points",
        "position": (200, 150),
        "parents": [TROPHY_SURVIVAL_START]
    },
    TROPHY_SURVIVAL_50: {
        "name": "Survivant",
        "description": "Atteindre 50 points",
        "position": (300, 100),
        "parents": [TROPHY_SURVIVAL_10]
    },
    TROPHY_SURVIVAL_100: {
        "name": "Maître survivant",
        "description": "Atteindre 100 points",
        "position": (400, 50),
        "parents": [TROPHY_SURVIVAL_50]
    },
    TROPHY_SURVIVAL_GHOST: {
        "name": "Chasseur de fantômes",
        "description": "Manger 5 fantômes",
        "position": (200, 250),
        "parents": [TROPHY_SURVIVAL_START]
    },
    TROPHY_SURVIVAL_POWER: {
        "name": "Puissance maximale",
        "description": "Manger un power-up",
        "position": (300, 300),
        "parents": [TROPHY_SURVIVAL_GHOST]
    }
}

# Configuration des images de font
FONT_IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.webp')
FONT_IMAGE_EXCLUDE = {
    "avatar.png",
    "avatar pacman simple.png",
    "image-1ua5ykn6zpdhiyrhwcxym.webp",
    "image-j7dl7rmkwua252pmy6w50(2).png",
    "image-t26edcoujixq72uqkab3r(2).png",
    "avatar.jpg",
    "avatar.jpeg",
    "fatome_epee.png",
    "67",
    "67.png",
    "67.jpg",
    "67.jpeg",
    "67.webp",
    "six seveen .png",
    "le_super_67.webp",
    "le_super_67"
}
LEGACY_FONT_MAPPINGS = {
    "font1": ["font tout bleu.png", "font_tout_bleu.png", "font.png"],
    "font2": ["font arc en ciel.png", "font_arc_en_ciel.png"],
    "font3": ["tout pleins de couleur.png", "carré carré.png"]
}
FONT_GRID_IMAGE_SIZE = 80
FONT_GRID_SPACING = 90
FONT_GRID_START_Y = 120

def normalize_font_selection(font_key):
    """Normalise le nom de font en tenant compte des anciennes valeurs."""
    if not font_key:
        return None
    if font_key in LEGACY_FONT_MAPPINGS:
        for candidate in LEGACY_FONT_MAPPINGS[font_key]:
            if os.path.exists(candidate):
                return candidate
        return LEGACY_FONT_MAPPINGS[font_key][0]
    return font_key

def ensure_account_structure(account):
    """S'assure que la structure du compte contient toutes les clés nécessaires."""
    if 'trophies' not in account or not isinstance(account['trophies'], list):
        account['trophies'] = []
    # Normaliser les anciens avatars qui utilisaient l'image 2 (désormais supprimée)
    if account.get('selected_avatar') == 'avatar2':
        account['selected_avatar'] = 'avatar1'
    return account

def get_second_font():
    """Retourne le deuxième font (celui qui est exclu de la liste des fonts disponibles)."""
    font_files = []
    for entry in sorted(os.listdir(".")):
        entry_path = os.path.join(".", entry)
        if not os.path.isfile(entry_path):
            continue
        entry_lower = entry.lower()
        if not entry_lower.endswith(FONT_IMAGE_EXTENSIONS):
            continue
        # Exclure les images dans FONT_IMAGE_EXCLUDE, les avatars, les images avec "67", "le_super_67", et les images avec "(2)"
        if entry_lower in FONT_IMAGE_EXCLUDE or entry_lower.startswith("avatar") or entry_lower.startswith("67") or "le_super_67" in entry_lower or "(2)" in entry_lower:
            continue
        font_files.append(entry)
    # Retourner le deuxième font (index 1) s'il existe
    if len(font_files) > 1:
        return font_files[1]
    return None

def get_available_font_images():
    """Retourne la liste triée des images disponibles pour les fonts."""
    font_files = []
    for entry in sorted(os.listdir(".")):
        entry_path = os.path.join(".", entry)
        if not os.path.isfile(entry_path):
            continue
        entry_lower = entry.lower()
        if not entry_lower.endswith(FONT_IMAGE_EXTENSIONS):
            continue
        # Exclure les images dans FONT_IMAGE_EXCLUDE, les avatars, les images avec "67", "le_super_67", et les images avec "(2)"
        if entry_lower in FONT_IMAGE_EXCLUDE or entry_lower.startswith("avatar") or entry_lower.startswith("67") or "le_super_67" in entry_lower or "(2)" in entry_lower:
            continue
        font_files.append(entry)
    # Supprimer le deuxième font en partant de la gauche (index 1)
    if len(font_files) > 1:
        font_files.pop(1)
    return font_files

def build_font_option_rects(font_files, small_size=FONT_GRID_IMAGE_SIZE, spacing=FONT_GRID_SPACING, start_y=FONT_GRID_START_Y):
    """Construit les rectangles utilisés pour positionner les images de font."""
    rects = []
    items_per_row = max(1, (WINDOW_WIDTH - 40) // spacing)
    idx = 0
    current_y = start_y
    while idx < len(font_files):
        row_files = font_files[idx:idx + items_per_row]
        row_count = len(row_files)
        row_total_width = row_count * small_size + max(0, row_count - 1) * (spacing - small_size)
        row_start_x = max(10, (WINDOW_WIDTH - row_total_width) // 2)
        for col, font_file in enumerate(row_files):
            rect = pygame.Rect(row_start_x + col * spacing, current_y, small_size, small_size)
            rects.append((rect, font_file))
        current_y += spacing
        idx += items_per_row
    return rects

def load_font_surface(font_key):
    """Charge la surface correspondant à la font sélectionnée."""
    font_path = normalize_font_selection(font_key)
    if font_path and os.path.exists(font_path):
        try:
            return pygame.image.load(font_path)
        except Exception:
            return None
    return None

# Labyrinthes (1 = mur, 0 = chemin, 2 = point, 3 = pacgomme)
MAZE_1 = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,3,2,2,2,2,2,2,2,2,1,2,2,2,2,2,2,2,2,3,1],
    [1,2,1,1,1,2,1,1,1,2,1,2,1,1,1,2,1,1,1,2,1],
    [1,2,1,0,1,2,1,0,1,2,1,2,1,0,1,2,1,0,1,2,1],
    [1,2,1,1,1,2,1,1,1,2,1,2,1,1,1,2,1,1,1,2,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,1,2,1,2,1,1,1,1,1,2,1,2,1,1,1,2,1],
    [1,2,2,2,2,2,1,2,2,2,1,2,2,2,1,2,2,2,2,2,1],
    [1,1,1,1,1,2,1,1,1,0,1,0,1,1,1,2,1,1,1,1,1],
    [0,0,0,0,1,2,1,0,0,0,0,0,0,0,1,2,1,0,0,0,0],
    [1,1,1,1,1,2,1,0,1,1,1,1,1,0,1,2,1,1,1,1,1],
    [0,0,0,0,0,2,0,0,1,0,0,0,1,0,0,2,0,0,0,0,0],
    [1,1,1,1,1,2,1,0,1,1,1,1,1,0,1,2,1,1,1,1,1],
    [0,0,0,0,1,2,1,0,0,0,0,0,0,0,1,2,1,0,0,0,0],
    [1,1,1,1,1,2,1,0,1,1,1,1,1,0,1,2,1,1,1,1,1],
    [1,2,2,2,2,2,2,2,2,2,1,2,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,1,2,1,1,1,2,1,2,1,1,1,2,1,1,1,2,1],
    [1,2,2,2,1,2,2,2,2,2,0,2,2,2,2,2,1,2,2,2,1],
    [1,1,2,1,1,2,1,2,1,1,1,1,1,2,1,2,1,1,2,1,1],
    [1,3,2,2,2,2,1,2,2,2,1,2,2,2,1,2,2,2,2,3,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

MAZE_2 = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,3,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,3,1],
    [1,2,1,1,1,1,1,2,1,1,1,1,1,2,1,1,1,1,1,2,1],
    [1,2,1,0,0,0,1,2,1,0,0,0,1,2,1,0,0,0,1,2,1],
    [1,2,1,1,1,2,1,2,1,1,1,1,1,2,1,2,1,1,1,2,1],
    [1,2,2,2,2,2,2,2,2,2,1,2,2,2,2,2,2,2,2,2,1],
    [1,1,1,1,1,2,1,1,1,2,1,2,1,1,1,2,1,1,1,1,1],
    [0,0,0,0,1,2,1,2,2,2,0,2,2,2,1,2,1,0,0,0,0],
    [1,1,1,1,1,2,1,2,1,0,0,0,1,2,1,2,1,1,1,1,1],
    [0,0,0,0,0,2,0,2,1,0,0,0,1,2,0,2,0,0,0,0,0],
    [1,1,1,1,1,2,1,2,1,1,1,1,1,2,1,2,1,1,1,1,1],
    [0,0,0,0,0,2,0,2,0,0,0,0,0,2,0,2,0,0,0,0,0],
    [1,1,1,1,1,2,1,2,1,1,1,1,1,2,1,2,1,1,1,1,1],
    [0,0,0,0,0,2,0,2,1,0,0,0,1,2,0,2,0,0,0,0,0],
    [1,1,1,1,1,2,1,2,1,0,0,0,1,2,1,2,1,1,1,1,1],
    [0,0,0,0,1,2,1,2,2,2,0,2,2,2,1,2,1,0,0,0,0],
    [1,1,1,1,1,2,1,1,1,2,1,2,1,1,1,2,1,1,1,1,1],
    [1,2,2,2,2,2,2,2,2,2,1,2,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,1,1,1,2,1,1,1,1,1,2,1,1,1,1,1,2,1],
    [1,3,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,3,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

MAZE_3 = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,3,2,2,2,2,2,2,2,2,1,2,2,2,2,2,2,2,2,3,1],
    [1,2,1,1,1,2,1,1,1,2,1,2,1,1,1,2,1,1,1,2,1],
    [1,2,2,2,1,2,2,2,1,2,1,2,1,2,2,2,1,2,2,2,1],
    [1,1,1,2,1,1,1,2,1,2,1,2,1,2,1,1,1,2,1,1,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,1,2,1,2,1,1,1,1,1,2,1,2,1,1,1,2,1],
    [1,2,2,2,1,2,1,2,2,2,1,2,2,2,1,2,1,2,2,2,1],
    [1,1,1,2,1,2,1,1,1,0,1,0,1,1,1,2,1,2,1,1,1],
    [0,0,1,2,1,2,1,0,0,0,0,0,0,0,1,2,1,2,1,0,0],
    [1,1,1,2,1,2,1,0,1,1,1,1,1,0,1,2,1,2,1,1,1],
    [0,0,0,2,0,2,0,0,1,0,0,0,1,0,0,2,0,2,0,0,0],
    [1,1,1,2,1,2,1,0,1,1,1,1,1,0,1,2,1,2,1,1,1],
    [0,0,1,2,1,2,1,0,0,0,0,0,0,0,1,2,1,2,1,0,0],
    [1,1,1,2,1,2,1,1,1,0,1,0,1,1,1,2,1,2,1,1,1],
    [1,2,2,2,1,2,1,2,2,2,1,2,2,2,1,2,1,2,2,2,1],
    [1,2,1,1,1,2,1,2,1,1,1,1,1,2,1,2,1,1,1,2,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,1,1,2,1,1,1,2,1,1,1,1,1,2,1,1,1,2,1,1,1],
    [1,3,2,2,2,2,2,2,2,2,1,2,2,2,2,2,2,2,2,3,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

MAZE_4 = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,3,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,3,1],
    [1,2,1,1,1,2,1,1,1,1,1,1,1,1,1,2,1,1,1,2,1],
    [1,2,1,0,1,2,1,0,0,0,0,0,0,0,1,2,1,0,1,2,1],
    [1,2,1,1,1,2,1,1,1,2,1,2,1,1,1,2,1,1,1,2,1],
    [1,2,2,2,2,2,2,2,2,2,1,2,2,2,2,2,2,2,2,2,1],
    [1,1,1,1,1,2,1,1,1,2,1,2,1,1,1,2,1,1,1,1,1],
    [0,0,0,0,1,2,1,2,2,2,0,2,2,2,1,2,1,0,0,0,0],
    [1,1,1,1,1,2,1,2,1,0,0,0,1,2,1,2,1,1,1,1,1],
    [1,2,2,2,2,2,2,2,1,0,0,0,1,2,2,2,2,2,2,2,1],
    [1,1,1,1,1,2,1,2,1,1,1,1,1,2,1,2,1,1,1,1,1],
    [0,0,0,0,0,2,0,2,0,0,0,0,0,2,0,2,0,0,0,0,0],
    [1,1,1,1,1,2,1,2,1,1,1,1,1,2,1,2,1,1,1,1,1],
    [1,2,2,2,2,2,2,2,1,0,0,0,1,2,2,2,2,2,2,2,1],
    [1,1,1,1,1,2,1,2,1,0,0,0,1,2,1,2,1,1,1,1,1],
    [0,0,0,0,1,2,1,2,2,2,0,2,2,2,1,2,1,0,0,0,0],
    [1,1,1,1,1,2,1,1,1,2,1,2,1,1,1,2,1,1,1,1,1],
    [1,2,2,2,2,2,2,2,2,2,1,2,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,1,1,1,2,1,1,1,1,1,2,1,1,1,1,1,2,1],
    [1,3,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,3,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

# Fonction pour générer des variations de labyrinthes
def generate_maze_variation(base_maze, variation_id):
    """Génère une variation d'un labyrinthe de base"""
    maze = [row[:] for row in base_maze]
    
    # Modifier aléatoirement certains points et pacgommes
    random.seed(variation_id)  # Utiliser l'ID pour avoir des variations reproductibles
    
    for y in range(1, GRID_HEIGHT - 1):
        for x in range(1, GRID_WIDTH - 1):
            # Ne modifier que les chemins (0, 2, 3)
            if maze[y][x] in [0, 2, 3]:
                rand = random.random()
                # Parfois changer un point en chemin vide ou vice versa
                if rand < 0.1:  # 10% de chance
                    if maze[y][x] == 2:
                        maze[y][x] = 0
                    elif maze[y][x] == 0:
                        maze[y][x] = 2
                # Parfois changer une pacgomme en point ou vice versa
                elif rand < 0.15:  # 5% de chance supplémentaire
                    if maze[y][x] == 3:
                        maze[y][x] = 2
                    elif maze[y][x] == 2 and random.random() < 0.05:
                        maze[y][x] = 3
    
    # S'assurer qu'il y a au moins 2 pacgommes
    pacgomme_count = sum(row.count(3) for row in maze)
    if pacgomme_count < 2:
        # Ajouter des pacgommes si nécessaire
        for y in range(1, GRID_HEIGHT - 1):
            for x in range(1, GRID_WIDTH - 1):
                if maze[y][x] == 2 and pacgomme_count < 2:
                    maze[y][x] = 3
                    pacgomme_count += 1
    
    return maze

# Utiliser seulement les 4 labyrinthes de base
MAZES = []
base_mazes = [MAZE_1, MAZE_2, MAZE_3, MAZE_4]

# Ajouter les 4 labyrinthes de base
for base_maze in base_mazes:
    MAZES.append([row[:] for row in base_maze])

def find_path_between(maze, start, target):
    """Trouve un chemin accessible entre deux points en utilisant BFS"""
    if start == target:
        return [start]
    
    queue = [(start, [start])]
    visited = {start}
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    
    while queue:
        (x, y), path = queue.pop(0)
        
        for dx, dy in directions:
            new_x = x + dx
            new_y = y + dy
            
            # Vérifier les limites et si c'est accessible
            if 0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT:
                if maze[new_y][new_x] != 1:  # Pas un mur
                    if (new_x, new_y) == target:
                        return path + [(new_x, new_y)]
                    if (new_x, new_y) not in visited:
                        visited.add((new_x, new_y))
                        queue.append(((new_x, new_y), path + [(new_x, new_y)]))
    
    return None  # Pas de chemin trouvé

def generate_path_through_all_cells(maze):
    """Génère un chemin qui traverse toutes les cases accessibles du labyrinthe"""
    path = []
    visited = set()
    
    # Trouver toutes les cases accessibles (pas de mur)
    accessible_cells = []
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if maze[y][x] != 1:  # Pas un mur
                accessible_cells.append((x, y))
    
    if not accessible_cells:
        return [(10, 9)]  # Chemin par défaut
    
    # Utiliser un algorithme de parcours pour visiter toutes les cases
    # Commencer par la première case accessible
    start = accessible_cells[0]
    visited.add(start)
    path.append(start)
    
    # Parcourir toutes les cases en utilisant un DFS simplifié
    while len(visited) < len(accessible_cells):
        current = path[-1]
        x, y = current
        
        # Chercher une case adjacente non visitée
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        found = False
        
        for dx, dy in directions:
            new_x = x + dx
            new_y = y + dy
            
            # Vérifier les limites et si c'est accessible
            if 0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT:
                if maze[new_y][new_x] != 1 and (new_x, new_y) not in visited:
                    path.append((new_x, new_y))
                    visited.add((new_x, new_y))
                    found = True
                    break
        
        # Si aucune case adjacente non visitée, chercher la plus proche non visitée
        if not found:
            min_dist = float('inf')
            closest = None
            for cell in accessible_cells:
                if cell not in visited:
                    dist = abs(cell[0] - x) + abs(cell[1] - y)
                    if dist < min_dist:
                        min_dist = dist
                        closest = cell
            
            if closest:
                # Trouver un chemin valide vers la case la plus proche
                sub_path = find_path_between(maze, current, closest)
                if sub_path:
                    # Ajouter toutes les cases du chemin (sauf la première qui est déjà dans path)
                    for cell in sub_path[1:]:
                        if cell not in visited:
                            path.append(cell)
                            visited.add(cell)
                else:
                    # Si pas de chemin trouvé, essayer une autre case
                    break
            else:
                break
    
    return path if path else [(10, 9)]

class Pacman:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = (0, 0)
        self.next_direction = (0, 0)
        self.mouth_open = True
        self.mouth_angle = 0
        
    def update(self, maze):
        # Essayer de changer de direction
        if self.can_move(self.next_direction, maze):
            self.direction = self.next_direction
        
        # Se déplacer dans la direction actuelle
        if self.can_move(self.direction, maze):
            self.x += self.direction[0]
            self.y += self.direction[1]
            # Téléportation aux bords
            if self.x < 0:
                self.x = GRID_WIDTH - 1
            elif self.x >= GRID_WIDTH:
                self.x = 0
        
        # Animation de la bouche
        self.mouth_angle += 5
        if self.mouth_angle >= 360:
            self.mouth_angle = 0
        self.mouth_open = (self.mouth_angle // 30) % 2 == 0
    
    def can_move(self, direction, maze):
        new_x = self.x + direction[0]
        new_y = self.y + direction[1]
        
        # Téléportation aux bords
        if new_x < 0 or new_x >= GRID_WIDTH:
            return True
        
        if new_y < 0 or new_y >= GRID_HEIGHT:
            return False
        
        return maze[new_y][new_x] != 1
    
    def set_direction(self, direction):
        self.next_direction = direction
    
    def draw(self, screen, invincible=False, has_crown=False, has_longue_vue=False, has_indigestion=False, is_double_longue_vue=False, is_rainbow_critique=False, has_skin_bleu=False, has_skin_orange=False, has_skin_rose=False, has_skin_rouge=False, super_vie_active=False):
        center_x = self.x * CELL_SIZE + CELL_SIZE // 2
        center_y = self.y * CELL_SIZE + CELL_SIZE // 2
        radius = CELL_SIZE // 2 - 2
        
        # Si invincible (mais pas super vie), faire clignoter (afficher seulement 50% du temps)
        # La super vie ne fait pas clignoter
        if invincible and not super_vie_active and (pygame.time.get_ticks() // 100) % 2 == 0:
            return  # Ne pas dessiner pendant le clignotement
        
        # Choisir la couleur : arc-en-ciel si coup critique, vert si indigestion, bleu clair si un skin est équipé, jaune sinon
        LIGHT_BLUE = (173, 216, 230)  # Bleu clair
        if is_rainbow_critique:
            # Effet arc-en-ciel : changer de couleur selon le temps
            time = pygame.time.get_ticks() // 30  # Vitesse de changement de couleur (plus rapide)
            r = int(127.5 * (1 + math.sin(time * 0.2)))
            g = int(127.5 * (1 + math.sin(time * 0.2 + 2.09)))
            b = int(127.5 * (1 + math.sin(time * 0.2 + 4.18)))
            pacman_color = (r, g, b)
        elif has_indigestion:
            pacman_color = (0, 255, 0)  # Vert
        elif has_skin_bleu or has_skin_orange or has_skin_rose or has_skin_rouge:
            pacman_color = LIGHT_BLUE  # Bleu clair pour tous les skins
        else:
            pacman_color = YELLOW
        
        # Dessiner le cercle de Pacman
        pygame.draw.circle(screen, pacman_color, (center_x, center_y), radius)
        
        # Dessiner la bouche si elle est ouverte
        if self.mouth_open and self.direction != (0, 0):
            # Calculer la direction de la bouche
            if self.direction == (1, 0):  # Droite
                mouth_points = [
                    (center_x, center_y),
                    (center_x + radius, center_y - radius // 2),
                    (center_x + radius, center_y + radius // 2)
                ]
            elif self.direction == (-1, 0):  # Gauche
                mouth_points = [
                    (center_x, center_y),
                    (center_x - radius, center_y - radius // 2),
                    (center_x - radius, center_y + radius // 2)
                ]
            elif self.direction == (0, -1):  # Haut
                mouth_points = [
                    (center_x, center_y),
                    (center_x - radius // 2, center_y - radius),
                    (center_x + radius // 2, center_y - radius)
                ]
            elif self.direction == (0, 1):  # Bas
                mouth_points = [
                    (center_x, center_y),
                    (center_x - radius // 2, center_y + radius),
                    (center_x + radius // 2, center_y + radius)
                ]
            else:
                mouth_points = [
                    (center_x, center_y),
                    (center_x + radius, center_y - radius // 2),
                    (center_x + radius, center_y + radius // 2)
                ]
            
            # Dessiner un triangle noir pour la bouche
            pygame.draw.polygon(screen, BLACK, mouth_points)
        
        # Dessiner la couronne si on en a une
        if has_crown:
            # Couleur dorée pour la couronne
            crown_color = (255, 215, 0)  # Or
            crown_y = center_y - radius - 5
            crown_width = radius + 4
            crown_height = 8
            
            # Base de la couronne (rectangle)
            pygame.draw.rect(screen, crown_color, 
                           (center_x - crown_width // 2, crown_y, crown_width, crown_height))
            
            # Pointes de la couronne (triangles)
            num_points = 5
            point_width = crown_width // num_points
            for i in range(num_points):
                point_x = center_x - crown_width // 2 + i * point_width + point_width // 2
                point_top = crown_y - 6
                point_points = [
                    (point_x, point_top),
                    (point_x - point_width // 3, crown_y),
                    (point_x + point_width // 3, crown_y)
                ]
                pygame.draw.polygon(screen, crown_color, point_points)
        
        # Dessiner la longue vue si équipée
        if has_longue_vue:
            # Selle sur Pacman (rectangle marron sur le dos)
            selle_color = (139, 69, 19)  # Marron
            selle_width = radius + 2
            selle_height = radius // 2
            selle_x = center_x - selle_width // 2
            selle_y = center_y + radius // 3
            pygame.draw.rect(screen, selle_color, (selle_x, selle_y, selle_width, selle_height))
            pygame.draw.rect(screen, BLACK, (selle_x, selle_y, selle_width, selle_height), 1)
            
            # Lanterne (cercle jaune/orange avec lumière)
            lanterne_x = center_x
            lanterne_y = center_y - radius - 8
            lanterne_radius = 6
            # Corps de la lanterne (orange)
            pygame.draw.circle(screen, (255, 165, 0), (lanterne_x, lanterne_y), lanterne_radius)
            pygame.draw.circle(screen, BLACK, (lanterne_x, lanterne_y), lanterne_radius, 1)
            # Lumière de la lanterne (jaune clair)
            pygame.draw.circle(screen, (255, 255, 200), (lanterne_x, lanterne_y), lanterne_radius - 2)
            
            # Blocs selon la direction (1 pour simple longue vue, 4 pour double longue vue)
            if is_double_longue_vue:
                # Double longue vue : blocs dans les 4 directions
                block_positions = [
                    (self.x + 1, self.y),  # Droite
                    (self.x - 1, self.y),  # Gauche
                    (self.x, self.y + 1),  # Bas
                    (self.x, self.y - 1)   # Haut
                ]
            else:
                # Simple longue vue : bloc devant selon la direction
                block_cell_x = self.x
                block_cell_y = self.y
                if self.direction == (1, 0):  # Droite
                    block_cell_x = self.x + 1
                    block_cell_y = self.y
                elif self.direction == (-1, 0):  # Gauche
                    block_cell_x = self.x - 1
                    block_cell_y = self.y
                elif self.direction == (0, -1):  # Haut
                    block_cell_x = self.x
                    block_cell_y = self.y - 1
                elif self.direction == (0, 1):  # Bas
                    block_cell_x = self.x
                    block_cell_y = self.y + 1
                else:
                    # Par défaut, devant (droite)
                    block_cell_x = self.x + 1
                    block_cell_y = self.y
                block_positions = [(block_cell_x, block_cell_y)]
            
            # Dessiner les blocs
            block_color = (128, 128, 128)  # Gris
            for block_cell_x, block_cell_y in block_positions:
                # Gérer la téléportation aux bords
                if block_cell_x < 0:
                    block_cell_x = GRID_WIDTH - 1
                elif block_cell_x >= GRID_WIDTH:
                    block_cell_x = 0
                
                # Vérifier que le bloc est dans les limites du labyrinthe
                if 0 <= block_cell_x < GRID_WIDTH and 0 <= block_cell_y < GRID_HEIGHT:
                    block_x = block_cell_x * CELL_SIZE
                    block_y = block_cell_y * CELL_SIZE
                    
                    # Dessiner le bloc (rectangle gris)
                    block_rect = pygame.Rect(block_x, block_y, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(screen, block_color, block_rect)
                    pygame.draw.rect(screen, BLACK, block_rect, 2)

class Ghost:
    def __init__(self, x, y, color, harmless=False, hits_required=1):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.color = color
        self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        self.steps = 0
        self.vulnerable = False
        self.returning = False
        self.eyes = False  # État yeux seulement (après avoir été mangé)
        self.ice_slowdown = 0  # Compteur pour ralentir le fantôme sur la glace
        self.harmless = harmless  # Si True, ce fantôme ne peut pas tuer Pacman (pour l'indigestion)
        self.flee_timer = 0  # Timer pour faire fuir le fantôme (10 secondes = 100 frames à 10 FPS)
        self.immobilized_timer = 0  # Timer pour immobiliser le fantôme (10 secondes = 100 frames à 10 FPS)
        self.hits_required = hits_required  # Nombre de "coups" nécessaires pour tuer le fantôme (par défaut 1)
        self.hits_taken = 0  # Nombre de "coups" déjà reçus
        # Chemin prédéfini pour les fantômes bleus
        if color == BLUE:
            # Le chemin sera généré lors de l'initialisation avec le labyrinthe
            self.path = None
            self.path_index = 0
        else:
            self.path = None
            self.path_index = 0
    
    def set_path(self, maze):
        """Définit le chemin prédéfini pour les fantômes bleus"""
        if self.color == BLUE:
            self.path = generate_path_through_all_cells(maze)
            # Trouver la position la plus proche dans le chemin
            min_dist = float('inf')
            closest_index = 0
            for i, (px, py) in enumerate(self.path):
                dist = abs(px - self.x) + abs(py - self.y)
                if dist < min_dist:
                    min_dist = dist
                    closest_index = i
            self.path_index = closest_index
        
    def update(self, maze, pacman_pos=None):
        self.steps += 1
        
        # Si en mode yeux, retourner à la base (peut traverser les murs)
        if self.eyes:
            # Se diriger vers la position de départ (chemin le plus court)
            dx = self.start_x - self.x
            dy = self.start_y - self.y
            
            # Choisir la direction qui se rapproche le plus de la base
            # Les yeux peuvent traverser les murs, donc on choisit directement la meilleure direction
            if abs(dx) > abs(dy):
                if dx > 0:
                    self.direction = (1, 0)
                elif dx < 0:
                    self.direction = (-1, 0)
                elif dy > 0:
                    self.direction = (0, 1)
                elif dy < 0:
                    self.direction = (0, -1)
            else:
                if dy > 0:
                    self.direction = (0, 1)
                elif dy < 0:
                    self.direction = (0, -1)
                elif dx > 0:
                    self.direction = (1, 0)
                elif dx < 0:
                    self.direction = (-1, 0)
            
            # Vérifier si on est arrivé à la base
            if self.x == self.start_x and self.y == self.start_y:
                self.eyes = False
                self.vulnerable = False
                self.returning = False
                self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        # Si le fantôme doit fuir (flee_timer > 0), fuir Pacman (comme vulnérable)
        elif self.flee_timer > 0 and pacman_pos is not None:
            pacman_x, pacman_y = pacman_pos
            # Calculer la direction pour s'éloigner de Pacman
            dx = self.x - pacman_x
            dy = self.y - pacman_y
            
            # Choisir la direction qui s'éloigne le plus de Pacman
            possible_dirs = []
            if abs(dx) > abs(dy):
                if dx > 0:
                    possible_dirs.append((1, 0))
                else:
                    possible_dirs.append((-1, 0))
                if dy > 0:
                    possible_dirs.append((0, 1))
                else:
                    possible_dirs.append((0, -1))
            else:
                if dy > 0:
                    possible_dirs.append((0, 1))
                else:
                    possible_dirs.append((0, -1))
                if dx > 0:
                    possible_dirs.append((1, 0))
                else:
                    possible_dirs.append((-1, 0))
            
            # Choisir une direction valide qui s'éloigne de Pacman
            valid_dirs = [d for d in possible_dirs if self.can_move(d, maze)]
            if valid_dirs:
                self.direction = valid_dirs[0]
            elif self.steps % 3 == 0:
                # Si bloqué, essayer une direction aléatoire
                all_dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                valid_dirs = [d for d in all_dirs if self.can_move(d, maze)]
                if valid_dirs:
                    self.direction = random.choice(valid_dirs)
        # Si vulnérable, fuir Pacman
        elif self.vulnerable and pacman_pos is not None:
            pacman_x, pacman_y = pacman_pos
            # Calculer la direction pour s'éloigner de Pacman
            dx = self.x - pacman_x
            dy = self.y - pacman_y
            
            # Choisir la direction qui s'éloigne le plus de Pacman
            possible_dirs = []
            if abs(dx) > abs(dy):
                if dx > 0:
                    possible_dirs.append((1, 0))
                else:
                    possible_dirs.append((-1, 0))
                if dy > 0:
                    possible_dirs.append((0, 1))
                else:
                    possible_dirs.append((0, -1))
            else:
                if dy > 0:
                    possible_dirs.append((0, 1))
                else:
                    possible_dirs.append((0, -1))
                if dx > 0:
                    possible_dirs.append((1, 0))
                else:
                    possible_dirs.append((-1, 0))
            
            # Choisir une direction valide qui s'éloigne de Pacman
            valid_dirs = [d for d in possible_dirs if self.can_move(d, maze)]
            if valid_dirs:
                self.direction = valid_dirs[0]
            elif self.steps % 3 == 0:
                # Si bloqué, essayer une direction aléatoire
                all_dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                valid_dirs = [d for d in all_dirs if self.can_move(d, maze)]
                if valid_dirs:
                    self.direction = random.choice(valid_dirs)
        else:
            # Comportement normal : les fantômes bleus suivent un chemin prédéfini
            if self.color == BLUE and self.path is not None:
                # Les fantômes bleus suivent un chemin prédéfini
                target_x, target_y = self.path[self.path_index]
                
                # Si on est arrivé à la position cible, passer à la suivante
                if self.x == target_x and self.y == target_y:
                    self.path_index = (self.path_index + 1) % len(self.path)
                    target_x, target_y = self.path[self.path_index]
                
                # Calculer la direction vers la prochaine position du chemin
                dx = target_x - self.x
                dy = target_y - self.y
                
                # Choisir la direction qui se rapproche le plus de la cible
                possible_dirs = []
                if abs(dx) > abs(dy):
                    if dx > 0:
                        possible_dirs.append((1, 0))
                    elif dx < 0:
                        possible_dirs.append((-1, 0))
                    if dy > 0:
                        possible_dirs.append((0, 1))
                    elif dy < 0:
                        possible_dirs.append((0, -1))
                else:
                    if dy > 0:
                        possible_dirs.append((0, 1))
                    elif dy < 0:
                        possible_dirs.append((0, -1))
                    if dx > 0:
                        possible_dirs.append((1, 0))
                    elif dx < 0:
                        possible_dirs.append((-1, 0))
                
                # Choisir une direction valide qui se rapproche de la cible
                valid_dirs = [d for d in possible_dirs if self.can_move(d, maze)]
                if valid_dirs:
                    self.direction = valid_dirs[0]
                elif self.steps % 3 == 0:
                    # Si bloqué, essayer une direction aléatoire
                    all_dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                    valid_dirs = [d for d in all_dirs if self.can_move(d, maze)]
                    if valid_dirs:
                        self.direction = random.choice(valid_dirs)
            elif self.color == RED and pacman_pos is not None:
                # Les fantômes rouges suivent Pacman
                pacman_x, pacman_y = pacman_pos
                dx = pacman_x - self.x
                dy = pacman_y - self.y
                
                # Choisir la direction qui se rapproche le plus de Pacman
                possible_dirs = []
                if abs(dx) > abs(dy):
                    if dx > 0:
                        possible_dirs.append((1, 0))
                    elif dx < 0:
                        possible_dirs.append((-1, 0))
                    if dy > 0:
                        possible_dirs.append((0, 1))
                    elif dy < 0:
                        possible_dirs.append((0, -1))
                else:
                    if dy > 0:
                        possible_dirs.append((0, 1))
                    elif dy < 0:
                        possible_dirs.append((0, -1))
                    if dx > 0:
                        possible_dirs.append((1, 0))
                    elif dx < 0:
                        possible_dirs.append((-1, 0))
                
                # Choisir une direction valide qui se rapproche de Pacman
                valid_dirs = [d for d in possible_dirs if self.can_move(d, maze)]
                if valid_dirs:
                    self.direction = valid_dirs[0]
                elif self.steps % 3 == 0:
                    # Si bloqué, essayer une direction aléatoire
                    all_dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                    valid_dirs = [d for d in all_dirs if self.can_move(d, maze)]
                    if valid_dirs:
                        self.direction = random.choice(valid_dirs)
            else:
                # Comportement normal pour les autres fantômes : changer de direction moins souvent
                if self.steps % 8 == 0 or not self.can_move(self.direction, maze):
                    possible_dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                    # Éviter de revenir en arrière
                    opposite = (-self.direction[0], -self.direction[1])
                    possible_dirs = [d for d in possible_dirs if d != opposite]
                    
                    valid_dirs = [d for d in possible_dirs if self.can_move(d, maze)]
                    if valid_dirs:
                        self.direction = random.choice(valid_dirs)
                    elif self.can_move(self.direction, maze):
                        pass  # Garder la direction actuelle
                    else:
                        self.direction = random.choice(possible_dirs)
        
        # Les yeux peuvent traverser les murs, les autres non
        # Les fantômes rouges sont 2 fois moins rapides (ne se déplacent qu'une fois sur deux)
        if self.eyes or self.can_move(self.direction, maze):
            # Si c'est un fantôme rouge, ne se déplacer qu'une fois sur deux frames
            if self.color == RED and self.steps % 2 != 0:
                pass  # Ne pas se déplacer cette frame
            else:
                self.x += self.direction[0]
                self.y += self.direction[1]
                # Téléportation aux bords
                if self.x < 0:
                    self.x = GRID_WIDTH - 1
                elif self.x >= GRID_WIDTH:
                    self.x = 0
            # Pour les yeux, s'assurer qu'ils restent dans les limites verticales
            if self.eyes:
                if self.y < 0:
                    self.y = 0
                elif self.y >= GRID_HEIGHT:
                    self.y = GRID_HEIGHT - 1
    
    def can_move(self, direction, maze):
        new_x = self.x + direction[0]
        new_y = self.y + direction[1]
        
        # Téléportation aux bords
        if new_x < 0 or new_x >= GRID_WIDTH:
            return True
        
        if new_y < 0 or new_y >= GRID_HEIGHT:
            return False
        
        return maze[new_y][new_x] != 1
    
    def draw(self, screen):
        center_x = self.x * CELL_SIZE + CELL_SIZE // 2
        center_y = self.y * CELL_SIZE + CELL_SIZE // 2
        radius = CELL_SIZE // 2 - 2
        
        # Si en mode yeux, dessiner seulement les yeux
        if self.eyes:
            # Yeux seulement (plus grands pour être visibles)
            pygame.draw.circle(screen, WHITE, (center_x - 5, center_y), 4)
            pygame.draw.circle(screen, WHITE, (center_x + 5, center_y), 4)
            pygame.draw.circle(screen, BLACK, (center_x - 5, center_y), 2)
            pygame.draw.circle(screen, BLACK, (center_x + 5, center_y), 2)
        else:
            # Choisir la couleur selon l'état
            if self.vulnerable:
                ghost_color = BLUE
            elif self.returning:
                ghost_color = WHITE
            else:
                ghost_color = self.color
            
            # Corps du fantôme
            pygame.draw.circle(screen, ghost_color, (center_x, center_y), radius)
            # Rectangle pour la partie inférieure
            pygame.draw.rect(screen, ghost_color, 
                            (center_x - radius, center_y, radius * 2, radius))
            
            # Yeux (seulement si pas vulnérable ou retournant)
            if not self.vulnerable or self.returning:
                pygame.draw.circle(screen, WHITE, (center_x - 5, center_y - 3), 3)
                pygame.draw.circle(screen, WHITE, (center_x + 5, center_y - 3), 3)
                pygame.draw.circle(screen, BLACK, (center_x - 5, center_y - 3), 1)
                pygame.draw.circle(screen, BLACK, (center_x + 5, center_y - 3), 1)



def draw_maze(screen, maze, ice_tiles=None, fire_tiles=None, is_adventure_mode=False):
    if ice_tiles is None:
        ice_tiles = {}
    if fire_tiles is None:
        fire_tiles = {}
    
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if maze[y][x] == 1:
                pygame.draw.rect(screen, DARK_BLUE, rect)
            elif maze[y][x] == 2:
                # Dessiner un point (sauf en mode aventure)
                if not is_adventure_mode:
                    center_x = x * CELL_SIZE + CELL_SIZE // 2
                    center_y = y * CELL_SIZE + CELL_SIZE // 2
                    pygame.draw.circle(screen, YELLOW, (center_x, center_y), 2)
            elif maze[y][x] == 3:
                # Dessiner une pacgomme (toujours visible, même en mode aventure)
                center_x = x * CELL_SIZE + CELL_SIZE // 2
                center_y = y * CELL_SIZE + CELL_SIZE // 2
                pygame.draw.circle(screen, YELLOW, (center_x, center_y), 6)
            
            # Dessiner les cases de feu (avant la glace pour que le feu soit visible)
            if (x, y) in fire_tiles:
                # Dessiner une case de feu (rouge-orange avec effet de flammes)
                fire_color = (255, 69, 0)  # Rouge-orange
                pygame.draw.rect(screen, fire_color, rect)
                # Dessiner des flammes animées
                center_x = x * CELL_SIZE + CELL_SIZE // 2
                center_y = y * CELL_SIZE + CELL_SIZE // 2
                # Flamme principale
                flame_points = [
                    (center_x, rect.top + 2),
                    (rect.left + 3, center_y),
                    (center_x, rect.bottom - 2),
                    (rect.right - 3, center_y),
                ]
                pygame.draw.polygon(screen, (255, 140, 0), flame_points)
                # Flamme intérieure
                inner_flame_points = [
                    (center_x, rect.top + 4),
                    (rect.left + 6, center_y),
                    (center_x, rect.bottom - 4),
                    (rect.right - 6, center_y),
                ]
                pygame.draw.polygon(screen, (255, 255, 0), inner_flame_points)
            
            # Dessiner les cases de glace
            if (x, y) in ice_tiles:
                # Dessiner une case de glace (violet avec effet gelé)
                ice_color = (148, 0, 211)  # Violet
                pygame.draw.rect(screen, ice_color, rect)
                # Dessiner un motif de glace (lignes blanches)
                pygame.draw.line(screen, (255, 255, 255), 
                               (rect.left, rect.top + CELL_SIZE // 2), 
                               (rect.right, rect.top + CELL_SIZE // 2), 1)
                pygame.draw.line(screen, (255, 255, 255), 
                               (rect.left + CELL_SIZE // 2, rect.top), 
                               (rect.left + CELL_SIZE // 2, rect.bottom), 1)
                # Dessiner des petits cristaux de glace
                for i in range(3):
                    for j in range(3):
                        if (i + j) % 2 == 0:
                            crystal_x = rect.left + i * CELL_SIZE // 3 + CELL_SIZE // 6
                            crystal_y = rect.top + j * CELL_SIZE // 3 + CELL_SIZE // 6
                            pygame.draw.circle(screen, (255, 255, 255), (crystal_x, crystal_y), 2)

def count_points(maze):
    count = 0
    for row in maze:
        count += row.count(2)  # Points normaux
        count += row.count(3)  # Pacgommes
    return count

def get_most_common_ghost_color(ghosts, level):
    """Détermine la couleur de fantôme la plus courante dans le niveau"""
    # Compter les couleurs des fantômes normaux (pas les inoffensifs)
    color_counts = {}
    for ghost in ghosts:
        if not ghost.harmless:
            color = ghost.color
            color_counts[color] = color_counts.get(color, 0) + 1
    
    # Si on a des fantômes, retourner la couleur la plus fréquente
    if color_counts:
        return max(color_counts, key=color_counts.get)
    
    # Sinon, déterminer la couleur selon le niveau
    ORANGE = (255, 165, 0)
    ROSE = (255, 192, 203)
    
    if level <= 6:
        return BLUE
    elif level <= 10:
        return ORANGE
    elif level <= 14:
        return ROSE
    else:
        return RED

def start_next_level(level, is_adventure_mode=False):
    """Initialise le niveau suivant avec un labyrinthe différent"""
    # Choisir un labyrinthe différent selon le niveau (rotation entre les 100 labyrinthes)
    maze_index = (level - 1) % len(MAZES)
    selected_maze = MAZES[maze_index]
    maze = [row[:] for row in selected_maze]
    pacman = Pacman(10, 15)
    # Augmenter le nombre de fantômes selon le niveau
    # Niveaux 1-2: 1 fantôme bleu
    # Niveaux 3-4: 2 fantômes bleus
    # Niveaux 5-6: 1 fantôme bleu, 1 fantôme orange
    # Niveaux 7-8: 2 fantômes orange
    # Niveaux 9-10: 1 fantôme orange, 1 fantôme rose
    # Niveaux 11-12: 2 fantômes roses
    # Niveaux 13-14: 1 fantôme rose, 1 fantôme rouge
    # Niveaux 15-16: 2 fantômes rouges
    ghosts = []
    ORANGE = (255, 165, 0)
    ROSE = (255, 192, 203)
    VIOLET = (148, 0, 211)  # Violet pour le fantôme spécial au niveau 5 en mode aventure
    
    if level <= 2:
        # Niveaux 1-2: 1 fantôme bleu
        num_ghosts = 1
        for i in range(num_ghosts):
            ghosts.append(Ghost(10 + i, 9, BLUE))
    elif level <= 4:
        # Niveaux 3-4: 2 fantômes bleus
        num_ghosts = 2
        for i in range(num_ghosts):
            ghosts.append(Ghost(10 + i, 9, BLUE))
    elif level <= 6:
        # Niveaux 5-6: 1 fantôme bleu, 1 fantôme orange
        # En mode aventure niveau 5: remplacer le fantôme orange par un fantôme violet spécial (nécessite 2 coups)
        num_ghosts = 2
        ghosts.append(Ghost(10, 9, BLUE))
        if is_adventure_mode and level == 5:
            # Fantôme violet spécial au niveau 5 en mode aventure (nécessite 2 coups)
            ghosts.append(Ghost(11, 9, VIOLET, harmless=False, hits_required=2))
        else:
            ghosts.append(Ghost(11, 9, ORANGE))
    elif level <= 8:
        # Niveaux 7-8: 2 fantômes orange
        num_ghosts = 2
        for i in range(num_ghosts):
            ghosts.append(Ghost(10 + i, 9, ORANGE))
    elif level <= 10:
        # Niveaux 9-10: 1 fantôme orange, 1 fantôme rose
        num_ghosts = 2
        ghosts.append(Ghost(10, 9, ORANGE))
        ghosts.append(Ghost(11, 9, ROSE))
    elif level <= 12:
        # Niveaux 11-12: 2 fantômes roses
        num_ghosts = 2
        for i in range(num_ghosts):
            ghosts.append(Ghost(10 + i, 9, ROSE))
    elif level <= 14:
        # Niveaux 13-14: 1 fantôme rose, 1 fantôme rouge
        num_ghosts = 2
        ghosts.append(Ghost(10, 9, ROSE))
        ghosts.append(Ghost(11, 9, RED))
    elif level <= 16:
        # Niveaux 15-16: 2 fantômes rouges
        num_ghosts = 2
        for i in range(num_ghosts):
            ghosts.append(Ghost(10 + i, 9, RED))
    else:
        # Niveaux 17+: 2 fantômes rouges (par défaut)
        num_ghosts = 2
        for i in range(num_ghosts):
            ghosts.append(Ghost(10 + i, 9, RED))
    
    # Définir le chemin pour tous les fantômes bleus
    for ghost in ghosts:
        if ghost.color == BLUE:
            ghost.set_path(maze)
    
    return maze, pacman, ghosts

def calculate_invincibilite_bonus(capacite_items, inventaire_items):
    """Calcule le bonus d'invincibilité selon le niveau de la capacité équipée"""
    invincibilite_level = capacite_items.count("invincibilité") if capacite_items else 0
    has_invincibilite_capacity = (('capacite1' in inventaire_items and inventaire_items['capacite1'].get('type') == 'invincibilité') or
                                 ('capacite2' in inventaire_items and inventaire_items['capacite2'].get('type') == 'invincibilité'))
    return invincibilite_level * 10 if has_invincibilite_capacity else 0  # 1 seconde = 10 frames par niveau

def calculate_armor_lives_bonus(inventaire_items):
    """Calcule le bonus de vies selon les armures équipées (grosse armure et armure de fer)"""
    has_grosse_armure = (('objet0' in inventaire_items and inventaire_items['objet0'].get('type') == 'grosse armure') or
                         ('objet1' in inventaire_items and inventaire_items['objet1'].get('type') == 'grosse armure') or
                         ('objet2' in inventaire_items and inventaire_items['objet2'].get('type') == 'grosse armure'))
    has_armure_fer = (('objet0' in inventaire_items and inventaire_items['objet0'].get('type') == 'armure de fer') or
                      ('objet1' in inventaire_items and inventaire_items['objet1'].get('type') == 'armure de fer') or
                      ('objet2' in inventaire_items and inventaire_items['objet2'].get('type') == 'armure de fer'))
    # Chaque type d'armure donne +1 coeur ; si les deux sont équipées, cela fait donc +2 coeurs
    return (1 if has_grosse_armure else 0) + (1 if has_armure_fer else 0)

def get_equipped_gadget(inventaire_items):
    """Retourne le gadget équipé dans gadget, ou None si aucun n'est équipé"""
    if 'gadget' in inventaire_items:
        return inventaire_items['gadget']
    return None

def calculate_fire_duration(inventaire_items, base_duration=100):
    """Calcule la durée du feu selon si 'flamme' est équipé. Augmente de 50% si équipé."""
    has_flamme = (('objet0' in inventaire_items and inventaire_items['objet0'].get('type') == 'flamme') or
                  ('objet1' in inventaire_items and inventaire_items['objet1'].get('type') == 'flamme') or
                  ('objet2' in inventaire_items and inventaire_items['objet2'].get('type') == 'flamme'))
    if has_flamme:
        return int(base_duration * 1.5)  # +50% de durée
    return base_duration

def has_double_gadget_equipped(inventaire_items):
    """Vérifie si 'double gadget' est équipé dans les slots objet."""
    return (('objet0' in inventaire_items and inventaire_items['objet0'].get('type') == 'double gadget') or
            ('objet1' in inventaire_items and inventaire_items['objet1'].get('type') == 'double gadget') or
            ('objet2' in inventaire_items and inventaire_items['objet2'].get('type') == 'double gadget'))

def respawn_player_and_ghosts(pacman, ghosts, invincibilite_bonus=0):
    """Réinitialise les positions de Pacman et des fantômes après perte de vie"""
    pacman = Pacman(10, 15)
    for ghost in ghosts:
        ghost.x = ghost.start_x
        ghost.y = ghost.start_y
        ghost.vulnerable = False
        ghost.returning = False
        ghost.eyes = False
        ghost.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
    return pacman, 30 + invincibilite_bonus  # Retourner aussi le timer d'invincibilité (3 secondes + bonus)

def start_game_with_difficulty(difficulty, inventaire_items, capacite_items, invincibilite_bonus, ghosts):
    """Démarre la partie selon la difficulté choisie"""
    # Supprimer le fantôme d'indigestion s'il existe
    ghosts[:] = [ghost for ghost in ghosts if not ghost.harmless]
    has_indigestion = False
    indigestion_timer = 0
    
    if difficulty == "facile":
        # Facile : niveau 1 avec 5 vies
        maze, pacman, ghosts = start_next_level(1)
        armor_lives_bonus_init = calculate_armor_lives_bonus(inventaire_items)
        lives = 5 + armor_lives_bonus_init
    elif difficulty == "moyen":
        # Moyen : niveau 3 avec un fantôme bleu supplémentaire
        maze, pacman, ghosts = start_next_level(3)
        # Ajouter un fantôme bleu supplémentaire pour le mode moyen
        new_ghost = Ghost(11, 9, BLUE)
        ghosts.append(new_ghost)
        new_ghost.set_path(maze)
        armor_lives_bonus_init = calculate_armor_lives_bonus(inventaire_items)
        lives = 2 + armor_lives_bonus_init
    elif difficulty == "difficile":
        # Difficile : niveau 1 avec 1 vie
        maze, pacman, ghosts = start_next_level(1)
        armor_lives_bonus_init = calculate_armor_lives_bonus(inventaire_items)
        lives = 1 + armor_lives_bonus_init
    elif difficulty == "hardcore":
        # Hardcore : niveau 5 avec 1 vie
        maze, pacman, ghosts = start_next_level(5)
        armor_lives_bonus_init = calculate_armor_lives_bonus(inventaire_items)
        lives = 1 + armor_lives_bonus_init
    else:
        # Par défaut : facile
        maze, pacman, ghosts = start_next_level(1)
        armor_lives_bonus_init = calculate_armor_lives_bonus(inventaire_items)
        lives = 2 + armor_lives_bonus_init
    
    # Initialisations communes
    score = 0
    last_bonus_score = 0
    game_over = False
    won = False
    ice_tiles = {}
    pacman_last_pos = (pacman.x, pacman.y)
    vulnerable_timer = 0
    level_transition = False
    level_transition_timer = 0
    respawn_timer = 0
    invincibility_timer = 30 + invincibilite_bonus
    crown_timer = 0
    crown_count = 0
    jeton_count = 0
    last_ghost_time = 0
    fire_tiles = {}
    fire_active = False
    fire_timer = 0
    gadget_cooldown = 0
    mort_cooldown = 0
    bombe_cooldown = 0
    bombe_active = False
    pieges = {}
    portal1_pos = None
    portal2_pos = None
    portal_use_count = 0
    mur_pos = None
    mur_use_count = 0
    gadget_use_count = 0
    
    # Retourner toutes les variables initialisées
    return (maze, pacman, ghosts, score, lives, last_bonus_score, game_over, won,
            ice_tiles, pacman_last_pos, vulnerable_timer, level_transition, level_transition_timer,
            respawn_timer, invincibility_timer, crown_timer, crown_count, jeton_count, last_ghost_time,
            fire_tiles, fire_active, fire_timer, gadget_cooldown, mort_cooldown, bombe_cooldown,
            bombe_active, pieges, portal1_pos, portal2_pos, portal_use_count, mur_pos, mur_use_count,
            gadget_use_count, has_indigestion, indigestion_timer)

def draw_delete_confirmation(screen, step=1, account_name=""):
    """Dessine la boîte de dialogue de confirmation de suppression"""
    # Fond semi-transparent
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    overlay.set_alpha(180)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    
    # Boîte de dialogue
    dialog_width = 500
    dialog_height = 200
    dialog_x = (WINDOW_WIDTH - dialog_width) // 2
    dialog_y = (WINDOW_HEIGHT - dialog_height) // 2
    dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
    
    # Fond de la boîte
    pygame.draw.rect(screen, (50, 50, 50), dialog_rect)
    pygame.draw.rect(screen, WHITE, dialog_rect, 3)
    
    # Texte de la question
    font_question = pygame.font.Font(None, 36)
    if step == 1:
        question_text = font_question.render("Voulez-vous supprimer ce compte ?", True, WHITE)
    else:
        question_text = font_question.render("Vous allez supprimer ce compte", True, WHITE)
    question_rect = question_text.get_rect(center=(dialog_x + dialog_width // 2, dialog_y + 50))
    screen.blit(question_text, question_rect)
    
    # Nom du compte
    if account_name:
        font_name = pygame.font.Font(None, 28)
        name_text = font_name.render(f"({account_name})", True, YELLOW)
        name_rect = name_text.get_rect(center=(dialog_x + dialog_width // 2, dialog_y + 90))
        screen.blit(name_text, name_rect)
    
    # Boutons Oui et Non
    button_width = 100
    button_height = 40
    button_spacing = 20
    
    # OUI toujours à droite, NON toujours à gauche
    non_button = pygame.Rect(dialog_x + dialog_width // 2 - button_width - button_spacing // 2, dialog_y + 130, button_width, button_height)
    oui_button = pygame.Rect(dialog_x + dialog_width // 2 + button_spacing // 2, dialog_y + 130, button_width, button_height)
    
    # Bouton Oui (rouge)
    pygame.draw.rect(screen, RED, oui_button)
    pygame.draw.rect(screen, WHITE, oui_button, 2)
    font_button = pygame.font.Font(None, 32)
    oui_text = font_button.render("OUI", True, WHITE)
    oui_text_rect = oui_text.get_rect(center=oui_button.center)
    screen.blit(oui_text, oui_text_rect)
    
    # Bouton Non (vert)
    pygame.draw.rect(screen, (0, 150, 0), non_button)
    pygame.draw.rect(screen, WHITE, non_button, 2)
    non_text = font_button.render("NON", True, WHITE)
    non_text_rect = non_text.get_rect(center=non_button.center)
    screen.blit(non_text, non_text_rect)
    
    return oui_button, non_button

def draw_start_menu(screen, accounts=None, current_account_index=None, scroll_offset=0):
    """Dessine l'écran de démarrage avec les comptes créés et un bouton +"""
    if accounts is None:
        accounts = []
    
    screen.fill(BLACK)
    
    # Afficher le compteur de trophées total en haut de l'écran
    # Compter tous les trophées uniques gagnés (chaque trophée ne peut être gagné qu'une fois)
    all_trophies = set()
    for account in accounts:
        for trophy in account.get('trophies', []):
            all_trophies.add(trophy)
    total_trophies = len(all_trophies)
    font_trophy_header = pygame.font.Font(None, 48)
    trophy_header_text = font_trophy_header.render(f"Trophées: {total_trophies}/{TOTAL_TROPHY_COUNT}", True, YELLOW)
    trophy_header_rect = trophy_header_text.get_rect(center=(WINDOW_WIDTH//2, 30))
    screen.blit(trophy_header_text, trophy_header_rect)
    
    
    # Afficher tous les comptes créés en haut à gauche, les uns après les autres
    profile_rects = []  # Liste des rectangles cliquables pour chaque compte
    start_x = 50
    start_y = 120  # Décaler vers le bas pour laisser de la place au bouton
    circle_radius = 50
    spacing = 120  # Espacement horizontal entre les comptes
    line_height = circle_radius * 2 + 80  # Hauteur d'une ligne (cercle + nom + espacement)
    
    current_x = start_x
    current_y = start_y
    
    for i, account in enumerate(accounts):
        if account.get('player_name') and account.get('selected_avatar') and account.get('selected_font'):
            # Vérifier si le compte dépasse de l'écran par la droite
            if current_x + circle_radius * 2 > WINDOW_WIDTH - 20:
                # Passer à la ligne suivante
                current_x = start_x
                current_y += line_height
            
            profile_x = current_x
            profile_y = current_y - scroll_offset
            circle_x = profile_x + circle_radius
            circle_y = profile_y + circle_radius
            
            # Charger l'image de police pour le fond du cercle
            selected_font = account.get('selected_font')
            font_image = load_font_surface(selected_font)
            
            # Créer une surface pour le cercle avec transparence
            circle_surface = pygame.Surface((circle_radius * 2, circle_radius * 2), pygame.SRCALPHA)
            
            # Si une police est sélectionnée, utiliser l'image comme texture
            if font_image:
                font_texture = pygame.transform.scale(font_image, (circle_radius * 2, circle_radius * 2))
                mask = pygame.Surface((circle_radius * 2, circle_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(mask, (255, 255, 255, 255), (circle_radius, circle_radius), circle_radius)
                circle_surface.blit(font_texture, (0, 0))
                circle_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            else:
                pygame.draw.circle(circle_surface, YELLOW, (circle_radius, circle_radius), circle_radius)
            
            # Dessiner le cercle sur l'écran
            screen.blit(circle_surface, (circle_x - circle_radius, circle_y - circle_radius))
            
            # Dessiner la bordure blanche (jaune si c'est le compte actuel)
            border_color = YELLOW if (current_account_index is not None and i == current_account_index) else WHITE
            border_width = 4 if (current_account_index is not None and i == current_account_index) else 2
            pygame.draw.circle(screen, border_color, (circle_x, circle_y), circle_radius, border_width)
            
            # Afficher l'avatar à l'intérieur du cercle
            avatar_image = None
            selected_avatar = account.get('selected_avatar')
            if selected_avatar == "avatar1":
                avatar_paths = ["fatome_epee.png", "avatar.png", "image-t26edcoUjiXQ72uQKAB3R(2).png", "avatar.jpg", "avatar.jpeg"]
            elif selected_avatar == "avatar2":
                # Utiliser le deuxième font comme avatar2
                second_font = get_second_font()
                avatar_paths = [second_font] if second_font else []
            elif selected_avatar == "avatar3":
                avatar_paths = ["image-1uA5ykn6ZPDhIyRHwCxym.webp"]
            elif selected_avatar == "avatar4":
                avatar_paths = ["le_super_67.webp"]
            else:
                avatar_paths = []
            
            for path in avatar_paths:
                if os.path.exists(path):
                    try:
                        avatar_image = pygame.image.load(path)
                        break
                    except:
                        continue
            
            if avatar_image:
                avatar_size = int(circle_radius * 1.6)
                avatar_image = pygame.transform.scale(avatar_image, (avatar_size, avatar_size))
                avatar_x = circle_x - avatar_size // 2
                avatar_y = circle_y - avatar_size // 2
                screen.blit(avatar_image, (avatar_x, avatar_y))
            
            # Afficher le nom en dessous du cercle
            font_name = pygame.font.Font(None, 36)
            name_text = font_name.render(account.get('player_name', ''), True, WHITE)
            name_x = circle_x - name_text.get_width() // 2
            name_y = circle_y + circle_radius + 10
            
            # Créer un rectangle cliquable autour du profil
            rect_padding = 20
            profile_rect = pygame.Rect(
                circle_x - circle_radius - rect_padding,
                circle_y - circle_radius - rect_padding,
                circle_radius * 2 + rect_padding * 2,
                circle_radius * 2 + rect_padding * 2 + 50
            )
            profile_rects.append(("profile", profile_rect, i))  # Stocker l'index du compte avec le rectangle
            
            screen.blit(name_text, (name_x, name_y))
            
            # Mettre à jour la position pour le prochain compte
            current_x += spacing
    
    # Bouton "+" après le dernier compte (ou au début si aucun compte)
    plus_button = None
    font_button = pygame.font.Font(None, 120)
    button_size = 100
    
    if len(accounts) > 0:
        # Positionner le bouton "+" après le dernier compte
        plus_x = current_x
        plus_y = current_y
        
        # Vérifier si le bouton dépasse de l'écran
        if plus_x + button_size > WINDOW_WIDTH - 20:
            # Passer à la ligne suivante
            plus_x = start_x
            plus_y += line_height
    else:
        # Si aucun compte, positionner le bouton "+" au début
        plus_x = start_x
        plus_y = start_y
    
    # Calculer la hauteur totale du contenu (après avoir déterminé la position finale du bouton "+")
    total_height = plus_y + line_height
    
    # Appliquer le scroll_offset au bouton "+"
    plus_y_display = plus_y - scroll_offset
    
    plus_button = pygame.Rect(plus_x, plus_y_display, button_size, button_size)
    pygame.draw.rect(screen, YELLOW, plus_button)
    pygame.draw.rect(screen, WHITE, plus_button, 3)
    
    plus_text = font_button.render("+", True, BLACK)
    plus_text_rect = plus_text.get_rect(center=plus_button.center)
    screen.blit(plus_text, plus_text_rect)
    
    return plus_button, profile_rects, total_height

def draw_skill_tree_menu(screen):
    """Dessine le menu de l'arbre des trophées"""
    screen.fill(BLACK)
    
    # Titre sur 2 lignes
    font_title = pygame.font.Font(None, 72)
    title_text1 = font_title.render("ARBRE DES", True, YELLOW)
    title_text2 = font_title.render("TROPHÉES", True, YELLOW)
    title_rect1 = title_text1.get_rect(center=(WINDOW_WIDTH//2, 60))
    title_rect2 = title_text2.get_rect(center=(WINDOW_WIDTH//2, 100))
    screen.blit(title_text1, title_rect1)
    screen.blit(title_text2, title_rect2)
    
    # Bouton retour
    retour_button = pygame.Rect(10, 10, 100, 40)
    pygame.draw.rect(screen, RED, retour_button)
    pygame.draw.rect(screen, WHITE, retour_button, 2)
    font_retour = pygame.font.Font(None, 36)
    retour_text = font_retour.render("RETOUR", True, WHITE)
    retour_text_rect = retour_text.get_rect(center=retour_button.center)
    screen.blit(retour_text, retour_text_rect)
    
    # Boutons "Survie" et "Équipement"
    font_button = pygame.font.Font(None, 48)
    button_width = 200
    button_height = 60
    button_spacing = 30
    total_buttons_width = (button_width * 2) + button_spacing
    start_x = (WINDOW_WIDTH - total_buttons_width) // 2
    
    # Bouton "Survie"
    survie_button = pygame.Rect(start_x, WINDOW_HEIGHT//2 - button_height//2, button_width, button_height)
    pygame.draw.rect(screen, (0, 150, 0), survie_button)  # Vert foncé
    pygame.draw.rect(screen, WHITE, survie_button, 3)
    survie_text = font_button.render("Survie", True, WHITE)
    survie_text_rect = survie_text.get_rect(center=survie_button.center)
    screen.blit(survie_text, survie_text_rect)
    
    # Bouton "Équipement"
    equipement_button = pygame.Rect(start_x + button_width + button_spacing, WINDOW_HEIGHT//2 - button_height//2, button_width, button_height)
    pygame.draw.rect(screen, (150, 100, 0), equipement_button)  # Orange
    pygame.draw.rect(screen, WHITE, equipement_button, 3)
    equipement_text = font_button.render("Équipement", True, WHITE)
    equipement_text_rect = equipement_text.get_rect(center=equipement_button.center)
    screen.blit(equipement_text, equipement_text_rect)
    
    return retour_button, survie_button, equipement_button

def draw_survie_skill_tree_menu(screen, unlocked_trophies=None):
    """Dessine l'arbre de trophée de survie (style Minecraft)"""
    if unlocked_trophies is None:
        unlocked_trophies = []
    
    screen.fill(BLACK)
    
    # Titre
    font_title = pygame.font.Font(None, 72)
    title_text = font_title.render("ARBRE DE TROPHÉE - SURVIE", True, YELLOW)
    title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, 40))
    screen.blit(title_text, title_rect)
    
    # Bouton retour
    retour_button = pygame.Rect(10, 10, 100, 40)
    pygame.draw.rect(screen, RED, retour_button)
    pygame.draw.rect(screen, WHITE, retour_button, 2)
    font_retour = pygame.font.Font(None, 36)
    retour_text = font_retour.render("RETOUR", True, WHITE)
    retour_text_rect = retour_text.get_rect(center=retour_button.center)
    screen.blit(retour_text, retour_text_rect)
    
    # Zone de l'arbre (avec décalage pour le titre)
    tree_area_y = 100
    tree_area_height = WINDOW_HEIGHT - tree_area_y - 20
    
    # Dessiner les connexions entre les trophées (lignes)
    for trophy_id, trophy_data in SURVIVAL_TROPHY_TREE.items():
        trophy_pos = trophy_data["position"]
        parents = trophy_data["parents"]
        
        for parent_id in parents:
            if parent_id in SURVIVAL_TROPHY_TREE:
                parent_pos = SURVIVAL_TROPHY_TREE[parent_id]["position"]
                
                # Vérifier si le parent est débloqué pour déterminer la couleur de la ligne
                parent_unlocked = parent_id in unlocked_trophies
                line_color = (100, 200, 100) if parent_unlocked else (80, 80, 80)  # Vert si débloqué, gris sinon
                
                # Dessiner la ligne de connexion
                pygame.draw.line(screen, line_color, parent_pos, trophy_pos, 3)
    
    # Dessiner les trophées
    trophy_rects = {}
    trophy_size = 50
    
    for trophy_id, trophy_data in SURVIVAL_TROPHY_TREE.items():
        trophy_pos = trophy_data["position"]
        is_unlocked = trophy_id in unlocked_trophies
        
        # Vérifier si tous les parents sont débloqués (pour déterminer si accessible)
        parents_unlocked = all(parent_id in unlocked_trophies for parent_id in trophy_data["parents"])
        is_accessible = len(trophy_data["parents"]) == 0 or parents_unlocked
        
        # Couleur du trophée
        if is_unlocked:
            trophy_color = (255, 215, 0)  # Or pour débloqué
            border_color = (255, 255, 0)  # Jaune vif
        elif is_accessible:
            trophy_color = (150, 150, 150)  # Gris clair pour accessible mais non débloqué
            border_color = (200, 200, 200)
        else:
            trophy_color = (60, 60, 60)  # Gris foncé pour verrouillé
            border_color = (100, 100, 100)
        
        # Dessiner le cercle du trophée
        trophy_rect = pygame.Rect(trophy_pos[0] - trophy_size//2, trophy_pos[1] - trophy_size//2, trophy_size, trophy_size)
        pygame.draw.circle(screen, trophy_color, trophy_pos, trophy_size//2)
        pygame.draw.circle(screen, border_color, trophy_pos, trophy_size//2, 3)
        
        # Dessiner une icône simple (étoile ou cercle)
        if is_unlocked:
            # Étoile pour trophée débloqué
            star_points = []
            for i in range(5):
                angle = (i * 2 * math.pi / 5) - math.pi / 2
                outer_x = trophy_pos[0] + int((trophy_size//2 - 5) * math.cos(angle))
                outer_y = trophy_pos[1] + int((trophy_size//2 - 5) * math.sin(angle))
                star_points.append((outer_x, outer_y))
            pygame.draw.polygon(screen, (255, 255, 255), star_points)
        else:
            # Cercle simple pour trophée non débloqué
            pygame.draw.circle(screen, (100, 100, 100), trophy_pos, trophy_size//4)
        
        # Stocker le rectangle pour les interactions
        trophy_rects[trophy_id] = trophy_rect
        
        # Afficher le nom du trophée en dessous
        font_name = pygame.font.Font(None, 20)
        name_text = font_name.render(trophy_data["name"], True, WHITE if is_unlocked else (150, 150, 150))
        name_rect = name_text.get_rect(center=(trophy_pos[0], trophy_pos[1] + trophy_size//2 + 15))
        screen.blit(name_text, name_rect)
    
    # Afficher la description du trophée survolé (si nécessaire, peut être ajouté plus tard)
    # Pour l'instant, affichons un message d'aide en bas
    font_help = pygame.font.Font(None, 24)
    help_text = font_help.render("Les trophées dorés sont débloqués, les gris sont verrouillés", True, (150, 150, 150))
    help_rect = help_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT - 30))
    screen.blit(help_text, help_rect)
    
    return retour_button, trophy_rects

def draw_equipement_skill_tree_menu(screen):
    """Dessine l'arbre de trophée d'équipement"""
    screen.fill(BLACK)
    
    # Titre
    font_title = pygame.font.Font(None, 72)
    title_text = font_title.render("ARBRE DE TROPHÉE - ÉQUIPEMENT", True, YELLOW)
    title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, 80))
    screen.blit(title_text, title_rect)
    
    # Bouton retour
    retour_button = pygame.Rect(10, 10, 100, 40)
    pygame.draw.rect(screen, RED, retour_button)
    pygame.draw.rect(screen, WHITE, retour_button, 2)
    font_retour = pygame.font.Font(None, 36)
    retour_text = font_retour.render("RETOUR", True, WHITE)
    retour_text_rect = retour_text.get_rect(center=retour_button.center)
    screen.blit(retour_text, retour_text_rect)
    
    # Première formule : "Mieux gagner niveau 1"
    font_formula = pygame.font.Font(None, 48)
    formula_y = 200
    formula_text = font_formula.render("Mieux gagner niveau 1", True, WHITE)
    formula_rect = formula_text.get_rect(center=(WINDOW_WIDTH//2, formula_y))
    screen.blit(formula_text, formula_rect)
    
    # Zone pour l'arbre de trophée (à développer plus tard)
    skill_area = pygame.Rect(50, formula_y + 60, WINDOW_WIDTH - 100, WINDOW_HEIGHT - formula_y - 120)
    pygame.draw.rect(screen, (30, 30, 30), skill_area)
    pygame.draw.rect(screen, WHITE, skill_area, 2)
    
    # Message informatif
    font_info = pygame.font.Font(None, 32)
    info_text = font_info.render("Arbre de trophée d'équipement - À développer", True, (150, 150, 150))
    info_rect = info_text.get_rect(center=(WINDOW_WIDTH//2, skill_area.centery))
    screen.blit(info_text, info_rect)
    
    return retour_button

def draw_aventure_menu(screen):
    """Dessine le menu d'aventure"""
    screen.fill(BLACK)
    
    # Titre
    font_title = pygame.font.Font(None, 72)
    title_text = font_title.render("AVENTURE", True, YELLOW)
    title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, 80))
    screen.blit(title_text, title_rect)
    
    # Bouton retour
    retour_button = pygame.Rect(10, 10, 100, 40)
    pygame.draw.rect(screen, RED, retour_button)
    pygame.draw.rect(screen, WHITE, retour_button, 2)
    font_retour = pygame.font.Font(None, 36)
    retour_text = font_retour.render("RETOUR", True, WHITE)
    retour_text_rect = retour_text.get_rect(center=retour_button.center)
    screen.blit(retour_text, retour_text_rect)
    
    # Bouton pour démarrer la carte 1
    font_button = pygame.font.Font(None, 48)
    button_width = 250
    button_height = 60
    carte1_button = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, WINDOW_HEIGHT//2 - button_height//2, button_width, button_height)
    pygame.draw.rect(screen, (0, 150, 255), carte1_button)  # Bleu
    pygame.draw.rect(screen, WHITE, carte1_button, 3)
    carte1_text = font_button.render("CARTE 1", True, WHITE)
    carte1_text_rect = carte1_text.get_rect(center=carte1_button.center)
    screen.blit(carte1_text, carte1_text_rect)
    
    # Afficher les paramètres de l'aventure
    font_info = pygame.font.Font(None, 28)
    info_text = font_info.render("3 vies | 0 couronnes | 0 pacoins", True, (150, 150, 150))
    info_rect = info_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 80))
    screen.blit(info_text, info_rect)
    
    return retour_button, carte1_button

def draw_reward_animation(screen, reward_animations):
    """Dessine les animations de récompenses"""
    for anim in reward_animations[:]:  # Copie de la liste pour éviter les problèmes de modification
        # Calculer la position (animation vers le haut)
        y_offset = anim['timer'] * 2  # Se déplace vers le haut
        x = anim['x']
        y = anim['y'] - y_offset
        
        # Calculer l'opacité (disparaît progressivement)
        max_timer = 180  # 3 secondes à 60 FPS
        alpha = max(0, 255 - (anim['timer'] * 255 // max_timer))
        
        # Couleur avec alpha
        color = anim['color']
        if alpha < 255:
            color = tuple(int(c * alpha / 255) for c in color[:3])
        
        # Taille du texte (légèrement agrandie)
        font_size = 36 + (anim['timer'] // 10)  # Grandit légèrement
        font = pygame.font.Font(None, font_size)
        
        # Dessiner le texte de la récompense
        reward_text = font.render(anim['text'], True, color)
        text_rect = reward_text.get_rect(center=(x, y))
        
        # Dessiner un fond semi-transparent pour la lisibilité
        bg_rect = text_rect.inflate(20, 10)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surface.set_alpha(alpha // 2)
        bg_surface.fill((0, 0, 0))
        screen.blit(bg_surface, bg_rect)
        
        # Dessiner le texte
        screen.blit(reward_text, text_rect)
        
        # Incrémenter le timer
        anim['timer'] += 1
        
        # Supprimer l'animation si elle est terminée
        if anim['timer'] >= max_timer:
            reward_animations.remove(anim)

def draw_star_upgrade_menu(screen, star_rarity="rare", clicks_remaining=5):
    """Dessine le menu d'amélioration d'étoile"""
    screen.fill(BLACK)
    
    # Titre
    font_title = pygame.font.Font(None, 72)
    title_text = font_title.render("AMÉLIORATION D'ÉTOILE", True, YELLOW)
    title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, 80))
    screen.blit(title_text, title_rect)
    
    # Bouton retour
    retour_button = pygame.Rect(10, 10, 100, 40)
    pygame.draw.rect(screen, RED, retour_button)
    pygame.draw.rect(screen, WHITE, retour_button, 2)
    font_retour = pygame.font.Font(None, 36)
    retour_text = font_retour.render("RETOUR", True, WHITE)
    retour_text_rect = retour_text.get_rect(center=retour_button.center)
    screen.blit(retour_text, retour_text_rect)
    
    # Dessiner l'étoile au centre de l'écran
    star_size = 150
    star_center_x = WINDOW_WIDTH // 2
    star_center_y = WINDOW_HEIGHT // 2
    
    # Couleur selon la rareté
    rarity_colors = {
        "rare": (0, 200, 0),  # Vert
        "super_rare": (0, 100, 255),  # Bleu
        "epique": (148, 0, 211),  # Violet
        "legendaire": (255, 215, 0)  # Jaune/Or
    }
    star_color = rarity_colors.get(star_rarity, (0, 200, 0))
    
    # Dessiner une grande étoile
    import math
    star_points = []
    outer_radius = star_size // 2
    inner_radius = star_size // 4
    
    for i in range(10):  # 10 points pour 5 branches
        angle = (i * math.pi / 5) - (math.pi / 2)
        if i % 2 == 0:
            # Point extérieur
            radius = outer_radius
        else:
            # Point intérieur
            radius = inner_radius
        x = star_center_x + radius * math.cos(angle)
        y = star_center_y + radius * math.sin(angle)
        star_points.append((int(x), int(y)))
    
    # Dessiner l'étoile
    pygame.draw.polygon(screen, star_color, star_points)
    pygame.draw.polygon(screen, WHITE, star_points, 3)
    
    # Afficher le nom de la rareté
    font_rarity = pygame.font.Font(None, 48)
    rarity_names = {
        "rare": "RARE",
        "super_rare": "SUPER RARE",
        "epique": "ÉPIQUE",
        "legendaire": "LÉGENDAIRE"
    }
    rarity_name = rarity_names.get(star_rarity, "RARE")
    rarity_text = font_rarity.render(rarity_name, True, star_color)
    rarity_rect = rarity_text.get_rect(center=(star_center_x, star_center_y + star_size // 2 + 40))
    screen.blit(rarity_text, rarity_rect)
    
    # Afficher les clics restants
    font_clicks = pygame.font.Font(None, 36)
    clicks_text = font_clicks.render(f"Clics restants: {clicks_remaining}", True, WHITE)
    clicks_rect = clicks_text.get_rect(center=(star_center_x, star_center_y + star_size // 2 + 90))
    screen.blit(clicks_text, clicks_rect)
    
    # Instructions
    font_instructions = pygame.font.Font(None, 28)
    if clicks_remaining > 0:
        instructions_text = font_instructions.render("Cliquez sur l'étoile pour tenter de l'améliorer", True, (150, 150, 150))
    else:
        instructions_text = font_instructions.render("Plus de clics disponibles", True, (150, 150, 150))
    instructions_rect = instructions_text.get_rect(center=(star_center_x, WINDOW_HEIGHT - 100))
    screen.blit(instructions_text, instructions_rect)
    
    # Rectangle cliquable pour l'étoile
    star_clickable_rect = pygame.Rect(star_center_x - star_size // 2, star_center_y - star_size // 2, star_size, star_size)
    
    return retour_button, star_clickable_rect

def draw_customization_menu(screen, player_name="", selected_avatar=None, selected_font=None, trophy_count=0):
    """Dessine le menu de personnalisation avec les boutons Font et Avatar"""
    screen.fill(BLACK)
    
    # Titre
    font_title = pygame.font.Font(None, 72)
    title_text = font_title.render("PERSONNALISATION", True, YELLOW)
    title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, 100))
    screen.blit(title_text, title_rect)
    
    # Rectangle de clic pour le cercle avatar (initialisé à None)
    avatar_circle_rect = None
    
    # Afficher un cercle avec le fond de police et l'avatar à l'intérieur si défini
    if player_name:
        # Zone de profil en haut à gauche
        profile_y = 200
        profile_x = 50
        
        # Dessiner un cercle avec le fond de police sélectionné
        circle_radius = 50
        circle_x = profile_x + circle_radius
        circle_y = profile_y + circle_radius
        
        # Créer un rectangle de clic pour le cercle (carré qui englobe le cercle)
        avatar_circle_rect = pygame.Rect(circle_x - circle_radius, circle_y - circle_radius, circle_radius * 2, circle_radius * 2)
        
        # Charger l'image de police pour le fond du cercle
        font_image = load_font_surface(selected_font)
        
        # Créer une surface pour le cercle avec transparence
        circle_surface = pygame.Surface((circle_radius * 2, circle_radius * 2), pygame.SRCALPHA)
        
        # Si une police est sélectionnée, utiliser l'image comme texture
        if font_image:
            # Redimensionner l'image de police pour couvrir le cercle
            font_texture = pygame.transform.scale(font_image, (circle_radius * 2, circle_radius * 2))
            # Créer un masque circulaire
            mask = pygame.Surface((circle_radius * 2, circle_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(mask, (255, 255, 255, 255), (circle_radius, circle_radius), circle_radius)
            # Appliquer l'image de police sur la surface du cercle
            circle_surface.blit(font_texture, (0, 0))
            # Appliquer le masque circulaire pour découper l'image
            circle_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        else:
            # Si pas de police, utiliser la couleur jaune par défaut
            pygame.draw.circle(circle_surface, YELLOW, (circle_radius, circle_radius), circle_radius)
        
        # Dessiner le cercle sur l'écran
        screen.blit(circle_surface, (circle_x - circle_radius, circle_y - circle_radius))
        
        # Dessiner la bordure blanche
        pygame.draw.circle(screen, WHITE, (circle_x, circle_y), circle_radius, 2)
        
        # Afficher l'avatar à l'intérieur du cercle si sélectionné
        if selected_avatar:
            avatar_image = None
            if selected_avatar == "avatar1":
                avatar_paths = ["fatome_epee.png", "avatar.png", "image-t26edcoUjiXQ72uQKAB3R(2).png", "avatar.jpg", "avatar.jpeg"]
            elif selected_avatar == "avatar2":
                # Utiliser le deuxième font comme avatar2
                second_font = get_second_font()
                avatar_paths = [second_font] if second_font else []
            elif selected_avatar == "avatar3":
                avatar_paths = ["image-1uA5ykn6ZPDhIyRHwCxym.webp"]
            elif selected_avatar == "avatar4":
                avatar_paths = ["le_super_67.webp"]
            else:
                avatar_paths = []
            
            for path in avatar_paths:
                if os.path.exists(path):
                    try:
                        avatar_image = pygame.image.load(path)
                        break
                    except:
                        continue
            
            if avatar_image:
                # Redimensionner l'avatar pour qu'il rentre dans le cercle (avec un peu de marge)
                avatar_size = int(circle_radius * 1.6)  # Légèrement plus petit que le cercle
                avatar_image = pygame.transform.scale(avatar_image, (avatar_size, avatar_size))
                # Centrer l'avatar dans le cercle
                avatar_x = circle_x - avatar_size // 2
                avatar_y = circle_y - avatar_size // 2
                screen.blit(avatar_image, (avatar_x, avatar_y))
        
        # Afficher le nom en dessous du cercle
        font_name = pygame.font.Font(None, 36)
        name_text = font_name.render(player_name, True, WHITE)
        name_x = circle_x - name_text.get_width() // 2  # Centrer le texte sous le cercle
        name_y = circle_y + circle_radius + 10
        screen.blit(name_text, (name_x, name_y))
        
        trophy_font = pygame.font.Font(None, 28)
        trophy_text = trophy_font.render(f"Trophées: {trophy_count}/{TOTAL_TROPHY_COUNT}", True, WHITE)
        trophy_x = circle_x - trophy_text.get_width() // 2
        trophy_y = name_y + 30
        screen.blit(trophy_text, (trophy_x, trophy_y))
    
    # Boutons
    font_button = pygame.font.Font(None, 48)
    button_width = 200
    button_height = 60
    button_spacing = 80
    start_y = WINDOW_HEIGHT//2 - button_height
    
    # Bouton "Font"
    font_button_rect = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, start_y, button_width, button_height)
    pygame.draw.rect(screen, BLUE, font_button_rect)
    pygame.draw.rect(screen, WHITE, font_button_rect, 3)
    font_text = font_button.render("Font", True, WHITE)
    font_text_rect = font_text.get_rect(center=font_button_rect.center)
    screen.blit(font_text, font_text_rect)
    
    # Bouton "Avatar"
    avatar_button_rect = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, start_y + button_spacing, button_width, button_height)
    pygame.draw.rect(screen, BLUE, avatar_button_rect)
    pygame.draw.rect(screen, WHITE, avatar_button_rect, 3)
    avatar_text = font_button.render("Avatar", True, WHITE)
    avatar_text_rect = avatar_text.get_rect(center=avatar_button_rect.center)
    screen.blit(avatar_text, avatar_text_rect)
    
    # Bouton "Nom"
    nom_button_rect = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, start_y + button_spacing * 2, button_width, button_height)
    pygame.draw.rect(screen, BLUE, nom_button_rect)
    pygame.draw.rect(screen, WHITE, nom_button_rect, 3)
    nom_text = font_button.render("Nom", True, WHITE)
    nom_text_rect = nom_text.get_rect(center=nom_button_rect.center)
    screen.blit(nom_text, nom_text_rect)
    
    # Bouton retour
    retour_button = pygame.Rect(10, 10, 100, 40)
    pygame.draw.rect(screen, RED, retour_button)
    pygame.draw.rect(screen, WHITE, retour_button, 2)
    font_retour = pygame.font.Font(None, 36)
    retour_text = font_retour.render("RETOUR", True, WHITE)
    retour_text_rect = retour_text.get_rect(center=retour_button.center)
    screen.blit(retour_text, retour_text_rect)
    
    # Bouton "Créer le compte" - apparaît seulement si tout est choisi
    creer_compte_button = None
    if player_name and selected_avatar and selected_font:
        creer_compte_button = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, start_y + button_spacing * 3, button_width, button_height)
        pygame.draw.rect(screen, (0, 200, 0), creer_compte_button)  # Vert
        pygame.draw.rect(screen, WHITE, creer_compte_button, 3)
        creer_text = font_button.render("Créer le compte", True, WHITE)
        creer_text_rect = creer_text.get_rect(center=creer_compte_button.center)
        screen.blit(creer_text, creer_text_rect)
    
    return retour_button, font_button_rect, avatar_button_rect, nom_button_rect, creer_compte_button, avatar_circle_rect

def draw_font_menu(screen, selected_font=None, pending_font=None):
    """Dessine le menu de police avec l'image de la police"""
    screen.fill(BLACK)
    
    # Titre
    font_title = pygame.font.Font(None, 72)
    title_text = font_title.render("FONT", True, YELLOW)
    title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, 80))
    screen.blit(title_text, title_rect)
    
    font_files = get_available_font_images()
    font_option_rects = build_font_option_rects(font_files)
    normalized_selected = normalize_font_selection(selected_font)
    normalized_pending = normalize_font_selection(pending_font)
    active_selection = normalized_pending if pending_font is not None else normalized_selected
    
    for rect, font_file in font_option_rects:
        try:
            font_image = pygame.image.load(font_file)
            font_image = pygame.transform.scale(font_image, (FONT_GRID_IMAGE_SIZE, FONT_GRID_IMAGE_SIZE))
            screen.blit(font_image, rect.topleft)
        except Exception:
            pygame.draw.rect(screen, WHITE, rect, 2)
        font_identifier = normalize_font_selection(font_file)
        is_selected = active_selection is not None and font_identifier == active_selection
        border_color = YELLOW if is_selected else WHITE
        border_width = 4 if is_selected else 2
        pygame.draw.rect(screen, border_color, rect, border_width)
    # Afficher un message si aucune image n'est trouvée
    if not font_option_rects:
        font_info = pygame.font.Font(None, 36)
        info_text = font_info.render("Images de police non trouvées", True, WHITE)
        info_rect = info_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
        screen.blit(info_text, info_rect)
        
        font_info2 = pygame.font.Font(None, 24)
        info_text2 = font_info2.render("Placez les images dans le dossier du jeu", True, WHITE)
        info_rect2 = info_text2.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 40))
        screen.blit(info_text2, info_rect2)
    
    # Bouton retour
    retour_button = pygame.Rect(10, 10, 100, 40)
    pygame.draw.rect(screen, RED, retour_button)
    pygame.draw.rect(screen, WHITE, retour_button, 2)
    font_retour = pygame.font.Font(None, 36)
    retour_text = font_retour.render("RETOUR", True, WHITE)
    retour_text_rect = retour_text.get_rect(center=retour_button.center)
    screen.blit(retour_text, retour_text_rect)
    
    # Bouton Valider - apparaît seulement si une sélection temporaire existe
    valider_button = None
    if normalized_pending is not None:
        valider_button = pygame.Rect(WINDOW_WIDTH - 120, WINDOW_HEIGHT - 60, 110, 50)
        pygame.draw.rect(screen, (0, 200, 0), valider_button)  # Vert
        pygame.draw.rect(screen, WHITE, valider_button, 2)
        valider_text = font_retour.render("VALIDER", True, WHITE)
        valider_text_rect = valider_text.get_rect(center=valider_button.center)
        screen.blit(valider_text, valider_text_rect)
    
    return retour_button, font_option_rects, valider_button

def draw_name_menu(screen, player_name="", input_active=False):
    """Dessine le menu de nom avec un champ de texte"""
    screen.fill(BLACK)
    
    # Titre
    font_title = pygame.font.Font(None, 72)
    title_text = font_title.render("NOM", True, YELLOW)
    title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, 80))
    screen.blit(title_text, title_rect)
    
    # Champ de texte
    input_width = 400
    input_height = 50
    input_x = (WINDOW_WIDTH - input_width) // 2
    input_y = WINDOW_HEIGHT // 2 - 50
    input_rect = pygame.Rect(input_x, input_y, input_width, input_height)
    
    # Couleur du champ selon si il est actif
    if input_active:
        input_color = WHITE
        border_color = YELLOW
        border_width = 3
    else:
        input_color = (100, 100, 100)
        border_color = WHITE
        border_width = 2
    
    pygame.draw.rect(screen, input_color, input_rect)
    pygame.draw.rect(screen, border_color, input_rect, border_width)
    
    # Afficher le texte saisi
    font_input = pygame.font.Font(None, 36)
    if player_name:
        text_surface = font_input.render(player_name, True, BLACK if input_active else WHITE)
        # Limiter la largeur du texte affiché
        max_text_width = input_width - 20
        if text_surface.get_width() > max_text_width:
            # Tronquer le texte si trop long
            while text_surface.get_width() > max_text_width and len(player_name) > 0:
                player_name = player_name[:-1]
                text_surface = font_input.render(player_name, True, BLACK if input_active else WHITE)
        screen.blit(text_surface, (input_x + 10, input_y + 10))
    
    # Curseur clignotant si le champ est actif
    if input_active:
        cursor_x = input_x + 10 + (font_input.size(player_name)[0] if player_name else 0)
        cursor_y = input_y + 10
        # Faire clignoter le curseur (basé sur le temps)
        import time
        if int(time.time() * 2) % 2 == 0:
            pygame.draw.line(screen, BLACK, (cursor_x, cursor_y), (cursor_x, cursor_y + 30), 2)
    
    # Instructions
    font_instruction = pygame.font.Font(None, 24)
    instruction_text = font_instruction.render("Tapez votre nom (max 7 caractères) et appuyez sur Entrée pour valider", True, WHITE)
    instruction_rect = instruction_text.get_rect(center=(WINDOW_WIDTH//2, input_y + 80))
    screen.blit(instruction_text, instruction_rect)
    
    # Afficher le nombre de caractères restants
    font_counter = pygame.font.Font(None, 20)
    remaining = 7 - len(player_name)
    counter_text = font_counter.render(f"Caractères restants: {remaining}", True, (150, 150, 150))
    counter_rect = counter_text.get_rect(center=(WINDOW_WIDTH//2, input_y + 110))
    screen.blit(counter_text, counter_rect)
    
    # Bouton retour
    retour_button = pygame.Rect(10, 10, 100, 40)
    pygame.draw.rect(screen, RED, retour_button)
    pygame.draw.rect(screen, WHITE, retour_button, 2)
    font_retour = pygame.font.Font(None, 36)
    retour_text = font_retour.render("RETOUR", True, WHITE)
    retour_text_rect = retour_text.get_rect(center=retour_button.center)
    screen.blit(retour_text, retour_text_rect)
    
    return retour_button, input_rect

def draw_avatar_menu(screen, selected_avatar=None, pending_avatar=None):
    """Dessine le menu d'avatar avec les images du chat sur le fantôme"""
    screen.fill(BLACK)
    
    # Titre
    font_title = pygame.font.Font(None, 72)
    title_text = font_title.render("AVATAR", True, YELLOW)
    title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, 80))
    screen.blit(title_text, title_rect)
    
    # Essayer de charger les images d'avatar
    avatar_image1 = None
    avatar_image2 = None
    avatar_image3 = None
    avatar_image4 = None
    avatar_paths1 = ["fatome_epee.png", "avatar.png", "image-t26edcoUjiXQ72uQKAB3R(2).png", "avatar.jpg", "avatar.jpeg"]
    # Utiliser le deuxième font comme avatar2
    second_font = get_second_font()
    avatar_paths2 = [second_font] if second_font else []
    avatar_paths3 = ["image-1uA5ykn6ZPDhIyRHwCxym.webp"]
    avatar_paths4 = ["le_super_67.webp"]
    
    # Charger la première image
    for path in avatar_paths1:
        if os.path.exists(path):
            try:
                avatar_image1 = pygame.image.load(path)
                break
            except:
                continue
    
    # Charger la deuxième image
    for path in avatar_paths2:
        if os.path.exists(path):
            try:
                avatar_image2 = pygame.image.load(path)
                break
            except:
                continue
    
    # Charger la troisième image
    for path in avatar_paths3:
        if os.path.exists(path):
            try:
                avatar_image3 = pygame.image.load(path)
                break
            except:
                continue
    
    # Charger la quatrième image
    for path in avatar_paths4:
        if os.path.exists(path):
            try:
                avatar_image4 = pygame.image.load(path)
                break
            except:
                continue
    
    # Afficher les images si elles existent
    small_size = 80  # Taille fixe de 80x80 pixels
    
    # Position verticale : en dessous du titre (80 + marge)
    img_y = 120
    spacing = 90  # Espacement entre les images
    
    # Calculer la position horizontale pour centrer les images
    total_width = 0
    image_count = sum([1 for img in [avatar_image1, avatar_image2, avatar_image3, avatar_image4] if img is not None])
    if image_count > 0:
        total_width = (image_count * small_size) + ((image_count - 1) * (spacing - small_size))
        start_x = (WINDOW_WIDTH - total_width) // 2
    else:
        start_x = 10
    
    # Rectangles pour les clics
    avatar_rect1 = None
    avatar_rect2 = None
    avatar_rect3 = None
    avatar_rect4 = None
    
    # Déterminer quel avatar est actuellement sélectionné (pending_avatar a la priorité)
    current_selection = pending_avatar if pending_avatar is not None else selected_avatar
    
    # Première image
    if avatar_image1:
        avatar_image1 = pygame.transform.scale(avatar_image1, (small_size, small_size))
        img_x = start_x
        avatar_rect1 = pygame.Rect(img_x, img_y, small_size, small_size)
        screen.blit(avatar_image1, (img_x, img_y))
        # Dessiner une bordure (jaune si sélectionné, blanche sinon)
        border_color = YELLOW if current_selection == "avatar1" else WHITE
        border_width = 4 if current_selection == "avatar1" else 2
        pygame.draw.rect(screen, border_color, avatar_rect1, border_width)
        start_x += spacing
    
    # Deuxième image
    if avatar_image2:
        avatar_image2 = pygame.transform.scale(avatar_image2, (small_size, small_size))
        img_x = start_x
        avatar_rect2 = pygame.Rect(img_x, img_y, small_size, small_size)
        screen.blit(avatar_image2, (img_x, img_y))
        # Dessiner une bordure (jaune si sélectionné, blanche sinon)
        border_color = YELLOW if current_selection == "avatar2" else WHITE
        border_width = 4 if current_selection == "avatar2" else 2
        pygame.draw.rect(screen, border_color, avatar_rect2, border_width)
        start_x += spacing
    
    # Troisième image
    if avatar_image3:
        avatar_image3 = pygame.transform.scale(avatar_image3, (small_size, small_size))
        img_x = start_x
        avatar_rect3 = pygame.Rect(img_x, img_y, small_size, small_size)
        screen.blit(avatar_image3, (img_x, img_y))
        # Dessiner une bordure (jaune si sélectionné, blanche sinon)
        border_color = YELLOW if current_selection == "avatar3" else WHITE
        border_width = 4 if current_selection == "avatar3" else 2
        pygame.draw.rect(screen, border_color, avatar_rect3, border_width)
        start_x += spacing
    
    # Quatrième image
    if avatar_image4:
        avatar_image4 = pygame.transform.scale(avatar_image4, (small_size, small_size))
        img_x = start_x
        avatar_rect4 = pygame.Rect(img_x, img_y, small_size, small_size)
        screen.blit(avatar_image4, (img_x, img_y))
        # Dessiner une bordure (jaune si sélectionné, blanche sinon)
        border_color = YELLOW if current_selection == "avatar4" else WHITE
        border_width = 4 if current_selection == "avatar4" else 2
        pygame.draw.rect(screen, border_color, avatar_rect4, border_width)
    # Afficher un message si aucune image n'est trouvée
    if not avatar_image1 and not avatar_image2 and not avatar_image3 and not avatar_image4:
        font_info = pygame.font.Font(None, 36)
        info_text = font_info.render("Images d'avatar non trouvées", True, WHITE)
        info_rect = info_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
        screen.blit(info_text, info_rect)
        
        font_info2 = pygame.font.Font(None, 24)
        info_text2 = font_info2.render("Placez les images dans le dossier du jeu", True, WHITE)
        info_rect2 = info_text2.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 40))
        screen.blit(info_text2, info_rect2)
    
    # Bouton retour (en haut à gauche)
    retour_button = pygame.Rect(10, 10, 100, 40)
    pygame.draw.rect(screen, RED, retour_button)
    pygame.draw.rect(screen, WHITE, retour_button, 2)
    font_retour = pygame.font.Font(None, 36)
    retour_text = font_retour.render("RETOUR", True, WHITE)
    retour_text_rect = retour_text.get_rect(center=retour_button.center)
    screen.blit(retour_text, retour_text_rect)
    
    # Bouton Valider - apparaît seulement si une sélection temporaire existe
    valider_button = None
    if pending_avatar is not None:
        valider_button = pygame.Rect(WINDOW_WIDTH - 120, WINDOW_HEIGHT - 60, 110, 50)
        pygame.draw.rect(screen, (0, 200, 0), valider_button)  # Vert
        pygame.draw.rect(screen, WHITE, valider_button, 2)
        valider_text = font_retour.render("VALIDER", True, WHITE)
        valider_text_rect = valider_text.get_rect(center=valider_button.center)
        screen.blit(valider_text, valider_text_rect)
    
    return retour_button, avatar_rect1, avatar_rect2, avatar_rect3, avatar_rect4, valider_button

def draw_menu(screen, difficulty=None):
    """Dessine le menu principal"""
    screen.fill(BLACK)
    
    # Bouton "Changer de compte" en haut à droite
    font_changer_compte = pygame.font.Font(None, 24)
    changer_compte_button = pygame.Rect(WINDOW_WIDTH - 180, 10, 170, 35)
    pygame.draw.rect(screen, (100, 100, 200), changer_compte_button)  # Bleu-gris
    pygame.draw.rect(screen, WHITE, changer_compte_button, 2)
    changer_compte_text = font_changer_compte.render("Changer de compte", True, WHITE)
    changer_compte_text_rect = changer_compte_text.get_rect(center=changer_compte_button.center)
    screen.blit(changer_compte_text, changer_compte_text_rect)
    
    
    # Boutons
    font_button = pygame.font.Font(None, 32)  # Réduit de 36 à 32
    button_height = 40  # Réduit de 45 à 40
    button_width = 140  # Réduit de 150 à 140
    button_spacing = 42  # Réduit de 50 à 42
    start_y = 170  # Réduit de 180 à 170
    
    # Afficher la difficulté choisie au-dessus du bouton "Jouer" si une difficulté a été sélectionnée
    if difficulty:
        font_difficulty = pygame.font.Font(None, 28)
        difficulty_names = {
            "facile": "FACILE",
            "moyen": "MOYEN",
            "difficile": "DIFFICILE",
            "hardcore": "HARDCORE"
        }
        difficulty_colors = {
            "facile": (0, 200, 0),  # Vert
            "moyen": (200, 200, 0),  # Jaune
            "difficile": (200, 0, 0),  # Rouge
            "hardcore": (128, 0, 128)  # Violet
        }
        difficulty_text_str = difficulty_names.get(difficulty, difficulty.upper())
        difficulty_text = font_difficulty.render(f"Difficulté: {difficulty_text_str}", True, WHITE)
        difficulty_text_rect = difficulty_text.get_rect(center=(WINDOW_WIDTH//2, start_y - 25))
        screen.blit(difficulty_text, difficulty_text_rect)
    
    # Bouton Jeu
    jeu_button = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, start_y, button_width, button_height)
    pygame.draw.rect(screen, BLUE, jeu_button)
    pygame.draw.rect(screen, WHITE, jeu_button, 3)
    jeu_text = font_button.render("JEU", True, WHITE)
    jeu_text_rect = jeu_text.get_rect(center=jeu_button.center)
    screen.blit(jeu_text, jeu_text_rect)
    
    # Bouton Magasin
    magasin_button = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, start_y + button_spacing, button_width, button_height)
    pygame.draw.rect(screen, BLUE, magasin_button)
    pygame.draw.rect(screen, WHITE, magasin_button, 3)
    magasin_text = font_button.render("MAGASIN", True, WHITE)
    magasin_text_rect = magasin_text.get_rect(center=magasin_button.center)
    screen.blit(magasin_text, magasin_text_rect)
    
    # Bouton Difficulté
    difficulte_button = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, start_y + button_spacing * 2, button_width, button_height)
    pygame.draw.rect(screen, BLUE, difficulte_button)  # Bleu
    pygame.draw.rect(screen, WHITE, difficulte_button, 3)
    difficulte_text = font_button.render("DIFFICULTÉ", True, WHITE)
    difficulte_text_rect = difficulte_text.get_rect(center=difficulte_button.center)
    screen.blit(difficulte_text, difficulte_text_rect)
    
    # Bouton Poche
    poche_button = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, start_y + button_spacing * 3, button_width, button_height)
    pygame.draw.rect(screen, BLUE, poche_button)
    pygame.draw.rect(screen, WHITE, poche_button, 3)
    poche_text = font_button.render("POCHE", True, WHITE)
    poche_text_rect = poche_text.get_rect(center=poche_button.center)
    screen.blit(poche_text, poche_text_rect)
    
    # Bouton Inventaire
    inventaire_button = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, start_y + button_spacing * 4, button_width, button_height)
    pygame.draw.rect(screen, BLUE, inventaire_button)
    pygame.draw.rect(screen, WHITE, inventaire_button, 3)
    inventaire_text = font_button.render("INVENTAIRE", True, WHITE)
    inventaire_text_rect = inventaire_text.get_rect(center=inventaire_button.center)
    screen.blit(inventaire_text, inventaire_text_rect)
    
    # Bouton Vente
    vente_button = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, start_y + button_spacing * 5, button_width, button_height)
    pygame.draw.rect(screen, BLUE, vente_button)  # Bleu
    pygame.draw.rect(screen, WHITE, vente_button, 3)
    vente_text = font_button.render("VENTE", True, WHITE)
    vente_text_rect = vente_text.get_rect(center=vente_button.center)
    screen.blit(vente_text, vente_text_rect)
    
    # Bouton Aventure (entre Vente et Passe)
    aventure_button = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, start_y + button_spacing * 6, button_width, button_height)
    pygame.draw.rect(screen, (0, 150, 255), aventure_button)  # Bleu
    pygame.draw.rect(screen, WHITE, aventure_button, 3)
    aventure_text = font_button.render("AVENTURE", True, WHITE)
    aventure_text_rect = aventure_text.get_rect(center=aventure_button.center)
    screen.blit(aventure_text, aventure_text_rect)
    
    # Bouton Boutique
    boutique_button = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, start_y + button_spacing * 7, button_width, button_height)
    pygame.draw.rect(screen, (255, 215, 0), boutique_button)  # Or
    pygame.draw.rect(screen, WHITE, boutique_button, 3)
    boutique_text = font_button.render("BOUTIQUE", True, BLACK)
    boutique_text_rect = boutique_text.get_rect(center=boutique_button.center)
    screen.blit(boutique_text, boutique_text_rect)
    
    # Bouton Passe de combat
    passe_combat_button = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, start_y + button_spacing * 8, button_width, button_height)
    pygame.draw.rect(screen, (200, 100, 0), passe_combat_button)  # Orange
    pygame.draw.rect(screen, WHITE, passe_combat_button, 3)
    passe_combat_text = font_button.render("PASSE", True, WHITE)
    passe_combat_text_rect = passe_combat_text.get_rect(center=passe_combat_button.center)
    screen.blit(passe_combat_text, passe_combat_text_rect)
    
    # Bouton "Arbre des trophées" en dessous de PASSE
    skill_tree_button = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, start_y + button_spacing * 9, button_width, button_height)
    pygame.draw.rect(screen, (100, 50, 200), skill_tree_button)  # Violet
    pygame.draw.rect(screen, WHITE, skill_tree_button, 3)
    font_skill_tree = pygame.font.Font(None, 28)  # Police plus petite pour le texte sur 2 lignes
    skill_tree_text1 = font_skill_tree.render("Arbre des", True, WHITE)
    skill_tree_text2 = font_skill_tree.render("trophées", True, WHITE)
    skill_tree_text_rect1 = skill_tree_text1.get_rect(center=(skill_tree_button.centerx, skill_tree_button.centery - 8))
    skill_tree_text_rect2 = skill_tree_text2.get_rect(center=(skill_tree_button.centerx, skill_tree_button.centery + 8))
    screen.blit(skill_tree_text1, skill_tree_text_rect1)
    screen.blit(skill_tree_text2, skill_tree_text_rect2)
    
    # Bouton Tutoriel
    tutoriel_button = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, start_y + button_spacing * 10, button_width, button_height)
    pygame.draw.rect(screen, (150, 0, 150), tutoriel_button)  # Violet
    pygame.draw.rect(screen, WHITE, tutoriel_button, 3)
    tutoriel_text = font_button.render("TUTORIEL", True, WHITE)
    tutoriel_text_rect = tutoriel_text.get_rect(center=tutoriel_button.center)
    screen.blit(tutoriel_text, tutoriel_text_rect)
    
    return jeu_button, magasin_button, difficulte_button, poche_button, inventaire_button, vente_button, changer_compte_button, aventure_button, boutique_button, passe_combat_button, skill_tree_button, tutoriel_button

def draw_tutorial_menu(screen, page=0):
    """Dessine le menu de tutoriel avec plusieurs pages"""
    screen.fill(BLACK)
    
    # Navigation en haut
    font_nav = pygame.font.Font(None, 32)
    prev_button = None
    next_button = None
    
    # Bouton Précédent en haut à gauche
    if page > 0:
        prev_button = pygame.Rect(10, 10, 120, 40)
        pygame.draw.rect(screen, BLUE, prev_button)
        pygame.draw.rect(screen, WHITE, prev_button, 2)
        prev_text = font_nav.render("PRÉCÉDENT", True, WHITE)
        prev_text_rect = prev_text.get_rect(center=prev_button.center)
        screen.blit(prev_text, prev_text_rect)
    
    # Bouton Suivant en haut à droite
    total_pages = 6
    if page < total_pages - 1:
        next_button = pygame.Rect(WINDOW_WIDTH - 130, 10, 120, 40)
        pygame.draw.rect(screen, (0, 200, 0), next_button)  # Vert
        pygame.draw.rect(screen, WHITE, next_button, 2)
        next_text = font_nav.render("SUIVANT", True, WHITE)
        next_text_rect = next_text.get_rect(center=next_button.center)
        screen.blit(next_text, next_text_rect)
    
    # Titre
    font_title = pygame.font.Font(None, 72)
    title_text = font_title.render("TUTORIEL", True, YELLOW)
    title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, 50))
    screen.blit(title_text, title_rect)
    
    # Contenu de la page
    font_content = pygame.font.Font(None, 28)
    font_subtitle = pygame.font.Font(None, 40)
    content_y = 120
    line_height = 35
    max_width = WINDOW_WIDTH - 100
    
    if page == 0:
        # Page 1: Bienvenue et objectif
        subtitle = font_subtitle.render("BIENVENUE DANS PACMAN !", True, YELLOW)
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH//2, content_y))
        screen.blit(subtitle, subtitle_rect)
        content_y += 60
        
        lines = [
            "Ce jeu est une version améliorée du classique Pacman.",
            "",
            "OBJECTIF PRINCIPAL :",
            "• Collectez tous les points jaunes et les pacgommes",
            "• Évitez les fantômes qui vous poursuivent",
            "• Survivez le plus longtemps possible",
            "",
            "CONTRÔLES :",
            "• Flèches directionnelles (↑ ↓ ← →) : Déplacer Pacman",
            "• R : Redémarrer après une partie terminée",
            "",
            "POINTS ET SCORE :",
            "• Points jaunes : 10 points chacun",
            "• Pacgommes (grosses pastilles) : 50 points",
            "• Fantômes vulnérables : 200 points chacun"
        ]
        
    elif page == 1:
        # Page 2: Mécaniques de jeu
        subtitle = font_subtitle.render("MÉCANIQUES DE JEU", True, YELLOW)
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH//2, content_y))
        screen.blit(subtitle, subtitle_rect)
        content_y += 60
        
        lines = [
            "PACGOMMES :",
            "• Les pacgommes rendent tous les fantômes vulnérables",
            "• Les fantômes deviennent bleus pendant 5 secondes",
            "• Vous pouvez les manger pour gagner 200 points",
            "",
            "FANTÔMES :",
            "• Les fantômes normaux vous poursuivent",
            "• Les fantômes vulnérables (bleus) vous fuient",
            "• Quand un fantôme est mangé, il devient des yeux",
            "• Les yeux retournent à la base et ne peuvent pas vous toucher",
            "",
            "VIES :",
            "• Vous commencez avec 2 vies",
            "• Si un fantôme normal vous touche, vous perdez une vie",
            "• Vous réapparaissez à la position de départ",
            "• Le jeu se termine quand vous n'avez plus de vies"
        ]
        
    elif page == 2:
        # Page 3: Système de niveaux
        subtitle = font_subtitle.render("SYSTÈME DE NIVEAUX", True, YELLOW)
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH//2, content_y))
        screen.blit(subtitle, subtitle_rect)
        content_y += 60
        
        lines = [
            "PROGRESSION :",
            "• Le jeu continue indéfiniment avec des niveaux",
            "• 4 labyrinthes différents alternent entre les niveaux",
            "• La difficulté augmente avec chaque niveau",
            "",
            "FANTÔMES PAR NIVEAU :",
            "• Niveau 1 : 2 fantômes",
            "• Niveaux 2-3 : 3 fantômes",
            "• Niveau 4+ : 4 fantômes (maximum)",
            "",
            "TÉLÉPORTATION :",
            "• Vous pouvez traverser les bords du labyrinthe",
            "• Sortir d'un côté vous fait apparaître de l'autre"
        ]
        
    elif page == 3:
        # Page 4: Menu et comptes
        subtitle = font_subtitle.render("MENU ET COMPTES", True, YELLOW)
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH//2, content_y))
        screen.blit(subtitle, subtitle_rect)
        content_y += 60
        
        lines = [
            "CRÉATION DE COMPTE :",
            "• Au démarrage, créez votre compte",
            "• Choisissez un nom (max 7 caractères)",
            "• Sélectionnez un avatar parmi les options",
            "• Choisissez une police pour votre profil",
            "",
            "MENU PRINCIPAL :",
            "• JEU : Lancer une partie",
            "• DIFFICULTÉ : Choisir la difficulté (Facile, Moyen, Difficile, Hardcore)",
            "• MAGASIN : Acheter des objets et améliorations",
            "• INVENTAIRE : Voir vos objets possédés",
            "• POCHE : Consulter vos ressources (jetons, couronnes, gemmes)"
        ]
        
    elif page == 4:
        # Page 5: Fonctionnalités avancées
        subtitle = font_subtitle.render("FONCTIONNALITÉS AVANCÉES", True, YELLOW)
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH//2, content_y))
        screen.blit(subtitle, subtitle_rect)
        content_y += 60
        
        lines = [
            "AVENTURE :",
            "• Mode spécial avec 3 vies et progression",
            "• Commencez avec 0 couronnes et 0 pacoins",
            "",
            "PASSE DE COMBAT :",
            "• Gagnez de l'XP en jouant",
            "• Débloquez des récompenses à chaque niveau",
            "• Utilisez les étoiles pour des bonus spéciaux",
            "",
            "ARBRE DES TROPHÉES :",
            "• Débloquez des trophées en accomplissant des défis",
            "• Deux catégories : Survie et Équipement",
            "• Les trophées débloquent de nouvelles capacités",
            "",
            "BOUTIQUE :",
            "• Achetez des objets avec vos ressources",
            "• VENTE : Vendez vos objets pour obtenir des ressources"
        ]
        
    elif page == 5:
        # Page 6: Conseils et stratégies
        subtitle = font_subtitle.render("CONSEILS ET STRATÉGIES", True, YELLOW)
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH//2, content_y))
        screen.blit(subtitle, subtitle_rect)
        content_y += 60
        
        lines = [
            "STRATÉGIES :",
            "• Planifiez votre route pour collecter les points efficacement",
            "• Utilisez les pacgommes stratégiquement",
            "• Les coins sont souvent plus sûrs que le centre",
            "",
            "GESTION DES FANTÔMES :",
            "• Observez les patterns de déplacement des fantômes",
            "• Utilisez les murs pour bloquer les fantômes",
            "• Attirez les fantômes dans des zones mortes",
            "",
            "SURVIE :",
            "• Ne prenez pas de risques inutiles",
            "• Gardez toujours une voie de fuite",
            "• Utilisez la téléportation pour échapper aux fantômes",
            "",
            "BONNE CHANCE ET AMUSEZ-VOUS BIEN !"
        ]
    
    # Afficher les lignes de contenu
    for line in lines:
        if line:
            text_surface = font_content.render(line, True, WHITE)
            # Centrer le texte si c'est un titre ou une ligne courte
            if line.startswith("•") or ":" in line:
                text_rect = text_surface.get_rect(x=100, y=content_y)
            else:
                text_rect = text_surface.get_rect(center=(WINDOW_WIDTH//2, content_y))
            screen.blit(text_surface, text_rect)
        content_y += line_height
    
    # Numéro de page
    total_pages = 6
    page_text = font_content.render(f"Page {page + 1}/{total_pages}", True, (150, 150, 150))
    page_rect = page_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT - 30))
    screen.blit(page_text, page_rect)
    
    return prev_button, next_button

def draw_passe_menu(screen, battle_pass_level=1, battle_pass_xp=0, battle_pass_xp_needed=100, claimed_rewards=None, jeton_poche=0, crown_poche=0, gemme_poche=0, used_stars=None, scroll_offset=0):
    """Dessine le menu de la passe de combat (style Brawl Stars)"""
    if claimed_rewards is None:
        claimed_rewards = []
    if used_stars is None:
        used_stars = []
    MAX_BATTLE_PASS_LEVEL = 30  # Niveau maximum avant de recommencer
    # Niveaux avec récompenses en pacoins
    REWARD_LEVELS_PACOINS = {
        1: 300, 5: 300, 7: 300, 9: 300, 11: 300, 15: 300, 18: 300, 22: 300, 25: 300, 28: 1000, 29: 300
    }
    # Niveaux avec récompenses en couronnes
    REWARD_LEVELS_CROWNS = {
        2: 5, 6: 5, 13: 5, 20: 5, 27: 5
    }
    # Niveaux avec récompenses en gemmes
    REWARD_LEVELS_GEMS = {
        3: 10, 12: 10, 17: 10, 21: 10, 26: 10
    }
    screen.fill(BLACK)
    
    # Titre
    font_title = pygame.font.Font(None, 72)
    title_text = font_title.render("PASSE DE COMBAT", True, YELLOW)
    title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, 50))
    screen.blit(title_text, title_rect)
    
    # Bouton retour
    retour_button = pygame.Rect(10, 10, 100, 40)
    pygame.draw.rect(screen, RED, retour_button)
    pygame.draw.rect(screen, WHITE, retour_button, 2)
    font_retour = pygame.font.Font(None, 36)
    retour_text = font_retour.render("RETOUR", True, WHITE)
    retour_text_rect = retour_text.get_rect(center=retour_button.center)
    screen.blit(retour_text, retour_text_rect)
    
    # Barre de progression (style Brawl Stars)
    progress_y = 120
    progress_width = WINDOW_WIDTH - 100
    progress_height = 40
    progress_x = (WINDOW_WIDTH - progress_width) // 2
    
    # Fond de la barre de progression (gris)
    progress_bg = pygame.Rect(progress_x, progress_y, progress_width, progress_height)
    pygame.draw.rect(screen, (50, 50, 50), progress_bg)
    pygame.draw.rect(screen, WHITE, progress_bg, 2)
    
    # Barre de progression remplie (orange/jaune)
    progress_percent = min(battle_pass_xp / battle_pass_xp_needed, 1.0) if battle_pass_xp_needed > 0 else 0
    progress_filled_width = int(progress_width * progress_percent)
    if progress_filled_width > 0:
        progress_filled = pygame.Rect(progress_x, progress_y, progress_filled_width, progress_height)
        pygame.draw.rect(screen, (255, 200, 0), progress_filled)
    
    # Texte du niveau et XP
    font_progress = pygame.font.Font(None, 32)
    progress_text = f"Niveau {battle_pass_level} - {battle_pass_xp}/{battle_pass_xp_needed} XP"
    progress_text_surface = font_progress.render(progress_text, True, WHITE)
    progress_text_rect = progress_text_surface.get_rect(center=(WINDOW_WIDTH//2, progress_y + progress_height//2))
    screen.blit(progress_text_surface, progress_text_rect)
    
    # Afficher les pacoins, couronnes et gemmes disponibles
    font_currency = pygame.font.Font(None, 28)
    pacoins_text = font_currency.render(f"Pacoins: {jeton_poche}", True, YELLOW)
    pacoins_rect = pacoins_text.get_rect(center=(WINDOW_WIDTH//2 - 150, progress_y + progress_height + 25))
    screen.blit(pacoins_text, pacoins_rect)
    
    crowns_text = font_currency.render(f"Couronnes: {crown_poche}", True, (255, 215, 0))
    crowns_rect = crowns_text.get_rect(center=(WINDOW_WIDTH//2, progress_y + progress_height + 25))
    screen.blit(crowns_text, crowns_rect)
    
    gems_text = font_currency.render(f"Gemmes: {gemme_poche}", True, (0, 255, 255))
    gems_rect = gems_text.get_rect(center=(WINDOW_WIDTH//2 + 150, progress_y + progress_height + 25))
    screen.blit(gems_text, gems_rect)
    
    # Zone des récompenses (niveaux de la passe)
    rewards_start_y = progress_y + progress_height + 30
    rewards_area_height = WINDOW_HEIGHT - rewards_start_y - 60
    rewards_area = pygame.Rect(50, rewards_start_y, WINDOW_WIDTH - 100, rewards_area_height)
    pygame.draw.rect(screen, (30, 30, 30), rewards_area)
    pygame.draw.rect(screen, WHITE, rewards_area, 2)
    
    # Afficher quelques niveaux de récompenses (style Brawl Stars)
    font_reward = pygame.font.Font(None, 20)
    reward_item_size = 45
    reward_spacing = 55
    rewards_per_row = 10
    start_reward_x = rewards_area.x + 10
    start_reward_y = rewards_area.y + 10
    
    # Calculer le niveau effectif (boucle après le niveau 30)
    effective_level = ((battle_pass_level - 1) % MAX_BATTLE_PASS_LEVEL) + 1
    
    # Liste pour stocker les rectangles des récompenses (pour les clics)
    reward_rects = []
    
    # Afficher les récompenses pour les niveaux 1-30 avec défilement
    for level in range(1, MAX_BATTLE_PASS_LEVEL + 1):
        row = (level - 1) // rewards_per_row
        col = (level - 1) % rewards_per_row
        reward_x = start_reward_x + col * reward_spacing
        reward_y = start_reward_y + row * reward_spacing - scroll_offset
        
        # Ne dessiner que les récompenses visibles dans la zone
        if reward_y + reward_item_size < rewards_area.y:
            continue  # Trop haut, ne pas dessiner
        if reward_y > rewards_area.y + rewards_area.height:
            continue  # Trop bas, ne pas dessiner
        
        # Calculer le niveau équivalent dans le cycle actuel
        # Si on est au niveau 31, on est au niveau 1 du nouveau cycle
        cycle_number = (battle_pass_level - 1) // MAX_BATTLE_PASS_LEVEL
        level_in_current_cycle = level
        
        # Couleur selon l'état du niveau
        if battle_pass_level > MAX_BATTLE_PASS_LEVEL:
            # Si on a dépassé le niveau 30, on est dans un nouveau cycle
            # Tous les niveaux sont récupérables (vert) car on recommence
            if level == effective_level:
                reward_color = (0, 200, 0)  # Vert si on peut le récupérer maintenant
            elif level < effective_level:
                reward_color = (255, 165, 0)  # Orange si déjà récupéré dans ce cycle
            else:
                reward_color = (100, 100, 100)  # Gris si pas encore atteint dans ce cycle
        else:
            # Cycle normal (niveau 1-30)
            if level < battle_pass_level:
                reward_color = (255, 165, 0)  # Orange si déjà débloqué et récupéré
            elif level == battle_pass_level:
                reward_color = (0, 200, 0)  # Vert si on peut encore le récupérer
            else:
                reward_color = (100, 100, 100)  # Gris si verrouillé
        
        # Rectangle pour la récompense
        reward_rect = pygame.Rect(reward_x, reward_y, reward_item_size, reward_item_size)
        pygame.draw.rect(screen, reward_color, reward_rect)
        pygame.draw.rect(screen, WHITE, reward_rect, 2)
        
        # Numéro du niveau (seulement si ce n'est pas une case avec étoile)
        STAR_LEVELS = [4, 8, 10, 14, 16, 19, 23, 24, 30]
        if level not in STAR_LEVELS:
            level_text = font_reward.render(str(level), True, WHITE)
            level_text_rect = level_text.get_rect(center=(reward_rect.centerx, reward_rect.centery - 10))
            screen.blit(level_text, level_text_rect)
        
        # Afficher l'icône de récompense si c'est un niveau avec récompense (mais pas si c'est une case avec étoile)
        if level not in STAR_LEVELS:
            if level in REWARD_LEVELS_PACOINS:
                reward_amount = REWARD_LEVELS_PACOINS[level]
                reward_icon_text = font_reward.render(str(reward_amount), True, YELLOW)
                reward_icon_rect = reward_icon_text.get_rect(center=(reward_rect.centerx, reward_rect.centery + 1))
                screen.blit(reward_icon_text, reward_icon_rect)
                # Afficher "pacoins" en dessous
                font_pacoins_small = pygame.font.Font(None, 14)
                pacoins_text = font_pacoins_small.render("pacoins", True, YELLOW)
                pacoins_rect = pacoins_text.get_rect(center=(reward_rect.centerx, reward_rect.centery + 12))
                screen.blit(pacoins_text, pacoins_rect)
            elif level in REWARD_LEVELS_CROWNS:
                reward_amount = REWARD_LEVELS_CROWNS[level]
                reward_icon_text = font_reward.render(str(reward_amount), True, (255, 215, 0))  # Or pour les couronnes
                reward_icon_rect = reward_icon_text.get_rect(center=(reward_rect.centerx, reward_rect.centery + 1))
                screen.blit(reward_icon_text, reward_icon_rect)
                # Afficher "couronnes" en dessous
                font_crowns_small = pygame.font.Font(None, 14)
                crowns_text = font_crowns_small.render("couronnes", True, (255, 215, 0))
                crowns_rect = crowns_text.get_rect(center=(reward_rect.centerx, reward_rect.centery + 12))
                screen.blit(crowns_text, crowns_rect)
            elif level in REWARD_LEVELS_GEMS:
                reward_amount = REWARD_LEVELS_GEMS[level]
                reward_icon_text = font_reward.render(str(reward_amount), True, (0, 255, 255))  # Cyan pour les gemmes
                reward_icon_rect = reward_icon_text.get_rect(center=(reward_rect.centerx, reward_rect.centery + 1))
                screen.blit(reward_icon_text, reward_icon_rect)
                # Afficher "gemmes" en dessous
                font_gems_small = pygame.font.Font(None, 14)
                gems_text = font_gems_small.render("gemmes", True, (0, 255, 255))
                gems_rect = gems_text.get_rect(center=(reward_rect.centerx, reward_rect.centery + 12))
                screen.blit(gems_text, gems_rect)
        
        # Afficher une étoile cliquable sur les cases 4, 8, 10, 14, 16, 19, 23, 24, 30
        star_rect = None
        STAR_LEVELS = [4, 8, 10, 14, 16, 19, 23, 24, 30]
        if level in STAR_LEVELS:
            # Dessiner une grande étoile qui remplit toute la case
            star_rect = reward_rect  # L'étoile remplit toute la case
            star_size = reward_item_size  # Utiliser la taille de la case
            
            # Dessiner une étoile simple avec des lignes (5 branches) qui remplit la case
            import math
            star_points = []
            center_x, center_y = reward_rect.centerx, reward_rect.centery
            outer_radius = star_size // 2 - 5  # Laisser un peu de marge
            inner_radius = outer_radius * 0.4  # Ratio pour l'étoile
            
            for i in range(10):  # 10 points pour 5 branches
                angle = (i * math.pi / 5) - (math.pi / 2)
                if i % 2 == 0:
                    # Point extérieur
                    radius = outer_radius
                else:
                    # Point intérieur
                    radius = inner_radius
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                star_points.append((int(x), int(y)))
            
            # Couleur de l'étoile selon si le niveau est atteint et si elle a été utilisée
            # Si l'étoile a été utilisée, elle est grise
            # Si le niveau est atteint et l'étoile n'a pas été utilisée, l'étoile est verte et cliquable
            # Sinon, l'étoile est grise et non cliquable
            if level in used_stars:
                # Étoile déjà utilisée - étoile grise
                pygame.draw.polygon(screen, (100, 100, 100), star_points)
                pygame.draw.polygon(screen, (150, 150, 150), star_points, 2)
            elif level <= battle_pass_level:
                # Niveau atteint et étoile non utilisée
                # Étoile légendaire (jaune) pour le niveau 30, verte pour les autres
                if level == 30:
                    pygame.draw.polygon(screen, (255, 215, 0), star_points)  # Jaune/Or pour légendaire
                    pygame.draw.polygon(screen, (255, 255, 0), star_points, 2)  # Jaune clair pour le contour
                else:
                    pygame.draw.polygon(screen, (0, 200, 0), star_points)  # Vert pour rare
                    pygame.draw.polygon(screen, (0, 255, 0), star_points, 2)  # Vert clair pour le contour
            else:
                # Niveau non atteint - étoile grise et non cliquable
                pygame.draw.polygon(screen, (100, 100, 100), star_points)
                pygame.draw.polygon(screen, (150, 150, 150), star_points, 2)
        
        # Stocker le rectangle pour les clics (récompense et étoile si présente)
        reward_rects.append(("reward", reward_rect, level))
        # Stocker l'étoile seulement si le niveau est atteint (acheté) et qu'elle n'a pas été utilisée
        if star_rect and level <= battle_pass_level and level not in used_stars:
            reward_rects.append(("star", star_rect, level))
    
    # Flèche vers la droite pour aller au pass +
    arrow_button = pygame.Rect(WINDOW_WIDTH - 110, WINDOW_HEIGHT // 2 - 50 + 100, 100, 100)
    pygame.draw.rect(screen, (100, 100, 100), arrow_button)
    pygame.draw.rect(screen, WHITE, arrow_button, 2)
    # Dessiner une flèche vers la droite (pointe à droite) - 100 pixels
    arrow_points = [
        (arrow_button.centerx + 30, arrow_button.centery),  # Pointe de la flèche (droite)
        (arrow_button.centerx - 10, arrow_button.centery - 30),  # Haut gauche
        (arrow_button.centerx - 10, arrow_button.centery - 10),  # Milieu gauche haut
        (arrow_button.centerx - 30, arrow_button.centery - 10),  # Extrémité gauche haut
        (arrow_button.centerx - 30, arrow_button.centery + 10),  # Extrémité gauche bas
        (arrow_button.centerx - 10, arrow_button.centery + 10),  # Milieu gauche bas
        (arrow_button.centerx - 10, arrow_button.centery + 30)  # Bas gauche
    ]
    pygame.draw.polygon(screen, WHITE, arrow_points)
    
    return retour_button, reward_rects, arrow_button

def draw_passe_plus_menu(screen, battle_pass_level=1, battle_pass_xp=0, battle_pass_xp_needed=100, claimed_rewards=None, jeton_poche=0, crown_poche=0, gemme_poche=0, used_stars=None, scroll_offset=0, pass_plus_purchased=False):
    """Dessine le menu du passe de combat + (premium) - mêmes récompenses que le pass normal"""
    if claimed_rewards is None:
        claimed_rewards = []
    if used_stars is None:
        used_stars = []
    PASS_PLUS_PRICE = 100  # Prix du pass + en gemmes
    MAX_BATTLE_PASS_LEVEL = 30  # Niveau maximum avant de recommencer
    # Niveaux avec récompenses en pacoins
    REWARD_LEVELS_PACOINS = {
        1: 300, 5: 300, 7: 300, 9: 300, 11: 300, 15: 300, 18: 300, 22: 300, 25: 300, 28: 1000, 29: 300
    }
    # Niveaux avec récompenses en couronnes
    REWARD_LEVELS_CROWNS = {
        2: 5, 6: 5, 13: 5, 20: 5, 27: 5
    }
    # Niveaux avec récompenses en gemmes
    REWARD_LEVELS_GEMS = {
        3: 10, 12: 10, 17: 10, 21: 10, 26: 10
    }
    screen.fill(BLACK)
    
    # Titre
    font_title = pygame.font.Font(None, 72)
    title_text = font_title.render("PASSE DE COMBAT +", True, (255, 215, 0))  # Or
    title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, 50))
    screen.blit(title_text, title_rect)
    
    # Bouton retour
    retour_button = pygame.Rect(10, 10, 100, 40)
    pygame.draw.rect(screen, RED, retour_button)
    pygame.draw.rect(screen, WHITE, retour_button, 2)
    font_retour = pygame.font.Font(None, 36)
    retour_text = font_retour.render("RETOUR", True, WHITE)
    retour_text_rect = retour_text.get_rect(center=retour_button.center)
    screen.blit(retour_text, retour_text_rect)
    
    # Barre de progression (style Brawl Stars)
    progress_y = 120
    progress_width = WINDOW_WIDTH - 100
    progress_height = 40
    progress_x = (WINDOW_WIDTH - progress_width) // 2
    
    # Fond de la barre de progression (gris)
    progress_bg = pygame.Rect(progress_x, progress_y, progress_width, progress_height)
    pygame.draw.rect(screen, (50, 50, 50), progress_bg)
    pygame.draw.rect(screen, WHITE, progress_bg, 2)
    
    # Barre de progression remplie (orange/jaune)
    progress_percent = min(battle_pass_xp / battle_pass_xp_needed, 1.0) if battle_pass_xp_needed > 0 else 0
    progress_filled_width = int(progress_width * progress_percent)
    if progress_filled_width > 0:
        progress_filled = pygame.Rect(progress_x, progress_y, progress_filled_width, progress_height)
        pygame.draw.rect(screen, (255, 200, 0), progress_filled)
    
    # Texte du niveau et XP
    font_progress = pygame.font.Font(None, 32)
    progress_text = f"Niveau {battle_pass_level} - {battle_pass_xp}/{battle_pass_xp_needed} XP"
    progress_text_surface = font_progress.render(progress_text, True, WHITE)
    progress_text_rect = progress_text_surface.get_rect(center=(WINDOW_WIDTH//2, progress_y + progress_height//2))
    screen.blit(progress_text_surface, progress_text_rect)
    
    # Afficher les pacoins, couronnes et gemmes disponibles
    font_currency = pygame.font.Font(None, 28)
    pacoins_text = font_currency.render(f"Pacoins: {jeton_poche}", True, YELLOW)
    pacoins_rect = pacoins_text.get_rect(center=(WINDOW_WIDTH//2 - 150, progress_y + progress_height + 25))
    screen.blit(pacoins_text, pacoins_rect)
    
    crowns_text = font_currency.render(f"Couronnes: {crown_poche}", True, (255, 215, 0))
    crowns_rect = crowns_text.get_rect(center=(WINDOW_WIDTH//2, progress_y + progress_height + 25))
    screen.blit(crowns_text, crowns_rect)
    
    gems_text = font_currency.render(f"Gemmes: {gemme_poche}", True, (0, 255, 255))
    gems_rect = gems_text.get_rect(center=(WINDOW_WIDTH//2 + 150, progress_y + progress_height + 25))
    screen.blit(gems_text, gems_rect)
    
    # Zone des récompenses (niveaux de la passe)
    rewards_start_y = progress_y + progress_height + 30
    rewards_area_height = WINDOW_HEIGHT - rewards_start_y - 60
    rewards_area = pygame.Rect(50, rewards_start_y, WINDOW_WIDTH - 100, rewards_area_height)
    pygame.draw.rect(screen, (30, 30, 30), rewards_area)
    pygame.draw.rect(screen, WHITE, rewards_area, 2)
    
    # Afficher quelques niveaux de récompenses (style Brawl Stars)
    font_reward = pygame.font.Font(None, 20)
    reward_item_size = 45
    reward_spacing = 55
    rewards_per_row = 10
    start_reward_x = rewards_area.x + 10
    start_reward_y = rewards_area.y + 10
    
    # Calculer le niveau effectif (boucle après le niveau 30)
    effective_level = ((battle_pass_level - 1) % MAX_BATTLE_PASS_LEVEL) + 1
    
    # Liste pour stocker les rectangles des récompenses (pour les clics)
    reward_rects = []
    
    # Afficher les récompenses pour les niveaux 1-30 avec défilement
    for level in range(1, MAX_BATTLE_PASS_LEVEL + 1):
        row = (level - 1) // rewards_per_row
        col = (level - 1) % rewards_per_row
        reward_x = start_reward_x + col * reward_spacing
        reward_y = start_reward_y + row * reward_spacing - scroll_offset
        
        # Ne dessiner que les récompenses visibles dans la zone
        if reward_y + reward_item_size < rewards_area.y:
            continue  # Trop haut, ne pas dessiner
        if reward_y > rewards_area.y + rewards_area.height:
            continue  # Trop bas, ne pas dessiner
        
        # Calculer le niveau équivalent dans le cycle actuel
        # Si on est au niveau 31, on est au niveau 1 du nouveau cycle
        cycle_number = (battle_pass_level - 1) // MAX_BATTLE_PASS_LEVEL
        level_in_current_cycle = level
        
        # Couleur selon l'état du niveau (utiliser claimed_rewards pour le pass +)
        # Si le pass + n'est pas acheté, toutes les récompenses sont grisées
        if not pass_plus_purchased:
            reward_color = (50, 50, 50)  # Gris foncé si pass + non acheté
        elif battle_pass_level > MAX_BATTLE_PASS_LEVEL:
            # Si on a dépassé le niveau 30, on est dans un nouveau cycle
            # Tous les niveaux sont récupérables (vert) car on recommence
            if level == effective_level:
                reward_color = (0, 200, 0)  # Vert si on peut le récupérer maintenant
            elif level < effective_level:
                # Vérifier si la récompense a été récupérée dans claimed_rewards
                if level in claimed_rewards or level in used_stars:
                    reward_color = (255, 165, 0)  # Orange si déjà récupéré dans ce cycle
                else:
                    reward_color = (0, 200, 0)  # Vert si pas encore récupéré
            else:
                reward_color = (100, 100, 100)  # Gris si pas encore atteint dans ce cycle
        else:
            # Cycle normal (niveau 1-30)
            if level < battle_pass_level:
                # Vérifier si la récompense a été récupérée dans claimed_rewards
                if level in claimed_rewards or level in used_stars:
                    reward_color = (255, 165, 0)  # Orange si déjà débloqué et récupéré
                else:
                    reward_color = (0, 200, 0)  # Vert si débloqué mais pas encore récupéré
            elif level == battle_pass_level:
                reward_color = (0, 200, 0)  # Vert si on peut encore le récupérer
            else:
                reward_color = (100, 100, 100)  # Gris si verrouillé
        
        # Rectangle pour la récompense
        reward_rect = pygame.Rect(reward_x, reward_y, reward_item_size, reward_item_size)
        pygame.draw.rect(screen, reward_color, reward_rect)
        pygame.draw.rect(screen, WHITE, reward_rect, 2)
        
        # Numéro du niveau (seulement si ce n'est pas une case avec étoile)
        STAR_LEVELS = [4, 8, 10, 14, 16, 19, 23, 24, 30]
        if level not in STAR_LEVELS:
            level_text = font_reward.render(str(level), True, WHITE)
            level_text_rect = level_text.get_rect(center=(reward_rect.centerx, reward_rect.centery - 10))
            screen.blit(level_text, level_text_rect)
        
        # Afficher l'icône de récompense si c'est un niveau avec récompense (mais pas si c'est une case avec étoile)
        if level not in STAR_LEVELS:
            if level in REWARD_LEVELS_PACOINS:
                reward_amount = REWARD_LEVELS_PACOINS[level]
                reward_icon_text = font_reward.render(str(reward_amount), True, YELLOW)
                reward_icon_rect = reward_icon_text.get_rect(center=(reward_rect.centerx, reward_rect.centery + 1))
                screen.blit(reward_icon_text, reward_icon_rect)
                # Afficher "pacoins" en dessous
                font_pacoins_small = pygame.font.Font(None, 14)
                pacoins_text = font_pacoins_small.render("pacoins", True, YELLOW)
                pacoins_rect = pacoins_text.get_rect(center=(reward_rect.centerx, reward_rect.centery + 12))
                screen.blit(pacoins_text, pacoins_rect)
            elif level in REWARD_LEVELS_CROWNS:
                reward_amount = REWARD_LEVELS_CROWNS[level]
                reward_icon_text = font_reward.render(str(reward_amount), True, (255, 215, 0))  # Or pour les couronnes
                reward_icon_rect = reward_icon_text.get_rect(center=(reward_rect.centerx, reward_rect.centery + 1))
                screen.blit(reward_icon_text, reward_icon_rect)
                # Afficher "couronnes" en dessous
                font_crowns_small = pygame.font.Font(None, 14)
                crowns_text = font_crowns_small.render("couronnes", True, (255, 215, 0))
                crowns_rect = crowns_text.get_rect(center=(reward_rect.centerx, reward_rect.centery + 12))
                screen.blit(crowns_text, crowns_rect)
            elif level in REWARD_LEVELS_GEMS:
                reward_amount = REWARD_LEVELS_GEMS[level]
                reward_icon_text = font_reward.render(str(reward_amount), True, (0, 255, 255))  # Cyan pour les gemmes
                reward_icon_rect = reward_icon_text.get_rect(center=(reward_rect.centerx, reward_rect.centery + 1))
                screen.blit(reward_icon_text, reward_icon_rect)
                # Afficher "gemmes" en dessous
                font_gems_small = pygame.font.Font(None, 14)
                gems_text = font_gems_small.render("gemmes", True, (0, 255, 255))
                gems_rect = gems_text.get_rect(center=(reward_rect.centerx, reward_rect.centery + 12))
                screen.blit(gems_text, gems_rect)
        
        # Afficher une étoile cliquable sur les cases 4, 8, 10, 14, 16, 19, 23, 24, 30
        star_rect = None
        STAR_LEVELS = [4, 8, 10, 14, 16, 19, 23, 24, 30]
        if level in STAR_LEVELS:
            # Dessiner une grande étoile qui remplit toute la case
            star_rect = reward_rect  # L'étoile remplit toute la case
            star_size = reward_item_size  # Utiliser la taille de la case
            
            # Dessiner une étoile simple avec des lignes (5 branches) qui remplit la case
            import math
            star_points = []
            center_x, center_y = reward_rect.centerx, reward_rect.centery
            outer_radius = star_size // 2 - 5  # Laisser un peu de marge
            inner_radius = outer_radius * 0.4  # Ratio pour l'étoile
            
            for i in range(10):  # 10 points pour 5 branches
                angle = (i * math.pi / 5) - (math.pi / 2)
                if i % 2 == 0:
                    # Point extérieur
                    radius = outer_radius
                else:
                    # Point intérieur
                    radius = inner_radius
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                star_points.append((int(x), int(y)))
            
            # Couleur de l'étoile selon si le niveau est atteint et si elle a été utilisée
            # Si l'étoile a été utilisée, elle est grise
            # Si le niveau est atteint et l'étoile n'a pas été utilisée, l'étoile est verte et cliquable
            # Sinon, l'étoile est grise et non cliquable
            # Si le pass + n'est pas acheté, toutes les étoiles sont grisées
            if not pass_plus_purchased:
                # Pass + non acheté - étoile grise foncée
                pygame.draw.polygon(screen, (50, 50, 50), star_points)
                pygame.draw.polygon(screen, (100, 100, 100), star_points, 2)
            elif level in used_stars:
                # Étoile déjà utilisée - étoile grise
                pygame.draw.polygon(screen, (100, 100, 100), star_points)
                pygame.draw.polygon(screen, (150, 150, 150), star_points, 2)
            elif level <= battle_pass_level:
                # Niveau atteint et étoile non utilisée
                # Étoile légendaire (jaune) pour le niveau 30, verte pour les autres
                if level == 30:
                    pygame.draw.polygon(screen, (255, 215, 0), star_points)  # Jaune/Or pour légendaire
                    pygame.draw.polygon(screen, (255, 255, 0), star_points, 2)  # Jaune clair pour le contour
                else:
                    pygame.draw.polygon(screen, (0, 200, 0), star_points)  # Vert pour rare
                    pygame.draw.polygon(screen, (0, 255, 0), star_points, 2)  # Vert clair pour le contour
            else:
                # Niveau non atteint - étoile grise et non cliquable
                pygame.draw.polygon(screen, (100, 100, 100), star_points)
                pygame.draw.polygon(screen, (150, 150, 150), star_points, 2)
        
        # Stocker le rectangle pour les clics (récompense et étoile si présente)
        reward_rects.append(("reward", reward_rect, level))
        # Stocker l'étoile seulement si le niveau est atteint (acheté) et qu'elle n'a pas été utilisée
        if star_rect and level <= battle_pass_level and level not in used_stars:
            reward_rects.append(("star", star_rect, level))
    
    # Bouton pour acheter le pass + (si non acheté)
    buy_pass_plus_button = None
    if not pass_plus_purchased:
        buy_pass_plus_button = pygame.Rect(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT - 60, 300, 50)
        pygame.draw.rect(screen, (255, 215, 0), buy_pass_plus_button)  # Or
        pygame.draw.rect(screen, WHITE, buy_pass_plus_button, 3)
        font_buy = pygame.font.Font(None, 36)
        buy_text = font_buy.render(f"ACHETER PASS + ({PASS_PLUS_PRICE} gemmes)", True, BLACK)
        buy_text_rect = buy_text.get_rect(center=buy_pass_plus_button.center)
        screen.blit(buy_text, buy_text_rect)
    
    # Bouton pour gagner 100 XP (en bas à droite, seulement si le pass + est acheté)
    gain_xp_button = None
    if pass_plus_purchased:
        gain_xp_button = pygame.Rect(WINDOW_WIDTH - 200, WINDOW_HEIGHT - 60, 180, 50)
        pygame.draw.rect(screen, (0, 200, 0), gain_xp_button)  # Vert
        pygame.draw.rect(screen, WHITE, gain_xp_button, 3)
        font_gain_xp = pygame.font.Font(None, 32)
        gain_xp_text = font_gain_xp.render("+100 XP", True, WHITE)
        gain_xp_text_rect = gain_xp_text.get_rect(center=gain_xp_button.center)
        screen.blit(gain_xp_text, gain_xp_text_rect)
    
    # Flèche vers la gauche pour revenir au pass normal
    arrow_left_button = pygame.Rect(10, WINDOW_HEIGHT // 2 - 50 + 100, 100, 100)
    pygame.draw.rect(screen, (100, 100, 100), arrow_left_button)
    pygame.draw.rect(screen, WHITE, arrow_left_button, 2)
    # Dessiner une flèche vers la gauche (pointe à gauche) - 100 pixels
    arrow_left_points = [
        (arrow_left_button.centerx - 30, arrow_left_button.centery),  # Pointe de la flèche (gauche)
        (arrow_left_button.centerx + 10, arrow_left_button.centery - 30),  # Haut droite
        (arrow_left_button.centerx + 10, arrow_left_button.centery - 10),  # Milieu droite haut
        (arrow_left_button.centerx + 30, arrow_left_button.centery - 10),  # Extrémité droite haut
        (arrow_left_button.centerx + 30, arrow_left_button.centery + 10),  # Extrémité droite bas
        (arrow_left_button.centerx + 10, arrow_left_button.centery + 10),  # Milieu droite bas
        (arrow_left_button.centerx + 10, arrow_left_button.centery + 30)  # Bas droite
    ]
    pygame.draw.polygon(screen, WHITE, arrow_left_points)
    
    return retour_button, gain_xp_button, reward_rects, arrow_left_button, buy_pass_plus_button

def draw_shop(screen):
    """Dessine l'écran du magasin"""
    screen.fill(BLACK)
    
    font_title = pygame.font.Font(None, 72)
    title_text = font_title.render("MAGASIN", True, BLACK)
    title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, 100))
    screen.blit(title_text, title_rect)
    
    # Boutons du magasin
    font_button = pygame.font.Font(None, 36)
    button_width = 150
    button_height = 50
    button_spacing = 60
    start_y = 200
    
    # Bouton GADGET
    gadget_button = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, start_y, button_width, button_height)
    pygame.draw.rect(screen, BLUE, gadget_button)
    pygame.draw.rect(screen, WHITE, gadget_button, 2)
    gadget_text = font_button.render("GADGET", True, BLACK)
    gadget_text_rect = gadget_text.get_rect(center=gadget_button.center)
    screen.blit(gadget_text, gadget_text_rect)
    
    # Bouton POUVOIR
    pouvoir_button = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, start_y + button_spacing, button_width, button_height)
    pygame.draw.rect(screen, (255, 0, 255), pouvoir_button)  # Magenta
    pygame.draw.rect(screen, WHITE, pouvoir_button, 2)
    pouvoir_text = font_button.render("POUVOIR", True, BLACK)
    pouvoir_text_rect = pouvoir_text.get_rect(center=pouvoir_button.center)
    screen.blit(pouvoir_text, pouvoir_text_rect)
    
    # Bouton OBJET
    objet_button = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, start_y + button_spacing * 2, button_width, button_height)
    pygame.draw.rect(screen, (0, 255, 0), objet_button)  # Vert
    pygame.draw.rect(screen, WHITE, objet_button, 2)
    objet_text = font_button.render("OBJET", True, BLACK)
    objet_text_rect = objet_text.get_rect(center=objet_button.center)
    screen.blit(objet_text, objet_text_rect)
    
    # Bouton CAPACITE
    capacite_button = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, start_y + button_spacing * 3, button_width, button_height)
    pygame.draw.rect(screen, (255, 165, 0), capacite_button)  # Orange
    pygame.draw.rect(screen, WHITE, capacite_button, 2)
    capacite_text = font_button.render("CAPACITÉ", True, BLACK)
    capacite_text_rect = capacite_text.get_rect(center=capacite_button.center)
    screen.blit(capacite_text, capacite_text_rect)
    
    # Bouton retour
    font_retour = pygame.font.Font(None, 36)
    retour_button = pygame.Rect(10, 10, 100, 40)
    pygame.draw.rect(screen, RED, retour_button)
    pygame.draw.rect(screen, WHITE, retour_button, 2)
    retour_text = font_retour.render("RETOUR", True, WHITE)
    retour_text_rect = retour_text.get_rect(center=retour_button.center)
    screen.blit(retour_text, retour_text_rect)
    
    return retour_button, gadget_button, pouvoir_button, objet_button, capacite_button

def draw_shop_pouvoir(screen, jeton_poche=0, pouvoir_items=None, crown_poche=0, item_description=None, level=1, inventaire_items=None, bon_marche_ameliore=False, capacite_items=None):
    """Dessine l'écran des items de pouvoir"""
    if pouvoir_items is None:
        pouvoir_items = []
    if inventaire_items is None:
        inventaire_items = {}
    if capacite_items is None:
        capacite_items = []
    
    # Calculer le niveau total de "bon marché" (nombre total d'achats)
    bon_marche_level = capacite_items.count("bon marché")
    
    # Réduction de prix : 5 par niveau (niveau 1 = 5, niveau 2 = 10, etc.)
    # Si amélioré avec couronnes, double la réduction
    price_reduction = bon_marche_level * 5
    if bon_marche_ameliore and bon_marche_level > 0:
        price_reduction *= 2
    
    screen.fill(BLACK)
    
    font_title = pygame.font.Font(None, 72)
    title_text = font_title.render("POUVOIR", True, YELLOW)
    title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, 100))
    screen.blit(title_text, title_rect)
    
    # Afficher les pacoins et couronnes disponibles
    font_info = pygame.font.Font(None, 36)
    pacoin_text = font_info.render(f"Pacoins: {jeton_poche}", True, WHITE)
    screen.blit(pacoin_text, (WINDOW_WIDTH//2 - 100, 150))
    crown_text = font_info.render(f"Couronnes: {crown_poche}", True, WHITE)
    screen.blit(crown_text, (WINDOW_WIDTH//2 - 100, 180))
    
    # Item "Longue vue"
    item_y = 220
    item_height = 55
    item_spacing = 65
    
    # Bouton "Longue vue" (aligné à gauche)
    button_width = 200  # Largeur réduite
    button_x = 20  # Aligné à gauche avec marge de 20
    button_x_right = WINDOW_WIDTH - button_width - 20  # Aligné à droite avec marge de 20
    longue_vue_button = pygame.Rect(button_x, item_y, button_width, item_height)
    # Mettre la longue vue en vert dans le magasin
    pygame.draw.rect(screen, (0, 255, 0), longue_vue_button)  # Vert vif
    pygame.draw.rect(screen, WHITE, longue_vue_button, 2)
    
    font_item = pygame.font.Font(None, 28)  # Police réduite pour que le texte rentre
    longue_vue_count = pouvoir_items.count("longue vue")
    longue_vue_name = f"Longue vue x{longue_vue_count}" if longue_vue_count > 0 else "Longue vue"
    longue_vue_text = font_item.render(longue_vue_name, True, BLACK)
    # Vérifier que le texte ne dépasse pas
    if longue_vue_text.get_width() > button_width - 10:
        longue_vue_name_short = f"L.vue x{longue_vue_count}" if longue_vue_count > 0 else "Longue vue"
        longue_vue_text = font_item.render(longue_vue_name_short, True, BLACK)
    longue_vue_text_rect = longue_vue_text.get_rect(center=(longue_vue_button.centerx, longue_vue_button.centery - 10))
    screen.blit(longue_vue_text, longue_vue_text_rect)
    
    font_price = pygame.font.Font(None, 20)  # Police réduite pour le prix
    longue_vue_price = max(0, 1000 - price_reduction)  # Prix réduit si "bon marché" est équipé
    price_text = font_price.render(f"Prix: {longue_vue_price} pacoins", True, BLACK)
    # Vérifier que le texte ne dépasse pas
    if price_text.get_width() > button_width - 10:
        price_text = font_price.render(f"{longue_vue_price} pacoins", True, BLACK)
    price_text_rect = price_text.get_rect(center=(longue_vue_button.centerx, longue_vue_button.centery + 10))
    screen.blit(price_text, price_text_rect)
    
    # Vérifier si déjà acheté
    if "longue vue" in pouvoir_items:
        font_owned = pygame.font.Font(None, 18)  # Police réduite
        owned_text = font_owned.render("(Déjà acheté)", True, BLACK)
        # Vérifier que le texte ne dépasse pas
        if owned_text.get_width() > button_width - 10:
            owned_text = font_owned.render("(Acheté)", True, BLACK)
        owned_text_rect = owned_text.get_rect(center=(longue_vue_button.centerx, longue_vue_button.centery + 22))
        screen.blit(owned_text, owned_text_rect)
    
    # Item "Double longue vue"
    double_longue_vue_y = item_y + item_spacing
    
    # Bouton "Double longue vue" (aligné à droite)
    double_longue_vue_button = pygame.Rect(button_x, double_longue_vue_y, button_width, item_height)
    pygame.draw.rect(screen, (100, 100, 255), double_longue_vue_button)
    pygame.draw.rect(screen, WHITE, double_longue_vue_button, 2)
    
    double_longue_vue_count = pouvoir_items.count("double longue vue")
    double_longue_vue_name = f"Double longue vue x{double_longue_vue_count}" if double_longue_vue_count > 0 else "Double longue vue"
    double_longue_vue_text = font_item.render(double_longue_vue_name, True, BLACK)
    # Vérifier que le texte ne dépasse pas
    if double_longue_vue_text.get_width() > button_width - 10:
        double_longue_vue_name_short = f"D.l.vue x{double_longue_vue_count}" if double_longue_vue_count > 0 else "Double l.vue"
        double_longue_vue_text = font_item.render(double_longue_vue_name_short, True, BLACK)
    double_longue_vue_text_rect = double_longue_vue_text.get_rect(center=(double_longue_vue_button.centerx, double_longue_vue_button.centery - 10))
    screen.blit(double_longue_vue_text, double_longue_vue_text_rect)
    
    double_longue_vue_price = max(0, 4000 - price_reduction)  # Prix réduit si "bon marché" est équipé
    double_longue_vue_price_text = font_price.render(f"Prix: {double_longue_vue_price} pacoins", True, BLACK)
    # Vérifier que le texte ne dépasse pas
    if double_longue_vue_price_text.get_width() > button_width - 10:
        double_longue_vue_price_text = font_price.render(f"{double_longue_vue_price} pacoins", True, BLACK)
    double_longue_vue_price_text_rect = double_longue_vue_price_text.get_rect(center=(double_longue_vue_button.centerx, double_longue_vue_button.centery + 10))
    screen.blit(double_longue_vue_price_text, double_longue_vue_price_text_rect)
    
    # Vérifier si déjà acheté
    if "double longue vue" in pouvoir_items:
        font_owned = pygame.font.Font(None, 18)  # Police réduite
        owned_text = font_owned.render("(Déjà acheté)", True, BLACK)
        # Vérifier que le texte ne dépasse pas
        if owned_text.get_width() > button_width - 10:
            owned_text = font_owned.render("(Acheté)", True, BLACK)
        owned_text_rect = owned_text.get_rect(center=(double_longue_vue_button.centerx, double_longue_vue_button.centery + 22))
        screen.blit(owned_text, owned_text_rect)
    
    # Item "Bon repas"
    bon_repas_y = double_longue_vue_y + item_spacing
    
    # Bouton "Bon repas" (aligné à droite)
    bon_repas_button = pygame.Rect(button_x, bon_repas_y, button_width, item_height)
    pygame.draw.rect(screen, (148, 0, 211), bon_repas_button)  # Violet
    pygame.draw.rect(screen, WHITE, bon_repas_button, 2)
    
    bon_repas_count = pouvoir_items.count("bon repas")
    bon_repas_name = f"Bon repas x{bon_repas_count}" if bon_repas_count > 0 else "Bon repas"
    bon_repas_text = font_item.render(bon_repas_name, True, BLACK)
    bon_repas_text_rect = bon_repas_text.get_rect(center=(bon_repas_button.centerx, bon_repas_button.centery - 10))
    screen.blit(bon_repas_text, bon_repas_text_rect)
    
    bon_repas_price = max(0, 2000 - price_reduction)  # Prix réduit si "bon marché" est équipé
    bon_repas_price_text = font_price.render(f"Prix: {bon_repas_price} pacoins", True, BLACK)
    # Vérifier que le texte ne dépasse pas
    if bon_repas_price_text.get_width() > button_width - 10:
        bon_repas_price_text = font_price.render(f"{bon_repas_price} pacoins", True, BLACK)
    bon_repas_price_text_rect = bon_repas_price_text.get_rect(center=(bon_repas_button.centerx, bon_repas_button.centery + 10))
    screen.blit(bon_repas_price_text, bon_repas_price_text_rect)
    
    # Vérifier si déjà acheté
    if "bon repas" in pouvoir_items:
        font_owned = pygame.font.Font(None, 18)  # Police réduite
        owned_text = font_owned.render("(Déjà acheté)", True, BLACK)
        # Vérifier que le texte ne dépasse pas
        if owned_text.get_width() > button_width - 10:
            owned_text = font_owned.render("(Acheté)", True, BLACK)
        owned_text_rect = owned_text.get_rect(center=(bon_repas_button.centerx, bon_repas_button.centery + 22))
        screen.blit(owned_text, owned_text_rect)
    
    # Item "Bon goût"
    bon_gout_y = bon_repas_y + item_spacing
    
    # Bouton "Bon goût" (aligné à droite)
    bon_gout_button = pygame.Rect(button_x, bon_gout_y, button_width, item_height)
    pygame.draw.rect(screen, (148, 0, 211), bon_gout_button)  # Violet
    pygame.draw.rect(screen, WHITE, bon_gout_button, 2)
    
    bon_gout_count = pouvoir_items.count("bon goût")
    bon_gout_name = f"Bon goût x{bon_gout_count}" if bon_gout_count > 0 else "Bon goût"
    bon_gout_text = font_item.render(bon_gout_name, True, BLACK)
    bon_gout_text_rect = bon_gout_text.get_rect(center=(bon_gout_button.centerx, bon_gout_button.centery - 10))
    screen.blit(bon_gout_text, bon_gout_text_rect)
    
    bon_gout_price = max(0, 3000 - price_reduction)  # Prix réduit si "bon marché" est équipé
    bon_gout_price_text = font_price.render(f"Prix: {bon_gout_price} pacoins", True, BLACK)
    # Vérifier que le texte ne dépasse pas
    if bon_gout_price_text.get_width() > button_width - 10:
        bon_gout_price_text = font_price.render(f"{bon_gout_price} pacoins", True, BLACK)
    bon_gout_price_text_rect = bon_gout_price_text.get_rect(center=(bon_gout_button.centerx, bon_gout_button.centery + 10))
    screen.blit(bon_gout_price_text, bon_gout_price_text_rect)
    
    # Vérifier si déjà acheté
    if "bon goût" in pouvoir_items:
        font_owned = pygame.font.Font(None, 18)  # Police réduite
        owned_text = font_owned.render("(Déjà acheté)", True, BLACK)
        # Vérifier que le texte ne dépasse pas
        if owned_text.get_width() > button_width - 10:
            owned_text = font_owned.render("(Acheté)", True, BLACK)
        owned_text_rect = owned_text.get_rect(center=(bon_gout_button.centerx, bon_gout_button.centery + 22))
        screen.blit(owned_text, owned_text_rect)
    
    # Item "Pas d'indigestion"
    pas_indigestion_y = bon_gout_y + item_spacing
    
    # Bouton "Pas d'indigestion" (aligné à droite)
    pas_indigestion_button = pygame.Rect(button_x, pas_indigestion_y, button_width, item_height)
    pygame.draw.rect(screen, (148, 0, 211), pas_indigestion_button)  # Violet
    pygame.draw.rect(screen, WHITE, pas_indigestion_button, 2)
    
    pas_indigestion_count = pouvoir_items.count("pas d'indigestion")
    pas_indigestion_name = f"Pas d'indigestion x{pas_indigestion_count}" if pas_indigestion_count > 0 else "Pas d'indigestion"
    pas_indigestion_text = font_item.render(pas_indigestion_name, True, BLACK)
    # Vérifier que le texte ne dépasse pas
    if pas_indigestion_text.get_width() > button_width - 10:
        pas_indigestion_name_short = f"Pas indigestion x{pas_indigestion_count}" if pas_indigestion_count > 0 else "Pas indigestion"
        pas_indigestion_text = font_item.render(pas_indigestion_name_short, True, BLACK)
    pas_indigestion_text_rect = pas_indigestion_text.get_rect(center=(pas_indigestion_button.centerx, pas_indigestion_button.centery - 10))
    screen.blit(pas_indigestion_text, pas_indigestion_text_rect)
    
    pas_indigestion_price = max(0, 5000 - price_reduction)  # Prix réduit si "bon marché" est équipé
    pas_indigestion_price_text = font_price.render(f"Prix: {pas_indigestion_price} pacoins", True, BLACK)
    # Vérifier que le texte ne dépasse pas
    if pas_indigestion_price_text.get_width() > button_width - 10:
        pas_indigestion_price_text = font_price.render(f"{pas_indigestion_price} pacoins", True, BLACK)
    pas_indigestion_price_text_rect = pas_indigestion_price_text.get_rect(center=(pas_indigestion_button.centerx, pas_indigestion_button.centery + 10))
    screen.blit(pas_indigestion_price_text, pas_indigestion_price_text_rect)
    
    # Vérifier si déjà acheté
    if "pas d'indigestion" in pouvoir_items:
        font_owned = pygame.font.Font(None, 18)  # Police réduite
        owned_text = font_owned.render("(Déjà acheté)", True, BLACK)
        # Vérifier que le texte ne dépasse pas
        if owned_text.get_width() > button_width - 10:
            owned_text = font_owned.render("(Acheté)", True, BLACK)
        owned_text_rect = owned_text.get_rect(center=(pas_indigestion_button.centerx, pas_indigestion_button.centery + 22))
        screen.blit(owned_text, owned_text_rect)
    
    # Bouton retour
    font_retour = pygame.font.Font(None, 36)
    retour_button = pygame.Rect(10, 10, 100, 40)
    pygame.draw.rect(screen, RED, retour_button)
    pygame.draw.rect(screen, WHITE, retour_button, 2)
    retour_text = font_retour.render("RETOUR", True, WHITE)
    retour_text_rect = retour_text.get_rect(center=retour_button.center)
    screen.blit(retour_text, retour_text_rect)
    
    # Item "Skin bleu" (en haut à droite)
    skin_bleu_y = item_y  # Même niveau que "Longue vue"
    
    # Bouton "Skin bleu" (aligné à droite)
    skin_bleu_button = pygame.Rect(button_x_right, skin_bleu_y, button_width, item_height)
    pygame.draw.rect(screen, YELLOW, skin_bleu_button)  # Jaune
    pygame.draw.rect(screen, WHITE, skin_bleu_button, 2)
    
    skin_bleu_count = pouvoir_items.count("skin bleu")
    skin_bleu_name = f"Skin bleu x{skin_bleu_count}" if skin_bleu_count > 0 else "Skin bleu"
    skin_bleu_text = font_item.render(skin_bleu_name, True, BLACK)
    skin_bleu_text_rect = skin_bleu_text.get_rect(center=(skin_bleu_button.centerx, skin_bleu_button.centery - 10))
    screen.blit(skin_bleu_text, skin_bleu_text_rect)
    
    skin_bleu_price = max(0, 10000 - price_reduction)  # Prix réduit si "bon marché" est équipé (seulement pour les pacoins)
    skin_bleu_price_text = font_price.render(f"{skin_bleu_price} pacoins et 1000 couronnes", True, BLACK)
    # Vérifier que le texte ne dépasse pas et le diviser en deux lignes si nécessaire
    if skin_bleu_price_text.get_width() > button_width - 10:
        # Diviser en deux lignes
        skin_bleu_price_text1 = font_price.render(f"{skin_bleu_price} pacoins", True, BLACK)
        skin_bleu_price_text2 = font_price.render("1000 couronnes", True, BLACK)
        skin_bleu_price_text_rect1 = skin_bleu_price_text1.get_rect(center=(skin_bleu_button.centerx, skin_bleu_button.centery + 5))
        skin_bleu_price_text_rect2 = skin_bleu_price_text2.get_rect(center=(skin_bleu_button.centerx, skin_bleu_button.centery + 15))
        screen.blit(skin_bleu_price_text1, skin_bleu_price_text_rect1)
        screen.blit(skin_bleu_price_text2, skin_bleu_price_text_rect2)
    else:
        skin_bleu_price_text_rect = skin_bleu_price_text.get_rect(center=(skin_bleu_button.centerx, skin_bleu_button.centery + 10))
        screen.blit(skin_bleu_price_text, skin_bleu_price_text_rect)
    
    # Vérifier si déjà acheté
    if "skin bleu" in pouvoir_items:
        font_owned = pygame.font.Font(None, 18)  # Police réduite
        owned_text = font_owned.render("(Déjà acheté)", True, BLACK)
        # Vérifier que le texte ne dépasse pas
        if owned_text.get_width() > button_width - 10:
            owned_text = font_owned.render("(Acheté)", True, BLACK)
        owned_text_rect = owned_text.get_rect(center=(skin_bleu_button.centerx, skin_bleu_button.centery + 22))
        screen.blit(owned_text, owned_text_rect)
    
    # Item "Skin orange" (juste en dessous de "Skin bleu")
    skin_orange_y = skin_bleu_y + item_spacing
    
    # Bouton "Skin orange" (aligné à droite)
    skin_orange_button = pygame.Rect(button_x_right, skin_orange_y, button_width, item_height)
    pygame.draw.rect(screen, YELLOW, skin_orange_button)  # Jaune
    pygame.draw.rect(screen, WHITE, skin_orange_button, 2)
    
    skin_orange_count = pouvoir_items.count("skin orange")
    skin_orange_name = f"Skin orange x{skin_orange_count}" if skin_orange_count > 0 else "Skin orange"
    skin_orange_text = font_item.render(skin_orange_name, True, BLACK)
    skin_orange_text_rect = skin_orange_text.get_rect(center=(skin_orange_button.centerx, skin_orange_button.centery - 10))
    screen.blit(skin_orange_text, skin_orange_text_rect)
    
    skin_orange_price = max(0, 10000 - price_reduction)  # Prix réduit si "bon marché" est équipé (seulement pour les pacoins)
    skin_orange_price_text = font_price.render(f"{skin_orange_price} pacoins et 1000 couronnes", True, BLACK)
    # Vérifier que le texte ne dépasse pas et le diviser en deux lignes si nécessaire
    if skin_orange_price_text.get_width() > button_width - 10:
        # Diviser en deux lignes
        skin_orange_price_text1 = font_price.render(f"{skin_orange_price} pacoins", True, BLACK)
        skin_orange_price_text2 = font_price.render("1000 couronnes", True, BLACK)
        skin_orange_price_text_rect1 = skin_orange_price_text1.get_rect(center=(skin_orange_button.centerx, skin_orange_button.centery + 5))
        skin_orange_price_text_rect2 = skin_orange_price_text2.get_rect(center=(skin_orange_button.centerx, skin_orange_button.centery + 15))
        screen.blit(skin_orange_price_text1, skin_orange_price_text_rect1)
        screen.blit(skin_orange_price_text2, skin_orange_price_text_rect2)
    else:
        skin_orange_price_text_rect = skin_orange_price_text.get_rect(center=(skin_orange_button.centerx, skin_orange_button.centery + 10))
        screen.blit(skin_orange_price_text, skin_orange_price_text_rect)
    
    # Vérifier si déjà acheté
    if "skin orange" in pouvoir_items:
        font_owned = pygame.font.Font(None, 18)  # Police réduite
        owned_text = font_owned.render("(Déjà acheté)", True, BLACK)
        # Vérifier que le texte ne dépasse pas
        if owned_text.get_width() > button_width - 10:
            owned_text = font_owned.render("(Acheté)", True, BLACK)
        owned_text_rect = owned_text.get_rect(center=(skin_orange_button.centerx, skin_orange_button.centery + 22))
        screen.blit(owned_text, owned_text_rect)
    
    # Item "Glace" (en dessous de "Skin orange")
    glace_y = skin_orange_y + item_spacing
    
    # Bouton "Glace" (aligné à droite)
    glace_button = pygame.Rect(button_x_right, glace_y, button_width, item_height)
    pygame.draw.rect(screen, (148, 0, 211), glace_button)  # Violet
    pygame.draw.rect(screen, WHITE, glace_button, 2)
    
    glace_count = pouvoir_items.count("glace")
    glace_name = f"Glace x{glace_count}" if glace_count > 0 else "Glace"
    glace_text = font_item.render(glace_name, True, BLACK)
    glace_text_rect = glace_text.get_rect(center=(glace_button.centerx, glace_button.centery - 10))
    screen.blit(glace_text, glace_text_rect)
    
    glace_price = max(0, 3000 - price_reduction)  # Prix réduit si "bon marché" est équipé (seulement pour les pacoins)
    glace_price_text = font_price.render(f"Prix: {glace_price} pacoins et 100 couronnes", True, BLACK)
    # Vérifier que le texte ne dépasse pas et le diviser en deux lignes si nécessaire
    if glace_price_text.get_width() > button_width - 10:
        # Diviser en deux lignes
        glace_price_text1 = font_price.render(f"{glace_price} pacoins", True, BLACK)
        glace_price_text2 = font_price.render("100 couronnes", True, BLACK)
        glace_price_text_rect1 = glace_price_text1.get_rect(center=(glace_button.centerx, glace_button.centery + 5))
        glace_price_text_rect2 = glace_price_text2.get_rect(center=(glace_button.centerx, glace_button.centery + 15))
        screen.blit(glace_price_text1, glace_price_text_rect1)
        screen.blit(glace_price_text2, glace_price_text_rect2)
    else:
        glace_price_text_rect = glace_price_text.get_rect(center=(glace_button.centerx, glace_button.centery + 10))
        screen.blit(glace_price_text, glace_price_text_rect)
    
    # Vérifier si déjà acheté
    if "glace" in pouvoir_items:
        font_owned = pygame.font.Font(None, 18)  # Police réduite
        owned_text = font_owned.render("(Déjà acheté)", True, BLACK)
        # Vérifier que le texte ne dépasse pas
        if owned_text.get_width() > button_width - 10:
            owned_text = font_owned.render("(Acheté)", True, BLACK)
        owned_text_rect = owned_text.get_rect(center=(glace_button.centerx, glace_button.centery + 22))
        screen.blit(owned_text, owned_text_rect)
    
    # Item "Skin rose" (en dessous de "Glace")
    skin_rose_y = glace_y + item_spacing
    
    # Bouton "Skin rose" (aligné à droite)
    skin_rose_button = pygame.Rect(button_x_right, skin_rose_y, button_width, item_height)
    pygame.draw.rect(screen, YELLOW, skin_rose_button)  # Jaune
    pygame.draw.rect(screen, WHITE, skin_rose_button, 2)
    
    skin_rose_count = pouvoir_items.count("skin rose")
    skin_rose_name = f"Skin rose x{skin_rose_count}" if skin_rose_count > 0 else "Skin rose"
    skin_rose_text = font_item.render(skin_rose_name, True, BLACK)
    skin_rose_text_rect = skin_rose_text.get_rect(center=(skin_rose_button.centerx, skin_rose_button.centery - 10))
    screen.blit(skin_rose_text, skin_rose_text_rect)
    
    skin_rose_price = max(0, 10000 - price_reduction)  # Prix réduit si "bon marché" est équipé (seulement pour les pacoins)
    skin_rose_price_text = font_price.render(f"{skin_rose_price} pacoins et 1000 couronnes", True, BLACK)
    # Vérifier que le texte ne dépasse pas et le diviser en deux lignes si nécessaire
    if skin_rose_price_text.get_width() > button_width - 10:
        # Diviser en deux lignes
        skin_rose_price_text1 = font_price.render(f"{skin_rose_price} pacoins", True, BLACK)
        skin_rose_price_text2 = font_price.render("1000 couronnes", True, BLACK)
        skin_rose_price_text_rect1 = skin_rose_price_text1.get_rect(center=(skin_rose_button.centerx, skin_rose_button.centery + 5))
        skin_rose_price_text_rect2 = skin_rose_price_text2.get_rect(center=(skin_rose_button.centerx, skin_rose_button.centery + 15))
        screen.blit(skin_rose_price_text1, skin_rose_price_text_rect1)
        screen.blit(skin_rose_price_text2, skin_rose_price_text_rect2)
    else:
        skin_rose_price_text_rect = skin_rose_price_text.get_rect(center=(skin_rose_button.centerx, skin_rose_button.centery + 10))
        screen.blit(skin_rose_price_text, skin_rose_price_text_rect)
    
    # Vérifier si déjà acheté
    if "skin rose" in pouvoir_items:
        font_owned = pygame.font.Font(None, 18)  # Police réduite
        owned_text = font_owned.render("(Déjà acheté)", True, BLACK)
        # Vérifier que le texte ne dépasse pas
        if owned_text.get_width() > button_width - 10:
            owned_text = font_owned.render("(Acheté)", True, BLACK)
        owned_text_rect = owned_text.get_rect(center=(skin_rose_button.centerx, skin_rose_button.centery + 22))
        screen.blit(owned_text, owned_text_rect)
    
    # Item "Skin rouge" (en dessous de "Skin rose")
    skin_rouge_y = skin_rose_y + item_spacing
    
    # Bouton "Skin rouge" (aligné à droite)
    skin_rouge_button = pygame.Rect(button_x_right, skin_rouge_y, button_width, item_height)
    pygame.draw.rect(screen, YELLOW, skin_rouge_button)  # Jaune
    pygame.draw.rect(screen, WHITE, skin_rouge_button, 2)
    
    skin_rouge_count = pouvoir_items.count("skin rouge")
    skin_rouge_name = f"Skin rouge x{skin_rouge_count}" if skin_rouge_count > 0 else "Skin rouge"
    skin_rouge_text = font_item.render(skin_rouge_name, True, BLACK)
    skin_rouge_text_rect = skin_rouge_text.get_rect(center=(skin_rouge_button.centerx, skin_rouge_button.centery - 10))
    screen.blit(skin_rouge_text, skin_rouge_text_rect)
    
    skin_rouge_price = max(0, 10000 - price_reduction)  # Prix réduit si "bon marché" est équipé (seulement pour les pacoins)
    skin_rouge_price_text = font_price.render(f"{skin_rouge_price} pacoins et 1000 couronnes", True, BLACK)
    # Vérifier que le texte ne dépasse pas et le diviser en deux lignes si nécessaire
    if skin_rouge_price_text.get_width() > button_width - 10:
        # Diviser en deux lignes
        skin_rouge_price_text1 = font_price.render(f"{skin_rouge_price} pacoins", True, BLACK)
        skin_rouge_price_text2 = font_price.render("1000 couronnes", True, BLACK)
        skin_rouge_price_text_rect1 = skin_rouge_price_text1.get_rect(center=(skin_rouge_button.centerx, skin_rouge_button.centery + 5))
        skin_rouge_price_text_rect2 = skin_rouge_price_text2.get_rect(center=(skin_rouge_button.centerx, skin_rouge_button.centery + 15))
        screen.blit(skin_rouge_price_text1, skin_rouge_price_text_rect1)
        screen.blit(skin_rouge_price_text2, skin_rouge_price_text_rect2)
    else:
        skin_rouge_price_text_rect = skin_rouge_price_text.get_rect(center=(skin_rouge_button.centerx, skin_rouge_button.centery + 10))
        screen.blit(skin_rouge_price_text, skin_rouge_price_text_rect)
    
    # Vérifier si déjà acheté
    if "skin rouge" in pouvoir_items:
        font_owned = pygame.font.Font(None, 18)  # Police réduite
        owned_text = font_owned.render("(Déjà acheté)", True, BLACK)
        # Vérifier que le texte ne dépasse pas
        if owned_text.get_width() > button_width - 10:
            owned_text = font_owned.render("(Acheté)", True, BLACK)
        owned_text_rect = owned_text.get_rect(center=(skin_rouge_button.centerx, skin_rouge_button.centery + 22))
        screen.blit(owned_text, owned_text_rect)
    
    # Détecter quel item est survolé pour afficher sa rareté
    mouse_pos = pygame.mouse.get_pos()
    hovered_item_type = None
    if longue_vue_button.collidepoint(mouse_pos):
        hovered_item_type = 'longue vue'
    elif double_longue_vue_button.collidepoint(mouse_pos):
        hovered_item_type = 'double longue vue'
    elif bon_repas_button.collidepoint(mouse_pos):
        hovered_item_type = 'bon repas'
    elif bon_gout_button.collidepoint(mouse_pos):
        hovered_item_type = 'bon goût'
    elif pas_indigestion_button.collidepoint(mouse_pos):
        hovered_item_type = 'pas d\'indigestion'
    elif glace_button.collidepoint(mouse_pos):
        hovered_item_type = 'glace'
    elif skin_bleu_button.collidepoint(mouse_pos):
        hovered_item_type = 'skin bleu'
    elif skin_orange_button.collidepoint(mouse_pos):
        hovered_item_type = 'skin orange'
    elif skin_rose_button.collidepoint(mouse_pos):
        hovered_item_type = 'skin rose'
    elif skin_rouge_button.collidepoint(mouse_pos):
        hovered_item_type = 'skin rouge'
    
    # Afficher la description de l'item si elle existe ou si on survole un objet
    if item_description or hovered_item_type:
        # Zone de description en bas de l'écran
        desc_y = WINDOW_HEIGHT - 120
        desc_height = 100
        desc_rect = pygame.Rect(10, desc_y, WINDOW_WIDTH - 20, desc_height)
        pygame.draw.rect(screen, (50, 50, 50), desc_rect)
        pygame.draw.rect(screen, WHITE, desc_rect, 2)
        
        # Afficher la rareté si on survole un objet
        if hovered_item_type:
            rarity_name, rarity_color = get_item_rarity(hovered_item_type)
            font_rarity = pygame.font.Font(None, 28)
            rarity_text = font_rarity.render(f"Rareté: {rarity_name}", True, rarity_color)
            rarity_text_rect = rarity_text.get_rect(x=20, y=desc_y + 10)
            screen.blit(rarity_text, rarity_text_rect)
        
        # Afficher le texte de description si elle existe
        if item_description:
            font_desc = pygame.font.Font(None, 24)
            # Diviser le texte en lignes si nécessaire
            words = item_description.split(' ')
            lines = []
            current_line = ""
            for word in words:
                test_line = current_line + word + " " if current_line else word + " "
                text_width = font_desc.size(test_line)[0]
                if text_width > WINDOW_WIDTH - 40:
                    if current_line:
                        lines.append(current_line)
                    current_line = word + " "
                else:
                    current_line = test_line
            if current_line:
                lines.append(current_line)
            
            # Afficher les lignes (limiter à 3 lignes maximum si rareté affichée, sinon 4)
            max_lines = min(len(lines), 3 if hovered_item_type else 4)
            start_y = desc_y + 40 if hovered_item_type else desc_y + 10
            for i in range(max_lines):
                desc_text = font_desc.render(lines[i], True, WHITE)
                screen.blit(desc_text, (20, start_y + i * 25))
    
    return retour_button, longue_vue_button, double_longue_vue_button, bon_repas_button, bon_gout_button, pas_indigestion_button, glace_button, skin_bleu_button, skin_orange_button, skin_rose_button, skin_rouge_button

def draw_shop_gadget(screen, jeton_poche=0, gadget_items=None, crown_poche=0, item_description=None, level=1, inventaire_items=None, bon_marche_ameliore=False, capacite_items=None):
    """Dessine l'écran des items de gadget"""
    if gadget_items is None:
        gadget_items = []
    if inventaire_items is None:
        inventaire_items = {}
    if capacite_items is None:
        capacite_items = []
    
    # Calculer le niveau total de "bon marché" (nombre total d'achats)
    bon_marche_level = capacite_items.count("bon marché")
    
    # Réduction de prix : 5 par niveau (niveau 1 = 5, niveau 2 = 10, etc.)
    # Si amélioré avec couronnes, double la réduction
    price_reduction = bon_marche_level * 5
    if bon_marche_ameliore and bon_marche_level > 0:
        price_reduction *= 2
    
    screen.fill(BLACK)
    
    font_title = pygame.font.Font(None, 72)
    title_text = font_title.render("GADGET", True, YELLOW)
    title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, 100))
    screen.blit(title_text, title_rect)
    
    # Afficher les pacoins et couronnes disponibles
    font_info = pygame.font.Font(None, 36)
    pacoin_text = font_info.render(f"Pacoins: {jeton_poche}", True, WHITE)
    screen.blit(pacoin_text, (WINDOW_WIDTH//2 - 100, 150))
    crown_text = font_info.render(f"Couronnes: {crown_poche}", True, WHITE)
    screen.blit(crown_text, (WINDOW_WIDTH//2 - 100, 180))
    
    # Bouton retour
    font_retour = pygame.font.Font(None, 36)
    retour_button = pygame.Rect(10, 10, 100, 40)
    pygame.draw.rect(screen, RED, retour_button)
    pygame.draw.rect(screen, WHITE, retour_button, 2)
    retour_text = font_retour.render("RETOUR", True, WHITE)
    retour_text_rect = retour_text.get_rect(center=retour_button.center)
    screen.blit(retour_text, retour_text_rect)
    
    # Afficher la description de l'item si elle existe
    if item_description:
        # Zone de description en bas de l'écran
        desc_y = WINDOW_HEIGHT - 120
        desc_height = 100
        desc_rect = pygame.Rect(10, desc_y, WINDOW_WIDTH - 20, desc_height)
        pygame.draw.rect(screen, (50, 50, 50), desc_rect)
        pygame.draw.rect(screen, WHITE, desc_rect, 2)
        
        # Afficher le texte de description
        font_desc = pygame.font.Font(None, 24)
        # Diviser le texte en lignes si nécessaire
        words = item_description.split(' ')
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + word + " " if current_line else word + " "
            text_width = font_desc.size(test_line)[0]
            if text_width > WINDOW_WIDTH - 40:
                if current_line:
                    lines.append(current_line)
                current_line = word + " "
            else:
                current_line = test_line
        if current_line:
            lines.append(current_line)
        
        # Afficher les lignes (limiter à 4 lignes maximum)
        max_lines = min(len(lines), 4)
        for i in range(max_lines):
            desc_text = font_desc.render(lines[i], True, WHITE)
            screen.blit(desc_text, (20, desc_y + 10 + i * 25))
    
    # Item "Explosion"
    item_y = 220
    item_height = 55
    item_spacing = 65
    button_width = 200
    button_x = 20
    button_x_right = WINDOW_WIDTH - button_width - 20
    
    # Polices pour les items et prix
    font_item = pygame.font.Font(None, 28)
    font_price = pygame.font.Font(None, 20)
    
    # Bouton "Explosion" (aligné à gauche)
    explosion_button = pygame.Rect(button_x, item_y, button_width, item_height)
    pygame.draw.rect(screen, (128, 0, 128), explosion_button)  # Violet
    pygame.draw.rect(screen, WHITE, explosion_button, 2)
    
    explosion_count = gadget_items.count("explosion")
    explosion_name = f"Explosion x{explosion_count}" if explosion_count > 0 else "Explosion"
    explosion_text = font_item.render(explosion_name, True, BLACK)
    explosion_text_rect = explosion_text.get_rect(center=(explosion_button.centerx, explosion_button.centery - 10))
    screen.blit(explosion_text, explosion_text_rect)
    
    explosion_price = max(0, 10000 - price_reduction)  # Prix réduit si "bon marché" est équipé
    explosion_price_text = font_price.render(f"Prix: {explosion_price} pacoins", True, BLACK)
    explosion_price_text_rect = explosion_price_text.get_rect(center=(explosion_button.centerx, explosion_button.centery + 10))
    screen.blit(explosion_price_text, explosion_price_text_rect)
    
    # Vérifier si déjà acheté
    if "explosion" in gadget_items:
        font_owned = pygame.font.Font(None, 18)
        owned_text = font_owned.render("(Déjà acheté)", True, BLACK)
        if owned_text.get_width() > button_width - 10:
            owned_text = font_owned.render("(Acheté)", True, BLACK)
        owned_text_rect = owned_text.get_rect(center=(explosion_button.centerx, explosion_button.centery + 22))
        screen.blit(owned_text, owned_text_rect)
    
    # Bouton "Vision X" (aligné à gauche, en dessous de Explosion)
    vision_x_button = pygame.Rect(button_x, item_y + item_spacing, button_width, item_height)
    pygame.draw.rect(screen, (128, 0, 128), vision_x_button)  # Violet
    pygame.draw.rect(screen, WHITE, vision_x_button, 2)
    
    vision_x_count = gadget_items.count("vision x")
    vision_x_name = f"Vision X x{vision_x_count}" if vision_x_count > 0 else "Vision X"
    vision_x_text = font_item.render(vision_x_name, True, BLACK)
    vision_x_text_rect = vision_x_text.get_rect(center=(vision_x_button.centerx, vision_x_button.centery - 10))
    screen.blit(vision_x_text, vision_x_text_rect)
    
    vision_x_price = max(0, 10000 - price_reduction)  # Prix réduit si "bon marché" est équipé
    vision_x_price_text = font_price.render(f"Prix: {vision_x_price} pacoins", True, BLACK)
    vision_x_price_text_rect = vision_x_price_text.get_rect(center=(vision_x_button.centerx, vision_x_button.centery + 10))
    screen.blit(vision_x_price_text, vision_x_price_text_rect)
    
    # Vérifier si déjà acheté
    if "vision x" in gadget_items:
        font_owned = pygame.font.Font(None, 18)
        owned_text = font_owned.render("(Déjà acheté)", True, BLACK)
        if owned_text.get_width() > button_width - 10:
            owned_text = font_owned.render("(Acheté)", True, BLACK)
        owned_text_rect = owned_text.get_rect(center=(vision_x_button.centerx, vision_x_button.centery + 22))
        screen.blit(owned_text, owned_text_rect)
    
    # Gestion du survol pour afficher la description
    mouse_pos = pygame.mouse.get_pos()
    hovered_item_type = None
    if explosion_button.collidepoint(mouse_pos):
        item_description = "Explosion: Utilisez le clic gauche de la souris pour activer. Tue tous les fantômes sur le terrain. Vous ne récupérez pas de couronnes. Temps de recharge de 1 minute entre chaque utilisation."
        hovered_item_type = 'explosion'
    elif vision_x_button.collidepoint(mouse_pos):
        item_description = "Vision X: Utilisez le clic gauche de la souris pour activer. Fait disparaître tous les fantômes d'indigestion sur le terrain. Temps de recharge de 1 minute entre chaque utilisation."
        hovered_item_type = 'vision x'
    
    # Bouton "Feu" (aligné à droite, même niveau que Explosion)
    feu_button = pygame.Rect(button_x_right, item_y, button_width, item_height)
    pygame.draw.rect(screen, (128, 0, 128), feu_button)  # Violet
    pygame.draw.rect(screen, WHITE, feu_button, 2)
    
    feu_count = gadget_items.count("feu")
    feu_name = f"Feu x{feu_count}" if feu_count > 0 else "Feu"
    feu_text = font_item.render(feu_name, True, BLACK)
    feu_text_rect = feu_text.get_rect(center=(feu_button.centerx, feu_button.centery - 10))
    screen.blit(feu_text, feu_text_rect)
    
    feu_price = max(0, 5000 - price_reduction)  # Prix réduit si "bon marché" est équipé
    feu_price_text = font_price.render(f"Prix: {feu_price} pacoins", True, BLACK)
    feu_price_text_rect = feu_price_text.get_rect(center=(feu_button.centerx, feu_button.centery + 10))
    screen.blit(feu_price_text, feu_price_text_rect)
    
    # Vérifier si déjà acheté
    if "feu" in gadget_items:
        font_owned = pygame.font.Font(None, 18)
        owned_text = font_owned.render("(Déjà acheté)", True, BLACK)
        if owned_text.get_width() > button_width - 10:
            owned_text = font_owned.render("(Acheté)", True, BLACK)
        owned_text_rect = owned_text.get_rect(center=(feu_button.centerx, feu_button.centery + 22))
        screen.blit(owned_text, owned_text_rect)
    
    # Mettre à jour la description pour "feu"
    if feu_button.collidepoint(mouse_pos):
        item_description = "Feu: Utilisez le clic gauche de la souris pour activer. Place du feu derrière Pacman lorsqu'il se déplace. Si un fantôme marche dessus, il vous fuit pendant 10 secondes. Temps de recharge de 1 minute entre chaque utilisation."
        hovered_item_type = 'feu'
    
    # Bouton "Tir" (aligné à droite, en dessous de Feu)
    tir_button = pygame.Rect(button_x_right, item_y + item_spacing, button_width, item_height)
    pygame.draw.rect(screen, (0, 255, 0), tir_button)  # Vert
    pygame.draw.rect(screen, WHITE, tir_button, 2)
    
    tir_count = gadget_items.count("tir")
    tir_name = f"Tir x{tir_count}" if tir_count > 0 else "Tir"
    tir_text = font_item.render(tir_name, True, BLACK)
    tir_text_rect = tir_text.get_rect(center=(tir_button.centerx, tir_button.centery - 10))
    screen.blit(tir_text, tir_text_rect)
    
    tir_price = max(0, 1000 - price_reduction)  # Prix réduit si "bon marché" est équipé
    tir_price_text = font_price.render(f"Prix: {tir_price} pacoins", True, BLACK)
    tir_price_text_rect = tir_price_text.get_rect(center=(tir_button.centerx, tir_button.centery + 10))
    screen.blit(tir_price_text, tir_price_text_rect)
    
    # Vérifier si déjà acheté
    if "tir" in gadget_items:
        font_owned = pygame.font.Font(None, 18)
        owned_text = font_owned.render("(Déjà acheté)", True, BLACK)
        if owned_text.get_width() > button_width - 10:
            owned_text = font_owned.render("(Acheté)", True, BLACK)
        owned_text_rect = owned_text.get_rect(center=(tir_button.centerx, tir_button.centery + 22))
        screen.blit(owned_text, owned_text_rect)
    
    # Mettre à jour la description pour "tir"
    if tir_button.collidepoint(mouse_pos):
        item_description = "Tir: Utilisez le clic gauche de la souris pour activer. Tue un fantôme dans votre champ de vision (direction où vous regardez). Vous ne récupérez pas de couronnes. Temps de recharge de 1 minute entre chaque utilisation."
        hovered_item_type = 'tir'
    
    # Bouton "Mort" (aligné à droite, en dessous de Tir)
    mort_button = pygame.Rect(button_x_right, item_y + item_spacing * 2, button_width, item_height)
    pygame.draw.rect(screen, (255, 255, 0), mort_button)  # Jaune
    pygame.draw.rect(screen, WHITE, mort_button, 2)
    
    mort_count = gadget_items.count("mort")
    mort_name = f"Mort x{mort_count}" if mort_count > 0 else "Mort"
    mort_text = font_item.render(mort_name, True, BLACK)
    mort_text_rect = mort_text.get_rect(center=(mort_button.centerx, mort_button.centery - 10))
    screen.blit(mort_text, mort_text_rect)
    
    mort_price = max(0, 15000 - price_reduction)  # Prix réduit si "bon marché" est équipé
    mort_price_text = font_price.render(f"Prix: {mort_price} pacoins", True, BLACK)
    mort_price_text_rect = mort_price_text.get_rect(center=(mort_button.centerx, mort_button.centery + 10))
    screen.blit(mort_price_text, mort_price_text_rect)
    
    # Vérifier si déjà acheté
    if "mort" in gadget_items:
        font_owned = pygame.font.Font(None, 18)
        owned_text = font_owned.render("(Déjà acheté)", True, BLACK)
        if owned_text.get_width() > button_width - 10:
            owned_text = font_owned.render("(Acheté)", True, BLACK)
        owned_text_rect = owned_text.get_rect(center=(mort_button.centerx, mort_button.centery + 22))
        screen.blit(owned_text, owned_text_rect)
    
    # Mettre à jour la description pour "mort"
    if mort_button.collidepoint(mouse_pos):
        item_description = "Mort: Utilisez le clic gauche de la souris pour activer. Tue définitivement le fantôme le plus proche de vous, peu importe sa position. Le fantôme ne réapparaîtra plus. Temps de recharge de 1 minute entre chaque utilisation."
        hovered_item_type = 'mort'
    
    # Bouton "Bombe Téléguidée" (aligné à gauche, en dessous de Vision X)
    bombe_button = pygame.Rect(button_x, item_y + item_spacing * 2, button_width, item_height)
    pygame.draw.rect(screen, (0, 255, 0), bombe_button)  # Vert
    pygame.draw.rect(screen, WHITE, bombe_button, 2)
    
    bombe_count = gadget_items.count("bombe téléguidée")
    bombe_name = f"Bombe Téléguidée x{bombe_count}" if bombe_count > 0 else "Bombe Téléguidée"
    bombe_text = font_item.render(bombe_name, True, BLACK)
    bombe_text_rect = bombe_text.get_rect(center=(bombe_button.centerx, bombe_button.centery - 10))
    screen.blit(bombe_text, bombe_text_rect)
    
    bombe_price = max(0, 20000 - price_reduction)  # Prix réduit si "bon marché" est équipé
    bombe_price_text = font_price.render(f"Prix: {bombe_price} pacoins", True, BLACK)
    bombe_price_text_rect = bombe_price_text.get_rect(center=(bombe_button.centerx, bombe_button.centery + 10))
    screen.blit(bombe_price_text, bombe_price_text_rect)
    
    # Vérifier si déjà acheté
    if "bombe téléguidée" in gadget_items:
        font_owned = pygame.font.Font(None, 18)
        owned_text = font_owned.render("(Déjà acheté)", True, BLACK)
        if owned_text.get_width() > button_width - 10:
            owned_text = font_owned.render("(Acheté)", True, BLACK)
        owned_text_rect = owned_text.get_rect(center=(bombe_button.centerx, bombe_button.centery + 22))
        screen.blit(owned_text, owned_text_rect)
    
    # Mettre à jour la description pour "bombe téléguidée"
    if bombe_button.collidepoint(mouse_pos):
        item_description = "Bombe Téléguidée: Utilisez le clic gauche de la souris pour activer. Pacman s'arrête et vous contrôlez une bombe avec les flèches directionnelles. Après 10 secondes, la bombe explose : les fantômes touchés meurent et les murs se cassent. Temps de recharge de 1 minute entre chaque utilisation."
        hovered_item_type = 'bombe téléguidée'
    
    # Bouton "Piège" (aligné à droite, en dessous de Mort)
    piege_button = pygame.Rect(button_x_right, item_y + item_spacing * 3, button_width, item_height)
    pygame.draw.rect(screen, (0, 255, 0), piege_button)  # Vert
    pygame.draw.rect(screen, WHITE, piege_button, 2)
    
    piege_count = gadget_items.count("piège")
    piege_name = f"Piège x{piege_count}" if piege_count > 0 else "Piège"
    piege_text = font_item.render(piege_name, True, BLACK)
    piege_text_rect = piege_text.get_rect(center=(piege_button.centerx, piege_button.centery - 10))
    screen.blit(piege_text, piege_text_rect)
    
    piege_price = max(0, 5000 - price_reduction)  # Prix réduit si "bon marché" est équipé
    piege_price_text = font_price.render(f"Prix: {piege_price} pacoins", True, BLACK)
    piege_price_text_rect = piege_price_text.get_rect(center=(piege_button.centerx, piege_button.centery + 10))
    screen.blit(piege_price_text, piege_price_text_rect)
    
    # Vérifier si déjà acheté
    if "piège" in gadget_items:
        font_owned = pygame.font.Font(None, 18)
        owned_text = font_owned.render("(Déjà acheté)", True, BLACK)
        if owned_text.get_width() > button_width - 10:
            owned_text = font_owned.render("(Acheté)", True, BLACK)
        owned_text_rect = owned_text.get_rect(center=(piege_button.centerx, piege_button.centery + 22))
        screen.blit(owned_text, owned_text_rect)
    
    # Mettre à jour la description pour "piège"
    if piege_button.collidepoint(mouse_pos):
        item_description = "Piège: Utilisez le clic gauche de la souris pour activer. Pose un piège à votre position. Si un fantôme marche sur le piège, il est immobilisé pendant 10 secondes. Temps de recharge de 1 minute entre chaque utilisation."
        hovered_item_type = 'piège'
    
    # Bouton "TP" (aligné à gauche, en dessous de Bombe Téléguidée)
    tp_button = pygame.Rect(button_x, item_y + item_spacing * 3, button_width, item_height)
    pygame.draw.rect(screen, (128, 0, 128), tp_button)  # Violet
    pygame.draw.rect(screen, WHITE, tp_button, 2)
    
    tp_count = gadget_items.count("tp")
    tp_name = f"TP x{tp_count}" if tp_count > 0 else "TP"
    tp_text = font_item.render(tp_name, True, BLACK)
    tp_text_rect = tp_text.get_rect(center=(tp_button.centerx, tp_button.centery - 10))
    screen.blit(tp_text, tp_text_rect)
    
    tp_price = max(0, 3000 - price_reduction)  # Prix réduit si "bon marché" est équipé
    tp_price_text = font_price.render(f"Prix: {tp_price} pacoins", True, BLACK)
    tp_price_text_rect = tp_price_text.get_rect(center=(tp_button.centerx, tp_button.centery + 10))
    screen.blit(tp_price_text, tp_price_text_rect)
    
    # Vérifier si déjà acheté
    if "tp" in gadget_items:
        font_owned = pygame.font.Font(None, 18)
        owned_text = font_owned.render("(Déjà acheté)", True, BLACK)
        if owned_text.get_width() > button_width - 10:
            owned_text = font_owned.render("(Acheté)", True, BLACK)
        owned_text_rect = owned_text.get_rect(center=(tp_button.centerx, tp_button.centery + 22))
        screen.blit(owned_text, owned_text_rect)
    
    # Mettre à jour la description pour "tp"
    if tp_button.collidepoint(mouse_pos):
        item_description = "TP: Utilisez le clic gauche de la souris pour activer. Téléporte Pacman à la position de la souris, sauf si c'est un mur. Temps de recharge de 25 secondes entre chaque utilisation."
        hovered_item_type = 'tp'
    
    # Bouton "Portail" (aligné à droite, en dessous de Piège)
    portail_button = pygame.Rect(button_x_right, item_y + item_spacing * 4, button_width, item_height)
    pygame.draw.rect(screen, (0, 100, 200), portail_button)  # Bleu
    pygame.draw.rect(screen, WHITE, portail_button, 2)
    
    portail_count = gadget_items.count("portail")
    portail_name = f"Portail x{portail_count}" if portail_count > 0 else "Portail"
    portail_text = font_item.render(portail_name, True, BLACK)
    portail_text_rect = portail_text.get_rect(center=(portail_button.centerx, portail_button.centery - 10))
    screen.blit(portail_text, portail_text_rect)
    
    portail_price = max(0, 4000 - price_reduction)  # Prix réduit si "bon marché" est équipé
    portail_price_text = font_price.render(f"Prix: {portail_price} pacoins", True, BLACK)
    portail_price_text_rect = portail_price_text.get_rect(center=(portail_button.centerx, portail_button.centery + 10))
    screen.blit(portail_price_text, portail_price_text_rect)
    
    # Vérifier si déjà acheté
    if "portail" in gadget_items:
        font_owned = pygame.font.Font(None, 18)
        owned_text = font_owned.render("(Déjà acheté)", True, BLACK)
        if owned_text.get_width() > button_width - 10:
            owned_text = font_owned.render("(Acheté)", True, BLACK)
        owned_text_rect = owned_text.get_rect(center=(portail_button.centerx, portail_button.centery + 22))
        screen.blit(owned_text, owned_text_rect)
    
    # Mettre à jour la description pour "portail"
    if portail_button.collidepoint(mouse_pos):
        item_description = "Portail: Utilisez le clic gauche de la souris pour activer. 1ère utilisation : pose un portail à votre position. 2ème utilisation : pose un deuxième portail. Si vous entrez dans un portail, vous ressortez par l'autre. 3ème utilisation : enlève les portails. Temps de recharge de 25 secondes entre chaque utilisation."
    
    # Bouton "Mur" (aligné à gauche, en dessous de Portail)
    mur_button = pygame.Rect(button_x, item_y + item_spacing * 4, button_width, item_height)
    pygame.draw.rect(screen, (0, 100, 200), mur_button)  # Bleu
    pygame.draw.rect(screen, WHITE, mur_button, 2)
    
    mur_count = gadget_items.count("mur")
    mur_name = f"Mur x{mur_count}" if mur_count > 0 else "Mur"
    mur_text = font_item.render(mur_name, True, BLACK)
    mur_text_rect = mur_text.get_rect(center=(mur_button.centerx, mur_button.centery - 10))
    screen.blit(mur_text, mur_text_rect)
    
    mur_price = max(0, 2500 - price_reduction)  # Prix réduit si "bon marché" est équipé
    mur_price_text = font_price.render(f"Prix: {mur_price} pacoins", True, BLACK)
    mur_price_text_rect = mur_price_text.get_rect(center=(mur_button.centerx, mur_button.centery + 10))
    screen.blit(mur_price_text, mur_price_text_rect)
    
    # Vérifier si déjà acheté
    if "mur" in gadget_items:
        font_owned = pygame.font.Font(None, 18)
        owned_text = font_owned.render("(Déjà acheté)", True, BLACK)
        if owned_text.get_width() > button_width - 10:
            owned_text = font_owned.render("(Acheté)", True, BLACK)
        owned_text_rect = owned_text.get_rect(center=(mur_button.centerx, mur_button.centery + 22))
        screen.blit(owned_text, owned_text_rect)
    
    # Mettre à jour la description pour "mur"
    if mur_button.collidepoint(mouse_pos):
        item_description = "Mur: Utilisez le clic gauche de la souris pour activer. 1ère utilisation : crée un mur à votre position (si ce n'est pas déjà un mur). 2ème utilisation : enlève le mur créé. Temps de recharge de 25 secondes entre chaque utilisation."
        hovered_item_type = 'mur'
    
    # Afficher la description de l'item si elle existe ou si on survole un objet
    if item_description or hovered_item_type:
        # Zone de description en bas de l'écran
        desc_y = WINDOW_HEIGHT - 120
        desc_height = 100
        desc_rect = pygame.Rect(10, desc_y, WINDOW_WIDTH - 20, desc_height)
        pygame.draw.rect(screen, (50, 50, 50), desc_rect)
        pygame.draw.rect(screen, WHITE, desc_rect, 2)
        
        # Afficher la rareté si on survole un objet
        if hovered_item_type:
            rarity_name, rarity_color = get_item_rarity(hovered_item_type)
            font_rarity = pygame.font.Font(None, 28)
            rarity_text = font_rarity.render(f"Rareté: {rarity_name}", True, rarity_color)
            rarity_text_rect = rarity_text.get_rect(x=20, y=desc_y + 10)
            screen.blit(rarity_text, rarity_text_rect)
        
        # Afficher le texte de description si elle existe
        if item_description:
            font_desc = pygame.font.Font(None, 24)
            # Diviser le texte en lignes si nécessaire
            words = item_description.split(' ')
            lines = []
            current_line = ""
            for word in words:
                test_line = current_line + word + " " if current_line else word + " "
                text_width = font_desc.size(test_line)[0]
                if text_width > WINDOW_WIDTH - 40:
                    if current_line:
                        lines.append(current_line)
                    current_line = word + " "
                else:
                    current_line = test_line
            if current_line:
                lines.append(current_line)
            
            # Afficher les lignes (limiter à 3 lignes maximum si rareté affichée, sinon 4)
            max_lines = min(len(lines), 3 if hovered_item_type else 4)
            start_y = desc_y + 40 if hovered_item_type else desc_y + 10
            for i in range(max_lines):
                desc_text = font_desc.render(lines[i], True, WHITE)
                screen.blit(desc_text, (20, start_y + i * 25))
    
    return retour_button, explosion_button, vision_x_button, feu_button, tir_button, mort_button, bombe_button, piege_button, tp_button, portail_button, mur_button

def draw_shop_capacite(screen, jeton_poche=0, capacite_items=None, crown_poche=0, item_description=None, bon_marche_ameliore=False):
    """Dessine l'écran des items de capacité"""
    if capacite_items is None:
        capacite_items = []
    
    # Calculer la réduction de prix selon le niveau de "bon marché"
    bon_marche_level = capacite_items.count("bon marché")
    price_reduction = bon_marche_level * 5
    if bon_marche_ameliore and bon_marche_level > 0:
        price_reduction *= 2
    
    screen.fill(BLACK)
    
    font_title = pygame.font.Font(None, 72)
    title_text = font_title.render("CAPACITÉ", True, YELLOW)
    title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, 100))
    screen.blit(title_text, title_rect)
    
    # Afficher les pacoins et couronnes disponibles
    font_info = pygame.font.Font(None, 36)
    pacoin_text = font_info.render(f"Pacoins: {jeton_poche}", True, WHITE)
    screen.blit(pacoin_text, (WINDOW_WIDTH//2 - 100, 150))
    crown_text = font_info.render(f"Couronnes: {crown_poche}", True, WHITE)
    screen.blit(crown_text, (WINDOW_WIDTH//2 - 100, 180))
    
    # Item "Bon marché"
    item_y = 220
    item_height = 55
    item_spacing = 65
    button_width = 200
    button_x = 20
    button_x_right = WINDOW_WIDTH - button_width - 20
    
    # Bouton "Bon marché" (aligné à gauche)
    bon_marche_button = pygame.Rect(button_x, item_y, button_width, item_height)
    pygame.draw.rect(screen, (0, 255, 0), bon_marche_button)  # Vert
    pygame.draw.rect(screen, WHITE, bon_marche_button, 2)
    
    font_item = pygame.font.Font(None, 28)
    bon_marche_count = capacite_items.count("bon marché")
    bon_marche_name = f"Bon marché x{bon_marche_count}" if bon_marche_count > 0 else "Bon marché"
    bon_marche_text = font_item.render(bon_marche_name, True, BLACK)
    bon_marche_text_rect = bon_marche_text.get_rect(center=(bon_marche_button.centerx, bon_marche_button.centery - 10))
    screen.blit(bon_marche_text, bon_marche_text_rect)
    
    font_price = pygame.font.Font(None, 20)
    bon_marche_price = max(0, 5000 - price_reduction)  # Prix réduit si "bon marché" est équipé
    bon_marche_price_text = font_price.render(f"Prix: {bon_marche_price} pacoins", True, BLACK)
    bon_marche_price_text_rect = bon_marche_price_text.get_rect(center=(bon_marche_button.centerx, bon_marche_button.centery + 10))
    screen.blit(bon_marche_price_text, bon_marche_price_text_rect)
    
    # Afficher le niveau si déjà acheté
    bon_marche_level = capacite_items.count("bon marché")
    if bon_marche_level > 0:
        font_owned = pygame.font.Font(None, 18)
        level_text = font_owned.render(f"Niveau {bon_marche_level}", True, BLACK)
        if level_text.get_width() > button_width - 10:
            level_text = font_owned.render(f"Nv.{bon_marche_level}", True, BLACK)
        level_text_rect = level_text.get_rect(center=(bon_marche_button.centerx, bon_marche_button.centery + 22))
        screen.blit(level_text, level_text_rect)
    
    # Afficher "(Maximum atteint)" si la limite de 10 est atteinte
    if bon_marche_level >= 10:
        font_max = pygame.font.Font(None, 16)
        max_text = font_max.render("(Maximum atteint)", True, BLACK)
        max_text_rect = max_text.get_rect(center=(bon_marche_button.centerx, bon_marche_button.centery + 40))
        screen.blit(max_text, max_text_rect)
    
    # Bouton "Gadget" (aligné à droite)
    gadget_button = pygame.Rect(button_x_right, item_y, button_width, item_height)
    pygame.draw.rect(screen, (255, 255, 0), gadget_button)  # Jaune
    pygame.draw.rect(screen, WHITE, gadget_button, 2)
    
    gadget_count = capacite_items.count("gadget")
    gadget_name = f"Gadget x{gadget_count}" if gadget_count > 0 else "Gadget"
    gadget_text = font_item.render(gadget_name, True, BLACK)
    gadget_text_rect = gadget_text.get_rect(center=(gadget_button.centerx, gadget_button.centery - 10))
    screen.blit(gadget_text, gadget_text_rect)
    
    gadget_price = max(0, 10000 - price_reduction)  # Prix réduit si "bon marché" est équipé (seulement pour les pacoins)
    gadget_price_text = font_price.render(f"{gadget_price} pacoins et 1000 couronnes", True, BLACK)
    # Vérifier que le texte ne dépasse pas et le diviser en deux lignes si nécessaire
    if gadget_price_text.get_width() > button_width - 10:
        # Diviser en deux lignes
        gadget_price_text1 = font_price.render(f"{gadget_price} pacoins", True, BLACK)
        gadget_price_text2 = font_price.render("1000 couronnes", True, BLACK)
        gadget_price_text_rect1 = gadget_price_text1.get_rect(center=(gadget_button.centerx, gadget_button.centery + 5))
        gadget_price_text_rect2 = gadget_price_text2.get_rect(center=(gadget_button.centerx, gadget_button.centery + 15))
        screen.blit(gadget_price_text1, gadget_price_text_rect1)
        screen.blit(gadget_price_text2, gadget_price_text_rect2)
    else:
        gadget_price_text_rect = gadget_price_text.get_rect(center=(gadget_button.centerx, gadget_button.centery + 10))
        screen.blit(gadget_price_text, gadget_price_text_rect)
    
    # Afficher le niveau si déjà acheté
    gadget_level = capacite_items.count("gadget")
    if gadget_level > 0:
        font_owned = pygame.font.Font(None, 18)
        level_text = font_owned.render(f"Niveau {gadget_level}", True, BLACK)
        if level_text.get_width() > button_width - 10:
            level_text = font_owned.render(f"Nv.{gadget_level}", True, BLACK)
        level_text_rect = level_text.get_rect(center=(gadget_button.centerx, gadget_button.centery + 22))
        screen.blit(level_text, level_text_rect)
    
    # Afficher "(Maximum atteint)" si la limite de 10 est atteinte
    if gadget_level >= 10:
        font_max = pygame.font.Font(None, 16)
        max_text = font_max.render("(Maximum atteint)", True, BLACK)
        max_text_rect = max_text.get_rect(center=(gadget_button.centerx, gadget_button.centery + 40))
        screen.blit(max_text, max_text_rect)
    
    # Bouton "Piquant" (aligné à droite, en dessous de "Gadget")
    piquant_button = pygame.Rect(button_x_right, item_y + item_spacing, button_width, item_height)
    pygame.draw.rect(screen, (0, 255, 0), piquant_button)  # Vert
    pygame.draw.rect(screen, WHITE, piquant_button, 2)
    
    piquant_count = capacite_items.count("piquant")
    piquant_name = f"Piquant x{piquant_count}" if piquant_count > 0 else "Piquant"
    piquant_text = font_item.render(piquant_name, True, BLACK)
    piquant_text_rect = piquant_text.get_rect(center=(piquant_button.centerx, piquant_button.centery - 10))
    screen.blit(piquant_text, piquant_text_rect)
    
    piquant_price = max(0, 5000 - price_reduction)  # Prix réduit si "bon marché" est équipé
    piquant_price_text = font_price.render(f"Prix: {piquant_price} pacoins", True, BLACK)
    piquant_price_text_rect = piquant_price_text.get_rect(center=(piquant_button.centerx, piquant_button.centery + 10))
    screen.blit(piquant_price_text, piquant_price_text_rect)
    
    # Afficher le niveau si déjà acheté
    piquant_level = capacite_items.count("piquant")
    if piquant_level > 0:
        font_owned = pygame.font.Font(None, 18)
        level_text = font_owned.render(f"Niveau {piquant_level}", True, BLACK)
        if level_text.get_width() > button_width - 10:
            level_text = font_owned.render(f"Nv.{piquant_level}", True, BLACK)
        level_text_rect = level_text.get_rect(center=(piquant_button.centerx, piquant_button.centery + 22))
        screen.blit(level_text, level_text_rect)
    
    # Afficher "(Maximum atteint)" si la limite de 10 est atteinte
    if piquant_level >= 10:
        font_max = pygame.font.Font(None, 16)
        max_text = font_max.render("(Maximum atteint)", True, BLACK)
        max_text_rect = max_text.get_rect(center=(piquant_button.centerx, piquant_button.centery + 40))
        screen.blit(max_text, max_text_rect)
    
    # Bouton "Pacgum" (aligné à gauche, en dessous de "Bon marché")
    pacgum_button = pygame.Rect(button_x, item_y + item_spacing, button_width, item_height)
    pygame.draw.rect(screen, (128, 0, 128), pacgum_button)  # Violet
    pygame.draw.rect(screen, WHITE, pacgum_button, 2)
    
    pacgum_count = capacite_items.count("pacgum")
    pacgum_name = f"Pacgum x{pacgum_count}" if pacgum_count > 0 else "Pacgum"
    pacgum_text = font_item.render(pacgum_name, True, BLACK)
    pacgum_text_rect = pacgum_text.get_rect(center=(pacgum_button.centerx, pacgum_button.centery - 10))
    screen.blit(pacgum_text, pacgum_text_rect)
    
    pacgum_price_text = font_price.render("Prix: 4000 pacoins", True, BLACK)
    pacgum_price_text_rect = pacgum_price_text.get_rect(center=(pacgum_button.centerx, pacgum_button.centery + 10))
    screen.blit(pacgum_price_text, pacgum_price_text_rect)
    
    # Afficher le niveau si déjà acheté
    pacgum_level = capacite_items.count("pacgum")
    if pacgum_level > 0:
        font_owned = pygame.font.Font(None, 18)
        level_text = font_owned.render(f"Niveau {pacgum_level}", True, BLACK)
        if level_text.get_width() > button_width - 10:
            level_text = font_owned.render(f"Nv.{pacgum_level}", True, BLACK)
        level_text_rect = level_text.get_rect(center=(pacgum_button.centerx, pacgum_button.centery + 22))
        screen.blit(level_text, level_text_rect)
    
    # Afficher "(Maximum atteint)" si la limite de 10 est atteinte
    if pacgum_level >= 10:
        font_max = pygame.font.Font(None, 16)
        max_text = font_max.render("(Maximum atteint)", True, BLACK)
        max_text_rect = max_text.get_rect(center=(pacgum_button.centerx, pacgum_button.centery + 40))
        screen.blit(max_text, max_text_rect)
    
    # Bouton "Bonbe" (aligné à gauche, en dessous de "Pacgum")
    bonbe_button = pygame.Rect(button_x, item_y + item_spacing * 2, button_width, item_height)
    pygame.draw.rect(screen, (0, 255, 0), bonbe_button)  # Vert
    pygame.draw.rect(screen, WHITE, bonbe_button, 2)
    
    bonbe_count = capacite_items.count("bonbe")
    bonbe_name = f"Bonbe x{bonbe_count}" if bonbe_count > 0 else "Bonbe"
    bonbe_text = font_item.render(bonbe_name, True, BLACK)
    bonbe_text_rect = bonbe_text.get_rect(center=(bonbe_button.centerx, bonbe_button.centery - 10))
    screen.blit(bonbe_text, bonbe_text_rect)
    
    bonbe_price = max(0, 5000 - price_reduction)  # Prix réduit si "bon marché" est équipé
    bonbe_price_text = font_price.render(f"Prix: {bonbe_price} pacoins", True, BLACK)
    bonbe_price_text_rect = bonbe_price_text.get_rect(center=(bonbe_button.centerx, bonbe_button.centery + 10))
    screen.blit(bonbe_price_text, bonbe_price_text_rect)
    
    # Afficher le niveau si déjà acheté
    bonbe_level = capacite_items.count("bonbe")
    if bonbe_level > 0:
        font_owned = pygame.font.Font(None, 18)
        level_text = font_owned.render(f"Niveau {bonbe_level}", True, BLACK)
        if level_text.get_width() > button_width - 10:
            level_text = font_owned.render(f"Nv.{bonbe_level}", True, BLACK)
        level_text_rect = level_text.get_rect(center=(bonbe_button.centerx, bonbe_button.centery + 22))
        screen.blit(level_text, level_text_rect)
    
    # Afficher "(Maximum atteint)" si la limite de 3 est atteinte
    if bonbe_level >= 3:
        font_max = pygame.font.Font(None, 16)
        max_text = font_max.render("(Maximum atteint)", True, BLACK)
        max_text_rect = max_text.get_rect(center=(bonbe_button.centerx, bonbe_button.centery + 40))
        screen.blit(max_text, max_text_rect)
    
    # Bouton "Indigestion" (aligné à droite, en dessous de "Piquant")
    indigestion_button = pygame.Rect(button_x_right, item_y + item_spacing * 2, button_width, item_height)
    pygame.draw.rect(screen, (0, 0, 255), indigestion_button)  # Bleu
    pygame.draw.rect(screen, WHITE, indigestion_button, 2)
    
    indigestion_count = capacite_items.count("indigestion")
    indigestion_name = f"Indigestion x{indigestion_count}" if indigestion_count > 0 else "Indigestion"
    indigestion_text = font_item.render(indigestion_name, True, BLACK)
    indigestion_text_rect = indigestion_text.get_rect(center=(indigestion_button.centerx, indigestion_button.centery - 10))
    screen.blit(indigestion_text, indigestion_text_rect)
    
    indigestion_price = max(0, 3500 - price_reduction)  # Prix réduit si "bon marché" est équipé
    indigestion_price_text = font_price.render(f"Prix: {indigestion_price} pacoins", True, BLACK)
    indigestion_price_text_rect = indigestion_price_text.get_rect(center=(indigestion_button.centerx, indigestion_button.centery + 10))
    screen.blit(indigestion_price_text, indigestion_price_text_rect)
    
    # Afficher le niveau si déjà acheté
    indigestion_level = capacite_items.count("indigestion")
    if indigestion_level > 0:
        font_owned = pygame.font.Font(None, 18)
        level_text = font_owned.render(f"Niveau {indigestion_level}", True, BLACK)
        if level_text.get_width() > button_width - 10:
            level_text = font_owned.render(f"Nv.{indigestion_level}", True, BLACK)
        level_text_rect = level_text.get_rect(center=(indigestion_button.centerx, indigestion_button.centery + 22))
        screen.blit(level_text, level_text_rect)
    
    # Afficher "(Maximum atteint)" si la limite de 10 est atteinte
    if indigestion_level >= 10:
        font_max = pygame.font.Font(None, 16)
        max_text = font_max.render("(Maximum atteint)", True, BLACK)
        max_text_rect = max_text.get_rect(center=(indigestion_button.centerx, indigestion_button.centery + 40))
        screen.blit(max_text, max_text_rect)
    
    # Bouton "Bonne vue" (aligné à droite, en dessous de "Indigestion")
    bon_vue_button = pygame.Rect(button_x_right, item_y + item_spacing * 3, button_width, item_height)
    pygame.draw.rect(screen, (0, 255, 0), bon_vue_button)  # Vert
    pygame.draw.rect(screen, WHITE, bon_vue_button, 2)
    
    bon_vue_count = capacite_items.count("bonne vue")
    bon_vue_name = f"Bonne vue x{bon_vue_count}" if bon_vue_count > 0 else "Bonne vue"
    bon_vue_text = font_item.render(bon_vue_name, True, BLACK)
    bon_vue_text_rect = bon_vue_text.get_rect(center=(bon_vue_button.centerx, bon_vue_button.centery - 10))
    screen.blit(bon_vue_text, bon_vue_text_rect)
    
    bon_vue_price = max(0, 5000 - price_reduction)  # Prix réduit si "bon marché" est équipé
    bon_vue_price_text = font_price.render(f"Prix: {bon_vue_price} pacoins", True, BLACK)
    bon_vue_price_text_rect = bon_vue_price_text.get_rect(center=(bon_vue_button.centerx, bon_vue_button.centery + 10))
    screen.blit(bon_vue_price_text, bon_vue_price_text_rect)
    
    # Afficher le niveau si déjà acheté
    bon_vue_level = capacite_items.count("bonne vue")
    if bon_vue_level > 0:
        font_owned = pygame.font.Font(None, 18)
        level_text = font_owned.render(f"Niveau {bon_vue_level}", True, BLACK)
        if level_text.get_width() > button_width - 10:
            level_text = font_owned.render(f"Nv.{bon_vue_level}", True, BLACK)
        level_text_rect = level_text.get_rect(center=(bon_vue_button.centerx, bon_vue_button.centery + 22))
        screen.blit(level_text, level_text_rect)
    
    # Afficher "(Maximum atteint)" si la limite de 10 est atteinte
    if bon_vue_level >= 10:
        font_max = pygame.font.Font(None, 16)
        max_text = font_max.render("(Maximum atteint)", True, BLACK)
        max_text_rect = max_text.get_rect(center=(bon_vue_button.centerx, bon_vue_button.centery + 40))
        screen.blit(max_text, max_text_rect)
    
    # Bouton "Gel" (aligné à gauche, en dessous de "Bonbe")
    gel_button = pygame.Rect(button_x, item_y + item_spacing * 3, button_width, item_height)
    pygame.draw.rect(screen, (0, 255, 0), gel_button)  # Vert
    pygame.draw.rect(screen, WHITE, gel_button, 2)
    
    gel_count = capacite_items.count("gel")
    gel_name = f"Gel x{gel_count}" if gel_count > 0 else "Gel"
    gel_text = font_item.render(gel_name, True, BLACK)
    gel_text_rect = gel_text.get_rect(center=(gel_button.centerx, gel_button.centery - 10))
    screen.blit(gel_text, gel_text_rect)
    
    gel_price = max(0, 5000 - price_reduction)  # Prix réduit si "bon marché" est équipé
    gel_price_text = font_price.render(f"Prix: {gel_price} pacoins", True, BLACK)
    gel_price_text_rect = gel_price_text.get_rect(center=(gel_button.centerx, gel_button.centery + 10))
    screen.blit(gel_price_text, gel_price_text_rect)
    
    # Afficher le niveau si déjà acheté
    gel_level = capacite_items.count("gel")
    if gel_level > 0:
        font_owned = pygame.font.Font(None, 18)
        level_text = font_owned.render(f"Niveau {gel_level}", True, BLACK)
        if level_text.get_width() > button_width - 10:
            level_text = font_owned.render(f"Nv.{gel_level}", True, BLACK)
        level_text_rect = level_text.get_rect(center=(gel_button.centerx, gel_button.centery + 22))
        screen.blit(level_text, level_text_rect)
    
    # Afficher "(Maximum atteint)" si la limite de 10 est atteinte
    if gel_level >= 10:
        font_max = pygame.font.Font(None, 16)
        max_text = font_max.render("(Maximum atteint)", True, BLACK)
        max_text_rect = max_text.get_rect(center=(gel_button.centerx, gel_button.centery + 40))
        screen.blit(max_text, max_text_rect)
    
    # Bouton "Lunette" (aligné à gauche, en dessous de "Gel")
    lunette_button = pygame.Rect(button_x, item_y + item_spacing * 4, button_width, item_height)
    pygame.draw.rect(screen, (255, 255, 0), lunette_button)  # Jaune
    pygame.draw.rect(screen, WHITE, lunette_button, 2)
    
    lunette_count = capacite_items.count("lunette")
    lunette_name = f"Lunette x{lunette_count}" if lunette_count > 0 else "Lunette"
    lunette_text = font_item.render(lunette_name, True, BLACK)
    lunette_text_rect = lunette_text.get_rect(center=(lunette_button.centerx, lunette_button.centery - 10))
    screen.blit(lunette_text, lunette_text_rect)
    
    lunette_price = max(0, 10000 - price_reduction)  # Prix réduit si "bon marché" est équipé (seulement pour les pacoins)
    lunette_price_text = font_price.render(f"{lunette_price} pacoins et 10000 couronnes", True, BLACK)



    
    # Vérifier que le texte ne dépasse pas et le diviser en deux lignes si nécessaire
    if lunette_price_text.get_width() > button_width - 10:
        # Diviser en deux lignes
        lunette_price_text1 = font_price.render(f"{lunette_price} pacoins", True, BLACK)
        lunette_price_text2 = font_price.render("10000 couronnes", True, BLACK)
        lunette_price_text_rect1 = lunette_price_text1.get_rect(center=(lunette_button.centerx, lunette_button.centery + 5))
        lunette_price_text_rect2 = lunette_price_text2.get_rect(center=(lunette_button.centerx, lunette_button.centery + 15))
        screen.blit(lunette_price_text1, lunette_price_text_rect1)
        screen.blit(lunette_price_text2, lunette_price_text_rect2)
    else:
        lunette_price_text_rect = lunette_price_text.get_rect(center=(lunette_button.centerx, lunette_button.centery + 10))
        screen.blit(lunette_price_text, lunette_price_text_rect)
    
    # Afficher le niveau si déjà acheté
    lunette_level = capacite_items.count("lunette")
    if lunette_level > 0:
        font_owned = pygame.font.Font(None, 18)
        level_text = font_owned.render(f"Niveau {lunette_level}", True, BLACK)
        if level_text.get_width() > button_width - 10:
            level_text = font_owned.render(f"Nv.{lunette_level}", True, BLACK)
        level_text_rect = level_text.get_rect(center=(lunette_button.centerx, lunette_button.centery + 22))
        screen.blit(level_text, level_text_rect)
    
    # Afficher "(Maximum atteint)" si la limite de 2 est atteinte
    if lunette_level >= 2:
        font_max = pygame.font.Font(None, 16)
        max_text = font_max.render("(Maximum atteint)", True, BLACK)
        max_text_rect = max_text.get_rect(center=(lunette_button.centerx, lunette_button.centery + 40))
        screen.blit(max_text, max_text_rect)
    
    # Bouton "Invincibilité" (aligné à droite, en dessous de "Bonne vue")
    invincibilite_button = pygame.Rect(button_x_right, item_y + item_spacing * 4, button_width, item_height)
    pygame.draw.rect(screen, (128, 0, 128), invincibilite_button)  # Violet
    pygame.draw.rect(screen, WHITE, invincibilite_button, 2)
    
    invincibilite_count = capacite_items.count("invincibilité")
    invincibilite_name = f"Invincibilité x{invincibilite_count}" if invincibilite_count > 0 else "Invincibilité"
    invincibilite_text = font_item.render(invincibilite_name, True, BLACK)
    invincibilite_text_rect = invincibilite_text.get_rect(center=(invincibilite_button.centerx, invincibilite_button.centery - 10))
    screen.blit(invincibilite_text, invincibilite_text_rect)
    
    invincibilite_price = max(0, 5000 - price_reduction)  # Prix réduit si "bon marché" est équipé
    invincibilite_price_text = font_price.render(f"Prix: {invincibilite_price} pacoins", True, BLACK)
    invincibilite_price_text_rect = invincibilite_price_text.get_rect(center=(invincibilite_button.centerx, invincibilite_button.centery + 10))
    screen.blit(invincibilite_price_text, invincibilite_price_text_rect)
    
    # Afficher le niveau si déjà acheté
    invincibilite_level = capacite_items.count("invincibilité")
    if invincibilite_level > 0:
        font_owned = pygame.font.Font(None, 18)
        level_text = font_owned.render(f"Niveau {invincibilite_level}", True, BLACK)
        if level_text.get_width() > button_width - 10:
            level_text = font_owned.render(f"Nv.{invincibilite_level}", True, BLACK)
        level_text_rect = level_text.get_rect(center=(invincibilite_button.centerx, invincibilite_button.centery + 22))
        screen.blit(level_text, level_text_rect)
    
    # Afficher "(Maximum atteint)" si la limite de 10 est atteinte
    if invincibilite_level >= 10:
        font_max = pygame.font.Font(None, 16)
        max_text = font_max.render("(Maximum atteint)", True, BLACK)
        max_text_rect = max_text.get_rect(center=(invincibilite_button.centerx, invincibilite_button.centery + 40))
        screen.blit(max_text, max_text_rect)
    
    # Bouton retour
    font_retour = pygame.font.Font(None, 36)
    retour_button = pygame.Rect(10, 10, 100, 40)
    pygame.draw.rect(screen, RED, retour_button)
    pygame.draw.rect(screen, WHITE, retour_button, 2)
    retour_text = font_retour.render("RETOUR", True, WHITE)
    retour_text_rect = retour_text.get_rect(center=retour_button.center)
    screen.blit(retour_text, retour_text_rect)
    
    # Afficher la description de l'item si elle existe
    if item_description:
        # Zone de description en bas de l'écran
        desc_y = WINDOW_HEIGHT - 120
        desc_height = 100
        desc_rect = pygame.Rect(10, desc_y, WINDOW_WIDTH - 20, desc_height)
        pygame.draw.rect(screen, (50, 50, 50), desc_rect)
        pygame.draw.rect(screen, WHITE, desc_rect, 2)
        
        # Afficher le texte de description
        font_desc = pygame.font.Font(None, 24)
        # Diviser le texte en lignes si nécessaire
        words = item_description.split(' ')
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + word + " " if current_line else word + " "
            text_width = font_desc.size(test_line)[0]
            if text_width > WINDOW_WIDTH - 40:
                if current_line:
                    lines.append(current_line)
                current_line = word + " "
            else:
                current_line = test_line
        if current_line:
            lines.append(current_line)
        
        # Afficher les lignes (limiter à 4 lignes maximum)
        max_lines = min(len(lines), 4)
        last_text_y = desc_y + 10
        for i in range(max_lines):
            desc_text = font_desc.render(lines[i], True, WHITE)
            screen.blit(desc_text, (20, desc_y + 10 + i * 25))
            last_text_y = desc_y + 10 + i * 25 + 25
        
        # Afficher le niveau de "bon marché" si c'est l'item affiché
        ameliorer_button = None
        if "bon marché" in capacite_items and item_description and "Bon marché" in item_description:
            niveau_text_y = last_text_y
            bon_marche_level = capacite_items.count("bon marché")
            niveau_text = font_desc.render(f"Niveau {bon_marche_level}", True, BLACK)
            screen.blit(niveau_text, (20, niveau_text_y))
            
            # Bouton "Améliorer" juste après le niveau si pas encore amélioré (système d'amélioration avec couronnes)
            if not bon_marche_ameliore:
                ameliorer_button_width = 120
                ameliorer_button_height = 22
                ameliorer_button_x = 20 + niveau_text.get_width() + 10
                ameliorer_button_y = niveau_text_y
                ameliorer_button = pygame.Rect(ameliorer_button_x, ameliorer_button_y, ameliorer_button_width, ameliorer_button_height)
                pygame.draw.rect(screen, (0, 200, 0), ameliorer_button)  # Vert
                pygame.draw.rect(screen, WHITE, ameliorer_button, 1)
                font_ameliorer = pygame.font.Font(None, 16)  # Police très petite
                ameliorer_text = font_ameliorer.render("Améliorer (-1)", True, BLACK)
                # Vérifier si le texte dépasse et le raccourcir si nécessaire
                if ameliorer_text.get_width() > ameliorer_button_width - 4:
                    ameliorer_text = font_ameliorer.render("Améliorer", True, BLACK)
                ameliorer_text_rect = ameliorer_text.get_rect(center=ameliorer_button.center)
                screen.blit(ameliorer_text, ameliorer_text_rect)
    else:
        ameliorer_button = None
    
    # Détecter quel item est survolé pour afficher sa rareté
    mouse_pos = pygame.mouse.get_pos()
    hovered_item_type = None
    if bon_marche_button.collidepoint(mouse_pos):
        hovered_item_type = 'bon marché'
    elif gadget_button.collidepoint(mouse_pos):
        hovered_item_type = 'gadget'
    elif piquant_button.collidepoint(mouse_pos):
        hovered_item_type = 'piquant'
    elif pacgum_button.collidepoint(mouse_pos):
        hovered_item_type = 'pacgum'
    elif bonbe_button.collidepoint(mouse_pos):
        hovered_item_type = 'bonbe'
    elif indigestion_button.collidepoint(mouse_pos):
        hovered_item_type = 'indigestion'
    elif bon_vue_button.collidepoint(mouse_pos):
        hovered_item_type = 'bonne vue'
    elif gel_button.collidepoint(mouse_pos):
        hovered_item_type = 'gel'
    elif lunette_button.collidepoint(mouse_pos):
        hovered_item_type = 'lunette'
    elif invincibilite_button.collidepoint(mouse_pos):
        hovered_item_type = 'invincibilité'
    
    # Afficher la description de l'item si elle existe ou si on survole un objet
    if item_description or hovered_item_type:
        # Zone de description en bas de l'écran
        desc_y = WINDOW_HEIGHT - 120
        desc_height = 100
        desc_rect = pygame.Rect(10, desc_y, WINDOW_WIDTH - 20, desc_height)
        pygame.draw.rect(screen, (50, 50, 50), desc_rect)
        pygame.draw.rect(screen, WHITE, desc_rect, 2)
        
        # Afficher la rareté si on survole un objet
        if hovered_item_type:
            rarity_name, rarity_color = get_item_rarity(hovered_item_type)
            font_rarity = pygame.font.Font(None, 28)
            rarity_text = font_rarity.render(f"Rareté: {rarity_name}", True, rarity_color)
            rarity_text_rect = rarity_text.get_rect(x=20, y=desc_y + 10)
            screen.blit(rarity_text, rarity_text_rect)
        
        # Afficher le texte de description si elle existe
        if item_description:
            font_desc = pygame.font.Font(None, 24)
            # Diviser le texte en lignes si nécessaire
            words = item_description.split(' ')
            lines = []
            current_line = ""
            for word in words:
                test_line = current_line + word + " " if current_line else word + " "
                text_width = font_desc.size(test_line)[0]
                if text_width > WINDOW_WIDTH - 40:
                    if current_line:
                        lines.append(current_line)
                    current_line = word + " "
                else:
                    current_line = test_line
            if current_line:
                lines.append(current_line)
            
            # Afficher les lignes (limiter à 3 lignes maximum si rareté affichée, sinon 4)
            max_lines = min(len(lines), 3 if hovered_item_type else 4)
            start_y = desc_y + 40 if hovered_item_type else desc_y + 10
            for i in range(max_lines):
                desc_text = font_desc.render(lines[i], True, WHITE)
                screen.blit(desc_text, (20, start_y + i * 25))
    
    return retour_button, bon_marche_button, gadget_button, piquant_button, pacgum_button, bonbe_button, indigestion_button, bon_vue_button, gel_button, lunette_button, invincibilite_button, ameliorer_button

def draw_shop_objet(screen, jeton_poche=0, objet_items=None, crown_poche=0, item_description=None, level=1, inventaire_items=None, bon_marche_ameliore=False, capacite_items=None):
    """Dessine l'écran des items d'objet"""
    if objet_items is None:
        objet_items = []
    if inventaire_items is None:
        inventaire_items = {}
    if capacite_items is None:
        capacite_items = []
    
    # Calculer le niveau total de "bon marché" (nombre total d'achats)
    bon_marche_level = capacite_items.count("bon marché")
    
    # Réduction de prix : 5 par niveau (niveau 1 = 5, niveau 2 = 10, etc.)
    # Si amélioré avec couronnes, double la réduction
    price_reduction = bon_marche_level * 5
    if bon_marche_ameliore and bon_marche_level > 0:
        price_reduction *= 2
    
    screen.fill(BLACK)
    
    font_title = pygame.font.Font(None, 72)
    title_text = font_title.render("OBJET", True, YELLOW)
    title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, 100))
    screen.blit(title_text, title_rect)
    
    # Afficher les pacoins et couronnes disponibles
    font_info = pygame.font.Font(None, 36)
    pacoin_text = font_info.render(f"Pacoins: {jeton_poche}", True, WHITE)
    screen.blit(pacoin_text, (WINDOW_WIDTH//2 - 100, 150))
    crown_text = font_info.render(f"Couronnes: {crown_poche}", True, WHITE)
    screen.blit(crown_text, (WINDOW_WIDTH//2 - 100, 180))
    
    # Bouton retour
    font_retour = pygame.font.Font(None, 36)
    retour_button = pygame.Rect(10, 10, 100, 40)
    pygame.draw.rect(screen, RED, retour_button)
    pygame.draw.rect(screen, WHITE, retour_button, 2)
    retour_text = font_retour.render("RETOUR", True, WHITE)
    retour_text_rect = retour_text.get_rect(center=retour_button.center)
    screen.blit(retour_text, retour_text_rect)
    
    # Afficher la description de l'item si elle existe
    if item_description:
        # Zone de description en bas de l'écran
        desc_y = WINDOW_HEIGHT - 120
        desc_height = 100
        desc_rect = pygame.Rect(10, desc_y, WINDOW_WIDTH - 20, desc_height)
        pygame.draw.rect(screen, (50, 50, 50), desc_rect)
        pygame.draw.rect(screen, WHITE, desc_rect, 2)
        
        # Afficher le texte de description
        font_desc = pygame.font.Font(None, 24)
        # Diviser le texte en lignes si nécessaire
        words = item_description.split(' ')
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + word + " " if current_line else word + " "
            text_width = font_desc.size(test_line)[0]
            if text_width > WINDOW_WIDTH - 40:
                if current_line:
                    lines.append(current_line)
                current_line = word + " "
            else:
                current_line = test_line
        if current_line:
            lines.append(current_line)
        
        # Afficher les lignes (limiter à 4 lignes maximum)
        max_lines = min(len(lines), 4)
        for i in range(max_lines):
            desc_text = font_desc.render(lines[i], True, WHITE)
            screen.blit(desc_text, (20, desc_y + 10 + i * 25))
    
    # Item "Pièce mythique"
    item_y = 220
    item_height = 55
    item_spacing = 65
    button_width = 200
    button_x = 20
    button_x_right = WINDOW_WIDTH - button_width - 20
    
    # Bouton "Pièce mythique" (aligné à gauche)
    piece_mythique_button = pygame.Rect(button_x, item_y, button_width, item_height)
    pygame.draw.rect(screen, (255, 255, 0), piece_mythique_button)  # Jaune
    pygame.draw.rect(screen, WHITE, piece_mythique_button, 2)
    
    font_item = pygame.font.Font(None, 28)
    piece_mythique_count = objet_items.count("pièce mythique")
    piece_mythique_name = f"Pièce mythique x{piece_mythique_count}" if piece_mythique_count > 0 else "Pièce mythique"
    piece_mythique_text = font_item.render(piece_mythique_name, True, BLACK)
    piece_mythique_text_rect = piece_mythique_text.get_rect(center=(piece_mythique_button.centerx, piece_mythique_button.centery - 10))
    screen.blit(piece_mythique_text, piece_mythique_text_rect)
    
    font_price = pygame.font.Font(None, 20)
    piece_mythique_price = max(0, 10000 - price_reduction)  # Prix réduit si "bon marché" est équipé
    piece_mythique_price_text = font_price.render(f"Prix: {piece_mythique_price} pacoins et 50 couronnes", True, BLACK)
    # Vérifier que le texte ne dépasse pas et le diviser en deux lignes si nécessaire
    if piece_mythique_price_text.get_width() > button_width - 10:
        # Diviser en deux lignes
        piece_mythique_price_text1 = font_price.render(f"{piece_mythique_price} pacoins", True, BLACK)
        piece_mythique_price_text2 = font_price.render("50 couronnes", True, BLACK)
        piece_mythique_price_text_rect1 = piece_mythique_price_text1.get_rect(center=(piece_mythique_button.centerx, piece_mythique_button.centery + 5))
        piece_mythique_price_text_rect2 = piece_mythique_price_text2.get_rect(center=(piece_mythique_button.centerx, piece_mythique_button.centery + 15))
        screen.blit(piece_mythique_price_text1, piece_mythique_price_text_rect1)
        screen.blit(piece_mythique_price_text2, piece_mythique_price_text_rect2)
    else:
        piece_mythique_price_text_rect = piece_mythique_price_text.get_rect(center=(piece_mythique_button.centerx, piece_mythique_button.centery + 10))
        screen.blit(piece_mythique_price_text, piece_mythique_price_text_rect)
    
    # Vérifier si déjà acheté
    if "pièce mythique" in objet_items:
        font_owned = pygame.font.Font(None, 18)
        owned_text = font_owned.render("(Déjà acheté)", True, BLACK)
        if owned_text.get_width() > button_width - 10:
            owned_text = font_owned.render("(Acheté)", True, BLACK)
        owned_text_rect = owned_text.get_rect(center=(piece_mythique_button.centerx, piece_mythique_button.centery + 22))
        screen.blit(owned_text, owned_text_rect)
    
    # Bouton "Grosse armure" (aligné à droite)
    grosse_armure_button = pygame.Rect(button_x_right, item_y, button_width, item_height)
    pygame.draw.rect(screen, (0, 0, 255), grosse_armure_button)  # Bleu
    pygame.draw.rect(screen, WHITE, grosse_armure_button, 2)
    
    grosse_armure_name = "Grosse armure"
    grosse_armure_text = font_item.render(grosse_armure_name, True, BLACK)
    grosse_armure_text_rect = grosse_armure_text.get_rect(center=(grosse_armure_button.centerx, grosse_armure_button.centery - 10))
    screen.blit(grosse_armure_text, grosse_armure_text_rect)
    
    grosse_armure_price = max(0, 500 - price_reduction)  # Prix réduit si "bon marché" est équipé
    grosse_armure_price_text = font_price.render(f"Prix: {grosse_armure_price} pacoins", True, BLACK)
    grosse_armure_price_text_rect = grosse_armure_price_text.get_rect(center=(grosse_armure_button.centerx, grosse_armure_button.centery + 10))
    screen.blit(grosse_armure_price_text, grosse_armure_price_text_rect)
    
    # Vérifier si déjà acheté
    if "grosse armure" in objet_items:
        font_owned = pygame.font.Font(None, 18)
        owned_text = font_owned.render("(Déjà acheté)", True, BLACK)
        if owned_text.get_width() > button_width - 10:
            owned_text = font_owned.render("(Acheté)", True, BLACK)
        owned_text_rect = owned_text.get_rect(center=(grosse_armure_button.centerx, grosse_armure_button.centery + 22))
        screen.blit(owned_text, owned_text_rect)
    
    # Bouton "Armure de fer" (aligné à droite, en dessous de "Grosse armure")
    armure_fer_button = pygame.Rect(button_x_right, item_y + item_spacing, button_width, item_height)
    pygame.draw.rect(screen, (0, 0, 255), armure_fer_button)  # Bleu
    pygame.draw.rect(screen, WHITE, armure_fer_button, 2)
    
    armure_fer_name = "Armure de fer"
    armure_fer_text = font_item.render(armure_fer_name, True, BLACK)
    armure_fer_text_rect = armure_fer_text.get_rect(center=(armure_fer_button.centerx, armure_fer_button.centery - 10))
    screen.blit(armure_fer_text, armure_fer_text_rect)
    
    armure_fer_price = max(0, 500 - price_reduction)  # Prix réduit si "bon marché" est équipé
    armure_fer_price_text = font_price.render(f"Prix: {armure_fer_price} pacoins", True, BLACK)
    armure_fer_price_text_rect = armure_fer_price_text.get_rect(center=(armure_fer_button.centerx, armure_fer_button.centery + 10))
    screen.blit(armure_fer_price_text, armure_fer_price_text_rect)
    
    # Vérifier si déjà acheté
    if "armure de fer" in objet_items:
        font_owned = pygame.font.Font(None, 18)
        owned_text = font_owned.render("(Déjà acheté)", True, BLACK)
        if owned_text.get_width() > button_width - 10:
            owned_text = font_owned.render("(Acheté)", True, BLACK)
        owned_text_rect = owned_text.get_rect(center=(armure_fer_button.centerx, armure_fer_button.centery + 22))
        screen.blit(owned_text, owned_text_rect)
    
    # Bouton "Flamme" (aligné à gauche, en dessous de "Pièce mythique")
    flamme_button = pygame.Rect(button_x, item_y + item_spacing, button_width, item_height)
    pygame.draw.rect(screen, (0, 0, 255), flamme_button)  # Bleu
    pygame.draw.rect(screen, WHITE, flamme_button, 2)
    
    flamme_name = "Flamme"
    flamme_text = font_item.render(flamme_name, True, BLACK)
    flamme_text_rect = flamme_text.get_rect(center=(flamme_button.centerx, flamme_button.centery - 10))
    screen.blit(flamme_text, flamme_text_rect)
    
    flamme_price = max(0, 2000 - price_reduction)  # Prix réduit si "bon marché" est équipé
    flamme_price_text = font_price.render(f"Prix: {flamme_price} pacoins", True, BLACK)
    flamme_price_text_rect = flamme_price_text.get_rect(center=(flamme_button.centerx, flamme_button.centery + 10))
    screen.blit(flamme_price_text, flamme_price_text_rect)
    
    # Vérifier si déjà acheté
    if "flamme" in objet_items:
        font_owned = pygame.font.Font(None, 18)
        owned_text = font_owned.render("(Déjà acheté)", True, BLACK)
        if owned_text.get_width() > button_width - 10:
            owned_text = font_owned.render("(Acheté)", True, BLACK)
        owned_text_rect = owned_text.get_rect(center=(flamme_button.centerx, flamme_button.centery + 22))
        screen.blit(owned_text, owned_text_rect)
    
    # Item "Givre" (aligné à droite, en dessous de "Armure de fer")
    givre_y = armure_fer_button.y + item_spacing
    
    # Bouton "Givre" (aligné à droite)
    givre_button = pygame.Rect(button_x_right, givre_y, button_width, item_height)
    pygame.draw.rect(screen, (128, 0, 128), givre_button)  # Violet
    pygame.draw.rect(screen, WHITE, givre_button, 2)
    
    givre_name = "Givre"
    givre_text = font_item.render(givre_name, True, BLACK)
    givre_text_rect = givre_text.get_rect(center=(givre_button.centerx, givre_button.centery - 10))
    screen.blit(givre_text, givre_text_rect)
    
    givre_price = max(0, 3000 - price_reduction)  # Prix réduit si "bon marché" est équipé
    givre_price_text = font_price.render(f"Prix: {givre_price} pacoins", True, BLACK)
    givre_price_text_rect = givre_price_text.get_rect(center=(givre_button.centerx, givre_button.centery + 10))
    screen.blit(givre_price_text, givre_price_text_rect)
    
    # Vérifier si déjà acheté
    if "givre" in objet_items:
        font_owned = pygame.font.Font(None, 18)
        owned_text = font_owned.render("(Déjà acheté)", True, BLACK)
        if owned_text.get_width() > button_width - 10:
            owned_text = font_owned.render("(Acheté)", True, BLACK)
        owned_text_rect = owned_text.get_rect(center=(givre_button.centerx, givre_button.centery + 22))
        screen.blit(owned_text, owned_text_rect)
    
    # Item "Infra rouge" (aligné à gauche, en dessous de "Flamme")
    infra_rouge_y = flamme_button.y + item_spacing
    
    # Bouton "Infra rouge" (aligné à gauche)
    infra_rouge_button = pygame.Rect(button_x, infra_rouge_y, button_width, item_height)
    pygame.draw.rect(screen, (0, 255, 0), infra_rouge_button)  # Vert
    pygame.draw.rect(screen, WHITE, infra_rouge_button, 2)
    
    infra_rouge_name = "Infra rouge"
    infra_rouge_text = font_item.render(infra_rouge_name, True, BLACK)
    infra_rouge_text_rect = infra_rouge_text.get_rect(center=(infra_rouge_button.centerx, infra_rouge_button.centery - 10))
    screen.blit(infra_rouge_text, infra_rouge_text_rect)
    
    infra_rouge_price = max(0, 4000 - price_reduction)  # Prix réduit si "bon marché" est équipé
    infra_rouge_price_text = font_price.render(f"Prix: {infra_rouge_price} pacoins", True, BLACK)
    infra_rouge_price_text_rect = infra_rouge_price_text.get_rect(center=(infra_rouge_button.centerx, infra_rouge_button.centery + 10))
    screen.blit(infra_rouge_price_text, infra_rouge_price_text_rect)
    
    # Vérifier si déjà acheté
    if "infra rouge" in objet_items:
        font_owned = pygame.font.Font(None, 18)
        owned_text = font_owned.render("(Déjà acheté)", True, BLACK)
        if owned_text.get_width() > button_width - 10:
            owned_text = font_owned.render("(Acheté)", True, BLACK)
        owned_text_rect = owned_text.get_rect(center=(infra_rouge_button.centerx, infra_rouge_button.centery + 22))
        screen.blit(owned_text, owned_text_rect)
    
    # Item "Coffre fort" (aligné à gauche, en dessous de "Infra rouge")
    coffre_fort_y = infra_rouge_button.y + item_spacing
    
    # Bouton "Coffre fort" (aligné à gauche)
    coffre_fort_button = pygame.Rect(button_x, coffre_fort_y, button_width, item_height)
    pygame.draw.rect(screen, (0, 255, 0), coffre_fort_button)  # Vert
    pygame.draw.rect(screen, WHITE, coffre_fort_button, 2)
    
    coffre_fort_name = "Coffre fort"
    coffre_fort_text = font_item.render(coffre_fort_name, True, BLACK)
    coffre_fort_text_rect = coffre_fort_text.get_rect(center=(coffre_fort_button.centerx, coffre_fort_button.centery - 10))
    screen.blit(coffre_fort_text, coffre_fort_text_rect)
    
    coffre_fort_price = max(0, 10000 - price_reduction)  # Prix réduit si "bon marché" est équipé
    coffre_fort_price_text = font_price.render(f"Prix: {coffre_fort_price} pacoins", True, BLACK)
    coffre_fort_price_text_rect = coffre_fort_price_text.get_rect(center=(coffre_fort_button.centerx, coffre_fort_button.centery + 10))
    screen.blit(coffre_fort_price_text, coffre_fort_price_text_rect)
    
    # Vérifier si déjà acheté
    if "coffre fort" in objet_items:
        font_owned = pygame.font.Font(None, 18)
        owned_text = font_owned.render("(Déjà acheté)", True, BLACK)
        if owned_text.get_width() > button_width - 10:
            owned_text = font_owned.render("(Acheté)", True, BLACK)
        owned_text_rect = owned_text.get_rect(center=(coffre_fort_button.centerx, coffre_fort_button.centery + 22))
        screen.blit(owned_text, owned_text_rect)
    
    # Item "Bric" (aligné à droite, même niveau que "Coffre fort")
    bric_y = coffre_fort_button.y
    
    # Bouton "Bric" (aligné à droite)
    bric_button = pygame.Rect(button_x_right, bric_y, button_width, item_height)
    pygame.draw.rect(screen, (0, 0, 255), bric_button)  # Bleu
    pygame.draw.rect(screen, WHITE, bric_button, 2)
    
    bric_name = "Bric"
    bric_text = font_item.render(bric_name, True, BLACK)
    bric_text_rect = bric_text.get_rect(center=(bric_button.centerx, bric_button.centery - 10))
    screen.blit(bric_text, bric_text_rect)
    
    bric_price = max(0, 5000 - price_reduction)  # Prix réduit si "bon marché" est équipé
    bric_price_text = font_price.render(f"Prix: {bric_price} pacoins", True, BLACK)
    bric_price_text_rect = bric_price_text.get_rect(center=(bric_button.centerx, bric_button.centery + 10))
    screen.blit(bric_price_text, bric_price_text_rect)
    
    # Vérifier si déjà acheté
    if "bric" in objet_items:
        font_owned = pygame.font.Font(None, 18)
        owned_text = font_owned.render("(Déjà acheté)", True, BLACK)
        if owned_text.get_width() > button_width - 10:
            owned_text = font_owned.render("(Acheté)", True, BLACK)
        owned_text_rect = owned_text.get_rect(center=(bric_button.centerx, bric_button.centery + 22))
        screen.blit(owned_text, owned_text_rect)
    
    # Item "Coffre au trésor" (aligné à gauche, en dessous de "Bric")
    coffre_tresor_y = bric_button.y + item_spacing
    
    # Bouton "Coffre au trésor" (aligné à gauche)
    coffre_tresor_button = pygame.Rect(button_x, coffre_tresor_y, button_width, item_height)
    pygame.draw.rect(screen, (0, 255, 0), coffre_tresor_button)  # Vert
    pygame.draw.rect(screen, WHITE, coffre_tresor_button, 2)
    
    coffre_tresor_name = "Coffre au trésor"
    coffre_tresor_text = font_item.render(coffre_tresor_name, True, BLACK)
    coffre_tresor_text_rect = coffre_tresor_text.get_rect(center=(coffre_tresor_button.centerx, coffre_tresor_button.centery - 10))
    screen.blit(coffre_tresor_text, coffre_tresor_text_rect)
    
    coffre_tresor_price = max(0, 15000 - price_reduction)  # Prix réduit si "bon marché" est équipé
    coffre_tresor_price_text = font_price.render(f"Prix: {coffre_tresor_price} pacoins", True, BLACK)
    coffre_tresor_price_text_rect = coffre_tresor_price_text.get_rect(center=(coffre_tresor_button.centerx, coffre_tresor_button.centery + 10))
    screen.blit(coffre_tresor_price_text, coffre_tresor_price_text_rect)
    
    # Vérifier si déjà acheté
    if "coffre au trésor" in objet_items:
        font_owned = pygame.font.Font(None, 18)
        owned_text = font_owned.render("(Déjà acheté)", True, BLACK)
        if owned_text.get_width() > button_width - 10:
            owned_text = font_owned.render("(Acheté)", True, BLACK)
        owned_text_rect = owned_text.get_rect(center=(coffre_tresor_button.centerx, coffre_tresor_button.centery + 22))
        screen.blit(owned_text, owned_text_rect)
    
    # Item "Double gadget" (aligné à droite, même niveau que "Coffre au trésor")
    double_gadget_y = coffre_tresor_button.y
    
    # Bouton "Double gadget" (aligné à droite)
    double_gadget_button = pygame.Rect(button_x_right, double_gadget_y, button_width, item_height)
    pygame.draw.rect(screen, (128, 0, 128), double_gadget_button)  # Violet
    pygame.draw.rect(screen, WHITE, double_gadget_button, 2)
    
    double_gadget_name = "Double gadget"
    double_gadget_text = font_item.render(double_gadget_name, True, BLACK)
    double_gadget_text_rect = double_gadget_text.get_rect(center=(double_gadget_button.centerx, double_gadget_button.centery - 10))
    screen.blit(double_gadget_text, double_gadget_text_rect)
    
    double_gadget_price = max(0, 8000 - price_reduction)  # Prix réduit si "bon marché" est équipé
    double_gadget_price_text = font_price.render(f"Prix: {double_gadget_price} pacoins", True, BLACK)
    double_gadget_price_text_rect = double_gadget_price_text.get_rect(center=(double_gadget_button.centerx, double_gadget_button.centery + 10))
    screen.blit(double_gadget_price_text, double_gadget_price_text_rect)
    
    # Vérifier si déjà acheté
    if "double gadget" in objet_items:
        font_owned = pygame.font.Font(None, 18)
        owned_text = font_owned.render("(Déjà acheté)", True, BLACK)
        if owned_text.get_width() > button_width - 10:
            owned_text = font_owned.render("(Acheté)", True, BLACK)
        owned_text_rect = owned_text.get_rect(center=(double_gadget_button.centerx, double_gadget_button.centery + 22))
        screen.blit(owned_text, owned_text_rect)
    
    # Gestion du survol pour afficher la description et la rareté
    mouse_pos = pygame.mouse.get_pos()
    hovered_item_type = None
    if piece_mythique_button.collidepoint(mouse_pos):
        item_description = "Pièce mythique: Une pièce légendaire aux pouvoirs mystiques. Double les pièces gagnées quand équipée."
        hovered_item_type = 'pièce mythique'
    elif grosse_armure_button.collidepoint(mouse_pos):
        item_description = "Grosse armure: Une armure robuste qui vous protège. +1 vie quand équipée (et +2 vies si équipée avec l'armure de fer)."
        hovered_item_type = 'grosse armure'
    elif armure_fer_button.collidepoint(mouse_pos):
        item_description = "Armure de fer: Une armure robuste qui vous protège. +1 vie quand équipée (et +2 vies si équipée avec la grosse armure)."
        hovered_item_type = 'armure de fer'
    elif flamme_button.collidepoint(mouse_pos):
        item_description = "Flamme: Augmente la durée d'activation du feu de 50% quand équipé."
        hovered_item_type = 'flamme'
    elif givre_button.collidepoint(mouse_pos):
        item_description = "Givre: Diminue encore plus la vitesse de déplacement des fantômes sur la glace si équipé avec le pouvoir 'glace'."
        hovered_item_type = 'givre'
    elif infra_rouge_button.collidepoint(mouse_pos):
        item_description = "Infra rouge: Diminue le temps de rechargement de Vision X si équipé."
        hovered_item_type = 'infra rouge'
    elif bric_button.collidepoint(mouse_pos):
        item_description = "Bric: Si équipé avec le gadget 'mur', permet de poser 2 murs (1ère et 2ème utilisation) puis de les enlever (3ème utilisation)."
        hovered_item_type = 'bric'
    elif coffre_fort_button.collidepoint(mouse_pos):
        item_description = "Coffre fort: Si équipé, vous donne des couronnes et des pacoins à chaque fois que vous gagnez un niveau."
        hovered_item_type = 'coffre fort'
    elif coffre_tresor_button.collidepoint(mouse_pos):
        item_description = "Coffre au trésor: Si équipé, vous donne des couronnes et des pacoins à chaque fois que vous gagnez un niveau."
        hovered_item_type = 'coffre au trésor'
    elif double_gadget_button.collidepoint(mouse_pos):
        item_description = "Double gadget: Permet d'utiliser un gadget deux fois avant que le temps de recharge commence."
        hovered_item_type = 'double gadget'
    
    # Afficher la description de l'item si elle existe ou si on survole un objet
    if item_description or hovered_item_type:
        # Zone de description en bas de l'écran
        desc_y = WINDOW_HEIGHT - 120
        desc_height = 100
        desc_rect = pygame.Rect(10, desc_y, WINDOW_WIDTH - 20, desc_height)
        pygame.draw.rect(screen, (50, 50, 50), desc_rect)
        pygame.draw.rect(screen, WHITE, desc_rect, 2)
        
        # Afficher la rareté si on survole un objet
        if hovered_item_type:
            rarity_name, rarity_color = get_item_rarity(hovered_item_type)
            font_rarity = pygame.font.Font(None, 28)
            rarity_text = font_rarity.render(f"Rareté: {rarity_name}", True, rarity_color)
            rarity_text_rect = rarity_text.get_rect(x=20, y=desc_y + 10)
            screen.blit(rarity_text, rarity_text_rect)
        
        # Afficher le texte de description si elle existe
        if item_description:
            font_desc = pygame.font.Font(None, 24)
            # Diviser le texte en lignes si nécessaire
            words = item_description.split(' ')
            lines = []
            current_line = ""
            for word in words:
                test_line = current_line + word + " " if current_line else word + " "
                text_width = font_desc.size(test_line)[0]
                if text_width > WINDOW_WIDTH - 40:
                    if current_line:
                        lines.append(current_line)
                    current_line = word + " "
                else:
                    current_line = test_line
            if current_line:
                lines.append(current_line)
            
            # Afficher les lignes (limiter à 3 lignes maximum si rareté affichée, sinon 4)
            max_lines = min(len(lines), 3 if hovered_item_type else 4)
            start_y = desc_y + 40 if hovered_item_type else desc_y + 10
            for i in range(max_lines):
                desc_text = font_desc.render(lines[i], True, WHITE)
                screen.blit(desc_text, (20, start_y + i * 25))
    
    return retour_button, piece_mythique_button, grosse_armure_button, armure_fer_button, flamme_button, givre_button, infra_rouge_button, bric_button, coffre_fort_button, coffre_tresor_button, double_gadget_button

def draw_difficulty(screen):
    """Dessine l'écran de sélection de difficulté"""
    screen.fill(BLACK)
    
    font_title = pygame.font.Font(None, 72)
    title_text = font_title.render("DIFFICULTÉ", True, YELLOW)
    title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, 100))
    screen.blit(title_text, title_rect)
    
    # Quatre boutons de difficulté
    font_button = pygame.font.Font(None, 48)
    button_width = 200
    button_height = 60
    button_spacing = 80
    start_y = 220  # Ajusté pour avoir de la place pour 4 boutons
    
    # Bouton 1
    button1 = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, start_y, button_width, button_height)
    pygame.draw.rect(screen, (0, 200, 0), button1)  # Vert pour facile
    pygame.draw.rect(screen, WHITE, button1, 2)
    button1_text = font_button.render("FACILE", True, WHITE)
    button1_text_rect = button1_text.get_rect(center=button1.center)
    screen.blit(button1_text, button1_text_rect)
    
    # Bouton 2
    button2 = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, start_y + button_spacing, button_width, button_height)
    pygame.draw.rect(screen, (200, 200, 0), button2)  # Jaune pour moyen
    pygame.draw.rect(screen, WHITE, button2, 2)
    button2_text = font_button.render("MOYEN", True, WHITE)
    button2_text_rect = button2_text.get_rect(center=button2.center)
    screen.blit(button2_text, button2_text_rect)
    
    # Bouton 3
    button3 = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, start_y + button_spacing * 2, button_width, button_height)
    pygame.draw.rect(screen, (200, 0, 0), button3)  # Rouge pour difficile
    pygame.draw.rect(screen, WHITE, button3, 2)
    button3_text = font_button.render("DIFFICILE", True, WHITE)
    button3_text_rect = button3_text.get_rect(center=button3.center)
    screen.blit(button3_text, button3_text_rect)
    
    # Bouton 4 (HARDCORE)
    button4 = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, start_y + button_spacing * 3, button_width, button_height)
    pygame.draw.rect(screen, (128, 0, 128), button4)  # Violet foncé pour hardcore
    pygame.draw.rect(screen, WHITE, button4, 2)
    button4_text = font_button.render("HARDCORE", True, WHITE)
    button4_text_rect = button4_text.get_rect(center=button4.center)
    screen.blit(button4_text, button4_text_rect)
    
    # Bouton retour
    font_retour = pygame.font.Font(None, 36)
    retour_button = pygame.Rect(10, 10, 100, 40)
    pygame.draw.rect(screen, RED, retour_button)
    pygame.draw.rect(screen, WHITE, retour_button, 2)
    retour_text = font_retour.render("RETOUR", True, WHITE)
    retour_text_rect = retour_text.get_rect(center=retour_button.center)
    screen.blit(retour_text, retour_text_rect)
    
    return retour_button, button1, button2, button3, button4

def get_item_rarity(item_type):
    """Retourne la rareté d'un objet et sa couleur
    Retourne: (rareté_nom, couleur) où couleur est (R, G, B)
    Vert = Rare, Bleu = Super rare, Violet = Épique, Jaune = Légendaire
    """
    # Définir la rareté de chaque objet
    rarity_map = {
        # Légendaire (Jaune) - Tous les objets avec bouton jaune
        'skin bleu': ('Légendaire', YELLOW),
        'skin orange': ('Légendaire', YELLOW),
        'skin rose': ('Légendaire', YELLOW),
        'skin rouge': ('Légendaire', YELLOW),
        'double longue vue': ('Légendaire', YELLOW),
        'mort': ('Légendaire', YELLOW),
        'pièce mythique': ('Légendaire', YELLOW),
        'coffre au trésor': ('Légendaire', YELLOW),
        'gadget': ('Légendaire', YELLOW),
        'lunette': ('Légendaire', YELLOW),
        
        # Épique (Violet) - Tous les objets avec bouton violet
        'bombe téléguidée': ('Épique', (148, 0, 211)),
        'glace': ('Épique', (148, 0, 211)),
        'bon goût': ('Épique', (148, 0, 211)),
        'pas d\'indigestion': ('Épique', (148, 0, 211)),
        'coffre fort': ('Épique', (148, 0, 211)),
        'bon repas': ('Épique', (148, 0, 211)),
        'explosion': ('Épique', (128, 0, 128)),
        'vision x': ('Épique', (128, 0, 128)),
        'feu': ('Épique', (128, 0, 128)),
        'tp': ('Épique', (128, 0, 128)),
        'pacgum': ('Épique', (128, 0, 128)),
        'invincibilité': ('Épique', (128, 0, 128)),
        'givre': ('Épique', (128, 0, 128)),
        'double gadget': ('Épique', (128, 0, 128)),
        
        # Super rare (Bleu) - Tous les objets avec bouton bleu
        'grosse armure': ('Super rare', BLUE),
        'armure de fer': ('Super rare', BLUE),
        'indigestion': ('Super rare', BLUE),
        'portail': ('Super rare', BLUE),
        'mur': ('Super rare', BLUE),
        'lave': ('Super rare', BLUE),
        'flamme': ('Super rare', BLUE),
        'bric': ('Super rare', BLUE),
        
        # Rare (Vert) - Tous les objets avec bouton vert
        'longue vue': ('Rare', (0, 255, 0)),
        'tir': ('Rare', (0, 255, 0)),
        'piège': ('Rare', (0, 255, 0)),
        'bon marché': ('Rare', (0, 255, 0)),
        'piquant': ('Rare', (0, 255, 0)),
        'bonbe': ('Rare', (0, 255, 0)),
        'bonne vue': ('Rare', (0, 255, 0)),
        'gel': ('Rare', (0, 255, 0)),
        'infra rouge': ('Rare', (0, 255, 0)),
    }
    
    return rarity_map.get(item_type, ('Commun', WHITE))

def draw_inventaire(screen, crown_poche=0, jeton_poche=0, pouvoir_items=None, inventaire_items=None, item_description=None, mouse_pos=None, show_start_button=False):
    """Dessine l'écran de l'inventaire (style Minecraft)"""
    if pouvoir_items is None:
        pouvoir_items = []
    if inventaire_items is None:
        inventaire_items = {}
    
    screen.fill(BLACK)
    
    font_title = pygame.font.Font(None, 72)
    title_text = font_title.render("INVENTAIRE", True, YELLOW)
    title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, 50))
    screen.blit(title_text, title_rect)
    
    # Grille d'inventaire (4x10 = 40 emplacements, style Minecraft)
    slot_size = 40
    slot_spacing = 5
    grid_cols = 4
    grid_rows = 10
    grid_start_x = (WINDOW_WIDTH - (grid_cols * (slot_size + slot_spacing) - slot_spacing)) // 2
    grid_start_y = 100
    
    # Case pour le pouvoir en haut à gauche
    pouvoir_slot_size = 50
    pouvoir_slot_x = 20
    pouvoir_slot_y = 80
    pouvoir_slot_rect = pygame.Rect(pouvoir_slot_x, pouvoir_slot_y, pouvoir_slot_size, pouvoir_slot_size)
    
    # Couleur des emplacements
    slot_color = (139, 139, 139)  # Gris foncé
    slot_border = (200, 200, 200)  # Gris clair
    
    # Dessiner la case du pouvoir
    pygame.draw.rect(screen, slot_color, pouvoir_slot_rect)
    pygame.draw.rect(screen, slot_border, pouvoir_slot_rect, 2)
    
    # Définir font_item pour l'utiliser plus tard
    font_item = pygame.font.Font(None, 20)
    
    # Texte "POUVOIR" au-dessus de la case
    font_label = pygame.font.Font(None, 24)
    pouvoir_label = font_label.render("POUVOIR", True, WHITE)
    pouvoir_label_rect = pouvoir_label.get_rect(center=(pouvoir_slot_x + pouvoir_slot_size // 2, pouvoir_slot_y - 15))
    screen.blit(pouvoir_label, pouvoir_label_rect)
    
    # Texte "GADGET" en dessous de la case pouvoir
    gadget_label = font_label.render("GADGET", True, WHITE)
    gadget_label_rect = gadget_label.get_rect(center=(pouvoir_slot_x + pouvoir_slot_size // 2, pouvoir_slot_y + pouvoir_slot_size + 15))
    screen.blit(gadget_label, gadget_label_rect)
    
    # Une case en dessous du texte "GADGET"
    gadget_slot_size = 50
    gadget_slot_x = pouvoir_slot_x
    gadget_slot_y = pouvoir_slot_y + pouvoir_slot_size + 30  # En dessous du texte "GADGET"
    gadget_slot_rect = pygame.Rect(gadget_slot_x, gadget_slot_y, gadget_slot_size, gadget_slot_size)
    pygame.draw.rect(screen, slot_color, gadget_slot_rect)
    pygame.draw.rect(screen, slot_border, gadget_slot_rect, 2)
    
    # Texte "CAPACITÉ" en dessous de la case gadget
    capacite_label = font_label.render("CAPACITÉ", True, WHITE)
    capacite_label_rect = capacite_label.get_rect(center=(gadget_slot_x + gadget_slot_size // 2, gadget_slot_y + gadget_slot_size + 15))
    screen.blit(capacite_label, capacite_label_rect)
    
    # Deux cases en dessous du texte "CAPACITÉ" (qui se touchent)
    capacite_slot_size = 50
    capacite_slot_x = pouvoir_slot_x
    # En dessous de la case gadget
    capacite_slot_y1 = gadget_slot_y + gadget_slot_size + 30
    capacite_slot_y2 = capacite_slot_y1 + capacite_slot_size  # Pas d'espacement, elles se touchent
    
    capacite_slot_rect1 = pygame.Rect(capacite_slot_x, capacite_slot_y1, capacite_slot_size, capacite_slot_size)
    capacite_slot_rect2 = pygame.Rect(capacite_slot_x, capacite_slot_y2, capacite_slot_size, capacite_slot_size)
    
    # Dessiner les deux cases de capacité
    pygame.draw.rect(screen, slot_color, capacite_slot_rect1)
    pygame.draw.rect(screen, slot_border, capacite_slot_rect1, 2)
    pygame.draw.rect(screen, slot_color, capacite_slot_rect2)
    pygame.draw.rect(screen, slot_border, capacite_slot_rect2, 2)
    
    # Dessiner un grand Pacman en dessous des cases de capacité
    pacman_size = 200
    pacman_x = pouvoir_slot_x + 10  # Un tout petit peu à droite
    pacman_y = capacite_slot_y2 + 100  # Un peu plus en haut
    pacman_center_x = pacman_x + pacman_size // 2
    pacman_center_y = pacman_y + pacman_size // 2
    pacman_radius = pacman_size // 2
    
    # Dessiner le cercle de Pacman
    pygame.draw.circle(screen, YELLOW, (pacman_center_x, pacman_center_y), pacman_radius)
    
    # Dessiner la bouche de Pacman (triangle)
    mouth_points = [
        (pacman_center_x, pacman_center_y),
        (pacman_center_x + pacman_radius, pacman_center_y - pacman_radius // 2),
        (pacman_center_x + pacman_radius, pacman_center_y + pacman_radius // 2)
    ]
    pygame.draw.polygon(screen, BLACK, mouth_points)
    
    # Trois cases collées à côté de la case pouvoir (verticalement)
    objet_slot_size = 50
    objet_slot_x = pouvoir_slot_x + pouvoir_slot_size + 30  # Plus à droite que la case pouvoir
    objet_slot_start_y = pouvoir_slot_y  # Même hauteur que la case pouvoir
    
    # Texte "OBJET" au-dessus des trois cases
    objet_label = font_label.render("OBJET", True, WHITE)
    objet_label_rect = objet_label.get_rect(center=(objet_slot_x + objet_slot_size // 2, objet_slot_start_y - 15))
    screen.blit(objet_label, objet_label_rect)
    
    # Créer une liste pour stocker les rectangles des cases d'objets
    objet_slot_rects = []
    # Dessiner les trois cases d'objets collées verticalement
    for i in range(3):
        objet_slot_y = objet_slot_start_y + i * objet_slot_size  # Pas d'espacement, elles se touchent
        objet_slot_rect = pygame.Rect(objet_slot_x, objet_slot_y, objet_slot_size, objet_slot_size)
        objet_slot_rects.append(objet_slot_rect)
        pygame.draw.rect(screen, slot_color, objet_slot_rect)
        pygame.draw.rect(screen, slot_border, objet_slot_rect, 2)
    
    # Créer une liste pour stocker les rectangles de la grille
    grid_slot_rects = []
    # Dessiner la grille d'inventaire
    for row in range(grid_rows):
        for col in range(grid_cols):
            slot_x = grid_start_x + col * (slot_size + slot_spacing)
            slot_y = grid_start_y + row * (slot_size + slot_spacing)
            slot_rect = pygame.Rect(slot_x, slot_y, slot_size, slot_size)
            grid_slot_rects.append((row, col, slot_rect))
            pygame.draw.rect(screen, slot_color, slot_rect)
            pygame.draw.rect(screen, slot_border, slot_rect, 2)
    
    # Afficher les items dans l'inventaire
    font = pygame.font.Font(None, 24)
    
    # Bouton retour et/ou commencer
    font_button = pygame.font.Font(None, 36)
    # Toujours afficher le bouton retour
    retour_button = pygame.Rect(10, 10, 100, 40)
    pygame.draw.rect(screen, RED, retour_button)
    pygame.draw.rect(screen, WHITE, retour_button, 2)
    retour_text = font_button.render("RETOUR", True, WHITE)
    retour_text_rect = retour_text.get_rect(center=retour_button.center)
    screen.blit(retour_text, retour_text_rect)
    
    # Afficher aussi le bouton "Commencer" si show_start_button est True
    if show_start_button:
        # Afficher un bouton "Commencer" à droite en bas
        start_button = pygame.Rect(WINDOW_WIDTH - 150, WINDOW_HEIGHT - 60, 140, 50)
        pygame.draw.rect(screen, (0, 255, 0), start_button)  # Vert
        pygame.draw.rect(screen, WHITE, start_button, 2)
        # Utiliser une police plus petite pour le bouton "Commencer"
        font_start = pygame.font.Font(None, 28)
        start_text = font_start.render("COMMENCER", True, WHITE)
        start_text_rect = start_text.get_rect(center=start_button.center)
        screen.blit(start_text, start_text_rect)
        start_button_for_slots = start_button
    else:
        start_button_for_slots = None
    
    # Créer un dictionnaire avec tous les rectangles des slots pour le drag and drop
    slots = {
        'pouvoir': pouvoir_slot_rect,
        'gadget': gadget_slot_rect,
        'capacite1': capacite_slot_rect1,
        'capacite2': capacite_slot_rect2,
    }
    if retour_button:
        slots['retour'] = retour_button
    if start_button_for_slots:
        slots['commencer'] = start_button_for_slots
    # Ajouter les cases d'objets
    for i, rect in enumerate(objet_slot_rects):
        slots[f'objet{i}'] = rect
    # Ajouter la grille d'inventaire
    for row, col, rect in grid_slot_rects:
        slots[f'grid_{row}_{col}'] = rect
    
    # Afficher les items dans les slots selon inventaire_items
    for slot_name, item_data in inventaire_items.items():
        if slot_name in slots:
            slot_rect = slots[slot_name]
            # Dessiner l'item dans le slot
            if item_data.get('type') == 'bon repas':
                # Dessiner une assiette avec de la nourriture (Pacman miniature dans une assiette)
                center_x = slot_rect.centerx
                center_y = slot_rect.centery
                
                # Assiette (cercle blanc/gris)
                plate_radius = 14
                pygame.draw.circle(screen, (220, 220, 220), (center_x, center_y), plate_radius)  # Gris clair
                pygame.draw.circle(screen, (180, 180, 180), (center_x, center_y), plate_radius, 2)  # Bordure grise
                pygame.draw.circle(screen, (240, 240, 240), (center_x, center_y), plate_radius - 3)  # Intérieur blanc
                
                # Pacman miniature au centre de l'assiette (nourriture)
                pacman_radius = 6
                pacman_x = center_x
                pacman_y = center_y - 2  # Légèrement décalé vers le haut
                pygame.draw.circle(screen, YELLOW, (pacman_x, pacman_y), pacman_radius)
                
                # Bouche de Pacman (triangle noir)
                mouth_points = [
                    (pacman_x, pacman_y),
                    (pacman_x + pacman_radius, pacman_y - pacman_radius // 2),
                    (pacman_x + pacman_radius, pacman_y + pacman_radius // 2)
                ]
                pygame.draw.polygon(screen, BLACK, mouth_points)
                
                # Petits points de nourriture autour (points)
                for offset_x, offset_y in [(-8, 4), (8, 4), (0, 6)]:
                    pygame.draw.circle(screen, (255, 192, 203), (center_x + offset_x, center_y + offset_y), 2)
            elif item_data.get('type') == 'bon goût':
                # Dessiner un Pacman miniature avec un symbole de goût (étoile)
                center_x = slot_rect.centerx
                center_y = slot_rect.centery
                
                # Pacman (cercle jaune avec bouche)
                pacman_radius = 10
                pacman_x = center_x - 5
                pacman_y = center_y
                
                # Dessiner le cercle de Pacman
                pygame.draw.circle(screen, YELLOW, (pacman_x, pacman_y), pacman_radius)
                
                # Dessiner la bouche de Pacman (triangle noir)
                mouth_points = [
                    (pacman_x, pacman_y),
                    (pacman_x + pacman_radius, pacman_y - pacman_radius // 2),
                    (pacman_x + pacman_radius, pacman_y + pacman_radius // 2)
                ]
                pygame.draw.polygon(screen, BLACK, mouth_points)
                
                # Symbole de goût (étoile rose) à droite de Pacman
                star_x = center_x + 8
                star_y = center_y
                star_size = 6
                
                # Dessiner une étoile (5 branches)
                star_points = []
                for i in range(5):
                    angle = (i * 2 * math.pi / 5) - math.pi / 2
                    # Point extérieur
                    outer_x = star_x + star_size * math.cos(angle)
                    outer_y = star_y + star_size * math.sin(angle)
                    star_points.append((outer_x, outer_y))
                    # Point intérieur
                    inner_angle = angle + math.pi / 5
                    inner_x = star_x + (star_size * 0.4) * math.cos(inner_angle)
                    inner_y = star_y + (star_size * 0.4) * math.sin(inner_angle)
                    star_points.append((inner_x, inner_y))
                
                pygame.draw.polygon(screen, (148, 0, 211), star_points)  # Violet
            elif item_data.get('type') == 'pas d\'indigestion':
                # Dessiner un Pacman miniature avec un symbole de protection (bouclier)
                center_x = slot_rect.centerx
                center_y = slot_rect.centery
                
                # Pacman (cercle jaune avec bouche)
                pacman_radius = 10
                pacman_x = center_x - 5
                pacman_y = center_y
                
                # Dessiner le cercle de Pacman
                pygame.draw.circle(screen, YELLOW, (pacman_x, pacman_y), pacman_radius)
                
                # Dessiner la bouche de Pacman (triangle noir)
                mouth_points = [
                    (pacman_x, pacman_y),
                    (pacman_x + pacman_radius, pacman_y - pacman_radius // 2),
                    (pacman_x + pacman_radius, pacman_y + pacman_radius // 2)
                ]
                pygame.draw.polygon(screen, BLACK, mouth_points)
                
                # Bouclier bleu à droite de Pacman
                shield_x = center_x + 8
                shield_y = center_y
                shield_width = 8
                shield_height = 10
                
                # Dessiner un bouclier (forme de losange/écu)
                shield_points = [
                    (shield_x, shield_y - shield_height // 2),  # Haut
                    (shield_x + shield_width // 2, shield_y),  # Droite
                    (shield_x, shield_y + shield_height // 2),  # Bas
                    (shield_x - shield_width // 2, shield_y)   # Gauche
                ]
                pygame.draw.polygon(screen, (148, 0, 211), shield_points)  # Violet
                pygame.draw.polygon(screen, WHITE, shield_points, 1)  # Bordure blanche
            elif item_data.get('type') == 'longue vue' or item_data.get('type') == 'double longue vue':
                # Dessiner un Pacman miniature avec une torche devant lui (et derrière pour double longue vue)
                center_x = slot_rect.centerx
                center_y = slot_rect.centery
                
                # Pacman (cercle jaune avec bouche)
                pacman_radius = 10
                # Position de Pacman : au centre pour double longue vue, à gauche pour simple
                if item_data.get('type') == 'double longue vue':
                    pacman_x = center_x  # Pacman au centre pour double longue vue
                else:
                    pacman_x = center_x - 5  # Pacman à gauche pour simple longue vue
                pacman_y = center_y
                
                # Variables pour les torches
                stick_width = 2
                stick_height = 8
                
                # Pour la double longue vue, dessiner d'abord la torche derrière
                if item_data.get('type') == 'double longue vue':
                    # Torche derrière Pacman (à gauche)
                    torch_x_back = pacman_x - 12  # Torche à gauche de Pacman (derrière)
                    torch_y_back = center_y
                    stick_rect_back = pygame.Rect(torch_x_back - stick_width // 2, torch_y_back - stick_height // 2, stick_width, stick_height)
                    pygame.draw.rect(screen, (139, 69, 19), stick_rect_back)  # Marron
                    flame_x_back = torch_x_back
                    flame_y_back = torch_y_back - stick_height // 2 - 2
                    flame_points_back = [
                        (flame_x_back, flame_y_back - 4),
                        (flame_x_back - 3, flame_y_back),
                        (flame_x_back, flame_y_back + 2),
                        (flame_x_back + 3, flame_y_back)
                    ]
                    pygame.draw.polygon(screen, (255, 165, 0), flame_points_back)
                    inner_flame_points_back = [
                        (flame_x_back, flame_y_back - 2),
                        (flame_x_back - 1, flame_y_back),
                        (flame_x_back, flame_y_back + 1),
                        (flame_x_back + 1, flame_y_back)
                    ]
                    pygame.draw.polygon(screen, (255, 255, 200), inner_flame_points_back)
                
                # Dessiner le cercle de Pacman
                pygame.draw.circle(screen, YELLOW, (pacman_x, pacman_y), pacman_radius)
                
                # Dessiner la bouche de Pacman (triangle noir)
                mouth_points = [
                    (pacman_x, pacman_y),
                    (pacman_x + pacman_radius, pacman_y - pacman_radius // 2),
                    (pacman_x + pacman_radius, pacman_y + pacman_radius // 2)
                ]
                pygame.draw.polygon(screen, BLACK, mouth_points)
                
                # Torche devant Pacman (bâton + flamme)
                if item_data.get('type') == 'double longue vue':
                    torch_x = pacman_x + 12  # Torche à droite de Pacman (devant) pour double longue vue
                else:
                    torch_x = center_x + 5  # Torche à droite pour simple longue vue
                torch_y = center_y
                
                # Bâton de la torche (rectangle marron)
                stick_rect = pygame.Rect(torch_x - stick_width // 2, torch_y - stick_height // 2, stick_width, stick_height)
                pygame.draw.rect(screen, (139, 69, 19), stick_rect)  # Marron
                
                # Flamme de la torche (triangle orange/jaune)
                flame_x = torch_x
                flame_y = torch_y - stick_height // 2 - 2
                flame_points = [
                    (flame_x, flame_y - 4),  # Pointe de la flamme
                    (flame_x - 3, flame_y),  # Gauche
                    (flame_x, flame_y + 2),  # Bas
                    (flame_x + 3, flame_y)   # Droite
                ]
                # Flamme extérieure (orange)
                pygame.draw.polygon(screen, (255, 165, 0), flame_points)
                # Flamme intérieure (jaune clair)
                inner_flame_points = [
                    (flame_x, flame_y - 2),
                    (flame_x - 1, flame_y),
                    (flame_x, flame_y + 1),
                    (flame_x + 1, flame_y)
                ]
                pygame.draw.polygon(screen, (255, 255, 200), inner_flame_points)
            elif item_data.get('type') == 'glace':
                # Dessiner une case de glace (bleu avec motif gelé)
                center_x = slot_rect.centerx
                center_y = slot_rect.centery
                
                # Dessiner le fond de glace (bleu)
                ice_color = BLUE  # Bleu
                pygame.draw.rect(screen, ice_color, slot_rect)
                
                # Dessiner des lignes blanches pour l'effet de glace
                pygame.draw.line(screen, (255, 255, 255), 
                               (slot_rect.left, slot_rect.centery), 
                               (slot_rect.right, slot_rect.centery), 2)
                pygame.draw.line(screen, (255, 255, 255), 
                               (slot_rect.centerx, slot_rect.top), 
                               (slot_rect.centerx, slot_rect.bottom), 2)
                
                # Dessiner de petits cristaux de glace
                for i in range(2):
                    for j in range(2):
                        crystal_x = slot_rect.left + (i + 1) * slot_rect.width // 3
                        crystal_y = slot_rect.top + (j + 1) * slot_rect.height // 3
                        pygame.draw.circle(screen, (255, 255, 255), (crystal_x, crystal_y), 2)
            elif item_data.get('type') == 'skin bleu':
                # Dessiner un Pacman bleu miniature
                center_x = slot_rect.centerx
                center_y = slot_rect.centery
                
                # Pacman bleu (cercle bleu avec bouche)
                pacman_radius = 10
                pacman_x = center_x
                pacman_y = center_y
                
                # Dessiner le cercle de Pacman en bleu clair
                pygame.draw.circle(screen, (173, 216, 230), (pacman_x, pacman_y), pacman_radius)
                
                # Dessiner la bouche de Pacman (triangle noir)
                mouth_points = [
                    (pacman_x, pacman_y),
                    (pacman_x + pacman_radius, pacman_y - pacman_radius // 2),
                    (pacman_x + pacman_radius, pacman_y + pacman_radius // 2)
                ]
                pygame.draw.polygon(screen, BLACK, mouth_points)
            elif item_data.get('type') == 'skin orange':
                # Dessiner un Pacman orange miniature
                center_x = slot_rect.centerx
                center_y = slot_rect.centery
                
                # Pacman orange (cercle orange avec bouche)
                pacman_radius = 10
                pacman_x = center_x
                pacman_y = center_y
                
                # Dessiner le cercle de Pacman en orange
                pygame.draw.circle(screen, (255, 165, 0), (pacman_x, pacman_y), pacman_radius)
                
                # Dessiner la bouche de Pacman (triangle noir)
                mouth_points = [
                    (pacman_x, pacman_y),
                    (pacman_x + pacman_radius, pacman_y - pacman_radius // 2),
                    (pacman_x + pacman_radius, pacman_y + pacman_radius // 2)
                ]
                pygame.draw.polygon(screen, BLACK, mouth_points)
            elif item_data.get('type') == 'skin rose':
                # Dessiner un Pacman rose miniature
                center_x = slot_rect.centerx
                center_y = slot_rect.centery
                
                # Pacman rose (cercle rose avec bouche)
                pacman_radius = 10
                pacman_x = center_x
                pacman_y = center_y
                
                # Dessiner le cercle de Pacman en rose
                pygame.draw.circle(screen, (255, 192, 203), (pacman_x, pacman_y), pacman_radius)
                
                # Dessiner la bouche de Pacman (triangle noir)
                mouth_points = [
                    (pacman_x, pacman_y),
                    (pacman_x + pacman_radius, pacman_y - pacman_radius // 2),
                    (pacman_x + pacman_radius, pacman_y + pacman_radius // 2)
                ]
                pygame.draw.polygon(screen, BLACK, mouth_points)
            elif item_data.get('type') == 'skin rouge':
                # Dessiner un Pacman rouge miniature
                center_x = slot_rect.centerx
                center_y = slot_rect.centery
                
                # Pacman rouge (cercle rouge avec bouche)
                pacman_radius = 10
                pacman_x = center_x
                pacman_y = center_y
                
                # Dessiner le cercle de Pacman en rouge
                pygame.draw.circle(screen, RED, (pacman_x, pacman_y), pacman_radius)
                
                # Dessiner la bouche de Pacman (triangle noir)
                mouth_points = [
                    (pacman_x, pacman_y),
                    (pacman_x + pacman_radius, pacman_y - pacman_radius // 2),
                    (pacman_x + pacman_radius, pacman_y + pacman_radius // 2)
                ]
                pygame.draw.polygon(screen, BLACK, mouth_points)
            elif item_data.get('type') == 'lave':
                # Dessiner de la lave (cercle rouge foncé avec effet de bulle)
                center_x = slot_rect.centerx
                center_y = slot_rect.centery
                
                # Cercle principal de la lave (rouge foncé/orange foncé)
                lave_radius = 12
                pygame.draw.circle(screen, (200, 50, 0), (center_x, center_y), lave_radius)  # Rouge foncé
                pygame.draw.circle(screen, (255, 100, 0), (center_x, center_y), lave_radius - 2)  # Orange foncé intérieur
                
                # Dessiner quelques bulles de lave (petits cercles)
                bubble_positions = [
                    (center_x - 3, center_y - 3),
                    (center_x + 3, center_y - 2),
                    (center_x - 2, center_y + 3),
                    (center_x + 2, center_y + 2),
                ]
                for bubble_x, bubble_y in bubble_positions:
                    pygame.draw.circle(screen, (255, 150, 50), (bubble_x, bubble_y), 2)  # Orange clair pour les bulles
            elif item_data.get('type') == 'feu':
                # Dessiner du feu (flamme rouge-orange)
                center_x = slot_rect.centerx
                center_y = slot_rect.centery
                
                # Cercle principal du feu (rouge-orange)
                feu_radius = 12
                pygame.draw.circle(screen, (255, 69, 0), (center_x, center_y), feu_radius)  # Rouge-orange
                pygame.draw.circle(screen, (255, 140, 0), (center_x, center_y), feu_radius - 3)  # Orange intérieur
                
                # Dessiner des flammes (petites formes triangulaires)
                flame_positions = [
                    (center_x - 4, center_y - 4),
                    (center_x + 4, center_y - 3),
                    (center_x - 3, center_y + 4),
                    (center_x + 3, center_y + 3),
                ]
                for flame_x, flame_y in flame_positions:
                    # Petite flamme (triangle pointant vers le haut)
                    flame_points = [
                        (flame_x, flame_y - 3),
                        (flame_x - 2, flame_y + 2),
                        (flame_x + 2, flame_y + 2),
                    ]
                    pygame.draw.polygon(screen, (255, 200, 0), flame_points)  # Jaune-orange pour les flammes
            elif item_data.get('type') == 'explosion':
                # Dessiner une explosion (étoile/cercle avec rayons)
                center_x = slot_rect.centerx
                center_y = slot_rect.centery
                
                # Cercle central de l'explosion (rouge/orange)
                explosion_radius = 12
                pygame.draw.circle(screen, (255, 100, 0), (center_x, center_y), explosion_radius)  # Rouge-orange
                pygame.draw.circle(screen, (255, 200, 0), (center_x, center_y), explosion_radius - 3)  # Jaune-orange intérieur
                
                # Rayons de l'explosion (lignes partant du centre)
                num_rays = 8
                ray_length = explosion_radius + 4
                for i in range(num_rays):
                    angle = (i * 2 * math.pi / num_rays) - math.pi / 2
                    start_x = center_x + (explosion_radius - 2) * math.cos(angle)
                    start_y = center_y + (explosion_radius - 2) * math.sin(angle)
                    end_x = center_x + ray_length * math.cos(angle)
                    end_y = center_y + ray_length * math.sin(angle)
                    pygame.draw.line(screen, (255, 0, 0), (start_x, start_y), (end_x, end_y), 2)  # Rouge vif pour les rayons
                
                # Points d'explosion autour (petites particules)
                for offset_angle in [0, math.pi/2, math.pi, 3*math.pi/2]:
                    part_x = center_x + (explosion_radius + 2) * math.cos(offset_angle)
                    part_y = center_y + (explosion_radius + 2) * math.sin(offset_angle)
                    pygame.draw.circle(screen, (255, 255, 0), (int(part_x), int(part_y)), 2)  # Jaune pour les particules
            elif item_data.get('type') == 'tir':
                # Dessiner un projectile/tir (flèche ou balle)
                center_x = slot_rect.centerx
                center_y = slot_rect.centery
                
                # Cercle principal (orange/rouge)
                bullet_radius = 10
                pygame.draw.circle(screen, (255, 140, 0), (center_x, center_y), bullet_radius)  # Orange foncé
                pygame.draw.circle(screen, (255, 200, 0), (center_x, center_y), bullet_radius - 3)  # Jaune-orange intérieur
                
                # Flèche pointant vers la droite (direction du tir)
                arrow_length = 8
                arrow_start_x = center_x + bullet_radius - 2
                arrow_start_y = center_y
                arrow_end_x = center_x + bullet_radius + arrow_length
                arrow_end_y = center_y
                
                # Ligne principale de la flèche
                pygame.draw.line(screen, (255, 100, 0), (arrow_start_x, arrow_start_y), (arrow_end_x, arrow_end_y), 3)
                
                # Pointe de la flèche (triangle)
                arrow_tip_size = 4
                arrow_tip_points = [
                    (arrow_end_x, arrow_end_y),  # Pointe
                    (arrow_end_x - arrow_tip_size, arrow_end_y - arrow_tip_size // 2),  # Haut
                    (arrow_end_x - arrow_tip_size, arrow_end_y + arrow_tip_size // 2)   # Bas
                ]
                pygame.draw.polygon(screen, (255, 100, 0), arrow_tip_points)
            elif item_data.get('type') == 'vision x':
                # Dessiner une vision X (lunettes ou yeux avec X)
                center_x = slot_rect.centerx
                center_y = slot_rect.centery
                
                # Lunettes/yeux (cercles)
                eye_radius = 8
                eye_spacing = 6
                left_eye_x = center_x - eye_spacing
                right_eye_x = center_x + eye_spacing
                
                # Cercles des yeux (violet foncé)
                pygame.draw.circle(screen, (138, 43, 226), (left_eye_x, center_y), eye_radius)
                pygame.draw.circle(screen, (138, 43, 226), (right_eye_x, center_y), eye_radius)
                pygame.draw.circle(screen, (160, 80, 255), (left_eye_x, center_y), eye_radius - 2)  # Violet clair intérieur
                pygame.draw.circle(screen, (160, 80, 255), (right_eye_x, center_y), eye_radius - 2)
                
                # X au centre (lignes diagonales)
                x_size = 6
                # Ligne diagonale de haut-gauche à bas-droite
                pygame.draw.line(screen, (255, 255, 255), 
                               (center_x - x_size, center_y - x_size), 
                               (center_x + x_size, center_y + x_size), 2)
                # Ligne diagonale de haut-droite à bas-gauche
                pygame.draw.line(screen, (255, 255, 255), 
                               (center_x + x_size, center_y - x_size), 
                               (center_x - x_size, center_y + x_size), 2)
            elif item_data.get('type') == 'mort':
                # Dessiner une faucheuse ou symbole de mort (tête de mort)
                center_x = slot_rect.centerx
                center_y = slot_rect.centery
                
                # Tête de mort (cercle)
                skull_radius = 12
                pygame.draw.circle(screen, (200, 200, 200), (center_x, center_y), skull_radius)  # Gris clair
                pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), skull_radius - 2)  # Blanc
                
                # Orbites des yeux (cercles noirs)
                eye_radius = 3
                eye_offset_y = -3
                pygame.draw.circle(screen, BLACK, (center_x - 4, center_y + eye_offset_y), eye_radius)
                pygame.draw.circle(screen, BLACK, (center_x + 4, center_y + eye_offset_y), eye_radius)
                
                # Nez (triangle inversé)
                nose_points = [
                    (center_x, center_y + 2),
                    (center_x - 2, center_y + 5),
                    (center_x + 2, center_y + 5)
                ]
                pygame.draw.polygon(screen, BLACK, nose_points)
                
                # Bouche (arc ou ligne)
                mouth_start = (center_x - 4, center_y + 6)
                mouth_end = (center_x + 4, center_y + 6)
                # Dessiner un arc pour la bouche (sourire de mort)
                for i in range(5):
                    x = center_x - 3 + i
                    y = center_y + 7 + (i % 2)
                    pygame.draw.circle(screen, BLACK, (x, y), 1)
            elif item_data.get('type') == 'bombe téléguidée':
                # Dessiner une bombe (cercle noir avec mèche)
                center_x = slot_rect.centerx
                center_y = slot_rect.centery
                
                # Corps de la bombe (cercle noir)
                bombe_radius = 10
                pygame.draw.circle(screen, BLACK, (center_x, center_y), bombe_radius)
                
                # Reflet sur la bombe (petit cercle blanc)
                pygame.draw.circle(screen, (100, 100, 100), (center_x - 3, center_y - 3), 3)
                
                # Mèche (ligne brune/rouge)
                mèche_start = (center_x, center_y - bombe_radius)
                mèche_end = (center_x, center_y - bombe_radius - 5)
                pygame.draw.line(screen, (139, 69, 19), mèche_start, mèche_end, 2)  # Brun
                
                # Flamme sur la mèche (petit triangle orange/rouge)
                flame_points = [
                    (center_x, center_y - bombe_radius - 5),
                    (center_x - 2, center_y - bombe_radius - 8),
                    (center_x + 2, center_y - bombe_radius - 8)
                ]
                pygame.draw.polygon(screen, (255, 140, 0), flame_points)  # Orange
            elif item_data.get('type') == 'piège':
                # Dessiner un piège (cercle avec dents ou crocs)
                center_x = slot_rect.centerx
                center_y = slot_rect.centery
                
                # Cercle principal (brun/marron)
                piege_radius = 10
                pygame.draw.circle(screen, (139, 69, 19), (center_x, center_y), piege_radius)  # Brun
                pygame.draw.circle(screen, (101, 50, 14), (center_x, center_y), piege_radius - 2)  # Brun foncé
                
                # Dents/crocs autour du piège (triangles)
                num_teeth = 8
                for i in range(num_teeth):
                    angle = (2 * math.pi * i) / num_teeth
                    tooth_x = center_x + (piege_radius - 1) * math.cos(angle)
                    tooth_y = center_y + (piege_radius - 1) * math.sin(angle)
                    # Triangle pointant vers l'extérieur
                    outer_x = center_x + (piege_radius + 3) * math.cos(angle)
                    outer_y = center_y + (piege_radius + 3) * math.sin(angle)
                    # Points du triangle
                    tooth_points = [
                        (tooth_x, tooth_y),
                        (outer_x, outer_y),
                        (center_x + (piege_radius - 1) * math.cos(angle + 2 * math.pi / num_teeth),
                         center_y + (piege_radius - 1) * math.sin(angle + 2 * math.pi / num_teeth))
                    ]
                    pygame.draw.polygon(screen, (80, 40, 10), tooth_points)  # Brun très foncé
            elif item_data.get('type') == 'tp':
                # Dessiner un symbole de téléportation (cercle violet avec flèches)
                center_x = slot_rect.centerx
                center_y = slot_rect.centery
                
                # Cercle principal (violet)
                tp_radius = 12
                pygame.draw.circle(screen, (128, 0, 128), (center_x, center_y), tp_radius)  # Violet
                pygame.draw.circle(screen, (160, 32, 160), (center_x, center_y), tp_radius - 2)  # Violet clair
                
                # Flèches de téléportation (4 flèches pointant vers l'extérieur)
                arrow_length = 6
                for i in range(4):
                    angle = (2 * math.pi * i) / 4
                    # Ligne de la flèche
                    start_x = center_x + (tp_radius - 2) * math.cos(angle)
                    start_y = center_y + (tp_radius - 2) * math.sin(angle)
                    end_x = center_x + (tp_radius + arrow_length) * math.cos(angle)
                    end_y = center_y + (tp_radius + arrow_length) * math.sin(angle)
                    pygame.draw.line(screen, WHITE, (start_x, start_y), (end_x, end_y), 2)
                    # Pointe de la flèche (triangle)
                    arrow_angle1 = angle + 2.5
                    arrow_angle2 = angle - 2.5
                    arrow_tip_x = end_x
                    arrow_tip_y = end_y
                    arrow_side1_x = end_x - 4 * math.cos(arrow_angle1)
                    arrow_side1_y = end_y - 4 * math.sin(arrow_angle1)
                    arrow_side2_x = end_x - 4 * math.cos(arrow_angle2)
                    arrow_side2_y = end_y - 4 * math.sin(arrow_angle2)
                    pygame.draw.polygon(screen, WHITE, [(arrow_tip_x, arrow_tip_y), (arrow_side1_x, arrow_side1_y), (arrow_side2_x, arrow_side2_y)])
            elif item_data.get('type') == 'portail':
                # Dessiner un portail (cercle bleu avec effet de vortex)
                center_x = slot_rect.centerx
                center_y = slot_rect.centery
                
                # Cercle principal (bleu)
                portal_radius = 12
                pygame.draw.circle(screen, (0, 100, 200), (center_x, center_y), portal_radius)  # Bleu
                pygame.draw.circle(screen, (50, 150, 255), (center_x, center_y), portal_radius - 2)  # Bleu clair
                
                # Effet de vortex (cercles concentriques)
                for i in range(3):
                    inner_radius = portal_radius - 4 - i * 2
                    if inner_radius > 2:
                        pygame.draw.circle(screen, (100, 200, 255), (center_x, center_y), inner_radius, 1)
                
                # Lignes de connexion (simuler un portail)
                for i in range(4):
                    angle = (2 * math.pi * i) / 4 + math.pi / 4
                    start_x = center_x + (portal_radius - 3) * math.cos(angle)
                    start_y = center_y + (portal_radius - 3) * math.sin(angle)
                    end_x = center_x + (portal_radius + 2) * math.cos(angle)
                    end_y = center_y + (portal_radius + 2) * math.sin(angle)
                    pygame.draw.line(screen, (150, 220, 255), (start_x, start_y), (end_x, end_y), 1)
            elif item_data.get('type') == 'mur':
                # Dessiner un mur (rectangle gris avec briques)
                center_x = slot_rect.centerx
                center_y = slot_rect.centery
                
                # Rectangle principal (gris)
                wall_width = 20
                wall_height = 15
                wall_rect = pygame.Rect(center_x - wall_width // 2, center_y - wall_height // 2, wall_width, wall_height)
                pygame.draw.rect(screen, (100, 100, 100), wall_rect)  # Gris
                pygame.draw.rect(screen, (80, 80, 80), wall_rect, 2)  # Bordure gris foncé
                
                # Lignes de briques (horizontal)
                for i in range(2):
                    y_line = center_y - wall_height // 2 + (i + 1) * (wall_height // 3)
                    pygame.draw.line(screen, (70, 70, 70), (center_x - wall_width // 2, y_line), (center_x + wall_width // 2, y_line), 1)
                
                # Lignes de briques (vertical, décalées)
                for i in range(3):
                    x_line = center_x - wall_width // 2 + i * (wall_width // 3)
                    if i % 2 == 0:  # Lignes verticales sur les briques paires
                        pygame.draw.line(screen, (70, 70, 70), (x_line, center_y - wall_height // 2), (x_line, center_y + wall_height // 2), 1)
            elif item_data.get('type') == 'bon marché':
                # Dessiner une pièce de monnaie (cercle jaune/orange avec symbole)
                center_x = slot_rect.centerx
                center_y = slot_rect.centery
                
                # Cercle de la pièce (jaune-orange)
                coin_radius = 12
                pygame.draw.circle(screen, (255, 200, 0), (center_x, center_y), coin_radius)
                pygame.draw.circle(screen, (255, 220, 100), (center_x, center_y), coin_radius - 2)
                
                # Symbole $ ou € au centre (simplifié en ligne)
                font_coin = pygame.font.Font(None, 16)
                coin_symbol = font_coin.render("$", True, (200, 150, 0))
                coin_symbol_rect = coin_symbol.get_rect(center=(center_x, center_y))
                screen.blit(coin_symbol, coin_symbol_rect)
            elif item_data.get('type') == 'gadget':
                # Dessiner un gadget (cercle bleu avec symbole d'éclair)
                center_x = slot_rect.centerx
                center_y = slot_rect.centery
                
                # Cercle du gadget (bleu)
                gadget_radius = 12
                pygame.draw.circle(screen, (100, 150, 255), (center_x, center_y), gadget_radius)
                pygame.draw.circle(screen, (150, 200, 255), (center_x, center_y), gadget_radius - 2)
                
                # Symbole d'éclair au centre (utiliser "G" si l'éclair ne fonctionne pas)
                font_gadget = pygame.font.Font(None, 18)
                try:
                    gadget_symbol = font_gadget.render("⚡", True, (255, 255, 0))  # Jaune
                except:
                    gadget_symbol = font_gadget.render("G", True, (255, 255, 0))  # Jaune
                gadget_symbol_rect = gadget_symbol.get_rect(center=(center_x, center_y))
                screen.blit(gadget_symbol, gadget_symbol_rect)
            elif item_data.get('type') == 'pacgum':
                # Dessiner une pacgomme (cercle jaune avec symbole)
                center_x = slot_rect.centerx
                center_y = slot_rect.centery
                
                # Cercle de la pacgomme (jaune)
                pacgum_radius = 12
                pygame.draw.circle(screen, YELLOW, (center_x, center_y), pacgum_radius)
                pygame.draw.circle(screen, (255, 255, 200), (center_x, center_y), pacgum_radius - 2)
                
                # Symbole "P" au centre
                font_pacgum = pygame.font.Font(None, 18)
                pacgum_symbol = font_pacgum.render("P", True, (200, 150, 0))  # Jaune foncé
                pacgum_symbol_rect = pacgum_symbol.get_rect(center=(center_x, center_y))
                screen.blit(pacgum_symbol, pacgum_symbol_rect)
            elif item_data.get('type') == 'indigestion':
                # Dessiner une capacité indigestion (cercle vert avec symbole)
                center_x = slot_rect.centerx
                center_y = slot_rect.centery
                
                # Cercle de la capacité indigestion (vert clair)
                indigestion_radius = 12
                pygame.draw.circle(screen, (0, 255, 100), (center_x, center_y), indigestion_radius)
                pygame.draw.circle(screen, (100, 255, 150), (center_x, center_y), indigestion_radius - 2)
                
                # Symbole "I" au centre
                font_indigestion = pygame.font.Font(None, 18)
                indigestion_symbol = font_indigestion.render("I", True, (0, 200, 0))  # Vert foncé
                indigestion_symbol_rect = indigestion_symbol.get_rect(center=(center_x, center_y))
                screen.blit(indigestion_symbol, indigestion_symbol_rect)
            elif item_data.get('type') == 'gel':
                # Dessiner une capacité gel (cercle bleu moyen avec symbole)
                center_x = slot_rect.centerx
                center_y = slot_rect.centery
                
                # Cercle de la capacité gel (bleu moyen)
                gel_radius = 12
                pygame.draw.circle(screen, (100, 150, 255), (center_x, center_y), gel_radius)
                pygame.draw.circle(screen, (150, 200, 255), (center_x, center_y), gel_radius - 2)
                
                # Symbole flocon de neige au centre
                # Dessiner un flocon de neige simple
                flake_size = 6
                # Ligne verticale
                pygame.draw.line(screen, (255, 255, 255), 
                               (center_x, center_y - flake_size), 
                               (center_x, center_y + flake_size), 2)
                # Ligne horizontale
                pygame.draw.line(screen, (255, 255, 255), 
                               (center_x - flake_size, center_y), 
                               (center_x + flake_size, center_y), 2)
                # Lignes diagonales
                diag_size = 4
                # Diagonale haut-gauche vers bas-droite
                pygame.draw.line(screen, (255, 255, 255), 
                               (center_x - diag_size, center_y - diag_size), 
                               (center_x + diag_size, center_y + diag_size), 1)
                # Diagonale haut-droite vers bas-gauche
                pygame.draw.line(screen, (255, 255, 255), 
                               (center_x + diag_size, center_y - diag_size), 
                               (center_x - diag_size, center_y + diag_size), 1)
            elif item_data.get('type') == 'lunette':
                # Dessiner une capacité lunette (cercle bleu très clair avec symbole de lunettes)
                center_x = slot_rect.centerx
                center_y = slot_rect.centery
                
                # Cercle de la capacité lunette (bleu très clair)
                lunette_radius = 12
                pygame.draw.circle(screen, (200, 200, 255), (center_x, center_y), lunette_radius)
                pygame.draw.circle(screen, (230, 230, 255), (center_x, center_y), lunette_radius - 2)
                
                # Dessiner des lunettes simples (deux cercles avec une barre)
                # Cercle gauche
                pygame.draw.circle(screen, (100, 100, 150), (center_x - 4, center_y), 4, 2)
                # Cercle droit
                pygame.draw.circle(screen, (100, 100, 150), (center_x + 4, center_y), 4, 2)
                # Barre entre les deux cercles
                pygame.draw.line(screen, (100, 100, 150), 
                               (center_x - 4, center_y), 
                               (center_x + 4, center_y), 2)
            elif item_data.get('type') == 'invincibilité':
                # Dessiner une capacité invincibilité (cercle doré avec symbole)
                center_x = slot_rect.centerx
                center_y = slot_rect.centery
                
                # Cercle de la capacité invincibilité (doré)
                invincibilite_radius = 12
                pygame.draw.circle(screen, (255, 215, 0), (center_x, center_y), invincibilite_radius)
                pygame.draw.circle(screen, (255, 235, 100), (center_x, center_y), invincibilite_radius - 2)
                
                # Symbole bouclier ou étoile au centre (utiliser "I" si le symbole ne fonctionne pas)
                font_invincibilite = pygame.font.Font(None, 18)
                try:
                    invincibilite_symbol = font_invincibilite.render("🛡", True, (200, 150, 0))  # Or foncé
                except:
                    invincibilite_symbol = font_invincibilite.render("I", True, (200, 150, 0))  # Or foncé
                invincibilite_symbol_rect = invincibilite_symbol.get_rect(center=(center_x, center_y))
                screen.blit(invincibilite_symbol, invincibilite_symbol_rect)
            elif item_data.get('type') == 'piquant':
                # Dessiner une capacité piquant (cercle rose/rouge avec épines)
                center_x = slot_rect.centerx
                center_y = slot_rect.centery
                
                # Cercle de la capacité piquant (rose/rouge foncé)
                piquant_radius = 12
                pygame.draw.circle(screen, (255, 0, 100), (center_x, center_y), piquant_radius)
                pygame.draw.circle(screen, (200, 0, 80), (center_x, center_y), piquant_radius - 2)
                
                # Dessiner des épines autour du cercle (triangles pointus)
                num_spikes = 8
                for i in range(num_spikes):
                    angle = (i * 2 * math.pi / num_spikes) - math.pi / 2
                    spike_x = center_x + (piquant_radius - 1) * math.cos(angle)
                    spike_y = center_y + (piquant_radius - 1) * math.sin(angle)
                    outer_x = center_x + (piquant_radius + 3) * math.cos(angle)
                    outer_y = center_y + (piquant_radius + 3) * math.sin(angle)
                    # Triangle pour l'épine
                    spike_points = [
                        (spike_x, spike_y),
                        (outer_x, outer_y),
                        (center_x + (piquant_radius - 1) * math.cos(angle + 2 * math.pi / num_spikes),
                         center_y + (piquant_radius - 1) * math.sin(angle + 2 * math.pi / num_spikes))
                    ]
                    pygame.draw.polygon(screen, (150, 0, 60), spike_points)
            elif item_data.get('type') == 'bonne vue':
                # Dessiner une capacité bonne vue (cercle bleu clair avec lunettes/yeux améliorés)
                center_x = slot_rect.centerx
                center_y = slot_rect.centery
                
                # Cercle de la capacité bonne vue (bleu clair)
                bonne_vue_radius = 12
                pygame.draw.circle(screen, (0, 150, 255), (center_x, center_y), bonne_vue_radius)
                pygame.draw.circle(screen, (100, 200, 255), (center_x, center_y), bonne_vue_radius - 2)
                
                # Dessiner des lunettes (deux cercles pour les verres + pont)
                # Verre gauche
                left_eye_x = center_x - 4
                left_eye_y = center_y
                pygame.draw.circle(screen, (200, 230, 255), (left_eye_x, left_eye_y), 4)
                pygame.draw.circle(screen, (0, 100, 200), (left_eye_x, left_eye_y), 4, 1)
                # Verre droit
                right_eye_x = center_x + 4
                right_eye_y = center_y
                pygame.draw.circle(screen, (200, 230, 255), (right_eye_x, right_eye_y), 4)
                pygame.draw.circle(screen, (0, 100, 200), (right_eye_x, right_eye_y), 4, 1)
                # Pont entre les verres
                pygame.draw.line(screen, (0, 100, 200), (left_eye_x + 3, center_y), (right_eye_x - 3, center_y), 2)
                # Pupilles dans les verres
                pygame.draw.circle(screen, (0, 50, 150), (left_eye_x, left_eye_y), 2)
                pygame.draw.circle(screen, (0, 50, 150), (right_eye_x, right_eye_y), 2)
            elif item_data.get('type') == 'bonbe':
                # Dessiner une capacité bonbe (cercle rouge foncé avec symbole d'explosion)
                center_x = slot_rect.centerx
                center_y = slot_rect.centery
                
                # Cercle de la capacité bonbe (rouge foncé)
                bonbe_radius = 12
                pygame.draw.circle(screen, (150, 0, 0), (center_x, center_y), bonbe_radius)
                pygame.draw.circle(screen, (200, 50, 50), (center_x, center_y), bonbe_radius - 2)
                
                # Dessiner un symbole d'explosion au centre (étoile à 4 branches)
                star_size = 6
                star_points = []
                for i in range(8):
                    angle = (i * 2 * math.pi / 8) - math.pi / 2
                    if i % 2 == 0:
                        # Point extérieur
                        outer_x = center_x + star_size * math.cos(angle)
                        outer_y = center_y + star_size * math.sin(angle)
                        star_points.append((outer_x, outer_y))
                    else:
                        # Point intérieur
                        inner_x = center_x + (star_size * 0.5) * math.cos(angle)
                        inner_y = center_y + (star_size * 0.5) * math.sin(angle)
                        star_points.append((inner_x, inner_y))
                pygame.draw.polygon(screen, (255, 100, 0), star_points)  # Orange pour l'explosion
            elif item_data.get('type') == 'glace':
                # Dessiner une capacité glace (cercle violet avec symbole)
                center_x = slot_rect.centerx
                center_y = slot_rect.centery
                
                # Cercle de la capacité glace (violet)
                glace_radius = 12
                pygame.draw.circle(screen, (148, 0, 211), (center_x, center_y), glace_radius)
                pygame.draw.circle(screen, (170, 20, 230), (center_x, center_y), glace_radius - 2)
                
                # Symbole "G" au centre
                font_glace = pygame.font.Font(None, 18)
                glace_symbol = font_glace.render("G", True, (101, 67, 33))  # Marron foncé
                glace_symbol_rect = glace_symbol.get_rect(center=(center_x, center_y))
                screen.blit(glace_symbol, glace_symbol_rect)
            elif item_data.get('type') == 'pièce mythique':
                # Dessiner une pièce mythique (cercle violet avec étoile)
                center_x = slot_rect.centerx
                center_y = slot_rect.centery
                
                # Cercle de la pièce (violet sombre e clair)
                coin_radius = 14
                pygame.draw.circle(screen, (138, 43, 226), (center_x, center_y), coin_radius)  # Violet sombre (bleu-violet)
                pygame.draw.circle(screen, (186, 85, 211), (center_x, center_y), coin_radius - 2)  # Violet moyen
                pygame.draw.circle(screen, (147, 112, 219), (center_x, center_y), coin_radius - 4)  # Violet clair (intérieur)
                pygame.draw.circle(screen, (75, 0, 130), (center_x, center_y), coin_radius, 2)  # Bordure violette très sombre
                
                # Effet de texture avec des cercles supplémentaires pour donner de la profondeur
                pygame.draw.circle(screen, (221, 160, 221), (center_x - 3, center_y - 3), 4)  # Reflet violet clair
                pygame.draw.circle(screen, (148, 0, 211), (center_x + 3, center_y + 3), 3)  # Ombre violette sombre
                
                # Étoile au centre (symbole mythique)
                star_size = 8
                star_points = []
                for i in range(5):
                    angle = (i * 2 * math.pi / 5) - math.pi / 2
                    # Point extérieur
                    outer_x = center_x + star_size * math.cos(angle)
                    outer_y = center_y + star_size * math.sin(angle)
                    star_points.append((outer_x, outer_y))
                    # Point intérieur
                    inner_angle = angle + math.pi / 5
                    inner_x = center_x + (star_size * 0.4) * math.cos(inner_angle)
                    inner_y = center_y + (star_size * 0.4) * math.sin(inner_angle)
                    star_points.append((inner_x, inner_y))
                pygame.draw.polygon(screen, (255, 240, 255), star_points)  # Blanc violet très clair pour l'étoile
            elif item_data.get('type') == 'grosse armure':
                # Dessiner une grosse armure (bouclier/armure)
                center_x = slot_rect.centerx
                center_y = slot_rect.centery
                
                # Bouclier principal (forme d'écu)
                shield_width = 20
                shield_height = 24
                shield_points = [
                    (center_x, center_y - shield_height // 2),  # Haut (pointe)
                    (center_x + shield_width // 2, center_y - shield_height // 4),  # Haut droite
                    (center_x + shield_width // 2, center_y + shield_height // 4),  # Bas droite
                    (center_x, center_y + shield_height // 2),  # Bas (pointe)
                    (center_x - shield_width // 2, center_y + shield_height // 4),  # Bas gauche
                    (center_x - shield_width // 2, center_y - shield_height // 4)   # Haut gauche
                ]
                # Couleur de l'armure (gris métallique/marron)
                pygame.draw.polygon(screen, (139, 69, 19), shield_points)  # Marron (couleur d'armure)
                pygame.draw.polygon(screen, (101, 67, 33), shield_points, 2)  # Bordure marron foncé
                
                # Lignes de renforcement (croix)
                pygame.draw.line(screen, (101, 67, 33), (center_x, center_y - shield_height // 2), (center_x, center_y + shield_height // 2), 2)  # Ligne verticale
                pygame.draw.line(screen, (101, 67, 33), (center_x - shield_width // 3, center_y), (center_x + shield_width // 3, center_y), 2)  # Ligne horizontale
            elif item_data.get('type') == 'armure de fer':
                # Dessiner une armure de fer (bouclier/armure grise)
                center_x = slot_rect.centerx
                center_y = slot_rect.centery
                
                # Bouclier principal (forme d'écu)
                shield_width = 20
                shield_height = 24
                shield_points = [
                    (center_x, center_y - shield_height // 2),  # Haut (pointe)
                    (center_x + shield_width // 2, center_y - shield_height // 4),  # Haut droite
                    (center_x + shield_width // 2, center_y + shield_height // 4),  # Bas droite
                    (center_x, center_y + shield_height // 2),  # Bas (pointe)
                    (center_x - shield_width // 2, center_y + shield_height // 4),  # Bas gauche
                    (center_x - shield_width // 2, center_y - shield_height // 4)   # Haut gauche
                ]
                # Couleur de l'armure de fer (gris métallique)
                pygame.draw.polygon(screen, (105, 105, 105), shield_points)  # Gris (couleur de fer)
                pygame.draw.polygon(screen, (70, 70, 70), shield_points, 2)  # Bordure gris foncé
                
                # Lignes de renforcement (croix)
                pygame.draw.line(screen, (70, 70, 70), (center_x, center_y - shield_height // 2), (center_x, center_y + shield_height // 2), 2)  # Ligne verticale
                pygame.draw.line(screen, (70, 70, 70), (center_x - shield_width // 3, center_y), (center_x + shield_width // 3, center_y), 2)  # Ligne horizontale
                
                # Bosses/rivets (cercles)
                for offset_x, offset_y in [(-shield_width // 4, -shield_height // 4), (shield_width // 4, -shield_height // 4), 
                                           (-shield_width // 4, shield_height // 4), (shield_width // 4, shield_height // 4)]:
                    pygame.draw.circle(screen, (200, 150, 100), (center_x + offset_x, center_y + offset_y), 2)  # Rivets dorés
            elif item_data.get('type') == 'flamme':
                # Dessiner une flamme (feu orange-rouge)
                center_x = slot_rect.centerx
                center_y = slot_rect.centery
                
                # Flamme principale (forme de flamme avec plusieurs couches)
                flame_points = [
                    (center_x, center_y - 12),  # Pointe haute
                    (center_x + 6, center_y - 4),  # Droite haute
                    (center_x + 8, center_y + 4),  # Droite milieu
                    (center_x + 4, center_y + 8),  # Droite bas
                    (center_x, center_y + 10),  # Bas
                    (center_x - 4, center_y + 8),  # Gauche bas
                    (center_x - 8, center_y + 4),  # Gauche milieu
                    (center_x - 6, center_y - 4)   # Gauche haute
                ]
                # Couche extérieure (rouge foncé)
                pygame.draw.polygon(screen, (200, 50, 0), flame_points)  # Rouge foncé
                # Couche intérieure (orange)
                inner_flame_points = [
                    (center_x, center_y - 8),
                    (center_x + 4, center_y - 2),
                    (center_x + 5, center_y + 2),
                    (center_x + 2, center_y + 5),
                    (center_x, center_y + 6),
                    (center_x - 2, center_y + 5),
                    (center_x - 5, center_y + 2),
                    (center_x - 4, center_y - 2)
                ]
                pygame.draw.polygon(screen, (255, 140, 0), inner_flame_points)  # Orange
                # Coeur de la flamme (jaune)
                pygame.draw.circle(screen, (255, 255, 0), (center_x, center_y), 3)  # Jaune
            elif item_data.get('type') == 'givre':
                # Dessiner du givre (cristaux de glace bleu clair/blanc)
                center_x = slot_rect.centerx
                center_y = slot_rect.centery
                
                # Fond bleu clair/blanc (couleur de givre)
                pygame.draw.rect(screen, (200, 220, 255), slot_rect)  # Bleu clair/blanc
                
                # Dessiner des cristaux de glace (étoiles/hexagones)
                # Cristal principal au centre
                crystal_size = 8
                crystal_points = [
                    (center_x, center_y - crystal_size),  # Haut
                    (center_x + crystal_size * 0.866, center_y - crystal_size * 0.5),  # Haut droite
                    (center_x + crystal_size * 0.866, center_y + crystal_size * 0.5),  # Bas droite
                    (center_x, center_y + crystal_size),  # Bas
                    (center_x - crystal_size * 0.866, center_y + crystal_size * 0.5),  # Bas gauche
                    (center_x - crystal_size * 0.866, center_y - crystal_size * 0.5)   # Haut gauche
                ]
                pygame.draw.polygon(screen, (255, 255, 255), crystal_points)  # Blanc
                pygame.draw.polygon(screen, (180, 200, 255), crystal_points, 2)  # Bordure bleu clair
                
                # Petits cristaux autour
                for offset_x, offset_y in [(-6, -6), (6, -6), (-6, 6), (6, 6)]:
                    small_crystal_size = 4
                    small_crystal_points = [
                        (center_x + offset_x, center_y + offset_y - small_crystal_size),
                        (center_x + offset_x + small_crystal_size * 0.866, center_y + offset_y - small_crystal_size * 0.5),
                        (center_x + offset_x + small_crystal_size * 0.866, center_y + offset_y + small_crystal_size * 0.5),
                        (center_x + offset_x, center_y + offset_y + small_crystal_size),
                        (center_x + offset_x - small_crystal_size * 0.866, center_y + offset_y + small_crystal_size * 0.5),
                        (center_x + offset_x - small_crystal_size * 0.866, center_y + offset_y - small_crystal_size * 0.5)
                    ]
                    pygame.draw.polygon(screen, (240, 245, 255), small_crystal_points)  # Blanc très clair
            elif item_data.get('type') == 'bric':
                # Dessiner une brique (rectangle marron avec lignes)
                center_x = slot_rect.centerx
                center_y = slot_rect.centery
                
                # Fond marron (couleur de brique)
                pygame.draw.rect(screen, (139, 69, 19), slot_rect)  # Marron
                
                # Dessiner une brique (rectangle avec lignes horizontales)
                brick_width = 24
                brick_height = 12
                brick_rect = pygame.Rect(center_x - brick_width // 2, center_y - brick_height // 2, brick_width, brick_height)
                pygame.draw.rect(screen, (160, 82, 45), brick_rect)  # Marron plus clair
                pygame.draw.rect(screen, (101, 67, 33), brick_rect, 2)  # Bordure marron foncé
                
                # Lignes horizontales pour l'effet de brique
                pygame.draw.line(screen, (101, 67, 33), (brick_rect.left, center_y - 2), (brick_rect.right, center_y - 2), 1)
                pygame.draw.line(screen, (101, 67, 33), (brick_rect.left, center_y + 2), (brick_rect.right, center_y + 2), 1)
            elif item_data.get('type') == 'infra rouge':
                # Dessiner un infra rouge (cristal rouge)
                center_x = slot_rect.centerx
                center_y = slot_rect.centery
                
                # Fond rouge
                pygame.draw.rect(screen, (255, 0, 0), slot_rect)  # Rouge
                
                # Dessiner un cristal rouge au centre
                crystal_size = 10
                crystal_points = [
                    (center_x, center_y - crystal_size),  # Haut
                    (center_x + crystal_size * 0.866, center_y - crystal_size * 0.5),  # Haut droite
                    (center_x + crystal_size * 0.866, center_y + crystal_size * 0.5),  # Bas droite
                    (center_x, center_y + crystal_size),  # Bas
                    (center_x - crystal_size * 0.866, center_y + crystal_size * 0.5),  # Bas gauche
                    (center_x - crystal_size * 0.866, center_y - crystal_size * 0.5)   # Haut gauche
                ]
                pygame.draw.polygon(screen, (200, 0, 0), crystal_points)  # Rouge foncé
                pygame.draw.polygon(screen, (255, 100, 100), crystal_points, 2)  # Bordure rouge clair
                
                # Ligne centrale (reflet)
                pygame.draw.line(screen, (255, 150, 150), (center_x, center_y - crystal_size), (center_x, center_y + crystal_size), 2)
            elif item_data.get('type') == 'coffre fort':
                # Dessiner un coffre fort (coffre doré avec serrure)
                center_x = slot_rect.centerx
                center_y = slot_rect.centery
                
                # Fond doré (couleur de coffre fort)
                pygame.draw.rect(screen, (184, 134, 11), slot_rect)  # Or
                
                # Dessiner un coffre (rectangle avec couvercle)
                chest_width = 28
                chest_height = 18
                chest_rect = pygame.Rect(center_x - chest_width // 2, center_y - chest_height // 2, chest_width, chest_height)
                pygame.draw.rect(screen, (218, 165, 32), chest_rect)  # Or plus clair
                pygame.draw.rect(screen, (139, 101, 8), chest_rect, 2)  # Bordure or foncé
                
                # Couvercle (ligne horizontale en haut)
                pygame.draw.line(screen, (139, 101, 8), (chest_rect.left, chest_rect.top), (chest_rect.right, chest_rect.top), 3)
                
                # Serrure (cercle au centre)
                pygame.draw.circle(screen, (139, 101, 8), (center_x, center_y), 4)  # Serrure
                pygame.draw.circle(screen, (184, 134, 11), (center_x, center_y), 2)  # Intérieur de la serrure
            elif item_data.get('type') == 'coffre au trésor':
                # Dessiner un coffre au trésor (coffre doré brillant avec trésor)
                center_x = slot_rect.centerx
                center_y = slot_rect.centery
                
                # Fond or brillant (couleur de coffre au trésor)
                pygame.draw.rect(screen, (255, 215, 0), slot_rect)  # Or brillant
                
                # Dessiner un coffre (rectangle avec couvercle)
                chest_width = 28
                chest_height = 18
                chest_rect = pygame.Rect(center_x - chest_width // 2, center_y - chest_height // 2, chest_width, chest_height)
                pygame.draw.rect(screen, (255, 223, 0), chest_rect)  # Or plus brillant
                pygame.draw.rect(screen, (184, 134, 11), chest_rect, 2)  # Bordure or foncé
                
                # Couvercle (ligne horizontale en haut)
                pygame.draw.line(screen, (184, 134, 11), (chest_rect.left, chest_rect.top), (chest_rect.right, chest_rect.top), 3)
                
                # Serrure (cercle au centre)
                pygame.draw.circle(screen, (139, 101, 8), (center_x, center_y), 4)  # Serrure
                pygame.draw.circle(screen, (255, 215, 0), (center_x, center_y), 2)  # Intérieur de la serrure
                
                # Étoiles/étincelles autour (effet de trésor)
                for offset_x, offset_y in [(-10, -8), (10, -8), (-10, 8), (10, 8)]:
                    pygame.draw.circle(screen, (255, 255, 0), (center_x + offset_x, center_y + offset_y), 2)  # Petites étoiles jaunes
            elif item_data.get('type') == 'double gadget':
                # Dessiner un double gadget (deux gadgets côte à côte en violet)
                center_x = slot_rect.centerx
                center_y = slot_rect.centery
                
                # Deux cercles côte à côte (gadgets)
                circle_radius = 8
                circle_spacing = 6
                
                # Premier gadget (gauche)
                pygame.draw.circle(screen, (128, 0, 128), (center_x - circle_spacing // 2, center_y), circle_radius)  # Violet
                pygame.draw.circle(screen, WHITE, (center_x - circle_spacing // 2, center_y), circle_radius, 1)  # Bordure blanche
                
                # Deuxième gadget (droite)
                pygame.draw.circle(screen, (128, 0, 128), (center_x + circle_spacing // 2, center_y), circle_radius)  # Violet
                pygame.draw.circle(screen, WHITE, (center_x + circle_spacing // 2, center_y), circle_radius, 1)  # Bordure blanche
                
                # Point au centre de chaque gadget
                pygame.draw.circle(screen, WHITE, (center_x - circle_spacing // 2, center_y), 2)  # Point blanc
                pygame.draw.circle(screen, WHITE, (center_x + circle_spacing // 2, center_y), 2)  # Point blanc
    
    # Afficher le nom de l'objet au-dessus de l'objet si la souris passe dessus
    hovered_item_name = None
    hovered_item_type = None
    if mouse_pos is not None:
        mouse_x, mouse_y = mouse_pos
        # Vérifier si la souris est sur un objet
        for slot_name, item_data in inventaire_items.items():
            if slot_name in slots:
                slot_rect = slots[slot_name]
                if slot_rect.collidepoint(mouse_x, mouse_y):
                    # Obtenir le nom de l'objet
                    item_type = item_data.get('type', '')
                    hovered_item_type = item_type
                    # Mapper les types aux noms affichés
                    item_names = {
                        'longue vue': 'Longue vue',
                        'double longue vue': 'Double longue vue',
                        'bon repas': 'Bon repas',
                        'bon goût': 'Bon goût',
                        'pas d\'indigestion': 'Pas d\'indigestion',
                        'glace': 'Glace',
                        'skin bleu': 'Skin bleu',
                        'skin orange': 'Skin orange',
                        'skin rose': 'Skin rose',
                        'skin rouge': 'Skin rouge',
                        'bon marché': 'Bon marché',
                        'gadget': 'Gadget',
                        'pacgum': 'Pacgum',
                        'indigestion': 'Indigestion',
                        'lave': 'Lave',
                        'feu': 'Feu',
                        'flamme': 'Flamme',
                        'givre': 'Givre',
                        'infra rouge': 'Infra rouge',
                        'bric': 'Bric',
                        'coffre fort': 'Coffre fort',
                        'coffre au trésor': 'Coffre au trésor',
                        'grosse armure': 'Grosse armure',
                        'armure de fer': 'Armure de fer',
                        'double gadget': 'Double gadget'
                    }
                    hovered_item_name = item_names.get(item_type, item_type.capitalize())
                    break
    
    # Afficher le nom de l'objet au-dessus de l'objet
    if hovered_item_name:
        # Trouver le slot survolé pour positionner le texte
        for slot_name, item_data in inventaire_items.items():
            if slot_name in slots:
                slot_rect = slots[slot_name]
                if mouse_pos and slot_rect.collidepoint(mouse_pos[0], mouse_pos[1]):
                    # Afficher le nom au-dessus du slot
                    font_name = pygame.font.Font(None, 24)
                    name_text = font_name.render(hovered_item_name, True, YELLOW)
                    name_text_rect = name_text.get_rect(center=(slot_rect.centerx, slot_rect.top - 15))
                    # Dessiner un fond noir pour le texte
                    padding = 5
                    bg_rect = pygame.Rect(
                        name_text_rect.x - padding,
                        name_text_rect.y - padding,
                        name_text_rect.width + padding * 2,
                        name_text_rect.height + padding * 2
                    )
                    pygame.draw.rect(screen, BLACK, bg_rect)
                    pygame.draw.rect(screen, WHITE, bg_rect, 1)
                    screen.blit(name_text, name_text_rect)
                    break
    
    # Afficher la description de l'item si elle existe ou si on survole un objet
    if item_description or (hovered_item_type and mouse_pos):
        # Zone de description en bas de l'écran
        desc_y = WINDOW_HEIGHT - 120
        desc_height = 100
        desc_rect = pygame.Rect(10, desc_y, WINDOW_WIDTH - 20, desc_height)
        pygame.draw.rect(screen, (50, 50, 50), desc_rect)
        pygame.draw.rect(screen, WHITE, desc_rect, 2)
        
        # Afficher la rareté si on survole un objet (même si item_description existe)
        if hovered_item_type:
            rarity_name, rarity_color = get_item_rarity(hovered_item_type)
            font_rarity = pygame.font.Font(None, 28)
            rarity_text = font_rarity.render(f"Rareté: {rarity_name}", True, rarity_color)
            rarity_text_rect = rarity_text.get_rect(x=20, y=desc_y + 10)
            screen.blit(rarity_text, rarity_text_rect)
        
        # Afficher le texte de description si elle existe
        if item_description:
            font_desc = pygame.font.Font(None, 24)
            # Diviser le texte en lignes si nécessaire
            words = item_description.split(' ')
            lines = []
            current_line = ""
            for word in words:
                test_line = current_line + word + " " if current_line else word + " "
                text_width = font_desc.size(test_line)[0]
                if text_width > WINDOW_WIDTH - 40:
                    if current_line:
                        lines.append(current_line)
                    current_line = word + " "
                else:
                    current_line = test_line
            if current_line:
                lines.append(current_line)
            
            # Afficher les lignes (limiter à 3 lignes maximum si rareté affichée, sinon 4)
            max_lines = min(len(lines), 3 if hovered_item_type else 4)
            start_y = desc_y + 40 if hovered_item_type else desc_y + 10
            for i in range(max_lines):
                desc_text = font_desc.render(lines[i], True, WHITE)
                screen.blit(desc_text, (20, start_y + i * 25))
    
    return retour_button, slots, start_button_for_slots if show_start_button else None

def draw_vente(screen, inventaire_items=None, jeton_poche=0, crown_poche=0, scroll_offset=0, capacite_items=None, bon_marche_ameliore=False):
    """Dessine l'écran de vente"""
    if inventaire_items is None:
        inventaire_items = {}
    if capacite_items is None:
        capacite_items = []
    
    # Calculer le niveau total de "bon marché" (nombre total d'achats)
    bon_marche_level = capacite_items.count("bon marché")
    
    # Réduction de prix : 5 par niveau (niveau 1 = 5, niveau 2 = 10, etc.)
    # Si amélioré avec couronnes, double la réduction
    price_reduction = bon_marche_level * 5
    if bon_marche_ameliore and bon_marche_level > 0:
        price_reduction *= 2
    
    screen.fill(BLACK)
    
    # Titre
    font_title = pygame.font.Font(None, 72)
    title_text = font_title.render("VENTE", True, (255, 140, 0))  # Orange
    title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, 50))
    screen.blit(title_text, title_rect)
    
    # Afficher les pacoins et couronnes disponibles
    font_info = pygame.font.Font(None, 36)
    pacoin_text = font_info.render(f"Pacoins: {jeton_poche}", True, WHITE)
    screen.blit(pacoin_text, (WINDOW_WIDTH//2 - 100, 100))
    crown_text = font_info.render(f"Couronnes: {crown_poche}", True, WHITE)
    screen.blit(crown_text, (WINDOW_WIDTH//2 - 100, 130))
    
    # Bouton retour
    font_button = pygame.font.Font(None, 36)
    retour_button = pygame.Rect(10, 10, 100, 40)
    pygame.draw.rect(screen, RED, retour_button)
    pygame.draw.rect(screen, WHITE, retour_button, 2)
    retour_text = font_button.render("RETOUR", True, WHITE)
    retour_text_rect = retour_text.get_rect(center=retour_button.center)
    screen.blit(retour_text, retour_text_rect)
    
    # Instructions
    font_instructions = pygame.font.Font(None, 24)
    instructions_text = font_instructions.render("Cliquez sur un objet pour le vendre", True, WHITE)
    instructions_rect = instructions_text.get_rect(center=(WINDOW_WIDTH//2, 180))
    screen.blit(instructions_text, instructions_rect)
    
    # Définir les prix de vente de base (50% du prix d'achat, arrondi)
    base_sell_prices = {
        'longue vue': (500, 0),  # 50% de 1000
        'double longue vue': (2000, 0),  # 50% de 4000
        'bon repas': (1000, 0),  # 50% de 2000
        'bon goût': (1500, 0),  # 50% de 3000
        'pas d\'indigestion': (2500, 0),  # 50% de 5000
        'glace': (1500, 50),  # 50% de 3000 pacoins et 100 couronnes
        'skin bleu': (5000, 500),  # 50% de 10000 pacoins et 1000 couronnes
        'skin orange': (5000, 500),  # 50% de 10000 pacoins et 1000 couronnes
        'skin rose': (5000, 500),  # 50% de 10000 pacoins et 1000 couronnes
        'skin rouge': (5000, 500),  # 50% de 10000 pacoins et 1000 couronnes
        'bon marché': (2500, 0),  # 50% de 5000
        'lave': (2500, 0),  # 50% de 5000
        'feu': (2500, 0),  # 50% de 5000
        'explosion': (5000, 0),  # 50% de 10000
        'tir': (500, 0),  # 50% de 1000
        'vision x': (5000, 0),  # 50% de 10000
        'mort': (7500, 0),  # 50% de 15000
        'bombe téléguidée': (10000, 0),  # 50% de 20000
        'piège': (2500, 0),  # 50% de 5000
        'tp': (1500, 0),  # 50% de 3000
        'portail': (2000, 0),  # 50% de 4000
        'mur': (1250, 0),  # 50% de 2500
        'pièce mythique': (5000, 25),  # 50% de 10000 pacoins et 50 couronnes
        'grosse armure': (250, 0),  # 50% de 500
        'armure de fer': (250, 0),  # 50% de 500
        'flamme': (1000, 0),  # 50% de 2000
        'givre': (1500, 0),  # 50% de 3000
        'infra rouge': (2000, 0),  # 50% de 4000
        'bric': (2500, 0),  # 50% de 5000
        'coffre fort': (5000, 0),  # 50% de 10000
        'coffre au trésor': (7500, 0),  # 50% de 15000
        'gadget': (5000, 500),  # 50% de 10000 pacoins et 1000 couronnes
        'double gadget': (4000, 0),  # Prix de vente fixe de 4000 pacoins
        'pacgum': (2000, 0),  # 50% de 4000
        'indigestion': (1750, 0),  # 50% de 3500
        'gel': (2500, 0),  # 50% de 5000
        'lunette': (5000, 5000),  # 50% de 10000 pacoins et 10000 couronnes
        'invincibilité': (2500, 0),  # 50% de 5000
        'piquant': (2500, 0),  # 50% de 5000
        'bonne vue': (2500, 0),  # 50% de 5000
        'bonbe': (2500, 0),  # 50% de 5000
    }
    
    # Appliquer la réduction de prix aux prix de vente (seulement pour les pacoins, pas pour les couronnes)
    sell_prices = {}
    for item_type, (base_pacoins, base_crowns) in base_sell_prices.items():
        # Réduction de 5 pacoins par niveau (appliquée à la moitié du prix d'achat)
        # La réduction est la moitié de la réduction d'achat (car prix de vente = 50% du prix d'achat)
        reduction_sell = price_reduction // 2  # Diviser par 2 car on vend à 50% du prix d'achat
        reduced_pacoins = max(0, base_pacoins - reduction_sell)
        sell_prices[item_type] = (reduced_pacoins, base_crowns)
    
    # Afficher les items de l'inventaire avec leurs prix de vente
    font_item = pygame.font.Font(None, 18)  # Réduit de 24 à 18
    font_price = pygame.font.Font(None, 16)  # Réduit de 20 à 16
    start_y = 220
    item_height = 35  # Réduit de 50 à 35
    item_spacing = 3  # Réduit de 5 à 3
    items_per_column = 12  # Augmenté de 8 à 12 pour afficher plus d'items
    column_width = WINDOW_WIDTH // 2 - 20
    column_x1 = 20
    column_x2 = WINDOW_WIDTH // 2 + 10
    
    items_list = list(inventaire_items.items())
    
    # Créer une liste de rectangles pour les items
    item_rects = {}
    
    for idx, (slot_name, item_data) in enumerate(items_list):
        item_type = item_data.get('type', '')
        item_name = item_data.get('name', item_type)
        
        # Déterminer la colonne et la position (avec défilement)
        if idx < items_per_column:
            x_pos = column_x1
            y_pos = start_y + idx * (item_height + item_spacing) - scroll_offset
        else:
            x_pos = column_x2
            y_pos = start_y + (idx - items_per_column) * (item_height + item_spacing) - scroll_offset
        
        # Ne dessiner que les items visibles à l'écran
        visible_area_top = 180
        visible_area_bottom = WINDOW_HEIGHT
        
        # Rectangle de l'item
        item_rect = pygame.Rect(x_pos, y_pos, column_width - 40, item_height)
        item_rects[slot_name] = item_rect
        
        # Ne dessiner que si l'item est visible
        if y_pos + item_height >= visible_area_top and y_pos <= visible_area_bottom:
            # Couleur de fond (gris foncé)
            pygame.draw.rect(screen, (60, 60, 60), item_rect)
            pygame.draw.rect(screen, WHITE, item_rect, 2)
            
            # Nom de l'item
            name_text = font_item.render(item_name, True, WHITE)
            screen.blit(name_text, (item_rect.x + 5, item_rect.y + 3))
            
            # Prix de vente
            if item_type in sell_prices:
                pacoins_price, crowns_price = sell_prices[item_type]
                if crowns_price > 0:
                    price_text = font_price.render(f"Vendre: {pacoins_price} pacoins, {crowns_price} couronnes", True, BLACK)
                else:
                    price_text = font_price.render(f"Vendre: {pacoins_price} pacoins", True, BLACK)
                screen.blit(price_text, (item_rect.x + 5, item_rect.y + 18))
            else:
                price_text = font_price.render("Vendre: 0 pacoins", True, (128, 128, 128))
                screen.blit(price_text, (item_rect.x + 5, item_rect.y + 18))
    
    return retour_button, item_rects, sell_prices

def draw_poche(screen, crown_poche=0, jeton_poche=0, gemme_poche=0):
    """Dessine l'écran de la poche"""
    screen.fill(BLACK)
    
    font_title = pygame.font.Font(None, 72)
    title_text = font_title.render("POCHE", True, YELLOW)
    title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, 100))
    screen.blit(title_text, title_rect)
    
    # Afficher les compteurs
    font = pygame.font.Font(None, 48)
    y_offset = 200
    spacing = 60
    
    # Afficher le compteur de couronnes dans la poche
    crown_count_text = font.render(f"Couronnes: {crown_poche}", True, (255, 215, 0))  # Or
    crown_rect = crown_count_text.get_rect(center=(WINDOW_WIDTH//2, y_offset))
    screen.blit(crown_count_text, crown_rect)
    
    # Afficher le compteur de jetons dans la poche
    jeton_count_text = font.render(f"Jetons: {jeton_poche}", True, (255, 192, 203))  # Rose
    jeton_rect = jeton_count_text.get_rect(center=(WINDOW_WIDTH//2, y_offset + spacing))
    screen.blit(jeton_count_text, jeton_rect)
    
    # Afficher le compteur de gemmes dans la poche
    gemme_count_text = font.render(f"Gemmes: {gemme_poche}", True, (0, 255, 255))  # Cyan
    gemme_rect = gemme_count_text.get_rect(center=(WINDOW_WIDTH//2, y_offset + spacing * 2))
    screen.blit(gemme_count_text, gemme_rect)
    
    # Bouton retour
    font_button = pygame.font.Font(None, 36)
    retour_button = pygame.Rect(10, 10, 100, 40)
    pygame.draw.rect(screen, RED, retour_button)
    pygame.draw.rect(screen, WHITE, retour_button, 2)
    retour_text = font_button.render("RETOUR", True, WHITE)
    retour_text_rect = retour_text.get_rect(center=retour_button.center)
    screen.blit(retour_text, retour_text_rect)
    
    return retour_button

def draw_boutique(screen, jeton_poche=0, crown_poche=0, gemme_poche=0):
    """Dessine le menu de la boutique pour échanger des devises"""
    screen.fill(BLACK)
    
    font_title = pygame.font.Font(None, 72)
    title_text = font_title.render("BOUTIQUE", True, (255, 215, 0))  # Or
    title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, 100))
    screen.blit(title_text, title_rect)
    
    # Afficher les devises disponibles
    font_currency = pygame.font.Font(None, 36)
    currency_y = 180
    spacing = 40
    
    pacoins_text = font_currency.render(f"Pacoins: {jeton_poche}", True, (255, 192, 203))  # Rose
    pacoins_rect = pacoins_text.get_rect(center=(WINDOW_WIDTH//2, currency_y))
    screen.blit(pacoins_text, pacoins_rect)
    
    couronnes_text = font_currency.render(f"Couronnes: {crown_poche}", True, (255, 215, 0))  # Or
    couronnes_rect = couronnes_text.get_rect(center=(WINDOW_WIDTH//2, currency_y + spacing))
    screen.blit(couronnes_text, couronnes_rect)
    
    gemmes_text = font_currency.render(f"Gemmes: {gemme_poche}", True, (0, 255, 255))  # Cyan
    gemmes_rect = gemmes_text.get_rect(center=(WINDOW_WIDTH//2, currency_y + spacing * 2))
    screen.blit(gemmes_text, gemmes_rect)
    
    # Boutons d'échange
    font_button = pygame.font.Font(None, 32)
    button_width = 400
    button_height = 60
    button_spacing = 80
    start_y = 350
    
    # Échange 1: 500 pacoins → 1 couronne
    exchange1_button = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, start_y, button_width, button_height)
    pygame.draw.rect(screen, (0, 200, 0), exchange1_button)  # Vert
    pygame.draw.rect(screen, WHITE, exchange1_button, 2)
    exchange1_text = font_button.render("500 Pacoins → 1 Couronne", True, WHITE)
    exchange1_text_rect = exchange1_text.get_rect(center=exchange1_button.center)
    screen.blit(exchange1_text, exchange1_text_rect)
    
    # Échange 2: 1 couronne → 500 pacoins
    exchange2_button = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, start_y + button_spacing, button_width, button_height)
    pygame.draw.rect(screen, (0, 200, 0), exchange2_button)  # Vert
    pygame.draw.rect(screen, WHITE, exchange2_button, 2)
    exchange2_text = font_button.render("1 Couronne → 500 Pacoins", True, WHITE)
    exchange2_text_rect = exchange2_text.get_rect(center=exchange2_button.center)
    screen.blit(exchange2_text, exchange2_text_rect)
    
    # Échange 3: 10 gemmes → 10 couronnes
    exchange3_button = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, start_y + button_spacing * 2, button_width, button_height)
    pygame.draw.rect(screen, (0, 200, 0), exchange3_button)  # Vert
    pygame.draw.rect(screen, WHITE, exchange3_button, 2)
    exchange3_text = font_button.render("10 Gemmes → 10 Couronnes", True, WHITE)
    exchange3_text_rect = exchange3_text.get_rect(center=exchange3_button.center)
    screen.blit(exchange3_text, exchange3_text_rect)
    
    # Bouton retour
    font_retour = pygame.font.Font(None, 36)
    retour_button = pygame.Rect(10, 10, 100, 40)
    pygame.draw.rect(screen, RED, retour_button)
    pygame.draw.rect(screen, WHITE, retour_button, 2)
    retour_text = font_retour.render("RETOUR", True, WHITE)
    retour_text_rect = retour_text.get_rect(center=retour_button.center)
    screen.blit(retour_text, retour_text_rect)
    
    return retour_button, exchange1_button, exchange2_button, exchange3_button

def save_accounts_data(accounts):
    """Sauvegarde tous les comptes dans un fichier JSON"""
    try:
        with open('pacman_accounts.json', 'w', encoding='utf-8') as f:
            json.dump(accounts, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des comptes: {e}")

def load_accounts_data():
    """Charge tous les comptes depuis un fichier JSON"""
    save_file = 'pacman_accounts.json'
    if os.path.exists(save_file):
        try:
            with open(save_file, 'r', encoding='utf-8') as f:
                accounts = json.load(f)
                if not isinstance(accounts, list):
                    accounts = []
                for account in accounts:
                    ensure_account_structure(account)
                return accounts
        except Exception as e:
            print(f"Erreur lors du chargement des comptes: {e}")
            return []
    return []

def save_game_data_for_account(account_index, pouvoir_items, gadget_items, objet_items, capacite_items, inventaire_items, jeton_poche, crown_poche, bon_marche_ameliore, battle_pass_xp=0, battle_pass_claimed_rewards=None, gemme_poche=0, used_stars=None, accounts_list=None, battle_pass_plus_claimed_rewards=None, used_stars_plus=None, pass_plus_purchased=False):
    """Sauvegarde les données de jeu d'un compte spécifique"""
    if accounts_list is None:
        accounts_list = load_accounts_data()
    if used_stars is None:
        used_stars = []
    if used_stars_plus is None:
        used_stars_plus = []
    if 0 <= account_index < len(accounts_list):
        accounts_list[account_index]['game_data'] = {
            'pouvoir_items': pouvoir_items,
            'gadget_items': gadget_items,
            'objet_items': objet_items,
            'capacite_items': capacite_items,
            'inventaire_items': inventaire_items,
            'jeton_poche': jeton_poche,
            'crown_poche': crown_poche,
            'bon_marche_ameliore': bon_marche_ameliore,
            'battle_pass_xp': battle_pass_xp,
            'battle_pass_claimed_rewards': battle_pass_claimed_rewards if battle_pass_claimed_rewards is not None else [],
            'battle_pass_plus_claimed_rewards': battle_pass_plus_claimed_rewards if battle_pass_plus_claimed_rewards is not None else [],
            'gemme_poche': gemme_poche,
            'used_stars': used_stars,
            'used_stars_plus': used_stars_plus,
            'pass_plus_purchased': pass_plus_purchased
        }
        save_accounts_data(accounts_list)

def load_game_data_for_account(account_index):
    """Charge les données de jeu d'un compte spécifique"""
    accounts = load_accounts_data()
    if 0 <= account_index < len(accounts) and 'game_data' in accounts[account_index]:
        game_data = accounts[account_index]['game_data']
        return (
            game_data.get('pouvoir_items', []),
            game_data.get('gadget_items', []),
            game_data.get('objet_items', []),
            game_data.get('capacite_items', []),
            game_data.get('inventaire_items', {}),
            game_data.get('jeton_poche', 0),
            game_data.get('crown_poche', 0),
            game_data.get('bon_marche_ameliore', False),
            int(game_data.get('battle_pass_xp', 0)) if isinstance(game_data.get('battle_pass_xp', 0), (int, float)) else 0,
            game_data.get('battle_pass_claimed_rewards', []),
            int(game_data.get('gemme_poche', 0)) if isinstance(game_data.get('gemme_poche', 0), (int, float)) else 0,
            game_data.get('used_stars', []),
            game_data.get('battle_pass_plus_claimed_rewards', []),
            game_data.get('used_stars_plus', []),
            game_data.get('pass_plus_purchased', False)
        )
    return [], [], [], [], {}, 0, 0, False, 0, [], 0, [], [], [], False

def all_battle_pass_rewards_claimed(battle_pass_claimed_rewards, used_stars, max_level=30):
    """Vérifie si toutes les récompenses du battle pass ont été récupérées"""
    for level in range(1, max_level + 1):
        if level not in battle_pass_claimed_rewards and level not in used_stars:
            return False
    return True

def auto_save_account_data(account_index, pouvoir_items, gadget_items, objet_items, capacite_items, inventaire_items, jeton_poche, crown_poche, bon_marche_ameliore, battle_pass_xp, battle_pass_claimed_rewards=None, gemme_poche=0, used_stars=None, accounts_list=None, battle_pass_plus_claimed_rewards=None, used_stars_plus=None, pass_plus_purchased=False):
    """Sauvegarde automatiquement les données du compte actuel"""
    if account_index is not None:
        if battle_pass_claimed_rewards is None:
            battle_pass_claimed_rewards = []
        if used_stars is None:
            used_stars = []
        if battle_pass_plus_claimed_rewards is None:
            battle_pass_plus_claimed_rewards = []
        if used_stars_plus is None:
            used_stars_plus = []
        save_game_data_for_account(account_index, pouvoir_items, gadget_items, objet_items, capacite_items, inventaire_items, jeton_poche, crown_poche, bon_marche_ameliore, battle_pass_xp, battle_pass_claimed_rewards, gemme_poche, used_stars, accounts_list, battle_pass_plus_claimed_rewards, used_stars_plus, pass_plus_purchased)

def main():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Pacman")
    clock = pygame.time.Clock()
    
    # États du jeu
    START_MENU = "start_menu"
    CUSTOMIZATION_MENU = "customization_menu"
    FONT_MENU = "font_menu"
    AVATAR_MENU = "avatar_menu"
    NAME_MENU = "name_menu"
    MENU = "menu"
    TUTORIAL_MENU = "tutorial_menu"
    SKILL_TREE_MENU = "skill_tree_menu"
    SURVIE_SKILL_TREE_MENU = "survie_skill_tree_menu"
    EQUIPEMENT_SKILL_TREE_MENU = "equipement_skill_tree_menu"
    AVENTURE_MENU = "aventure_menu"
    PASSE_MENU = "passe_menu"
    BOUTIQUE = "boutique"
    PASSE_PLUS_MENU = "passe_plus_menu"
    STAR_UPGRADE_MENU = "star_upgrade_menu"
    GAME = "game"
    SHOP = "shop"
    SHOP_GADGET = "shop_gadget"
    SHOP_POUVOIR = "shop_pouvoir"
    SHOP_CAPACITE = "shop_capacite"
    SHOP_OBJET = "shop_objet"
    DIFFICULTY = "difficulty"
    POCHE = "poche"
    INVENTAIRE = "inventaire"
    VENTE = "vente"
    
    current_state = START_MENU  # Commencer par le menu de démarrage
    
    # Créer une copie du labyrinthe pour pouvoir modifier les points (niveau 1 = MAZE_1)
    maze = [row[:] for row in MAZES[0]]
    
    # Position initiale de Pacman
    pacman = Pacman(10, 15)
    
    # Créer des fantômes (niveau 1 : 1 fantôme bleu)
    ghosts = [
        Ghost(10, 9, BLUE),
    ]
    # Définir le chemin pour tous les fantômes bleus
    for ghost in ghosts:
        if ghost.color == BLUE:
            ghost.set_path(maze)
    
    score = 0
    level = 1
    MAX_LIVES = 5  # Nombre maximum de vies
    last_bonus_score = 0  # Dernier multiple de 2000 atteint
    game_over = False
    won = False
    vulnerable_timer = 0
    VULNERABLE_DURATION = 50  # Durée de vulnérabilité en frames (5 secondes à 10 FPS)
    level_transition = False
    level_transition_timer = 0
    respawn_timer = 0  # Timer pour la réapparition après perte de vie
    crown_timer = 0  # Timer pour la couronne après avoir mangé un fantôme (3 secondes)
    crown_count = 0  # Compteur de couronnes gagnées pendant le jeu (temporaires)
    grande_couronne_count = 0  # Compteur de grandes couronnes
    last_ghost_time = 0  # Timer depuis le dernier fantôme mangé (en frames)
    difficulty = None  # Difficulté choisie ("facile", "moyen", "difficile")
    first_level_success_unlocked = False  # Succès "Premier niveau" déjà débloqué
    success_notification_text = ""  # Texte du dernier succès débloqué
    success_notification_timer = 0  # Timer d'affichage du succès (1 s = 60 frames)
    is_adventure_mode = False  # Mode aventure activé ou non
    # Variables pour le système de maps 4x4 aux niveaux multiples de 10 en mode aventure
    map_x = 0  # Coordonnée X dans la grille 4x4 (0-3)
    map_y = 0  # Coordonnée Y dans la grille 4x4 (0-3)
    is_multi_map_mode = False  # Si on est en mode multi-map (niveau multiple de 10 en aventure)
    
    # Initialiser les données de jeu (seront chargées quand un compte est sélectionné)
    pouvoir_items = []  # Liste des items de pouvoir achetés
    gadget_items = []  # Liste des items de gadget achetés
    capacite_items = []  # Liste des items de capacité achetés
    objet_items = []  # Liste des items d'objet achetés
    inventaire_items_loaded = {}  # Dictionnaire des items dans l'inventaire {slot_name: item_data}
    jeton_poche = 0
    crown_poche = 0
    bon_marche_ameliore = False
    battle_pass_xp = 0  # XP du passe de combat
    battle_pass_claimed_rewards = []  # Liste des récompenses récupérées du passe de combat
    battle_pass_plus_claimed_rewards = []  # Liste des récompenses récupérées du passe de combat +
    pass_plus_purchased = False  # Indique si le pass + a été acheté
    star_rarity = "rare"  # Rareté de l'étoile (rare, super_rare, epique, legendaire)
    star_clicks_remaining = 5  # Nombre de clics restants sur l'étoile
    xp_doubler_active = False  # Doubleur d'XP actif pour la prochaine partie
    xp_doublers_count = 0  # Nombre de doubleurs d'XP disponibles
    vulnerable_ghosts_eaten_this_game = 0  # Nombre de fantômes vulnérables mangés dans cette partie
    used_stars = []  # Liste des niveaux d'étoiles déjà utilisées
    used_stars_plus = []  # Liste des niveaux d'étoiles déjà utilisées dans le pass +
    current_star_level = None  # Niveau de l'étoile actuellement ouverte
    is_plus_star = False  # Indique si l'étoile actuelle est du pass +
    reward_animations = []  # Liste des animations de récompenses actives
    passe_scroll_offset = 0  # Décalage de défilement pour le menu du battle pass
    
    inventaire_items = inventaire_items_loaded.copy() if inventaire_items_loaded else {}  # Dictionnaire des items dans l'inventaire {slot_name: item_data}
    jeton_count = 0  # Compteur de jetons gagnés pendant le jeu (temporaires)
    # Calculer le bonus d'invincibilité selon le niveau de la capacité équipée
    invincibilite_bonus = calculate_invincibilite_bonus(capacite_items, inventaire_items)
    invincibility_timer = 30 + invincibilite_bonus  # 3 secondes d'invincibilité au spawn (30 frames à 10 FPS) + bonus
    game_initialized = False  # Variable pour suivre si le jeu a été initialisé (pour éviter de réinitialiser les vies à chaque retour)
    game_needs_reset = False  # Variable pour suivre si la partie doit être réinitialisée au retour
    # Initialiser les vies : base 2 + bonus d'armures (grosse armure et armure de fer)
    armor_lives_bonus_init = calculate_armor_lives_bonus(inventaire_items)
    lives = 2 + armor_lives_bonus_init  # Chaque armure équipée donne +1 coeur (jusqu'à +2 si les deux sont équipées)
    selected_item = None  # Item sélectionné pour le drag and drop (slot_name, item_data)
    indigestion_timer = 0  # Timer pour l'indigestion (1 minute = 600 frames à 10 FPS)
    super_vie_active = False  # État de la super vie (invincibilité permanente sans clignotement)
    has_indigestion = False  # État d'indigestion
    item_description = None  # Description de l'item à afficher (None ou texte)
    rainbow_timer = 0  # Timer pour l'effet arc-en-ciel du coup critique (2 secondes = 20 frames à 10 FPS)
    is_rainbow_critique = False  # État d'arc-en-ciel (coup critique)
    ice_tiles = {}  # Dictionnaire pour stocker les cases de glace: {(x, y): timestamp}
    ICE_DURATION = 30  # Durée de la glace en frames (3 secondes à 10 FPS)
    pacman_last_pos = (pacman.x, pacman.y)  # Position précédente de Pacman pour créer la glace
    fire_tiles = {}  # Dictionnaire pour stocker les cases de feu: {(x, y): timestamp}
    FIRE_DURATION = 100  # Durée du feu en frames (10 secondes à 10 FPS)
    fire_active = False  # État d'activation du feu (si True, créer du feu sur le chemin)
    fire_timer = 0  # Timer pour la durée d'activation du feu (10 secondes)
    pacgomme_timers = {}  # Dictionnaire pour stocker les timers de réapparition des pacgommes: {(x, y): timer}
    PACGOMME_RESPAWN_TIME = 20  # Temps de réapparition des pacgommes en frames (2 secondes à 10 FPS)
    ghost_timers = {}  # Dictionnaire pour stocker les timers de réapparition des fantômes en mode aventure: {(start_x, start_y, color): timer}
    GHOST_RESPAWN_TIME = 50  # Temps de réapparition des fantômes en frames (5 secondes à 10 FPS)
    gadget_cooldown = 0  # Cooldown entre les utilisations de gadget (25 secondes = 250 frames à 10 FPS)
    GADGET_COOLDOWN_DURATION = 250  # Durée du cooldown en frames (25 secondes à 10 FPS)
    MORT_COOLDOWN_DURATION = 600  # Durée du cooldown pour "mort" en frames (1 minute = 60 secondes = 600 frames à 10 FPS)
    mort_cooldown = 0  # Cooldown spécifique pour le gadget "mort"
    gadget_use_count = 0  # Compteur d'utilisations pour "double gadget" (alternance recharge instantanée/normale)
    BOMBE_COOLDOWN_DURATION = 600  # Durée du cooldown pour "bombe téléguidée" en frames (1 minute = 60 secondes = 600 frames à 10 FPS)
    bombe_cooldown = 0  # Cooldown spécifique pour le gadget "bombe téléguidée"
    bombe_active = False  # État d'activation de la bombe téléguidée
    bombe_x = 0  # Position X de la bombe
    bombe_y = 0  # Position Y de la bombe
    bombe_timer = 0  # Timer avant l'explosion (10 secondes = 100 frames à 10 FPS)
    BOMBE_EXPLOSION_DELAY = 100  # Délai avant explosion en frames (10 secondes à 10 FPS)
    pacman_frozen = False  # Indique si Pacman est gelé (pendant le contrôle de la bombe)
    pieges = {}  # Dictionnaire pour stocker les pièges posés: {(x, y): True} (True = piège actif)
    PIEGE_IMMOBILISATION_DURATION = 100  # Durée d'immobilisation en frames (10 secondes à 10 FPS)
    portal1_pos = None  # Position du premier portail (x, y) ou None
    portal2_pos = None  # Position du deuxième portail (x, y) ou None
    portal_use_count = 0  # Compteur d'utilisation du portail (0, 1, ou 2)
    mur_pos = None  # Position du mur créé (x, y) ou None
    mur_use_count = 0  # Compteur d'utilisation du mur (0 ou 1)
    
    # Variables pour les boutons de difficulté
    retour_button = None
    button1 = None
    button2 = None
    button3 = None
    button4 = None
    # Variables pour les boutons du magasin
    # Variables pour l'inventaire
    inventaire_retour_button = None
    inventaire_slots = None
    inventaire_start_button = None
    inventaire_before_game = False  # Variable pour savoir si on est dans l'inventaire avant de commencer la partie
    music_playing = False  # Variable pour suivre si la musique est en cours de lecture
    shop_retour_button = None
    shop_gadget_button = None
    shop_pouvoir_button = None
    shop_objet_button = None
    shop_capacite_button = None
    # Variables pour les boutons de l'écran gadget
    shop_gadget_retour_button = None
    # Variables pour les boutons de l'écran pouvoir
    shop_pouvoir_retour_button = None
    shop_longue_vue_button = None
    shop_double_longue_vue_button = None
    shop_bon_repas_button = None
    shop_bon_gout_button = None
    shop_pas_indigestion_button = None
    shop_skin_orange_button = None
    shop_skin_rose_button = None
    shop_skin_rouge_button = None
    # Variable pour le bouton retour dans le jeu
    game_retour_button = None
    
    # Variable pour le défilement dans l'écran de vente
    vente_scroll_offset = 0
    
    # Variable pour le défilement dans le menu de démarrage
    start_menu_scroll_offset = 0
    start_menu_total_height = 0  # Hauteur totale du contenu dans le menu de démarrage
    
    # Variables pour les comptes multiples
    accounts = load_accounts_data()  # Charger les comptes sauvegardés
    current_account_index = None  # Index du compte actuellement sélectionné
    creating_new_account = False  # Si on est en train de créer un nouveau compte
    
    # Variables pour la suppression de compte
    account_long_press_timer = 0  # Timer pour détecter l'appui long
    account_long_press_index = None  # Index du compte sur lequel on maintient le clic
    mouse_button_down = False  # Si le bouton de la souris est enfoncé
    delete_confirmation_step = 0  # 0 = pas de confirmation, 1 = première confirmation, 2 = deuxième confirmation
    account_to_delete = None  # Index du compte à supprimer
    
    # Variables pour le menu nom (pour la création/édition de compte)
    player_name = ""  # Nom du joueur
    name_input_active = False  # Si le champ de texte est actif
    
    # Variable pour l'avatar sélectionné
    selected_avatar = None  # "avatar1", "avatar2", "avatar3" ou None
    
    # Variable pour la police sélectionnée
    selected_font = None  # Nom de fichier de la font sélectionnée (ou valeur legacy)
    pending_font = None  # Nom de fichier temporaire dans le menu font
    pending_avatar = None  # Sélection temporaire dans le menu avatar
    tutorial_page = 0  # Page actuelle du tutoriel
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.MOUSEWHEEL:
                # Gérer le défilement dans le menu de démarrage
                if current_state == START_MENU:
                    # Constantes utilisées dans draw_start_menu
                    start_y = 50
                    
                    # Utiliser la hauteur totale calculée lors du dernier dessin
                    # Si c'est la première frame, utiliser une estimation
                    if start_menu_total_height == 0:
                        start_x = 50
                        circle_radius = 50
                        spacing = 120
                        line_height = circle_radius * 2 + 110
                        
                        # Estimer la hauteur totale
                        num_valid_accounts = sum(1 for acc in accounts if acc.get('player_name') and acc.get('selected_avatar') and acc.get('selected_font'))
                        if num_valid_accounts > 0:
                            # Calculer le nombre de lignes nécessaires
                            accounts_per_line = max(1, (WINDOW_WIDTH - start_x * 2) // spacing)
                            num_lines = (num_valid_accounts + accounts_per_line) // accounts_per_line
                            if (num_valid_accounts % accounts_per_line) == 0 and num_valid_accounts > 0:
                                num_lines += 1  # Ligne pour le bouton "+"
                            total_height = start_y + num_lines * line_height
                        else:
                            total_height = start_y + line_height
                    else:
                        total_height = start_menu_total_height
                    
                    # Calculer le défilement maximum
                    visible_area_bottom = WINDOW_HEIGHT
                    max_scroll = max(0, total_height - visible_area_bottom + start_y)
                    
                    # Ajuster le défilement selon la molette (event.y est positif vers le haut, négatif vers le bas)
                    scroll_speed = 30  # Vitesse de défilement
                    start_menu_scroll_offset += event.y * scroll_speed
                    
                    # Limiter le défilement
                    start_menu_scroll_offset = max(0, min(start_menu_scroll_offset, max_scroll))
                # Gérer le défilement dans l'écran de vente
                elif current_state == VENTE:
                    # Calculer le nombre total d'items
                    num_items = len(inventaire_items)
                    # Utiliser les mêmes valeurs que dans draw_vente
                    items_per_column = 12
                    item_height = 35
                    item_spacing = 3
                    start_y = 220
                    visible_area_top = 180
                    visible_area_bottom = WINDOW_HEIGHT
                    visible_height = visible_area_bottom - visible_area_top
                    
                    # Calculer la hauteur totale nécessaire pour afficher tous les items
                    # Les items sont répartis en deux colonnes : items_per_column dans la première, le reste dans la deuxième
                    num_items_col1 = min(items_per_column, num_items)
                    num_items_col2 = max(0, num_items - items_per_column)
                    # Le nombre de lignes est le maximum entre les deux colonnes
                    num_rows_col1 = num_items_col1
                    num_rows_col2 = num_items_col2
                    max_rows = max(num_rows_col1, num_rows_col2)
                    
                    # Calculer le défilement maximum
                    # La position du dernier item (en bas) serait : start_y + (max_rows - 1) * (item_height + item_spacing) + item_height
                    # Pour que le dernier item soit visible, on doit avoir :
                    # start_y + (max_rows - 1) * (item_height + item_spacing) + item_height - scroll_offset <= visible_area_bottom
                    # Donc : scroll_offset >= start_y + (max_rows - 1) * (item_height + item_spacing) + item_height - visible_area_bottom
                    if max_rows > 0:
                        last_item_bottom = start_y + (max_rows - 1) * (item_height + item_spacing) + item_height
                        max_scroll = max(0, last_item_bottom - visible_area_bottom)
                    else:
                        max_scroll = 0
                    
                    # Ajuster le défilement selon la molette (event.y est positif vers le haut, négatif vers le bas)
                    scroll_speed = 30  # Vitesse de défilement
                    vente_scroll_offset += event.y * scroll_speed
                    
                    # Limiter le défilement
                    vente_scroll_offset = max(0, min(vente_scroll_offset, max_scroll))
                # Gérer le défilement dans le menu du battle pass
                elif current_state == PASSE_MENU:
                    # Calculer la hauteur totale nécessaire pour afficher tous les niveaux
                    MAX_BATTLE_PASS_LEVEL = 30
                    rewards_per_row = 10
                    reward_spacing = 55
                    rewards_start_y = 120 + 40 + 30  # progress_y + progress_height + 30
                    num_rows = (MAX_BATTLE_PASS_LEVEL + rewards_per_row - 1) // rewards_per_row
                    total_height = rewards_start_y + num_rows * reward_spacing
                    
                    # Calculer le défilement maximum
                    visible_area_bottom = WINDOW_HEIGHT - 60  # Réserver de l'espace pour le bouton +100 XP
                    max_scroll = max(0, total_height - visible_area_bottom + rewards_start_y)
                    
                    # Ajuster le défilement selon la molette
                    scroll_speed = 30
                    passe_scroll_offset += event.y * scroll_speed
                    
                    # Limiter le défilement
                    passe_scroll_offset = max(0, min(passe_scroll_offset, max_scroll))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Clic gauche
                    mouse_pos = event.pos
                    mouse_button_down = True
                    
                    if current_state == START_MENU and delete_confirmation_step == 0:
                        # Vérifier si on clique sur un compte pour commencer l'appui long
                        account_clicked = False
                        for rect_type, rect, account_idx in start_profile_rects:
                            if rect_type == "profile" and rect.collidepoint(mouse_pos):
                                # Sélectionner le compte
                                account_long_press_index = account_idx
                                account_long_press_timer = 0
                                account_clicked = True
                                break
                        
                        # Si on a cliqué sur le bouton "+"
                        if not account_clicked and start_plus_button and start_plus_button.collidepoint(mouse_pos):
                            # Créer un nouveau compte
                            creating_new_account = True
                            player_name = ""
                            selected_avatar = None
                            selected_font = None
                            pending_font = None
                            pending_avatar = None
                            current_state = CUSTOMIZATION_MENU
                    elif (current_state == START_MENU or current_state == MENU) and delete_confirmation_step > 0:
                        # Gérer les clics sur les boutons de confirmation
                        # Calculer les positions des boutons (même logique que dans draw_delete_confirmation)
                        dialog_width = 500
                        dialog_height = 200
                        dialog_x = (WINDOW_WIDTH - dialog_width) // 2
                        dialog_y = (WINDOW_HEIGHT - dialog_height) // 2
                        button_width = 100
                        button_height = 40
                        button_spacing = 20
                        # OUI toujours à droite, NON toujours à gauche
                        non_button = pygame.Rect(dialog_x + dialog_width // 2 - button_width - button_spacing // 2, dialog_y + 130, button_width, button_height)
                        oui_button = pygame.Rect(dialog_x + dialog_width // 2 + button_spacing // 2, dialog_y + 130, button_width, button_height)
                        
                        if oui_button.collidepoint(mouse_pos):
                            if delete_confirmation_step == 1:
                                # Première confirmation : passer à la deuxième
                                delete_confirmation_step = 2
                            elif delete_confirmation_step == 2:
                                # Deuxième confirmation : supprimer le compte
                                if account_to_delete is not None and account_to_delete < len(accounts):
                                    accounts.pop(account_to_delete)
                                    save_accounts_data(accounts)
                                    # Réinitialiser les variables
                                    delete_confirmation_step = 0
                                    account_to_delete = None
                                    account_long_press_index = None
                                    account_long_press_timer = 0
                                    # Si on était dans MENU, retourner au menu de démarrage
                                    if current_state == MENU:
                                        current_account_index = None
                                        current_state = START_MENU
                        elif non_button.collidepoint(mouse_pos):
                            # Annuler la suppression
                            delete_confirmation_step = 0
                            account_to_delete = None
                            account_long_press_index = None
                            account_long_press_timer = 0
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Relâchement du clic gauche
                    mouse_pos = event.pos
                    mouse_button_down = False
                    
                    if current_state == START_MENU and delete_confirmation_step == 0:
                        # Si on relâche avant le temps d'appui long, c'est un clic normal
                        if account_long_press_index is not None and account_long_press_timer < 60:  # Moins de 1 seconde (60 frames à 60 FPS)
                            # Clic normal : sélectionner le compte
                            current_account_index = account_long_press_index
                            account = accounts[account_long_press_index]
                            player_name = account.get('player_name', '')
                            selected_avatar = account.get('selected_avatar')
                            selected_font = account.get('selected_font')
                            # Charger les données de jeu de ce compte
                            pouvoir_items, gadget_items, objet_items, capacite_items, inventaire_items_loaded, jeton_poche, crown_poche, bon_marche_ameliore, battle_pass_xp, battle_pass_claimed_rewards, gemme_poche, used_stars, battle_pass_plus_claimed_rewards, used_stars_plus, pass_plus_purchased = load_game_data_for_account(current_account_index)
                            # Lancer le jeu
                            current_state = MENU
                        # Réinitialiser le timer
                        account_long_press_index = None
                        account_long_press_timer = 0
                    elif current_state == AVENTURE_MENU:
                        aventure_retour_button = pygame.Rect(10, 10, 100, 40)
                        aventure_carte1_button = pygame.Rect(WINDOW_WIDTH//2 - 125, WINDOW_HEIGHT//2 - 30, 250, 60)
                        if aventure_retour_button.collidepoint(mouse_pos):
                            current_state = MENU
                        elif aventure_carte1_button.collidepoint(mouse_pos):
                            # Démarrer l'aventure : carte 1 avec 3 vies, 0 couronnes, 0 pacoins
                            # Réinitialiser les valeurs pour l'aventure
                            jeton_poche = 0
                            crown_poche = 0
                            # Démarrer le jeu avec la carte 1 (niveau 1)
                            maze, pacman, ghosts = start_next_level(1, is_adventure_mode=True)
                            # Ajouter 4 pacgommes aux mêmes positions que dans le jeu normal
                            # Les pacgommes sont généralement aux 4 coins du labyrinthe
                            # Positions standard : (1,1), (19,1), (1,19), (19,19)
                            # Mais on vérifie d'abord si ces positions sont valides (pas des murs)
                            corner_positions = [
                                (1, 1),   # Coin haut-gauche
                                (GRID_WIDTH - 2, 1),  # Coin haut-droite (19, 1)
                                (1, GRID_HEIGHT - 2),  # Coin bas-gauche (1, 19)
                                (GRID_WIDTH - 2, GRID_HEIGHT - 2)  # Coin bas-droite (19, 19)
                            ]
                            
                            # Placer les pacgommes aux positions des coins si elles sont valides
                            for x, y in corner_positions:
                                if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                                    if maze[y][x] != 1:  # Si ce n'est pas un mur
                                        maze[y][x] = 3  # Placer une pacgomme
                                    else:
                                        # Si c'est un mur, chercher la case valide la plus proche
                                        found = False
                                        for dy in range(-2, 3):
                                            for dx in range(-2, 3):
                                                new_x = x + dx
                                                new_y = y + dy
                                                if 0 <= new_x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                                                    if maze[new_y][new_x] != 1 and maze[new_y][new_x] != 3:
                                                        maze[new_y][new_x] = 3
                                                        found = True
                                                        break
                                            if found:
                                                break
                            # Initialiser les variables du jeu
                            score = 0
                            last_bonus_score = 0
                            game_over = False
                            won = False
                            ice_tiles = {}
                            pacgomme_timers = {}  # Réinitialiser les timers de pacgommes pour l'aventure
                            ghost_timers = {}  # Réinitialiser les timers de fantômes pour l'aventure
                            pacman_last_pos = (pacman.x, pacman.y)
                            vulnerable_timer = 0
                            level_transition = False
                            level_transition_timer = 0
                            respawn_timer = 0
                            lives = 3  # 3 vies pour l'aventure
                            invincibility_timer = 30
                            crown_timer = 0
                            level = 1
                            invincibilite_bonus = 0
                            has_indigestion = False
                            indigestion_timer = 0
                            gadget_cooldown = 0
                            gadget_use_count = 0
                            portal_use_count = 0
                            portal1_pos = None
                            portal2_pos = None
                            vulnerable_ghosts_eaten_this_game = 0
                            crown_count = 0
                            jeton_count = 0
                            last_ghost_time = 0
                            fire_tiles = {}
                            fire_active = False
                            fire_timer = 0
                            mort_cooldown = 0
                            bombe_cooldown = 0
                            bombe_active = False
                            pieges = {}
                            mur_pos = None
                            mur_use_count = 0
                            rainbow_timer = 0
                            is_rainbow_critique = False
                            game_initialized = True
                            is_adventure_mode = True  # Activer le mode aventure
                            # Passer à l'état GAME
                            current_state = GAME
                    elif current_state == SKILL_TREE_MENU:
                        # Utiliser les boutons retournés par draw_skill_tree_menu
                        if skill_tree_retour_button.collidepoint(mouse_pos):
                            current_state = MENU
                        elif skill_tree_survie_button.collidepoint(mouse_pos):
                            current_state = SURVIE_SKILL_TREE_MENU
                        elif skill_tree_equipement_button.collidepoint(mouse_pos):
                            current_state = EQUIPEMENT_SKILL_TREE_MENU
                    elif current_state == SURVIE_SKILL_TREE_MENU:
                        if survie_skill_tree_retour_button.collidepoint(mouse_pos):
                            current_state = SKILL_TREE_MENU
                    elif current_state == EQUIPEMENT_SKILL_TREE_MENU:
                        if equipement_skill_tree_retour_button.collidepoint(mouse_pos):
                            current_state = SKILL_TREE_MENU
                    elif current_state == CUSTOMIZATION_MENU:
                        # Calculer les positions des boutons (même logique que dans draw_customization_menu)
                        button_width = 200
                        button_height = 60
                        button_spacing = 80
                        start_y = WINDOW_HEIGHT//2 - button_height
                        font_button_rect = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, start_y, button_width, button_height)
                        avatar_button_rect = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, start_y + button_spacing, button_width, button_height)
                        nom_button_rect = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, start_y + button_spacing * 2, button_width, button_height)
                        retour_button = pygame.Rect(10, 10, 100, 40)
                        
                        # Bouton "Créer le compte" - apparaît seulement si tout est choisi
                        creer_compte_button = None
                        if player_name and selected_avatar and selected_font:
                            creer_compte_button = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, start_y + button_spacing * 3, button_width, button_height)
                        
                        # Calculer le rectangle du cercle avatar si un nom est défini
                        avatar_circle_rect = None
                        if player_name:
                            profile_y = 200
                            profile_x = 50
                            circle_radius = 50
                            circle_x = profile_x + circle_radius
                            circle_y = profile_y + circle_radius
                            avatar_circle_rect = pygame.Rect(circle_x - circle_radius, circle_y - circle_radius, circle_radius * 2, circle_radius * 2)
                        
                        if retour_button.collidepoint(mouse_pos):
                            current_state = START_MENU
                        elif avatar_circle_rect and avatar_circle_rect.collidepoint(mouse_pos):
                            # Ouvrir le menu avatar en cliquant sur le cercle
                            current_state = AVATAR_MENU
                        elif creer_compte_button and creer_compte_button.collidepoint(mouse_pos):
                            # Créer le compte et l'ajouter à la liste
                            new_account = {
                                'player_name': player_name,
                                'selected_avatar': selected_avatar,
                                'selected_font': selected_font,
                                'trophies': [],
                                'game_data': {
                                    'pouvoir_items': [],
                                    'gadget_items': [],
                                    'objet_items': [],
                                    'capacite_items': [],
                                    'inventaire_items': {},
                                    'jeton_poche': 0,
                                    'crown_poche': 0,
                                    'bon_marche_ameliore': False
                                }
                            }
                            accounts.append(new_account)
                            current_account_index = len(accounts) - 1
                            # Charger les données de jeu du nouveau compte
                            pouvoir_items, gadget_items, objet_items, capacite_items, inventaire_items_loaded, jeton_poche, crown_poche, bon_marche_ameliore, battle_pass_xp, battle_pass_claimed_rewards, gemme_poche, used_stars, battle_pass_plus_claimed_rewards, used_stars_plus, pass_plus_purchased = load_game_data_for_account(current_account_index)
                            # Sauvegarder les comptes
                            save_accounts_data(accounts)
                            # Réinitialiser pour un nouveau compte si nécessaire
                            creating_new_account = False
                            player_name = ""
                            selected_avatar = None
                            selected_font = None
                            pending_font = None
                            pending_avatar = None
                            current_state = START_MENU
                        elif font_button_rect.collidepoint(mouse_pos):
                            current_state = FONT_MENU
                        elif avatar_button_rect.collidepoint(mouse_pos):
                            current_state = AVATAR_MENU
                        elif nom_button_rect.collidepoint(mouse_pos):
                            current_state = NAME_MENU
                            name_input_active = True
                    elif current_state == NAME_MENU:
                        name_retour_button = pygame.Rect(10, 10, 100, 40)
                        input_width = 400
                        input_height = 50
                        input_x = (WINDOW_WIDTH - input_width) // 2
                        input_y = WINDOW_HEIGHT // 2 - 50
                        name_input_rect = pygame.Rect(input_x, input_y, input_width, input_height)
                        
                        if name_retour_button.collidepoint(mouse_pos):
                            current_state = CUSTOMIZATION_MENU
                            name_input_active = False
                        elif name_input_rect.collidepoint(mouse_pos):
                            name_input_active = True
                        else:
                            name_input_active = False
                    elif current_state == FONT_MENU:
                        font_retour_button = pygame.Rect(10, 10, 100, 40)
                        font_files = get_available_font_images()
                        font_rects = build_font_option_rects(font_files)
                        
                        if font_retour_button.collidepoint(mouse_pos):
                            current_state = CUSTOMIZATION_MENU
                            pending_font = None  # Réinitialiser la sélection temporaire
                        elif font_valider_button is not None and font_valider_button.collidepoint(mouse_pos):
                            # Valider la sélection temporaire
                            if pending_font is not None:
                                selected_font = pending_font
                            current_state = CUSTOMIZATION_MENU
                            pending_font = None
                        else:
                            for rect, font_file in font_rects:
                                if rect.collidepoint(mouse_pos):
                                    pending_font = font_file
                                    break
                    elif current_state == AVATAR_MENU:
                        avatar_retour_button = pygame.Rect(10, 10, 100, 40)
                        # Calculer les positions des images (même logique que dans draw_avatar_menu)
                        small_size = 80
                        img_y = 120
                        spacing = 90
                        avatar_image1 = None
                        avatar_image2 = None
                        avatar_image3 = None
                        avatar_image4 = None
                        avatar_paths1 = ["fatome_epee.png", "avatar.png", "image-t26edcoUjiXQ72uQKAB3R(2).png", "avatar.jpg", "avatar.jpeg"]
                        # Utiliser le deuxième font comme avatar2
                        second_font = get_second_font()
                        avatar_paths2 = [second_font] if second_font else []
                        avatar_paths3 = ["image-1uA5ykn6ZPDhIyRHwCxym.webp"]
                        avatar_paths4 = ["le_super_67.webp"]
                        
                        for path in avatar_paths1:
                            if os.path.exists(path):
                                try:
                                    avatar_image1 = pygame.image.load(path)
                                    break
                                except:
                                    continue
                        for path in avatar_paths2:
                            if os.path.exists(path):
                                try:
                                    avatar_image2 = pygame.image.load(path)
                                    break
                                except:
                                    continue
                        for path in avatar_paths3:
                            if os.path.exists(path):
                                try:
                                    avatar_image3 = pygame.image.load(path)
                                    break
                                except:
                                    continue
                        for path in avatar_paths4:
                            if os.path.exists(path):
                                try:
                                    avatar_image4 = pygame.image.load(path)
                                    break
                                except:
                                    continue
                        
                        image_count = sum([1 for img in [avatar_image1, avatar_image2, avatar_image3, avatar_image4] if img is not None])
                        if image_count > 0:
                            total_width = (image_count * small_size) + ((image_count - 1) * (spacing - small_size))
                            start_x = (WINDOW_WIDTH - total_width) // 2
                        else:
                            start_x = 10
                        
                        # Calculer les rectangles de la même manière que dans draw_avatar_menu
                        avatar_rect1 = None
                        avatar_rect2 = None
                        avatar_rect3 = None
                        avatar_rect4 = None
                        current_x = start_x
                        
                        if avatar_image1:
                            avatar_rect1 = pygame.Rect(current_x, img_y, small_size, small_size)
                            current_x += spacing
                        if avatar_image2:
                            avatar_rect2 = pygame.Rect(current_x, img_y, small_size, small_size)
                            current_x += spacing
                        if avatar_image3:
                            avatar_rect3 = pygame.Rect(current_x, img_y, small_size, small_size)
                            current_x += spacing
                        if avatar_image4:
                            avatar_rect4 = pygame.Rect(current_x, img_y, small_size, small_size)
                        
                        if avatar_retour_button.collidepoint(mouse_pos):
                            current_state = CUSTOMIZATION_MENU
                            pending_avatar = None  # Réinitialiser la sélection temporaire
                        elif avatar_valider_button is not None and avatar_valider_button.collidepoint(mouse_pos):
                            # Valider la sélection temporaire
                            if pending_avatar is not None:
                                selected_avatar = pending_avatar
                                # Sauvegarder dans le compte si un compte est actuellement sélectionné
                                if current_account_index is not None and current_account_index < len(accounts):
                                    accounts[current_account_index]['selected_avatar'] = selected_avatar
                                    save_accounts_data(accounts)
                            current_state = CUSTOMIZATION_MENU
                            pending_avatar = None
                        elif avatar_rect1 and avatar_rect1.collidepoint(mouse_pos):
                            # Sélectionner temporairement le premier avatar
                            pending_avatar = "avatar1"
                        elif avatar_rect2 and avatar_rect2.collidepoint(mouse_pos):
                            # Sélectionner temporairement le deuxième avatar
                            pending_avatar = "avatar2"
                        elif avatar_rect3 and avatar_rect3.collidepoint(mouse_pos):
                            # Sélectionner temporairement le troisième avatar
                            pending_avatar = "avatar3"
                        elif avatar_rect4 and avatar_rect4.collidepoint(mouse_pos):
                            # Sélectionner temporairement le quatrième avatar
                            pending_avatar = "avatar4"
                    elif current_state == MENU:
                        # Si on est en mode confirmation, ignorer tous les autres clics
                        if delete_confirmation_step == 0:
                            # Calculer les positions des boutons (même logique que dans draw_menu)
                            changer_compte_button = pygame.Rect(WINDOW_WIDTH - 180, 10, 170, 35)
                            button_width = 140  # Réduit pour correspondre à draw_menu
                            button_height = 40  # Réduit pour correspondre à draw_menu
                            button_spacing = 42  # Réduit pour correspondre à draw_menu
                            start_y = 170  # Réduit pour correspondre à draw_menu
                            jeu_button = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, start_y, button_width, button_height)
                            magasin_button = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, start_y + button_spacing, button_width, button_height)
                            difficulte_button = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, start_y + button_spacing * 2, button_width, button_height)
                            poche_button = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, start_y + button_spacing * 3, button_width, button_height)
                            inventaire_button = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, start_y + button_spacing * 4, button_width, button_height)
                            vente_button = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, start_y + button_spacing * 5, button_width, button_height)
                            aventure_button = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, start_y + button_spacing * 6, button_width, button_height)
                            boutique_button = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, start_y + button_spacing * 7, button_width, button_height)
                            passe_combat_button = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, start_y + button_spacing * 8, button_width, button_height)
                            skill_tree_button = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, start_y + button_spacing * 9, button_width, button_height)
                            
                            # Vérifier le clic sur le bouton "Changer de compte"
                            if changer_compte_button.collidepoint(mouse_pos):
                                # Sauvegarder les données du compte actuel avant de quitter
                                if current_account_index is not None:
                                    save_game_data_for_account(current_account_index, pouvoir_items, gadget_items, objet_items, capacite_items, inventaire_items, jeton_poche, crown_poche, bon_marche_ameliore, battle_pass_xp, battle_pass_claimed_rewards, gemme_poche, used_stars, accounts, battle_pass_plus_claimed_rewards, used_stars_plus, pass_plus_purchased)
                                current_state = START_MENU
                            elif jeu_button.collidepoint(mouse_pos):
                                # Si on revient du menu après avoir cliqué sur retour, réinitialiser la partie
                                if game_needs_reset:
                                    # Réinitialiser la partie complètement
                                    maze = [row[:] for row in MAZES[0]]
                                    pacman = Pacman(10, 15)
                                    ghosts = [
                                        Ghost(10, 9, BLUE),
                                    ]
                                    # Définir le chemin pour tous les fantômes bleus
                                    for ghost in ghosts:
                                        if ghost.color == BLUE:
                                            ghost.set_path(maze)
                                    score = 0
                                    level = 1
                                    last_bonus_score = 0
                                    game_over = False
                                    won = False
                                    vulnerable_timer = 0
                                    ice_tiles = {}  # Réinitialiser les cases de glace
                                    fire_tiles = {}  # Réinitialiser les cases de feu
                                    fire_active = False
                                    fire_timer = 0
                                    gadget_cooldown = 0
                                    mort_cooldown = 0
                                    bombe_cooldown = 0
                                    bombe_active = False
                                    pieges = {}
                                    portal1_pos = None
                                    portal2_pos = None
                                    portal_use_count = 0
                                    mur_pos = None
                                    mur_use_count = 0
                                    gadget_use_count = 0
                                    invincibility_timer = 30 + invincibilite_bonus  # Réinitialiser le timer d'invincibilité
                                    level_transition = False
                                    level_transition_timer = 0
                                    respawn_timer = 0
                                    crown_count = 0  # Réinitialiser le compteur de couronnes temporaires
                                    jeton_count = 0  # Réinitialiser le compteur de jetons temporaires
                                    last_ghost_time = 0  # Réinitialiser le timer depuis le dernier fantôme mangé
                                    has_indigestion = False
                                    indigestion_timer = 0
                                    game_needs_reset = False
                                    # Ouvrir l'inventaire pour permettre de changer l'équipement avant de commencer
                                    current_state = INVENTAIRE
                                    inventaire_before_game = True  # Variable pour indiquer qu'on est dans l'inventaire avant de commencer la partie
                                else:
                                    # Initialiser le jeu pour la première fois
                                    if not game_initialized:
                                        # Initialiser le labyrinthe et les entités
                                        maze = [row[:] for row in MAZES[0]]
                                        pacman = Pacman(10, 15)
                                        ghosts = [
                                            Ghost(10, 9, BLUE),
                                        ]
                                        # Définir le chemin pour tous les fantômes bleus
                                        for ghost in ghosts:
                                            if ghost.color == BLUE:
                                                ghost.set_path(maze)
                                        score = 0
                                        level = 1
                                        last_bonus_score = 0
                                        game_over = False
                                        won = False
                                        vulnerable_timer = 0
                                        ice_tiles = {}
                                        fire_tiles = {}
                                        fire_active = False
                                        fire_timer = 0
                                        gadget_cooldown = 0
                                        mort_cooldown = 0
                                        bombe_cooldown = 0
                                        bombe_active = False
                                        pieges = {}
                                        portal1_pos = None
                                        portal2_pos = None
                                        portal_use_count = 0
                                        mur_pos = None
                                        mur_use_count = 0
                                        gadget_use_count = 0
                                        invincibility_timer = 30 + invincibilite_bonus
                                        level_transition = False
                                        level_transition_timer = 0
                                        respawn_timer = 0
                                        crown_count = 0
                                        jeton_count = 0
                                        last_ghost_time = 0
                                        has_indigestion = False
                                        indigestion_timer = 0
                                        game_initialized = True
                                    # Ouvrir l'inventaire pour permettre de changer l'équipement avant de commencer
                                    current_state = INVENTAIRE
                                    inventaire_before_game = True
                            elif magasin_button.collidepoint(mouse_pos):
                                current_state = SHOP
                            elif difficulte_button.collidepoint(mouse_pos):
                                current_state = DIFFICULTY
                            elif poche_button.collidepoint(mouse_pos):
                                current_state = POCHE
                            elif inventaire_button.collidepoint(mouse_pos):
                                current_state = INVENTAIRE
                            elif vente_button.collidepoint(mouse_pos):
                                current_state = VENTE
                            elif aventure_button.collidepoint(mouse_pos):
                                current_state = AVENTURE_MENU
                            elif boutique_button.collidepoint(mouse_pos):
                                current_state = BOUTIQUE
                            elif passe_combat_button.collidepoint(mouse_pos):
                                current_state = PASSE_MENU
                            elif skill_tree_button.collidepoint(mouse_pos):
                                current_state = SKILL_TREE_MENU
                            elif tutoriel_button.collidepoint(mouse_pos):
                                current_state = TUTORIAL_MENU
                                tutorial_page = 0
                    elif current_state == TUTORIAL_MENU:
                        # Calculer les boutons pour la détection de collision (en haut)
                        tutorial_prev_button = None
                        tutorial_next_button = None
                        if tutorial_page > 0:
                            tutorial_prev_button = pygame.Rect(10, 10, 120, 40)
                        if tutorial_page < 5:
                            tutorial_next_button = pygame.Rect(WINDOW_WIDTH - 130, 10, 120, 40)
                        
                        if tutorial_prev_button is not None and tutorial_prev_button.collidepoint(mouse_pos):
                            if tutorial_page > 0:
                                tutorial_page -= 1
                        elif tutorial_next_button is not None and tutorial_next_button.collidepoint(mouse_pos):
                            if tutorial_page < 5:
                                tutorial_page += 1
                    elif current_state == PASSE_MENU:
                        passe_retour_button = pygame.Rect(10, 10, 100, 40)
                        if passe_retour_button.collidepoint(mouse_pos):
                            current_state = MENU
                        elif passe_arrow_button.collidepoint(mouse_pos):
                            current_state = PASSE_PLUS_MENU
                        else:
                            # Vérifier si on clique sur une récompense
                            REWARD_LEVELS_PACOINS = {1: 300, 5: 300, 7: 300, 9: 300, 11: 300, 15: 300, 18: 300, 22: 300, 25: 300, 28: 1000, 29: 300}
                            REWARD_LEVELS_CROWNS = {2: 5, 6: 5, 13: 5, 20: 5, 27: 5}
                            REWARD_LEVELS_GEMS = {3: 10, 12: 10, 17: 10, 21: 10, 26: 10}
                            XP_PER_LEVEL = 100
                            # S'assurer que battle_pass_xp est un entier
                            if not isinstance(battle_pass_xp, (int, float)):
                                battle_pass_xp = 0
                            battle_pass_level = (int(battle_pass_xp) // XP_PER_LEVEL) + 1
                            # Niveaux avec étoiles
                            STAR_LEVELS = [4, 8, 10, 14, 16, 19, 23, 24, 30]
                            
                            for reward_type, reward_rect, reward_level in passe_reward_rects:
                                if reward_rect.collidepoint(mouse_pos):
                                    # Si c'est une étoile (seulement si le niveau est atteint et non utilisée), ouvrir le menu d'amélioration
                                    if reward_type == "star":
                                        # Vérifier que le niveau est atteint (acheté) et que l'étoile n'a pas déjà été utilisée
                                        if reward_level <= battle_pass_level and reward_level not in used_stars:
                                            # Ouvrir le menu d'amélioration d'étoile
                                            current_state = STAR_UPGRADE_MENU
                                            # Initialiser l'étoile : légendaire pour le niveau 30, rare pour les autres
                                            if reward_level == 30:
                                                star_rarity = "legendaire"
                                            else:
                                                star_rarity = "rare"
                                            star_clicks_remaining = 5
                                            # Activer un doubleur d'XP si disponible
                                            if xp_doublers_count > 0:
                                                xp_doubler_active = True
                                                xp_doublers_count -= 1
                                            else:
                                                xp_doubler_active = False
                                            current_star_level = reward_level  # Sauvegarder le niveau de l'étoile actuelle
                                            is_plus_star = False  # Étoile du pass normal
                                        break
                                    # Si c'est une case avec étoile mais le niveau n'est pas atteint, ne rien faire
                                    elif reward_type == "reward" and reward_level in STAR_LEVELS:
                                        # Vérifier que le niveau est atteint et que l'étoile n'a pas déjà été utilisée
                                        if reward_level <= battle_pass_level and reward_level not in used_stars:
                                            current_state = STAR_UPGRADE_MENU
                                            # Initialiser l'étoile : légendaire pour le niveau 30, rare pour les autres
                                            if reward_level == 30:
                                                star_rarity = "legendaire"
                                            else:
                                                star_rarity = "rare"
                                            star_clicks_remaining = 5
                                            current_star_level = reward_level  # Sauvegarder le niveau de l'étoile actuelle
                                            is_plus_star = False  # Étoile du pass normal
                                        break
                                    # Vérifier si le niveau est atteint et si la récompense n'a pas été récupérée
                                    reward_claimed = False
                                    if reward_level <= battle_pass_level:
                                        if reward_level in REWARD_LEVELS_PACOINS:
                                            # Vérifier si la récompense n'a pas déjà été récupérée
                                            if reward_level not in battle_pass_claimed_rewards:
                                                # Ajouter les pacoins selon le niveau
                                                reward_amount = REWARD_LEVELS_PACOINS[reward_level]
                                                jeton_poche += reward_amount
                                                # Marquer la récompense comme récupérée
                                                battle_pass_claimed_rewards.append(reward_level)
                                                reward_claimed = True
                                                # Ajouter une animation de récompense
                                                reward_animations.append({
                                                    'text': f"+{reward_amount} pacoins",
                                                    'x': WINDOW_WIDTH // 2,
                                                    'y': WINDOW_HEIGHT // 2,
                                                    'color': (255, 215, 0),  # Or
                                                    'timer': 0
                                                })
                                        elif reward_level in REWARD_LEVELS_CROWNS:
                                            # Vérifier si la récompense n'a pas déjà été récupérée
                                            if reward_level not in battle_pass_claimed_rewards:
                                                # Ajouter les couronnes selon le niveau
                                                reward_amount = REWARD_LEVELS_CROWNS[reward_level]
                                                crown_poche += reward_amount
                                                # Marquer la récompense comme récupérée
                                                battle_pass_claimed_rewards.append(reward_level)
                                                reward_claimed = True
                                                # Ajouter une animation de récompense
                                                reward_animations.append({
                                                    'text': f"+{reward_amount} couronnes",
                                                    'x': WINDOW_WIDTH // 2,
                                                    'y': WINDOW_HEIGHT // 2,
                                                    'color': (255, 215, 0),  # Or
                                                    'timer': 0
                                                })
                                        elif reward_level in REWARD_LEVELS_GEMS:
                                            # Vérifier si la récompense n'a pas déjà été récupérée
                                            if reward_level not in battle_pass_claimed_rewards:
                                                # Ajouter les gemmes selon le niveau
                                                reward_amount = REWARD_LEVELS_GEMS[reward_level]
                                                gemme_poche += reward_amount
                                                # Marquer la récompense comme récupérée
                                                battle_pass_claimed_rewards.append(reward_level)
                                                reward_claimed = True
                                                # Ajouter une animation de récompense
                                                reward_animations.append({
                                                    'text': f"+{reward_amount} gemmes",
                                                    'x': WINDOW_WIDTH // 2,
                                                    'y': WINDOW_HEIGHT // 2,
                                                    'color': (0, 255, 255),  # Cyan
                                                    'timer': 0
                                                })
                                    
                                    if reward_claimed:
                                        # Sauvegarder
                                        if current_account_index is not None:
                                            auto_save_account_data(current_account_index, pouvoir_items, gadget_items, objet_items, capacite_items, inventaire_items, jeton_poche, crown_poche, bon_marche_ameliore, battle_pass_xp, battle_pass_claimed_rewards, gemme_poche, used_stars, accounts, battle_pass_plus_claimed_rewards, used_stars_plus, pass_plus_purchased)
                                    break
                    elif current_state == PASSE_PLUS_MENU:
                        passe_plus_retour_button = pygame.Rect(10, 10, 100, 40)
                        passe_plus_arrow_left_button = pygame.Rect(10, WINDOW_HEIGHT // 2 - 50 + 100, 100, 100)
                        PASS_PLUS_PRICE = 100  # Prix du pass + en gemmes
                        if passe_plus_retour_button.collidepoint(mouse_pos):
                            current_state = MENU
                        elif passe_plus_arrow_left_button.collidepoint(mouse_pos):
                            current_state = PASSE_MENU
                        elif passe_plus_buy_button is not None and passe_plus_buy_button.collidepoint(mouse_pos):
                            # Acheter le pass +
                            if gemme_poche >= PASS_PLUS_PRICE:
                                gemme_poche -= PASS_PLUS_PRICE
                                pass_plus_purchased = True
                                # Sauvegarder
                                if current_account_index is not None:
                                    auto_save_account_data(current_account_index, pouvoir_items, gadget_items, objet_items, capacite_items, inventaire_items, jeton_poche, crown_poche, bon_marche_ameliore, battle_pass_xp, battle_pass_claimed_rewards, gemme_poche, used_stars, accounts, battle_pass_plus_claimed_rewards, used_stars_plus, pass_plus_purchased)
                                # Ajouter une animation de confirmation
                                reward_animations.append({
                                    'text': "Pass + acheté !",
                                    'x': WINDOW_WIDTH // 2,
                                    'y': WINDOW_HEIGHT // 2,
                                    'color': (255, 215, 0),  # Or
                                    'timer': 0
                                })
                        elif passe_plus_gain_xp_button is not None and passe_plus_gain_xp_button.collidepoint(mouse_pos):
                            # Gagner 100 XP
                            # S'assurer que battle_pass_xp est un entier
                            if not isinstance(battle_pass_xp, (int, float)):
                                battle_pass_xp = 0
                            # Calculer le nouveau XP
                            new_xp = int(battle_pass_xp) + 100
                            # Limiter l'XP au niveau 30 si toutes les récompenses ne sont pas récupérées
                            MAX_BATTLE_PASS_LEVEL = 30
                            XP_PER_LEVEL = 100
                            MAX_BATTLE_PASS_XP = MAX_BATTLE_PASS_LEVEL * XP_PER_LEVEL
                            if new_xp >= MAX_BATTLE_PASS_XP:
                                # Vérifier si toutes les récompenses ont été récupérées (pass +)
                                if not all_battle_pass_rewards_claimed(battle_pass_plus_claimed_rewards, used_stars_plus, MAX_BATTLE_PASS_LEVEL):
                                    # Bloquer l'XP au maximum du niveau 30
                                    new_xp = MAX_BATTLE_PASS_XP
                            battle_pass_xp = new_xp
                            # Sauvegarder l'XP gagné
                            if current_account_index is not None:
                                auto_save_account_data(current_account_index, pouvoir_items, gadget_items, objet_items, capacite_items, inventaire_items, jeton_poche, crown_poche, bon_marche_ameliore, battle_pass_xp, battle_pass_claimed_rewards, gemme_poche, used_stars, accounts, battle_pass_plus_claimed_rewards, used_stars_plus)
                        else:
                            # Vérifier si on clique sur une récompense
                            REWARD_LEVELS_PACOINS = {1: 300, 5: 300, 7: 300, 9: 300, 11: 300, 15: 300, 18: 300, 22: 300, 25: 300, 28: 1000, 29: 300}
                            REWARD_LEVELS_CROWNS = {2: 5, 6: 5, 13: 5, 20: 5, 27: 5}
                            REWARD_LEVELS_GEMS = {3: 10, 12: 10, 17: 10, 21: 10, 26: 10}
                            XP_PER_LEVEL = 100
                            # S'assurer que battle_pass_xp est un entier
                            if not isinstance(battle_pass_xp, (int, float)):
                                battle_pass_xp = 0
                            battle_pass_level = (int(battle_pass_xp) // XP_PER_LEVEL) + 1
                            # Niveaux avec étoiles
                            STAR_LEVELS = [4, 8, 10, 14, 16, 19, 23, 24, 30]
                            
                            for reward_type, reward_rect, reward_level in passe_plus_reward_rects:
                                if reward_rect.collidepoint(mouse_pos):
                                    # Si c'est une étoile (seulement si le niveau est atteint et non utilisée), ouvrir le menu d'amélioration
                                    # Ne peut ouvrir que si le pass + est acheté
                                    if not pass_plus_purchased:
                                        # Pass + non acheté, ne peut pas utiliser les étoiles
                                        break
                                    if reward_type == "star":
                                        # Vérifier que le niveau est atteint (acheté) et que l'étoile n'a pas déjà été utilisée (pass +)
                                        if reward_level <= battle_pass_level and reward_level not in used_stars_plus:
                                            # Ouvrir le menu d'amélioration d'étoile
                                            current_state = STAR_UPGRADE_MENU
                                            # Initialiser l'étoile : légendaire pour le niveau 30, rare pour les autres
                                            if reward_level == 30:
                                                star_rarity = "legendaire"
                                            else:
                                                star_rarity = "rare"
                                            star_clicks_remaining = 5
                                            # Activer un doubleur d'XP si disponible
                                            if xp_doublers_count > 0:
                                                xp_doubler_active = True
                                                xp_doublers_count -= 1
                                            else:
                                                xp_doubler_active = False
                                            current_star_level = reward_level  # Sauvegarder le niveau de l'étoile actuelle
                                            is_plus_star = True  # Marquer que c'est une étoile du pass +
                                        break
                                    # Si c'est une case avec étoile mais le niveau n'est pas atteint, ne rien faire
                                    elif reward_type == "reward" and reward_level in STAR_LEVELS:
                                        # Vérifier que le niveau est atteint et que l'étoile n'a pas déjà été utilisée (pass +)
                                        if reward_level <= battle_pass_level and reward_level not in used_stars_plus:
                                            current_state = STAR_UPGRADE_MENU
                                            # Initialiser l'étoile : légendaire pour le niveau 30, rare pour les autres
                                            if reward_level == 30:
                                                star_rarity = "legendaire"
                                            else:
                                                star_rarity = "rare"
                                            star_clicks_remaining = 5
                                            current_star_level = reward_level  # Sauvegarder le niveau de l'étoile actuelle
                                            is_plus_star = True  # Marquer que c'est une étoile du pass +
                                        break
                                    # Vérifier si le niveau est atteint et si la récompense n'a pas été récupérée (pass +)
                                    # Ne peut récupérer que si le pass + est acheté
                                    reward_claimed = False
                                    if not pass_plus_purchased:
                                        # Pass + non acheté, ne peut pas récupérer les récompenses
                                        break
                                    if reward_level <= battle_pass_level:
                                        if reward_level in REWARD_LEVELS_PACOINS:
                                            # Vérifier si la récompense n'a pas déjà été récupérée (pass +)
                                            if reward_level not in battle_pass_plus_claimed_rewards:
                                                # Ajouter les pacoins selon le niveau
                                                reward_amount = REWARD_LEVELS_PACOINS[reward_level]
                                                jeton_poche += reward_amount
                                                # Marquer la récompense comme récupérée (pass +)
                                                battle_pass_plus_claimed_rewards.append(reward_level)
                                                reward_claimed = True
                                                # Ajouter une animation de récompense
                                                reward_animations.append({
                                                    'text': f"+{reward_amount} pacoins",
                                                    'x': WINDOW_WIDTH // 2,
                                                    'y': WINDOW_HEIGHT // 2,
                                                    'color': (255, 215, 0),  # Or
                                                    'timer': 0
                                                })
                                        elif reward_level in REWARD_LEVELS_CROWNS:
                                            # Vérifier si la récompense n'a pas déjà été récupérée (pass +)
                                            if reward_level not in battle_pass_plus_claimed_rewards:
                                                # Ajouter les couronnes selon le niveau
                                                reward_amount = REWARD_LEVELS_CROWNS[reward_level]
                                                crown_poche += reward_amount
                                                # Marquer la récompense comme récupérée (pass +)
                                                battle_pass_plus_claimed_rewards.append(reward_level)
                                                reward_claimed = True
                                                # Ajouter une animation de récompense
                                                reward_animations.append({
                                                    'text': f"+{reward_amount} couronnes",
                                                    'x': WINDOW_WIDTH // 2,
                                                    'y': WINDOW_HEIGHT // 2,
                                                    'color': (255, 215, 0),  # Or
                                                    'timer': 0
                                                })
                                        elif reward_level in REWARD_LEVELS_GEMS:
                                            # Vérifier si la récompense n'a pas déjà été récupérée (pass +)
                                            if reward_level not in battle_pass_plus_claimed_rewards:
                                                # Ajouter les gemmes selon le niveau
                                                reward_amount = REWARD_LEVELS_GEMS[reward_level]
                                                gemme_poche += reward_amount
                                                # Marquer la récompense comme récupérée (pass +)
                                                battle_pass_plus_claimed_rewards.append(reward_level)
                                                reward_claimed = True
                                                # Ajouter une animation de récompense
                                                reward_animations.append({
                                                    'text': f"+{reward_amount} gemmes",
                                                    'x': WINDOW_WIDTH // 2,
                                                    'y': WINDOW_HEIGHT // 2,
                                                    'color': (0, 255, 255),  # Cyan
                                                    'timer': 0
                                                })
                                    
                                    if reward_claimed:
                                        # Vérifier si toutes les récompenses du pass + ont été récupérées
                                        MAX_BATTLE_PASS_LEVEL = 30
                                        all_rewards_claimed_plus = all_battle_pass_rewards_claimed(battle_pass_plus_claimed_rewards, used_stars_plus, MAX_BATTLE_PASS_LEVEL)
                                        
                                        # Si toutes les récompenses sont récupérées, perdre le pass + et réinitialiser
                                        if all_rewards_claimed_plus:
                                            battle_pass_plus_claimed_rewards = []
                                            used_stars_plus = []
                                            pass_plus_purchased = False
                                            # Ajouter une animation pour informer qu'il faut racheter le pass +
                                            reward_animations.append({
                                                'text': "Toutes les récompenses récupérées ! Achetez le pass + pour continuer",
                                                'x': WINDOW_WIDTH // 2,
                                                'y': WINDOW_HEIGHT // 2,
                                                'color': (255, 215, 0),  # Or
                                                'timer': 0
                                            })
                                        
                                        # Sauvegarder
                                        if current_account_index is not None:
                                            auto_save_account_data(current_account_index, pouvoir_items, gadget_items, objet_items, capacite_items, inventaire_items, jeton_poche, crown_poche, bon_marche_ameliore, battle_pass_xp, battle_pass_claimed_rewards, gemme_poche, used_stars, accounts, battle_pass_plus_claimed_rewards, used_stars_plus, pass_plus_purchased)
                                    break
                    elif current_state == STAR_UPGRADE_MENU:
                        if star_retour_button.collidepoint(mouse_pos):
                            current_state = PASSE_MENU
                        elif star_clickable_rect.collidepoint(mouse_pos) and star_clicks_remaining > 0:
                            # Clic sur l'étoile
                            
                            # Si c'est le 5ème clic (quand il reste 1 clic, donc après 4 clics), ouvrir l'étoile et donner une récompense
                            if star_clicks_remaining == 1:
                                # Ouvrir l'étoile et donner une récompense aléatoire selon la rareté
                                rand = random.random() * 100  # 0-100
                                
                                # Si l'étoile est épique (violette), utiliser les nouvelles probabilités
                                if star_rarity == "epique":
                                    # 40% de chance d'avoir 500 pacoins
                                    if rand < 40:
                                        jeton_poche += 500
                                        reward_message = "Vous avez gagné 500 pacoins !"
                                        reward_animations.append({
                                            'text': "+500 pacoins",
                                            'x': WINDOW_WIDTH // 2,
                                            'y': WINDOW_HEIGHT // 2,
                                            'color': (255, 215, 0),  # Or
                                            'timer': 0
                                        })
                                    # 40.9% de chance d'avoir 10 doubleurs d'XP
                                    elif rand < 80.9:  # 40 + 40.9
                                        xp_doublers_count += 10
                                        reward_message = "Vous avez gagné 10 doubleurs d'XP !"
                                        reward_animations.append({
                                            'text': "+10 Doubleurs d'XP",
                                            'x': WINDOW_WIDTH // 2,
                                            'y': WINDOW_HEIGHT // 2,
                                            'color': (0, 255, 0),  # Vert
                                            'timer': 0
                                        })
                                    # 19% de chance d'avoir 50 gemmes
                                    elif rand < 99.9:  # 40 + 40.9 + 19
                                        gemme_poche += 50
                                        reward_message = "Vous avez gagné 50 gemmes !"
                                        reward_animations.append({
                                            'text': "+50 gemmes",
                                            'x': WINDOW_WIDTH // 2,
                                            'y': WINDOW_HEIGHT // 2,
                                            'color': (0, 255, 255),  # Cyan
                                            'timer': 0
                                        })
                                    # 0.015% de chance d'avoir un item épique (violet)
                                    elif rand < 99.915:  # 99.9 + 0.015
                                        # Choisir aléatoirement un item épique parmi les catégories
                                        epic_items = {
                                            'pouvoir': ['glace', 'bon goût', 'bon repas'],
                                            'gadget': ['bombe téléguidée', 'explosion', 'vision x', 'feu', 'tp', 'pacgum', 'invincibilité', 'givre', 'double gadget'],
                                            'objet': ['coffre fort'],
                                            'capacite': ['pas d\'indigestion']
                                        }
                                        # Choisir une catégorie aléatoirement parmi celles qui ont des items
                                        categories = [cat for cat, items in epic_items.items() if items]
                                        if categories:
                                            chosen_category = random.choice(categories)
                                            chosen_item = random.choice(epic_items[chosen_category])
                                            
                                            if chosen_category == 'pouvoir':
                                                pouvoir_items.append(chosen_item)
                                            elif chosen_category == 'gadget':
                                                gadget_items.append(chosen_item)
                                            elif chosen_category == 'objet':
                                                objet_items.append(chosen_item)
                                            elif chosen_category == 'capacite':
                                                capacite_items.append(chosen_item)
                                            
                                            reward_message = f"Vous avez gagné {chosen_item} (Épique) !"
                                            reward_animations.append({
                                                'text': f"+{chosen_item} (Épique)",
                                                'x': WINDOW_WIDTH // 2,
                                                'y': WINDOW_HEIGHT // 2,
                                                'color': (148, 0, 211),  # Violet
                                                'timer': 0
                                            })
                                    # 0.085% de chance d'avoir un item super rare (bleu) (ajusté pour que le total fasse 100%)
                                    else:  # 99.915 à 100
                                        # Choisir aléatoirement un item super rare parmi les catégories
                                        super_rare_items = {
                                            'pouvoir': [],
                                            'gadget': ['portail', 'mur'],
                                            'objet': ['grosse armure', 'armure de fer'],
                                            'capacite': ['indigestion']
                                        }
                                        # Choisir une catégorie aléatoirement parmi celles qui ont des items
                                        categories = [cat for cat, items in super_rare_items.items() if items]
                                        if categories:
                                            chosen_category = random.choice(categories)
                                            chosen_item = random.choice(super_rare_items[chosen_category])
                                            
                                            if chosen_category == 'pouvoir':
                                                pouvoir_items.append(chosen_item)
                                            elif chosen_category == 'gadget':
                                                gadget_items.append(chosen_item)
                                            elif chosen_category == 'objet':
                                                objet_items.append(chosen_item)
                                            elif chosen_category == 'capacite':
                                                capacite_items.append(chosen_item)
                                            
                                            reward_message = f"Vous avez gagné {chosen_item} (Super Rare) !"
                                            reward_animations.append({
                                                'text': f"+{chosen_item} (Super Rare)",
                                                'x': WINDOW_WIDTH // 2,
                                                'y': WINDOW_HEIGHT // 2,
                                                'color': (0, 100, 255),  # Bleu
                                                'timer': 0
                                            })
                                # Si l'étoile est légendaire (jaune), utiliser les nouvelles probabilités
                                elif star_rarity == "legendaire":
                                    # 40% de chance d'avoir 30 gemmes
                                    if rand < 40:
                                        gemme_poche += 30
                                        reward_message = "Vous avez gagné 30 gemmes !"
                                        reward_animations.append({
                                            'text': "+30 gemmes",
                                            'x': WINDOW_WIDTH // 2,
                                            'y': WINDOW_HEIGHT // 2,
                                            'color': (0, 255, 255),  # Cyan
                                            'timer': 0
                                        })
                                    # 30% de chance d'avoir 1000 pacoins
                                    elif rand < 70:  # 40 + 30
                                        jeton_poche += 1000
                                        reward_message = "Vous avez gagné 1000 pacoins !"
                                        reward_animations.append({
                                            'text': "+1000 pacoins",
                                            'x': WINDOW_WIDTH // 2,
                                            'y': WINDOW_HEIGHT // 2,
                                            'color': (255, 215, 0),  # Or
                                            'timer': 0
                                        })
                                    # 29.9% de chance d'avoir 100 couronnes
                                    elif rand < 99.9:  # 40 + 30 + 29.9
                                        crown_poche += 100
                                        reward_message = "Vous avez gagné 100 couronnes !"
                                        reward_animations.append({
                                            'text': "+100 couronnes",
                                            'x': WINDOW_WIDTH // 2,
                                            'y': WINDOW_HEIGHT // 2,
                                            'color': (255, 215, 0),  # Or
                                            'timer': 0
                                        })
                                    # 0.075% de chance d'avoir un item épique (violet)
                                    elif rand < 99.975:  # 99.9 + 0.075
                                        # Choisir aléatoirement un item épique parmi les catégories
                                        epic_items = {
                                            'pouvoir': ['glace', 'bon goût', 'bon repas'],
                                            'gadget': ['bombe téléguidée', 'explosion', 'vision x', 'feu', 'tp', 'pacgum', 'invincibilité', 'givre', 'double gadget'],
                                            'objet': ['coffre fort'],
                                            'capacite': ['pas d\'indigestion']
                                        }
                                        # Choisir une catégorie aléatoirement parmi celles qui ont des items
                                        categories = [cat for cat, items in epic_items.items() if items]
                                        if categories:
                                            chosen_category = random.choice(categories)
                                            chosen_item = random.choice(epic_items[chosen_category])
                                            
                                            if chosen_category == 'pouvoir':
                                                pouvoir_items.append(chosen_item)
                                            elif chosen_category == 'gadget':
                                                gadget_items.append(chosen_item)
                                            elif chosen_category == 'objet':
                                                objet_items.append(chosen_item)
                                            elif chosen_category == 'capacite':
                                                capacite_items.append(chosen_item)
                                            
                                            reward_message = f"Vous avez gagné {chosen_item} (Épique) !"
                                            reward_animations.append({
                                                'text': f"+{chosen_item} (Épique)",
                                                'x': WINDOW_WIDTH // 2,
                                                'y': WINDOW_HEIGHT // 2,
                                                'color': (148, 0, 211),  # Violet
                                                'timer': 0
                                            })
                                    # 0.015% de chance d'avoir un item légendaire (jaune)
                                    else:  # 99.975 à 100
                                        # Choisir aléatoirement un item légendaire parmi les catégories
                                        legendary_items = {
                                            'pouvoir': ['skin bleu', 'skin orange', 'skin rose', 'skin rouge'],
                                            'gadget': [],
                                            'objet': ['coffre au trésor'],
                                            'capacite': []
                                        }
                                        # Choisir une catégorie aléatoirement parmi celles qui ont des items
                                        categories = [cat for cat, items in legendary_items.items() if items]
                                        if categories:
                                            chosen_category = random.choice(categories)
                                            chosen_item = random.choice(legendary_items[chosen_category])
                                            
                                            if chosen_category == 'pouvoir':
                                                pouvoir_items.append(chosen_item)
                                            elif chosen_category == 'gadget':
                                                gadget_items.append(chosen_item)
                                            elif chosen_category == 'objet':
                                                objet_items.append(chosen_item)
                                            elif chosen_category == 'capacite':
                                                capacite_items.append(chosen_item)
                                            
                                            reward_message = f"Vous avez gagné {chosen_item} (Légendaire) !"
                                            reward_animations.append({
                                                'text': f"+{chosen_item} (Légendaire)",
                                                'x': WINDOW_WIDTH // 2,
                                                'y': WINDOW_HEIGHT // 2,
                                                'color': (255, 215, 0),  # Jaune/Or
                                                'timer': 0
                                            })
                                # Si l'étoile est super rare (bleue), utiliser les nouvelles probabilités
                                elif star_rarity == "super_rare":
                                    # 40% de chance d'avoir 200 pacoins
                                    if rand < 40:
                                        jeton_poche += 200
                                        reward_message = "Vous avez gagné 200 pacoins !"
                                        reward_animations.append({
                                            'text': "+200 pacoins",
                                            'x': WINDOW_WIDTH // 2,
                                            'y': WINDOW_HEIGHT // 2,
                                            'color': (255, 215, 0),  # Or
                                            'timer': 0
                                        })
                                    # 40.9% de chance d'avoir 5 doubleurs d'XP
                                    elif rand < 80.9:  # 40 + 40.9
                                        xp_doublers_count += 5
                                        reward_message = "Vous avez gagné 5 doubleurs d'XP !"
                                        reward_animations.append({
                                            'text': "+5 Doubleurs d'XP",
                                            'x': WINDOW_WIDTH // 2,
                                            'y': WINDOW_HEIGHT // 2,
                                            'color': (0, 255, 0),  # Vert
                                            'timer': 0
                                        })
                                    # 19% de chance d'avoir 5 couronnes
                                    elif rand < 99.9:  # 40 + 40.9 + 19
                                        crown_poche += 5
                                        reward_message = "Vous avez gagné 5 couronnes !"
                                        reward_animations.append({
                                            'text': "+5 couronnes",
                                            'x': WINDOW_WIDTH // 2,
                                            'y': WINDOW_HEIGHT // 2,
                                            'color': (255, 215, 0),  # Or
                                            'timer': 0
                                        })
                                    # 0.075% de chance d'avoir un item rare (vert)
                                    elif rand < 99.975:  # 99.9 + 0.075
                                        # Choisir aléatoirement un item rare parmi les catégories
                                        rare_items = {
                                            'pouvoir': ['longue vue'],
                                            'gadget': ['tir', 'piège'],
                                            'objet': [],
                                            'capacite': ['bon marché', 'gel']
                                        }
                                        # Choisir une catégorie aléatoirement parmi celles qui ont des items
                                        categories = [cat for cat, items in rare_items.items() if items]
                                        if categories:
                                            chosen_category = random.choice(categories)
                                            chosen_item = random.choice(rare_items[chosen_category])
                                            
                                            if chosen_category == 'pouvoir':
                                                pouvoir_items.append(chosen_item)
                                            elif chosen_category == 'gadget':
                                                gadget_items.append(chosen_item)
                                            elif chosen_category == 'objet':
                                                objet_items.append(chosen_item)
                                            elif chosen_category == 'capacite':
                                                capacite_items.append(chosen_item)
                                            
                                            reward_message = f"Vous avez gagné {chosen_item} (Rare) !"
                                            reward_animations.append({
                                                'text': f"+{chosen_item} (Rare)",
                                                'x': WINDOW_WIDTH // 2,
                                                'y': WINDOW_HEIGHT // 2,
                                                'color': (0, 255, 0),  # Vert
                                                'timer': 0
                                            })
                                    # 0.015% de chance d'avoir un item super rare (bleu)
                                    else:  # 99.975 à 100
                                        # Choisir aléatoirement un item super rare parmi les catégories
                                        super_rare_items = {
                                            'pouvoir': [],
                                            'gadget': ['portail', 'mur'],
                                            'objet': ['grosse armure', 'armure de fer'],
                                            'capacite': ['indigestion']
                                        }
                                        # Choisir une catégorie aléatoirement parmi celles qui ont des items
                                        categories = [cat for cat, items in super_rare_items.items() if items]
                                        if categories:
                                            chosen_category = random.choice(categories)
                                            chosen_item = random.choice(super_rare_items[chosen_category])
                                            
                                            if chosen_category == 'pouvoir':
                                                pouvoir_items.append(chosen_item)
                                            elif chosen_category == 'gadget':
                                                gadget_items.append(chosen_item)
                                            elif chosen_category == 'objet':
                                                objet_items.append(chosen_item)
                                            elif chosen_category == 'capacite':
                                                capacite_items.append(chosen_item)
                                            
                                            reward_message = f"Vous avez gagné {chosen_item} (Super Rare) !"
                                            reward_animations.append({
                                                'text': f"+{chosen_item} (Super Rare)",
                                                'x': WINDOW_WIDTH // 2,
                                                'y': WINDOW_HEIGHT // 2,
                                                'color': (0, 100, 255),  # Bleu
                                                'timer': 0
                                            })
                                else:
                                    # Ancien système pour les étoiles non super rares
                                    if rand < 50:
                                        # 50% de chance d'avoir 100 pacoins
                                        jeton_poche += 100
                                        reward_message = "Vous avez gagné 100 pacoins !"
                                        # Ajouter une animation de récompense
                                        reward_animations.append({
                                            'text': "+100 pacoins",
                                            'x': WINDOW_WIDTH // 2,
                                            'y': WINDOW_HEIGHT // 2,
                                            'color': (255, 215, 0),  # Or
                                            'timer': 0
                                        })
                                    elif rand < 70:  # 50% + 20%
                                        # 20% de chance d'avoir 5 couronnes
                                        crown_poche += 5
                                        reward_message = "Vous avez gagné 5 couronnes !"
                                        # Ajouter une animation de récompense
                                        reward_animations.append({
                                            'text': "+5 couronnes",
                                            'x': WINDOW_WIDTH // 2,
                                            'y': WINDOW_HEIGHT // 2,
                                            'color': (255, 215, 0),  # Or
                                            'timer': 0
                                        })
                                    else:  # 30% restant
                                        # 30% de chance d'avoir 1 doubleur d'XP
                                        xp_doubler_active = True
                                        reward_message = "Vous avez gagné un doubleur d'XP pour la prochaine partie !"
                                        # Ajouter une animation de récompense
                                        reward_animations.append({
                                            'text': "+1 Doubleur d'XP",
                                            'x': WINDOW_WIDTH // 2,
                                            'y': WINDOW_HEIGHT // 2,
                                            'color': (0, 255, 0),  # Vert
                                            'timer': 0
                                        })
                                
                                # Marquer l'étoile comme utilisée (pass normal ou pass +)
                                if current_star_level is not None:
                                    if is_plus_star:
                                        # Étoile du pass +
                                        if current_star_level not in used_stars_plus:
                                            used_stars_plus.append(current_star_level)
                                        
                                        # Vérifier si toutes les récompenses du pass + ont été récupérées
                                        MAX_BATTLE_PASS_LEVEL = 30
                                        all_rewards_claimed_plus = all_battle_pass_rewards_claimed(battle_pass_plus_claimed_rewards, used_stars_plus, MAX_BATTLE_PASS_LEVEL)
                                        
                                        # Si toutes les récompenses sont récupérées, perdre le pass + et réinitialiser
                                        if all_rewards_claimed_plus:
                                            battle_pass_plus_claimed_rewards = []
                                            used_stars_plus = []
                                            pass_plus_purchased = False
                                            # Ajouter une animation pour informer qu'il faut racheter le pass +
                                            reward_animations.append({
                                                'text': "Toutes les récompenses récupérées ! Achetez le pass + pour continuer",
                                                'x': WINDOW_WIDTH // 2,
                                                'y': WINDOW_HEIGHT // 2,
                                                'color': (255, 215, 0),  # Or
                                                'timer': 0
                                            })
                                    else:
                                        # Étoile du pass normal
                                        if current_star_level not in used_stars:
                                            used_stars.append(current_star_level)
                                
                                # Sauvegarder
                                if current_account_index is not None:
                                    auto_save_account_data(current_account_index, pouvoir_items, gadget_items, objet_items, capacite_items, inventaire_items, jeton_poche, crown_poche, bon_marche_ameliore, battle_pass_xp, battle_pass_claimed_rewards, gemme_poche, used_stars, accounts, battle_pass_plus_claimed_rewards, used_stars_plus, pass_plus_purchased)
                                
                                # Réinitialiser l'étoile et fermer le menu
                                star_rarity = "rare"
                                star_clicks_remaining = 5
                                current_star_level = None
                                current_state = PASSE_MENU  # Retourner au menu du passe
                                
                                # Afficher un message (on pourrait ajouter un système de message ici)
                                print(reward_message)
                            else:
                                # Clics 1-4 : tenter d'améliorer la rareté
                                rand = random.random() * 100  # 0-100
                                
                                # Probabilités de montée en rareté
                                # L'étoile ne peut que monter, pas descendre
                                if star_rarity == "rare":
                                    # 10% super rare, 5% épique, 1% légendaire
                                    if rand < 1:
                                        star_rarity = "legendaire"
                                    elif rand < 6:  # 1% + 5%
                                        star_rarity = "epique"
                                    elif rand < 16:  # 1% + 5% + 10%
                                        star_rarity = "super_rare"
                                    # Sinon reste rare
                                elif star_rarity == "super_rare":
                                    # 5% épique, 1% légendaire
                                    if rand < 1:
                                        star_rarity = "legendaire"
                                    elif rand < 6:  # 1% + 5%
                                        star_rarity = "epique"
                                    # Sinon reste super rare
                                elif star_rarity == "epique":
                                    # 1% légendaire
                                    if rand < 1:
                                        star_rarity = "legendaire"
                                    # Sinon reste épique
                                # Légendaire reste légendaire
                            
                            star_clicks_remaining -= 1
                    elif current_state == SHOP:
                        # Les boutons sont retournés par draw_shop (appelé dans la partie dessin)
                        # Vérifier que les boutons sont définis avant de les utiliser
                        if shop_retour_button is not None and shop_retour_button.collidepoint(mouse_pos):
                            current_state = MENU
                        elif shop_gadget_button is not None and shop_gadget_button.collidepoint(mouse_pos):
                            # Bouton GADGET - aller à l'écran des items de gadget
                            current_state = SHOP_GADGET
                        elif shop_pouvoir_button is not None and shop_pouvoir_button.collidepoint(mouse_pos):
                            # Bouton POUVOIR - aller à l'écran des items de pouvoir
                            current_state = SHOP_POUVOIR
                        elif shop_objet_button is not None and shop_objet_button.collidepoint(mouse_pos):
                            # Bouton OBJET - aller à l'écran des items d'objet
                            current_state = SHOP_OBJET
                        elif shop_capacite_button is not None and shop_capacite_button.collidepoint(mouse_pos):
                            # Bouton CAPACITE - aller à l'écran des items de capacité
                            current_state = SHOP_CAPACITE
                    elif current_state == SHOP_GADGET:
                        # Les boutons sont retournés par draw_shop_gadget
                        if shop_gadget_retour_button is not None and shop_gadget_retour_button.collidepoint(mouse_pos):
                            current_state = SHOP
                            item_description = None  # Effacer la description quand on retourne
                        elif shop_explosion_button is not None and shop_explosion_button.collidepoint(mouse_pos):
                            # Acheter "Explosion" pour 10000 pacoins (réduit selon le niveau de "bon marché")
                            bon_marche_level = capacite_items.count("bon marché") if capacite_items else 0
                            price_reduction = bon_marche_level * 5
                            if bon_marche_ameliore and bon_marche_level > 0:
                                price_reduction *= 2
                            explosion_price = max(0, 10000 - price_reduction)
                            if "explosion" not in gadget_items and jeton_poche >= explosion_price:
                                gadget_items.append("explosion")
                                jeton_poche -= explosion_price
                                # Ajouter "explosion" dans le cadrillage (grille d'inventaire)
                                # Trouver le premier slot disponible dans la grille
                                grid_slot_found = False
                                for row in range(10):
                                    for col in range(4):
                                        slot_name = f'grid_{row}_{col}'
                                        if slot_name not in inventaire_items:
                                            inventaire_items[slot_name] = {'type': 'explosion', 'name': 'Explosion'}
                                            grid_slot_found = True
                                            break
                                    if grid_slot_found:
                                        break
                        elif shop_vision_x_button is not None and shop_vision_x_button.collidepoint(mouse_pos):
                            # Acheter "Vision X" pour 10000 pacoins (réduit si "bon marché" est équipé)
                            # Calculer la réduction selon le niveau de "bon marché"
                            bon_marche_level = capacite_items.count("bon marché") if capacite_items else 0
                            price_reduction = bon_marche_level * 5
                            if bon_marche_ameliore and bon_marche_level > 0:
                                price_reduction *= 2
                            vision_x_price = max(0, 10000 - price_reduction)
                            if "vision x" not in gadget_items and jeton_poche >= vision_x_price:
                                gadget_items.append("vision x")
                                jeton_poche -= vision_x_price
                                # Ajouter "vision x" dans le cadrillage (grille d'inventaire)
                                # Trouver le premier slot disponible dans la grille
                                grid_slot_found = False
                                for row in range(10):
                                    for col in range(4):
                                        slot_name = f'grid_{row}_{col}'
                                        if slot_name not in inventaire_items:
                                            inventaire_items[slot_name] = {'type': 'vision x', 'name': 'Vision X'}
                                            grid_slot_found = True
                                            break
                                    if grid_slot_found:
                                        break
                        elif shop_tir_button is not None and shop_tir_button.collidepoint(mouse_pos):
                            # Acheter "Tir" pour 1000 pacoins (réduit si "bon marché" est équipé)
                            # Calculer la réduction selon le niveau de "bon marché"
                            bon_marche_level = capacite_items.count("bon marché") if capacite_items else 0
                            price_reduction = bon_marche_level * 5
                            if bon_marche_ameliore and bon_marche_level > 0:
                                price_reduction *= 2
                            tir_price = max(0, 1000 - price_reduction)
                            if "tir" not in gadget_items and jeton_poche >= tir_price:
                                gadget_items.append("tir")
                                jeton_poche -= tir_price
                                # Ajouter "tir" dans le cadrillage (grille d'inventaire)
                                # Trouver le premier slot disponible dans la grille
                                grid_slot_found = False
                                for row in range(10):
                                    for col in range(4):
                                        slot_name = f'grid_{row}_{col}'
                                        if slot_name not in inventaire_items:
                                            inventaire_items[slot_name] = {'type': 'tir', 'name': 'Tir'}
                                            grid_slot_found = True
                                            break
                                    if grid_slot_found:
                                        break
                        elif shop_feu_button is not None and shop_feu_button.collidepoint(mouse_pos):
                            # Acheter "Feu" pour 5000 pacoins (réduit si "bon marché" est équipé)
                            # Calculer la réduction selon le niveau de "bon marché"
                            bon_marche_level = capacite_items.count("bon marché") if capacite_items else 0
                            price_reduction = bon_marche_level * 5
                            if bon_marche_ameliore and bon_marche_level > 0:
                                price_reduction *= 2
                            feu_price = max(0, 5000 - price_reduction)
                            if "feu" not in gadget_items and jeton_poche >= feu_price:
                                gadget_items.append("feu")
                                jeton_poche -= feu_price
                                # Ajouter "feu" dans le cadrillage (grille d'inventaire)
                                # Trouver le premier slot disponible dans la grille
                                grid_slot_found = False
                                for row in range(10):
                                    for col in range(4):
                                        slot_name = f'grid_{row}_{col}'
                                        if slot_name not in inventaire_items:
                                            inventaire_items[slot_name] = {'type': 'feu', 'name': 'Feu'}
                                            grid_slot_found = True
                                            break
                                    if grid_slot_found:
                                        break
                        elif shop_mort_button is not None and shop_mort_button.collidepoint(mouse_pos):
                            # Acheter "Mort" pour 15000 pacoins (réduit si "bon marché" est équipé)
                            # Calculer la réduction selon le niveau de "bon marché"
                            bon_marche_level = capacite_items.count("bon marché") if capacite_items else 0
                            price_reduction = bon_marche_level * 5
                            if bon_marche_ameliore and bon_marche_level > 0:
                                price_reduction *= 2
                            mort_price = max(0, 15000 - price_reduction)
                            if "mort" not in gadget_items and jeton_poche >= mort_price:
                                gadget_items.append("mort")
                                jeton_poche -= mort_price
                                # Ajouter "mort" dans le cadrillage (grille d'inventaire)
                                # Trouver le premier slot disponible dans la grille
                                grid_slot_found = False
                                for row in range(10):
                                    for col in range(4):
                                        slot_name = f'grid_{row}_{col}'
                                        if slot_name not in inventaire_items:
                                            inventaire_items[slot_name] = {'type': 'mort', 'name': 'Mort'}
                                            grid_slot_found = True
                                            break
                                    if grid_slot_found:
                                        break
                        elif shop_bombe_button is not None and shop_bombe_button.collidepoint(mouse_pos):
                            # Acheter "Bombe Téléguidée" pour 20000 pacoins (réduit si "bon marché" est équipé)
                            # Calculer la réduction selon le niveau de "bon marché"
                            bon_marche_level = capacite_items.count("bon marché") if capacite_items else 0
                            price_reduction = bon_marche_level * 5
                            if bon_marche_ameliore and bon_marche_level > 0:
                                price_reduction *= 2
                            bombe_price = max(0, 20000 - price_reduction)
                            if "bombe téléguidée" not in gadget_items and jeton_poche >= bombe_price:
                                gadget_items.append("bombe téléguidée")
                                jeton_poche -= bombe_price
                                # Ajouter "bombe téléguidée" dans le cadrillage (grille d'inventaire)
                                # Trouver le premier slot disponible dans la grille
                                grid_slot_found = False
                                for row in range(10):
                                    for col in range(4):
                                        slot_name = f'grid_{row}_{col}'
                                        if slot_name not in inventaire_items:
                                            inventaire_items[slot_name] = {'type': 'bombe téléguidée', 'name': 'Bombe Téléguidée'}
                                            grid_slot_found = True
                                            break
                                    if grid_slot_found:
                                        break
                        elif shop_piege_button is not None and shop_piege_button.collidepoint(mouse_pos):
                            # Acheter "Piège" pour 5000 pacoins (réduit si "bon marché" est équipé)
                            # Calculer la réduction selon le niveau de "bon marché"
                            bon_marche_level = capacite_items.count("bon marché") if capacite_items else 0
                            price_reduction = bon_marche_level * 5
                            if bon_marche_ameliore and bon_marche_level > 0:
                                price_reduction *= 2
                            piege_price = max(0, 5000 - price_reduction)
                            if "piège" not in gadget_items and jeton_poche >= piege_price:
                                gadget_items.append("piège")
                                jeton_poche -= piege_price
                                # Ajouter "piège" dans le cadrillage (grille d'inventaire)
                                # Trouver le premier slot disponible dans la grille
                                grid_slot_found = False
                                for row in range(10):
                                    for col in range(4):
                                        slot_name = f'grid_{row}_{col}'
                                        if slot_name not in inventaire_items:
                                            inventaire_items[slot_name] = {'type': 'piège', 'name': 'Piège'}
                                            grid_slot_found = True
                                            break
                                    if grid_slot_found:
                                        break
                        elif shop_tp_button is not None and shop_tp_button.collidepoint(mouse_pos):
                            # Acheter "TP" pour 3000 pacoins (réduit si "bon marché" est équipé)
                            # Calculer la réduction selon le niveau de "bon marché"
                            bon_marche_level = capacite_items.count("bon marché") if capacite_items else 0
                            price_reduction = bon_marche_level * 5
                            if bon_marche_ameliore and bon_marche_level > 0:
                                price_reduction *= 2
                            tp_price = max(0, 3000 - price_reduction)
                            if "tp" not in gadget_items and jeton_poche >= tp_price:
                                gadget_items.append("tp")
                                jeton_poche -= tp_price
                                # Ajouter "tp" dans le cadrillage (grille d'inventaire)
                                # Trouver le premier slot disponible dans la grille
                                grid_slot_found = False
                                for row in range(10):
                                    for col in range(4):
                                        slot_name = f'grid_{row}_{col}'
                                        if slot_name not in inventaire_items:
                                            inventaire_items[slot_name] = {'type': 'tp', 'name': 'TP'}
                                            grid_slot_found = True
                                            break
                                    if grid_slot_found:
                                        break
                        elif shop_portail_button is not None and shop_portail_button.collidepoint(mouse_pos):
                            # Acheter "Portail" pour 4000 pacoins (réduit si "bon marché" est équipé)
                            # Calculer la réduction selon le niveau de "bon marché"
                            bon_marche_level = capacite_items.count("bon marché") if capacite_items else 0
                            price_reduction = bon_marche_level * 5
                            if bon_marche_ameliore and bon_marche_level > 0:
                                price_reduction *= 2
                            portail_price = max(0, 4000 - price_reduction)
                            if "portail" not in gadget_items and jeton_poche >= portail_price:
                                gadget_items.append("portail")
                                jeton_poche -= portail_price
                                # Ajouter "portail" dans le cadrillage (grille d'inventaire)
                                # Trouver le premier slot disponible dans la grille
                                grid_slot_found = False
                                for row in range(10):
                                    for col in range(4):
                                        slot_name = f'grid_{row}_{col}'
                                        if slot_name not in inventaire_items:
                                            inventaire_items[slot_name] = {'type': 'portail', 'name': 'Portail'}
                                            grid_slot_found = True
                                            break
                                    if grid_slot_found:
                                        break
                        elif shop_mur_button is not None and shop_mur_button.collidepoint(mouse_pos):
                            # Acheter "Mur" pour 2500 pacoins (réduit si "bon marché" est équipé)
                            # Calculer la réduction selon le niveau de "bon marché"
                            bon_marche_level = capacite_items.count("bon marché") if capacite_items else 0
                            price_reduction = bon_marche_level * 5
                            if bon_marche_ameliore and bon_marche_level > 0:
                                price_reduction *= 2
                            mur_price = max(0, 2500 - price_reduction)
                            if "mur" not in gadget_items and jeton_poche >= mur_price:
                                gadget_items.append("mur")
                                jeton_poche -= mur_price
                                # Ajouter "mur" dans le cadrillage (grille d'inventaire)
                                # Trouver le premier slot disponible dans la grille
                                grid_slot_found = False
                                for row in range(10):
                                    for col in range(4):
                                        slot_name = f'grid_{row}_{col}'
                                        if slot_name not in inventaire_items:
                                            inventaire_items[slot_name] = {'type': 'mur', 'name': 'Mur'}
                                            grid_slot_found = True
                                            break
                                    if grid_slot_found:
                                        break
                    elif current_state == SHOP_POUVOIR:
                        # Calculer la réduction selon le niveau de "bon marché"
                        bon_marche_level = capacite_items.count("bon marché") if capacite_items else 0
                        price_reduction = bon_marche_level * 5
                        if bon_marche_ameliore and bon_marche_level > 0:
                            price_reduction *= 2
                        
                        # Les boutons sont retournés par draw_shop_pouvoir
                        if shop_pouvoir_retour_button is not None and shop_pouvoir_retour_button.collidepoint(mouse_pos):
                            current_state = SHOP
                            item_description = None  # Effacer la description quand on retourne
                        elif shop_longue_vue_button is not None and shop_longue_vue_button.collidepoint(mouse_pos):
                            # Acheter "Longue vue" pour 1000 pacoins (réduit si "bon marché" équipé au niveau 1)
                            longue_vue_price = max(0, 1000 - price_reduction)
                            if "longue vue" not in pouvoir_items and jeton_poche >= longue_vue_price:
                                pouvoir_items.append("longue vue")
                                jeton_poche -= longue_vue_price
                                # Ajouter "longue vue" dans le cadrillage (grille d'inventaire)
                                # Trouver le premier slot disponible dans la grille
                                grid_slot_found = False
                                for row in range(10):
                                    for col in range(4):
                                        slot_name = f'grid_{row}_{col}'
                                        if slot_name not in inventaire_items:
                                            inventaire_items[slot_name] = {'type': 'longue vue', 'name': 'Longue vue'}
                                            grid_slot_found = True
                                            break
                                    if grid_slot_found:
                                        break
                        elif shop_double_longue_vue_button is not None and shop_double_longue_vue_button.collidepoint(mouse_pos):
                            # Acheter "Double longue vue" pour 4000 pacoins (réduit si "bon marché" équipé au niveau 1)
                            double_longue_vue_price = max(0, 4000 - price_reduction)
                            if "double longue vue" not in pouvoir_items and jeton_poche >= double_longue_vue_price:
                                pouvoir_items.append("double longue vue")
                                jeton_poche -= double_longue_vue_price
                                # Ajouter "double longue vue" dans le cadrillage (grille d'inventaire)
                                # Trouver le premier slot disponible dans la grille
                                grid_slot_found = False
                                for row in range(10):
                                    for col in range(4):
                                        slot_name = f'grid_{row}_{col}'
                                        if slot_name not in inventaire_items:
                                            inventaire_items[slot_name] = {'type': 'double longue vue', 'name': 'Double longue vue'}
                                            grid_slot_found = True
                                            break
                                    if grid_slot_found:
                                        break
                        elif shop_bon_repas_button is not None and shop_bon_repas_button.collidepoint(mouse_pos):
                            # Acheter "Bon repas" pour 2000 pacoins (réduit si "bon marché" équipé au niveau 1)
                            bon_repas_price = max(0, 2000 - price_reduction)
                            if "bon repas" not in pouvoir_items and jeton_poche >= bon_repas_price:
                                pouvoir_items.append("bon repas")
                                jeton_poche -= bon_repas_price
                                # Ajouter "bon repas" dans le cadrillage (grille d'inventaire)
                                # Trouver le premier slot disponible dans la grille
                                grid_slot_found = False
                                for row in range(10):
                                    for col in range(4):
                                        slot_name = f'grid_{row}_{col}'
                                        if slot_name not in inventaire_items:
                                            inventaire_items[slot_name] = {'type': 'bon repas', 'name': 'Bon repas'}
                                            grid_slot_found = True
                                            break
                                    if grid_slot_found:
                                        break
                        elif shop_bon_gout_button is not None and shop_bon_gout_button.collidepoint(mouse_pos):
                            # Acheter "Bon goût" pour 3000 pacoins (réduit si "bon marché" équipé au niveau 1)
                            bon_gout_price = max(0, 3000 - price_reduction)
                            if "bon goût" not in pouvoir_items and jeton_poche >= bon_gout_price:
                                pouvoir_items.append("bon goût")
                                jeton_poche -= bon_gout_price
                                # Ajouter "bon goût" dans le cadrillage (grille d'inventaire)
                                # Trouver le premier slot disponible dans la grille
                                grid_slot_found = False
                                for row in range(10):
                                    for col in range(4):
                                        slot_name = f'grid_{row}_{col}'
                                        if slot_name not in inventaire_items:
                                            inventaire_items[slot_name] = {'type': 'bon goût', 'name': 'Bon goût'}
                                            grid_slot_found = True
                                            break
                                    if grid_slot_found:
                                        break
                        elif shop_glace_button is not None and shop_glace_button.collidepoint(mouse_pos):
                            # Acheter "Glace" pour 3000 pacoins et 100 couronnes (réduit si "bon marché" équipé au niveau 1)
                            glace_price = max(0, 3000 - price_reduction)
                            if "glace" not in pouvoir_items and jeton_poche >= glace_price and crown_poche >= 100:
                                pouvoir_items.append("glace")
                                jeton_poche -= glace_price
                                crown_poche -= 100
                                # Ajouter "glace" dans le cadrillage (grille d'inventaire)
                                # Trouver le premier slot disponible dans la grille
                                grid_slot_found = False
                                for row in range(10):
                                    for col in range(4):
                                        slot_name = f'grid_{row}_{col}'
                                        if slot_name not in inventaire_items:
                                            inventaire_items[slot_name] = {'type': 'glace', 'name': 'Glace'}
                                            grid_slot_found = True
                                            break
                                    if grid_slot_found:
                                        break
                        elif shop_skin_bleu_button is not None and shop_skin_bleu_button.collidepoint(mouse_pos):
                            # Acheter "Skin bleu" pour 10000 pacoins et 1000 couronnes (réduit si "bon marché" équipé au niveau 1)
                            skin_bleu_price = max(0, 10000 - price_reduction)
                            if "skin bleu" not in pouvoir_items and jeton_poche >= skin_bleu_price and crown_poche >= 1000:
                                pouvoir_items.append("skin bleu")
                                jeton_poche -= skin_bleu_price
                                crown_poche -= 1000
                                # Ajouter "skin bleu" dans le cadrillage (grille d'inventaire)
                                # Trouver le premier slot disponible dans la grille
                                grid_slot_found = False
                                for row in range(10):
                                    for col in range(4):
                                        slot_name = f'grid_{row}_{col}'
                                        if slot_name not in inventaire_items:
                                            inventaire_items[slot_name] = {'type': 'skin bleu', 'name': 'Skin bleu'}
                                            grid_slot_found = True
                                            break
                                    if grid_slot_found:
                                        break
                        elif shop_skin_orange_button is not None and shop_skin_orange_button.collidepoint(mouse_pos):
                            # Acheter "Skin orange" pour 10000 pacoins et 1000 couronnes (réduit si "bon marché" équipé au niveau 1)
                            skin_orange_price = max(0, 10000 - price_reduction)
                            if "skin orange" not in pouvoir_items and jeton_poche >= skin_orange_price and crown_poche >= 1000:
                                pouvoir_items.append("skin orange")
                                jeton_poche -= skin_orange_price
                                crown_poche -= 1000
                                # Ajouter "skin orange" dans le cadrillage (grille d'inventaire)
                                # Trouver le premier slot disponible dans la grille
                                grid_slot_found = False
                                for row in range(10):
                                    for col in range(4):
                                        slot_name = f'grid_{row}_{col}'
                                        if slot_name not in inventaire_items:
                                            inventaire_items[slot_name] = {'type': 'skin orange', 'name': 'Skin orange'}
                                            grid_slot_found = True
                                            break
                                    if grid_slot_found:
                                        break
                        elif shop_skin_rose_button is not None and shop_skin_rose_button.collidepoint(mouse_pos):
                            # Acheter "Skin rose" pour 10000 pacoins et 1000 couronnes (réduit si "bon marché" équipé au niveau 1)
                            skin_rose_price = max(0, 10000 - price_reduction)
                            if "skin rose" not in pouvoir_items and jeton_poche >= skin_rose_price and crown_poche >= 1000:
                                pouvoir_items.append("skin rose")
                                jeton_poche -= skin_rose_price
                                crown_poche -= 1000
                                # Ajouter "skin rose" dans le cadrillage (grille d'inventaire)
                                # Trouver le premier slot disponible dans la grille
                                grid_slot_found = False
                                for row in range(10):
                                    for col in range(4):
                                        slot_name = f'grid_{row}_{col}'
                                        if slot_name not in inventaire_items:
                                            inventaire_items[slot_name] = {'type': 'skin rose', 'name': 'Skin rose'}
                                            grid_slot_found = True
                                            break
                                    if grid_slot_found:
                                        break
                        elif shop_skin_rouge_button is not None and shop_skin_rouge_button.collidepoint(mouse_pos):
                            # Acheter "Skin rouge" pour 10000 pacoins et 1000 couronnes (réduit si "bon marché" équipé au niveau 1)
                            skin_rouge_price = max(0, 10000 - price_reduction)
                            if "skin rouge" not in pouvoir_items and jeton_poche >= skin_rouge_price and crown_poche >= 1000:
                                pouvoir_items.append("skin rouge")
                                jeton_poche -= skin_rouge_price
                                crown_poche -= 1000
                                # Ajouter "skin rouge" dans le cadrillage (grille d'inventaire)
                                # Trouver le premier slot disponible dans la grille
                                grid_slot_found = False
                                for row in range(10):
                                    for col in range(4):
                                        slot_name = f'grid_{row}_{col}'
                                        if slot_name not in inventaire_items:
                                            inventaire_items[slot_name] = {'type': 'skin rouge', 'name': 'Skin rouge'}
                                            grid_slot_found = True
                                            break
                                    if grid_slot_found:
                                        break
                        elif shop_pas_indigestion_button is not None and shop_pas_indigestion_button.collidepoint(mouse_pos):
                            # Acheter "Pas d'indigestion" pour 5000 pacoins (réduit si "bon marché" équipé au niveau 1)
                            pas_indigestion_price = max(0, 5000 - price_reduction)
                            if "pas d'indigestion" not in pouvoir_items and jeton_poche >= pas_indigestion_price:
                                pouvoir_items.append("pas d'indigestion")
                                jeton_poche -= pas_indigestion_price
                                # Ajouter "pas d'indigestion" dans le cadrillage (grille d'inventaire)
                                # Trouver le premier slot disponible dans la grille
                                grid_slot_found = False
                                for row in range(10):
                                    for col in range(4):
                                        slot_name = f'grid_{row}_{col}'
                                        if slot_name not in inventaire_items:
                                            inventaire_items[slot_name] = {'type': 'pas d\'indigestion', 'name': 'Pas d\'indigestion'}
                                            grid_slot_found = True
                                            break
                                    if grid_slot_found:
                                        break
                        else:
                            # Si on clique gauche ailleurs (pas sur un bouton), effacer la description
                            item_description = None
                    elif current_state == SHOP_CAPACITE:
                        # Les boutons sont retournés par draw_shop_capacite
                        if shop_capacite_retour_button is not None and shop_capacite_retour_button.collidepoint(mouse_pos):
                            current_state = SHOP
                            item_description = None  # Effacer la description quand on retourne
                        elif shop_bon_marche_button is not None and shop_bon_marche_button.collidepoint(mouse_pos):
                            # Acheter "Bon marché" pour 5000 pacoins (peut être acheté jusqu'à 10 fois, fusionne en un objet plus puissant)
                            bon_marche_count = capacite_items.count("bon marché")
                            # Calculer la réduction de prix selon le niveau de "bon marché" (pour le prix d'achat lui-même)
                            bon_marche_level_for_price = bon_marche_count
                            price_reduction_for_bon_marche = bon_marche_level_for_price * 5
                            if bon_marche_ameliore and bon_marche_level_for_price > 0:
                                price_reduction_for_bon_marche *= 2
                            bon_marche_price = max(0, 5000 - price_reduction_for_bon_marche)  # Prix réduit si "bon marché" est déjà équipé
                            if bon_marche_count < 10 and jeton_poche >= bon_marche_price:
                                capacite_items.append("bon marché")
                                jeton_poche -= bon_marche_price
                                bon_marche_level = capacite_items.count("bon marché")
                                # Chercher si "bon marché" existe déjà dans l'inventaire (grille, capacite1 ou capacite2)
                                existing_slot = None
                                # Chercher d'abord dans les slots capacité équipés
                                if 'capacite1' in inventaire_items and inventaire_items['capacite1'].get('type') == 'bon marché':
                                    existing_slot = 'capacite1'
                                elif 'capacite2' in inventaire_items and inventaire_items['capacite2'].get('type') == 'bon marché':
                                    existing_slot = 'capacite2'
                                else:
                                    # Chercher dans la grille
                                    for slot_name, item_data in inventaire_items.items():
                                        if item_data.get('type') == 'bon marché':
                                            existing_slot = slot_name
                                            break
                                
                                if existing_slot:
                                    # Fusionner : mettre à jour le niveau de l'objet existant
                                    inventaire_items[existing_slot] = {'type': 'bon marché', 'name': f'Bon marché Nv.{bon_marche_level}'}
                                else:
                                    # Créer un nouveau slot si l'objet n'existe pas
                                    grid_slot_found = False
                                    for row in range(10):
                                        for col in range(4):
                                            slot_name = f'grid_{row}_{col}'
                                            if slot_name not in inventaire_items:
                                                inventaire_items[slot_name] = {'type': 'bon marché', 'name': f'Bon marché Nv.{bon_marche_level}'}
                                                grid_slot_found = True
                                                break
                                        if grid_slot_found:
                                            break
                        elif shop_gadget_button is not None and shop_gadget_button.collidepoint(mouse_pos):
                            # Acheter "Gadget" pour 10000 pacoins et 1000 couronnes (peut être acheté jusqu'à 10 fois, fusionne en un objet plus puissant)
                            gadget_count = capacite_items.count("gadget")
                            # Calculer la réduction de prix selon le niveau de "bon marché"
                            bon_marche_level = capacite_items.count("bon marché") if capacite_items else 0
                            price_reduction = bon_marche_level * 5
                            if bon_marche_ameliore and bon_marche_level > 0:
                                price_reduction *= 2
                            gadget_price = max(0, 10000 - price_reduction)  # Prix réduit si "bon marché" est équipé (seulement pour les pacoins)
                            if gadget_count < 10 and jeton_poche >= gadget_price and crown_poche >= 1000:
                                capacite_items.append("gadget")
                                jeton_poche -= gadget_price
                                crown_poche -= 1000
                                gadget_level = capacite_items.count("gadget")
                                # Chercher si "gadget" existe déjà dans l'inventaire (grille, capacite1 ou capacite2)
                                existing_slot = None
                                # Chercher d'abord dans les slots capacité équipés
                                if 'capacite1' in inventaire_items and inventaire_items['capacite1'].get('type') == 'gadget':
                                    existing_slot = 'capacite1'
                                elif 'capacite2' in inventaire_items and inventaire_items['capacite2'].get('type') == 'gadget':
                                    existing_slot = 'capacite2'
                                else:
                                    # Chercher dans la grille
                                    for slot_name, item_data in inventaire_items.items():
                                        if item_data.get('type') == 'gadget':
                                            existing_slot = slot_name
                                            break
                                
                                if existing_slot:
                                    # Fusionner : mettre à jour le niveau de l'objet existant
                                    inventaire_items[existing_slot] = {'type': 'gadget', 'name': f'Gadget Nv.{gadget_level}'}
                                else:
                                    # Créer un nouveau slot si l'objet n'existe pas
                                    grid_slot_found = False
                                    for row in range(10):
                                        for col in range(4):
                                            slot_name = f'grid_{row}_{col}'
                                            if slot_name not in inventaire_items:
                                                inventaire_items[slot_name] = {'type': 'gadget', 'name': f'Gadget Nv.{gadget_level}'}
                                                grid_slot_found = True
                                                break
                                        if grid_slot_found:
                                            break
                        elif shop_pacgum_button is not None and shop_pacgum_button.collidepoint(mouse_pos):
                            # Acheter "Pacgum" pour 4000 pacoins (peut être acheté jusqu'à 10 fois, fusionne en un objet plus puissant)
                            pacgum_count = capacite_items.count("pacgum")
                            if pacgum_count < 10 and jeton_poche >= 4000:
                                capacite_items.append("pacgum")
                                jeton_poche -= 4000
                                pacgum_level = capacite_items.count("pacgum")
                                # Chercher si "pacgum" existe déjà dans l'inventaire (grille, capacite1 ou capacite2)
                                existing_slot = None
                                # Chercher d'abord dans les slots capacité équipés
                                if 'capacite1' in inventaire_items and inventaire_items['capacite1'].get('type') == 'pacgum':
                                    existing_slot = 'capacite1'
                                elif 'capacite2' in inventaire_items and inventaire_items['capacite2'].get('type') == 'pacgum':
                                    existing_slot = 'capacite2'
                                else:
                                    # Chercher dans la grille
                                    for slot_name, item_data in inventaire_items.items():
                                        if item_data.get('type') == 'pacgum':
                                            existing_slot = slot_name
                                            break
                                
                                if existing_slot:
                                    # Fusionner : mettre à jour le niveau de l'objet existant
                                    inventaire_items[existing_slot] = {'type': 'pacgum', 'name': f'Pacgum Nv.{pacgum_level}'}
                                else:
                                    # Créer un nouveau slot si l'objet n'existe pas
                                    grid_slot_found = False
                                    for row in range(10):
                                        for col in range(4):
                                            slot_name = f'grid_{row}_{col}'
                                            if slot_name not in inventaire_items:
                                                inventaire_items[slot_name] = {'type': 'pacgum', 'name': f'Pacgum Nv.{pacgum_level}'}
                                                grid_slot_found = True
                                                break
                                        if grid_slot_found:
                                            break
                        elif shop_indigestion_button is not None and shop_indigestion_button.collidepoint(mouse_pos):
                            # Acheter "Indigestion" pour 3500 pacoins (peut être acheté jusqu'à 10 fois, fusionne en un objet plus puissant)
                            indigestion_count = capacite_items.count("indigestion")
                            # Calculer la réduction de prix selon le niveau de "bon marché"
                            bon_marche_level = capacite_items.count("bon marché") if capacite_items else 0
                            price_reduction = bon_marche_level * 5
                            if bon_marche_ameliore and bon_marche_level > 0:
                                price_reduction *= 2
                            indigestion_price = max(0, 3500 - price_reduction)  # Prix réduit si "bon marché" est équipé
                            if indigestion_count < 10 and jeton_poche >= indigestion_price:
                                capacite_items.append("indigestion")
                                jeton_poche -= indigestion_price
                                indigestion_level = capacite_items.count("indigestion")
                                # Chercher si "indigestion" existe déjà dans l'inventaire (grille, capacite1 ou capacite2)
                                existing_slot = None
                                # Chercher d'abord dans les slots capacité équipés
                                if 'capacite1' in inventaire_items and inventaire_items['capacite1'].get('type') == 'indigestion':
                                    existing_slot = 'capacite1'
                                elif 'capacite2' in inventaire_items and inventaire_items['capacite2'].get('type') == 'indigestion':
                                    existing_slot = 'capacite2'
                                else:
                                    # Chercher dans la grille
                                    for slot_name, item_data in inventaire_items.items():
                                        if item_data.get('type') == 'indigestion':
                                            existing_slot = slot_name
                                            break
                                
                                if existing_slot:
                                    # Fusionner : mettre à jour le niveau de l'objet existant
                                    inventaire_items[existing_slot] = {'type': 'indigestion', 'name': f'Indigestion Nv.{indigestion_level}'}
                                else:
                                    # Créer un nouveau slot si l'objet n'existe pas
                                    grid_slot_found = False
                                    for row in range(10):
                                        for col in range(4):
                                            slot_name = f'grid_{row}_{col}'
                                            if slot_name not in inventaire_items:
                                                inventaire_items[slot_name] = {'type': 'indigestion', 'name': f'Indigestion Nv.{indigestion_level}'}
                                                grid_slot_found = True
                                                break
                                        if grid_slot_found:
                                            break
                        elif shop_gel_button is not None and shop_gel_button.collidepoint(mouse_pos):
                            # Acheter "Gel" pour 5000 pacoins (peut être acheté jusqu'à 10 fois, fusionne en un objet plus puissant)
                            gel_count = capacite_items.count("gel")
                            # Calculer la réduction de prix selon le niveau de "bon marché"
                            bon_marche_level = capacite_items.count("bon marché") if capacite_items else 0
                            price_reduction = bon_marche_level * 5
                            if bon_marche_ameliore and bon_marche_level > 0:
                                price_reduction *= 2
                            gel_price = max(0, 5000 - price_reduction)  # Prix réduit si "bon marché" est équipé
                            if gel_count < 10 and jeton_poche >= gel_price:
                                capacite_items.append("gel")
                                jeton_poche -= gel_price
                                gel_level = capacite_items.count("gel")
                                # Chercher si "gel" existe déjà dans l'inventaire (grille, capacite1 ou capacite2)
                                existing_slot = None
                                # Chercher d'abord dans les slots capacité équipés
                                if 'capacite1' in inventaire_items and inventaire_items['capacite1'].get('type') == 'gel':
                                    existing_slot = 'capacite1'
                                elif 'capacite2' in inventaire_items and inventaire_items['capacite2'].get('type') == 'gel':
                                    existing_slot = 'capacite2'
                                else:
                                    # Chercher dans la grille
                                    for slot_name, item_data in inventaire_items.items():
                                        if item_data.get('type') == 'gel':
                                            existing_slot = slot_name
                                            break
                                
                                if existing_slot:
                                    # Fusionner : mettre à jour le niveau de l'objet existant
                                    inventaire_items[existing_slot] = {'type': 'gel', 'name': f'Gel Nv.{gel_level}'}
                                else:
                                    # Créer un nouveau slot si l'objet n'existe pas
                                    grid_slot_found = False
                                    for row in range(10):
                                        for col in range(4):
                                            slot_name = f'grid_{row}_{col}'
                                            if slot_name not in inventaire_items:
                                                inventaire_items[slot_name] = {'type': 'gel', 'name': f'Gel Nv.{gel_level}'}
                                                grid_slot_found = True
                                                break
                                        if grid_slot_found:
                                            break
                        elif shop_lunette_button is not None and shop_lunette_button.collidepoint(mouse_pos):
                            # Acheter "Lunette" pour 10000 pacoins et 10000 couronnes (peut être acheté jusqu'à 2 fois, fusionne en un objet plus puissant)
                            lunette_count = capacite_items.count("lunette")
                            # Calculer la réduction de prix selon le niveau de "bon marché"
                            bon_marche_level = capacite_items.count("bon marché") if capacite_items else 0
                            price_reduction = bon_marche_level * 5
                            if bon_marche_ameliore and bon_marche_level > 0:
                                price_reduction *= 2
                            lunette_price = max(0, 10000 - price_reduction)  # Prix réduit si "bon marché" est équipé (seulement pour les pacoins)
                            lunette_crown_price = 10000  # Prix en couronnes (non affecté par "bon marché")
                            if lunette_count < 2 and jeton_poche >= lunette_price and crown_poche >= lunette_crown_price:
                                capacite_items.append("lunette")
                                jeton_poche -= lunette_price
                                crown_poche -= lunette_crown_price
                                lunette_level = capacite_items.count("lunette")
                                # Chercher si "lunette" existe déjà dans l'inventaire (grille, capacite1 ou capacite2)
                                existing_slot = None
                                # Chercher d'abord dans les slots capacité équipés
                                if 'capacite1' in inventaire_items and inventaire_items['capacite1'].get('type') == 'lunette':
                                    existing_slot = 'capacite1'
                                elif 'capacite2' in inventaire_items and inventaire_items['capacite2'].get('type') == 'lunette':
                                    existing_slot = 'capacite2'
                                else:
                                    # Chercher dans la grille
                                    for slot_name, item_data in inventaire_items.items():
                                        if item_data.get('type') == 'lunette':
                                            existing_slot = slot_name
                                            break
                                
                                if existing_slot:
                                    # Fusionner : mettre à jour le niveau de l'objet existant
                                    inventaire_items[existing_slot] = {'type': 'lunette', 'name': f'Lunette Nv.{lunette_level}'}
                                else:
                                    # Créer un nouveau slot si l'objet n'existe pas
                                    grid_slot_found = False
                                    for row in range(10):
                                        for col in range(4):
                                            slot_name = f'grid_{row}_{col}'
                                            if slot_name not in inventaire_items:
                                                inventaire_items[slot_name] = {'type': 'lunette', 'name': f'Lunette Nv.{lunette_level}'}
                                                grid_slot_found = True
                                                break
                                        if grid_slot_found:
                                            break
                        elif shop_invincibilite_button is not None and shop_invincibilite_button.collidepoint(mouse_pos):
                            # Acheter "Invincibilité" pour 5000 pacoins (peut être acheté jusqu'à 10 fois, fusionne en un objet plus puissant)
                            invincibilite_count = capacite_items.count("invincibilité")
                            # Calculer la réduction de prix selon le niveau de "bon marché"
                            bon_marche_level = capacite_items.count("bon marché") if capacite_items else 0
                            price_reduction = bon_marche_level * 5
                            if bon_marche_ameliore and bon_marche_level > 0:
                                price_reduction *= 2
                            invincibilite_price = max(0, 5000 - price_reduction)  # Prix réduit si "bon marché" est équipé
                            if invincibilite_count < 10 and jeton_poche >= invincibilite_price:
                                capacite_items.append("invincibilité")
                                jeton_poche -= invincibilite_price
                                invincibilite_level = capacite_items.count("invincibilité")
                                # Chercher si "invincibilité" existe déjà dans l'inventaire (grille, capacite1 ou capacite2)
                                existing_slot = None
                                # Chercher d'abord dans les slots capacité équipés
                                if 'capacite1' in inventaire_items and inventaire_items['capacite1'].get('type') == 'invincibilité':
                                    existing_slot = 'capacite1'
                                elif 'capacite2' in inventaire_items and inventaire_items['capacite2'].get('type') == 'invincibilité':
                                    existing_slot = 'capacite2'
                                else:
                                    # Chercher dans la grille
                                    for slot_name, item_data in inventaire_items.items():
                                        if item_data.get('type') == 'invincibilité':
                                            existing_slot = slot_name
                                            break
                                
                                if existing_slot:
                                    # Fusionner : mettre à jour le niveau de l'objet existant
                                    inventaire_items[existing_slot] = {'type': 'invincibilité', 'name': f'Invincibilité Nv.{invincibilite_level}'}
                                else:
                                    # Créer un nouveau slot si l'objet n'existe pas
                                    grid_slot_found = False
                                    for row in range(10):
                                        for col in range(4):
                                            slot_name = f'grid_{row}_{col}'
                                            if slot_name not in inventaire_items:
                                                inventaire_items[slot_name] = {'type': 'invincibilité', 'name': f'Invincibilité Nv.{invincibilite_level}'}
                                                grid_slot_found = True
                                                break
                                        if grid_slot_found:
                                            break
                        elif shop_piquant_button is not None and shop_piquant_button.collidepoint(mouse_pos):
                            # Acheter "Piquant" pour 5000 pacoins (peut être acheté jusqu'à 10 fois, fusionne en un objet plus puissant)
                            piquant_count = capacite_items.count("piquant")
                            # Calculer la réduction de prix selon le niveau de "bon marché"
                            bon_marche_level = capacite_items.count("bon marché") if capacite_items else 0
                            price_reduction = bon_marche_level * 5
                            if bon_marche_ameliore and bon_marche_level > 0:
                                price_reduction *= 2
                            piquant_price = max(0, 5000 - price_reduction)  # Prix réduit si "bon marché" est équipé
                            if piquant_count < 10 and jeton_poche >= piquant_price:
                                capacite_items.append("piquant")
                                jeton_poche -= piquant_price
                                piquant_level = capacite_items.count("piquant")
                                # Chercher si "piquant" existe déjà dans l'inventaire (grille, capacite1 ou capacite2)
                                existing_slot = None
                                # Chercher d'abord dans les slots capacité équipés
                                if 'capacite1' in inventaire_items and inventaire_items['capacite1'].get('type') == 'piquant':
                                    existing_slot = 'capacite1'
                                elif 'capacite2' in inventaire_items and inventaire_items['capacite2'].get('type') == 'piquant':
                                    existing_slot = 'capacite2'
                                else:
                                    # Chercher dans la grille
                                    for slot_name, item_data in inventaire_items.items():
                                        if item_data.get('type') == 'piquant':
                                            existing_slot = slot_name
                                            break
                                
                                if existing_slot:
                                    # Fusionner : mettre à jour le niveau de l'objet existant
                                    inventaire_items[existing_slot] = {'type': 'piquant', 'name': f'Piquant Nv.{piquant_level}'}
                                else:
                                    # Créer un nouveau slot si l'objet n'existe pas
                                    grid_slot_found = False
                                    for row in range(10):
                                        for col in range(4):
                                            slot_name = f'grid_{row}_{col}'
                                            if slot_name not in inventaire_items:
                                                inventaire_items[slot_name] = {'type': 'piquant', 'name': f'Piquant Nv.{piquant_level}'}
                                                grid_slot_found = True
                                                break
                                        if grid_slot_found:
                                            break
                        elif shop_bon_vue_button is not None and shop_bon_vue_button.collidepoint(mouse_pos):
                            # Acheter "Bonne vue" pour 5000 pacoins (peut être acheté jusqu'à 10 fois, fusionne en un objet plus puissant)
                            bon_vue_count = capacite_items.count("bonne vue")
                            # Calculer la réduction de prix selon le niveau de "bon marché"
                            bon_marche_level = capacite_items.count("bon marché") if capacite_items else 0
                            price_reduction = bon_marche_level * 5
                            if bon_marche_ameliore and bon_marche_level > 0:
                                price_reduction *= 2
                            bon_vue_price = max(0, 5000 - price_reduction)  # Prix réduit si "bon marché" est équipé
                            if bon_vue_count < 10 and jeton_poche >= bon_vue_price:
                                capacite_items.append("bonne vue")
                                jeton_poche -= bon_vue_price
                                bon_vue_level = capacite_items.count("bonne vue")
                                # Chercher si "bonne vue" existe déjà dans l'inventaire (grille, capacite1 ou capacite2)
                                existing_slot = None
                                # Chercher d'abord dans les slots capacité équipés
                                if 'capacite1' in inventaire_items and inventaire_items['capacite1'].get('type') == 'bonne vue':
                                    existing_slot = 'capacite1'
                                elif 'capacite2' in inventaire_items and inventaire_items['capacite2'].get('type') == 'bonne vue':
                                    existing_slot = 'capacite2'
                                else:
                                    # Chercher dans la grille
                                    for slot_name, item_data in inventaire_items.items():
                                        if item_data.get('type') == 'bonne vue':
                                            existing_slot = slot_name
                                            break
                                
                                if existing_slot:
                                    # Fusionner : mettre à jour le niveau de l'objet existant
                                    inventaire_items[existing_slot] = {'type': 'bonne vue', 'name': f'Bonne vue Nv.{bon_vue_level}'}
                                else:
                                    # Créer un nouveau slot si l'objet n'existe pas
                                    grid_slot_found = False
                                    for row in range(10):
                                        for col in range(4):
                                            slot_name = f'grid_{row}_{col}'
                                            if slot_name not in inventaire_items:
                                                inventaire_items[slot_name] = {'type': 'bonne vue', 'name': f'Bonne vue Nv.{bon_vue_level}'}
                                                grid_slot_found = True
                                                break
                                        if grid_slot_found:
                                            break
                        elif shop_bonbe_button is not None and shop_bonbe_button.collidepoint(mouse_pos):
                            # Acheter "Bonbe" pour 5000 pacoins (peut être acheté jusqu'à 3 fois, fusionne en un objet plus puissant)
                            bonbe_count = capacite_items.count("bonbe")
                            # Calculer la réduction de prix selon le niveau de "bon marché"
                            bon_marche_level = capacite_items.count("bon marché") if capacite_items else 0
                            price_reduction = bon_marche_level * 5
                            if bon_marche_ameliore and bon_marche_level > 0:
                                price_reduction *= 2
                            bonbe_price = max(0, 5000 - price_reduction)  # Prix réduit si "bon marché" est équipé
                            if bonbe_count < 3 and jeton_poche >= bonbe_price:
                                capacite_items.append("bonbe")
                                jeton_poche -= bonbe_price
                                bonbe_level = capacite_items.count("bonbe")
                                # Chercher si "bonbe" existe déjà dans l'inventaire (grille, capacite1 ou capacite2)
                                existing_slot = None
                                # Chercher d'abord dans les slots capacité équipés
                                if 'capacite1' in inventaire_items and inventaire_items['capacite1'].get('type') == 'bonbe':
                                    existing_slot = 'capacite1'
                                elif 'capacite2' in inventaire_items and inventaire_items['capacite2'].get('type') == 'bonbe':
                                    existing_slot = 'capacite2'
                                else:
                                    # Chercher dans la grille
                                    for slot_name, item_data in inventaire_items.items():
                                        if item_data.get('type') == 'bonbe':
                                            existing_slot = slot_name
                                            break
                                
                                if existing_slot:
                                    # Fusionner : mettre à jour le niveau de l'objet existant
                                    inventaire_items[existing_slot] = {'type': 'bonbe', 'name': f'Bonbe Nv.{bonbe_level}'}
                                else:
                                    # Créer un nouveau slot si l'objet n'existe pas
                                    grid_slot_found = False
                                    for row in range(10):
                                        for col in range(4):
                                            slot_name = f'grid_{row}_{col}'
                                            if slot_name not in inventaire_items:
                                                inventaire_items[slot_name] = {'type': 'bonbe', 'name': f'Bonbe Nv.{bonbe_level}'}
                                                grid_slot_found = True
                                                break
                                        if grid_slot_found:
                                            break
                        elif shop_ameliorer_button is not None and shop_ameliorer_button.collidepoint(mouse_pos):
                            # Améliorer "Bon marché" pour 1 couronne (fonctionne aussi au niveau 2)
                            if "bon marché" in capacite_items and not bon_marche_ameliore and crown_poche >= 1:
                                bon_marche_ameliore = True
                                crown_poche -= 1
                        else:
                            # Si on clique gauche ailleurs (pas sur un bouton), effacer la description
                            item_description = None
                    elif current_state == SHOP_OBJET:
                        # Vérifier si "bon marché" est équipé et si on est au niveau 1 ou 2 (si amélioré)
                        # Calculer la réduction selon le niveau de "bon marché"
                        bon_marche_level = capacite_items.count("bon marché") if capacite_items else 0
                        price_reduction = bon_marche_level * 5
                        if bon_marche_ameliore and bon_marche_level > 0:
                            price_reduction *= 2
                        
                        # Les boutons sont retournés par draw_shop_objet
                        if shop_objet_retour_button is not None and shop_objet_retour_button.collidepoint(mouse_pos):
                            current_state = SHOP
                            item_description = None  # Effacer la description quand on retourne
                        elif shop_piece_mythique_button is not None and shop_piece_mythique_button.collidepoint(mouse_pos):
                            # Acheter "Pièce mythique" pour 10000 pacoins et 50 couronnes (réduit si "bon marché" est équipé)
                            piece_mythique_price = max(0, 10000 - price_reduction)
                            if "pièce mythique" not in objet_items and jeton_poche >= piece_mythique_price and crown_poche >= 50:
                                objet_items.append("pièce mythique")
                                jeton_poche -= piece_mythique_price
                                crown_poche -= 50
                                # Ajouter "pièce mythique" dans un slot objet (objet0, objet1, ou objet2) ou dans la grille
                                # Essayer d'abord les slots objet, puis la grille si aucun n'est disponible
                                slot_found = False
                                # Chercher dans les slots objet d'abord
                                for i in range(3):
                                    slot_name = f'objet{i}'
                                    if slot_name not in inventaire_items:
                                        inventaire_items[slot_name] = {'type': 'pièce mythique', 'name': 'Pièce mythique'}
                                        slot_found = True
                                        break
                                # Si aucun slot objet n'est disponible, chercher dans la grille
                                if not slot_found:
                                    for row in range(10):
                                        for col in range(4):
                                            slot_name = f'grid_{row}_{col}'
                                            if slot_name not in inventaire_items:
                                                inventaire_items[slot_name] = {'type': 'pièce mythique', 'name': 'Pièce mythique'}
                                                slot_found = True
                                                break
                                        if slot_found:
                                            break
                        elif shop_grosse_armure_button is not None and shop_grosse_armure_button.collidepoint(mouse_pos):
                            # Acheter "Grosse armure" pour 500 pacoins (réduit si "bon marché" est équipé)
                            grosse_armure_price = max(0, 500 - price_reduction)
                            # Permettre d'acheter une seule grosse armure
                            if "grosse armure" not in objet_items and jeton_poche >= grosse_armure_price:
                                objet_items.append("grosse armure")
                                jeton_poche -= grosse_armure_price
                                # Ajouter "grosse armure" dans un slot objet (objet0, objet1, ou objet2) ou dans la grille
                                # Essayer d'abord les slots objet, puis la grille si aucun n'est disponible
                                slot_found = False
                                # Chercher dans les slots objet d'abord
                                for i in range(3):
                                    slot_name = f'objet{i}'
                                    if slot_name not in inventaire_items:
                                        inventaire_items[slot_name] = {'type': 'grosse armure', 'name': 'Grosse armure'}
                                        slot_found = True
                                        break
                                # Si aucun slot objet n'est disponible, chercher dans la grille
                                if not slot_found:
                                    for row in range(10):
                                        for col in range(4):
                                            slot_name = f'grid_{row}_{col}'
                                            if slot_name not in inventaire_items:
                                                inventaire_items[slot_name] = {'type': 'grosse armure', 'name': 'Grosse armure'}
                                                slot_found = True
                                                break
                                        if slot_found:
                                            break
                        elif shop_armure_fer_button is not None and shop_armure_fer_button.collidepoint(mouse_pos):
                            # Acheter "Armure de fer" pour 500 pacoins (réduit si "bon marché" est équipé)
                            armure_fer_price = max(0, 500 - price_reduction)
                            # Permettre d'acheter une seule armure de fer
                            if "armure de fer" not in objet_items and jeton_poche >= armure_fer_price:
                                objet_items.append("armure de fer")
                                jeton_poche -= armure_fer_price
                                # Ajouter "armure de fer" dans un slot objet (objet0, objet1, ou objet2) ou dans la grille
                                # Essayer d'abord les slots objet, puis la grille si aucun n'est disponible
                                slot_found = False
                                # Chercher dans les slots objet d'abord
                                for i in range(3):
                                    slot_name = f'objet{i}'
                                    if slot_name not in inventaire_items:
                                        inventaire_items[slot_name] = {'type': 'armure de fer', 'name': 'Armure de fer'}
                                        slot_found = True
                                        break
                                # Si aucun slot objet n'est disponible, chercher dans la grille
                                if not slot_found:
                                    for row in range(10):
                                        for col in range(4):
                                            slot_name = f'grid_{row}_{col}'
                                            if slot_name not in inventaire_items:
                                                inventaire_items[slot_name] = {'type': 'armure de fer', 'name': 'Armure de fer'}
                                                slot_found = True
                                                break
                                        if slot_found:
                                            break
                        elif shop_flamme_button is not None and shop_flamme_button.collidepoint(mouse_pos):
                            # Acheter "Flamme" pour 2000 pacoins (réduit si "bon marché" est équipé)
                            flamme_price = max(0, 2000 - price_reduction)
                            # Permettre d'acheter une seule flamme
                            if "flamme" not in objet_items and jeton_poche >= flamme_price:
                                objet_items.append("flamme")
                                jeton_poche -= flamme_price
                                # Ajouter "flamme" dans un slot objet (objet0, objet1, ou objet2) ou dans la grille
                                # Essayer d'abord les slots objet, puis la grille si aucun n'est disponible
                                slot_found = False
                                # Chercher dans les slots objet d'abord
                                for i in range(3):
                                    slot_name = f'objet{i}'
                                    if slot_name not in inventaire_items:
                                        inventaire_items[slot_name] = {'type': 'flamme', 'name': 'Flamme'}
                                        slot_found = True
                                        break
                                # Si aucun slot objet n'est disponible, chercher dans la grille
                                if not slot_found:
                                    for row in range(10):
                                        for col in range(4):
                                            slot_name = f'grid_{row}_{col}'
                                            if slot_name not in inventaire_items:
                                                inventaire_items[slot_name] = {'type': 'flamme', 'name': 'Flamme'}
                                                slot_found = True
                                                break
                                        if slot_found:
                                            break
                        elif shop_givre_button is not None and shop_givre_button.collidepoint(mouse_pos):
                            # Acheter "Givre" pour 3000 pacoins (réduit si "bon marché" est équipé)
                            givre_price = max(0, 3000 - price_reduction)
                            # Permettre d'acheter un seul givre
                            if "givre" not in objet_items and jeton_poche >= givre_price:
                                objet_items.append("givre")
                                jeton_poche -= givre_price
                                # Ajouter "givre" dans un slot objet (objet0, objet1, ou objet2) ou dans la grille
                                # Essayer d'abord les slots objet, puis la grille si aucun n'est disponible
                                slot_found = False
                                # Chercher dans les slots objet d'abord
                                for i in range(3):
                                    slot_name = f'objet{i}'
                                    if slot_name not in inventaire_items:
                                        inventaire_items[slot_name] = {'type': 'givre', 'name': 'Givre'}
                                        slot_found = True
                                        break
                                # Si aucun slot objet n'est disponible, chercher dans la grille
                                if not slot_found:
                                    for row in range(10):
                                        for col in range(4):
                                            slot_name = f'grid_{row}_{col}'
                                            if slot_name not in inventaire_items:
                                                inventaire_items[slot_name] = {'type': 'givre', 'name': 'Givre'}
                                                slot_found = True
                                                break
                                        if slot_found:
                                            break
                        elif shop_infra_rouge_button is not None and shop_infra_rouge_button.collidepoint(mouse_pos):
                            # Acheter "Infra rouge" pour 4000 pacoins (réduit si "bon marché" est équipé)
                            infra_rouge_price = max(0, 4000 - price_reduction)
                            # Permettre d'acheter un seul infra rouge
                            if "infra rouge" not in objet_items and jeton_poche >= infra_rouge_price:
                                objet_items.append("infra rouge")
                                jeton_poche -= infra_rouge_price
                                # Ajouter "infra rouge" dans un slot objet (objet0, objet1, ou objet2) ou dans la grille
                                # Essayer d'abord les slots objet, puis la grille si aucun n'est disponible
                                slot_found = False
                                # Chercher dans les slots objet d'abord
                                for i in range(3):
                                    slot_name = f'objet{i}'
                                    if slot_name not in inventaire_items:
                                        inventaire_items[slot_name] = {'type': 'infra rouge', 'name': 'Infra rouge'}
                                        slot_found = True
                                        break
                                # Si aucun slot objet n'est disponible, chercher dans la grille
                                if not slot_found:
                                    for row in range(10):
                                        for col in range(4):
                                            slot_name = f'grid_{row}_{col}'
                                            if slot_name not in inventaire_items:
                                                inventaire_items[slot_name] = {'type': 'infra rouge', 'name': 'Infra rouge'}
                                                slot_found = True
                                                break
                                        if slot_found:
                                            break
                        elif shop_bric_button is not None and shop_bric_button.collidepoint(mouse_pos):
                            # Acheter "Bric" pour 5000 pacoins (réduit si "bon marché" est équipé)
                            bric_price = max(0, 5000 - price_reduction)
                            # Permettre d'acheter un seul bric
                            if "bric" not in objet_items and jeton_poche >= bric_price:
                                objet_items.append("bric")
                                jeton_poche -= bric_price
                                # Ajouter "bric" dans un slot objet (objet0, objet1, ou objet2) ou dans la grille
                                # Essayer d'abord les slots objet, puis la grille si aucun n'est disponible
                                slot_found = False
                                # Chercher dans les slots objet d'abord
                                for i in range(3):
                                    slot_name = f'objet{i}'
                                    if slot_name not in inventaire_items:
                                        inventaire_items[slot_name] = {'type': 'bric', 'name': 'Bric'}
                                        slot_found = True
                                        break
                                # Si aucun slot objet n'est disponible, chercher dans la grille
                                if not slot_found:
                                    for row in range(10):
                                        for col in range(4):
                                            slot_name = f'grid_{row}_{col}'
                                            if slot_name not in inventaire_items:
                                                inventaire_items[slot_name] = {'type': 'bric', 'name': 'Bric'}
                                                slot_found = True
                                                break
                                        if slot_found:
                                            break
                        elif shop_coffre_fort_button is not None and shop_coffre_fort_button.collidepoint(mouse_pos):
                            # Acheter "Coffre fort" pour 10000 pacoins (réduit si "bon marché" est équipé)
                            coffre_fort_price = max(0, 10000 - price_reduction)
                            # Permettre d'acheter un seul coffre fort
                            if "coffre fort" not in objet_items and jeton_poche >= coffre_fort_price:
                                objet_items.append("coffre fort")
                                jeton_poche -= coffre_fort_price
                                # Ajouter "coffre fort" dans un slot objet (objet0, objet1, ou objet2) ou dans la grille
                                # Essayer d'abord les slots objet, puis la grille si aucun n'est disponible
                                slot_found = False
                                # Chercher dans les slots objet d'abord
                                for i in range(3):
                                    slot_name = f'objet{i}'
                                    if slot_name not in inventaire_items:
                                        inventaire_items[slot_name] = {'type': 'coffre fort', 'name': 'Coffre fort'}
                                        slot_found = True
                                        break
                                # Si aucun slot objet n'est disponible, chercher dans la grille
                                if not slot_found:
                                    for row in range(10):
                                        for col in range(4):
                                            slot_name = f'grid_{row}_{col}'
                                            if slot_name not in inventaire_items:
                                                inventaire_items[slot_name] = {'type': 'coffre fort', 'name': 'Coffre fort'}
                                                slot_found = True
                                                break
                                        if slot_found:
                                            break
                        elif shop_coffre_tresor_button is not None and shop_coffre_tresor_button.collidepoint(mouse_pos):
                            # Acheter "Coffre au trésor" pour 15000 pacoins (réduit si "bon marché" est équipé)
                            coffre_tresor_price = max(0, 15000 - price_reduction)
                            # Permettre d'acheter un seul coffre au trésor
                            if "coffre au trésor" not in objet_items and jeton_poche >= coffre_tresor_price:
                                objet_items.append("coffre au trésor")
                                jeton_poche -= coffre_tresor_price
                                # Ajouter "coffre au trésor" dans un slot objet (objet0, objet1, ou objet2) ou dans la grille
                                # Essayer d'abord les slots objet, puis la grille si aucun n'est disponible
                                slot_found = False
                                # Chercher dans les slots objet d'abord
                                for i in range(3):
                                    slot_name = f'objet{i}'
                                    if slot_name not in inventaire_items:
                                        inventaire_items[slot_name] = {'type': 'coffre au trésor', 'name': 'Coffre au trésor'}
                                        slot_found = True
                                        break
                                # Si aucun slot objet n'est disponible, chercher dans la grille
                                if not slot_found:
                                    for row in range(10):
                                        for col in range(4):
                                            slot_name = f'grid_{row}_{col}'
                                            if slot_name not in inventaire_items:
                                                inventaire_items[slot_name] = {'type': 'coffre au trésor', 'name': 'Coffre au trésor'}
                                                slot_found = True
                                                break
                                        if slot_found:
                                            break
                        elif shop_double_gadget_button is not None and shop_double_gadget_button.collidepoint(mouse_pos):
                            # Acheter "Double gadget" pour 8000 pacoins (réduit si "bon marché" est équipé)
                            double_gadget_price = max(0, 8000 - price_reduction)
                            # Permettre d'acheter un seul double gadget
                            if "double gadget" not in objet_items and jeton_poche >= double_gadget_price:
                                objet_items.append("double gadget")
                                jeton_poche -= double_gadget_price
                                # Ajouter "double gadget" dans un slot objet (objet0, objet1, ou objet2) ou dans la grille
                                # Essayer d'abord les slots objet, puis la grille si aucun n'est disponible
                                slot_found = False
                                # Chercher dans les slots objet d'abord
                                for i in range(3):
                                    slot_name = f'objet{i}'
                                    if slot_name not in inventaire_items:
                                        inventaire_items[slot_name] = {'type': 'double gadget', 'name': 'Double gadget'}
                                        slot_found = True
                                        break
                                # Si aucun slot objet n'est disponible, chercher dans la grille
                                if not slot_found:
                                    for row in range(10):
                                        for col in range(4):
                                            slot_name = f'grid_{row}_{col}'
                                            if slot_name not in inventaire_items:
                                                inventaire_items[slot_name] = {'type': 'double gadget', 'name': 'Double gadget'}
                                                slot_found = True
                                                break
                                        if slot_found:
                                            break
                        else:
                            # Si on clique gauche ailleurs (pas sur un bouton), effacer la description
                            item_description = None
                    elif current_state == DIFFICULTY:
                        # Les boutons sont retournés par draw_difficulty
                        if retour_button.collidepoint(mouse_pos):
                            current_state = MENU
                        elif button1.collidepoint(mouse_pos):
                            # Bouton FACILE - sauvegarder la difficulté et revenir au menu
                            difficulty = "facile"
                            current_state = MENU
                        elif button2.collidepoint(mouse_pos):
                            # Bouton MOYEN - sauvegarder la difficulté et revenir au menu
                            difficulty = "moyen"
                            current_state = MENU
                        elif button3.collidepoint(mouse_pos):
                            # Bouton DIFFICILE - sauvegarder la difficulté et revenir au menu
                            difficulty = "difficile"
                            current_state = MENU
                        elif button4.collidepoint(mouse_pos):
                            # Bouton HARDCORE - sauvegarder la difficulté et revenir au menu
                            difficulty = "hardcore"
                            current_state = MENU
                    elif current_state == POCHE:
                        retour_button = pygame.Rect(10, 10, 100, 40)
                        if retour_button.collidepoint(mouse_pos):
                            current_state = MENU
                    elif current_state == BOUTIQUE:
                        # Gestion des clics dans la boutique
                        if boutique_retour_button is not None and boutique_retour_button.collidepoint(mouse_pos):
                            current_state = MENU
                        elif boutique_exchange1_button is not None and boutique_exchange1_button.collidepoint(mouse_pos):
                            # Échange 1: 500 pacoins → 1 couronne
                            if jeton_poche >= 500:
                                jeton_poche -= 500
                                crown_poche += 1
                                # Sauvegarder
                                if current_account_index is not None:
                                    auto_save_account_data(current_account_index, pouvoir_items, gadget_items, objet_items, capacite_items, inventaire_items, jeton_poche, crown_poche, bon_marche_ameliore, battle_pass_xp, battle_pass_claimed_rewards, gemme_poche, used_stars, accounts, battle_pass_plus_claimed_rewards, used_stars_plus, pass_plus_purchased)
                        elif boutique_exchange2_button is not None and boutique_exchange2_button.collidepoint(mouse_pos):
                            # Échange 2: 1 couronne → 500 pacoins
                            if crown_poche >= 1:
                                crown_poche -= 1
                                jeton_poche += 500
                                # Sauvegarder
                                if current_account_index is not None:
                                    auto_save_account_data(current_account_index, pouvoir_items, gadget_items, objet_items, capacite_items, inventaire_items, jeton_poche, crown_poche, bon_marche_ameliore, battle_pass_xp, battle_pass_claimed_rewards, gemme_poche, used_stars, accounts, battle_pass_plus_claimed_rewards, used_stars_plus, pass_plus_purchased)
                        elif boutique_exchange3_button is not None and boutique_exchange3_button.collidepoint(mouse_pos):
                            # Échange 3: 10 gemmes → 10 couronnes
                            if gemme_poche >= 10:
                                gemme_poche -= 10
                                crown_poche += 10
                                # Sauvegarder
                                if current_account_index is not None:
                                    auto_save_account_data(current_account_index, pouvoir_items, gadget_items, objet_items, capacite_items, inventaire_items, jeton_poche, crown_poche, bon_marche_ameliore, battle_pass_xp, battle_pass_claimed_rewards, gemme_poche, used_stars, accounts, battle_pass_plus_claimed_rewards, used_stars_plus, pass_plus_purchased)
                    elif current_state == VENTE:
                        # Calculer les rectangles des items pour détecter les clics
                        # (même calcul que dans draw_vente, mais sans dessiner)
                        vente_retour_button = pygame.Rect(10, 10, 100, 40)
                        
                        # Calculer la réduction selon le niveau de "bon marché"
                        bon_marche_level = capacite_items.count("bon marché") if capacite_items else 0
                        price_reduction = bon_marche_level * 5
                        if bon_marche_ameliore and bon_marche_level > 0:
                            price_reduction *= 2
                        
                        # Définir les prix de vente de base (50% du prix d'achat)
                        base_vente_sell_prices = {
                            'longue vue': (500, 0),  # 50% de 1000
                            'double longue vue': (2000, 0),  # 50% de 4000
                            'bon repas': (1000, 0),  # 50% de 2000
                            'bon goût': (1500, 0),  # 50% de 3000
                            'pas d\'indigestion': (2500, 0),  # 50% de 5000
                            'glace': (1500, 50),  # 50% de 3000 pacoins et 100 couronnes
                            'skin bleu': (5000, 500),  # 50% de 10000 pacoins et 1000 couronnes
                            'skin orange': (5000, 500),  # 50% de 10000 pacoins et 1000 couronnes
                            'skin rose': (5000, 500),  # 50% de 10000 pacoins et 1000 couronnes
                            'skin rouge': (5000, 500),  # 50% de 10000 pacoins et 1000 couronnes
                            'bon marché': (2500, 0),  # 50% de 5000
                            'lave': (2500, 0),  # 50% de 5000
                            'feu': (2500, 0),  # 50% de 5000
                            'explosion': (5000, 0),  # 50% de 10000
                            'tir': (500, 0),  # 50% de 1000
                            'vision x': (5000, 0),  # 50% de 10000
                            'mort': (7500, 0),  # 50% de 15000
                            'bombe téléguidée': (10000, 0),  # 50% de 20000
                            'piège': (2500, 0),  # 50% de 5000
                            'tp': (1500, 0),  # 50% de 3000
                            'portail': (2000, 0),  # 50% de 4000
                            'mur': (1250, 0),  # 50% de 2500
                            'pièce mythique': (5000, 25),  # 50% de 10000 pacoins et 50 couronnes
                            'grosse armure': (250, 0),  # 50% de 500
                            'armure de fer': (250, 0),  # 50% de 500
                            'flamme': (1000, 0),  # 50% de 2000
                            'givre': (1500, 0),  # 50% de 3000
                            'infra rouge': (2000, 0),  # 50% de 4000
                            'bric': (2500, 0),  # 50% de 5000
                            'coffre fort': (5000, 0),  # 50% de 10000
                            'coffre au trésor': (7500, 0),  # 50% de 15000
                            'gadget': (5000, 500),  # 50% de 10000 pacoins et 1000 couronnes
                            'double gadget': (4000, 0),  # Prix de vente fixe de 4000 pacoins
                            'pacgum': (2000, 0),  # 50% de 4000
                            'indigestion': (1750, 0),  # 50% de 3500
                            'gel': (2500, 0),  # 50% de 5000
                            'lunette': (5000, 5000),  # 50% de 10000 pacoins et 10000 couronnes
                            'invincibilité': (2500, 0),  # 50% de 5000
                            'piquant': (2500, 0),  # 50% de 5000
                            'bonne vue': (2500, 0),  # 50% de 5000
                            'bonbe': (2500, 0),  # 50% de 5000
                        }
                        
                        # Appliquer la réduction de prix aux prix de vente
                        vente_sell_prices = {}
                        for item_type, (base_pacoins, base_crowns) in base_vente_sell_prices.items():
                            reduction_sell = price_reduction // 2  # Diviser par 2 car on vend à 50% du prix d'achat
                            reduced_pacoins = max(0, base_pacoins - reduction_sell)
                            vente_sell_prices[item_type] = (reduced_pacoins, base_crowns)
                        
                        # Calculer les rectangles des items (même logique que draw_vente)
                        start_y = 220
                        item_height = 35  # Même valeur que dans draw_vente
                        item_spacing = 3  # Même valeur que dans draw_vente
                        items_per_column = 12  # Même valeur que dans draw_vente
                        column_width = WINDOW_WIDTH // 2 - 20
                        column_x1 = 20
                        column_x2 = WINDOW_WIDTH // 2 + 10
                        items_list = list(inventaire_items.items())
                        vente_item_rects = {}
                        
                        for idx, (slot_name, item_data) in enumerate(items_list):
                            if idx < items_per_column:
                                x_pos = column_x1
                                y_pos = start_y + idx * (item_height + item_spacing) - vente_scroll_offset
                            else:
                                x_pos = column_x2
                                y_pos = start_y + (idx - items_per_column) * (item_height + item_spacing) - vente_scroll_offset
                            item_rect = pygame.Rect(x_pos, y_pos, column_width - 40, item_height)
                            vente_item_rects[slot_name] = item_rect
                        
                        # Vérifier si on clique sur le bouton retour
                        if vente_retour_button.collidepoint(mouse_pos):
                            current_state = MENU
                            vente_scroll_offset = 0  # Réinitialiser le défilement quand on quitte
                        # Vérifier si on clique sur un item pour le vendre
                        else:
                            for slot_name, item_rect in vente_item_rects.items():
                                if item_rect.collidepoint(mouse_pos):
                                    # Vendre l'item
                                    if slot_name in inventaire_items:
                                        item_data = inventaire_items[slot_name]
                                        item_type = item_data.get('type', '')
                                        
                                        # Obtenir le prix de vente
                                        if item_type in vente_sell_prices:
                                            pacoins_price, crowns_price = vente_sell_prices[item_type]
                                            
                                            # Ajouter les pacoins et couronnes
                                            jeton_poche += pacoins_price
                                            crown_poche += crowns_price
                                            
                                            # Retirer l'item de l'inventaire
                                            del inventaire_items[slot_name]
                                            
                                            # Retirer l'item de la liste des items achetés
                                            if item_type in pouvoir_items:
                                                pouvoir_items.remove(item_type)
                                            elif item_type in gadget_items:
                                                gadget_items.remove(item_type)
                                            elif item_type in capacite_items:
                                                capacite_items.remove(item_type)
                                            elif item_type in objet_items:
                                                objet_items.remove(item_type)
                                            
                                            # Sortir de la boucle après avoir vendu l'item
                                            break
                    elif current_state == INVENTAIRE:
                        # Vérifier si on clique sur le bouton commencer
                        if inventaire_before_game and inventaire_start_button is not None and inventaire_start_button.collidepoint(mouse_pos):
                            # Démarrer la partie avec la difficulté choisie (ou facile par défaut)
                            if difficulty is None:
                                difficulty = "facile"  # Par défaut facile si aucune difficulté choisie
                            
                            (maze, pacman, ghosts, score, lives, last_bonus_score, game_over, won,
                             ice_tiles, pacman_last_pos, vulnerable_timer, level_transition, level_transition_timer,
                             respawn_timer, invincibility_timer, crown_timer, crown_count, jeton_count, last_ghost_time,
                             fire_tiles, fire_active, fire_timer, gadget_cooldown, mort_cooldown, bombe_cooldown,
                             bombe_active, pieges, portal1_pos, portal2_pos, portal_use_count, mur_pos, mur_use_count,
                             gadget_use_count, has_indigestion, indigestion_timer) = start_game_with_difficulty(
                                difficulty, inventaire_items, capacite_items, invincibilite_bonus, ghosts)
                            
                            is_adventure_mode = False  # Désactiver le mode aventure pour le jeu normal
                            
                            if difficulty == "facile":
                                level = 1
                            elif difficulty == "moyen":
                                level = 3
                            elif difficulty == "difficile":
                                level = 1
                            elif difficulty == "hardcore":
                                level = 5
                            else:
                                level = 1
                            
                            game_needs_reset = False
                            if not game_initialized:
                                game_initialized = True
                            current_state = GAME
                            inventaire_before_game = False  # Réinitialiser la variable
                            item_description = None  # Effacer la description
                            # Démarrer la musique de fond si elle n'est pas déjà en cours
                            if not music_playing:
                                try:
                                    # Essayer de charger différents formats de fichiers audio
                                    music_files = ["pacman_music.mp3", "pacman_music.ogg", "pacman_music.wav"]
                                    music_loaded = False
                                    for music_file in music_files:
                                        try:
                                            pygame.mixer.music.load(music_file)
                                            pygame.mixer.music.play(-1)  # -1 = boucle infinie
                                            music_playing = True
                                            music_loaded = True
                                            break
                                        except pygame.error:
                                            continue
                                    if not music_loaded:
                                        # Si aucun fichier n'est trouvé, créer une musique simple avec des bips
                                        # Note: pygame.mixer.music ne peut pas créer de musique synthétisée
                                        # On laisse music_playing à False si aucun fichier n'est trouvé
                                        pass
                                except Exception:
                                    # Si une erreur survient, continuer sans musique
                                    pass
                        # Vérifier si on clique sur le bouton retour
                        elif inventaire_retour_button is not None and inventaire_retour_button.collidepoint(mouse_pos):
                            current_state = MENU
                            inventaire_before_game = False  # Réinitialiser la variable
                            item_description = None  # Effacer la description quand on retourne au menu
                            # Arrêter la musique si elle est en cours
                            if music_playing:
                                pygame.mixer.music.stop()
                                music_playing = False
                        # Vérifier si on clique sur un slot pour sélectionner un item
                        elif inventaire_slots is not None:
                            # Si on clique gauche ailleurs (pas sur un slot), effacer la description
                            clicked_on_slot = False
                            for slot_name, slot_rect in inventaire_slots.items():
                                if slot_name != 'retour' and slot_name != 'commencer' and slot_rect.collidepoint(mouse_pos):
                                    clicked_on_slot = True
                                    # Si on clique sur un slot qui contient un item, le sélectionner ou désélectionner
                                    if slot_name in inventaire_items:
                                        # Si l'item est déjà sélectionné et qu'on reclique dessus, annuler la sélection
                                        if selected_item is not None and selected_item[0] == slot_name:
                                            selected_item = None
                                        else:
                                            selected_item = (slot_name, inventaire_items[slot_name])
                                    # Si on a un item sélectionné et qu'on clique sur un slot vide, le déplacer
                                    elif selected_item is not None:
                                        old_slot, item_data = selected_item
                                        # Vérifier si c'est la longue vue, double longue vue, bon repas, bon goût, pas d'indigestion, skin bleu, skin orange, skin rose ou skin rouge et si le slot de destination est valide
                                        if item_data.get('type') == 'longue vue' or item_data.get('type') == 'double longue vue' or item_data.get('type') == 'bon repas' or item_data.get('type') == 'bon goût' or item_data.get('type') == 'pas d\'indigestion' or item_data.get('type') == 'skin bleu' or item_data.get('type') == 'skin orange' or item_data.get('type') == 'skin rose' or item_data.get('type') == 'skin rouge':
                                            # La longue vue, double longue vue, bon repas, bon goût, pas d'indigestion ne peuvent aller que dans le cadrillage (grid_*) ou le slot pouvoir
                                            if slot_name.startswith('grid_') or slot_name == 'pouvoir':
                                                inventaire_items[slot_name] = item_data
                                                if old_slot in inventaire_items:
                                                    del inventaire_items[old_slot]
                                                selected_item = None
                                            # Sinon, ne pas déplacer (rester sélectionné)
                                        elif item_data.get('type') == 'bon marché':
                                            # "bon marché" ne peut aller QUE dans le cadrillage (grid_*), PAS dans les slots capacité
                                            if slot_name.startswith('grid_'):
                                                inventaire_items[slot_name] = item_data
                                                if old_slot in inventaire_items:
                                                    del inventaire_items[old_slot]
                                                selected_item = None
                                            # Sinon, ne pas déplacer (rester sélectionné)
                                        elif item_data.get('type') == 'gadget' or item_data.get('type') == 'pacgum' or item_data.get('type') == 'indigestion' or item_data.get('type') == 'gel' or item_data.get('type') == 'lunette' or item_data.get('type') == 'invincibilité' or item_data.get('type') == 'piquant' or item_data.get('type') == 'bonne vue' or item_data.get('type') == 'bonbe':
                                            # "gadget", "pacgum", "indigestion", "gel" et "lunette" peuvent aller dans le cadrillage (grid_*) ou les slots capacité (capacite1, capacite2)
                                            if slot_name.startswith('grid_') or slot_name == 'capacite1' or slot_name == 'capacite2':
                                                inventaire_items[slot_name] = item_data
                                                if old_slot in inventaire_items:
                                                    del inventaire_items[old_slot]
                                                selected_item = None
                                            # Sinon, ne pas déplacer (rester sélectionné)
                                        elif item_data.get('type') in gadget_items:
                                            # Les gadgets peuvent aller dans le slot gadget ou dans la grille d'inventaire
                                            if slot_name == 'gadget' or slot_name.startswith('grid_'):
                                                inventaire_items[slot_name] = item_data
                                                if old_slot in inventaire_items:
                                                    del inventaire_items[old_slot]
                                                selected_item = None
                                            # Sinon, ne pas déplacer (rester sélectionné)
                                        elif item_data.get('type') == 'lave':
                                            # "lave" peut aller dans le slot gadget ou dans la grille d'inventaire (même s'il est dans objet_items)
                                            if slot_name == 'gadget' or slot_name.startswith('grid_'):
                                                inventaire_items[slot_name] = item_data
                                                if old_slot in inventaire_items:
                                                    del inventaire_items[old_slot]
                                                selected_item = None
                                            # Sinon, ne pas déplacer (rester sélectionné)
                                        elif item_data.get('type') == 'pièce mythique':
                                            # La pièce mythique peut aller dans les slots objet (objet0, objet1, objet2) ou dans la grille d'inventaire
                                            if slot_name == 'objet0' or slot_name == 'objet1' or slot_name == 'objet2' or slot_name.startswith('grid_'):
                                                inventaire_items[slot_name] = item_data
                                                if old_slot in inventaire_items:
                                                    del inventaire_items[old_slot]
                                                selected_item = None
                                            # Sinon, ne pas déplacer (rester sélectionné)
                                        elif item_data.get('type') == 'grosse armure':
                                            # La grosse armure peut aller dans les slots objet (objet0, objet1, objet2) ou dans la grille d'inventaire
                                            if slot_name == 'objet0' or slot_name == 'objet1' or slot_name == 'objet2' or slot_name.startswith('grid_'):
                                                inventaire_items[slot_name] = item_data
                                                if old_slot in inventaire_items:
                                                    del inventaire_items[old_slot]
                                                selected_item = None
                                            # Sinon, ne pas déplacer (rester sélectionné)
                                        elif item_data.get('type') == 'armure de fer':
                                            # L'armure de fer peut aller dans les slots objet (objet0, objet1, objet2) ou dans la grille d'inventaire
                                            if slot_name == 'objet0' or slot_name == 'objet1' or slot_name == 'objet2' or slot_name.startswith('grid_'):
                                                inventaire_items[slot_name] = item_data
                                                if old_slot in inventaire_items:
                                                    del inventaire_items[old_slot]
                                                selected_item = None
                                            # Sinon, ne pas déplacer (rester sélectionné)
                                        elif item_data.get('type') == 'flamme':
                                            # La flamme peut aller dans les slots objet (objet0, objet1, objet2) ou dans la grille d'inventaire
                                            if slot_name == 'objet0' or slot_name == 'objet1' or slot_name == 'objet2' or slot_name.startswith('grid_'):
                                                inventaire_items[slot_name] = item_data
                                                if old_slot in inventaire_items:
                                                    del inventaire_items[old_slot]
                                                selected_item = None
                                            # Sinon, ne pas déplacer (rester sélectionné)
                                        elif item_data.get('type') == 'givre':
                                            # Le givre peut aller dans les slots objet (objet0, objet1, objet2) ou dans la grille d'inventaire
                                            if slot_name == 'objet0' or slot_name == 'objet1' or slot_name == 'objet2' or slot_name.startswith('grid_'):
                                                inventaire_items[slot_name] = item_data
                                                if old_slot in inventaire_items:
                                                    del inventaire_items[old_slot]
                                                selected_item = None
                                            # Sinon, ne pas déplacer (rester sélectionné)
                                        elif item_data.get('type') == 'infra rouge':
                                            # L'infra rouge peut aller dans les slots objet (objet0, objet1, objet2) ou dans la grille d'inventaire
                                            if slot_name == 'objet0' or slot_name == 'objet1' or slot_name == 'objet2' or slot_name.startswith('grid_'):
                                                inventaire_items[slot_name] = item_data
                                                if old_slot in inventaire_items:
                                                    del inventaire_items[old_slot]
                                                selected_item = None
                                            # Sinon, ne pas déplacer (rester sélectionné)
                                        elif item_data.get('type') == 'bric':
                                            # Le bric peut aller dans les slots objet (objet0, objet1, objet2) ou dans la grille d'inventaire
                                            if slot_name == 'objet0' or slot_name == 'objet1' or slot_name == 'objet2' or slot_name.startswith('grid_'):
                                                inventaire_items[slot_name] = item_data
                                                if old_slot in inventaire_items:
                                                    del inventaire_items[old_slot]
                                                selected_item = None
                                            # Sinon, ne pas déplacer (rester sélectionné)
                                        elif item_data.get('type') == 'coffre fort':
                                            # Le coffre fort peut aller dans les slots objet (objet0, objet1, objet2) ou dans la grille d'inventaire
                                            if slot_name == 'objet0' or slot_name == 'objet1' or slot_name == 'objet2' or slot_name.startswith('grid_'):
                                                inventaire_items[slot_name] = item_data
                                                if old_slot in inventaire_items:
                                                    del inventaire_items[old_slot]
                                                selected_item = None
                                            # Sinon, ne pas déplacer (rester sélectionné)
                                        elif item_data.get('type') == 'coffre au trésor':
                                            # Le coffre au trésor peut aller dans les slots objet (objet0, objet1, objet2) ou dans la grille d'inventaire
                                            if slot_name == 'objet0' or slot_name == 'objet1' or slot_name == 'objet2' or slot_name.startswith('grid_'):
                                                inventaire_items[slot_name] = item_data
                                                if old_slot in inventaire_items:
                                                    del inventaire_items[old_slot]
                                                selected_item = None
                                            # Sinon, ne pas déplacer (rester sélectionné)
                                        elif item_data.get('type') == 'double gadget':
                                            # Le double gadget peut aller dans les slots objet (objet0, objet1, objet2) ou dans la grille d'inventaire
                                            if slot_name == 'objet0' or slot_name == 'objet1' or slot_name == 'objet2' or slot_name.startswith('grid_'):
                                                inventaire_items[slot_name] = item_data
                                                if old_slot in inventaire_items:
                                                    del inventaire_items[old_slot]
                                                selected_item = None
                                            # Sinon, ne pas déplacer (rester sélectionné)
                                        else:
                                            # Pour les autres items, permettre le déplacement normal
                                            inventaire_items[slot_name] = item_data
                                            if old_slot in inventaire_items:
                                                del inventaire_items[old_slot]
                                            selected_item = None
                                    break
                            # Si on clique gauche ailleurs (pas sur un slot), effacer la description
                            if not clicked_on_slot:
                                item_description = None
                    elif current_state == GAME:
                        # Bouton retour dans le jeu
                        if game_retour_button is not None and game_retour_button.collidepoint(mouse_pos):
                            # Sauvegarder les données du compte actuel avant de quitter
                            if current_account_index is not None:
                                save_game_data_for_account(current_account_index, pouvoir_items, gadget_items, objet_items, capacite_items, inventaire_items, jeton_poche, crown_poche, bon_marche_ameliore, battle_pass_xp, battle_pass_claimed_rewards, gemme_poche, used_stars, accounts, battle_pass_plus_claimed_rewards, used_stars_plus)
                            game_needs_reset = True  # Marquer que la partie doit être réinitialisée au retour
                            current_state = MENU  # Retourner au menu principal
                            # Arrêter la musique si elle est en cours
                            if music_playing:
                                pygame.mixer.music.stop()
                                music_playing = False
                        else:
                            # Activer le gadget équipé dans le slot "gadget" avec le clic gauche (seulement si le temps de recharge est terminé)
                            equipped_gadget = get_equipped_gadget(inventaire_items)
                            if equipped_gadget:
                                gadget_type = equipped_gadget.get('type')
                                # Vérifier si "double gadget" est équipé
                                has_double_gadget = (('objet0' in inventaire_items and inventaire_items['objet0'].get('type') == 'double gadget') or
                                                    ('objet1' in inventaire_items and inventaire_items['objet1'].get('type') == 'double gadget') or
                                                    ('objet2' in inventaire_items and inventaire_items['objet2'].get('type') == 'double gadget'))
                                # Vérifier le temps de recharge approprié selon le gadget
                                if gadget_type == 'mort':
                                    can_activate = (mort_cooldown == 0)
                                elif gadget_type == 'bombe téléguidée':
                                    can_activate = (bombe_cooldown == 0)
                                else:
                                    can_activate = (gadget_cooldown == 0)
                                
                                if can_activate:
                                    if gadget_type == 'lave' and not fire_active:
                                        # Activer la lave (durée calculée selon si "flamme" est équipé)
                                        fire_active = True
                                        fire_timer = calculate_fire_duration(inventaire_items, FIRE_DURATION)
                                        # Gérer le temps de recharge avec "double gadget" (alternance recharge instantanée/normale)
                                        if has_double_gadget:
                                            gadget_use_count += 1
                                            if gadget_use_count % 2 == 1:  # Utilisation impaire (1, 3, 5...) : recharge instantanée
                                                gadget_cooldown = 0
                                            else:  # Utilisation paire (2, 4, 6...) : recharge normale
                                                gadget_cooldown = GADGET_COOLDOWN_DURATION
                                        else:
                                            gadget_cooldown = GADGET_COOLDOWN_DURATION  # 25 secondes de cooldown
                                    elif gadget_type == 'feu' and not fire_active:
                                        # Activer le feu (durée calculée selon si "flamme" est équipé)
                                        fire_active = True
                                        fire_timer = calculate_fire_duration(inventaire_items, FIRE_DURATION)
                                        # Gérer le temps de recharge avec "double gadget" (alternance recharge instantanée/normale)
                                        if has_double_gadget:
                                            gadget_use_count += 1
                                            if gadget_use_count % 2 == 1:  # Utilisation impaire (1, 3, 5...) : recharge instantanée
                                                gadget_cooldown = 0
                                            else:  # Utilisation paire (2, 4, 6...) : recharge normale
                                                gadget_cooldown = GADGET_COOLDOWN_DURATION
                                        else:
                                            gadget_cooldown = GADGET_COOLDOWN_DURATION  # 25 secondes de cooldown
                                    elif gadget_type == 'explosion':
                                        # Activer l'explosion : tuer tous les fantômes (sans donner de couronnes)
                                        for ghost in ghosts:
                                            # Ne tuer que les fantômes normaux (pas inoffensifs, pas déjà en mode yeux)
                                            if not ghost.harmless and not ghost.eyes:
                                                # Tuer le fantôme (le transformer en yeux)
                                                ghost.eyes = True
                                                ghost.vulnerable = False
                                                ghost.returning = False
                                                # Ajouter des points mais pas de couronnes
                                                score += 300
                                        # Gérer le temps de recharge avec "double gadget" (alternance recharge instantanée/normale)
                                        if has_double_gadget:
                                            gadget_use_count += 1
                                            if gadget_use_count % 2 == 1:  # Utilisation impaire (1, 3, 5...) : recharge instantanée
                                                gadget_cooldown = 0
                                            else:  # Utilisation paire (2, 4, 6...) : recharge normale
                                                gadget_cooldown = GADGET_COOLDOWN_DURATION
                                        else:
                                            gadget_cooldown = GADGET_COOLDOWN_DURATION  # 25 secondes de cooldown
                                    elif gadget_type == 'tir':
                                        # Activer le tir : tuer un fantôme dans le champ de vision (direction de Pacman)
                                        # Déterminer la direction de Pacman
                                        if pacman.direction != (0, 0):
                                            # Calculer les positions dans le champ de vision (ligne droite dans la direction de Pacman)
                                            target_positions = []
                                            dx, dy = pacman.direction
                                            # Chercher jusqu'à 5 cases dans la direction
                                            for i in range(1, 6):
                                                check_x = pacman.x + i * dx
                                                check_y = pacman.y + i * dy
                                                # Gérer la téléportation aux bords
                                                if check_x < 0:
                                                    check_x = GRID_WIDTH - 1
                                                elif check_x >= GRID_WIDTH:
                                                    check_x = 0
                                                if check_y < 0:
                                                    check_y = GRID_HEIGHT - 1
                                                elif check_y >= GRID_HEIGHT:
                                                    check_y = 0
                                                # Vérifier si c'est un mur, si oui arrêter
                                                if 0 <= check_y < GRID_HEIGHT and 0 <= check_x < GRID_WIDTH:
                                                    if maze[check_y][check_x] == 1:  # Mur
                                                        break
                                                    target_positions.append((check_x, check_y))
                                            
                                            # Trouver le fantôme le plus proche dans le champ de vision
                                            target_ghost = None
                                            min_distance = float('inf')
                                            for ghost in ghosts:
                                                # Ne tuer que les fantômes normaux (pas inoffensifs, pas déjà en mode yeux, pas orange, pas rose)
                                                ORANGE = (255, 165, 0)
                                                ROSE = (255, 192, 203)
                                                if not ghost.harmless and not ghost.eyes and ghost.color != ORANGE and ghost.color != ROSE:
                                                    if (ghost.x, ghost.y) in target_positions:
                                                        # Calculer la distance de Manhattan
                                                        distance = abs(ghost.x - pacman.x) + abs(ghost.y - pacman.y)
                                                        if distance < min_distance:
                                                            min_distance = distance
                                                            target_ghost = ghost
                                            
                                            # Tuer le fantôme ciblé
                                            if target_ghost is not None:
                                                target_ghost.eyes = True
                                                target_ghost.vulnerable = False
                                                target_ghost.returning = False
                                                # Ajouter des points mais pas de couronnes
                                                score += 300
                                        
                                        # Gérer le temps de recharge avec "double gadget" (alternance recharge instantanée/normale)
                                        if has_double_gadget:
                                            gadget_use_count += 1
                                            if gadget_use_count % 2 == 1:  # Utilisation impaire (1, 3, 5...) : recharge instantanée
                                                gadget_cooldown = 0
                                            else:  # Utilisation paire (2, 4, 6...) : recharge normale
                                                gadget_cooldown = GADGET_COOLDOWN_DURATION
                                        else:
                                            gadget_cooldown = GADGET_COOLDOWN_DURATION  # 25 secondes de cooldown
                                    elif gadget_type == 'vision x':
                                        # Vérifier si l'objet "Vision X" est équipé dans un slot objet
                                        has_vision_x_objet = (('objet0' in inventaire_items and inventaire_items['objet0'].get('type') == 'vision x') or
                                                             ('objet1' in inventaire_items and inventaire_items['objet1'].get('type') == 'vision x') or
                                                             ('objet2' in inventaire_items and inventaire_items['objet2'].get('type') == 'vision x'))
                                        # Activer Vision X si l'objet Vision X est équipé (ou si c'est le gadget vision x directement)
                                        if has_vision_x_objet or gadget_type == 'vision x':
                                            # Activer Vision X : faire disparaître tous les fantômes d'indigestion
                                            ghosts[:] = [ghost for ghost in ghosts if not ghost.harmless]
                                            # Calculer le bonus de "bonne vue" si équipé
                                            has_bon_vue_capacity = (('capacite1' in inventaire_items and inventaire_items['capacite1'].get('type') == 'bonne vue') or
                                                                   ('capacite2' in inventaire_items and inventaire_items['capacite2'].get('type') == 'bonne vue'))
                                            bon_vue_level = capacite_items.count("bonne vue") if capacite_items else 0
                                            cooldown_reduction = bon_vue_level * 25 if has_bon_vue_capacity else 0  # Réduction de 2.5 secondes par niveau (25 frames à 10 FPS)
                                            # Calculer le bonus de "infra rouge" si équipé
                                            has_infra_rouge = (('objet0' in inventaire_items and inventaire_items['objet0'].get('type') == 'infra rouge') or
                                                               ('objet1' in inventaire_items and inventaire_items['objet1'].get('type') == 'infra rouge') or
                                                               ('objet2' in inventaire_items and inventaire_items['objet2'].get('type') == 'infra rouge'))
                                            if has_infra_rouge:
                                                cooldown_reduction += 50  # Réduction supplémentaire de 5 secondes (50 frames à 10 FPS)
                                            # Gérer le temps de recharge avec "double gadget" (alternance recharge instantanée/normale)
                                            if has_double_gadget:
                                                gadget_use_count += 1
                                                if gadget_use_count % 2 == 1:  # Utilisation impaire (1, 3, 5...) : recharge instantanée
                                                    gadget_cooldown = 0
                                                else:  # Utilisation paire (2, 4, 6...) : recharge normale avec réductions
                                                    gadget_cooldown = max(0, GADGET_COOLDOWN_DURATION - cooldown_reduction)
                                            else:
                                                gadget_cooldown = max(0, GADGET_COOLDOWN_DURATION - cooldown_reduction)  # Cooldown réduit
                                    elif gadget_type == 'mort':
                                        # Activer Mort : tuer définitivement le fantôme le plus proche de Pacman (peu importe la direction)
                                        # Trouver le fantôme le plus proche de Pacman
                                        target_ghost = None
                                        min_distance = float('inf')
                                        for ghost in ghosts:
                                            # Ne tuer que les fantômes normaux (pas inoffensifs, pas déjà en mode yeux)
                                            if not ghost.harmless and not ghost.eyes:
                                                # Calculer la distance de Manhattan entre Pacman et le fantôme
                                                distance = abs(ghost.x - pacman.x) + abs(ghost.y - pacman.y)
                                                if distance < min_distance:
                                                    min_distance = distance
                                                    target_ghost = ghost
                                        
                                        # Tuer définitivement le fantôme ciblé (le retirer de la liste)
                                        if target_ghost is not None:
                                            # En mode aventure, supprimer le fantôme définitivement (pas de réapparition)
                                            ghosts.remove(target_ghost)
                                            # Ajouter des points mais pas de couronnes
                                            score += 300
                                        
                                        # Gérer le temps de recharge avec "double gadget" (alternance recharge instantanée/normale)
                                        if has_double_gadget:
                                            gadget_use_count += 1
                                            if gadget_use_count % 2 == 1:  # Utilisation impaire (1, 3, 5...) : recharge instantanée
                                                mort_cooldown = 0
                                            else:  # Utilisation paire (2, 4, 6...) : recharge normale
                                                mort_cooldown = MORT_COOLDOWN_DURATION
                                        else:
                                            mort_cooldown = MORT_COOLDOWN_DURATION  # 1 minute de cooldown
                                    elif gadget_type == 'bombe téléguidée' and not bombe_active:
                                        # Activer la bombe téléguidée : arrêter Pacman et créer une bombe
                                        bombe_active = True
                                        bombe_x = pacman.x
                                        bombe_y = pacman.y
                                        bombe_timer = BOMBE_EXPLOSION_DELAY  # 10 secondes
                                        pacman_frozen = True  # Geler Pacman
                                        # Arrêter Pacman
                                        pacman.direction = (0, 0)
                                        pacman.next_direction = (0, 0)
                                        # Gérer le temps de recharge avec "double gadget" (alternance recharge instantanée/normale)
                                        if has_double_gadget:
                                            gadget_use_count += 1
                                            if gadget_use_count % 2 == 1:  # Utilisation impaire (1, 3, 5...) : recharge instantanée
                                                bombe_cooldown = 0
                                            else:  # Utilisation paire (2, 4, 6...) : recharge normale
                                                bombe_cooldown = BOMBE_COOLDOWN_DURATION
                                        else:
                                            bombe_cooldown = BOMBE_COOLDOWN_DURATION  # 1 minute de cooldown
                                    elif gadget_type == 'piège':
                                        # Activer le piège : poser un piège à la position de Pacman
                                        # Vérifier que la position n'est pas un mur
                                        if 0 <= pacman.y < GRID_HEIGHT and 0 <= pacman.x < GRID_WIDTH:
                                            if maze[pacman.y][pacman.x] != 1:  # Pas un mur
                                                # Poser le piège à la position de Pacman
                                                pieges[(pacman.x, pacman.y)] = True
                                                # Gérer le temps de recharge avec "double gadget" (alternance recharge instantanée/normale)
                                                if has_double_gadget:
                                                    gadget_use_count += 1
                                                    if gadget_use_count % 2 == 1:  # Utilisation impaire (1, 3, 5...) : recharge instantanée
                                                        gadget_cooldown = 0
                                                    else:  # Utilisation paire (2, 4, 6...) : recharge normale
                                                        gadget_cooldown = GADGET_COOLDOWN_DURATION
                                                else:
                                                    gadget_cooldown = GADGET_COOLDOWN_DURATION  # 25 secondes de cooldown
                                    elif gadget_type == 'tp':
                                        # Activer TP : téléporter Pacman à la position de la souris (sauf si c'est un mur)
                                        # Convertir la position de la souris en coordonnées de grille
                                        grid_x = mouse_pos[0] // CELL_SIZE
                                        grid_y = mouse_pos[1] // CELL_SIZE
                                        
                                        # Vérifier que la position est valide et que ce n'est pas un mur
                                        if 0 <= grid_y < GRID_HEIGHT and 0 <= grid_x < GRID_WIDTH:
                                            if maze[grid_y][grid_x] != 1:  # Pas un mur
                                                # Téléporter Pacman à cette position
                                                pacman.x = grid_x
                                                pacman.y = grid_y
                                                # Gérer le temps de recharge avec "double gadget" (alternance recharge instantanée/normale)
                                                if has_double_gadget:
                                                    gadget_use_count += 1
                                                    if gadget_use_count % 2 == 1:  # Utilisation impaire (1, 3, 5...) : recharge instantanée
                                                        gadget_cooldown = 0
                                                    else:  # Utilisation paire (2, 4, 6...) : recharge normale
                                                        gadget_cooldown = GADGET_COOLDOWN_DURATION
                                                else:
                                                    gadget_cooldown = GADGET_COOLDOWN_DURATION  # 25 secondes de cooldown
                                    elif gadget_type == 'portail':
                                        # Activer Portail : cycle de 3 utilisations
                                        # Vérifier que la position de Pacman n'est pas un mur
                                        if 0 <= pacman.y < GRID_HEIGHT and 0 <= pacman.x < GRID_WIDTH:
                                            if maze[pacman.y][pacman.x] != 1:  # Pas un mur
                                                if portal_use_count == 0:
                                                    # 1ère utilisation : poser le premier portail
                                                    portal1_pos = (pacman.x, pacman.y)
                                                    portal_use_count = 1
                                                elif portal_use_count == 1:
                                                    # 2ème utilisation : poser le deuxième portail
                                                    portal2_pos = (pacman.x, pacman.y)
                                                    portal_use_count = 2
                                                elif portal_use_count == 2:
                                                    # 3ème utilisation : enlever les portails
                                                    portal1_pos = None
                                                    portal2_pos = None
                                                    portal_use_count = 0
                                                # Gérer le temps de recharge avec "double gadget" (alternance recharge instantanée/normale)
                                                if has_double_gadget:
                                                    gadget_use_count += 1
                                                    if gadget_use_count % 2 == 1:  # Utilisation impaire (1, 3, 5...) : recharge instantanée
                                                        gadget_cooldown = 0
                                                    else:  # Utilisation paire (2, 4, 6...) : recharge normale
                                                        gadget_cooldown = GADGET_COOLDOWN_DURATION
                                                else:
                                                    gadget_cooldown = GADGET_COOLDOWN_DURATION  # 25 secondes de cooldown
                                    elif gadget_type == 'mur':
                                        # Vérifier si "bric" est équipé
                                        has_bric = (('objet0' in inventaire_items and inventaire_items['objet0'].get('type') == 'bric') or
                                                   ('objet1' in inventaire_items and inventaire_items['objet1'].get('type') == 'bric') or
                                                   ('objet2' in inventaire_items and inventaire_items['objet2'].get('type') == 'bric'))
                                        
                                        # Vérifier que la position de Pacman est valide
                                        if 0 <= pacman.y < GRID_HEIGHT and 0 <= pacman.x < GRID_WIDTH:
                                            if has_bric:
                                                # Cycle de 3 utilisations avec "bric"
                                                if mur_use_count == 0:
                                                    # 1ère utilisation : créer un mur (si ce n'est pas déjà un mur)
                                                    if maze[pacman.y][pacman.x] != 1:  # Pas déjà un mur
                                                        maze[pacman.y][pacman.x] = 1  # Créer le mur
                                                        # Convertir mur_pos en liste si nécessaire
                                                        if mur_pos is None:
                                                            mur_pos = []
                                                        elif isinstance(mur_pos, tuple):
                                                            mur_pos = [mur_pos]
                                                        mur_pos.append((pacman.x, pacman.y))
                                                        mur_use_count = 1
                                                elif mur_use_count == 1:
                                                    # 2ème utilisation : créer un deuxième mur (si ce n'est pas déjà un mur)
                                                    if maze[pacman.y][pacman.x] != 1:  # Pas déjà un mur
                                                        maze[pacman.y][pacman.x] = 1  # Créer le mur
                                                        if isinstance(mur_pos, tuple):
                                                            mur_pos = [mur_pos]
                                                        elif mur_pos is None:
                                                            mur_pos = []
                                                        mur_pos.append((pacman.x, pacman.y))
                                                        mur_use_count = 2
                                                elif mur_use_count == 2:
                                                    # 3ème utilisation : enlever tous les murs créés
                                                    if isinstance(mur_pos, list):
                                                        for mur_x, mur_y in mur_pos:
                                                            if 0 <= mur_y < GRID_HEIGHT and 0 <= mur_x < GRID_WIDTH:
                                                                maze[mur_y][mur_x] = 0  # Enlever le mur (remettre en chemin)
                                                    elif isinstance(mur_pos, tuple):
                                                        mur_x, mur_y = mur_pos
                                                        if 0 <= mur_y < GRID_HEIGHT and 0 <= mur_x < GRID_WIDTH:
                                                            maze[mur_y][mur_x] = 0  # Enlever le mur (remettre en chemin)
                                                    mur_pos = None
                                                    mur_use_count = 0
                                            else:
                                                # Cycle de 2 utilisations sans "bric" (comportement original)
                                                if mur_use_count == 0:
                                                    # 1ère utilisation : créer un mur (si ce n'est pas déjà un mur)
                                                    if maze[pacman.y][pacman.x] != 1:  # Pas déjà un mur
                                                        maze[pacman.y][pacman.x] = 1  # Créer le mur
                                                        mur_pos = (pacman.x, pacman.y)
                                                        mur_use_count = 1
                                                elif mur_use_count == 1:
                                                    # 2ème utilisation : enlever le mur créé
                                                    if mur_pos is not None:
                                                        if isinstance(mur_pos, list):
                                                            # Si c'est une liste (cas avec bric précédemment), enlever tous les murs
                                                            for mur_x, mur_y in mur_pos:
                                                                if 0 <= mur_y < GRID_HEIGHT and 0 <= mur_x < GRID_WIDTH:
                                                                    maze[mur_y][mur_x] = 0
                                                        else:
                                                            # Si c'est un tuple (comportement normal)
                                                            mur_x, mur_y = mur_pos
                                                            if 0 <= mur_y < GRID_HEIGHT and 0 <= mur_x < GRID_WIDTH:
                                                                maze[mur_y][mur_x] = 0  # Enlever le mur (remettre en chemin)
                                                        mur_pos = None
                                                        mur_use_count = 0
                                            # Gérer le temps de recharge avec "double gadget" (alternance recharge instantanée/normale)
                                            if has_double_gadget:
                                                gadget_use_count += 1
                                                if gadget_use_count % 2 == 1:  # Utilisation impaire (1, 3, 5...) : recharge instantanée
                                                    gadget_cooldown = 0
                                                else:  # Utilisation paire (2, 4, 6...) : recharge normale
                                                    gadget_cooldown = GADGET_COOLDOWN_DURATION
                                            else:
                                                gadget_cooldown = GADGET_COOLDOWN_DURATION  # 25 secondes de cooldown
                elif event.button == 3:  # Clic droit
                    if current_state == GAME:
                        # Redémarrer le jeu ou continuer après perte de vie avec le clic droit
                        if game_over or won:
                            # Donner 10 XP minimum si aucun fantôme n'a été tué
                            if vulnerable_ghosts_eaten_this_game == 0:
                                xp_gained = 10
                                # Si le doubleur d'XP est actif, doubler l'XP
                                if xp_doubler_active:
                                    xp_gained *= 2
                                # S'assurer que battle_pass_xp est un entier
                                if not isinstance(battle_pass_xp, (int, float)):
                                    battle_pass_xp = 0
                                # Calculer le nouveau XP
                                new_xp = int(battle_pass_xp) + xp_gained
                                # Limiter l'XP au niveau 30 si toutes les récompenses ne sont pas récupérées
                                MAX_BATTLE_PASS_LEVEL = 30
                                XP_PER_LEVEL = 100
                                MAX_BATTLE_PASS_XP = MAX_BATTLE_PASS_LEVEL * XP_PER_LEVEL
                                if new_xp >= MAX_BATTLE_PASS_XP:
                                    # Vérifier si toutes les récompenses ont été récupérées
                                    if not all_battle_pass_rewards_claimed(battle_pass_claimed_rewards, used_stars, MAX_BATTLE_PASS_LEVEL):
                                        # Bloquer l'XP au maximum du niveau 30
                                        new_xp = MAX_BATTLE_PASS_XP
                                battle_pass_xp = new_xp
                                # Sauvegarder l'XP gagné
                                if current_account_index is not None:
                                    auto_save_account_data(current_account_index, pouvoir_items, gadget_items, objet_items, capacite_items, inventaire_items, jeton_poche, crown_poche, bon_marche_ameliore, battle_pass_xp, battle_pass_claimed_rewards, gemme_poche, used_stars, accounts, battle_pass_plus_claimed_rewards, used_stars_plus, pass_plus_purchased)
                            
                            # Utiliser un doubleur d'XP si disponible
                            if xp_doublers_count > 0:
                                xp_doubler_active = True
                                xp_doublers_count -= 1
                            else:
                                xp_doubler_active = False
                            vulnerable_ghosts_eaten_this_game = 0  # Réinitialiser le compteur
                            
                            # Redémarrer le jeu complètement
                            maze = [row[:] for row in MAZES[0]]
                            pacman = Pacman(10, 15)
                            ghosts = [
                                Ghost(10, 9, BLUE),
                            ]
                            # Définir le chemin pour tous les fantômes bleus
                            for ghost in ghosts:
                                if ghost.color == BLUE:
                                    ghost.set_path(maze)
                            score = 0
                            level = 1
                            # Initialiser les vies : base 2 + bonus d'armures (grosse armure et armure de fer)
                            armor_lives_bonus_init = calculate_armor_lives_bonus(inventaire_items)
                            lives = 2 + armor_lives_bonus_init
                            last_bonus_score = 0
                            game_over = False
                            won = False
                            crown_count = 0  # Réinitialiser le compteur de couronnes temporaires
                            # Ne pas réinitialiser crown_poche, jeton_poche et grande_couronne_count pour garder la sauvegarde
                            jeton_count = 0  # Réinitialiser le compteur de jetons temporaires
                            game_initialized = True  # Marquer le jeu comme initialisé
                            last_ghost_time = 0  # Réinitialiser le timer depuis le dernier fantôme mangé
                            vulnerable_timer = 0
                            level_transition = False
                            level_transition_timer = 0
                            respawn_timer = 0
                            invincibilite_bonus = calculate_invincibilite_bonus(capacite_items, inventaire_items)
                            invincibility_timer = 30 + invincibilite_bonus  # Réinitialiser l'invincibilité au redémarrage
                            crown_timer = 0  # Réinitialiser la couronne au redémarrage
                            indigestion_timer = 0  # Réinitialiser l'indigestion au redémarrage
                            # Ne pas réinitialiser super_vie_active - elle reste active jusqu'à ce qu'on reclique sur le bouton
                            has_indigestion = False  # Réinitialiser l'état d'indigestion
                            rainbow_timer = 0  # Réinitialiser le timer arc-en-ciel au redémarrage
                            is_rainbow_critique = False  # Réinitialiser l'état arc-en-ciel
                        elif respawn_timer > 0:
                            # Continuer le jeu après perte de vie (réapparition immédiate)
                            respawn_timer = 0
                            pacman, invincibility_timer = respawn_player_and_ghosts(pacman, ghosts)
                            vulnerable_timer = 0
                    elif current_state == INVENTAIRE:
                        # Vérifier si on fait un clic droit sur un slot contenant un item
                        if inventaire_slots is not None:
                            mouse_pos = event.pos
                            for slot_name, slot_rect in inventaire_slots.items():
                                if slot_name != 'retour' and slot_rect.collidepoint(mouse_pos):
                                    if slot_name in inventaire_items:
                                        item_data = inventaire_items[slot_name]
                                        item_type = item_data.get('type')
                                        
                                        # Définir la description selon le type d'item
                                        if item_type == 'longue vue':
                                            item_description = "Longue vue: Permet de collecter les points et pacgommes devant vous. Vous pouvez manger les fantômes vulnérables devant vous. Vous êtes protégé des fantômes devant vous."
                                        elif item_type == 'double longue vue':
                                            item_description = "Double longue vue: Permet de collecter les points et pacgommes dans les 4 directions (haut, bas, gauche, droite). Vous pouvez manger les fantômes vulnérables dans les 4 directions. Vous êtes protégé des fantômes dans les 4 directions (mais pas sur votre case)."
                                        elif item_type == 'bon repas':
                                            item_description = "Bon repas: Un repas délicieux qui redonne de l'énergie."
                                        elif item_type == 'bon goût':
                                            item_description = "Bon goût: Met les coups critiques à 1% (1 pour 100)."
                                        elif item_type == 'pas d\'indigestion':
                                            item_description = "Pas d'indigestion: Divise la chance d'avoir une indigestion par 2."
                                        elif item_type == 'glace':
                                            item_description = "Glace: Crée de la glace derrière vous quand vous vous déplacez. Ralentit les fantômes et disparaît après 3 secondes."
                                        elif item_type == 'skin bleu':
                                            item_description = "Skin bleu: Vous traversez les fantômes bleus sans mourir. Vous ne pouvez pas être tué par les fantômes bleus."
                                        elif item_type == 'skin orange':
                                            item_description = "Skin orange: Vous avez 85% de chance de ne pas mourir si vous touchez un fantôme orange."
                                        elif item_type == 'skin rose':
                                            item_description = "Skin rose: Vous avez 75% de chance de ne pas mourir si vous touchez un fantôme rose."
                                        elif item_type == 'skin rouge':
                                            item_description = "Skin rouge: Vous avez 50% de chance de ne pas mourir si vous touchez un fantôme rouge."
                                        elif item_type == 'bon marché':
                                            bon_marche_level = capacite_items.count("bon marché") if capacite_items else 0
                                            item_description = f"Bon marché: Réduit le prix des items dans le magasin. Niveau actuel: {bon_marche_level}"
                                        elif item_type == 'gadget':
                                            gadget_level = capacite_items.count("gadget") if capacite_items else 0
                                            item_description = f"Gadget: Les gadgets se rechargent 1 seconde plus vite par niveau. Niveau actuel: {gadget_level}"
                                        elif item_type == 'pacgum':
                                            pacgum_level = capacite_items.count("pacgum") if capacite_items else 0
                                            item_description = f"Pacgum: Augmente de 1 seconde le temps de vulnérabilité des fantômes par niveau. Niveau actuel: {pacgum_level}"
                                        elif item_type == 'indigestion':
                                            indigestion_level = capacite_items.count("indigestion") if capacite_items else 0
                                            reduction_percent = indigestion_level * 10
                                            item_description = f"Indigestion: Réduit de {reduction_percent}% la chance d'avoir une indigestion. Niveau actuel: {indigestion_level}"
                                        elif item_type == 'gel':
                                            gel_level = capacite_items.count("gel") if capacite_items else 0
                                            item_description = f"Gel: Si équipé avec le pouvoir glace, ajoute 1 seconde de durée à la glace par niveau. Niveau actuel: {gel_level}"
                                        elif item_type == 'lunette':
                                            lunette_level = capacite_items.count("lunette") if capacite_items else 0
                                            item_description = f"Lunette: Si équipée avec longue vue ou double longue vue, augmente la distance de {lunette_level + 1} cases par niveau. Niveau actuel: {lunette_level}"
                                        elif item_type == 'invincibilité':
                                            invincibilite_level = capacite_items.count("invincibilité") if capacite_items else 0
                                            bonus_time = invincibilite_level * 10  # 1 seconde par niveau (10 frames à 10 FPS)
                                            item_description = f"Invincibilité: Augmente le temps d'invincibilité au début du niveau de {bonus_time} frames ({invincibilite_level} seconde(s)) par niveau. Niveau actuel: {invincibilite_level}"
                                        elif item_type == 'piquant':
                                            piquant_level = capacite_items.count("piquant") if capacite_items else 0
                                            bonus_time = piquant_level * 10  # 1 seconde par niveau (10 frames à 10 FPS)
                                            item_description = f"Piquant: Augmente le temps d'immobilisation des fantômes dans un piège de {bonus_time} frames ({piquant_level} seconde(s)) par niveau. Niveau actuel: {piquant_level}"
                                        elif item_type == 'bonne vue':
                                            bon_vue_level = capacite_items.count("bonne vue") if capacite_items else 0
                                            cooldown_reduction = bon_vue_level * 25  # Réduction de 2.5 secondes par niveau (25 frames à 10 FPS)
                                            item_description = f"Bonne vue: Réduit le temps de recharge de Vision X de {cooldown_reduction} frames ({bon_vue_level * 2.5} seconde(s)) par niveau. Niveau actuel: {bon_vue_level}"
                                        elif item_type == 'bonbe':
                                            bonbe_level = capacite_items.count("bonbe") if capacite_items else 0
                                            radius_bonus = bonbe_level  # +1 case de rayon par niveau
                                            item_description = f"Bonbe: Augmente la grandeur de l'explosion de la bombe téléguidée de {radius_bonus} case(s) par niveau. Niveau actuel: {bonbe_level}"
                                        elif item_type == 'lave':
                                            item_description = "Lave: Utilisez le clic gauche de la souris pour activer. Place la lave sur votre chemin pendant 10 secondes. Si un fantôme touche la lave, il vous fuit pendant 10 secondes. Temps de recharge de 1 minute entre chaque utilisation."
                                        elif item_type == 'feu':
                                            item_description = "Feu: Utilisez le clic gauche de la souris pour activer. Place du feu derrière Pacman lorsqu'il se déplace. Si un fantôme marche dessus, il vous fuit pendant 10 secondes. Temps de recharge de 1 minute entre chaque utilisation."
                                        elif item_type == 'explosion':
                                            item_description = "Explosion: Utilisez le clic gauche de la souris pour activer. Tue tous les fantômes sur le terrain. Vous ne récupérez pas de couronnes. Temps de recharge de 1 minute entre chaque utilisation."
                                        elif item_type == 'tir':
                                            item_description = "Tir: Utilisez le clic gauche de la souris pour activer. Tue un fantôme dans votre champ de vision (direction où vous regardez). Vous ne récupérez pas de couronnes. Temps de recharge de 1 minute entre chaque utilisation."
                                        elif item_type == 'vision x':
                                            item_description = "Vision X: Utilisez le clic gauche de la souris pour activer. Fait disparaître tous les fantômes d'indigestion sur le terrain. Temps de recharge de 1 minute entre chaque utilisation."
                                        elif item_type == 'mort':
                                            item_description = "Mort: Utilisez le clic gauche de la souris pour activer. Tue définitivement le fantôme le plus proche de vous, peu importe sa position. Le fantôme ne réapparaîtra plus. Temps de recharge de 1 minute entre chaque utilisation."
                                        elif item_type == 'bombe téléguidée':
                                            item_description = "Bombe Téléguidée: Utilisez le clic gauche de la souris pour activer. Pacman s'arrête et vous contrôlez une bombe avec les flèches directionnelles. Après 10 secondes, la bombe explose : les fantômes touchés meurent et les murs se cassent. Temps de recharge de 1 minute entre chaque utilisation."
                                        elif item_type == 'piège':
                                            item_description = "Piège: Utilisez le clic gauche de la souris pour activer. Pose un piège à votre position. Si un fantôme marche sur le piège, il est immobilisé pendant 10 secondes. Temps de recharge de 1 minute entre chaque utilisation."
                                        elif item_type == 'tp':
                                            item_description = "TP: Utilisez le clic gauche de la souris pour activer. Téléporte Pacman à la position de la souris, sauf si c'est un mur. Temps de recharge de 25 secondes entre chaque utilisation."
                                        elif item_type == 'portail':
                                            item_description = "Portail: Utilisez le clic gauche de la souris pour activer. 1ère utilisation : pose un portail à votre position. 2ème utilisation : pose un deuxième portail. Si vous entrez dans un portail, vous ressortez par l'autre. 3ème utilisation : enlève les portails. Temps de recharge de 25 secondes entre chaque utilisation."
                                        elif item_type == 'mur':
                                            item_description = "Mur: Utilisez le clic gauche de la souris pour activer. 1ère utilisation : crée un mur à votre position (si ce n'est pas déjà un mur). 2ème utilisation : enlève le mur créé. Temps de recharge de 25 secondes entre chaque utilisation."
                                        elif item_type == 'pièce mythique':
                                            item_description = "Pièce mythique: Une pièce légendaire aux pouvoirs mystiques. Double les pièces gagnées quand équipée."
                                        elif item_type == 'grosse armure':
                                            item_description = "Grosse armure: Une armure robuste qui vous protège. +1 vie quand équipée (et +2 vies si équipée avec l'armure de fer)."
                                        elif item_type == 'armure de fer':
                                            item_description = "Armure de fer: Une armure robuste qui vous protège. +1 vie quand équipée (et +2 vies si équipée avec la grosse armure)."
                                        elif item_type == 'flamme':
                                            item_description = "Flamme: Augmente la durée d'activation du feu de 50% quand équipé."
                                        elif item_type == 'givre':
                                            item_description = "Givre: Diminue encore plus la vitesse de déplacement des fantômes sur la glace si équipé avec le pouvoir 'glace'."
                                        elif item_type == 'infra rouge':
                                            item_description = "Infra rouge: Diminue le temps de rechargement de Vision X si équipé."
                                        elif item_type == 'bric':
                                            item_description = "Bric: Si équipé avec le gadget 'mur', permet de poser 2 murs (1ère et 2ème utilisation) puis de les enlever (3ème utilisation)."
                                        elif item_type == 'coffre fort':
                                            item_description = "Coffre fort: Si équipé, vous donne des couronnes et des pacoins à chaque fois que vous gagnez un niveau."
                                        elif item_type == 'coffre au trésor':
                                            item_description = "Coffre au trésor: Si équipé, vous donne des couronnes et des pacoins à chaque fois que vous gagnez un niveau."
                                        elif item_type == 'double gadget':
                                            item_description = "Double gadget: Permet d'utiliser un gadget deux fois avant que le temps de recharge commence."
                                        else:
                                            item_description = None
                                        break
                            else:
                                # Si on clique ailleurs, effacer la description
                                item_description = None
                    elif current_state == SHOP_POUVOIR:
                        # Vérifier si on fait un clic droit sur un bouton d'item
                        mouse_pos = event.pos
                        if shop_longue_vue_button is not None and shop_longue_vue_button.collidepoint(mouse_pos):
                            item_description = "Longue vue: Permet de collecter les points et pacgommes devant vous. Vous pouvez manger les fantômes vulnérables devant vous. Vous êtes protégé des fantômes devant vous."
                        elif shop_double_longue_vue_button is not None and shop_double_longue_vue_button.collidepoint(mouse_pos):
                            item_description = "Double longue vue: Permet de collecter les points et pacgommes dans les 4 directions (haut, bas, gauche, droite). Vous pouvez manger les fantômes vulnérables dans les 4 directions. Vous êtes protégé des fantômes dans les 4 directions (mais pas sur votre case)."
                        elif shop_bon_repas_button is not None and shop_bon_repas_button.collidepoint(mouse_pos):
                            item_description = "Bon repas: 0.5% de chance d'avoir un coup critique qui rend Pacman arc-en-ciel pendant 2 secondes et donne +10 jetons."
                        elif shop_bon_gout_button is not None and shop_bon_gout_button.collidepoint(mouse_pos):
                            item_description = "Bon goût: Met les coups critiques à 1% (1 pour 100) quand équipé avec Bon repas."
                        elif shop_pas_indigestion_button is not None and shop_pas_indigestion_button.collidepoint(mouse_pos):
                            item_description = "Pas d'indigestion: Divise la chance d'avoir une indigestion par 2."
                        elif shop_glace_button is not None and shop_glace_button.collidepoint(mouse_pos):
                            item_description = "Glace: Crée de la glace derrière vous quand vous vous déplacez. Ralentit les fantômes et disparaît après 3 secondes."
                        elif shop_skin_bleu_button is not None and shop_skin_bleu_button.collidepoint(mouse_pos):
                            item_description = "Skin bleu: Permet de ne pas mourir si on touche un fantome bleu."
                        elif shop_skin_orange_button is not None and shop_skin_orange_button.collidepoint(mouse_pos):
                            item_description = "Skin orange: Quand tu l'équipes, tu as 85 pour cent de chance de ne pas mourir quand tu touches un fantome orange."
                        elif shop_skin_rose_button is not None and shop_skin_rose_button.collidepoint(mouse_pos):
                            item_description = "Skin rose: Quand tu l'équipes, tu as 75 pour cent de chance de ne pas mourir quand tu touches un fantome rose."
                        elif shop_skin_rouge_button is not None and shop_skin_rouge_button.collidepoint(mouse_pos):
                            item_description = "Skin rouge: Quand tu l'équipes, tu as 50 pour cent de chance de ne pas mourir quand tu touches un fantome rouge."
                        elif shop_bombe_button is not None and shop_bombe_button.collidepoint(mouse_pos):
                            item_description = "Bombe Téléguidée: Utilisez le clic gauche de la souris pour activer. Pacman s'arrête et vous contrôlez une bombe avec les flèches directionnelles. Après 10 secondes, la bombe explose : les fantômes touchés meurent et les murs se cassent. Temps de recharge de 1 minute entre chaque utilisation."
                        elif shop_piege_button is not None and shop_piege_button.collidepoint(mouse_pos):
                            item_description = "Piège: Utilisez le clic gauche de la souris pour activer. Pose un piège à votre position. Si un fantôme marche sur le piège, il est immobilisé pendant 10 secondes. Temps de recharge de 1 minute entre chaque utilisation."
                        elif shop_tp_button is not None and shop_tp_button.collidepoint(mouse_pos):
                            item_description = "TP: Utilisez le clic gauche de la souris pour activer. Téléporte Pacman à la position de la souris, sauf si c'est un mur. Temps de recharge de 25 secondes entre chaque utilisation."
                        elif shop_portail_button is not None and shop_portail_button.collidepoint(mouse_pos):
                            item_description = "Portail: Utilisez le clic gauche de la souris pour activer. 1ère utilisation : pose un portail à votre position. 2ème utilisation : pose un deuxième portail. Si vous entrez dans un portail, vous ressortez par l'autre. 3ème utilisation : enlève les portails. Temps de recharge de 25 secondes entre chaque utilisation."
                        elif shop_mur_button is not None and shop_mur_button.collidepoint(mouse_pos):
                            item_description = "Mur: Utilisez le clic gauche de la souris pour activer. 1ère utilisation : crée un mur à votre position (si ce n'est pas déjà un mur). 2ème utilisation : enlève le mur créé. Temps de recharge de 25 secondes entre chaque utilisation."
                        else:
                            # Si on clique ailleurs, ne pas changer la description (la laisser telle quelle)
                            pass
                    elif current_state == SHOP_CAPACITE:
                        # Vérifier si on fait un clic droit sur un bouton d'item
                        mouse_pos = event.pos
                        if shop_bon_marche_button is not None and shop_bon_marche_button.collidepoint(mouse_pos):
                            bon_marche_level = capacite_items.count("bon marché") if capacite_items else 0
                            item_description = f"Bon marché: Réduit le prix des items dans le magasin. Niveau actuel: {bon_marche_level}"
                        elif shop_gadget_button is not None and shop_gadget_button.collidepoint(mouse_pos):
                            gadget_level = capacite_items.count("gadget") if capacite_items else 0
                            item_description = f"Gadget: Les gadgets se rechargent 1 seconde plus vite par niveau. Niveau actuel: {gadget_level}"
                        elif shop_pacgum_button is not None and shop_pacgum_button.collidepoint(mouse_pos):
                            pacgum_level = capacite_items.count("pacgum") if capacite_items else 0
                            item_description = f"Pacgum: Augmente de 1 seconde le temps de vulnérabilité des fantômes par niveau. Niveau actuel: {pacgum_level}"
                        elif shop_indigestion_button is not None and shop_indigestion_button.collidepoint(mouse_pos):
                            indigestion_level = capacite_items.count("indigestion") if capacite_items else 0
                            reduction_percent = indigestion_level * 10
                            item_description = f"Indigestion: Réduit de {reduction_percent}% la chance d'avoir une indigestion. Niveau actuel: {indigestion_level}"
                        elif shop_gel_button is not None and shop_gel_button.collidepoint(mouse_pos):
                            gel_level = capacite_items.count("gel") if capacite_items else 0
                            item_description = f"Gel: Si équipé avec le pouvoir glace, ajoute 1 seconde de durée à la glace par niveau. Niveau actuel: {gel_level}"
                        elif shop_lunette_button is not None and shop_lunette_button.collidepoint(mouse_pos):
                            lunette_level = capacite_items.count("lunette") if capacite_items else 0
                            item_description = f"Lunette: Si équipée avec longue vue ou double longue vue, augmente la distance de {lunette_level + 1} cases par niveau. Niveau actuel: {lunette_level}"
                        elif shop_invincibilite_button is not None and shop_invincibilite_button.collidepoint(mouse_pos):
                            invincibilite_level = capacite_items.count("invincibilité") if capacite_items else 0
                            bonus_time = invincibilite_level * 10  # 1 seconde par niveau (10 frames à 10 FPS)
                            item_description = f"Invincibilité: Augmente le temps d'invincibilité au début du niveau de {bonus_time} frames ({invincibilite_level} seconde(s)) par niveau. Niveau actuel: {invincibilite_level}"
                        elif shop_piquant_button is not None and shop_piquant_button.collidepoint(mouse_pos):
                            piquant_level = capacite_items.count("piquant") if capacite_items else 0
                            bonus_time = piquant_level * 10  # 1 seconde par niveau (10 frames à 10 FPS)
                            item_description = f"Piquant: Augmente le temps d'immobilisation des fantômes dans un piège de {bonus_time} frames ({piquant_level} seconde(s)) par niveau. Niveau actuel: {piquant_level}"
                        elif shop_bon_vue_button is not None and shop_bon_vue_button.collidepoint(mouse_pos):
                            bon_vue_level = capacite_items.count("bonne vue") if capacite_items else 0
                            cooldown_reduction = bon_vue_level * 25  # Réduction de 2.5 secondes par niveau (25 frames à 10 FPS)
                            item_description = f"Bonne vue: Réduit le temps de recharge de Vision X de {cooldown_reduction} frames ({bon_vue_level * 2.5} seconde(s)) par niveau. Niveau actuel: {bon_vue_level}"
                        elif shop_bonbe_button is not None and shop_bonbe_button.collidepoint(mouse_pos):
                            bonbe_level = capacite_items.count("bonbe") if capacite_items else 0
                            radius_bonus = bonbe_level  # +1 case de rayon par niveau
                            item_description = f"Bonbe: Augmente la grandeur de l'explosion de la bombe téléguidée de {radius_bonus} case(s) par niveau. Niveau actuel: {bonbe_level}"
                        else:
                            # Si on clique ailleurs, ne pas changer la description (la laisser telle quelle)
                            pass
                    elif current_state == SHOP_GADGET:
                        # Vérifier si on fait un clic droit sur un bouton d'item
                        mouse_pos = event.pos
                        if shop_explosion_button is not None and shop_explosion_button.collidepoint(mouse_pos):
                            item_description = "Explosion: Utilisez le clic gauche de la souris pour activer. Tue tous les fantômes sur le terrain. Vous ne récupérez pas de couronnes. Temps de recharge de 1 minute entre chaque utilisation."
                        elif shop_vision_x_button is not None and shop_vision_x_button.collidepoint(mouse_pos):
                            item_description = "Vision X: Utilisez le clic gauche de la souris pour activer. Fait disparaître tous les fantômes d'indigestion sur le terrain. Temps de recharge de 1 minute entre chaque utilisation."
                        elif shop_tir_button is not None and shop_tir_button.collidepoint(mouse_pos):
                            item_description = "Tir: Utilisez le clic gauche de la souris pour activer. Tue un fantôme dans votre champ de vision (direction où vous regardez). Vous ne récupérez pas de couronnes. Temps de recharge de 1 minute entre chaque utilisation."
                        elif shop_feu_button is not None and shop_feu_button.collidepoint(mouse_pos):
                            item_description = "Feu: Utilisez le clic gauche de la souris pour activer. Place du feu derrière Pacman lorsqu'il se déplace. Si un fantôme marche dessus, il vous fuit pendant 10 secondes. Temps de recharge de 1 minute entre chaque utilisation."
                        elif shop_mort_button is not None and shop_mort_button.collidepoint(mouse_pos):
                            item_description = "Mort: Utilisez le clic gauche de la souris pour activer. Tue définitivement le fantôme le plus proche de vous, peu importe sa position. Le fantôme ne réapparaîtra plus. Temps de recharge de 1 minute entre chaque utilisation."
                        elif shop_bombe_button is not None and shop_bombe_button.collidepoint(mouse_pos):
                            item_description = "Bombe Téléguidée: Utilisez le clic gauche de la souris pour activer. Pacman s'arrête et vous contrôlez une bombe avec les flèches directionnelles. Après 10 secondes, la bombe explose : les fantômes touchés meurent et les murs se cassent. Temps de recharge de 1 minute entre chaque utilisation."
                        else:
                            # Si on clique ailleurs, ne pas changer la description (la laisser telle quelle)
                            pass
                    elif current_state == SHOP_OBJET:
                        # Vérifier si on fait un clic droit sur un bouton d'item
                        mouse_pos = event.pos
                        if shop_piece_mythique_button is not None and shop_piece_mythique_button.collidepoint(mouse_pos):
                            item_description = "Pièce mythique: Une pièce légendaire aux pouvoirs mystiques. Double les pièces gagnées quand équipée."
                        elif shop_grosse_armure_button is not None and shop_grosse_armure_button.collidepoint(mouse_pos):
                            item_description = "Grosse armure: Une armure robuste qui vous protège. +1 vie quand équipée."
                        elif shop_armure_fer_button is not None and shop_armure_fer_button.collidepoint(mouse_pos):
                            item_description = "Armure de fer: Une armure robuste qui vous protège. +1 vie quand équipée (et +2 vies si équipée avec la grosse armure)."
                        elif shop_flamme_button is not None and shop_flamme_button.collidepoint(mouse_pos):
                            item_description = "Flamme: Augmente la durée d'activation du feu de 50% quand équipé."
                        elif shop_givre_button is not None and shop_givre_button.collidepoint(mouse_pos):
                            item_description = "Givre: Diminue encore plus la vitesse de déplacement des fantômes sur la glace si équipé avec le pouvoir 'glace'."
                        elif shop_infra_rouge_button is not None and shop_infra_rouge_button.collidepoint(mouse_pos):
                            item_description = "Infra rouge: Diminue le temps de rechargement de Vision X si équipé."
                        elif shop_bric_button is not None and shop_bric_button.collidepoint(mouse_pos):
                            item_description = "Bric: Si équipé avec le gadget 'mur', permet de poser 2 murs (1ère et 2ème utilisation) puis de les enlever (3ème utilisation)."
                        elif shop_coffre_fort_button is not None and shop_coffre_fort_button.collidepoint(mouse_pos):
                            item_description = "Coffre fort: Si équipé, vous donne des couronnes et des pacoins à chaque fois que vous gagnez un niveau."
                        elif shop_coffre_tresor_button is not None and shop_coffre_tresor_button.collidepoint(mouse_pos):
                            item_description = "Coffre au trésor: Si équipé, vous donne des couronnes et des pacoins à chaque fois que vous gagnez un niveau."
                        elif shop_double_gadget_button is not None and shop_double_gadget_button.collidepoint(mouse_pos):
                            item_description = "Double gadget: Permet d'utiliser un gadget deux fois avant que le temps de recharge commence."
                        else:
                            # Si on clique ailleurs, ne pas changer la description (la laisser telle quelle)
                            pass
            elif event.type == pygame.KEYDOWN:
                if current_state == NAME_MENU and name_input_active:
                    # Gérer la saisie de texte dans le champ nom
                    if event.key == pygame.K_RETURN:
                        # Valider le nom et sortir automatiquement
                        name_input_active = False
                        current_state = CUSTOMIZATION_MENU
                    elif event.key == pygame.K_BACKSPACE:
                        # Supprimer le dernier caractère
                        player_name = player_name[:-1]
                    elif event.unicode and len(player_name) < 7:  # Limiter à 7 caractères
                        # Ajouter le caractère saisi
                        player_name += event.unicode
                elif current_state == GAME:
                    if bombe_active:
                        # Contrôler la bombe au lieu de Pacman
                        bombe_direction = (0, 0)
                        if event.key == pygame.K_UP:
                            bombe_direction = (0, -1)
                        elif event.key == pygame.K_DOWN:
                            bombe_direction = (0, 1)
                        elif event.key == pygame.K_LEFT:
                            bombe_direction = (-1, 0)
                        elif event.key == pygame.K_RIGHT:
                            bombe_direction = (1, 0)
                        
                        # Déplacer la bombe dans la direction
                        if bombe_direction != (0, 0):
                            new_bombe_x = bombe_x + bombe_direction[0]
                            new_bombe_y = bombe_y + bombe_direction[1]
                            
                            # Gérer la téléportation aux bords
                            if new_bombe_x < 0:
                                new_bombe_x = GRID_WIDTH - 1
                            elif new_bombe_x >= GRID_WIDTH:
                                new_bombe_x = 0
                            if new_bombe_y < 0:
                                new_bombe_y = GRID_HEIGHT - 1
                            elif new_bombe_y >= GRID_HEIGHT:
                                new_bombe_y = 0
                            
                            # Vérifier si la nouvelle position est valide (pas un mur)
                            if 0 <= new_bombe_y < GRID_HEIGHT and 0 <= new_bombe_x < GRID_WIDTH:
                                if maze[new_bombe_y][new_bombe_x] != 1:  # Pas un mur
                                    bombe_x = new_bombe_x
                                    bombe_y = new_bombe_y
                    else:
                        # Contrôler Pacman normalement
                        if event.key == pygame.K_UP:
                            pacman.set_direction((0, -1))
                        elif event.key == pygame.K_DOWN:
                            pacman.set_direction((0, 1))
                        elif event.key == pygame.K_LEFT:
                            pacman.set_direction((-1, 0))
                        elif event.key == pygame.K_RIGHT:
                            pacman.set_direction((1, 0))
        
        # Gérer la logique du jeu seulement si on est dans l'état GAME
        if current_state == GAME:
            # Vérifier si on est en mode multi-map (niveau multiple de 10 en mode aventure)
            is_multi_map_mode = is_adventure_mode and level % 10 == 0 and level > 0
            
            if success_notification_timer > 0:
                success_notification_timer -= 1
            # Gérer la transition entre niveaux
            if level_transition:
                level_transition_timer -= 1
                if level_transition_timer <= 0:
                    level_transition = False
                    # Déclencher l'invincibilité quand la transition se termine
                    # Calculer le bonus d'invincibilité selon le niveau de la capacité équipée
                    invincibilite_bonus = calculate_invincibilite_bonus(capacite_items, inventaire_items)
                    invincibility_timer = 30 + invincibilite_bonus  # 3 secondes d'invincibilité + bonus
                    # S'assurer que la glace est bien réinitialisée (au cas où)
                    ice_tiles = {}
                    pacman_last_pos = (pacman.x, pacman.y)
            
            # Gérer la réapparition après perte de vie
            if respawn_timer > 0:
                respawn_timer -= 1
                if respawn_timer == 0:
                    # Réinitialiser les positions (même code que quand on appuie sur R)
                    # Calculer le bonus d'invincibilité selon le niveau de la capacité équipée
                    invincibilite_bonus = calculate_invincibilite_bonus(capacite_items, inventaire_items)
                    pacman, invincibility_timer = respawn_player_and_ghosts(pacman, ghosts, invincibilite_bonus)
                    vulnerable_timer = 0
                    ice_tiles = {}  # Réinitialiser les cases de glace
                    fire_tiles = {}  # Réinitialiser les cases de feu
                    fire_active = False  # Réinitialiser l'activation du feu
                    fire_timer = 0  # Réinitialiser le timer du feu
                    gadget_cooldown = 0  # Réinitialiser le temps de recharge du gadget
                    mort_cooldown = 0  # Réinitialiser le temps de recharge de "mort"
                    bombe_cooldown = 0  # Réinitialiser le temps de recharge de "bombe téléguidée"
                    bombe_active = False  # Réinitialiser l'état de la bombe
                    pacman_frozen = False  # Réinitialiser l'état de gel de Pacman
                    bombe_timer = 0  # Réinitialiser le timer de la bombe
                    # Les pièges persistent entre les niveaux et les retours
                    portal1_pos = None  # Réinitialiser les portails
                    portal2_pos = None
                    portal_use_count = 0
                    # Enlever le mur créé du maze si nécessaire
                    if mur_pos is not None:
                        if isinstance(mur_pos, list):
                            # Si c'est une liste (cas avec bric), enlever tous les murs
                            for mur_x, mur_y in mur_pos:
                                if 0 <= mur_y < GRID_HEIGHT and 0 <= mur_x < GRID_WIDTH:
                                    maze[mur_y][mur_x] = 0  # Remettre en chemin
                        else:
                            # Si c'est un tuple (comportement normal)
                            mur_x, mur_y = mur_pos
                            if 0 <= mur_y < GRID_HEIGHT and 0 <= mur_x < GRID_WIDTH:
                                maze[mur_y][mur_x] = 0  # Remettre en chemin
                    mur_pos = None  # Réinitialiser le mur
                    mur_use_count = 0
                    pacman_last_pos = (pacman.x, pacman.y)  # Réinitialiser la position précédente
                    # Réinitialiser les flee_timer et immobilized_timer des fantômes
                    for ghost in ghosts:
                        ghost.flee_timer = 0
                        ghost.immobilized_timer = 0
            
            # Gérer l'invincibilité après spawn
            if invincibility_timer > 0:
                invincibility_timer -= 1
            
            # Gérer la couronne après avoir mangé un fantôme
            if crown_timer > 0:
                crown_timer -= 1
            
            # Gérer l'indigestion
            if indigestion_timer > 0:
                indigestion_timer -= 1
                if indigestion_timer == 0:
                    has_indigestion = False
                    # Supprimer le fantôme d'indigestion s'il existe
                    ghosts[:] = [ghost for ghost in ghosts if not ghost.harmless]
            
            # Gérer l'effet arc-en-ciel du coup critique
            if rainbow_timer > 0:
                rainbow_timer -= 1
                if rainbow_timer == 0:
                    is_rainbow_critique = False
            
            # Décrémenter le timer depuis le dernier fantôme mangé
            if last_ghost_time > 0:
                last_ghost_time -= 1
            
            # Mettre à jour le jeu seulement si on est dans l'état GAME
            if not game_over and not won and not level_transition and respawn_timer == 0:
                # Vérifier si "glace" est équipé avant de mettre à jour Pacman
                has_glace = ('pouvoir' in inventaire_items and 
                            inventaire_items['pouvoir'].get('type') == 'glace')
                
                # Sauvegarder la position précédente de Pacman avant de le mettre à jour
                old_pacman_pos = (pacman.x, pacman.y)
                
                # Gérer la bombe téléguidée
                if bombe_active:
                    # Décrémenter le timer de la bombe
                    bombe_timer -= 1
                    
                    # Si le timer arrive à 0, faire exploser la bombe
                    if bombe_timer <= 0:
                        # Calculer le bonus de "bonbe" si équipé
                        has_bonbe_capacity = (('capacite1' in inventaire_items and inventaire_items['capacite1'].get('type') == 'bonbe') or
                                            ('capacite2' in inventaire_items and inventaire_items['capacite2'].get('type') == 'bonbe'))
                        bonbe_level = capacite_items.count("bonbe") if capacite_items else 0
                        explosion_radius_bonus = bonbe_level if has_bonbe_capacity else 0  # +1 case de rayon par niveau
                        # Zone d'explosion : 3x3 cases autour de la bombe (base) + bonus de "bonbe"
                        explosion_radius = 1 + explosion_radius_bonus  # 1 case de base + bonus
                        
                        # Tuer les fantômes dans la zone d'explosion
                        for ghost in ghosts[:]:  # Utiliser une copie de la liste pour éviter les problèmes lors de la modification
                            # Vérifier si le fantôme est dans la zone d'explosion
                            dx = abs(ghost.x - bombe_x)
                            dy = abs(ghost.y - bombe_y)
                            
                            # Gérer la téléportation aux bords pour la distance
                            if dx > GRID_WIDTH // 2:
                                dx = GRID_WIDTH - dx
                            if dy > GRID_HEIGHT // 2:
                                dy = GRID_HEIGHT - dy
                            
                            if dx <= explosion_radius and dy <= explosion_radius:
                                # Le fantôme est dans la zone d'explosion
                                if not ghost.harmless and not ghost.eyes:
                                    # Tuer le fantôme (le transformer en yeux)
                                    ghost.eyes = True
                                    ghost.vulnerable = False
                                    ghost.returning = False
                                    score += 300
                        
                        # Casser les murs dans la zone d'explosion
                        for dy in range(-explosion_radius, explosion_radius + 1):
                            for dx in range(-explosion_radius, explosion_radius + 1):
                                check_x = bombe_x + dx
                                check_y = bombe_y + dy
                                
                                # Gérer la téléportation aux bords
                                if check_x < 0:
                                    check_x = GRID_WIDTH - 1
                                elif check_x >= GRID_WIDTH:
                                    check_x = 0
                                if check_y < 0:
                                    check_y = GRID_HEIGHT - 1
                                elif check_y >= GRID_HEIGHT:
                                    check_y = 0
                                
                                # Vérifier si c'est un mur et le casser
                                if 0 <= check_y < GRID_HEIGHT and 0 <= check_x < GRID_WIDTH:
                                    if maze[check_y][check_x] == 1:  # C'est un mur
                                        maze[check_y][check_x] = 0  # Casser le mur
                        
                        # Réinitialiser l'état de la bombe
                        bombe_active = False
                        pacman_frozen = False
                        bombe_timer = 0
                else:
                    # Mettre à jour Pacman normalement seulement si la bombe n'est pas active
                    # En mode multi-map, gérer le changement de map au lieu de la téléportation
                    if is_multi_map_mode:
                        # Sauvegarder la position avant le déplacement
                        old_x, old_y = pacman.x, pacman.y
                        # Essayer de changer de direction
                        if pacman.can_move(pacman.next_direction, maze):
                            pacman.direction = pacman.next_direction
                        
                        # Se déplacer dans la direction actuelle
                        if pacman.can_move(pacman.direction, maze):
                            pacman.x += pacman.direction[0]
                            pacman.y += pacman.direction[1]
                            
                            # Gérer le changement de map aux bords
                            map_changed = False
                            if pacman.x < 0:
                                # Sortir par la gauche, aller à la map de gauche
                                if map_x > 0:
                                    map_x -= 1
                                    pacman.x = GRID_WIDTH - 1
                                    map_changed = True
                                else:
                                    pacman.x = 0  # Bloquer au bord si on est déjà à gauche
                            elif pacman.x >= GRID_WIDTH:
                                # Sortir par la droite, aller à la map de droite
                                if map_x < 3:
                                    map_x += 1
                                    pacman.x = 0
                                    map_changed = True
                                else:
                                    pacman.x = GRID_WIDTH - 1  # Bloquer au bord si on est déjà à droite
                            
                            if pacman.y < 0:
                                # Sortir par le haut, aller à la map du haut
                                if map_y > 0:
                                    map_y -= 1
                                    pacman.y = GRID_HEIGHT - 1
                                    map_changed = True
                                else:
                                    pacman.y = 0  # Bloquer au bord si on est déjà en haut
                            elif pacman.y >= GRID_HEIGHT:
                                # Sortir par le bas, aller à la map du bas
                                if map_y < 3:
                                    map_y += 1
                                    pacman.y = 0
                                    map_changed = True
                                else:
                                    pacman.y = GRID_HEIGHT - 1  # Bloquer au bord si on est déjà en bas
                            
                            # Si on a changé de map, charger la nouvelle map
                            if map_changed:
                                # Calculer l'index de la map dans la grille 4x4 (0-15)
                                map_index = map_y * 4 + map_x
                                # Utiliser cet index pour choisir une map parmi les MAZES disponibles
                                maze_index = map_index % len(MAZES)
                                maze = [row[:] for row in MAZES[maze_index]]
                                # Réinitialiser les points et pacgommes sur la nouvelle map
                                for y in range(GRID_HEIGHT):
                                    for x in range(GRID_WIDTH):
                                        if maze[y][x] == 0:
                                            maze[y][x] = 2  # Remettre les points
                            
                            # Animation de la bouche
                            pacman.mouth_angle += 5
                            if pacman.mouth_angle >= 360:
                                pacman.mouth_angle = 0
                            pacman.mouth_open = (pacman.mouth_angle // 30) % 2 == 0
                        else:
                            # Animation de la bouche même si on ne peut pas bouger
                            pacman.mouth_angle += 5
                            if pacman.mouth_angle >= 360:
                                pacman.mouth_angle = 0
                            pacman.mouth_open = (pacman.mouth_angle // 30) % 2 == 0
                    else:
                        pacman.update(maze)
                    
                    # Vérifier si Pacman entre dans un portail et le téléporter
                    if portal1_pos is not None and portal2_pos is not None:
                        if (pacman.x, pacman.y) == portal1_pos:
                            # Téléporter vers le portail 2
                            pacman.x, pacman.y = portal2_pos
                        elif (pacman.x, pacman.y) == portal2_pos:
                            # Téléporter vers le portail 1
                            pacman.x, pacman.y = portal1_pos
                
                # La longue vue ou double longue vue est équipée seulement si elle est dans le slot "pouvoir"
                has_longue_vue = ('pouvoir' in inventaire_items and 
                                 (inventaire_items['pouvoir'].get('type') == 'longue vue' or 
                                  inventaire_items['pouvoir'].get('type') == 'double longue vue'))
                is_double_longue_vue = ('pouvoir' in inventaire_items and 
                                       inventaire_items['pouvoir'].get('type') == 'double longue vue')
                # Vérifier si "bon repas" est équipé dans le slot "pouvoir"
                has_bon_repas = ('pouvoir' in inventaire_items and 
                                inventaire_items['pouvoir'].get('type') == 'bon repas')
                # Vérifier si "bon goût" est équipé dans le slot "pouvoir"
                has_bon_gout = ('pouvoir' in inventaire_items and 
                               inventaire_items['pouvoir'].get('type') == 'bon goût')
                # Vérifier si "pas d'indigestion" est équipé dans le slot "pouvoir"
                has_pas_indigestion = ('pouvoir' in inventaire_items and 
                                      inventaire_items['pouvoir'].get('type') == 'pas d\'indigestion')
                # Vérifier si "pièce mythique" est équipée dans un slot objet
                has_piece_mythique = (('objet0' in inventaire_items and inventaire_items['objet0'].get('type') == 'pièce mythique') or
                                     ('objet1' in inventaire_items and inventaire_items['objet1'].get('type') == 'pièce mythique') or
                                     ('objet2' in inventaire_items and inventaire_items['objet2'].get('type') == 'pièce mythique'))
                # Vérifier les armures équipées et le bonus de vie correspondant
                armor_lives_bonus = calculate_armor_lives_bonus(inventaire_items)
                # Valeur théorique des vies max en tenant compte des armures
                current_max_lives = MAX_LIVES + armor_lives_bonus
                # Le bonus de vie ne s'applique qu'une seule fois au début du jeu, pas à chaque retour dans le jeu
                # On ne fait rien ici, le bonus est appliqué lors de l'initialisation des vies
                # Vérifier si "skin bleu" est équipé dans le slot "pouvoir"
                has_skin_bleu = ('pouvoir' in inventaire_items and 
                                 inventaire_items['pouvoir'].get('type') == 'skin bleu')
                
                # Vérifier si "skin orange" est équipé dans le slot "pouvoir"
                has_skin_orange = ('pouvoir' in inventaire_items and 
                                   inventaire_items['pouvoir'].get('type') == 'skin orange')
                
                # Vérifier si "skin rose" est équipé dans le slot "pouvoir"
                has_skin_rose = ('pouvoir' in inventaire_items and 
                                 inventaire_items['pouvoir'].get('type') == 'skin rose')
                
                # Vérifier si "skin rouge" est équipé dans le slot "pouvoir"
                has_skin_rouge = ('pouvoir' in inventaire_items and 
                                  inventaire_items['pouvoir'].get('type') == 'skin rouge')
                
                # Créer une case de glace derrière Pacman si "glace" est équipé et que Pacman s'est déplacé
                if has_glace:
                    new_pacman_pos = (pacman.x, pacman.y)
                    # Si Pacman s'est déplacé, créer une case de glace à sa position précédente
                    if old_pacman_pos != new_pacman_pos:
                        # Vérifier que la position précédente n'est pas un mur
                        last_x, last_y = old_pacman_pos
                        if 0 <= last_y < GRID_HEIGHT and 0 <= last_x < GRID_WIDTH:
                            if maze[last_y][last_x] != 1:  # Pas un mur
                                # Calculer la durée de la glace : ICE_DURATION + bonus si "gel" est équipé
                                gel_level = capacite_items.count("gel") if capacite_items else 0
                                # Vérifier si "gel" est équipé dans un slot capacité
                                has_gel_capacity = (('capacite1' in inventaire_items and inventaire_items['capacite1'].get('type') == 'gel') or
                                                   ('capacite2' in inventaire_items and inventaire_items['capacite2'].get('type') == 'gel'))
                                # Si le pouvoir glace est équipé ET la capacité gel est équipée, ajouter 1 seconde (10 frames) par niveau
                                ice_duration = ICE_DURATION
                                if has_glace and has_gel_capacity:
                                    ice_duration += gel_level * 10  # 1 seconde = 10 frames à 10 FPS
                                ice_tiles[old_pacman_pos] = ice_duration
                
                # Mettre à jour la position précédente de Pacman
                pacman_last_pos = (pacman.x, pacman.y)
                
                # Mettre à jour les cases de glace (décrémenter le timer et supprimer celles expirées)
                expired_tiles = []
                for tile_pos, timer in ice_tiles.items():
                    ice_tiles[tile_pos] = timer - 1
                    if ice_tiles[tile_pos] <= 0:
                        expired_tiles.append(tile_pos)
                for tile_pos in expired_tiles:
                    del ice_tiles[tile_pos]
                
                # Gérer la réapparition des pacgommes (seulement en mode aventure)
                if is_adventure_mode:
                    pacgomme_positions_to_remove = []
                    for pos, timer in pacgomme_timers.items():
                        pacgomme_timers[pos] = timer - 1
                        if pacgomme_timers[pos] <= 0:
                            x, y = pos
                            # Vérifier que la case est toujours valide (pas un mur) et qu'elle n'est pas occupée
                            if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                                if maze[y][x] != 1:  # Pas un mur
                                    maze[y][x] = 3  # Faire réapparaître la pacgomme
                            pacgomme_positions_to_remove.append(pos)
                    # Supprimer les timers terminés
                    for pos in pacgomme_positions_to_remove:
                        del pacgomme_timers[pos]
                    
                    # En mode aventure, les fantômes ne réapparaissent pas après avoir été mangés
                    # (La logique de réapparition a été supprimée)
                
                # Gérer le système de feu
                # Vérifier si le gadget lave ou feu est équipé dans le slot gadget
                equipped_gadget_feu = get_equipped_gadget(inventaire_items)
                has_feu_gadget = (equipped_gadget_feu is not None and 
                                 (equipped_gadget_feu.get('type') == 'lave' or 
                                  equipped_gadget_feu.get('type') == 'feu'))
                gadget_feu_type = None
                if equipped_gadget_feu:
                    gadget_type_feu = equipped_gadget_feu.get('type')
                    if gadget_type_feu == 'lave' or gadget_type_feu == 'feu':
                        gadget_feu_type = gadget_type_feu
                
                # Calculer le niveau de "gadget" équipé dans les slots capacité
                gadget_level = 0
                if 'capacite1' in inventaire_items and inventaire_items['capacite1'].get('type') == 'gadget':
                    gadget_level += 1
                if 'capacite2' in inventaire_items and inventaire_items['capacite2'].get('type') == 'gadget':
                    gadget_level += 1
                # Ajouter aussi le niveau de "gadget" dans la grille et dans capacite_items
                gadget_level_total = capacite_items.count("gadget") if capacite_items else 0
                gadget_level = gadget_level_total
                
                # Décrémenter les cooldowns (1 seconde par niveau = 10 frames par niveau)
                # Niveau 1 = 2 frames, niveau 2 = 3 frames, etc. (1 frame de base + niveau frames)
                cooldown_reduction = 1 + gadget_level
                if gadget_cooldown > 0:
                    gadget_cooldown = max(0, gadget_cooldown - cooldown_reduction)
                if mort_cooldown > 0:
                    mort_cooldown = max(0, mort_cooldown - cooldown_reduction)
                if bombe_cooldown > 0:
                    bombe_cooldown = max(0, bombe_cooldown - cooldown_reduction)
                
                # Décrémenter le timer d'activation du feu
                if fire_timer > 0:
                    fire_timer -= 1
                    if fire_timer <= 0:
                        fire_active = False
                
                
                # Si le feu est actif, créer des cases de feu sur le chemin de Pacman
                if fire_active and has_feu_gadget:
                    if gadget_feu_type == 'lave':
                        # Créer du feu à la position actuelle de Pacman si ce n'est pas un mur
                        if 0 <= pacman.y < GRID_HEIGHT and 0 <= pacman.x < GRID_WIDTH:
                            if maze[pacman.y][pacman.x] != 1:  # Pas un mur
                                fire_tiles[(pacman.x, pacman.y)] = calculate_fire_duration(inventaire_items, FIRE_DURATION)
                    elif gadget_feu_type == 'feu':
                        # Créer du feu DERRIÈRE Pacman (à sa position précédente) si Pacman s'est déplacé
                        if old_pacman_pos != (pacman.x, pacman.y):
                            last_x, last_y = old_pacman_pos
                            if 0 <= last_y < GRID_HEIGHT and 0 <= last_x < GRID_WIDTH:
                                if maze[last_y][last_x] != 1:  # Pas un mur
                                    fire_tiles[(last_x, last_y)] = calculate_fire_duration(inventaire_items, FIRE_DURATION)
                
                # Mettre à jour les cases de feu (décrémenter le timer et supprimer celles expirées)
                expired_fire_tiles = []
                for tile_pos, timer in fire_tiles.items():
                    fire_tiles[tile_pos] = timer - 1
                    if fire_tiles[tile_pos] <= 0:
                        expired_fire_tiles.append(tile_pos)
                for tile_pos in expired_fire_tiles:
                    del fire_tiles[tile_pos]
                
                # Calculer la position devant Pacman selon sa direction
                front_x = pacman.x
                front_y = pacman.y
                if pacman.direction != (0, 0):
                    front_x = pacman.x + pacman.direction[0]
                    front_y = pacman.y + pacman.direction[1]
                    # Gérer la téléportation aux bords
                    if front_x < 0:
                        front_x = GRID_WIDTH - 1
                    elif front_x >= GRID_WIDTH:
                        front_x = 0
                
                # Vérifier si "lunette" est équipée dans un slot capacité
                has_lunette_capacity = (('capacite1' in inventaire_items and inventaire_items['capacite1'].get('type') == 'lunette') or
                                       ('capacite2' in inventaire_items and inventaire_items['capacite2'].get('type') == 'lunette'))
                lunette_level = capacite_items.count("lunette") if capacite_items else 0
                # La distance de base est 1, augmentée de 1 par niveau de lunette si équipée avec longue vue
                distance = 1
                if has_longue_vue and has_lunette_capacity:
                    distance = 1 + lunette_level  # Distance = 1 + niveau de lunette
                
                # Pour la double longue vue, calculer les positions dans les 4 directions
                directions = []
                if is_double_longue_vue:
                    # Toutes les directions avec la distance augmentée par lunette
                    directions = []
                    for d in range(1, distance + 1):
                        directions.append((pacman.x + d, pacman.y))  # Droite
                        directions.append((pacman.x - d, pacman.y))  # Gauche
                        directions.append((pacman.x, pacman.y + d))  # Bas
                        directions.append((pacman.x, pacman.y - d))  # Haut
                    # Gérer la téléportation aux bords pour chaque direction
                    for i, (dx, dy) in enumerate(directions):
                        if dx < 0:
                            directions[i] = (GRID_WIDTH - 1, dy)
                        elif dx >= GRID_WIDTH:
                            directions[i] = (0, dy)
                elif has_longue_vue and pacman.direction != (0, 0):
                    # Devant pour la longue vue simple avec distance augmentée par lunette
                    directions = []
                    for d in range(1, distance + 1):
                        dir_x = pacman.x + pacman.direction[0] * d
                        dir_y = pacman.y + pacman.direction[1] * d
                        # Gérer la téléportation aux bords
                        if dir_x < 0:
                            dir_x = GRID_WIDTH - 1
                        elif dir_x >= GRID_WIDTH:
                            dir_x = 0
                        directions.append((dir_x, dir_y))
                
                # Vérifier si Pacman mange un point (à sa position ou devant si longue vue)
                if maze[pacman.y][pacman.x] == 2:
                    maze[pacman.y][pacman.x] = 0
                    score += 10
                    # Gagner un jeton pour chaque point mangé (2 si pièce mythique équipée) - sauf en mode aventure
                    if not is_adventure_mode:
                        if has_piece_mythique:
                            jeton_count += 2
                        else:
                            jeton_count += 1
                    
                    # Coup critique : "bon goût" seul donne 1%, "bon repas" seul donne 0.5%
                    if has_bon_gout:
                        # "bon goût" seul : 1% de chance de coup critique
                        crit_chance = 0.01
                        if random.random() < crit_chance:
                            # Coup critique : arc-en-ciel pendant 2 secondes et +10 jetons (20 si pièce mythique équipée)
                            is_rainbow_critique = True
                            rainbow_timer = 20  # 2 secondes à 10 FPS
                            if has_piece_mythique:
                                jeton_count += 20
                            else:
                                jeton_count += 10
                    elif has_bon_repas:
                        # "bon repas" seul : 0.5% de chance de coup critique
                        crit_chance = 0.005
                        if random.random() < crit_chance:
                            # Coup critique : arc-en-ciel pendant 2 secondes et +10 jetons (20 si pièce mythique équipée)
                            is_rainbow_critique = True
                            rainbow_timer = 20  # 2 secondes à 10 FPS
                            if has_piece_mythique:
                                jeton_count += 20
                            else:
                                jeton_count += 10
                    
                    # Calculer la chance d'indigestion en fonction de "pas d'indigestion" et de la capacité "indigestion"
                    base_indigestion_chance = 0.005  # 0.5% de base
                    if has_pas_indigestion:
                        base_indigestion_chance = 0.0025  # Divisée par 2 si "pas d'indigestion" équipé
                    
                    # Réduire la chance selon le niveau de la capacité "indigestion" (10% de réduction par niveau)
                    indigestion_capacity_level = capacite_items.count("indigestion") if capacite_items else 0
                    reduction_factor = 1.0 - (indigestion_capacity_level * 0.1)  # Réduction de 10% par niveau
                    reduction_factor = max(0.0, reduction_factor)  # Ne peut pas être négatif
                    indigestion_chance = base_indigestion_chance * reduction_factor
                    
                    if random.random() < indigestion_chance and not has_indigestion:
                        # Indigestion : perdre 10 jetons et devenir vert pendant 1 minute
                        jeton_count = max(0, jeton_count - 10)
                        has_indigestion = True
                        indigestion_timer = 600  # 1 minute (60 secondes = 600 frames à 10 FPS)
                        # Vérifier qu'il n'y a pas déjà un fantôme d'indigestion
                        if not any(ghost.harmless for ghost in ghosts):
                            # Créer un fantôme d'indigestion inoffensif près de Pacman
                            # Chercher une position valide (pas un mur) près de Pacman
                            indigestion_ghost_x = None
                            indigestion_ghost_y = None
                            attempts = 0
                            max_attempts = 50
                            while indigestion_ghost_x is None and attempts < max_attempts:
                                attempts += 1
                                # Position aléatoire près de Pacman (à une distance de 2-5 cases)
                                angle = random.random() * 2 * math.pi
                                distance = random.randint(2, 5)
                                test_x = int(pacman.x + distance * math.cos(angle))
                                test_y = int(pacman.y + distance * math.sin(angle))
                                # S'assurer que la position est dans les limites
                                test_x = max(0, min(GRID_WIDTH - 1, test_x))
                                test_y = max(0, min(GRID_HEIGHT - 1, test_y))
                                # Vérifier que la position n'est pas un mur
                                if 0 <= test_y < GRID_HEIGHT and 0 <= test_x < GRID_WIDTH:
                                    if maze[test_y][test_x] != 1:  # Pas un mur
                                        indigestion_ghost_x = test_x
                                        indigestion_ghost_y = test_y
                            # Si on n'a pas trouvé de position valide après plusieurs tentatives, utiliser une position proche de Pacman
                            if indigestion_ghost_x is None:
                                # Essayer les positions autour de Pacman
                                for dx in range(-3, 4):
                                    for dy in range(-3, 4):
                                        test_x = pacman.x + dx
                                        test_y = pacman.y + dy
                                        if 0 <= test_y < GRID_HEIGHT and 0 <= test_x < GRID_WIDTH:
                                            if maze[test_y][test_x] != 1:  # Pas un mur
                                                indigestion_ghost_x = test_x
                                                indigestion_ghost_y = test_y
                                                break
                                    if indigestion_ghost_x is not None:
                                        break
                            # Si on a trouvé une position valide, créer le fantôme
                            if indigestion_ghost_x is not None:
                                # Utiliser la couleur la plus courante dans le niveau
                                indigestion_ghost_color = get_most_common_ghost_color(ghosts, level)
                                indigestion_ghost = Ghost(indigestion_ghost_x, indigestion_ghost_y, indigestion_ghost_color, harmless=True)
                                ghosts.append(indigestion_ghost)
                    # Vérifier si on a atteint le seuil de jetons pour gagner une vie (100 en facile, 1000 en difficile, 2000 en hardcore, 200 sinon)
                    if difficulty == "facile":
                        jeton_threshold = 100
                    elif difficulty == "difficile":
                        jeton_threshold = 1000
                    elif difficulty == "hardcore":
                        jeton_threshold = 2000  # Pas de bonus de vie en hardcore (seuil très élevé)
                    else:
                        jeton_threshold = 200
                    if jeton_count >= jeton_threshold:
                        # En mode difficile et hardcore, on ne peut pas gagner de vies avec les jetons
                        if lives < current_max_lives and difficulty != "difficile" and difficulty != "hardcore":
                            lives += 1
                        # Mettre les jetons et couronnes dans la poche (sauf en mode aventure)
                        if not is_adventure_mode:
                            jeton_poche += jeton_count
                        crown_poche += crown_count
                        jeton_count = 0  # Réinitialiser le compteur de jetons
                        crown_count = 0  # Réinitialiser le compteur de couronnes
                    if count_points(maze) == 0:
                        # Passer au niveau suivant
                        level += 1
                        if level == 2 and not first_level_success_unlocked:
                            first_level_success_unlocked = True
                            # Vérifier si ce trophée a déjà été gagné par n'importe quel compte
                            trophy_already_earned = False
                            for account in accounts:
                                if TROPHY_FIRST_LEVEL in account.get('trophies', []):
                                    trophy_already_earned = True
                                    break
                            
                            if not trophy_already_earned:
                                success_notification_text = "Nouveau succès débloqué !"
                                success_notification_timer = 60  # Afficher le succès pendant 1 seconde
                                if current_account_index is not None and 0 <= current_account_index < len(accounts):
                                    trophies = accounts[current_account_index].setdefault('trophies', [])
                                    if TROPHY_FIRST_LEVEL not in trophies:
                                        trophies.append(TROPHY_FIRST_LEVEL)
                                        save_accounts_data(accounts)
                        # Vérifier si "coffre fort" est équipé
                        has_coffre_fort = (('objet0' in inventaire_items and inventaire_items['objet0'].get('type') == 'coffre fort') or
                                          ('objet1' in inventaire_items and inventaire_items['objet1'].get('type') == 'coffre fort') or
                                          ('objet2' in inventaire_items and inventaire_items['objet2'].get('type') == 'coffre fort'))
                        # Récompense du coffre fort si équipé
                        if has_coffre_fort:
                            jeton_poche += 100  # Gagner 100 pacoins
                        # Vérifier si "coffre au trésor" est équipé
                        has_coffre_tresor = (('objet0' in inventaire_items and inventaire_items['objet0'].get('type') == 'coffre au trésor') or
                                            ('objet1' in inventaire_items and inventaire_items['objet1'].get('type') == 'coffre au trésor') or
                                            ('objet2' in inventaire_items and inventaire_items['objet2'].get('type') == 'coffre au trésor'))
                        # Récompense du coffre au trésor si équipé
                        if has_coffre_tresor:
                            jeton_poche += 200  # Gagner 200 pacoins
                        # Récompense au niveau 17 en mode facile
                        if difficulty == "facile" and level == 17:
                            crown_poche += 1  # Gagner 1 couronne
                            jeton_poche += 50  # Gagner 50 pacoins
                        # Récompense au niveau 25 en mode moyen
                        if difficulty == "moyen" and level == 25:
                            crown_poche += 55  # Gagner 55 couronnes
                            jeton_poche += 1000  # Gagner 1000 pacoins
                        # Récompense au niveau 30 en mode difficile
                        if difficulty == "difficile" and level == 30:
                            crown_poche += 60  # Gagner 60 couronnes
                            jeton_poche += 1500  # Gagner 1500 pacoins
                        # Récompense au niveau 50 en mode hardcore
                        if difficulty == "hardcore" and level == 50:
                            crown_poche += 1000  # Gagner 1000 couronnes
                            jeton_poche += 200000  # Gagner 200000 pacoins
                        # Vérifier si on a gagné au niveau 24 (en moyenne)
                        if level == 24:
                            won = True
                            crown_poche += 10  # Gagner 10 couronnes
                            jeton_poche += 500  # Gagner 500 pacoins
                            # Arrêter la musique si elle est en cours
                            if music_playing:
                                pygame.mixer.music.stop()
                                music_playing = False
                        # Vérifier si on a gagné (niveau 20 en mode facile)
                        if difficulty == "facile" and level >= 20:
                            won = True
                            # Arrêter la musique si elle est en cours
                            if music_playing:
                                pygame.mixer.music.stop()
                                music_playing = False
                        # Vérifier si on a gagné au niveau 20 sans difficulté choisie
                        if difficulty is None and level >= 20:
                            won = True
                            # Arrêter la musique si elle est en cours
                            if music_playing:
                                pygame.mixer.music.stop()
                                music_playing = False
                            crown_poche += 10  # Gagner 10 couronnes
                            jeton_poche += 500  # Gagner 500 pacoins
                        level_transition = True
                        level_transition_timer = 60  # 2 secondes de transition
                        # Sauvegarder l'état de l'indigestion avant de passer au niveau suivant
                        indigestion_active = has_indigestion and indigestion_timer > 0
                        saved_indigestion_timer = indigestion_timer
                        # Supprimer le fantôme d'indigestion s'il existe avant de passer au niveau suivant
                        ghosts[:] = [ghost for ghost in ghosts if not ghost.harmless]
                        maze, pacman, ghosts = start_next_level(level)
                        # Initialiser les coordonnées de la map pour le système 4x4 aux niveaux multiples de 10 en mode aventure
                        if is_adventure_mode and level % 10 == 0 and level > 0:
                            map_x = 0
                            map_y = 0
                            # Charger la première map de la grille 4x4
                            map_index = map_y * 4 + map_x
                            maze_index = map_index % len(MAZES)
                            maze = [row[:] for row in MAZES[maze_index]]
                        # Ajouter un fantôme bleu supplémentaire pour le mode moyen (niveau 3+)
                        if difficulty == "moyen" and level >= 3:
                            new_ghost = Ghost(12, 9, BLUE)
                            ghosts.append(new_ghost)
                            new_ghost.set_path(maze)
                        # Ajouter 2 fantômes orange supplémentaires pour le mode difficile (niveau 3+)
                        if difficulty == "difficile" and level >= 3:
                            ORANGE = (255, 165, 0)
                            # Trouver une position libre pour les nouveaux fantômes
                            existing_positions = [(ghost.x, ghost.y) for ghost in ghosts]
                            new_x = 12
                            new_y = 9
                            # Chercher une position libre
                            while (new_x, new_y) in existing_positions:
                                new_x += 1
                                if new_x >= GRID_WIDTH:
                                    new_x = 0
                                    new_y += 1
                            new_ghost1 = Ghost(new_x, new_y, ORANGE)
                            ghosts.append(new_ghost1)
                            # Chercher une autre position libre pour le deuxième fantôme
                            existing_positions.append((new_x, new_y))
                            new_x2 = new_x + 1
                            new_y2 = new_y
                            while (new_x2, new_y2) in existing_positions:
                                new_x2 += 1
                                if new_x2 >= GRID_WIDTH:
                                    new_x2 = 0
                                    new_y2 += 1
                            new_ghost2 = Ghost(new_x2, new_y2, ORANGE)
                            ghosts.append(new_ghost2)
                            new_ghost2.set_path(maze)
                        # Ajouter 3 fantômes orange supplémentaires pour le mode hardcore (niveau 3+)
                        if difficulty == "hardcore" and level >= 3:
                            ORANGE = (255, 165, 0)
                            # Trouver une position libre pour les nouveaux fantômes
                            existing_positions = [(ghost.x, ghost.y) for ghost in ghosts]
                            # Ajouter 3 fantômes orange
                            for i in range(3):
                                new_x = 12 + i
                                new_y = 9
                                # Chercher une position libre
                                while (new_x, new_y) in existing_positions:
                                    new_x += 1
                                    if new_x >= GRID_WIDTH:
                                        new_x = 0
                                        new_y += 1
                                        if new_y >= GRID_HEIGHT:
                                            new_y = 0
                                # Ajouter le fantôme orange
                                new_ghost = Ghost(new_x, new_y, ORANGE)
                                ghosts.append(new_ghost)
                                new_ghost.set_path(maze)
                                existing_positions.append((new_x, new_y))
                        # Si l'indigestion était active, la recréer dans le nouveau niveau (après l'ajout des fantômes supplémentaires)
                        if indigestion_active:
                            has_indigestion = True
                            indigestion_timer = saved_indigestion_timer
                            # Créer un fantôme d'indigestion inoffensif près de Pacman dans le nouveau niveau
                            # Chercher une position valide (pas un mur) près de Pacman
                            indigestion_ghost_x = None
                            indigestion_ghost_y = None
                            attempts = 0
                            max_attempts = 50
                            while indigestion_ghost_x is None and attempts < max_attempts:
                                attempts += 1
                                # Position aléatoire près de Pacman (à une distance de 2-5 cases)
                                angle = random.random() * 2 * math.pi
                                distance = random.randint(2, 5)
                                test_x = int(pacman.x + distance * math.cos(angle))
                                test_y = int(pacman.y + distance * math.sin(angle))
                                # S'assurer que la position est dans les limites
                                test_x = max(0, min(GRID_WIDTH - 1, test_x))
                                test_y = max(0, min(GRID_HEIGHT - 1, test_y))
                                # Vérifier que la position n'est pas un mur
                                if 0 <= test_y < GRID_HEIGHT and 0 <= test_x < GRID_WIDTH:
                                    if maze[test_y][test_x] != 1:  # Pas un mur
                                        indigestion_ghost_x = test_x
                                        indigestion_ghost_y = test_y
                            # Si on n'a pas trouvé de position valide après plusieurs tentatives, utiliser une position proche de Pacman
                            if indigestion_ghost_x is None:
                                # Essayer les positions autour de Pacman
                                for dx in range(-3, 4):
                                    for dy in range(-3, 4):
                                        test_x = pacman.x + dx
                                        test_y = pacman.y + dy
                                        if 0 <= test_y < GRID_HEIGHT and 0 <= test_x < GRID_WIDTH:
                                            if maze[test_y][test_x] != 1:  # Pas un mur
                                                indigestion_ghost_x = test_x
                                                indigestion_ghost_y = test_y
                                                break
                                    if indigestion_ghost_x is not None:
                                        break
                            # Si on a trouvé une position valide, créer le fantôme
                            if indigestion_ghost_x is not None:
                                # Utiliser la couleur la plus courante dans le niveau (après l'ajout des fantômes supplémentaires)
                                indigestion_ghost_color = get_most_common_ghost_color(ghosts, level)
                                indigestion_ghost = Ghost(indigestion_ghost_x, indigestion_ghost_y, indigestion_ghost_color, harmless=True)
                                ghosts.append(indigestion_ghost)
                        else:
                            has_indigestion = False
                            indigestion_timer = 0
                        vulnerable_timer = 0
                        ice_tiles = {}  # Réinitialiser les cases de glace au nouveau niveau
                        pacman_last_pos = (pacman.x, pacman.y)  # Réinitialiser la position précédente
                # Vérifier si Pacman mange une pacgomme (à sa position ou devant si longue vue)
                elif maze[pacman.y][pacman.x] == 3:
                    # Enregistrer la position de la pacgomme mangée pour la faire réapparaître (seulement en mode aventure)
                    if is_adventure_mode:
                        pacgomme_timers[(pacman.x, pacman.y)] = PACGOMME_RESPAWN_TIME
                    maze[pacman.y][pacman.x] = 0
                    score += 50
                    # Gagner 5 jetons pour chaque pacgomme mangée (10 si pièce mythique équipée) - sauf en mode aventure
                    if not is_adventure_mode:
                        if has_piece_mythique:
                            jeton_count += 10
                        else:
                            jeton_count += 5
                    
                    # Coup critique : "bon goût" seul donne 1%, "bon repas" seul donne 0.5%
                    if has_bon_gout:
                        # "bon goût" seul : 1% de chance de coup critique
                        crit_chance = 0.01
                        if random.random() < crit_chance:
                            # Coup critique : arc-en-ciel pendant 2 secondes et +10 jetons (20 si pièce mythique équipée)
                            is_rainbow_critique = True
                            rainbow_timer = 20  # 2 secondes à 10 FPS
                            if not is_adventure_mode:
                                if has_piece_mythique:
                                    jeton_count += 20
                                else:
                                    jeton_count += 10
                    elif has_bon_repas:
                        # "bon repas" seul : 0.5% de chance de coup critique
                        crit_chance = 0.005
                        if random.random() < crit_chance:
                            # Coup critique : arc-en-ciel pendant 2 secondes et +10 jetons (20 si pièce mythique équipée)
                            is_rainbow_critique = True
                            rainbow_timer = 20  # 2 secondes à 10 FPS
                            if not is_adventure_mode:
                                if has_piece_mythique:
                                    jeton_count += 20
                                else:
                                    jeton_count += 10
                    # Vérifier si on a atteint le seuil de jetons pour gagner une vie (100 en facile, 1000 en difficile, 2000 en hardcore, 200 sinon)
                    if difficulty == "facile":
                        jeton_threshold = 100
                    elif difficulty == "difficile":
                        jeton_threshold = 1000
                    elif difficulty == "hardcore":
                        jeton_threshold = 2000  # Pas de bonus de vie en hardcore (seuil très élevé)
                    else:
                        jeton_threshold = 200
                    if jeton_count >= jeton_threshold:
                        # En mode difficile et hardcore, on ne peut pas gagner de vies avec les jetons
                        if lives < current_max_lives and difficulty != "difficile" and difficulty != "hardcore":
                            lives += 1
                        # Mettre les jetons et couronnes dans la poche (sauf en mode aventure)
                        if not is_adventure_mode:
                            jeton_poche += jeton_count
                        crown_poche += crown_count
                        jeton_count = 0  # Réinitialiser le compteur de jetons
                        crown_count = 0  # Réinitialiser le compteur de couronnes
                    
                    # Mode difficile : bonus spécial à 4000 pacoins
                    if difficulty == "difficile" and jeton_count >= 4000:
                        # Transférer les pacoins et couronnes à la poche (sauf en mode aventure)
                        if not is_adventure_mode:
                            jeton_poche += jeton_count
                        crown_poche += crown_count
                        # Gagner 1 cœur
                        if lives < current_max_lives:
                            lives += 1
                        # Réinitialiser les compteurs
                        jeton_count = 0
                        crown_count = 0
                    
                    # Calculer la durée de vulnérabilité en fonction du niveau de "pacgum"
                    pacgum_level = capacite_items.count("pacgum") if capacite_items else 0
                    vulnerable_duration = VULNERABLE_DURATION + (pacgum_level * 10)  # +1 seconde (10 frames) par niveau
                    vulnerable_timer = vulnerable_duration
                    # Rendre tous les fantômes vulnérables (sauf les fantômes roses qui ne sont pas affectés par le bonus de pacgomme)
                    ROSE = (255, 192, 203)
                    for ghost in ghosts:
                        if not ghost.returning and ghost.color != ROSE:
                            ghost.vulnerable = True
                
                # Si longue vue est équipée, récupérer les objets dans les directions appropriées
                if has_longue_vue and len(directions) > 0:
                    for check_x, check_y in directions:
                        if 0 <= check_y < GRID_HEIGHT and 0 <= check_x < GRID_WIDTH:
                            if maze[check_y][check_x] == 2:  # Point
                                maze[check_y][check_x] = 0
                                score += 10
                                # Gagner un jeton pour chaque point mangé (2 si pièce mythique équipée) - sauf en mode aventure
                                if not is_adventure_mode:
                                    if has_piece_mythique:
                                        jeton_count += 2
                                    else:
                                        jeton_count += 1
                                
                                # Coup critique : "bon goût" seul donne 1%, "bon repas" seul donne 0.5%
                                if has_bon_gout:
                                    # "bon goût" seul : 1% de chance de coup critique
                                    crit_chance = 0.01
                                    if random.random() < crit_chance:
                                        # Coup critique : arc-en-ciel pendant 2 secondes et +10 jetons (20 si pièce mythique équipée)
                                        is_rainbow_critique = True
                                        rainbow_timer = 20  # 2 secondes à 10 FPS
                                        if not is_adventure_mode:
                                            if has_piece_mythique:
                                                jeton_count += 20
                                            else:
                                                jeton_count += 10
                                elif has_bon_repas:
                                    # "bon repas" seul : 0.5% de chance de coup critique
                                    crit_chance = 0.005
                                    if random.random() < crit_chance:
                                        # Coup critique : arc-en-ciel pendant 2 secondes et +10 jetons (20 si pièce mythique équipée)
                                        is_rainbow_critique = True
                                        rainbow_timer = 20  # 2 secondes à 10 FPS
                                        if not is_adventure_mode:
                                            if has_piece_mythique:
                                                jeton_count += 20
                                            else:
                                                jeton_count += 10
                                
                                # Calculer la chance d'indigestion en fonction de "pas d'indigestion" et de la capacité "indigestion"
                                base_indigestion_chance = 0.005  # 0.5% de base
                                if has_pas_indigestion:
                                    base_indigestion_chance = 0.0025  # Divisée par 2 si "pas d'indigestion" équipé
                                
                                # Réduire la chance selon le niveau de la capacité "indigestion" (10% de réduction par niveau)
                                indigestion_capacity_level = capacite_items.count("indigestion") if capacite_items else 0
                                reduction_factor = 1.0 - (indigestion_capacity_level * 0.1)  # Réduction de 10% par niveau
                                reduction_factor = max(0.0, reduction_factor)  # Ne peut pas être négatif
                                indigestion_chance = base_indigestion_chance * reduction_factor
                                
                                if random.random() < indigestion_chance and not has_indigestion:
                                    # Indigestion : perdre 10 jetons et devenir vert pendant 1 minute
                                    jeton_count = max(0, jeton_count - 10)
                                    has_indigestion = True
                                    indigestion_timer = 600  # 1 minute (60 secondes = 600 frames à 10 FPS)
                                    # Vérifier qu'il n'y a pas déjà un fantôme d'indigestion
                                    if not any(ghost.harmless for ghost in ghosts):
                                        # Créer un fantôme d'indigestion inoffensif près de Pacman
                                        # Chercher une position valide (pas un mur) près de Pacman
                                        indigestion_ghost_x = None
                                        indigestion_ghost_y = None
                                        attempts = 0
                                        max_attempts = 50
                                        while indigestion_ghost_x is None and attempts < max_attempts:
                                            attempts += 1
                                            # Position aléatoire près de Pacman (à une distance de 2-5 cases)
                                            angle = random.random() * 2 * math.pi
                                            distance = random.randint(2, 5)
                                            test_x = int(pacman.x + distance * math.cos(angle))
                                            test_y = int(pacman.y + distance * math.sin(angle))
                                            # S'assurer que la position est dans les limites
                                            test_x = max(0, min(GRID_WIDTH - 1, test_x))
                                            test_y = max(0, min(GRID_HEIGHT - 1, test_y))
                                            # Vérifier que la position n'est pas un mur
                                            if 0 <= test_y < GRID_HEIGHT and 0 <= test_x < GRID_WIDTH:
                                                if maze[test_y][test_x] != 1:  # Pas un mur
                                                    indigestion_ghost_x = test_x
                                                    indigestion_ghost_y = test_y
                                        # Si on n'a pas trouvé de position valide après plusieurs tentatives, utiliser une position proche de Pacman
                                        if indigestion_ghost_x is None:
                                            # Essayer les positions autour de Pacman
                                            for dx in range(-3, 4):
                                                for dy in range(-3, 4):
                                                    test_x = pacman.x + dx
                                                    test_y = pacman.y + dy
                                                    if 0 <= test_y < GRID_HEIGHT and 0 <= test_x < GRID_WIDTH:
                                                        if maze[test_y][test_x] != 1:  # Pas un mur
                                                            indigestion_ghost_x = test_x
                                                            indigestion_ghost_y = test_y
                                                            break
                                                if indigestion_ghost_x is not None:
                                                    break
                                        # Si on a trouvé une position valide, créer le fantôme
                                        if indigestion_ghost_x is not None:
                                            # Utiliser la couleur la plus courante dans le niveau
                                            indigestion_ghost_color = get_most_common_ghost_color(ghosts, level)
                                            indigestion_ghost = Ghost(indigestion_ghost_x, indigestion_ghost_y, indigestion_ghost_color, harmless=True)
                                            ghosts.append(indigestion_ghost)
                                # Vérifier si on a atteint le seuil de jetons pour gagner une vie
                                if difficulty == "facile":
                                    jeton_threshold = 100
                                elif difficulty == "difficile":
                                    jeton_threshold = 1000
                                else:
                                    jeton_threshold = 200
                                if jeton_count >= jeton_threshold:
                                    # En mode difficile et hardcore, on ne peut pas gagner de vies avec les jetons
                                    if lives < MAX_LIVES and difficulty != "difficile" and difficulty != "hardcore":
                                        lives += 1
                                    if not is_adventure_mode:
                                        jeton_poche += jeton_count
                                    crown_poche += crown_count
                                    jeton_count = 0
                                    crown_count = 0
                                
                                # Mode difficile : bonus spécial à 4000 pacoins
                                if difficulty == "difficile" and jeton_count >= 4000:
                                    # Transférer les pacoins et couronnes à la poche (sauf en mode aventure)
                                    if not is_adventure_mode:
                                        jeton_poche += jeton_count
                                    crown_poche += crown_count
                                    # Gagner 1 cœur
                                    if lives < MAX_LIVES:
                                        lives += 1
                                    # Réinitialiser les compteurs
                                    jeton_count = 0
                                    crown_count = 0
                                
                                if count_points(maze) == 0:
                                    level += 1
                                    # Récompense au niveau 17 en mode facile
                                    if difficulty == "facile" and level == 17:
                                        crown_poche += 1  # Gagner 1 couronne
                                        jeton_poche += 50  # Gagner 50 pacoins
                                    # Récompense au niveau 25 en mode moyen
                                    if difficulty == "moyen" and level == 25:
                                        crown_poche += 55  # Gagner 55 couronnes
                                        jeton_poche += 1000  # Gagner 1000 pacoins
                                    # Récompense au niveau 30 en mode difficile
                                    if difficulty == "difficile" and level == 30:
                                        crown_poche += 60  # Gagner 60 couronnes
                                        jeton_poche += 1500  # Gagner 1500 pacoins
                                    # Récompense au niveau 50 en mode hardcore
                                    if difficulty == "hardcore" and level == 50:
                                        crown_poche += 1000  # Gagner 1000 couronnes
                                        jeton_poche += 200000  # Gagner 200000 pacoins
                                    # Vérifier si on a gagné au niveau 24 (en moyenne)
                                    if level == 24:
                                        won = True
                                        crown_poche += 10  # Gagner 10 couronnes
                                        jeton_poche += 500  # Gagner 500 pacoins
                                        # Arrêter la musique si elle est en cours
                                        if music_playing:
                                            pygame.mixer.music.stop()
                                            music_playing = False
                                    # Vérifier si on a gagné (niveau 20 en mode facile)
                                    if difficulty == "facile" and level >= 20:
                                        won = True
                                        # Arrêter la musique si elle est en cours
                                        if music_playing:
                                            pygame.mixer.music.stop()
                                            music_playing = False
                                    # Vérifier si on a gagné au niveau 20 sans difficulté choisie
                                    if difficulty is None and level >= 20:
                                        won = True
                                        # Arrêter la musique si elle est en cours
                                        if music_playing:
                                            pygame.mixer.music.stop()
                                            music_playing = False
                                        crown_poche += 10  # Gagner 10 couronnes
                                        jeton_poche += 500  # Gagner 500 pacoins
                                    level_transition = True
                                    level_transition_timer = 60
                                    # Sauvegarder l'état de l'indigestion avant de passer au niveau suivant
                                    indigestion_active = has_indigestion and indigestion_timer > 0
                                    saved_indigestion_timer = indigestion_timer
                                    # Supprimer le fantôme d'indigestion s'il existe avant de passer au niveau suivant
                                    ghosts[:] = [ghost for ghost in ghosts if not ghost.harmless]
                                    maze, pacman, ghosts = start_next_level(level)
                                    # Ajouter un fantôme bleu supplémentaire pour le mode moyen (niveau 3+)
                                    if difficulty == "moyen" and level >= 3:
                                        new_ghost = Ghost(12, 9, BLUE)
                                        ghosts.append(new_ghost)
                                        new_ghost.set_path(maze)
                                    # Ajouter 2 fantômes orange supplémentaires pour le mode difficile (niveau 3+)
                                    if difficulty == "difficile" and level >= 3:
                                        ORANGE = (255, 165, 0)
                                        # Trouver une position libre pour les nouveaux fantômes
                                        existing_positions = [(ghost.x, ghost.y) for ghost in ghosts]
                                        new_x = 12
                                        new_y = 9
                                        # Chercher une position libre
                                        while (new_x, new_y) in existing_positions:
                                            new_x += 1
                                            if new_x >= GRID_WIDTH:
                                                new_x = 0
                                                new_y += 1
                                        new_ghost1 = Ghost(new_x, new_y, ORANGE)
                                        ghosts.append(new_ghost1)
                                        # Chercher une autre position libre pour le deuxième fantôme
                                        existing_positions.append((new_x, new_y))
                                        new_x2 = new_x + 1
                                        new_y2 = new_y
                                        while (new_x2, new_y2) in existing_positions:
                                            new_x2 += 1
                                            if new_x2 >= GRID_WIDTH:
                                                new_x2 = 0
                                                new_y2 += 1
                                        new_ghost2 = Ghost(new_x2, new_y2, ORANGE)
                                        ghosts.append(new_ghost2)
                                        new_ghost2.set_path(maze)
                                    # Ajouter 3 fantômes orange supplémentaires pour le mode hardcore (niveau 3+)
                                    if difficulty == "hardcore" and level >= 3:
                                        ORANGE = (255, 165, 0)
                                        # Trouver une position libre pour les nouveaux fantômes
                                        existing_positions = [(ghost.x, ghost.y) for ghost in ghosts]
                                        # Ajouter 3 fantômes orange
                                        for i in range(3):
                                            new_x = 12 + i
                                            new_y = 9
                                            # Chercher une position libre
                                            while (new_x, new_y) in existing_positions:
                                                new_x += 1
                                                if new_x >= GRID_WIDTH:
                                                    new_x = 0
                                                    new_y += 1
                                                    if new_y >= GRID_HEIGHT:
                                                        new_y = 0
                                            # Ajouter le fantôme orange
                                            new_ghost = Ghost(new_x, new_y, ORANGE)
                                            ghosts.append(new_ghost)
                                            new_ghost.set_path(maze)
                                            existing_positions.append((new_x, new_y))
                                    # Si l'indigestion était active, la recréer dans le nouveau niveau (après l'ajout des fantômes supplémentaires)
                                    if indigestion_active:
                                        has_indigestion = True
                                        indigestion_timer = saved_indigestion_timer
                                        # Créer un fantôme d'indigestion inoffensif près de Pacman dans le nouveau niveau
                                        # Chercher une position valide (pas un mur) près de Pacman
                                        indigestion_ghost_x = None
                                        indigestion_ghost_y = None
                                        attempts = 0
                                        max_attempts = 50
                                        while indigestion_ghost_x is None and attempts < max_attempts:
                                            attempts += 1
                                            # Position aléatoire près de Pacman (à une distance de 2-5 cases)
                                            angle = random.random() * 2 * math.pi
                                            distance = random.randint(2, 5)
                                            test_x = int(pacman.x + distance * math.cos(angle))
                                            test_y = int(pacman.y + distance * math.sin(angle))
                                            # S'assurer que la position est dans les limites
                                            test_x = max(0, min(GRID_WIDTH - 1, test_x))
                                            test_y = max(0, min(GRID_HEIGHT - 1, test_y))
                                            # Vérifier que la position n'est pas un mur
                                            if 0 <= test_y < GRID_HEIGHT and 0 <= test_x < GRID_WIDTH:
                                                if maze[test_y][test_x] != 1:  # Pas un mur
                                                    indigestion_ghost_x = test_x
                                                    indigestion_ghost_y = test_y
                                        # Si on n'a pas trouvé de position valide après plusieurs tentatives, utiliser une position proche de Pacman
                                        if indigestion_ghost_x is None:
                                            # Essayer les positions autour de Pacman
                                            for dx in range(-3, 4):
                                                for dy in range(-3, 4):
                                                    test_x = pacman.x + dx
                                                    test_y = pacman.y + dy
                                                    if 0 <= test_y < GRID_HEIGHT and 0 <= test_x < GRID_WIDTH:
                                                        if maze[test_y][test_x] != 1:  # Pas un mur
                                                            indigestion_ghost_x = test_x
                                                            indigestion_ghost_y = test_y
                                                            break
                                                if indigestion_ghost_x is not None:
                                                    break
                                        # Si on a trouvé une position valide, créer le fantôme
                                        if indigestion_ghost_x is not None:
                                            # Utiliser la couleur la plus courante dans le niveau (après l'ajout des fantômes supplémentaires)
                                            indigestion_ghost_color = get_most_common_ghost_color(ghosts, level)
                                            indigestion_ghost = Ghost(indigestion_ghost_x, indigestion_ghost_y, indigestion_ghost_color, harmless=True)
                                            ghosts.append(indigestion_ghost)
                                    else:
                                        has_indigestion = False
                                        indigestion_timer = 0
                                    vulnerable_timer = 0
                                    ice_tiles = {}  # Réinitialiser les cases de glace au nouveau niveau
                                    pacman_last_pos = (pacman.x, pacman.y)  # Réinitialiser la position précédente
                            elif maze[check_y][check_x] == 3:  # Pacgomme
                                # Enregistrer la position de la pacgomme mangée pour la faire réapparaître (seulement en mode aventure)
                                if is_adventure_mode:
                                    pacgomme_timers[(check_x, check_y)] = PACGOMME_RESPAWN_TIME
                                maze[check_y][check_x] = 0
                                score += 50
                                # Gagner 5 jetons pour chaque pacgomme mangée (10 si pièce mythique équipée) - sauf en mode aventure
                                if not is_adventure_mode:
                                    if has_piece_mythique:
                                        jeton_count += 10
                                    else:
                                        jeton_count += 5
                                
                                # Coup critique : "bon goût" seul donne 1%, "bon repas" seul donne 0.5%
                                if has_bon_gout:
                                    # "bon goût" seul : 1% de chance de coup critique
                                    crit_chance = 0.01
                                    if random.random() < crit_chance:
                                        # Coup critique : arc-en-ciel pendant 2 secondes et +10 jetons (20 si pièce mythique équipée)
                                        is_rainbow_critique = True
                                        rainbow_timer = 20  # 2 secondes à 10 FPS
                                        if not is_adventure_mode:
                                            if has_piece_mythique:
                                                jeton_count += 20
                                            else:
                                                jeton_count += 10
                                elif has_bon_repas:
                                    # "bon repas" seul : 0.5% de chance de coup critique
                                    crit_chance = 0.005
                                    if random.random() < crit_chance:
                                        # Coup critique : arc-en-ciel pendant 2 secondes et +10 jetons (20 si pièce mythique équipée)
                                        is_rainbow_critique = True
                                        rainbow_timer = 20  # 2 secondes à 10 FPS
                                        if not is_adventure_mode:
                                            if has_piece_mythique:
                                                jeton_count += 20
                                            else:
                                                jeton_count += 10
                                # Vérifier si on a atteint le seuil de jetons pour gagner une vie
                                if difficulty == "facile":
                                    jeton_threshold = 100
                                elif difficulty == "difficile":
                                    jeton_threshold = 1000
                                else:
                                    jeton_threshold = 200
                                if jeton_count >= jeton_threshold:
                                    # En mode difficile et hardcore, on ne peut pas gagner de vies avec les jetons
                                    if lives < MAX_LIVES and difficulty != "difficile" and difficulty != "hardcore":
                                        lives += 1
                                    if not is_adventure_mode:
                                        jeton_poche += jeton_count
                                    crown_poche += crown_count
                                    jeton_count = 0
                                    crown_count = 0
                                # Calculer la durée de vulnérabilité en fonction du niveau de "pacgum"
                                pacgum_level = capacite_items.count("pacgum") if capacite_items else 0
                                vulnerable_duration = VULNERABLE_DURATION + (pacgum_level * 10)  # +1 seconde (10 frames) par niveau
                                vulnerable_timer = vulnerable_duration
                                # Rendre tous les fantômes vulnérables (sauf les fantômes roses qui ne sont pas affectés par le bonus de pacgomme)
                                ROSE = (255, 192, 203)
                                for ghost in ghosts:
                                    if not ghost.returning and ghost.color != ROSE:
                                        ghost.vulnerable = True
                
                # Vérifier si tous les points sont collectés
                if count_points(maze) == 0:
                    # Passer au niveau suivant
                    level += 1
                    # Récompense au niveau 17 en mode facile
                    if difficulty == "facile" and level == 17:
                        crown_poche += 1  # Gagner 1 couronne
                        jeton_poche += 50  # Gagner 50 pacoins
                    # Récompense au niveau 25 en mode moyen
                    if difficulty == "moyen" and level == 25:
                        crown_poche += 55  # Gagner 55 couronnes
                        jeton_poche += 1000  # Gagner 1000 pacoins
                    # Récompense au niveau 30 en mode difficile
                    if difficulty == "difficile" and level == 30:
                        crown_poche += 60  # Gagner 60 couronnes
                        jeton_poche += 1500  # Gagner 1500 pacoins
                    # Récompense au niveau 50 en mode hardcore
                    if difficulty == "hardcore" and level == 50:
                        crown_poche += 1000  # Gagner 1000 couronnes
                        jeton_poche += 200000  # Gagner 200000 pacoins
                    # Vérifier si on a gagné au niveau 24 (en moyenne)
                    if level == 24:
                        won = True
                        crown_poche += 10  # Gagner 10 couronnes
                        jeton_poche += 500  # Gagner 500 pacoins
                        # Arrêter la musique si elle est en cours
                        if music_playing:
                            pygame.mixer.music.stop()
                            music_playing = False
                    # Vérifier si on a gagné (niveau 20 en mode facile)
                    if difficulty == "facile" and level >= 20:
                        won = True
                        # Arrêter la musique si elle est en cours
                        if music_playing:
                            pygame.mixer.music.stop()
                            music_playing = False
                    # Vérifier si on a gagné au niveau 20 sans difficulté choisie
                    if difficulty is None and level >= 20:
                        won = True
                        # Arrêter la musique si elle est en cours
                        if music_playing:
                            pygame.mixer.music.stop()
                            music_playing = False
                        crown_poche += 10  # Gagner 10 couronnes
                        jeton_poche += 500  # Gagner 500 pacoins
                    level_transition = True
                    level_transition_timer = 60  # 2 secondes de transition
                    # Sauvegarder l'état de l'indigestion avant de passer au niveau suivant
                    indigestion_active = has_indigestion and indigestion_timer > 0
                    saved_indigestion_timer = indigestion_timer
                    # Supprimer le fantôme d'indigestion s'il existe avant de passer au niveau suivant
                    ghosts[:] = [ghost for ghost in ghosts if not ghost.harmless]
                    maze, pacman, ghosts = start_next_level(level)
                    # Ajouter un fantôme bleu supplémentaire pour le mode moyen (niveau 3+)
                    if difficulty == "moyen" and level >= 3:
                        new_ghost = Ghost(12, 9, BLUE)
                        ghosts.append(new_ghost)
                        new_ghost.set_path(maze)
                    # Ajouter 2 fantômes orange supplémentaires pour le mode difficile (niveau 3+)
                    if difficulty == "difficile" and level >= 3:
                        ORANGE = (255, 165, 0)
                        # Trouver une position libre pour les nouveaux fantômes
                        existing_positions = [(ghost.x, ghost.y) for ghost in ghosts]
                        new_x = 12
                        new_y = 9
                        # Chercher une position libre
                        while (new_x, new_y) in existing_positions:
                            new_x += 1
                            if new_x >= GRID_WIDTH:
                                new_x = 0
                                new_y += 1
                        new_ghost1 = Ghost(new_x, new_y, ORANGE)
                        ghosts.append(new_ghost1)
                        new_ghost1.set_path(maze)
                        # Chercher une autre position libre pour le deuxième fantôme
                        existing_positions.append((new_x, new_y))
                        new_x2 = new_x + 1
                        new_y2 = new_y
                        while (new_x2, new_y2) in existing_positions:
                            new_x2 += 1
                            if new_x2 >= GRID_WIDTH:
                                new_x2 = 0
                                new_y2 += 1
                        new_ghost2 = Ghost(new_x2, new_y2, ORANGE)
                        ghosts.append(new_ghost2)
                        new_ghost2.set_path(maze)
                    # Ajouter 3 fantômes orange supplémentaires pour le mode hardcore (niveau 3+)
                    if difficulty == "hardcore" and level >= 3:
                        ORANGE = (255, 165, 0)
                        # Trouver une position libre pour les nouveaux fantômes
                        existing_positions = [(ghost.x, ghost.y) for ghost in ghosts]
                        # Ajouter 3 fantômes orange
                        for i in range(3):
                            new_x = 12 + i
                            new_y = 9
                            # Chercher une position libre
                            while (new_x, new_y) in existing_positions:
                                new_x += 1
                                if new_x >= GRID_WIDTH:
                                    new_x = 0
                                    new_y += 1
                                    if new_y >= GRID_HEIGHT:
                                        new_y = 0
                            # Ajouter le fantôme orange
                            new_ghost = Ghost(new_x, new_y, ORANGE)
                            ghosts.append(new_ghost)
                            new_ghost.set_path(maze)
                            existing_positions.append((new_x, new_y))
                    # Si l'indigestion était active, la recréer dans le nouveau niveau (après l'ajout des fantômes supplémentaires)
                    if indigestion_active:
                        has_indigestion = True
                        indigestion_timer = saved_indigestion_timer
                        # Créer un fantôme d'indigestion inoffensif près de Pacman dans le nouveau niveau
                        # Chercher une position valide (pas un mur) près de Pacman
                        indigestion_ghost_x = None
                        indigestion_ghost_y = None
                        attempts = 0
                        max_attempts = 50
                        while indigestion_ghost_x is None and attempts < max_attempts:
                            attempts += 1
                            # Position aléatoire près de Pacman (à une distance de 2-5 cases)
                            angle = random.random() * 2 * math.pi
                            distance = random.randint(2, 5)
                            test_x = int(pacman.x + distance * math.cos(angle))
                            test_y = int(pacman.y + distance * math.sin(angle))
                            # S'assurer que la position est dans les limites
                            test_x = max(0, min(GRID_WIDTH - 1, test_x))
                            test_y = max(0, min(GRID_HEIGHT - 1, test_y))
                            # Vérifier que la position n'est pas un mur
                            if 0 <= test_y < GRID_HEIGHT and 0 <= test_x < GRID_WIDTH:
                                if maze[test_y][test_x] != 1:  # Pas un mur
                                    indigestion_ghost_x = test_x
                                    indigestion_ghost_y = test_y
                        # Si on n'a pas trouvé de position valide après plusieurs tentatives, utiliser une position proche de Pacman
                        if indigestion_ghost_x is None:
                            # Essayer les positions autour de Pacman
                            for dx in range(-3, 4):
                                for dy in range(-3, 4):
                                    test_x = pacman.x + dx
                                    test_y = pacman.y + dy
                                    if 0 <= test_y < GRID_HEIGHT and 0 <= test_x < GRID_WIDTH:
                                        if maze[test_y][test_x] != 1:  # Pas un mur
                                            indigestion_ghost_x = test_x
                                            indigestion_ghost_y = test_y
                                            break
                                if indigestion_ghost_x is not None:
                                    break
                        # Si on a trouvé une position valide, créer le fantôme
                        if indigestion_ghost_x is not None:
                            # Utiliser la couleur la plus courante dans le niveau (après l'ajout des fantômes supplémentaires)
                            indigestion_ghost_color = get_most_common_ghost_color(ghosts, level)
                            indigestion_ghost = Ghost(indigestion_ghost_x, indigestion_ghost_y, indigestion_ghost_color, harmless=True)
                            ghosts.append(indigestion_ghost)
                    else:
                        has_indigestion = False
                        indigestion_timer = 0
                    vulnerable_timer = 0
                    ice_tiles = {}  # Réinitialiser les cases de glace au nouveau niveau
                    fire_tiles = {}  # Réinitialiser les cases de feu au nouveau niveau
                    fire_active = False  # Réinitialiser l'activation du feu
                    fire_timer = 0  # Réinitialiser le timer du feu
                    gadget_cooldown = 0  # Réinitialiser le temps de recharge du gadget
                    mort_cooldown = 0  # Réinitialiser le temps de recharge de "mort"
                    bombe_cooldown = 0  # Réinitialiser le temps de recharge de "bombe téléguidée"
                    bombe_active = False  # Réinitialiser l'état de la bombe
                    pacman_frozen = False  # Réinitialiser l'état de gel de Pacman
                    bombe_timer = 0  # Réinitialiser le timer de la bombe
                    # Les pièges persistent entre les niveaux et les retours
                    portal1_pos = None  # Réinitialiser les portails
                    portal2_pos = None
                    portal_use_count = 0
                    # Enlever le mur créé du maze si nécessaire
                    if mur_pos is not None:
                        if isinstance(mur_pos, list):
                            # Si c'est une liste (cas avec bric), enlever tous les murs
                            for mur_x, mur_y in mur_pos:
                                if 0 <= mur_y < GRID_HEIGHT and 0 <= mur_x < GRID_WIDTH:
                                    maze[mur_y][mur_x] = 0  # Remettre en chemin
                        else:
                            # Si c'est un tuple (comportement normal)
                            mur_x, mur_y = mur_pos
                            if 0 <= mur_y < GRID_HEIGHT and 0 <= mur_x < GRID_WIDTH:
                                maze[mur_y][mur_x] = 0  # Remettre en chemin
                    mur_pos = None  # Réinitialiser le mur
                    mur_use_count = 0
                    pacman_last_pos = (pacman.x, pacman.y)  # Réinitialiser la position précédente
                    # Réinitialiser les flee_timer et immobilized_timer des fantômes
                    for ghost in ghosts:
                        ghost.flee_timer = 0
                        ghost.immobilized_timer = 0
                
                # Mettre à jour le timer de vulnérabilité
                if vulnerable_timer > 0:
                    vulnerable_timer -= 1
                    if vulnerable_timer == 0:
                        # Les fantômes redeviennent normaux
                        for ghost in ghosts:
                            if not ghost.returning:
                                ghost.vulnerable = False
                
                # Décrémenter le flee_timer de tous les fantômes
                for ghost in ghosts:
                    if ghost.flee_timer > 0:
                        ghost.flee_timer -= 1
                
                # Mettre à jour les fantômes
                ghosts_to_remove = []  # Liste des fantômes à supprimer en mode aventure
                for ghost in ghosts:
                    # Vérifier si le fantôme marche sur un piège
                    ghost_pos = (ghost.x, ghost.y)
                    ORANGE = (255, 165, 0)
                    ROSE = (255, 192, 203)
                    if ghost_pos in pieges and not ghost.eyes and not ghost.harmless and ghost.color != ORANGE and ghost.color != ROSE:
                        # Le fantôme marche sur un piège, l'immobiliser
                        if ghost.immobilized_timer == 0:  # Ne pas réinitialiser si déjà immobilisé
                            # Calculer le bonus de "piquant" si équipé
                            has_piquant_capacity = (('capacite1' in inventaire_items and inventaire_items['capacite1'].get('type') == 'piquant') or
                                                   ('capacite2' in inventaire_items and inventaire_items['capacite2'].get('type') == 'piquant'))
                            piquant_level = capacite_items.count("piquant") if capacite_items else 0
                            piquant_bonus = piquant_level * 10 if has_piquant_capacity else 0  # 1 seconde = 10 frames par niveau
                            ghost.immobilized_timer = PIEGE_IMMOBILISATION_DURATION + piquant_bonus  # 10 secondes + bonus
                            # Retirer le piège après activation (un piège ne peut être utilisé qu'une fois)
                            del pieges[ghost_pos]
                    
                    # Décrémenter le timer d'immobilisation
                    if ghost.immobilized_timer > 0:
                        ghost.immobilized_timer -= 1
                    
                    # Vérifier si le fantôme est sur une case de feu
                    is_on_fire = ghost_pos in fire_tiles
                    
                    if is_on_fire and not ghost.eyes and not ghost.harmless:
                        # Le fantôme touche le feu, le faire fuir (durée calculée selon si "flamme" est équipé)
                        ghost.flee_timer = calculate_fire_duration(inventaire_items, FIRE_DURATION)
                    
                    # Si le fantôme est immobilisé, ne pas le mettre à jour
                    if ghost.immobilized_timer > 0:
                        # Le fantôme est immobilisé, ne pas le déplacer
                        continue
                    
                    # Vérifier si le fantôme est sur une case de glace
                    is_on_ice = ghost_pos in ice_tiles
                    
                    # Vérifier si "givre" est équipé avec "glace"
                    has_glace = ('pouvoir' in inventaire_items and 
                                inventaire_items['pouvoir'].get('type') == 'glace')
                    has_givre = (('objet0' in inventaire_items and inventaire_items['objet0'].get('type') == 'givre') or
                                ('objet1' in inventaire_items and inventaire_items['objet1'].get('type') == 'givre') or
                                ('objet2' in inventaire_items and inventaire_items['objet2'].get('type') == 'givre'))
                    # Si "givre" est équipé avec "glace", ralentissement plus fort (5 frames au lieu de 3)
                    ice_slowdown_threshold = 5 if (has_glace and has_givre) else 3
                    
                    if is_on_ice:
                        # Ralentissement selon si "givre" est équipé avec "glace"
                        ghost.ice_slowdown += 1
                        if ghost.ice_slowdown >= ice_slowdown_threshold:
                            ghost.update(maze, (pacman.x, pacman.y))
                            ghost.ice_slowdown = 0
                    else:
                        # Déplacement normal
                        ghost.ice_slowdown = 0
                        ghost.update(maze, (pacman.x, pacman.y))
                    
                    # Vérifier si "lunette" est équipée dans un slot capacité
                    has_lunette_capacity = (('capacite1' in inventaire_items and inventaire_items['capacite1'].get('type') == 'lunette') or
                                           ('capacite2' in inventaire_items and inventaire_items['capacite2'].get('type') == 'lunette'))
                    lunette_level = capacite_items.count("lunette") if capacite_items else 0
                    # La distance de base est 1, augmentée de 1 par niveau de lunette si équipée avec longue vue
                    distance = 1
                    if has_longue_vue and has_lunette_capacity:
                        distance = 1 + lunette_level  # Distance = 1 + niveau de lunette
                    
                    # Calculer les directions pour manger les fantômes
                    directions = []
                    if is_double_longue_vue:
                        # Toutes les directions avec la distance augmentée par lunette
                        for d in range(1, distance + 1):
                            directions.append((pacman.x + d, pacman.y))  # Droite
                            directions.append((pacman.x - d, pacman.y))  # Gauche
                            directions.append((pacman.x, pacman.y + d))  # Bas
                            directions.append((pacman.x, pacman.y - d))  # Haut
                        # Gérer la téléportation aux bords pour chaque direction
                        for i, (dx, dy) in enumerate(directions):
                            if dx < 0:
                                directions[i] = (GRID_WIDTH - 1, dy)
                            elif dx >= GRID_WIDTH:
                                directions[i] = (0, dy)
                    elif has_longue_vue and pacman.direction != (0, 0):
                        # Devant pour la longue vue simple avec distance augmentée par lunette
                        for d in range(1, distance + 1):
                            dir_x = pacman.x + pacman.direction[0] * d
                            dir_y = pacman.y + pacman.direction[1] * d
                            # Gérer la téléportation aux bords
                            if dir_x < 0:
                                dir_x = GRID_WIDTH - 1
                            elif dir_x >= GRID_WIDTH:
                                dir_x = 0
                            directions.append((dir_x, dir_y))
                    
                    # Si longue vue est équipée et le fantôme est dans une direction valide ET vulnérable, on peut le manger
                    # Pour manger un fantôme, il faut toujours qu'il soit vulnérable (après avoir mangé une pacgomme)
                    # Les fantômes roses ne peuvent pas être mangés par la longue vue
                    ROSE = (255, 192, 203)
                    if has_longue_vue and len(directions) > 0:
                        ghost_in_range = (ghost.x, ghost.y) in directions
                        if ghost_in_range and not ghost.eyes and ghost.vulnerable and ghost.color != ROSE:
                            # En mode aventure, supprimer le fantôme définitivement (pas de réapparition)
                            if is_adventure_mode:
                                # Supprimer le fantôme immédiatement en mode aventure
                                ghosts.remove(ghost)
                                continue  # Passer au fantôme suivant
                            # Manger le fantôme vulnérable avec longue vue (mode normal)
                            score += 300
                            if difficulty == "facile":
                                jeton_threshold = 100
                            elif difficulty == "difficile":
                                jeton_threshold = 1000
                            elif difficulty == "hardcore":
                                jeton_threshold = 2000
                            else:
                                jeton_threshold = 200
                            if jeton_count >= jeton_threshold:
                                # En mode difficile et hardcore, on ne peut pas gagner de vies avec les jetons
                                    if lives < MAX_LIVES and difficulty != "difficile" and difficulty != "hardcore":
                                        lives += 1
                                    if not is_adventure_mode:
                                        jeton_poche += jeton_count
                                    crown_poche += crown_count
                                    jeton_count = 0
                                    crown_count = 0
                            # En mode aventure, marquer le fantôme pour suppression définitive (pas de réapparition)
                            if is_adventure_mode:
                                # Marquer le fantôme pour suppression (on le supprimera après la boucle)
                                ghosts_to_remove.append(ghost)
                                continue  # Passer au fantôme suivant
                            crown_timer = 30
                            crown_count += 1
                            if last_ghost_time > 0:
                                grande_couronne_count += 1
                            last_ghost_time = 100
                            ghost.eyes = True
                            ghost.vulnerable = False
                            ghost.returning = False
                            continue  # Passer au fantôme suivant
                    
                    # Vérifier collision avec Pacman (ignorer si invincible)
                    # Si longue vue est équipée et le fantôme est dans une direction adjacente (pas sur la même case), on est protégé
                    # Pour la double longue vue, protection dans les 4 directions adjacentes même sans pacgomme
                    # Mais si le fantôme arrive directement sur la case de Pacman, on perd une vie
                    if has_longue_vue and len(directions) > 0:
                        ghost_in_range = (ghost.x, ghost.y) in directions
                        if ghost_in_range:
                            # Le fantôme est dans une direction adjacente couverte, on est protégé, pas de collision
                            continue
                    
                    # Vérifier collision : même case OU cases adjacentes avec directions opposées
                    collision = False
                    # Collision sur la même case
                    if ghost.x == pacman.x and ghost.y == pacman.y:
                        collision = True
                    # Collision sur cases adjacentes si les deux se dirigent l'un vers l'autre
                    elif invincibility_timer == 0 and not super_vie_active:
                        # Calculer la direction du fantôme vers Pacman
                        dx = pacman.x - ghost.x
                        dy = pacman.y - ghost.y
                        # Vérifier si le fantôme est adjacent à Pacman (distance de 1 case)
                        if abs(dx) + abs(dy) == 1:
                            # Normaliser la direction (dx et dy doivent être -1, 0, ou 1)
                            if dx != 0:
                                dx = 1 if dx > 0 else -1
                            if dy != 0:
                                dy = 1 if dy > 0 else -1
                            # Vérifier si le fantôme se dirige vers Pacman (direction du fantôme = direction vers Pacman)
                            ghost_going_to_pacman = (ghost.direction[0] == dx and ghost.direction[1] == dy)
                            # Vérifier si Pacman se dirige vers le fantôme (direction de Pacman = direction opposée vers le fantôme)
                            pacman_going_to_ghost = (pacman.direction[0] == -dx and pacman.direction[1] == -dy)
                            # Collision si les deux se dirigent l'un vers l'autre
                            if ghost_going_to_pacman and pacman_going_to_ghost:
                                collision = True
                    
                    if collision and invincibility_timer == 0 and not super_vie_active:
                        # Si le fantôme est en mode yeux, pas de collision
                        if ghost.eyes:
                            continue
                        # Si le fantôme est vulnérable, Pacman le mange
                        if ghost.vulnerable:
                            # En mode aventure, gérer les fantômes spéciaux qui nécessitent plusieurs coups
                            if is_adventure_mode:
                                # Incrémenter le compteur de coups reçus
                                ghost.hits_taken += 1
                                # Si le fantôme a reçu assez de coups, le tuer définitivement (pas de réapparition)
                                if ghost.hits_taken >= ghost.hits_required:
                                    # Marquer le fantôme pour suppression (on le supprimera après la boucle)
                                    # Ne pas enregistrer dans ghost_timers pour qu'il ne réapparaisse pas
                                    ghosts_to_remove.append(ghost)
                                else:
                                    # Le fantôme n'est pas encore mort, juste rendre non-vulnérable temporairement
                                    ghost.vulnerable = False
                                    # Réinitialiser la position du fantôme à sa position de départ
                                    ghost.x = ghost.start_x
                                    ghost.y = ghost.start_y
                                continue  # Passer au fantôme suivant
                            # Pacman mange le fantôme - transformer en yeux (mode normal)
                            score += 300  # 200 points de base + 100 points bonus
                            # Gagner 30 XP pour le passe de combat
                            # S'assurer que battle_pass_xp est un entier
                            if not isinstance(battle_pass_xp, (int, float)):
                                battle_pass_xp = 0
                            xp_gained = 30
                            # Si le doubleur d'XP est actif, doubler l'XP
                            if xp_doubler_active:
                                xp_gained *= 2
                            # Calculer le nouveau XP
                            new_xp = int(battle_pass_xp) + xp_gained
                            # Limiter l'XP au niveau 30 si toutes les récompenses ne sont pas récupérées
                            MAX_BATTLE_PASS_LEVEL = 30
                            XP_PER_LEVEL = 100
                            MAX_BATTLE_PASS_XP = MAX_BATTLE_PASS_LEVEL * XP_PER_LEVEL
                            if new_xp >= MAX_BATTLE_PASS_XP:
                                # Vérifier si toutes les récompenses ont été récupérées
                                if not all_battle_pass_rewards_claimed(battle_pass_claimed_rewards, used_stars, MAX_BATTLE_PASS_LEVEL):
                                    # Bloquer l'XP au maximum du niveau 30
                                    new_xp = MAX_BATTLE_PASS_XP
                            battle_pass_xp = new_xp
                            vulnerable_ghosts_eaten_this_game += 1  # Compter le fantôme mangé
                            # Sauvegarder l'XP gagné
                            if current_account_index is not None:
                                auto_save_account_data(current_account_index, pouvoir_items, gadget_items, objet_items, capacite_items, inventaire_items, jeton_poche, crown_poche, bon_marche_ameliore, battle_pass_xp, battle_pass_claimed_rewards, gemme_poche, used_stars, accounts, battle_pass_plus_claimed_rewards, used_stars_plus)
                            # Vérifier si on a atteint le seuil de jetons pour gagner une vie (100 en facile, 1000 en difficile, 200 sinon)
                            if difficulty == "facile":
                                jeton_threshold = 100
                            elif difficulty == "difficile":
                                jeton_threshold = 1000
                            else:
                                jeton_threshold = 200
                            if jeton_count >= jeton_threshold:
                                # En mode difficile et hardcore, on ne peut pas gagner de vies avec les jetons
                                if lives < MAX_LIVES and difficulty != "difficile" and difficulty != "hardcore":
                                    lives += 1
                                # Mettre les jetons et couronnes dans la poche (sauf en mode aventure)
                                if not is_adventure_mode:
                                    jeton_poche += jeton_count
                                crown_poche += crown_count
                                jeton_count = 0  # Réinitialiser le compteur de jetons
                                crown_count = 0  # Réinitialiser le compteur de couronnes
                            # Activer la couronne pendant 3 secondes
                            crown_timer = 30  # 3 secondes (30 frames à 10 FPS)
                            crown_count += 1  # Incrémenter le compteur de couronnes
                            # Gagner une grande couronne si on mange deux fantômes avec moins de 10 secondes d'écart
                            if last_ghost_time > 0:  # Si on a mangé un fantôme récemment
                                grande_couronne_count += 1  # Gagner une grande couronne
                            last_ghost_time = 100  # Réinitialiser le timer à 10 secondes (100 frames à 10 FPS)
                            ghost.eyes = True
                            ghost.vulnerable = False
                            ghost.returning = False
                        # Sinon, Pacman est touché par un fantôme normal
                        else:
                            # Si le fantôme est inoffensif (fantôme d'indigestion), ne pas tuer Pacman
                            if ghost.harmless:
                                continue  # Passer au fantôme suivant sans perdre de vie
                            # Vérifier si "skin bleu" est équipé et si le fantôme est bleu
                            if has_skin_bleu and ghost.color == BLUE:
                                # Avec "skin bleu" équipé, Pacman traverse les fantômes bleus sans mourir
                                continue  # Passer au fantôme suivant sans perdre de vie
                            # Vérifier si "skin orange" est équipé et si le fantôme est orange
                            if has_skin_orange and ghost.color == (255, 165, 0):  # ORANGE
                                # Avec "skin orange" équipé, Pacman a 85% de chance de ne pas mourir
                                if random.random() < 0.85:
                                    # Pacman survit (85% de chance)
                                    continue  # Passer au fantôme suivant sans perdre de vie
                                # Sinon, Pacman meurt (15% de chance)
                            # Vérifier si "skin rose" est équipé et si le fantôme est rose
                            if has_skin_rose and ghost.color == (255, 192, 203):  # ROSE
                                # Avec "skin rose" équipé, Pacman a 75% de chance de ne pas mourir
                                if random.random() < 0.75:
                                    # Pacman survit (75% de chance)
                                    continue  # Passer au fantôme suivant sans perdre de vie
                                # Sinon, Pacman meurt (25% de chance)
                            # Vérifier si "skin rouge" est équipé et si le fantôme est rouge
                            if has_skin_rouge and ghost.color == RED:  # ROUGE
                                # Avec "skin rouge" équipé, Pacman a 50% de chance de ne pas mourir
                                if random.random() < 0.50:
                                    # Pacman survit (50% de chance)
                                    continue  # Passer au fantôme suivant sans perdre de vie
                                # Sinon, Pacman meurt (50% de chance)
                            # Pacman est touché par un fantôme normal
                            lives -= 1
                            last_ghost_time = 0  # Réinitialiser le timer depuis le dernier fantôme mangé
                            if lives <= 0:
                                game_over = True
                                # Arrêter la musique si elle est en cours
                                if music_playing:
                                    pygame.mixer.music.stop()
                                    music_playing = False
                            else:
                                # Perdre une vie et réapparaître
                                respawn_timer = 60  # 2 secondes de pause
                                # Réinitialiser les positions temporairement
                                pacman.x = 10
                                pacman.y = 15
                                pacman.direction = (0, 0)
                                pacman.next_direction = (0, 0)
                            # Sortir de la boucle pour éviter plusieurs collisions dans la même frame
                            break
                
                # Supprimer les fantômes marqués pour suppression en mode aventure
                for ghost_to_remove in ghosts_to_remove:
                    if ghost_to_remove in ghosts:
                        ghosts.remove(ghost_to_remove)
                
                # En mode aventure, vérifier si tous les fantômes vrais (non-harmless) ont été éliminés
                if is_adventure_mode and not game_over and not won and not level_transition:
                    # Compter uniquement les fantômes vrais (non-harmless, pas en mode yeux)
                    real_ghosts_count = sum(1 for ghost in ghosts if not ghost.harmless and not ghost.eyes)
                    # Si plus de fantômes vrais, passer au niveau suivant immédiatement
                    if real_ghosts_count == 0:
                        level += 1
                        maze, pacman, ghosts = start_next_level(level, is_adventure_mode=True)
                        ghost_timers = {}  # Réinitialiser les timers de réapparition
                        level_transition = True
                        level_transition_timer = 60  # 2 secondes de transition
        
        # Dessiner selon l'état actuel
        if current_state == START_MENU:
            start_plus_button, start_profile_rects, start_menu_total_height = draw_start_menu(screen, accounts, current_account_index, start_menu_scroll_offset)
            
            # Gérer l'appui long pour la suppression
            if mouse_button_down and account_long_press_index is not None and delete_confirmation_step == 0:
                account_long_press_timer += 1
                # Si on maintient le clic pendant 60 frames (1 seconde à 60 FPS)
                if account_long_press_timer >= 60:
                    delete_confirmation_step = 1
                    account_to_delete = account_long_press_index
                    mouse_button_down = False  # Réinitialiser pour éviter les problèmes
            
            # Afficher la boîte de dialogue de confirmation si nécessaire
            if delete_confirmation_step > 0 and account_to_delete is not None and account_to_delete < len(accounts) and (current_state == START_MENU or current_state == MENU):
                draw_delete_confirmation(screen, delete_confirmation_step, accounts[account_to_delete].get('player_name', ''))
        elif current_state == SKILL_TREE_MENU:
            skill_tree_retour_button, skill_tree_survie_button, skill_tree_equipement_button = draw_skill_tree_menu(screen)
        elif current_state == SURVIE_SKILL_TREE_MENU:
            # Récupérer les trophées du compte actuel
            unlocked_trophies = []
            if current_account_index is not None and 0 <= current_account_index < len(accounts):
                unlocked_trophies = accounts[current_account_index].get('trophies', [])
            survie_skill_tree_retour_button, survie_trophy_rects = draw_survie_skill_tree_menu(screen, unlocked_trophies)
        elif current_state == EQUIPEMENT_SKILL_TREE_MENU:
            equipement_skill_tree_retour_button = draw_equipement_skill_tree_menu(screen)
        elif current_state == AVENTURE_MENU:
            aventure_retour_button, aventure_carte1_button = draw_aventure_menu(screen)
        elif current_state == CUSTOMIZATION_MENU:
            current_trophy_count = 0
            if current_account_index is not None and 0 <= current_account_index < len(accounts):
                current_trophy_count = len(accounts[current_account_index].get('trophies', []))
            customization_retour_button, customization_font_button, customization_avatar_button, customization_nom_button, customization_creer_compte_button, customization_avatar_circle = draw_customization_menu(screen, player_name, selected_avatar, selected_font, trophy_count=current_trophy_count)
        elif current_state == NAME_MENU:
            name_retour_button, name_input_rect = draw_name_menu(screen, player_name, name_input_active)
        elif current_state == FONT_MENU:
            font_retour_button, font_rects, font_valider_button = draw_font_menu(screen, selected_font, pending_font)
        elif current_state == AVATAR_MENU:
            avatar_retour_button, avatar_rect1, avatar_rect2, avatar_rect3, avatar_rect4, avatar_valider_button = draw_avatar_menu(screen, pending_avatar if pending_avatar is not None else selected_avatar, pending_avatar)
        elif current_state == TUTORIAL_MENU:
            tutorial_prev_button, tutorial_next_button = draw_tutorial_menu(screen, tutorial_page)
        elif current_state == PASSE_MENU:
            # Calculer le niveau et l'XP nécessaire pour le passe de combat
            # 100 XP par niveau, maximum 30 niveaux
            XP_PER_LEVEL = 100
            MAX_BATTLE_PASS_LEVEL = 30
            MAX_BATTLE_PASS_XP = MAX_BATTLE_PASS_LEVEL * XP_PER_LEVEL  # 3000 XP pour compléter le passe
            
            # S'assurer que battle_pass_xp est un entier (au cas où les données seraient corrompues)
            if not isinstance(battle_pass_xp, (int, float)):
                battle_pass_xp = 0
            battle_pass_xp = int(battle_pass_xp)
            
            # Si on dépasse le niveau 30, vérifier si toutes les récompenses ont été récupérées avant de réinitialiser
            if battle_pass_xp >= MAX_BATTLE_PASS_XP:
                # Vérifier que toutes les récompenses ont été récupérées
                all_rewards_claimed = all_battle_pass_rewards_claimed(battle_pass_claimed_rewards, used_stars, MAX_BATTLE_PASS_LEVEL)
                
                # Réinitialiser seulement si toutes les récompenses ont été récupérées
                if all_rewards_claimed:
                    # Réinitialiser l'XP et recommencer au niveau 1
                    battle_pass_xp = battle_pass_xp % MAX_BATTLE_PASS_XP
                    # Réinitialiser les listes de récompenses récupérées et étoiles utilisées
                    battle_pass_claimed_rewards = []
                    used_stars = []
                    # Sauvegarder la réinitialisation
                    if current_account_index is not None:
                        auto_save_account_data(current_account_index, pouvoir_items, gadget_items, objet_items, capacite_items, inventaire_items, jeton_poche, crown_poche, bon_marche_ameliore, battle_pass_xp, battle_pass_claimed_rewards, gemme_poche, used_stars, accounts)
            
            battle_pass_level = (battle_pass_xp // XP_PER_LEVEL) + 1
            battle_pass_xp_current_level = battle_pass_xp % XP_PER_LEVEL
            battle_pass_xp_needed = XP_PER_LEVEL
            passe_retour_button, passe_reward_rects, passe_arrow_button = draw_passe_menu(screen, battle_pass_level, battle_pass_xp_current_level, battle_pass_xp_needed, battle_pass_claimed_rewards, jeton_poche, crown_poche, gemme_poche, used_stars, passe_scroll_offset)
            # Dessiner les animations de récompenses par-dessus le menu
            draw_reward_animation(screen, reward_animations)
        elif current_state == PASSE_PLUS_MENU:
            # Calculer le niveau et l'XP nécessaire pour le passe de combat
            XP_PER_LEVEL = 100
            MAX_BATTLE_PASS_LEVEL = 30
            MAX_BATTLE_PASS_XP = MAX_BATTLE_PASS_LEVEL * XP_PER_LEVEL
            
            # S'assurer que battle_pass_xp est un entier
            if not isinstance(battle_pass_xp, (int, float)):
                battle_pass_xp = 0
            battle_pass_xp = int(battle_pass_xp)
            
            # La vérification et la réinitialisation du pass + se font maintenant après chaque récupération de récompense
            # Plus besoin de vérifier ici car c'est fait en temps réel
            
            # Calculer le niveau actuel et l'XP dans le niveau actuel
            battle_pass_level = min((battle_pass_xp // XP_PER_LEVEL) + 1, MAX_BATTLE_PASS_LEVEL)
            battle_pass_xp_current_level = battle_pass_xp % XP_PER_LEVEL
            battle_pass_xp_needed = XP_PER_LEVEL
            
            passe_plus_retour_button, passe_plus_gain_xp_button, passe_plus_reward_rects, passe_plus_arrow_left_button, passe_plus_buy_button = draw_passe_plus_menu(screen, battle_pass_level, battle_pass_xp_current_level, battle_pass_xp_needed, battle_pass_plus_claimed_rewards, jeton_poche, crown_poche, gemme_poche, used_stars_plus, passe_scroll_offset, pass_plus_purchased)
            # Dessiner les animations de récompenses par-dessus le menu
            draw_reward_animation(screen, reward_animations)
        elif current_state == STAR_UPGRADE_MENU:
            star_retour_button, star_clickable_rect = draw_star_upgrade_menu(screen, star_rarity, star_clicks_remaining)
            # Dessiner les animations de récompenses par-dessus le menu
            draw_reward_animation(screen, reward_animations)
        elif current_state == MENU:
            jeu_button, magasin_button, difficulte_button, poche_button, inventaire_button, vente_button, changer_compte_button, aventure_button, boutique_button, passe_combat_button, skill_tree_button, tutoriel_button = draw_menu(screen, difficulty=difficulty)
            
            # Afficher la boîte de dialogue de confirmation si nécessaire
            if delete_confirmation_step > 0 and account_to_delete is not None and account_to_delete < len(accounts):
                draw_delete_confirmation(screen, delete_confirmation_step, accounts[account_to_delete].get('player_name', ''))
        elif current_state == SHOP:
            shop_retour_button, shop_gadget_button, shop_pouvoir_button, shop_objet_button, shop_capacite_button = draw_shop(screen)
        elif current_state == SHOP_GADGET:
            shop_gadget_retour_button, shop_explosion_button, shop_vision_x_button, shop_feu_button, shop_tir_button, shop_mort_button, shop_bombe_button, shop_piege_button, shop_tp_button, shop_portail_button, shop_mur_button = draw_shop_gadget(screen, jeton_poche, gadget_items, crown_poche, item_description, level, inventaire_items, bon_marche_ameliore, capacite_items)
        elif current_state == SHOP_POUVOIR:
            shop_pouvoir_retour_button, shop_longue_vue_button, shop_double_longue_vue_button, shop_bon_repas_button, shop_bon_gout_button, shop_pas_indigestion_button, shop_glace_button, shop_skin_bleu_button, shop_skin_orange_button, shop_skin_rose_button, shop_skin_rouge_button = draw_shop_pouvoir(screen, jeton_poche, pouvoir_items, crown_poche, item_description, level, inventaire_items, bon_marche_ameliore, capacite_items)
        elif current_state == SHOP_CAPACITE:
            shop_capacite_retour_button, shop_bon_marche_button, shop_gadget_button, shop_piquant_button, shop_pacgum_button, shop_bonbe_button, shop_indigestion_button, shop_bon_vue_button, shop_gel_button, shop_lunette_button, shop_invincibilite_button, shop_ameliorer_button = draw_shop_capacite(screen, jeton_poche, capacite_items, crown_poche, item_description, bon_marche_ameliore)
        elif current_state == SHOP_OBJET:
            shop_objet_retour_button, shop_piece_mythique_button, shop_grosse_armure_button, shop_armure_fer_button, shop_flamme_button, shop_givre_button, shop_infra_rouge_button, shop_bric_button, shop_coffre_fort_button, shop_coffre_tresor_button, shop_double_gadget_button = draw_shop_objet(screen, jeton_poche, objet_items, crown_poche, item_description, level, inventaire_items, bon_marche_ameliore, capacite_items)
        elif current_state == DIFFICULTY:
            retour_button, button1, button2, button3, button4 = draw_difficulty(screen)
        elif current_state == POCHE:
            draw_poche(screen, crown_poche, jeton_poche, gemme_poche)
        elif current_state == BOUTIQUE:
            boutique_retour_button, boutique_exchange1_button, boutique_exchange2_button, boutique_exchange3_button = draw_boutique(screen, jeton_poche, crown_poche, gemme_poche)
        elif current_state == VENTE:
            vente_retour_button, vente_item_rects, vente_sell_prices = draw_vente(screen, inventaire_items, jeton_poche, crown_poche, vente_scroll_offset, capacite_items, bon_marche_ameliore)
        elif current_state == INVENTAIRE:
            # Obtenir la position de la souris pour le tooltip
            mouse_pos = pygame.mouse.get_pos()
            inventaire_retour_button, inventaire_slots, inventaire_start_button = draw_inventaire(screen, crown_poche, jeton_poche, pouvoir_items, inventaire_items, item_description, mouse_pos, show_start_button=inventaire_before_game)
            # Afficher l'item sélectionné qui suit la souris
            if selected_item is not None:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                slot_name, item_data = selected_item
                # Dessiner un aperçu de l'item à la position de la souris
                preview_size = 30
                preview_rect = pygame.Rect(mouse_x - preview_size // 2, mouse_y - preview_size // 2, preview_size, preview_size)
                pygame.draw.rect(screen, (100, 100, 255), preview_rect)
                pygame.draw.rect(screen, WHITE, preview_rect, 2)
                # Afficher un symbole simple pour l'item
                font_preview = pygame.font.Font(None, 20)
                preview_text = font_preview.render("?", True, WHITE)
                preview_text_rect = preview_text.get_rect(center=preview_rect.center)
                screen.blit(preview_text, preview_text_rect)
        elif current_state == GAME:
            # Dessiner le jeu
            screen.fill(BLACK)
            draw_maze(screen, maze, ice_tiles, fire_tiles, is_adventure_mode)
            
            # Bouton pour revenir au menu de sélection des comptes (en haut à droite)
            retour_menu_button = pygame.Rect(WINDOW_WIDTH - 120, 10, 110, 40)
            pygame.draw.rect(screen, RED, retour_menu_button)
            pygame.draw.rect(screen, WHITE, retour_menu_button, 2)
            font_retour_menu = pygame.font.Font(None, 28)
            retour_menu_text = font_retour_menu.render("MENU", True, WHITE)
            retour_menu_text_rect = retour_menu_text.get_rect(center=retour_menu_button.center)
            screen.blit(retour_menu_text, retour_menu_text_rect)
            
            # Dessiner les pièges posés
            for piege_pos in pieges:
                piege_x, piege_y = piege_pos
                piege_screen_x = piege_x * CELL_SIZE + CELL_SIZE // 2
                piege_screen_y = piege_y * CELL_SIZE + CELL_SIZE // 2
                
                # Dessiner le piège (cercle brun avec dents)
                piege_radius = 6
                pygame.draw.circle(screen, (139, 69, 19), (piege_screen_x, piege_screen_y), piege_radius)  # Brun
                pygame.draw.circle(screen, (101, 50, 14), (piege_screen_x, piege_screen_y), piege_radius - 1)  # Brun foncé
                
                # Dents/crocs autour du piège (triangles)
                num_teeth = 6
                for i in range(num_teeth):
                    angle = (2 * math.pi * i) / num_teeth
                    outer_x = piege_screen_x + (piege_radius + 2) * math.cos(angle)
                    outer_y = piege_screen_y + (piege_radius + 2) * math.sin(angle)
                    inner_x1 = piege_screen_x + (piege_radius - 1) * math.cos(angle)
                    inner_y1 = piege_screen_y + (piege_radius - 1) * math.sin(angle)
                    inner_x2 = piege_screen_x + (piege_radius - 1) * math.cos(angle + 2 * math.pi / num_teeth)
                    inner_y2 = piege_screen_y + (piege_radius - 1) * math.sin(angle + 2 * math.pi / num_teeth)
                    # Triangle pointant vers l'extérieur
                    tooth_points = [
                        (inner_x1, inner_y1),
                        (outer_x, outer_y),
                        (inner_x2, inner_y2)
                    ]
                    pygame.draw.polygon(screen, (80, 40, 10), tooth_points)  # Brun très foncé
            
            # Dessiner les portails
            if portal1_pos is not None:
                portal1_x, portal1_y = portal1_pos
                portal1_screen_x = portal1_x * CELL_SIZE + CELL_SIZE // 2
                portal1_screen_y = portal1_y * CELL_SIZE + CELL_SIZE // 2
                
                # Dessiner le portail 1 (cercle bleu avec effet de vortex)
                portal_radius = 10
                pygame.draw.circle(screen, (0, 100, 200), (portal1_screen_x, portal1_screen_y), portal_radius)  # Bleu
                pygame.draw.circle(screen, (50, 150, 255), (portal1_screen_x, portal1_screen_y), portal_radius - 2)  # Bleu clair
                
                # Effet de vortex (cercles concentriques)
                for i in range(3):
                    inner_radius = portal_radius - 3 - i * 2
                    if inner_radius > 2:
                        pygame.draw.circle(screen, (100, 200, 255), (portal1_screen_x, portal1_screen_y), inner_radius, 1)
                
                # Lignes de connexion
                for i in range(4):
                    angle = (2 * math.pi * i) / 4 + math.pi / 4
                    start_x = portal1_screen_x + (portal_radius - 2) * math.cos(angle)
                    start_y = portal1_screen_y + (portal_radius - 2) * math.sin(angle)
                    end_x = portal1_screen_x + (portal_radius + 2) * math.cos(angle)
                    end_y = portal1_screen_y + (portal_radius + 2) * math.sin(angle)
                    pygame.draw.line(screen, (150, 220, 255), (start_x, start_y), (end_x, end_y), 1)
            
            if portal2_pos is not None:
                portal2_x, portal2_y = portal2_pos
                portal2_screen_x = portal2_x * CELL_SIZE + CELL_SIZE // 2
                portal2_screen_y = portal2_y * CELL_SIZE + CELL_SIZE // 2
                
                # Dessiner le portail 2 (cercle bleu avec effet de vortex)
                portal_radius = 10
                pygame.draw.circle(screen, (0, 100, 200), (portal2_screen_x, portal2_screen_y), portal_radius)  # Bleu
                pygame.draw.circle(screen, (50, 150, 255), (portal2_screen_x, portal2_screen_y), portal_radius - 2)  # Bleu clair
                
                # Effet de vortex (cercles concentriques)
                for i in range(3):
                    inner_radius = portal_radius - 3 - i * 2
                    if inner_radius > 2:
                        pygame.draw.circle(screen, (100, 200, 255), (portal2_screen_x, portal2_screen_y), inner_radius, 1)
                
                # Lignes de connexion
                for i in range(4):
                    angle = (2 * math.pi * i) / 4 + math.pi / 4
                    start_x = portal2_screen_x + (portal_radius - 2) * math.cos(angle)
                    start_y = portal2_screen_y + (portal_radius - 2) * math.sin(angle)
                    end_x = portal2_screen_x + (portal_radius + 2) * math.cos(angle)
                    end_y = portal2_screen_y + (portal_radius + 2) * math.sin(angle)
                    pygame.draw.line(screen, (150, 220, 255), (start_x, start_y), (end_x, end_y), 1)
            
            if not game_over and not won and not level_transition and respawn_timer == 0:
                # Dessiner la bombe téléguidée si elle est active
                if bombe_active:
                    # Calculer la position à l'écran de la bombe
                    bombe_screen_x = bombe_x * CELL_SIZE + CELL_SIZE // 2
                    bombe_screen_y = bombe_y * CELL_SIZE + CELL_SIZE // 2
                    
                    # Dessiner la bombe (cercle noir avec mèche)
                    bombe_radius = 8
                    pygame.draw.circle(screen, BLACK, (bombe_screen_x, bombe_screen_y), bombe_radius)
                    
                    # Reflet sur la bombe (petit cercle gris)
                    pygame.draw.circle(screen, (100, 100, 100), (bombe_screen_x - 2, bombe_screen_y - 2), 3)
                    
                    # Mèche (ligne brune)
                    mèche_start = (bombe_screen_x, bombe_screen_y - bombe_radius)
                    mèche_end = (bombe_screen_x, bombe_screen_y - bombe_radius - 4)
                    pygame.draw.line(screen, (139, 69, 19), mèche_start, mèche_end, 2)
                    
                    # Flamme sur la mèche (petit triangle orange)
                    flame_points = [
                        (bombe_screen_x, bombe_screen_y - bombe_radius - 4),
                        (bombe_screen_x - 2, bombe_screen_y - bombe_radius - 6),
                        (bombe_screen_x + 2, bombe_screen_y - bombe_radius - 6)
                    ]
                    pygame.draw.polygon(screen, (255, 140, 0), flame_points)
                    
                    # Afficher le temps restant (en secondes)
                    font_bombe = pygame.font.Font(None, 20)
                    time_left = max(0, (bombe_timer + 9) // 10)  # Arrondir vers le haut et afficher en secondes
                    time_text = font_bombe.render(str(time_left), True, WHITE)
                    time_text_rect = time_text.get_rect(center=(bombe_screen_x, bombe_screen_y + bombe_radius + 10))
                    screen.blit(time_text, time_text_rect)
                
                # Dessiner Pacman avec effet de clignotement si invincible et couronne si on en a une
                # La longue vue ou double longue vue est équipée seulement si elle est dans le slot "pouvoir"
                has_longue_vue = ('pouvoir' in inventaire_items and 
                                 (inventaire_items['pouvoir'].get('type') == 'longue vue' or 
                                  inventaire_items['pouvoir'].get('type') == 'double longue vue'))
                is_double_longue_vue = ('pouvoir' in inventaire_items and 
                                       inventaire_items['pouvoir'].get('type') == 'double longue vue')
                # Vérifier si les skins sont équipés dans le slot "pouvoir"
                has_skin_bleu_draw = ('pouvoir' in inventaire_items and 
                                      inventaire_items['pouvoir'].get('type') == 'skin bleu')
                has_skin_orange_draw = ('pouvoir' in inventaire_items and 
                                        inventaire_items['pouvoir'].get('type') == 'skin orange')
                has_skin_rose_draw = ('pouvoir' in inventaire_items and 
                                      inventaire_items['pouvoir'].get('type') == 'skin rose')
                has_skin_rouge_draw = ('pouvoir' in inventaire_items and 
                                       inventaire_items['pouvoir'].get('type') == 'skin rouge')
                # Dessiner Pacman seulement si la bombe n'est pas active (ou toujours le dessiner mais peut-être grisé)
                if not bombe_active:
                    pacman.draw(screen, invincible=(invincibility_timer > 0 or super_vie_active), has_crown=(crown_timer > 0), has_longue_vue=has_longue_vue, has_indigestion=has_indigestion, is_double_longue_vue=is_double_longue_vue, is_rainbow_critique=is_rainbow_critique, has_skin_bleu=has_skin_bleu_draw, has_skin_orange=has_skin_orange_draw, has_skin_rose=has_skin_rose_draw, has_skin_rouge=has_skin_rouge_draw, super_vie_active=super_vie_active)
                else:
                    # Dessiner Pacman mais grisé/frozen quand la bombe est active
                    pacman.draw(screen, invincible=(invincibility_timer > 0 or super_vie_active), has_crown=(crown_timer > 0), has_longue_vue=has_longue_vue, has_indigestion=has_indigestion, is_double_longue_vue=is_double_longue_vue, is_rainbow_critique=is_rainbow_critique, has_skin_bleu=has_skin_bleu_draw, has_skin_orange=has_skin_orange_draw, has_skin_rose=has_skin_rose_draw, has_skin_rouge=has_skin_rouge_draw, super_vie_active=super_vie_active)
                for ghost in ghosts:
                    ghost.draw(screen)
            
            # Afficher les jetons, le niveau et les vies
            font = pygame.font.Font(None, 36)
            jeton_text = font.render(f"Jetons: {jeton_count}", True, (255, 192, 203))  # Rose
            screen.blit(jeton_text, (10, 10))
            
            level_text = font.render(f"Niveau: {level}", True, WHITE)
            screen.blit(level_text, (10, 50))
            
            # Afficher le compteur de couronnes
            crown_count_text = font.render(f"Couronnes: {crown_count}", True, (255, 215, 0))  # Or
            screen.blit(crown_count_text, (10, 90))
            
            # Afficher les vies sous forme de cœurs
            heart_symbol = "♥"
            lives_display = heart_symbol * lives
            lives_text = font.render(lives_display, True, RED)
            screen.blit(lives_text, (10, 130))
            
            # Bouton retour
            font_button = pygame.font.Font(None, 36)
            game_retour_button = pygame.Rect(WINDOW_WIDTH - 110, 10, 100, 40)
            pygame.draw.rect(screen, RED, game_retour_button)
            pygame.draw.rect(screen, WHITE, game_retour_button, 2)
            retour_text = font_button.render("RETOUR", True, WHITE)
            retour_text_rect = retour_text.get_rect(center=game_retour_button.center)
            screen.blit(retour_text, retour_text_rect)
            
            # Message de transition entre niveaux
            if level_transition:
                if is_multi_map_mode:
                    transition_text = font.render(f"NIVEAU {level} - MAP {map_x + 1},{map_y + 1}/4x4", True, YELLOW)
                else:
                    maze_index = (level - 1) % len(MAZES)
                    transition_text = font.render(f"NIVEAU {level} - CARTE {maze_index + 1}!", True, YELLOW)
                text_rect = transition_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
                screen.blit(transition_text, text_rect)
            
            # Afficher les coordonnées de la map en mode multi-map
            if is_multi_map_mode:
                map_info_text = font.render(f"Map: {map_x + 1},{map_y + 1}/4x4", True, YELLOW)
                screen.blit(map_info_text, (10, 170))
            
            # Message de perte de vie
            if respawn_timer > 0:
                lives_lost_text = font.render(f"Vie perdue! Vies restantes: {lives}", True, RED)
                text_rect = lives_lost_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 20))
                screen.blit(lives_lost_text, text_rect)
                restart_text = font.render("Clic droit pour relancer", True, WHITE)



                

                restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 20))
                screen.blit(restart_text, restart_rect)
            
            if game_over:
                game_over_text = font.render("GAME OVER - Clic droit", True, RED)
                text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
                screen.blit(game_over_text, text_rect)
            
            if won:
                won_text = font.render("vous avez gagné", True, YELLOW)
                text_rect = won_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
                screen.blit(won_text, text_rect)
            
            if first_level_success_unlocked and success_notification_timer > 0 and success_notification_text:
                success_height = 60
                success_surface = pygame.Surface((WINDOW_WIDTH, success_height), pygame.SRCALPHA)
                success_surface.fill((0, 0, 0, 180))
                screen.blit(success_surface, (0, 180))
                font_success = pygame.font.Font(None, 40)
                success_text = font_success.render(success_notification_text, True, (0, 255, 0))
                success_rect = success_text.get_rect(center=(WINDOW_WIDTH//2, 210))
                screen.blit(success_text, success_rect)
            
            # Afficher l'indicateur de cooldown du gadget en bas de l'écran
            equipped_gadget_cooldown = get_equipped_gadget(inventaire_items)
            if equipped_gadget_cooldown:
                # Position du cercle en bas de l'écran (centré horizontalement)
                circle_x = WINDOW_WIDTH // 2
                circle_y = WINDOW_HEIGHT - 30
                circle_radius = 20
                
                # Déterminer le temps de recharge approprié selon le gadget équipé
                gadget_type_cooldown = equipped_gadget_cooldown.get('type')
                current_cooldown = 0
                max_cooldown = GADGET_COOLDOWN_DURATION
                if gadget_type_cooldown == 'mort':
                    current_cooldown = mort_cooldown
                    max_cooldown = MORT_COOLDOWN_DURATION
                elif gadget_type_cooldown == 'bombe téléguidée':
                    current_cooldown = bombe_cooldown
                    max_cooldown = BOMBE_COOLDOWN_DURATION
                else:
                    current_cooldown = gadget_cooldown
                    max_cooldown = GADGET_COOLDOWN_DURATION
                
                # Calculer le pourcentage de cooldown restant
                if current_cooldown > 0:
                    cooldown_percentage = 1.0 - (current_cooldown / max_cooldown)
                    # Dessiner le cercle de base en gris
                    pygame.draw.circle(screen, (80, 80, 80), (circle_x, circle_y), circle_radius)  # Gris foncé
                    
                    # Dessiner un secteur de cercle vert pour montrer la progression du cooldown
                    # L'arc part du haut (-90 degrés) et se remplit dans le sens horaire
                    if cooldown_percentage > 0:
                        # Angle de départ (en haut = -90 degrés)
                        start_angle_deg = -90
                        # Angle total couvert par la progression
                        angle_span_deg = 360 * cooldown_percentage
                        # Nombre de segments pour créer un arc lisse
                        num_segments = max(30, int(angle_span_deg))
                        
                        # Créer les points pour le secteur de cercle (partie remplie)
                        points = [(circle_x, circle_y)]  # Commencer au centre
                        for i in range(num_segments + 1):
                            angle_deg = start_angle_deg + (i * angle_span_deg / num_segments)
                            angle_rad = math.radians(angle_deg)
                            px = circle_x + circle_radius * math.cos(angle_rad)
                            py = circle_y + circle_radius * math.sin(angle_rad)
                            points.append((px, py))
                        
                        # Dessiner le secteur de cercle en vert pour montrer la progression
                        if len(points) > 2:
                            pygame.draw.polygon(screen, (0, 180, 0), points)  # Vert pour la partie rechargée
                    
                    # Dessiner la bordure du cercle
                    pygame.draw.circle(screen, (60, 60, 60), (circle_x, circle_y), circle_radius, 2)  # Bordure gris très foncé
                else:
                    # Cercle vert quand le gadget est disponible
                    pygame.draw.circle(screen, (0, 255, 0), (circle_x, circle_y), circle_radius)  # Vert
                    pygame.draw.circle(screen, (0, 200, 0), (circle_x, circle_y), circle_radius, 2)  # Bordure vert foncé
        
        pygame.display.flip()
        # Augmenter la vitesse avec les niveaux (plus lentement pour plus de facilité)
        if current_state == GAME:
            current_fps = BASE_FPS + (level - 1)  # +1 FPS par niveau au lieu de +2
            clock.tick(min(current_fps, 15))  # Max 15 FPS au lieu de 20
        else:
            clock.tick(30)  # FPS constant pour le menu
    
    # Sauvegarder toutes les données avant de quitter
    if current_account_index is not None:
        save_game_data_for_account(current_account_index, pouvoir_items, gadget_items, objet_items, capacite_items, inventaire_items, jeton_poche, crown_poche, bon_marche_ameliore, accounts)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()                                  