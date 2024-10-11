import csv
import os
import random
import pygame
import sys
from button import Button

# facilitará a utilização das funções do pygame
from pygame.math import Vector2
from pygame.draw import rect

# Inicializa a função pygame
pygame.init()

# cria uma variável de ecrã de 800 x 600
resolutionScreen = (1024, 720)
screen = pygame.display.set_mode(resolutionScreen)

# controla o jogo principal while loop
done = False

# controla se o jogo deve ou não ser iniciado a partir do menu principal
start = False # False indica que o jogo não está em andamento
aux_start = False # Variavel auxiliar para inicial pelo botão
waiting = True # True indica que está aguardando no Menu
onShop = False # False indica que a tela da loja está fechada

# define a taxa de quadros do programa
clock = pygame.time.Clock()

"""
CONSTANTES
"""
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

"""As funções lambda são funções anónimas que podem ser atribuídas a uma variável.
e.g.
1. x = lambda x: x + 2 # recebe um parâmetro x e adiciona-lhe 2
2. print(x(4))
>>6
"""
color = lambda: tuple([random.randint(0, 255) for i in range(3)])  # função lambda para a cor aleatória, não uma constante.
GRAVITY = Vector2(0, 0.86)  # Vector2 é um pygame

"""
Classe principal do jogador
"""

def get_font(size): # Retornando a fonte para os botões
    return pygame.font.Font("assets/font.ttf", size)

# Carregando o plano de fundo do menu
BG_MENU = pygame.image.load("assets/bg-cemitery.jpg")

class Player(pygame.sprite.Sprite):
    """Classe para o jogador. Contém o método de atualização, variáveis de vitória e morte, colisões e mais."""
    win: bool
    died: bool

    def __init__(self, image, platforms, pos, *groups):
        """
        :param imagem: avatar do rosto do bloco
        :param plataformas: obstáculos como moedas, blocos, picos e esferas
        :param pos: posição inicial
        :param groups: recebe qualquer número de grupos de actores.
        """
        super().__init__(*groups)
        self.onGround = False  # jogador no chão?
        self.platforms = platforms  # obstáculos mas cria uma variável de classe para isso
        self.died = False  # o jogador morreu?
        self.win = False  #  o jogador venceu o nível?

        self.image = pygame.transform.smoothscale(image, (32, 32))
        self.rect = self.image.get_rect(center=pos)  # get rect obtém um objeto Rect a partir da imagem
        self.jump_amount = 10.1  # força do salto
        self.particles = []  # rasto do jogador
        self.isjump = False  # o jogador está a saltar?
        self.vel = Vector2(0, 0)  # a velocidade começa em zero

    def draw_particle_trail(self, x, y, color=(255, 255, 255)):
        """desenha um rasto de partículas-reto numa linha em posições aleatórias atrás do jogador"""

        self.particles.append(
                [[x - 5, y - 8], [random.randint(0, 25) / 10 - 1, random.choice([0, 0])],
                 random.randint(5, 8)])

        for particle in self.particles:
            particle[0][0] += particle[1][0]
            particle[0][1] += particle[1][1]
            particle[2] -= 0.5
            particle[1][0] -= 0.4
            rect(alpha_surf, color,
                 ([int(particle[0][0]), int(particle[0][1])], [int(particle[2]) for i in range(2)]))
            if particle[2] <= 0:
                self.particles.remove(particle)

    def collide(self, yvel, platforms):
        global coins

        for p in platforms:
            if pygame.sprite.collide_rect(self, p):
                """método de colisão do sprite do pygame,
                vê se o jogador está a colidir com algum obstáculo"""
                if isinstance(p, Orb) and (keys[pygame.K_UP] or keys[pygame.K_SPACE]):
                    pygame.draw.circle(alpha_surf, (255, 255, 0), p.rect.center, 18)
                    screen.blit(pygame.image.load("images/editor-0.9s-47px.gif"), p.rect.center)
                    self.jump_amount = 12  # dá um pequeno impulso quando a esfera é atingida
                    self.jump()
                    self.jump_amount = 10  # volta o jump_amount ao normal

                if isinstance(p, End):
                    self.win = True

                if isinstance(p, Spike):
                    self.died = True  # morre no spike

                if isinstance(p, Coin):
                    # mantém o registo de todas as moedas durante todo o jogo (é possível um total de 6)
                    coins += 1

                    # apaga uma moeda
                    p.rect.x = 0
                    p.rect.y = 0

                if isinstance(p, Platform):  #  estes são os blocos (pode ser confuso devido a self.platforms)

                    if yvel > 0:
                        """se o jogador estiver a descer(yvel é +)"""
                        self.rect.bottom = p.rect.top  # não deixar o jogador atravessar o chão
                        self.vel.y = 0  # velocidade y restante porque o jogador está no chão

                        # define self.onGround para true porque o jogador colidiu com o chão
                        self.onGround = True

                        # reseta o pulo
                        self.isjump = False
                    elif yvel < 0:
                        """se y vel for (-),o jogador colidiu enquanto saltava"""
                        self.rect.top = p.rect.bottom  # o topo do jogador é colocado no fundo do bloco como se batesse na cabeça
                    else:
                        """caso contrário, se o jogador colidir com um bloco, morre"""
                        self.vel.x = 0
                        self.rect.right = p.rect.left  # não deixar o jogador atravessar paredes
                        self.died = True

    def jump(self):
        self.vel.y = -self.jump_amount  # a velocidade vertical do jogador é negativa, por isso ^

    def update(self):
        """atualizar jogador"""
        if self.isjump:
            if self.onGround:
                """se o jogador quiser saltar e estiver no chão: só então é permitido saltar"""
                self.jump()

        if not self.onGround:  # só acelera com a gravidade se estiver no ar
            self.vel += GRAVITY  # A gravidade cai

            # velocidade máxima de queda
            if self.vel.y > 100: self.vel.y = 100

        # faz colisões no eixo x
        self.collide(0, self.platforms)

        # incrementar na direção y
        self.rect.top += self.vel.y

        # assumindo que o jogador está no ar, e se não estiver, será definido como invertido após a colisão
        self.onGround = False

        # faz colisões no eixo y
        self.collide(self.vel.y, self.platforms)

        # Verificar se ganhámos ou se o jogador ganhou
        eval_outcome(self.win, self.died)


