import pygame, random, math, numpy, os, sys

class Player:
    def __init__(self, pos, size, speed, color, bullet_size, bullet_speed, health, damage, game):
        self.rect = pygame.Rect(pos, size)
        self.color = color
        self.health = health
        self.damage = damage
        self.speed = speed
        self.game = game
        self.bullet_size = bullet_size
        self.bullet_speed = bullet_speed

        self.left = False
        self.right = False
        self.up = False
        self.down = False

        self.next_damage = 0
        self.damage_cooldown = 1500
        
        self.next_shot = 0
        self.shot_cooldown = 500

        self.shoot_left = False
        self.shoot_right = False
        self.shoot_up = False
        self.shoot_down = False

        self.dead = False


    def update(self):
        if self.left and self.rect.x > 0: 
            self.rect.x -= self.speed
        if self.right and self.rect.x + self.rect.w  < self.game.WINDOW_SIZE[0]:
            self.rect.x += self.speed
        if self.up and self.rect.y > 150:
            self.rect.y -= self.speed
        if self.down and self.rect.y + self.rect.h < self.game.WINDOW_SIZE[1]:
            self.rect.y += self.speed
        
        if (self.shoot_left or self.shoot_right or self.shoot_down or self.shoot_up) and pygame.time.get_ticks() > self.next_shot:
            self.next_shot = pygame.time.get_ticks() + self.shot_cooldown
            center = (self.rect.x + (self.rect.w/2), self.rect.y + (self.rect.h/2))
             
            self.game.shot_sfx.play()
            if self.shoot_left:
                self.game.player_bullets.append([pygame.Vector2(center[0], center[1]), (-1 * self.bullet_speed, 0)])

            elif self.shoot_right:
                self.game.player_bullets.append([pygame.Vector2(center[0], center[1]), (1 * self.bullet_speed, 0)])

            elif self.shoot_down:
                self.game.player_bullets.append([pygame.Vector2(center[0], center[1]), (0, 1 * self.bullet_speed)])

            elif self.shoot_up:
                self.game.player_bullets.append([pygame.Vector2(center[0], center[1]), (0, -1 * self.bullet_speed)])


    def draw(self, display):
        pygame.draw.rect(display, self.color, self.rect)

    def take_damage(self, dmg):
        if pygame.time.get_ticks() > self.next_damage:
            self.health -= dmg
            self.game.hurt_sfx.play()
            self.next_damage = pygame.time.get_ticks() + self.damage_cooldown

            for i in range(15):
                health_bar_size = (self.game.health_bar_size[0] * self.health/100, self.game.health_bar_size[1])
                self.game.particles.append([pygame.Vector2(self.game.health_bar_pos[0] + health_bar_size[0], self.game.health_bar_pos[1] + (self.game.health_bar_size[1]/2)), (50, 255, 50)])

            if self.health <= 0:
                for i in range(50):
                    self.game.particles.append([pygame.Vector2(self.rect.x + (self.rect.w/2), self.rect.y + (self.rect.h/2)), (self.color[0] - int(self.color[0] * .2), self.color[1] - int(self.color[1] * .2), self.color[2] - int(self.color[2] * .2))])
                self.game.death_sfx.play()
                self.dead = True

                with open("data.txt") as f:
                    contents = f.read()
                    self.game.player_high_score = int(contents)

                if self.game.player_high_score < self.game.wave_counter:
                    with open("data.txt", "w") as f:
                        f.write(str(self.game.wave_counter))
                    self.game.player_high_score = self.game.wave_counter
 

            elif self.health >= 0:
                for i in range(10):
                    self.game.particles.append([pygame.Vector2(self.rect.x + (self.rect.w/2), self.rect.y + (self.rect.h/2)), (self.color[0] - int(self.color[0] * .2), self.color[1] - int(self.color[1] * .2), self.color[2] - int(self.color[2] * .2))])


