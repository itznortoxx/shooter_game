# ¡Crea tu propio juego de disparos!

from pygame import *
from random import randint, uniform
from time import time as tm

window = display.set_mode((700, 500))
display.set_caption("Juego de disparos")

background = transform.scale(image.load('galaxy_2.png'), (700,500))

ammo_icon = transform.scale(image.load('ammo_icon.png'), (45, 45))
time_icon = transform.scale(image.load('time_icon.png'), (60, 60))

init()

mixer.init()
mixer.music.load('space.ogg')
mixer.music.play()

fire_sfx = mixer.Sound('fire.ogg')
defeat_sfx = mixer.Sound('defeat.ogg')
victory_sfx = mixer.Sound('victory.mp3')
no_ammo_sfx = mixer.Sound('no_ammo.mp3')

font_one = font.SysFont('Arial', 23, True)
font_two = font.SysFont('Arial', 40, True)



FPS = 60
clock = time.Clock()

last_shoot = tm()
start_time = tm()
elapsed_time = 0

shoot_cooldown = 0.05
number_of_enemies = 5
number_of_asteroids = 3
missed_threshold = 20
winning_score = 10
reload_time = 3
max_time = 45
max_ammo = 50
ammo = max_ammo
ammo_shot_flag = 0
reload_start = 0
is_reloading = False
missed = 0
score = 0

background_y = 0

lower_enemy_speed = 1.5
upper_enemy_speed = 3.5

# clase padre para otros objetos
class GameSprite(sprite.Sprite):
    # constructor de clase
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        # llamamos al constructor de la clase (Sprite):
        sprite.Sprite.__init__(self)

        # cada objeto debe almacenar una propiedad image
        self.image = transform.scale(image.load(player_image), (size_x, size_y))
        self.speed = player_speed

        # cada objeto debe almacenar la propiedad rect en la cual está inscrito
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y

    # método que dibuja al personaje en la ventana
    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))


# clase del jugador principal
class Player(GameSprite):
    def update(self):
        keys_pressed = key.get_pressed()
        if keys_pressed[K_RIGHT] and self.rect.x < 629:
            self.rect.x += self.speed
        if keys_pressed[K_LEFT] and self.rect.x > 0:
            self.rect.x -= self.speed
        
    
    def fire(self):
        fire_sfx.play()
        bullet = createBullet()
        bullets.add(bullet)

class Enemy(GameSprite):
    def restart(self):
        global missed, lower_enemy_speed, upper_enemy_speed

        self.rect.y = randint(-80, -60)
        self.rect.x = randint(5, 572)
        self.speed = uniform(lower_enemy_speed, upper_enemy_speed)
        
    
    def update(self):
        global missed

        if self.rect.y >= 500:
            self.restart()
            missed += 1
        else:
            self.rect.y += self.speed

        collisions = sprite.spritecollide(player, enemies, False)

        if collisions:
            missed = missed_threshold

class Asteroid(GameSprite):
    def restart(self):
        self.rect.y = randint(-80, -60)
        self.rect.x = randint(5, 572)
        self.speed = uniform(lower_enemy_speed, upper_enemy_speed)

    def update(self):
        if self.rect.y >= 500:
            self.restart()
        else:
            self.rect.y += self.speed
        
        collisions = sprite.spritecollide(player, asteroids, False)

        if collisions:
            missed = missed_threshold

class Bullet(GameSprite):
    def update(self):
        global score, lower_enemy_speed, upper_enemy_speed

        if self.rect.y <= -80:
            bullets.remove(self)
            self.kill()
        else:
            self.rect.y -= self.speed
        
        enemy_collisions = sprite.groupcollide(bullets, enemies, True, False)
        
        if enemy_collisions:
            for bullet, ships in enemy_collisions.items():
                for enemy in ships:
                    enemy.restart()
                    score += 1
                    lower_enemy_speed += 0.15
                    upper_enemy_speed += 0.2
        
        asteroid_collisions = sprite.groupcollide(bullets, asteroids, True, False)
        
        self.reset()

def createBullet():
    bullet = Bullet('bullet.png', player.rect.x+24, player.rect.y - 30, 20, 50, 8)
    return bullet

game = True
finished = False
played = False

player = Player('rocket.png', 0, 400, 68, 100, 8)
enemies = sprite.Group()
bullets = sprite.Group()
asteroids = sprite.Group()