"""
CLASSE DE OBSTACULOS
"""


# Classe parental
class Draw(pygame.sprite.Sprite):
    """classe-mãe de todas as classes de obstáculos; classe Sprite"""

    def __init__(self, image, pos, *groups):
        super().__init__(*groups)
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)


#  ====================================================================================================================#
#  classes de todos os obstáculos. isto pode parecer repetitivo mas é útil (tanto quanto sei)
#  ====================================================================================================================#
#  filhos
class Platform(Draw):
    """bloco"""

    def __init__(self, image, pos, *groups):
        super().__init__(image, pos, *groups)


class Spike(Draw):
    """espinho"""

    def __init__(self, image, pos, *groups):
        super().__init__(image, pos, *groups)


class Coin(Draw):
    """moeda. Se conseguir 6, ganhas o jogo"""

    def __init__(self, image, pos, *groups):
        super().__init__(image, pos, *groups)


class Orb(Draw):
    """orbe. clica no espaço ou na seta para cima enquanto estás em cima dela para saltares no ar"""

    def __init__(self, image, pos, *groups):
        super().__init__(image, pos, *groups)


class Trick(Draw):
    """”bloco, mas é um truque porque podes passar por ele"""

    def __init__(self, image, pos, *groups):
        super().__init__(image, pos, *groups)


class End(Draw):
    "coloca isto no fim do nível"

    def __init__(self, image, pos, *groups):
        super().__init__(image, pos, *groups)


"""
FUNÇÕES
"""


def init_level(map):
    """é semelhante às listas 2d. Percorre uma lista de listas e cria instâncias de determinados obstáculos
    dependendo do item da lista"""
    x = 0
    y = 0

    for row in map:
        for col in row:

            if col == "0":
                Platform(block, (x, y), elements)

            if col == "C":
                Coin(coin, (x, y), elements)

            if col == "S":
                Spike(spike, (x, y), elements)
            if col == "O":
                orbs.append([x, y])

                Orb(orb, (x, y), elements)

            if col == "T":
                Trick(trick, (x, y), elements)

            if col == "End":
                End(avatar, (x, y), elements)
            x += 32
        y += 32
        x = 0