class Enemy:
    def __init__(self, pos, size, speed, color, bullet_size, bullet_speed, shot_cooldown, health, damage, game, follow=False, wander=True, shooter=False):
        self.rect = pygame.Rect(pos, size)
        self.velocity = pygame.Vector2(0, 0)
        self.speed = speed
        self.game = game
        self.color = color
        self.velocity = pygame.Vector2(0, 0)

        self.shooter = shooter
        self.next_shot = random.uniform(0, 10000)
        self.shot_cooldown = shot_cooldown
        self.bullet_size = bullet_size
        self.bullet_speed = bullet_speed

        self.health = health
        self.damage = damage

        self.follow = follow

        self.wander = wander
        self.next_wander = random.uniform(0, 1000)
        self.wander_interval = random.uniform(1500, 2000)
        
        self.left = False
        self.right = False
        self.down = False
        self.up = False

        self.dead = False

    
    def update(self):
        if self.rect.colliderect(self.game.player.rect):
            self.game.player.take_damage(self.damage)
        
        if not self.follow and self.wander:
            if pygame.time.get_ticks() > self.next_wander:
                self.left = False
                self.right = False
                self.down = False
                self.up = False

                self.next_wander = pygame.time.get_ticks() + self.wander_interval
                direction = random.randint(1, 4)

                if direction == 1:
                    self.left = True
                elif direction == 2:
                    self.right = True
                elif direction == 3:
                    self.up = True
                elif direction == 4:
                    self.down = True

            if self.rect.x <= 0:
                self.left = False
                self.up = False
                self.down = False
                self.right = True
            if self.rect.x + self.rect.w >= self.game.WINDOW_SIZE[0]:
                self.right = False
                self.up = False
                self.down = False
                self.left = True
            if self.rect.y <= 150:
                self.left = False
                self.right = False
                self.up = False
                self.down = True
            if self.rect.y + self.rect.h >= self.game.WINDOW_SIZE[1]: 
                self.left = False
                self.right = False
                self.down = False
                self.up = True

            if self.left and self.rect.x > 0: 
                self.velocity.x = -self.speed
            if self.right and self.rect.x + self.rect.w  < self.game.WINDOW_SIZE[0]:
                self.velocity.x = self.speed
            if self.up and self.rect.y > 150:
                self.velocity.y = -self.speed
            if self.down and self.rect.y + self.rect.h < self.game.WINDOW_SIZE[1]:
                self.velocity.y = self.speed

        elif self.follow:
            x, y = self.get_player_pos()
            self.velocity.x = x * self.speed
            self.velocity.y = y * self.speed

        if self.shooter and pygame.time.get_ticks() > self.next_shot:
            self.next_shot = pygame.time.get_ticks() + self.shot_cooldown
            self.shoot()
            self.game.shot_sfx.play()

        self.rect.x += self.velocity.x
        enemy_rects = []
        for enemy in self.game.enemies:
            if enemy != self:
                enemy_rects.append(enemy.rect)
        collisions = self.rect.collidelistall(enemy_rects)
        for enemy_rect in collisions:
            if self.velocity.x > 0:
                self.rect.right = enemy_rects[enemy_rect].left
            elif self.velocity.x < 0:
                self.rect.left = enemy_rects[enemy_rect].right

        self.rect.y += self.velocity.y
        enemy_rects = []
        for enemy in self.game.enemies:
            if enemy != self:
                enemy_rects.append(enemy.rect)
        collisions = self.rect.collidelistall(enemy_rects)
        for enemy_rect in collisions:
            if self.velocity.y > 0:
                self.rect.bottom = enemy_rects[enemy_rect].top
            elif self.velocity.y < 0:
                self.rect.top = enemy_rects[enemy_rect].bottom

    def shoot(self):
        pass


    def get_player_pos(self):
        player_pos = pygame.Vector2(self.game.player.rect.x + (self.game.player.rect.w/2), self.game.player.rect.y + (self.game.player.rect.h/2))
        pos = pygame.Vector2(self.rect.x + (self.rect.w/2), self.rect.y + (self.rect.h/2))

        x = player_pos.x - pos.x 
        y = player_pos.y - pos.y
        length = math.sqrt((x**2) + (y**2))
        if length != 0:
            x /= length
            y /= length
        else:
            x = 0
            y = 0

        return x, y

    
    def draw(self, display):
        pygame.draw.rect(display, self.color, self.rect)

    def die(self):
        for i in range(50):
            self.game.particles.append([pygame.Vector2(self.rect.x + (self.rect.w/2), self.rect.y + (self.rect.h/2)), (self.color[0] - int(self.color[0] * .2), self.color[1] - int(self.color[1] * .2), self.color[2] - int(self.color[2] * .2))])
        self.game.enemies.remove(self)


    def take_damage(self, dmg):
        self.health -= dmg
        self.game.hit_sfx.play()

        if self.health <= 0:
            self.game.death_sfx.play()
            self.die()

        elif self.health >= 0:
            for i in range(10):
                self.game.particles.append([pygame.Vector2(self.rect.x + (self.rect.w/2), self.rect.y + (self.rect.h/2)), (self.color[0] - int(self.color[0] * .2), self.color[1] - int(self.color[1] * .2), self.color[2] - int(self.color[2] * .2))])



