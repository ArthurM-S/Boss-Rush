import pygame
import sys
import random
from . import config
from .player import Jogador
from .boss import Boss
from .menu import tela_game_over, tela_vitoria


som_player_attack = config.carregar_som("player_attack.wav")
print("Som do player:", som_player_attack)
som_boss_attack = config.carregar_som("boss_attack.wav")

# Lista para textos flutuantes de dano
textos_dano = []

def adicionar_texto_dano(x, y, valor, cor, duracao=60):
    textos_dano.append({
        'x': x,
        'y': y,
        'valor': str(valor),
        'cor': cor,
        'timer': duracao,
        'vel_y': -2
    })

def desenhar_textos_dano(tela):
    global textos_dano
    for texto in textos_dano[:]:
        fonte = pygame.font.Font(None, 36)
        surf = fonte.render(texto['valor'], True, texto['cor'])
        alpha = int(255 * (texto['timer'] / 60))
        surf.set_alpha(alpha)
        tela.blit(surf, (texto['x'] - surf.get_width()//2, texto['y']))
        texto['y'] += texto['vel_y']
        texto['timer'] -= 1
        if texto['timer'] <= 0:
            textos_dano.remove(texto)

def jogo():
    global textos_dano
    textos_dano = []

    jogador = Jogador(config.LARGURA//2, config.ALTURA//2)
    jogador.invencivel = True
    jogador.tempo_invencivel = 60

    boss = Boss(config.LARGURA + 100, 150)
    pontuacao = 0
    tempo_inicio = pygame.time.get_ticks()
    game_over = False
    vitoria = False
    offset_x = 0

    morto = False
    tempo_morte = 0

    # Toca a música da batalha
    pygame.mixer.music.stop()
    try:
        pygame.mixer.music.load("assets/sounds/battle_music.wav")
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.6)
    except pygame.error as e:
        print(f"Erro ao carregar música da batalha: {e}")

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
                # Colisão com o boss (player toma dano)
                if jogador.rect.colliderect(boss.rect):
                    dano = random.randint(config.DANO_MIN_BOSS, config.DANO_MAX_BOSS)
                    jogador.tomar_dano(dano)
                    adicionar_texto_dano(
                        jogador.rect.centerx,
                        jogador.rect.top - 10,
                        dano,
                        (255, 50, 50)
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
                            (255, 50, 50)
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
                adicionar_texto_dano(
                    boss.rect.centerx,
                    boss.rect.top - 10,
                    dano,
                    (255, 255, 0)
                )
                # Toca o som do ataque do player
                if som_player_attack:
                    som_player_attack.set_volume(0.3)
                    som_player_attack.play()


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

        # Renderização
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

        jogador.desenhar(config.TELA)
        if boss.vida > 0:
            boss.desenhar(config.TELA)

        desenhar_textos_dano(config.TELA)

        jogador.desenhar_barra_vida(config.TELA)
        if boss.vida > 0:
            boss.desenhar_barra_vida(config.TELA)

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
        textos_dano = []
        jogo()