def blitRotate(surf, image, pos, originpos: tuple, angle: float):
    """
    :rodar o jogador
    :param surf: superfície
    :param image: imagem a rodar
    :param pos: posição da imagem
    :param originpos: x, y da origem em torno da qual rodar
    :param angle: ângulo a rodar
    """
    # calcula a caixa delimitadora alinhada com o eixo da imagem rodada
    w, h = image.get_size()
    box = [Vector2(p) for p in [(0, 0), (w, 0), (w, -h), (0, -h)]]
    box_rotate = [p.rotate(angle) for p in box]

    # certifica-se de que o jogador não se sobrepõe, utiliza algumas funções lambda (coisas novas que não aprendemos sobre o número 1)
    min_box = (min(box_rotate, key=lambda p: p[0])[0], min(box_rotate, key=lambda p: p[1])[1])
    max_box = (max(box_rotate, key=lambda p: p[0])[0], max(box_rotate, key=lambda p: p[1])[1])
    # calcula a translação do pivot
    pivot = Vector2(originpos[0], -originpos[1])
    pivot_rotate = pivot.rotate(angle)
    pivot_move = pivot_rotate - pivot

    # calcula a origem superior esquerda da imagem rodada
    origin = (pos[0] - originpos[0] + min_box[0] - pivot_move[0], pos[1] - originpos[1] - max_box[1] + pivot_move[1])

    # obter uma imagem rodada
    rotated_image = pygame.transform.rotozoom(image, angle, 1)

    # Rodar e esbater a imagem
    surf.blit(rotated_image, origin)


def won_screen():
    """mostra este ecrã quando se vence um nível"""
    global attempts, level, fill
    attempts = 0
    player_sprite.clear(player.image, screen)
    screen.fill(pygame.Color("yellow"))
    txt_win1 = txt_win2 = "Nada"
    if level == 1:
        if coins == 6:
            txt_win1 = f"Coin{coins}/6! "
            txt_win2 = "Venceu o jogo, Parabéns"
    else:
        txt_win1 = f"level{level}"
        txt_win2 = f"Coins: {coins}/6. "
    txt_win = f"{txt_win1} You beat {txt_win2}! Aperte ESPAÇO para recomeçar, ou ESC para sair"

    won_game = font.render(txt_win, True, BLUE)

    screen.blit(won_game, (200, 300))
    level += 1

    # wait_for_key()
    reset()


def death_screen():
    """mostra este ecrã na morte"""
    global attempts, fill
    fill = 0
    player_sprite.clear(player.image, screen)
    attempts += 1
    game_over = font.render("Fim do jogo,[ESPAÇO] para reiniciar", True, WHITE)

    screen.fill(pygame.Color("sienna1"))
    screen.blits([[game_over, (100, 100)], [tip, (100, 400)]])
    
    # Chamar a tela inicial depois da morrer
    # global start
    # start = False
    # wait_for_key()
    
    reset()


def eval_outcome(won: bool, died: bool):
    """função simples para executar o ecrã de vitória ou morte após a verificação de vitória ou morte"""
    if won:
        won_screen()
    if died:
        death_screen()


def block_map(level_num):
    """
    :abre um ficheiro csv que contenha o mapa de níveis correto
    """
    lvl = []
    with open(level_num, newline='') as csvfile:
        trash = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in trash:
            lvl.append(row)
    return lvl

def start_game():
    global aux_start, onShop, waiting, start
    onShop = False
    waiting = False
    aux_start = True
    
    if aux_start == True:
        start = True

def open_shop():
    global onShop
    onShop = True
    while onShop:
        PLAY_MOUSE_POS = pygame.mouse.get_pos()
        screen.fill(BLACK)

        title = font.render(f"Loja", True, WHITE)
        screen.blit(title, (100, 100))
        
        BUTTON_BACK = Button(image=None, pos=(512, 675), 
                            text_input="VOLTAR", font=get_font(16), base_color="White", hovering_color="Green")
        
        BUTTON_BACK.changeColor(PLAY_MOUSE_POS)
        BUTTON_BACK.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if BUTTON_BACK.checkForInput(PLAY_MOUSE_POS):
                    onShop = False
                    start_screen()

        pygame.display.update()

