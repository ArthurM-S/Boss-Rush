import pygame
import math
from .config import LARGURA, ALTURA, AZUL, BRANCO, AMARELO, VERMELHO, carregar_imagem

def carregar_sprite_sheet(caminho, qtd_frames, largura_frame, altura_frame, redimensionar=None):
    imagem = carregar_imagem(caminho)
    if not imagem:
        print(f"Erro: imagem não encontrada: {caminho}")
        return []
    quadros = []
    for i in range(qtd_frames):
        try:
            quadro = imagem.subsurface(pygame.Rect(i * largura_frame, 0, largura_frame, altura_frame))
            if redimensionar:
                quadro = pygame.transform.scale(quadro, redimensionar)
            quadros.append(quadro)
        except ValueError as e:
            print(f"Erro ao recortar quadro {i} de {caminho}: {e}")
            return []
    return quadros

class Jogador:
    def __init__(self, x, y):
        TAMANHO_SPRITE = (160, 160)
        self.quadros = {
            "idle": carregar_sprite_sheet("sprite_player/idle.png", 4, 96, 96, TAMANHO_SPRITE),
            "run": carregar_sprite_sheet("sprite_player/run.png", 4, 96, 96, TAMANHO_SPRITE),
            "jump": carregar_sprite_sheet("sprite_player/jump.png", 4, 96, 96, TAMANHO_SPRITE),
            "attack": carregar_sprite_sheet("sprite_player/attack.png", 4, 96, 96, TAMANHO_SPRITE),
            "death": carregar_sprite_sheet("sprite_player/death.png", 4, 96, 96, TAMANHO_SPRITE),
        }

        # Define a hitbox (colisão)
        self.hitbox_largura = 25
        self.hitbox_altura = 50
        self.rect = pygame.Rect(x, y, self.hitbox_largura, self.hitbox_altura)
        # Offset para centralizar a sprite na hitbox
        self.offset_x = 60
        self.offset_y = 90

        self.estado = "idle"
        self.quadro_atual = 0
        self.tempo_animacao = 0
        self.velocidade_animacao = 6
        self.sprite_atual = self.quadros["idle"][0] if self.quadros["idle"] else None

        self.vel_x = 0
        self.vel_y = 0
        self.ataque_cooldown = 0
        self.ataque_ativo = False
        self.direcao = 1
        self.angulo = 0

        self.vida_maxima = 500
        self.vida = self.vida_maxima
        self.invencivel = False
        self.tempo_invencivel = 0
        self.tempo_morte = 0

        self.sprint_cooldown = 0
        self.sprint_ativo = False
        self.sprint_timer = 0
        self.velocidade_base = 6
        self.velocidade_sprint = 14

    def tomar_dano(self, dano=1):
        if not self.invencivel and self.vida > 0:
            self.vida -= dano
            if self.vida < 0:
                self.vida = 0
            if self.vida == 0:
                self.tempo_morte = 60
            else:
                self.invencivel = True
                self.tempo_invencivel = 30

    def atualizar_estado(self, teclas, ataque_ativo):
        if self.vida <= 0:
            self.estado = "death"
        elif ataque_ativo:
            self.estado = "attack"
        elif teclas[pygame.K_a] or teclas[pygame.K_d] or teclas[pygame.K_w] or teclas[pygame.K_s]:
            self.estado = "run"
        else:
            self.estado = "idle"

        quadros_estado = self.quadros.get(self.estado, [])
        if quadros_estado:
            if self.quadro_atual >= len(quadros_estado):
                self.quadro_atual = 0
            self.sprite_atual = quadros_estado[self.quadro_atual]
        else:
            self.sprite_atual = self.quadros["idle"][0] if self.quadros["idle"] else None

    def atualizar_animacao(self):
        quadros_estado = self.quadros.get(self.estado, [])
        if not quadros_estado:
            return

        if self.estado == "death":
            if self.quadro_atual < len(quadros_estado) - 1:
                self.tempo_animacao += 1
                if self.tempo_animacao >= self.velocidade_animacao:
                    self.tempo_animacao = 0
                    self.quadro_atual += 1
                    self.sprite_atual = quadros_estado[self.quadro_atual]
            else:
                self.sprite_atual = quadros_estado[-1]
            return

        self.tempo_animacao += 1
        if self.tempo_animacao >= self.velocidade_animacao:
            self.tempo_animacao = 0
            self.quadro_atual = (self.quadro_atual + 1) % len(quadros_estado)
            self.sprite_atual = quadros_estado[self.quadro_atual]

    def atualizar(self, teclas, pos_mouse=None):
        if pos_mouse:
            dx = pos_mouse[0] - self.rect.centerx
            dy = pos_mouse[1] - self.rect.centery
            if dx != 0 or dy != 0:
                self.angulo = math.atan2(dy, dx)
                self.direcao = 1 if dx > 0 else -1

        velocidade = self.velocidade_sprint if self.sprint_ativo else self.velocidade_base

        self.vel_x = 0
        if teclas[pygame.K_a]:
            self.vel_x = -velocidade
        if teclas[pygame.K_d]:
            self.vel_x = velocidade

        self.vel_y = 0
        if teclas[pygame.K_w]:
            self.vel_y = -velocidade
        if teclas[pygame.K_s]:
            self.vel_y = velocidade

        if teclas[pygame.K_LSHIFT] and self.sprint_cooldown == 0 and not self.sprint_ativo:
            self.sprint_ativo = True
            self.sprint_timer = 30
            self.sprint_cooldown = 60

        if self.sprint_ativo:
            self.sprint_timer -= 1
            if self.sprint_timer <= 0:
                self.sprint_ativo = False

        if self.sprint_cooldown > 0:
            self.sprint_cooldown -= 1

        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        # Limites da arena
        from .config import LIMITE_ESQUERDA, LIMITE_DIREITA, LIMITE_TOPO, LIMITE_BAIXO
        if self.rect.left < LIMITE_ESQUERDA:
            self.rect.left = LIMITE_ESQUERDA
        if self.rect.right > LIMITE_DIREITA:
            self.rect.right = LIMITE_DIREITA
        if self.rect.top < LIMITE_TOPO:
            self.rect.top = LIMITE_TOPO
        if self.rect.bottom > LIMITE_BAIXO:
            self.rect.bottom = LIMITE_BAIXO

        if self.ataque_cooldown > 0:
            self.ataque_cooldown -= 1
        if self.ataque_cooldown == 0:
            self.ataque_ativo = False

        if self.invencivel:
            self.tempo_invencivel -= 1
            if self.tempo_invencivel <= 0:
                self.invencivel = False

        self.atualizar_estado(teclas, self.ataque_ativo)
        self.atualizar_animacao()

    def atacar(self):
        if self.ataque_cooldown == 0:
            self.ataque_ativo = True
            self.ataque_cooldown = 20

    def get_rect_ataque(self):
        if not self.ataque_ativo:
            return None
        alcance = 120
        espessura = 80
        cx = self.rect.centerx
        cy = self.rect.centery
        dx = math.cos(self.angulo) * alcance
        dy = math.sin(self.angulo) * alcance

        if abs(dx) > abs(dy):
            if dx > 0:
                return pygame.Rect(cx, cy - espessura//2, alcance, espessura)
            else:
                return pygame.Rect(cx - alcance, cy - espessura//2, alcance, espessura)
        else:
            if dy > 0:
                return pygame.Rect(cx - espessura//2, cy, espessura, alcance)
            else:
                return pygame.Rect(cx - espessura//2, cy - alcance, espessura, alcance)

    def desenhar(self, tela):
        if self.sprite_atual:
            #Calcula a posição real do sprite usando os offsets
            pos_x = self.rect.x - self.offset_x
            pos_y = self.rect.y - self.offset_y

            if self.invencivel and (self.tempo_invencivel // 5) % 2 == 0:
                sprite_temp = self.sprite_atual.copy()
                sprite_temp.set_alpha(128)
                #Pos_x e pos_y calculados
                tela.blit(sprite_temp, (pos_x, pos_y))
            else:
                if self.direcao == -1:
                    sprite_virada = pygame.transform.flip(self.sprite_atual, True, False)
                    tela.blit(sprite_virada, (pos_x, pos_y))
                else:
                    tela.blit(self.sprite_atual, (pos_x, pos_y))
        else:
            pygame.draw.rect(tela, AZUL, self.rect)

        #pygame.draw.rect(tela, (255, 0, 0), self.rect, 2)

    def desenhar_barra_vida(self, tela):
        largura_barra = 180
        altura_barra = 14
        x = 15
        y = 80

        fundo_rect = pygame.Rect(x, y, largura_barra, altura_barra)
        pygame.draw.rect(tela, (30, 30, 30), fundo_rect, border_radius=8)

        vida_ratio = self.vida / self.vida_maxima
        largura_vida = vida_ratio * (largura_barra - 4)
        if largura_vida < 0:
            largura_vida = 0

        if vida_ratio > 0.6:
            cor = (0, 220, 0)
        elif vida_ratio > 0.3:
            cor = (255, 220, 0)
        else:
            cor = (220, 30, 30)

        vida_rect = pygame.Rect(x + 2, y + 2, largura_vida, altura_barra - 4)
        pygame.draw.rect(tela, cor, vida_rect, border_radius=6)
        pygame.draw.rect(tela, (200, 200, 200), fundo_rect, 2, border_radius=8)

        fonte = pygame.font.Font(None, 24)
        texto = fonte.render(f"Arthimus: {self.vida}/{self.vida_maxima}", True, (255, 255, 255))
        tela.blit(texto, (x + 10, y - 24))