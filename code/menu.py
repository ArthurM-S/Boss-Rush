import pygame
import sys
from . import config

# Variáveis globais para o parallax
offset_x = 0
offset_y = 0

def tocar_musica_menu():
    try:
        pygame.mixer.music.load("assets/sounds/menu_music.wav")
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.6)
    except pygame.error as e:
        print(f"Erro ao carregar música do menu: {e}")

def tela_menu():
    global offset_x, offset_y

    if not pygame.mixer.music.get_busy():
        tocar_musica_menu()

    while True:
        # Movimento do parallax baseado no mouse
        mouse_x, mouse_y = pygame.mouse.get_pos()
        alvo_x = (mouse_x / config.LARGURA - 0.5) * 60
        alvo_y = (mouse_y / config.ALTURA - 0.5) * 40
        offset_x += (alvo_x - offset_x) * 0.05
        offset_y += (alvo_y - offset_y) * 0.05

        # Background com camadas
        if config.BACKGROUND_LAYERS_MENU:
            for idx, camada in enumerate(config.BACKGROUND_LAYERS_MENU):
                fator = 1.0 - (idx / len(config.BACKGROUND_LAYERS_MENU)) * 0.7
                deslocamento_x = int(offset_x * fator)
                deslocamento_y = int(offset_y * fator * 0.5)

                if deslocamento_x >= 0:
                    config.TELA.blit(camada, (deslocamento_x, deslocamento_y))
                    config.TELA.blit(camada, (deslocamento_x - config.LARGURA, deslocamento_y))
                else:
                    config.TELA.blit(camada, (deslocamento_x, deslocamento_y))
                    config.TELA.blit(camada, (deslocamento_x + config.LARGURA, deslocamento_y))
        else:
            config.TELA.fill(config.PRETO)

        # Título centralizado
        surf_titulo = config.FONTE_TITULO.render("Boss Rush", True, config.PRETO)
        config.TELA.blit(surf_titulo, (config.LARGURA//2 - surf_titulo.get_width()//2, 60))

        # Start game
        surf_enter = config.FONTE_MEDIA.render("Pressione ENTER para iniciar", True, config.BRANCO)
        x_enter = config.LARGURA//2 - surf_enter.get_width()//2
        y_enter = config.ALTURA - 120
        config.TELA.blit(surf_enter, (x_enter, y_enter))

        # Botão CONTROLES
        surf_controles = config.FONTE_MEDIA.render("CONTROLES", True, config.CINZA)
        rect_controles = surf_controles.get_rect()
        rect_controles.topleft = (30, config.ALTURA - 70)
        config.TELA.blit(surf_controles, rect_controles)

        # Botão SAIR (canto inferior direito)
        surf_sair = config.FONTE_MEDIA.render("SAIR", True, config.VERMELHO)
        rect_sair = surf_sair.get_rect()
        rect_sair.topright = (config.LARGURA - 30, config.ALTURA - 70)
        config.TELA.blit(surf_sair, rect_sair)

        pygame.display.flip()

        # Eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                pos = pygame.mouse.get_pos()
                if rect_controles.collidepoint(pos):
                    tela_controles()
                if rect_sair.collidepoint(pos):
                    pygame.quit()
                    sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                # Inicia o jogo com ENTER ou ESPAÇO
                if evento.key == pygame.K_RETURN or evento.key == pygame.K_SPACE:
                    return

def tela_controles():
    global offset_x, offset_y

    while True:
        # Parallax
        mouse_x, mouse_y = pygame.mouse.get_pos()
        alvo_x = (mouse_x / config.LARGURA - 0.5) * 60
        alvo_y = (mouse_y / config.ALTURA - 0.5) * 40
        offset_x += (alvo_x - offset_x) * 0.05
        offset_y += (alvo_y - offset_y) * 0.05

        if config.BACKGROUND_LAYERS_MENU:
            for idx, camada in enumerate(config.BACKGROUND_LAYERS_MENU):
                fator = 1.0 - (idx / len(config.BACKGROUND_LAYERS_MENU)) * 0.7
                deslocamento_x = int(offset_x * fator)
                deslocamento_y = int(offset_y * fator * 0.5)
                if deslocamento_x >= 0:
                    config.TELA.blit(camada, (deslocamento_x, deslocamento_y))
                    config.TELA.blit(camada, (deslocamento_x - config.LARGURA, deslocamento_y))
                else:
                    config.TELA.blit(camada, (deslocamento_x, deslocamento_y))
                    config.TELA.blit(camada, (deslocamento_x + config.LARGURA, deslocamento_y))
        else:
            config.TELA.fill(config.PRETO)

        # Título
        surf_titulo = config.FONTE_GRANDE.render("CONTROLES", True, config.AMARELO)
        config.TELA.blit(surf_titulo, (config.LARGURA//2 - surf_titulo.get_width()//2, 50))

        # Lista de comandos
        comandos = [
            ("MOVIMENTO", "W, A, S, D"),
            ("ATACAR", "ESPAÇO ou CLIQUE ESQUERDO"),
            ("SPRINT", "SHIFT corre mais rápido"),
            ("SAIR DO JOGO", "ESC"),
            ("VOLTAR AO MENU", "ESC nesta tela")
        ]

        y = 150
        for titulo, descricao in comandos:
            surf_tit = config.FONTE_MEDIA.render(titulo + ":", True, config.AMARELO)
            config.TELA.blit(surf_tit, (config.LARGURA//2 - 200, y))
            surf_desc = config.FONTE_MEDIA.render(descricao, True, config.BRANCO)
            config.TELA.blit(surf_desc, (config.LARGURA//2 + 50, y))
            y += 45

        # Botão VOLTAR
        surf_voltar = config.FONTE_MEDIA.render("VOLTAR", True, config.BRANCO)
        rect_voltar = surf_voltar.get_rect()
        rect_voltar.topleft = (30, config.ALTURA - 70)
        config.TELA.blit(surf_voltar, rect_voltar)

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if rect_voltar.collidepoint(pygame.mouse.get_pos()):
                    return
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return

def tela_game_over(pontuacao, vida_restante):
    config.TELA.fill(config.PRETO)
    surf_titulo = config.FONTE_GRANDE.render("DERROTA!", True, config.VERMELHO)
    config.TELA.blit(surf_titulo, (config.LARGURA//2 - surf_titulo.get_width()//2, 150))
    surf_pontos = config.FONTE_MEDIA.render(f"Pontuação: {pontuacao}", True, config.BRANCO)
    config.TELA.blit(surf_pontos, (config.LARGURA//2 - surf_pontos.get_width()//2, 250))
    surf_vida = config.FONTE_MEDIA.render(f"Vida restante: {vida_restante}", True, config.BRANCO)
    config.TELA.blit(surf_vida, (config.LARGURA//2 - surf_vida.get_width()//2, 290))
    surf_dica = config.FONTE_PEQUENA.render("Pressione [R] para recomeçar ou [ESC] para sair", True, config.CINZA)
    config.TELA.blit(surf_dica, (config.LARGURA//2 - surf_dica.get_width()//2, 400))
    pygame.display.flip()

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    return True
                if evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

def tela_vitoria(pontuacao):
    config.TELA.fill(config.PRETO)
    surf_titulo = config.FONTE_GRANDE.render("VITÓRIA!", True, config.VERDE)
    config.TELA.blit(surf_titulo, (config.LARGURA//2 - surf_titulo.get_width()//2, 150))
    surf_pontos = config.FONTE_MEDIA.render(f"Pontuação: {pontuacao}", True, config.BRANCO)
    config.TELA.blit(surf_pontos, (config.LARGURA//2 - surf_pontos.get_width()//2, 250))
    surf_dica = config.FONTE_PEQUENA.render("Pressione [R] para jogar novamente ou [ESC] para sair", True, config.CINZA)
    config.TELA.blit(surf_dica, (config.LARGURA//2 - surf_dica.get_width()//2, 350))
    pygame.display.flip()

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    return True
                if evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()