def start_screen():
    """menu principal. opção para mudar de nível, guia de controlos e visão geral do jogo."""
    global level
    pygame.mixer.music.set_volume(0.1)
    if not start and onShop == False:
        PLAY_MOUSE_POS = pygame.mouse.get_pos()
        screen.blit(BG_MENU, (0,0))
        
        welcome = font.render(f"Super Mauro Bros", True, WHITE)
        screen.blit(welcome, (100, 100))
        
        BUTTON_START = Button(image=None, pos=(512, 320), 
                    text_input="INICIAR", font=get_font(16), base_color="White", hovering_color="Green")
        BUTTON_SHOP = Button(image=None, pos=(512, 370), 
                    text_input="LOJA", font=get_font(16), base_color="White", hovering_color="Purple")
        BUTTON_CLOSE = Button(image=None, pos=(512, 420), 
                    text_input="SAIR", font=get_font(16), base_color="White", hovering_color="Red")
        
        BUTTON_START.changeColor(PLAY_MOUSE_POS)
        BUTTON_START.update(screen)
        BUTTON_SHOP.changeColor(PLAY_MOUSE_POS)
        BUTTON_SHOP.update(screen)
        BUTTON_CLOSE.changeColor(PLAY_MOUSE_POS)
        BUTTON_CLOSE.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if BUTTON_START.checkForInput(PLAY_MOUSE_POS):
                    start_game()
                if BUTTON_SHOP.checkForInput(PLAY_MOUSE_POS):
                    open_shop()
                if BUTTON_CLOSE.checkForInput(PLAY_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()


def reset():
    """reinicia os grupos de atores, a música, etc. para a morte e o novo nível"""
    global player, elements, player_sprite, level

    if level == 1:
        pygame.mixer.music.load(os.path.join("assets/music", "castle-town.mp3"))
    pygame.mixer.music.set_volume(0.1)
    pygame.mixer_music.play()
    player_sprite = pygame.sprite.Group()
    elements = pygame.sprite.Group()
    player = Player(avatar, elements, (150, 150), player_sprite)
    init_level(
            block_map(
                    level_num=levels[level]))


def move_map():
    """move obstáculos ao longo do ecrã"""
    for sprite in elements:
        sprite.rect.x -= CameraX


def draw_stats(surf, money=0):
    """
    desenha uma barra de progresso para o nível, número de tentativas, apresenta as moedas recolhidas e altera progressivamente a barra de progresso
    cores
    """
    global fill
    progress_colors = [pygame.Color("red"), pygame.Color("orange"), pygame.Color("yellow"), pygame.Color("lightgreen"),
                       pygame.Color("green")]

    tries = font.render(f" Progresso {str(attempts)}", True, WHITE)
    BAR_LENGTH = 498
    BAR_HEIGHT = 12
    for i in range(1, money):
        screen.blit(coin, (BAR_LENGTH, 25))
    if (fill <= BAR_LENGTH):
        fill += 0.5
        print('Barra de Progresso: ' + str(fill) + '%') # Teste para ver progressão
    else:
        fill += 0.0
    outline_rect = pygame.Rect(0, 0, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(0, 0, fill, BAR_HEIGHT)
    col = progress_colors[int(fill / 100)]
    rect(surf, col, fill_rect, 0, 4)
    rect(surf, WHITE, outline_rect, 3, 4)
    screen.blit(tries, (BAR_LENGTH, 0))


def wait_for_key():
    """loop de jogo separado para aguardar o pressionamento de uma tecla enquanto ainda executa o loop de jogo
    """
    global aux_start, start, waiting, onShop
    aux_start = False
    pygame.mixer.music.set_volume(0.1)
    while waiting:
        clock.tick(60)
        pygame.display.flip()

        if not start and onShop == False:
            start_screen()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
        pygame.display.update()


def coin_count(coins):
    """conta moedas"""
    if coins >= 3:
        coins = 3
    coins += 1
    return coins


def resize(img, size=(32, 32)):
    """redimensionar imagens
    param img: imagem a redimensionar
    tipo img: não tenho a certeza, provavelmente um objeto
    param size: a predefinição é 32 porque esse é o tamanho do mosaico
    tipo tamanho: tupla
    :return: imagem redimensionada

    :rtype:objeto??
    """
    resized = pygame.transform.smoothscale(img, size)
    return resized


"""
VARIAVEIS GLOBAIS
"""
font = pygame.font.SysFont("lucidaconsole", 20)

# a face quadrada do bloco é o personagem principal o ícone da janela é a face do bloco
avatar = pygame.image.load(os.path.join("assets/images", "avatar.png"))  # carrega o personagem principal
pygame.display.set_icon(avatar)
#  esta superfície tem um valor alfa com as cores, então o rastro do jogador desaparecerá usando opacidade
alpha_surf = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

# grupos de sprites
player_sprite = pygame.sprite.Group()
elements = pygame.sprite.Group()

# imagens
spike = pygame.image.load(os.path.join("assets/images", "obj-spike.png"))
spike = resize(spike)
coin = pygame.image.load(os.path.join("assets/images", "coin.png"))
coin = pygame.transform.smoothscale(coin, (32, 32))
block = pygame.image.load(os.path.join("assets/images", "block_1.png"))
block = pygame.transform.smoothscale(block, (32, 32))
orb = pygame.image.load((os.path.join("assets/images", "orb-yellow.png")))
orb = pygame.transform.smoothscale(orb, (32, 32))
trick = pygame.image.load((os.path.join("assets/images", "obj-breakable.png")))
trick = pygame.transform.smoothscale(trick, (32, 32))

#  inteiros
fill = 0
num = 0
CameraX = 0
attempts = 0
coins = 0
angle = 0
level = 0

# lista
particles = []
orbs = []
win_cubes = []

# inicializa o nivel com
levels = ["level_1.csv", "level_2.csv"]
level_list = block_map(levels[level])
level_width = (len(level_list[0]) * 32)
level_height = len(level_list) * 32
init_level(level_list)

# defini o título da janela adequado para o jogo
pygame.display.set_caption('Super Mauro Bros')

# inicializar a variável de fonte para desenhar texto mais tarde
text = font.render('image', False, (255, 255, 0))

# musica
music = pygame.mixer_music.load(os.path.join("assets/music", "bossfight-Vextron.mp3"))
pygame.mixer.music.set_volume(0.1)
pygame.mixer_music.play()

# imagem de fundo
imgGame = pygame.image.load(os.path.join("assets/images", "bg.png"))
bg = pygame.transform.scale(imgGame, resolutionScreen)

# cria objeto da classe player
player = Player(avatar, elements, (150, 150), player_sprite)

# mostra dica ao começar e ao morrer
tip = font.render("Dica: toque e segure durante os primeiros segundos do nível", True, BLUE)

while not done:
    keys = pygame.key.get_pressed()

    if not start and onShop == False:
        wait_for_key()
        reset()

        start = True

    player.vel.x = 6

    eval_outcome(player.win, player.died)
    if keys[pygame.K_UP] or keys[pygame.K_SPACE]:
        player.isjump = True

    # Reduz o alfa de todos os pixels nesta superfície a cada quadro.
    # Controla a velocidade do fade2 com o valor alfa.

    alpha_surf.fill((255, 255, 255, 1), special_flags=pygame.BLEND_RGBA_MULT)

    player_sprite.update()
    CameraX = player.vel.x  # para mover obstáculos
    move_map()  # aplicar CameraX a todos os elementos

    screen.blit(bg, (0, 0))  # Limpar a tela (com o bg)

    player.draw_particle_trail(player.rect.left - 1, player.rect.bottom + 2,
                               WHITE)
    screen.blit(alpha_surf, (0, 0))  # Aplicar o alpha_surf na tela.
    draw_stats(screen, coin_count(coins))

    if player.isjump:
        """gira o jogador em um ângulo e faz blit se o jogador estiver pulando"""
        angle -= 8.1712  # este pode ser o ângulo necessário para fazer uma volta de 360 ​​graus no comprimento coberto em um salto pelo jogador
        blitRotate(screen, player.image, player.rect.center, (16, 16), angle)
    else:
        """ise player.isjump for falso, então faça blit normalmente (usando Group().draw() para sprites"""
        player_sprite.draw(screen)  # desenha o grupo de sprites do jogador
    elements.draw(screen)  # desenha todos os outros obstáculos

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                """User friendly exit"""
                done = True
            if event.key == pygame.K_2:
                """change level by keypad"""
                player.jump_amount += 1

            if event.key == pygame.K_1:
                """change level by keypad"""

                player.jump_amount -= 1

    pygame.display.flip()
    clock.tick(60)
pygame.quit()
sys.exit()