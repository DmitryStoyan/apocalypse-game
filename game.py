import pygame
import random
import math

pygame.init()

WIDTH = 1100
HEIGHT = 700
FPS = 60
RED = (255, 0, 0)
BLACK = (0, 0, 0)
score = 0
playerhp = 150
bonus2_spawned = False

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My Game")
clock = pygame.time.Clock()

bg = pygame.image.load("bg.jpeg")
bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))

menu_bg = pygame.image.load("menu_bg2.jpg")
menu_bg = pygame.transform.scale(menu_bg, (WIDTH, HEIGHT))

player = pygame.transform.scale(pygame.image.load("player.png"), (75, 75))
player_rect = player.get_rect()
player_rect.x = 100
player_rect.y = 100

enemy_image = pygame.image.load('zombi.png')
enemy_image = pygame.transform.scale(enemy_image, (75, 75))
enemy_rect = enemy_image.get_rect()
enemy_rect.x = random.randint(0, WIDTH - enemy_rect.width)
enemy_rect.y = 5

enemy2_image = pygame.image.load('zombi2.png')
enemy2_image = pygame.transform.scale(enemy2_image, (150, 100))
enemy2_rect = enemy2_image.get_rect()
enemy2_rect.x = random.randint(0, WIDTH - enemy2_rect.width)
enemy2_rect.y = 5

myFont = pygame.font.SysFont("impact", 50)
game_over_text = myFont.render("Вы проиграли!", True, RED)
button_font = pygame.font.SysFont("impact", 35)

bonus = pygame.transform.scale(pygame.image.load('yabloko.png'), (21, 20))
bonus_rect = bonus.get_rect()
bonus_rect.x = 300
bonus_rect.y = 200

bullet_image = pygame.image.load('pulya.png')
bullet_image = pygame.transform.scale(bullet_image, (10, 10))

pygame.mixer.init()
bonus2_sound = pygame.mixer.Sound('eat.mp3')
bonus2_sound.set_volume(0.9)

bonus2 = pygame.transform.scale(pygame.image.load('aptechka.png'), (40, 40))
bonus2_rect = bonus2.get_rect()
bonus2_rect.x = 9999
bonus2_rect.y = 9999

pygame.mixer.init()
shoot_sound = pygame.mixer.Sound('gun.wav')
shoot_sound.set_volume(0.4)


menu_music = 'menuSound.mp3'
game_music = 'gameSound.mp3'
game_over_music = 'gameOverSound.mp3'

pygame.mixer.music.set_volume(0.5)

def play_music(music_file):
    pygame.mixer.music.load(music_file)
    pygame.mixer.music.play(-1)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.image = bullet_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.angle = angle
        self.speed = 10

    def update(self):
        self.rect.x += self.speed * math.cos(math.radians(self.angle))
        self.rect.y += self.speed * math.sin(math.radians(self.angle))
        if self.rect.bottom < 0 or self.rect.top > HEIGHT or self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()

bullets = pygame.sprite.Group()

speed = 5
angle = 0
enemy_speed = 0.9
enemy2_speed = 0.75

STATE_MENU = 0
STATE_PLAYING = 1
STATE_GAME_OVER = 2
game_state = STATE_MENU

