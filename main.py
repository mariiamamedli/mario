import os
import sys
import pygame
import time

FPS = 50

up = 0
down = 1
left = 2
right = 3


def load_image(name):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["ПРАВИЛА", "",
                  "Герой двигается",
                  "Карта тоже"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    try:
        with open(filename, 'r') as mapFile:
            level_map = [line.strip() for line in mapFile]
    except:
        print(f"Файл с уровнем '{filename}' не найден")
        exit()

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png')
}
player_image = load_image('mar.png')

tile_width = tile_height = 50


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.type = tile_type
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)

    def update(self, key):
        if key == up:
            x, y = 0, -50
        elif key == down:
            x, y = 0, 50
        elif key == left:
            x, y = -50, 0
        elif key == right:
            x, y = 50, 0
        else:
            return
        self.rect = self.rect.move(x, y)
        if not pygame.sprite.spritecollide(self, tiles_group, dokill=False):
            self.rect = self.rect.move(-x, -y)
            return
        for i in pygame.sprite.spritecollide(self, tiles_group, dokill=False):
            if i.type == 'wall':
                self.rect = self.rect.move(-x, -y)
                return


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy
        if obj.rect.x < 0:
            obj.rect.x += 8 * tile_width
        elif obj.rect.x + tile_width > width:
            obj.rect.x -= 8 * tile_width
        if obj.rect.y < 0:
            obj.rect.y += 8 * tile_height
        elif obj.rect.y + tile_height > height:
            obj.rect.y -= 8 * tile_height

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


# основной персонаж
player = None

# группы спрайтов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


if __name__ == '__main__':
    level = 'lvl0.txt'  # input()
    pygame.init()
    pygame.display.set_caption('Перемещение героя')
    size = width, height = 500, 500
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()
    camera = Camera()
    player, level_x, level_y = generate_level(load_level(level))
    key = 0
    start_screen()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    key = up
                elif event.key == pygame.K_DOWN:
                    key = down
                elif event.key == pygame.K_LEFT:
                    key = left
                elif event.key == pygame.K_RIGHT:
                    key = right
                else:
                    key = None
                player.update(key)
        if key is not None:
            # изменяем ракурс камеры
            camera.update(player);
            # обновляем положение всех спрайтов
            for sprite in all_sprites:
                camera.apply(sprite)
            screen.fill(pygame.Color('black'))
            all_sprites.draw(screen)
            player_group.draw(screen)
            pygame.draw.rect(screen, pygame.Color('black'), (0, 0, width, int(height * 0.15)))
            pygame.draw.rect(screen, pygame.Color('black'), (0, height - int(height * 0.15), width, int(height * 0.15)))
            pygame.draw.rect(screen, pygame.Color('black'), (0, 0, int(width * 0.15), height))
            pygame.draw.rect(screen, pygame.Color('black'), (width - int(width * 0.15), 0, int(width * 0.15), height))
            pygame.display.flip()
        key = None
