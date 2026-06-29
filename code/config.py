import pygame
import os
import sys

LARGURA = 1024
ALTURA = 780
TELA = pygame.display.set_mode((LARGURA, ALTURA))

PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
VERMELHO = (200, 30, 30)
AZUL = (30, 144, 255)
VERDE = (0, 255, 0)
CINZA = (100, 100, 100)
AMARELO = (255, 215, 0)
ROXO_BOSS = (120, 30, 150)

FPS = 60
RELÓGIO = pygame.time.Clock()

FONTE_PEQUENA = None
FONTE_MEDIA = None
FONTE_GRANDE = None
FONTE_TITULO = None

def inicializar_fontes():
    global FONTE_PEQUENA, FONTE_MEDIA, FONTE_GRANDE, FONTE_TITULO
    FONTE_PEQUENA = pygame.font.Font(None, 28)
    FONTE_MEDIA = pygame.font.Font(None, 36)
    FONTE_GRANDE = pygame.font.Font(None, 72)
    FONTE_TITULO = pygame.font.Font(None, 96)

def carregar_imagem(caminho, redimensionar=None):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    caminho_completo = os.path.join(base_path, "assets", "images", caminho)
    try:
        imagem = pygame.image.load(caminho_completo).convert_alpha()
        if redimensionar:
            imagem = pygame.transform.scale(imagem, redimensionar)
        return imagem
    except (pygame.error, FileNotFoundError):
        print(f"Aviso: imagem não encontrada: {caminho_completo}")
        return None

def carregar_som(caminho):
    try:
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        caminho_completo = os.path.join(base_path, "assets", "sounds", caminho)
        return pygame.mixer.Sound(caminho_completo)
    except (pygame.error, FileNotFoundError) as e:
        print(f"Erro ao carregar som {caminho}: {e}")
        return None

NOMES_CAMADAS_LUTA = ["bg.png", "mountaims.png", "windows.png", "cf.png", "candeliar.png", "floor.png", "dragon.png"]
NOMES_CAMADAS_MENU = ["1.png", "2.png", "3.png", "4.png", "5.png"]

BACKGROUND_LAYERS_LUTA = []
BACKGROUND_LAYERS_MENU = []

def carregar_background():
    global BACKGROUND_LAYERS_LUTA
    BACKGROUND_LAYERS_LUTA = []
    for nome in NOMES_CAMADAS_LUTA:
        img = carregar_imagem(nome, (LARGURA, ALTURA))
        if img:
            BACKGROUND_LAYERS_LUTA.append(img)
        else:
            fallback = pygame.Surface((LARGURA, ALTURA))
            fallback.fill(PRETO)
            BACKGROUND_LAYERS_LUTA.append(fallback)

def carregar_background_menu():
    global BACKGROUND_LAYERS_MENU
    BACKGROUND_LAYERS_MENU = []
    for nome in NOMES_CAMADAS_MENU:
        img = carregar_imagem(nome, (LARGURA, ALTURA))
        if img:
            BACKGROUND_LAYERS_MENU.append(img)
        else:
            fallback = pygame.Surface((LARGURA, ALTURA))
            fallback.fill(PRETO)
            BACKGROUND_LAYERS_MENU.append(fallback)

# Limites da arena
LIMITE_ESQUERDA = 25
LIMITE_DIREITA = LARGURA - 25
LIMITE_TOPO = 335
LIMITE_BAIXO = ALTURA - 20

# Dano aleatório
DANO_MIN_PLAYER = 67
DANO_MAX_PLAYER = 185
DANO_MIN_BOSS = 24
DANO_MAX_BOSS = 79