def draw_button(text, x, y, w, h, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if x + w > mouse[0] > x and y + h > y:
        pygame.draw.rect(screen, (170, 170, 170), (x, y, w, h))
        if click[0] == 1 and action is not None:
            action()
    else:
        pygame.draw.rect(screen, (100, 100, 100), (x, y, w, h))

    button_text = button_font.render(text, True, BLACK)
    button_rect = button_text.get_rect(center=(x + w / 2, y + h / 2))
    screen.blit(button_text, button_rect)

def start_game():
    global game_state, playerhp, player_rect, enemy_rect, enemy2_rect, bullets, score
    playerhp = 150
    player_rect.x = 100
    player_rect.y = 100
    enemy_rect.x = random.randint(0, WIDTH - enemy_rect.width)
    enemy_rect.y = 5
    enemy2_rect.x = random.randint(0, WIDTH - enemy2_rect.width)
    enemy2_rect.y = 5
    bullets.empty()
    score = 0
    game_state = STATE_PLAYING
    play_music(game_music)

def go_to_menu():
    global game_state
    game_state = STATE_MENU
    play_music(menu_music)

game_over_bg = pygame.image.load("gameOver_bg.jpeg")
game_over_bg = pygame.transform.scale(game_over_bg, (WIDTH, HEIGHT))

last_shot_time = 0

play_music(menu_music)

running = True

while running:
    current_time = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.blit(bg, (0, 0))

    if game_state == STATE_MENU:
        screen.blit(menu_bg, (0, 0))
        draw_button("Начать игру", WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 50, start_game)
    elif game_state == STATE_PLAYING:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            angle -= 3

        if keys[pygame.K_RIGHT]:
            angle += 3

        if keys[pygame.K_UP]:
            player_rect.x += speed * math.cos(math.radians(angle))
            player_rect.y += speed * math.sin(math.radians(angle))

        if keys[pygame.K_DOWN]:
            player_rect.x -= speed * math.cos(math.radians(angle))
            player_rect.y -= speed * math.sin(math.radians(angle))

        angle = angle % 360

        player_rotated = pygame.transform.rotate(player, -angle)
        player_rotated_rect = player_rotated.get_rect(center=player_rect.center)

        if keys[pygame.K_a]:
            player_rect.move_ip(-5, 0)
        if keys[pygame.K_d]:
            player_rect.move_ip(5, 0)

        if keys[pygame.K_SPACE] and current_time - last_shot_time > 200:
            bullet = Bullet(player_rotated_rect.centerx, player_rotated_rect.centery, angle)
            bullets.add(bullet)
            shoot_sound.play()
            last_shot_time = current_time

        bullets.update()

        def move_enemy(enemy_rect, player_rect, enemy_speed):
            enemy_dx = player_rect.centerx - enemy_rect.centerx
            enemy_dy = player_rect.centery - enemy_rect.centery
            distance = math.sqrt(enemy_dx**2 + enemy_dy**2)
            if distance != 0:
                enemy_dx /= distance
                enemy_dy /= distance
            enemy_rect.x += enemy_dx * enemy_speed
            enemy_rect.y += enemy_dy * enemy_speed

            return enemy_dx, enemy_dy

        def check_collision_with_bullets(enemy_rect):
            global score
            for bullet in bullets:
                if bullet.rect.colliderect(enemy_rect):
                    enemy_rect.x = random.randint(0, WIDTH - enemy_rect.width)
                    enemy_rect.y = random.randint(0, HEIGHT - enemy_rect.height)
                    bullet.kill()
                    score += 1

        enemy_dx, enemy_dy = move_enemy(enemy_rect, player_rect, enemy_speed)
        enemy_angle = math.degrees(math.atan2(-enemy_dy, enemy_dx))
        enemy_rotated = pygame.transform.rotate(enemy_image, enemy_angle)
        enemy_rotated_rect = enemy_rotated.get_rect(center=enemy_rect.center)

        check_collision_with_bullets(enemy_rect)

        if score > 1:
            enemy2_dx, enemy2_dy = move_enemy(enemy2_rect, player_rect, enemy2_speed)
            enemy2_angle = math.degrees(math.atan2(-enemy2_dy, enemy2_dx))
            enemy2_rotated = pygame.transform.rotate(enemy2_image, enemy2_angle)
            enemy2_rotated_rect = enemy2_rotated.get_rect(center=enemy2_rect.center)

            check_collision_with_bullets(enemy2_rect)

            if player_rect.colliderect(enemy2_rect):
                playerhp -= 20
                enemy2_rect.x = random.randint(0, WIDTH - enemy2_rect.width)
                enemy2_rect.y = random.randint(0, HEIGHT - enemy2_rect.height)

            screen.blit(enemy2_rotated, enemy2_rotated_rect)

        if player_rect.colliderect(enemy_rect):
            playerhp -= 20
            enemy_rect.x = random.randint(0, WIDTH - enemy_rect.width)
            enemy_rect.y = random.randint(0, HEIGHT - enemy_rect.height)

        if playerhp <= 0:
            game_state = STATE_GAME_OVER
            play_music(game_over_music)

        if player_rect.colliderect(bonus_rect):
            playerhp += 10
            bonus_rect.x = random.randint(0, 700)
            bonus_rect.y = random.randint(0, 500)
        for bullet in bullets:
          if bullet.rect.colliderect(enemy2_rect):
            enemy2_rect.x = random.randint(0, WIDTH - enemy2_rect.width)
            enemy2_rect.y = random.randint(0, HEIGHT - enemy2_rect.height)
            bullet.kill()
            score += 2

        if score >= 10 and not bonus2_spawned:
            bonus2_rect.x = random.randint(0, 900)
            bonus2_rect.y = random.randint(0, 500)
            bonus2_spawned = True

        if bonus2_rect.colliderect(player_rect):
            playerhp += 50
            bonus2_rect.x = 99999
            bonus2_rect.y = 99999
            bonus2_sound.play()

        pygame.draw.rect(screen, RED, (20, 20, playerhp, 20))
        score_text = myFont.render(f"Счет: {score}", True, BLACK)
        screen.blit(score_text, (20, 350))
        screen.blit(player_rotated, player_rotated_rect)
        screen.blit(enemy_rotated, enemy_rotated_rect)
        screen.blit(bonus, bonus_rect)
        screen.blit(bonus2, bonus2_rect)
        bullets.draw(screen)
    elif game_state == STATE_GAME_OVER:
        screen.blit(game_over_bg, (0, 0))
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 100))
        draw_button("Выйти в меню", WIDTH // 2 - 130, HEIGHT // 2, 250, 50, go_to_menu)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