class Giant(Enemy):
    def shoot(self):
        self.game.boulder_sfx.play()
        bullet_speed = self.bullet_speed
        xd, yd = (abs(self.game.player.rect.x - self.rect.x), abs(self.game.player.rect.y - self.rect.y))
        center = (self.rect.x + (self.rect.w/2), self.rect.y + (self.rect.h/2))

        if xd > yd:
            if self.game.player.rect.x > self.rect.x:
                self.game.enemy_bullets.append([pygame.Vector2(center[0], center[1]), (1 * self.bullet_speed, bullet_speed), self.damage, self.bullet_size])
                self.game.enemy_bullets.append([pygame.Vector2(center[0], center[1]), (1 * self.bullet_speed, 0), self.damage, self.bullet_size])
                self.game.enemy_bullets.append([pygame.Vector2(center[0], center[1]), (1 * self.bullet_speed, -bullet_speed), self.damage, self.bullet_size])
            else:
                self.game.enemy_bullets.append([pygame.Vector2(center[0], center[1]), (-1 * self.bullet_speed, bullet_speed), self.damage, self.bullet_size])
                self.game.enemy_bullets.append([pygame.Vector2(center[0], center[1]), (-1 * self.bullet_speed, 0), self.damage, self.bullet_size])
                self.game.enemy_bullets.append([pygame.Vector2(center[0], center[1]), (-1 * self.bullet_speed, -bullet_speed), self.damage, self.bullet_size])
        elif xd < yd:
            if self.game.player.rect.y > self.rect.y:
                self.game.enemy_bullets.append([pygame.Vector2(center[0], center[1]), (bullet_speed, 1 * self.bullet_speed), self.damage, self.bullet_size])
                self.game.enemy_bullets.append([pygame.Vector2(center[0], center[1]), (0, 1 * self.bullet_speed), self.damage, self.bullet_size])
                self.game.enemy_bullets.append([pygame.Vector2(center[0], center[1]), (-bullet_speed, 1 * self.bullet_speed), self.damage, self.bullet_size])
            else:
                self.game.enemy_bullets.append([pygame.Vector2(center[0], center[1]), (bullet_speed, -1 * self.bullet_speed), self.damage, self.bullet_size])
                self.game.enemy_bullets.append([pygame.Vector2(center[0], center[1]), (0, -1 * self.bullet_speed), self.damage, self.bullet_size])
                self.game.enemy_bullets.append([pygame.Vector2(center[0], center[1]), (-bullet_speed, -1 * self.bullet_speed), self.damage, self.bullet_size])
        else:
            self.next_shot = pygame.time.get_ticks()