for i in range(number_of_enemies):
    enemy = Enemy('ufo.png', randint(0, 572), 0, 128, 65, randint(2, 3))
    enemies.add(enemy)

for i in range(number_of_asteroids):
    asteroid = Asteroid('asteroid.png', randint(0, 572), -100, 70, 70, randint(2, 3))
    asteroids.add(asteroid)


while game:
    if missed < missed_threshold and score < winning_score and elapsed_time < max_time:
        window.blit(background, (0,background_y))
        window.blit(background, (0,background_y-500))

        if background_y > 500:
            background_y = 0
        else:
            background_y += 1
        
        
        elapsed_time = tm() - start_time
        
        for e in event.get():
            if e.type == QUIT:
                game = False

            if ammo_shot_flag >= 5 and not is_reloading:
                reload_start = tm()
                is_reloading = True
            
            if is_reloading:
                reloading_message = font_one.render(f'Recargando...', True, (255, 30, 30))
                reloading_message_rect = reloading_message.get_rect()
                window.blit(reloading_message, ((700-reloading_message_rect.width)/2,410))
                
                if tm() - reload_start >= reload_time:
                    ammo_shot_flag = 0
                    is_reloading = False
                        
            if e.type == KEYDOWN:
                if e.key == K_SPACE:
                    if tm() - last_shoot >= shoot_cooldown:
                        if ammo > 0 and not is_reloading:
                            fire_sfx.play()
                            player.fire()
                            last_shoot = tm()
                            ammo_shot_flag += 1
                            ammo -= 1
                        else:
                            no_ammo_sfx.play()
        
        player.update()

        keys_pressed = key.get_pressed()
            

        enemies.draw(window)
        enemies.update()

        asteroids.draw(window)
        asteroids.update()
        
        bullets.update()  
        
        
        player.reset()

        clock.tick(FPS)

        window.blit(ammo_icon, (550, 430))
        window.blit(time_icon, (540, 30))

        missed_text = font_one.render(f'Fallos: {missed} / {missed_threshold}', True, (255, 255, 255))
        score_text = font_one.render(f'Puntos: {score} / {winning_score}', True, (255, 255, 255))
        ammo_text = font_two.render(f'{ammo}', True, (255, 255, 255))
        remaining_time_text = font_two.render(f'{int(round(max_time - elapsed_time, 0))}', True, (255, 255, 255))
        
        window.blit(missed_text, (38,30))
        window.blit(score_text, (38, 60))
        window.blit(ammo_text, (615, 430))
        window.blit(remaining_time_text, (615, 35))

        display.update()
    else:
        if missed >= missed_threshold or elapsed_time > max_time:
            window.fill((255, 0, 0))
            
            defeat_message = font_two.render(f'HAS PERDIDO', True, (255, 255, 255))
            defeat_message_rect = defeat_message.get_rect()

            defeat_score_text = font_one.render(f'Puntaje: {score}/{winning_score} ({round(score*100/winning_score,0)}%)', True, (255, 255, 255))
            defeat_score_text_rect = defeat_score_text.get_rect()

            window.blit(defeat_message, ((700-defeat_message_rect.width)/2,230))
            window.blit(defeat_score_text, ((700-defeat_score_text_rect.width)/2,280))

            mixer.music.stop()
            if not played:
                defeat_sfx.play()
                played = True

            for e in event.get():
                if e.type == QUIT:
                    game = False

            clock.tick(FPS)
            display.update()
        else:
            window.fill((100, 200, 30))

            
            
            victory_message = font_two.render(f'¡VICTORIA!', True, (255, 255, 255))
            victory_message_rect = victory_message.get_rect()

            victory_score_text = font_one.render(f'Puntaje: {score} - Fallos: {missed}', True, (255, 255, 255))
            victory_score_text_rect = victory_score_text.get_rect()

            
            
            window.blit(victory_message, ((700-victory_message_rect.width)/2,190))
            window.blit(victory_score_text, ((700-victory_score_text_rect.width)/2,240))
            

            mixer.music.stop()
            if not played:
                victory_sfx.play()
                end_time = tm()
                play_time = end_time - start_time
                played = True
            
            victory_time_text = font_one.render(f'Tiempo restante: {round(max_time-play_time,2)}s', True, (255, 255, 255))
            victory_time_text_rect = victory_time_text.get_rect()

            window.blit(victory_time_text, ((700-victory_time_text_rect.width)/2,265))

            for e in event.get():
                if e.type == QUIT:
                    game = False

            clock.tick(FPS)
            display.update()