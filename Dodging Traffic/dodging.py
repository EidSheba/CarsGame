import pygame
import sys
import random
import time

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Frame rate
FPS = 60
clock = pygame.time.Clock()

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Load images
def load_image(path, width=None, height=None):
    try:
        image = pygame.image.load(path).convert_alpha()
        if width and height:
            image = pygame.transform.scale(image, (width, height))
        return image
    except Exception as e:
        print(f"Error loading image: {path}. {e}")
        return pygame.Surface((width or 50, height or 50))

# Load sounds
def load_sound(path):
    try:
        sound = pygame.mixer.Sound(path)
        return sound
    except Exception as e:
        print(f"Error loading sound: {path}. {e}")
        return None

click_sound = load_sound("click.wav")
background_music = load_sound("background.wav")
victory_sound = load_sound("victory.wav")
collision_sound = load_sound("crash.wav")
coin_sound = load_sound("coin_collect.wav") 

# Game assets
background_img = load_image("background.png", SCREEN_WIDTH, SCREEN_HEIGHT)
cloud1_img = load_image("cloud.png", 200, 75)
cloud2_img = load_image("cloud2.png", 175, 65)
level1_btn_img = load_image("level1.png", 200, 50)
level2_btn_img = load_image("level2.png", 200, 50)
level3_btn_img = load_image("level3.png", 200, 50)
play_btn_img = load_image("play.png", 200, 50)
player_img = load_image("player2.png", 100, 120)
enemy_img = load_image("enemy4.png",110 ,125)
same_dir_enemy_img = load_image("Enemy8.png", 110, 125)
rock_img = load_image("Rock.png", 60, 70)
street_img = load_image("AnimatedStreet.png", SCREEN_WIDTH, SCREEN_HEIGHT)
finishing_line_img = load_image("FinishingLine.png", SCREEN_WIDTH, 30)
lose_img = load_image("game_over_background.png", SCREEN_WIDTH, SCREEN_HEIGHT)
win_img = load_image("you_win_background.png", SCREEN_WIDTH, SCREEN_HEIGHT)
coin_img = load_image("coin.png", 70, 70)
# Fonts
font = pygame.font.SysFont("Arial", 30)
large_font = pygame.font.SysFont("Arial", 40)

# Game states
selected_level = None
message = ""

# Start screen
def start_screen():
    global selected_level, message
    cloud1_x = SCREEN_WIDTH
    cloud2_x = -cloud2_img.get_width()
    cloud1_y = int(SCREEN_HEIGHT * 0.1)
    cloud2_y = int(SCREEN_HEIGHT * 0.2)

    button_surfaces = [level1_btn_img, level2_btn_img, level3_btn_img, play_btn_img]
    btn_width = 200
    btn_height = 50
    x_pos = (SCREEN_WIDTH - btn_width) // 2
    gap = 20
    start_y = SCREEN_HEIGHT - 200
    y_positions = [start_y - i * (btn_height + gap) for i in range(4)]
    
    


    running = True
    while running:
        screen.blit(background_img, (0, 0))

        cloud1_x -= 1
        if cloud1_x < -cloud1_img.get_width():
            cloud1_x = SCREEN_WIDTH
        cloud2_x += 1
        if cloud2_x > SCREEN_WIDTH:
            cloud2_x = -cloud2_img.get_width()

        screen.blit(cloud1_img, (cloud1_x, cloud1_y))
        screen.blit(cloud2_img, (cloud2_x, cloud2_y))

        button_rects = []
        for i, y in enumerate(y_positions):
            rect = pygame.Rect(x_pos, y, btn_width, btn_height)
            screen.blit(button_surfaces[i], rect.topleft)
            button_rects.append(rect)

        if message:
            text_surface = font.render(message, True, BLACK)
            screen.blit(text_surface, (20,500 ))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(mx, my):
                        if i < 3:
                            selected_level = i + 1
                            message = f"Level {selected_level} selected"
                            if click_sound:
                                click_sound.play()  # Play sound on level select
                        else:
                            if selected_level is None:
                                message = "Choose level first"
                            else:
                                game_loop(selected_level)
                                selected_level = None
                                message = ""
                        break

        clock.tick(FPS)

def pause_screen():
    pygame.mixer.music.pause()  # Pause background music
    paused = True
    while paused:
        screen.fill(BLACK)
        pause_text = large_font.render("Paused", True, WHITE)
        resume_text = font.render("Press ESC to Resume", True, WHITE)
        screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 3))
        screen.blit(resume_text, (SCREEN_WIDTH // 2 - resume_text.get_width() // 2, SCREEN_HEIGHT // 2))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                paused = False
                pygame.mixer.music.unpause()  # Resume background music

        clock.tick(FPS)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.inflate_ip(-55, -20)# Shrink collision box (optional tuning)

        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 85)

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.move_ip(-5, 0)
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.move_ip(5, 0)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, image, speed):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.inflate_ip(-55,-20) 

        self.rect.center = (random.randint(50, SCREEN_WIDTH - 50), -50)
        self.base_speed = speed
        self.speed = speed

    def update(self):
        self.rect.move_ip(0, self.speed)
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class SameDirectionEnemy(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.inflate_ip(-55, - 20)# Shrink collision box (optional tuning)

        self.rect.center = (random.randint(50, SCREEN_WIDTH - 50), -100)

    def update(self, speed):
        self.rect.move_ip(0, speed)
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = coin_img  # تأكد من أنك تضيف صورة للكوي
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(50, SCREEN_WIDTH - 50), -40)
    def update(self):
        self.rect.move_ip(0, 5)  # سرعة نزول الكوين
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()  # إذا الكوين خرجت من الشاشة يتم حذفها