class Baby(Enemy):
    def shoot(self):
        center = (self.rect.x + (self.rect.w/2), self.rect.y + (self.rect.h/2))

        if self.velocity.x > 0:
            self.game.enemy_bullets.append([pygame.Vector2(center[0], center[1]), (self.bullet_speed, 0), self.damage, self.bullet_size])
        elif self.velocity.x < 0:
            self.game.enemy_bullets.append([pygame.Vector2(center[0], center[1]), (-self.bullet_speed, 0), self.damage, self.bullet_size])

class Goblin(Enemy):
    def shoot(self):
        center = (self.rect.x + (self.rect.w/2), self.rect.y + (self.rect.h/2))

        self.game.enemy_bullets.append([pygame.Vector2(center[0], center[1]), (self.bullet_speed, 0), self.damage, self.bullet_size])
        self.game.enemy_bullets.append([pygame.Vector2(center[0], center[1]), (0, self.bullet_speed), self.damage, self.bullet_size])
        self.game.enemy_bullets.append([pygame.Vector2(center[0], center[1]), (0, -self.bullet_speed), self.damage, self.bullet_size])
        self.game.enemy_bullets.append([pygame.Vector2(center[0], center[1]), (-self.bullet_speed, 0), self.damage, self.bullet_size])


class Boomer(Enemy):
    def die(self):
        super().die()

        self.game.enemies.append(Enemy(pygame.Vector2(self.rect.x, self.rect.y), (30, 20), 4.5, (random.randint(120, 255), 0, 0), 10, 5, 5000, 10, 10, self.game, True, False, False))
        self.game.enemies.append(Enemy(pygame.Vector2(self.rect.x, self.rect.y), (30, 20), 4.5, (random.randint(120, 255), 0, 0), 10, 5, 5000, 10, 10, self.game, True, False, False))

class Mushroom(Enemy):
    def __init__(self, pos, size, speed, color, bullet_size, bullet_speed, shot_cooldown, health, damage, game, follow=False, wander=True, shooter=False):
        super().__init__(pos, (0, 0), speed, color, bullet_size, bullet_speed, shot_cooldown, health, damage, game, follow, wander, shooter)
        self.real_size = size
        self.appear_next = 0
        self.appear_cooldown = 3000
        self.appearing = False
        self.played_sfx = False

    def update(self):
        super().update()
        if pygame.time.get_ticks() >= self.appear_next and not self.appearing:
            if not self.played_sfx:
                self.game.mushroom_grow_sfx.play()
                self.played_sfx = True
            self.rect.w += 1
            self.rect.h += 1
            if self.rect.w >= self.real_size[0]:
                self.played_sfx = False
                self.shoot() 
                self.appear_next = pygame.time.get_ticks() + self.appear_cooldown
                self.appearing = True

        elif pygame.time.get_ticks() >= self.appear_next and self.appearing:
            self.rect.w -= 1
            self.rect.h -= 1
            if self.rect.w <= 0:
                self.rect.x = random.randint(0, self.game.WINDOW_SIZE[0])
                self.rect.y = random.randint(0, self.game.WINDOW_SIZE[1])
                self.appearing = False
                self.appear_next = pygame.time.get_ticks() + self.appear_cooldown

    def shoot(self):
        center = (self.rect.x + (self.rect.w/2), self.rect.y + (self.rect.h/2))
        x, y = self.get_player_pos()

        self.game.enemy_bullets.append([pygame.Vector2(center[0], center[1]), (x * self.bullet_speed, y * self.bullet_speed), self.damage, self.bullet_size])


