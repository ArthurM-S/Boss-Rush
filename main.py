import pygame
import sys

# 1. Inicializa o Pygame e o mixer PRIMEIRO
pygame.init()
pygame.mixer.init()

# 2. Agora importa os módulos que precisam dos sons
from code.config import inicializar_fontes, carregar_background, carregar_background_menu
from code.menu import tela_menu
from code.game import jogo

def main():
    pygame.display.set_caption("Boss Rush")
    inicializar_fontes()
    carregar_background()
    carregar_background_menu()

    while True:
        tela_menu()
        jogo()

if __name__ == "__main__":
    main()