# Check collision
def check_collision(player, enemies):
    for enemy in enemies:
        if player.rect.colliderect(enemy.rect):
            return True
    return False

def game_loop(level):
    player = Player()
    player_group = pygame.sprite.Group(player)
    enemies = pygame.sprite.Group()
    same_direction_enemies = pygame.sprite.Group()
    coins = pygame.sprite.Group()  # مجموعة الكوينز
    street_y = 0
    base_speed = 5
    score = 0
    start_time = None
    enemy_timer = time.time()
    same_dir_timer = time.time()
    coin_timer = time.time()  # Timer لاضافة كوينات جديدة
    finishing_line_y = -30
    finishing_line_reached = False

    if background_music:
        pygame.mixer.music.load("background.wav")
        pygame.mixer.music.play(-1, 0.0)  # -1 means loop indefinitely

    running = True
    while running:
        screen.fill(WHITE)

        keys = pygame.key.get_pressed()
        street_speed = base_speed + (4 if keys[pygame.K_UP] else 0)

        street_y += street_speed  # Move down instead of up

        if street_y >= SCREEN_HEIGHT:
         street_y = 0

        screen.blit(street_img, (0, street_y))
        screen.blit(street_img, (0, street_y - SCREEN_HEIGHT))


        #street_y -= street_speed
        #if street_y <= -SCREEN_HEIGHT:
         #  street_y = 0

      #  screen.blit(street_img, (0, street_y))
       # screen.blit(street_img, (0, street_y + SCREEN_HEIGHT))

        now = time.time()

        if now - coin_timer >= 2:
            coins.add(Coin())
            coin_timer = now

        if now - enemy_timer >= 3:
            if level == 1:
                pass  # Only same-direction cars handled below
            elif level == 2:
                img = random.choice([same_dir_enemy_img, rock_img])
                enemies.add(Enemy(img, base_speed))
            elif level == 3:
                img = random.choice([enemy_img, rock_img])
                enemies.add(Enemy(img, street_speed ))
            enemy_timer = now

        if level >= 1 and now - same_dir_timer >= 5:
            same_direction_enemies.add(SameDirectionEnemy(same_dir_enemy_img))
            same_dir_timer = now
        coins.update()
        enemies.update()
        for e in same_direction_enemies:
            e.update(base_speed)

        coins.draw(screen)
        enemies.draw(screen)
        same_direction_enemies.draw(screen)

        player.update(keys)
        player_group.draw(screen)

        coin_collisions = pygame.sprite.spritecollide(player, coins, True)  # إزالة الكوين عند التصادم
        for coin in coin_collisions:
                score += 1 
                if coin_sound:
                    coin_sound.play()
        score_text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (10, 17))

        if check_collision(player, enemies) or check_collision(player, same_direction_enemies):
            if collision_sound:
                collision_sound.play()  # Play sound on collision
            pygame.mixer.music.stop()
            return game_over_screen()

        if start_time is None and keys[pygame.K_UP]:
            start_time = time.time()

        if start_time and now - start_time >= 60:
            if finishing_line_y < player.rect.top:
                finishing_line_y += 2
            else:
                finishing_line_reached = True
            screen.blit(finishing_line_img, (0, finishing_line_y))
            if finishing_line_reached:
                if victory_sound:
                    victory_sound.play()
                pygame.mixer.music.stop()      
                return level_complete_screen(level)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pause_screen()

        clock.tick(FPS)

def game_over_screen():

    while True:
        screen.blit(lose_img, (0, 0))
        pygame.display.flip()
        text2 =  large_font.render("Press SPACE to return to Start", True, WHITE)
        screen.blit(text2, (SCREEN_WIDTH // 2 - text2.get_width() // 2, SCREEN_HEIGHT // 2 + 100))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return start_screen()

        clock.tick(FPS)
   

def level_complete_screen(level):
    while True:
        screen.blit(win_img, (0, 0))
        pygame.display.flip()
        text2 =  large_font.render("Press SPACE to return to Start", True, WHITE)
        screen.blit(text2, (SCREEN_WIDTH // 2 - text2.get_width() // 2, SCREEN_HEIGHT // 2 + 120))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return start_screen()

        clock.tick(FPS)

    
# Start the game
start_screen()