class Bomber(Enemy):
    def __init__(self, pos, size, speed, color, bullet_size, bullet_speed, shot_cooldown, health, damage, game, follow=False, wander=True, shooter=False):
        super().__init__(pos, size, speed, color, bullet_size, bullet_speed, shot_cooldown, health, damage, game, follow, wander, shooter)
        self.bomb = None

    def update(self):
        super().update()

        if self.bomb is not None:
            if self.bomb[1].x != 0 and self.bomb[1].y != 0:
                self.bomb[0].x += self.bomb[1].x
                self.bomb[0].y += self.bomb[1].y

                self.bomb[1].x -= math.copysign(1, self.bomb[1].x) * .1
                self.bomb[1].y -= math.copysign(1, self.bomb[1].y) * .1

                if self.bomb[2].x > 0:
                    if self.bomb[1].x <= 0:
                        self.bomb[1].x = 0
                elif self.bomb[2].x <= 0:
                    if self.bomb[1].x >= 0:
                        self.bomb[1].x = 0   

                if self.bomb[2].y > 0:
                    if self.bomb[1].y <= 0:
                        self.bomb[1].y = 0
                elif self.bomb[2].x <= 0:
                    if self.bomb[1].y >= 0:
                        self.bomb[1].y = 0   


    def draw(self, display):
        super().draw(display)
        if self.bomb is not None:
            pygame.draw.circle(display, (255, 255, 255), self.bomb[0], self.bullet_size)

    def shoot(self):
        center = (self.rect.x + (self.rect.w/2), self.rect.y + (self.rect.h/2))
        x, y = self.get_player_pos()

        if self.bomb is not None:
            explosion_size = self.bullet_size * 10
            self.game.explosion_sfx.play()
            if pygame.Rect((self.bomb[0].x - (explosion_size/2), self.bomb[0].y - (explosion_size/2)), (explosion_size, explosion_size)).colliderect(self.game.player.rect):
                self.game.player.take_damage(self.damage)
            for i in range(100):
                self.game.particles.append([pygame.Vector2(self.bomb[0].x, self.bomb[0].y), (random.choice([(255, 165, 0), (255, 0, 0), (184, 15, 10)]))])

        self.bomb = [pygame.Vector2(center[0], center[1]), pygame.Vector2(x * self.bullet_speed, y * self.bullet_speed), pygame.Vector2(x * self.bullet_speed, y * self.bullet_speed)]

