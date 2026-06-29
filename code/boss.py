import pygame
import random
import math
from . import config  # <-- ESSENCIAL: importa o módulo config
from .config import LARGURA, ALTURA, ROXO_BOSS, VERMELHO, AMARELO, BRANCO, carregar_imagem

def carregar_sprite_sheet(caminho, qtd_frames, largura_frame, altura_frame, redimensionar=None):
    imagem = carregar_imagem(caminho)
    if not imagem:
        return []
    quadros = []
    for i in range(qtd_frames):
        try:
            quadro = imagem.subsurface(pygame.Rect(i * largura_frame, 0, largura_frame, altura_frame))
            if redimensionar:
                quadro = pygame.transform.scale(quadro, redimensionar)
            quadros.append(quadro)
        except Exception:
            return []
    return quadros

class Boss:
    def __init__(self, x, y):
        TAMANHO_SPRITE = (320, 320)
        self.quadros = {
            "idle": carregar_sprite_sheet("sprite_boss/idle.png", 4, 96, 96, TAMANHO_SPRITE),
            "hurt": carregar_sprite_sheet("sprite_boss/hurt.png", 4, 96, 96, TAMANHO_SPRITE),
            "attack": carregar_sprite_sheet("sprite_boss/attack.png", 4, 96, 96, TAMANHO_SPRITE),
            "death": carregar_sprite_sheet("sprite_boss/death.png", 4, 96, 96, TAMANHO_SPRITE),
        }

        self.hitbox_largura = 50
        self.hitbox_altura = 60
        self.rect = pygame.Rect(x, y, self.hitbox_largura, self.hitbox_altura)
        self.offset_x = 190
        self.offset_y = 200

        self.estado = "idle"
        self.sprite_atual = self.quadros["idle"][0] if self.quadros["idle"] else None

        self.tempo_entre_ataques = 60   # espera 1 segundo antes de atirar
        self.projeteis = []
        self.cor = ROXO_BOSS

        self.vida_maxima = 5000
        self.vida = self.vida_maxima
        self.tomou_dano = False
        self.tempo_morte = 0

        self.projetil_quadros = []
        for i in range(1, 9):
            img = carregar_imagem(f"sprite_boss/efeito/FS_{i}.png", (32, 32))
            if img:
                self.projetil_quadros.append(img)

        # Som do ataque do boss
        self.som_ataque = config.carregar_som("boss_attack.wav")
        if self.som_ataque:
            self.som_ataque.set_volume(0.2)

    def tomar_dano(self, dano=1):
        if self.vida > 0:
            self.vida -= dano
            if self.vida < 0:
                self.vida = 0
            self.tomou_dano = True
            self.cor = BRANCO
            if self.vida == 0:
                self.tempo_morte = 60
                self.estado = "death"
                if self.quadros["death"]:
                    self.sprite_atual = self.quadros["death"][0]

    def atualizar_estado(self, jogador_rect):
        if self.vida <= 0:
            self.estado = "death"
            return
        dx = jogador_rect.centerx - self.rect.centerx
        dy = jogador_rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if self.tempo_entre_ataques < 20:
            self.estado = "attack"
        elif dist > 150:
            self.estado = "hurt"
        else:
            self.estado = "idle"

    def atualizar_animacao(self):
        quadros_estado = self.quadros.get(self.estado, [])
        if quadros_estado:
            self.sprite_atual = quadros_estado[0]
        else:
            self.sprite_atual = None

    def atualizar(self, jogador_rect):
        if self.vida <= 0:
            self.atualizar_animacao()
            if self.tempo_morte > 0:
                self.tempo_morte -= 1
            return

        dx = jogador_rect.centerx - self.rect.centerx
        dy = jogador_rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist > 100:
            velocidade = 2.5
            if dist > 0:
                self.rect.x += (dx / dist) * velocidade
                self.rect.y += (dy / dist) * velocidade

        self.rect.clamp_ip(pygame.Rect(0, 0, LARGURA, ALTURA))

        self.tempo_entre_ataques -= 1
        if self.tempo_entre_ataques <= 0 and dist > 0 and self.vida > 0:
            vel_proj = 5
            dir_x = (dx / dist) * vel_proj
            dir_y = (dy / dist) * vel_proj
            self.projeteis.append({
                'x': self.rect.centerx,
                'y': self.rect.centery,
                'vx': dir_x,
                'vy': dir_y,
                'quadro': 0,
                'timer': 0
            })
            self.tempo_entre_ataques = random.randint(40, 90)
            self.estado = "attack"
            # Toca o som do tiro
            if self.som_ataque:
                self.som_ataque.play()

        for proj in self.projeteis[:]:
            proj['x'] += proj['vx']
            proj['y'] += proj['vy']
            proj['timer'] += 1
            if proj['timer'] >= 4:
                proj['timer'] = 0
                proj['quadro'] = (proj['quadro'] + 1) % 8
            if proj['x'] < -50 or proj['x'] > LARGURA + 50 or proj['y'] < -50 or proj['y'] > ALTURA + 50:
                self.projeteis.remove(proj)

        self.atualizar_estado(jogador_rect)
        self.atualizar_animacao()

        if self.tomou_dano:
            self.tomou_dano = False
            self.cor = ROXO_BOSS

    def desenhar(self, tela):
        if self.sprite_atual:
            pos_x = self.rect.x - self.offset_x
            pos_y = self.rect.y - self.offset_y
            tela.blit(self.sprite_atual, (pos_x, pos_y))
        else:
            pygame.draw.rect(tela, self.cor, self.rect)

        # Debug hitbox
        # pygame.draw.rect(tela, (255, 0, 0), self.rect, 2)

        for proj in self.projeteis:
            if self.projetil_quadros:
                quadro = self.projetil_quadros[proj['quadro']]
                x = int(proj['x'] - quadro.get_width() // 2)
                y = int(proj['y'] - quadro.get_height() // 2)
                tela.blit(quadro, (x, y))
            else:
                pygame.draw.circle(tela, VERMELHO, (int(proj['x']), int(proj['y'])), 12)
                pygame.draw.circle(tela, AMARELO, (int(proj['x']), int(proj['y'])), 6)

    def desenhar_barra_vida(self, tela):
        if self.vida <= 0:
            return
        largura_barra = 350
        altura_barra = 20
        x = (LARGURA - largura_barra) // 2
        y = 20

        fundo_rect = pygame.Rect(x, y, largura_barra, altura_barra)
        pygame.draw.rect(tela, (200, 30, 30), fundo_rect, border_radius=10)

        vida_ratio = self.vida / self.vida_maxima
        largura_vida = vida_ratio * (largura_barra - 4)
        if largura_vida < 0:
            largura_vida = 0

        cor = (200, 30, 30)
        vida_rect = pygame.Rect(x + 2, y + 2, largura_vida, altura_barra - 4)
        pygame.draw.rect(tela, cor, vida_rect, border_radius=2)
        pygame.draw.rect(tela, (0, 0, 0), fundo_rect, 3, border_radius=5)

        fonte_nome = pygame.font.Font(None, 18)
        nome = fonte_nome.render("Fire Ball", True, (200, 30, 30))
        tela.blit(nome, (x + 20, y - 18))

        fonte = pygame.font.Font(None, 26)
        texto = fonte.render(f"{self.vida} / {self.vida_maxima}", True, BRANCO)
        tela.blit(texto, (x + largura_barra // 2 - texto.get_width() // 2, y + 4))