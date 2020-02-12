import pygame
import math
from random import randint
from random import seed

# predefined values
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_FRAMERATE = 30

COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (0, 0, 255)
GAME_STATE = "GAME"


class Background(pygame.sprite.Sprite):
    def __init__(self, background, location):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(background)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location


class Spacecraft(pygame.sprite.Sprite):
    def __init__(self, image_file):
        pygame.sprite.Sprite.__init__(self)
        self.audio_explosion = pygame.mixer.Sound("explosion.wav")
        self.audio_explosion.set_volume(0.2)
        self.explode = pygame.image.load('explosion.png')
        self.image = pygame.image.load(image_file)
        self.center_x = self.image.get_rect().width / 2
        self.center_y = self.image.get_rect().height / 2
        self.x = SCREEN_WIDTH / 2 - self.center_x
        self.y = SCREEN_HEIGHT - self.image.get_rect().height

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

    def move(self, pos_x):
        if (self.x > 0) and (pos_x < 0):
            self.x = self.x + pos_x

        if (self.x < 750) and (pos_x > 0):
            self.x = self.x + pos_x
        screen.blit(self.image, (self.x, self.y))

    def explosion(self):
        screen.blit(self.explode, (self.x - self.center_x, self.y - self.center_y))
        self.audio_explosion.play()


class Laser:
    def __init__(self, x, y):
        self.audio_explosion = pygame.mixer.Sound("laser_explosion.wav")
        self.audio_explosion.set_volume(0.3)
        self.explosion = pygame.image.load('laser_explosion.png')
        self.audio_laser = pygame.mixer.Sound("laser.wav")
        self.audio_laser.play()
        self.image = pygame.image.load('laser.png')
        self.x = x
        self.y = y
        self.center_x = self.image.get_rect().width / 2
        self.center_y = self.image.get_rect().height / 2

    def draw(self):
        self.y -= 5
        return screen.blit(self.image, (self.x, self.y))

    def explode(self):
        screen.blit(self.explosion, (self.x - 50, self.y - 50))
        self.audio_explosion.play()


class Asteroid:
    def __init__(self, x, y):
        self.bg = randint(1, 5)
        self.image = pygame.image.load('asteroid' + str(self.bg) + '.png')
        self.x = x
        self.y = y
        self.center_x = self.image.get_rect().width / 2
        self.center_y = self.image.get_rect().height / 2
        self.move_x = randint(-2, 2)
        self.move_y = randint(1, 4)

    def draw(self):
        return screen.blit(self.image, (self.x, self.y))

    def move(self, pos_x, pos_y):
        self.x = pos_x
        self.y = pos_y

    def update(self):
        self.y = self.y + self.move_y
        if (self.x + self.move_x) > 730:
            self.move_x = -self.move_x
        elif(self.x + self.move_x) < 0:
            self.move_x = abs(self.move_x)
        self.x = self.x + self.move_x

    def collision(self, x, y, type):
        distance = math.sqrt((math.pow((self.x + self.center_x) - x, 2)) + (math.pow((self.y + self.center_y) - y, 2)))
        print(' distance: ' + str(distance))
        print(' asteroid x : ' + str(self.x))
        print(' asteroid y : ' + str(self.y))
        print(' x : ' + str(x))
        print(' y : ' + str(y))
        if distance < 40 and type == "LASER":
            return True
        if distance < 60 and type == "SPACECRAFT":
            return True
        return False


# INITIALIZE
seed(1)
pygame.init()
pygame.display.set_caption("Stellar")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
background = Background('background.png', [0, 0])
spacecraft = Spacecraft('spacecraft.png')
running = True
laser_ready = True

audio_next_wave = pygame.mixer.Sound("nextwave.wav")
audio_next_wave.set_volume(0.05)
pygame.mixer.init()
pygame.mixer.music.load("bgmusic.wav")
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(-1)

clock = pygame.time.Clock()
clock.tick(SCREEN_FRAMERATE)


def draw_text(surf, text, x, y, color):
    font = pygame.font.Font(pygame.font.match_font('arial'), 35)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


while running:
    # timer
    start_ticks = pygame.time.get_ticks()
    score = 0
    # wave settings
    laser_ready = True
    laser = None
    asteroids = [Asteroid(randint(0, 750), randint(1, 5))]
    audio_next_wave.play()
    next_wave = 0
    direction = 0

    # game in progress
    while GAME_STATE == "GAME":
        screen.fill([255, 255, 255])
        screen.blit(background.image, background.rect)
        score = (pygame.time.get_ticks() - start_ticks) / 1000

        if (int(score) % 10 == 0) and (next_wave < int(score)):
            laser_ready = True
            next_wave = int(score)
            audio_next_wave.play()
            for i in range(1, int(score), 4):
                asteroids.append(Asteroid(randint(1, 700), randint(1, 5)))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                direction = 0
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                direction = -5
            if keys[pygame.K_RIGHT]:
                direction = 5
            if keys[pygame.K_SPACE] and laser_ready:
                laser_ready = False
                laser = Laser(spacecraft.x + spacecraft.center_x, spacecraft.y + spacecraft.center_y)

        screen.blit(background.image, background.rect)
        spacecraft.move(direction)

        for index, asteroid in enumerate(asteroids):
            if asteroid.y > 830:
                asteroids.pop(index)
            if asteroid.collision(spacecraft.x + spacecraft.center_x, spacecraft.y + spacecraft.center_y, "SPACECRAFT"):
                spacecraft.explosion()
                GAME_STATE = "GAME_OVER"
            if laser:
                if asteroid.collision(laser.x + laser.center_x, laser.y + laser.center_y, "LASER"):
                    laser.explode()
                    asteroids.pop(index)
                    laser = None
                else:
                    laser.draw()
            asteroid.update()
            asteroid.draw()

        draw_text(screen, 'Wynik: ' + str(score).split(".")[0], SCREEN_WIDTH/2, 10, COLOR_BLUE)
        pygame.display.flip()

    # End game screen
    while GAME_STATE == "GAME_OVER":
        font = pygame.font.Font(pygame.font.match_font('arial'), 25)
        text_final_score = font.render("Koniec gry, wynik: " + str(score).split(".")[0], True, COLOR_RED)
        text_x = screen.get_width() / 2 - text_final_score.get_rect().width / 2
        text_y = screen.get_height() / 2 - text_final_score.get_rect().height / 2
        screen.blit(text_final_score, [text_x, text_y])

        text_new_game = font.render("Naciśnij spacje aby rozpocząć nową grę", True, COLOR_GREEN)
        screen.blit(text_new_game, [text_x - 100, text_y + 100])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                GAME_STATE = "GAME"
        pygame.display.flip()