class Game:
    def __init__(self, WINDOW_SIZE, title):
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()
        pygame.font.init()
        pygame.mixer.init()

        self.boulder_sfx = pygame.mixer.Sound(r"sfx/boulder.wav")
        self.death_sfx = pygame.mixer.Sound(r"sfx/death.wav")
        self.dice_rattle_sfx = pygame.mixer.Sound(r"sfx/dice_rattle.wav")
        self.dice_roll_sfx = pygame.mixer.Sound(r"sfx/dice_roll.wav")
        self.explosion_sfx = pygame.mixer.Sound(r"sfx/explosion.wav")
        self.hit_sfx = pygame.mixer.Sound(r"sfx/hit.wav")
        self.hurt_sfx = pygame.mixer.Sound(r"sfx/hurt.wav")
        self.mushroom_grow_sfx = pygame.mixer.Sound(r"sfx/mushroom_grow.wav")
        self.shot_sfx = pygame.mixer.Sound(r"sfx/shot.wav")
        self.spawn_sfx = pygame.mixer.Sound(r"sfx/spawn.wav")
        self.soundtrack = pygame.mixer.Sound(r"soundtrack.wav")

        self.clock = pygame.time.Clock()

        self.dice_font = pygame.font.Font(r"dogica.ttf", 80)
        self.wave_font = pygame.font.Font(r"dogica.ttf", 25)

        self.WINDOW_SIZE = WINDOW_SIZE
        self.display = pygame.display.set_mode(self.WINDOW_SIZE)
        pygame.display.set_caption(title)

        self.enemy_count = 3
        self.enemies_to_spawn = self.enemy_count
        self.wave_counter = 0
        self.ongoing_wave = False
        self.next_spawn = 0
        self.spawn_interval = 10000

        self.player_bullets = []
        self.enemy_bullets = []
        self.player = Player(pygame.Vector2(400, 400), (40, 40), 5, (100, 150, 255), 8, 10, 100, 10, self)
        self.enemies = []

        self.particles = []

        self.roll_dice = False
        self.roll_dice_enemy_type = 2
        self.next_dice_roll = 0
        self.dice_roll_length = 3000
        self.show_results = False
        self.dice_panel_size = (600, 600)
        self.dice_panel_pos = (self.WINDOW_SIZE[0]/2 - (self.dice_panel_size[0]/2), self.WINDOW_SIZE[1]/2 - (self.dice_panel_size[1]/2))
        self.choices = None
        self.result = None
        self.multiplier = 0
        self.enemy_types = []
        self.dice_roll([1, 1.1, 1.2, 1.3, 1.4, 1.5])


        self.health_bar_size = (750, 60)
        self.health_bar_pos = (self.WINDOW_SIZE[0]/2 - (self.health_bar_size[0]/2), 20)

        self.player_high_score = 0
        with open("data.txt") as f:
            contents = f.read()
            self.player_high_score = int(contents)

        self.soundtrack.play(-1)

    def next_wave(self):
        self.wave_counter += 1
        self.enemy_count *= self.multiplier
        self.enemy_count = int(self.enemy_count)
        self.player.health = 100

        if self.enemy_count % 2 != 0:
            self.enemy_count += 1

        self.ongoing_wave = True
        self.enemies_to_spawn = self.enemy_count
        if self.spawn_interval > 6:
            self.spawn_interval /= 1.01


    def dice_roll(self, choices):
        self.roll_dice = True
        self.show_results = False
        self.next_dice_roll = pygame.time.get_ticks() + self.dice_roll_length
        self.choices = choices
        self.result = random.choice(choices)
        self.dice_rattle_sfx.play(-1)

    def render(self):
        self.display.fill((0, 0, 0))

        for enemy in self.enemies:
            enemy.draw(self.display)
        if not self.player.dead:
            self.player.draw(self.display)

        for bullet in self.player_bullets:
            pygame.draw.circle(self.display, (255, 255, 255), bullet[0], self.player.bullet_size)

        for bullet in self.enemy_bullets:
            pygame.draw.circle(self.display, (255, 255, 255), bullet[0], bullet[3])

        for particle in self.particles:
            pygame.draw.circle(self.display, particle[1], particle[0], 5, 3)
        
        health_bar_size = (self.health_bar_size[0] * self.player.health/100, self.health_bar_size[1])
        pygame.draw.rect(self.display, (50, 255, 50), pygame.Rect(self.health_bar_pos, health_bar_size))
        pygame.draw.rect(self.display, (255, 255, 255), pygame.Rect(self.health_bar_pos, self.health_bar_size), 5)
        pygame.draw.rect(self.display, (255, 255, 255), pygame.Rect((0, 135), (self.WINDOW_SIZE[0], 10)))

        pos = (30, 100)
        self.display.blit(self.wave_font.render("WAVE: " + str(self.wave_counter) + "  HIGH SCORE: " + str(self.player_high_score), True, (255, 255, 255)), pos)

        if self.roll_dice:
            pygame.draw.rect(self.display, (0, 0, 0), pygame.Rect(self.dice_panel_pos, self.dice_panel_size))
            pygame.draw.rect(self.display, (255, 255, 255), pygame.Rect(self.dice_panel_pos, self.dice_panel_size), 10)
            if not self.show_results:
                random_choice = self.choices[random.randint(0, len(self.choices) - 1)]
                size = self.dice_font.size(str(random_choice))
                pos = (self.WINDOW_SIZE[0]/2 - (size[0]/2), self.WINDOW_SIZE[1]/2 - (size[1]/2))
                self.display.blit(self.dice_font.render(str(random_choice), True, (255, 255, 255)), pos)
            else:
                size = self.dice_font.size(str(self.result))
                pos = (self.WINDOW_SIZE[0]/2 - (size[0]/2), self.WINDOW_SIZE[1]/2 - (size[1]/2))
                self.display.blit(self.dice_font.render(str(self.result), True, (255, 255, 255)), pos)


            if pygame.time.get_ticks() >= self.next_dice_roll:
                if self.show_results:
                    self.roll_dice = False
                    self.show_results = False

                    if self.roll_dice_enemy_type == 0:
                        self.next_wave()

                    if self.roll_dice_enemy_type > 0:
                        self.dice_roll([1, 2, 3, 4, 5, 6])
                        self.enemy_types.append(self.result)
                        self.roll_dice_enemy_type -= 1
                    
                else:
                    if self.roll_dice_enemy_type == 2:
                        self.multiplier = self.result

                    self.show_results = True
                    self.next_dice_roll = pygame.time.get_ticks() + self.dice_roll_length
                    self.dice_rattle_sfx.stop()
                    self.dice_roll_sfx.play()


        pygame.display.update()


    def event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                elif event.key == pygame.K_w:
                    self.player.up = True

                elif event.key == pygame.K_s:
                    self.player.down = True

                elif event.key == pygame.K_a:
                    self.player.left = True

                elif event.key == pygame.K_d:
                    self.player.right = True

                elif event.key == pygame.K_j:
                    self.player.shoot_left = True
                
                elif event.key == pygame.K_l:
                    self.player.shoot_right = True

                elif event.key == pygame.K_i:
                    self.player.shoot_up = True

                elif event.key == pygame.K_k:
                    self.player.shoot_down = True

                elif event.key == pygame.K_TAB:
                    print(self.enemy_count)
                
                elif event.key == pygame.K_SPACE and self.player.dead:
                    self.enemy_count = 3
                    self.enemies_to_spawn = self.enemy_count
                    self.wave_counter = 0
                    self.ongoing_wave = False
                    self.next_spawn = 0
                    self.spawn_interval = 10000

                    self.player_bullets = []
                    self.enemy_bullets = []
                    self.player = Player(pygame.Vector2(400, 400), (40, 40), 5, (100, 150, 255), 8, 10, 100, 10, self)
                    self.enemies = []

                    self.particles = []

                    self.roll_dice = False
                    self.roll_dice_enemy_type = 2
                    self.next_dice_roll = 0
                    self.dice_roll_length = 3000
                    self.show_results = False
                    self.dice_panel_size = (600, 600)
                    self.dice_panel_pos = (self.WINDOW_SIZE[0]/2 - (self.dice_panel_size[0]/2), self.WINDOW_SIZE[1]/2 - (self.dice_panel_size[1]/2))
                    self.choices = None
                    self.result = None
                    self.multiplier = 0
                    self.enemy_types = []
                    self.dice_roll([1, 1.1, 1.2, 1.3, 1.4, 1.5])

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    self.player.up = False

                elif event.key == pygame.K_s:
                    self.player.down = False

                elif event.key == pygame.K_a:
                    self.player.left = False

                elif event.key == pygame.K_d:
                    self.player.right = False

                elif event.key == pygame.K_j:
                    self.player.shoot_left = False
                
                elif event.key == pygame.K_l:
                    self.player.shoot_right = False

                elif event.key == pygame.K_i:
                    self.player.shoot_up = False

                elif event.key == pygame.K_k:
                    self.player.shoot_down = False

    def update(self):
        if self.ongoing_wave and pygame.time.get_ticks() >= self.next_spawn and self.enemies_to_spawn > 0:
            for i in range(random.randint(2, 3)):
                e_type = random.choice(self.enemy_types)
                color = random.randint(120, 255)
                if e_type == 1:
                    self.enemies.append(Boomer(pygame.Vector2(random.randint(0, 800), random.randint(0, 800)), (50, 50), 2, (color, 0, 0), 15, 4, 2000, 80, 20, self, False, True, False))
                elif e_type == 2:
                    self.enemies.append(Giant(pygame.Vector2(random.randint(0, 800), random.randint(0, 800)), (50, 50), 2, (color, color, 0), 25, 3, 5000, 60, 20, self, True, False, True))
                elif e_type == 3:
                    self.enemies.append(Goblin(pygame.Vector2(random.randint(0, 800), random.randint(0, 800)), (30, 40), 3.25, (0, color, 0), 15, 4, 2000, 40, 10, self, True, False, True))
                elif e_type == 4:
                    self.enemies.append(Baby(pygame.Vector2(random.randint(0, 800), random.randint(0, 800)), (20, 30), 3.5, (0, color, color), 10, 6, 5000, 20, 5, self, False, True, True))
                elif e_type == 5:
                    self.enemies.append(Mushroom(pygame.Vector2(random.randint(0, 800), random.randint(0, 800)), (40, 40), 3.5, (color, 0, color), 10, 12.5, 5000, 50, 10, self, False, False, False))
                elif e_type == 6:
                    self.enemies.append(Bomber(pygame.Vector2(random.randint(0, 800), random.randint(0, 800)), (40, 40), 2, (color, color, color), 20, 10, random.randint(5000, 7000), 50, 10, self, False, True, True))

                self.enemies_to_spawn -= 1
                self.spawn_sfx.play()
            self.next_spawn = pygame.time.get_ticks() + self.spawn_interval

        if self.ongoing_wave and self.enemies_to_spawn <= 0 and len(self.enemies) <= 0:
            self.roll_dice_enemy_type = 2
            self.show_results = False
            self.choices = None
            self.result = None
            self.multiplier = 0
            self.enemy_types = []
            self.dice_roll([1, 1.1, 1.2, 1.3, 1.4, 1.4])
            self.ongoing_wave = False

        if not self.player.dead:
            self.player.update()

        for bullet in self.player_bullets:
            if bullet[0].x > self.WINDOW_SIZE[0] or bullet[0].x < 0 or bullet[0].y < 0 or bullet[0].y > self.WINDOW_SIZE[1]:
                self.player_bullets.remove(bullet)
                continue
            
            collided_enemy = pygame.Rect(bullet[0].x - self.player.bullet_size, bullet[0].y - self.player.bullet_size, self.player.bullet_size * 2, self.player.bullet_size * 2).collidelist(self.enemies)
            if collided_enemy != -1:
                self.enemies[collided_enemy].take_damage(self.player.damage)
                self.player_bullets.remove(bullet)
                continue

            bullet[0].x += bullet[1][0]
            bullet[0].y += bullet[1][1]
        
        for bullet in self.enemy_bullets:
            if bullet[0].x > self.WINDOW_SIZE[0] or bullet[0].x < 0 or bullet[0].y < 0 or bullet[0].y > self.WINDOW_SIZE[1]:
                self.enemy_bullets.remove(bullet)
                continue
            
            if pygame.Rect(bullet[0].x - self.player.bullet_size, bullet[0].y - self.player.bullet_size, self.player.bullet_size * 2, self.player.bullet_size * 2).colliderect(self.player.rect):
                if pygame.time.get_ticks() >= self.player.next_damage:
                    self.player.take_damage(bullet[2])
                    self.enemy_bullets.remove(bullet)
                    continue
            
            bullet[0].x += bullet[1][0]
            bullet[0].y += bullet[1][1]


        for particle in self.particles:
            if particle[0].x > self.WINDOW_SIZE[0] or particle[0].x < 0 or particle[0].y < 0 or particle[0].y > self.WINDOW_SIZE[1]:
                self.particles.remove(particle)

            if len(particle) <= 2:
                particle.append(pygame.Vector2(random.uniform(-3, 3), random.uniform(-3, -1)))

            particle[2].y += .2
            particle[0].x += particle[2].x
            particle[0].y += particle[2].y

        for enemy in self.enemies:
            enemy.update()


    def run(self):
        self.event_handler()
        self.update()
        self.render()
        self.clock.tick(60)


if __name__ == '__main__':
    game = Game((800, 800), "Fate of the Dice")
    while True:
        game.run()
