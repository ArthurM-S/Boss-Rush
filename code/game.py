import pygame
import sys
import random
from . import config
from .player import Jogador
from .boss import Boss
from .menu import tela_game_over, tela_vitoria

# Textos flutuantes de dano
textos_dano = []

def adicionar_texto_dano(x, y, valor, cor, duracao=60):
    # Adiciona um texto flutuante na tela.
    textos_dano.append({
        'x': x,
        'y': y,
        'valor': str(valor),
        'cor': cor,
        'timer': duracao,      # frames até sumir
        'vel_y': -2            # sobe devagar
    })

def desenhar_textos_dano(tela):
    # Desenha e atualiza os textos flutuantes.
    global textos_dano
    for texto in textos_dano[:]:
        # Renderiza o texto
        fonte = pygame.font.Font(None, 36)
        surf = fonte.render(texto['valor'], True, texto['cor'])
        # Desenha com transparência (quanto mais velho, mais transparente)
        alpha = int(255 * (texto['timer'] / 60))
        surf.set_alpha(alpha)
        tela.blit(surf, (texto['x'] - surf.get_width()//2, texto['y']))
        # Atualiza posição e timer
        texto['y'] += texto['vel_y']
        texto['timer'] -= 1
        # Remove se o timer acabar
        if texto['timer'] <= 0:
            textos_dano.remove(texto)

def jogo():
    global textos_dano
    textos_dano = []  # Reseta a lista a cada partida

    jogador = Jogador(config.LARGURA//2, config.ALTURA//2)
    # Invencibilidade inicial
    jogador.invencivel = True
    jogador.tempo_invencivel = 60

    #boss = Boss(config.LARGURA//100 - 10, 100)
    boss = Boss(config.LARGURA + 150, 350)
    pontuacao = 0
    tempo_inicio = pygame.time.get_ticks()
    game_over = False
    vitoria = False
    offset_x = 0

    morto = False
    tempo_morte = 0

    while not game_over and not vitoria:
        tempo_atual = int((pygame.time.get_ticks() - tempo_inicio) / 1000)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE and not morto:
                    jogador.atacar()
                if evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if evento.key == pygame.K_m:
                    jogador.vida = 0
                    morto = True
                    tempo_morte = 60
                    boss.projeteis.clear()
                    jogador.estado = "death"
                    jogador.quadro_atual = 0
                    jogador.tempo_animacao = 0
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1 and not morto:
                jogador.atacar()

        teclas = pygame.key.get_pressed()
        pos_mouse = pygame.mouse.get_pos()

        if not morto:
            jogador.atualizar(teclas, pos_mouse)
            boss.atualizar(jogador.rect)

            if boss.vida > 0:
                # Colisão com o boss
                if jogador.rect.colliderect(boss.rect):
                    dano = random.randint(config.DANO_MIN_BOSS, config.DANO_MAX_BOSS)
                    jogador.tomar_dano(dano)
                    # Texto flutuante VERMELHO no local do dano
                    adicionar_texto_dano(
                        jogador.rect.centerx,
                        jogador.rect.top - 10,
                        dano,
                        (255, 50, 50)  # vermelho
                    )
                    if jogador.direcao == 1:
                        jogador.rect.x -= 30
                    else:
                        jogador.rect.x += 30

                # Colisão com projéteis
                for proj in boss.projeteis[:]:
                    proj_rect = pygame.Rect(proj['x'] - 12, proj['y'] - 12, 24, 24)
                    if jogador.rect.colliderect(proj_rect):
                        dano = random.randint(config.DANO_MIN_BOSS, config.DANO_MAX_BOSS)
                        jogador.tomar_dano(dano)
                        adicionar_texto_dano(
                            jogador.rect.centerx,
                            jogador.rect.top - 10,
                            dano,
                            (255, 50, 50)  # vermelho
                        )
                        boss.projeteis.remove(proj)
                        if jogador.direcao == 1:
                            jogador.rect.x -= 20
                        else:
                            jogador.rect.x += 20

            # Ataque do jogador no boss
            ret_ataque = jogador.get_rect_ataque()
            if ret_ataque and ret_ataque.colliderect(boss.rect) and boss.vida > 0:
                dano = random.randint(config.DANO_MIN_PLAYER, config.DANO_MAX_PLAYER)
                boss.tomar_dano(dano)
                pontuacao += 10
                jogador.ataque_ativo = False
                # Texto flutuante AMARELO no local do acerto no boss
                adicionar_texto_dano(
                    boss.rect.centerx,
                    boss.rect.top - 10,
                    dano,
                    (255, 255, 0)  # amarelo
                )

            if jogador.vida <= 0:
                morto = True
                tempo_morte = 60
                boss.projeteis.clear()
                jogador.estado = "death"
                jogador.quadro_atual = 0
                jogador.tempo_animacao = 0
        else:
            jogador.atualizar_animacao()
            tempo_morte -= 1
            if tempo_morte <= 0:
                game_over = True

        if boss.vida <= 0 and not morto:
            vitoria = True

        # --- Renderização ---
        # Fundo (parallax)
        if config.BACKGROUND_LAYERS_LUTA:
            for idx, camada in enumerate(config.BACKGROUND_LAYERS_LUTA):
                if idx == 0:
                    offset = 0
                elif idx == 1:
                    offset = int(offset_x * 0.3) % config.LARGURA
                elif idx == 2:
                    offset = int(offset_x * 0.7) % config.LARGURA
                else:
                    offset = int(offset_x) % config.LARGURA
                if offset == 0:
                    config.TELA.blit(camada, (0, 0))
                else:
                    config.TELA.blit(camada, (offset, 0))
                    config.TELA.blit(camada, (offset - config.LARGURA, 0))
        else:
            config.TELA.fill(config.PRETO)

        if not morto and jogador.vel_x != 0:
            offset_x += jogador.vel_x * 0.5

        # Desenha jogador e boss
        jogador.desenhar(config.TELA)
        if boss.vida > 0:
            boss.desenhar(config.TELA)

        # Desenha os textos flutuantes de dano
        desenhar_textos_dano(config.TELA)

        # Barras de vida
        jogador.desenhar_barra_vida(config.TELA)
        if boss.vida > 0:
            boss.desenhar_barra_vida(config.TELA)

        # HUD
        if not morto:
            surf_score = config.FONTE_MEDIA.render(f"Pontos: {pontuacao}", True, config.BRANCO)
            x_score = config.LARGURA - surf_score.get_width() - 15
            config.TELA.blit(surf_score, (x_score, 10))

            surf_tempo = config.FONTE_MEDIA.render(f"Tempo: {tempo_atual}s", True, config.BRANCO)
            x_tempo = config.LARGURA - surf_tempo.get_width() - 15
            config.TELA.blit(surf_tempo, (x_tempo, 50))

        pygame.display.flip()
        config.RELÓGIO.tick(config.FPS)

    if game_over:
        reset = tela_game_over(pontuacao, jogador.vida)
    elif vitoria:
        reset = tela_vitoria(pontuacao)

    if reset:
        # Reinicia o jogo (reseta a lista de textos)
        textos_dano = []
        jogo()