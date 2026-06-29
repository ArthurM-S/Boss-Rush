import pygame
import sys
from code.config import inicializar_fontes, carregar_background, carregar_background_menu
from code.menu import tela_menu
from code.game import jogo

def main():
    pygame.init()
    pygame.display.set_caption("Boss Rush")
    inicializar_fontes()

    carregar_background()
    carregar_background_menu()

    while True:
        tela_menu()
        jogo()

if __name__ == "__main__":
    main()