# Python Final Fantasy Style RPG Battle Beginner Tutorial in PyGame by Coding With Russ
# https://www.youtube.com/watch?v=Vlolidaoiak&list=PLjcN1EyupaQnvpv61iriF8Ax9dKra-MhZ

import pygame
import random

pygame.init()

clock = pygame.time.Clock()
fps = 60

# game window
bottom_panel = 150
screen_width = 800
screen_height = 400 + bottom_panel

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Battle')

current_fighter = 1
total_fighters = 3
action_cooldown = 0
action_wait_time = 90
attack = False
potion = False
potion_effect = 15
clicked = False
game_over = 0

font = pygame.font.SysFont('Arial', 26)

red = (255, 0, 0)
green = (0, 255, 0)

background_img = pygame.image.load('img/background/background.png').convert_alpha()
panel_img = pygame.image.load('img/Icons/panel.png').convert_alpha()
sword_img = pygame.image.load('img/Icons/sword.png').convert_alpha()
potion_img = pygame.image.load('img/Icons/potion.png').convert_alpha()
restart_img = pygame.image.load('img/Icons/restart.png').convert_alpha()
victory_img = pygame.image.load('img/Icons/victory.png').convert_alpha()
defeat_img = pygame.image.load('img/Icons/defeat.png').convert_alpha()


def draw_text(text, font, text_col, x, y):
    screen.blit(font.render(text, True, text_col), (x, y))


def draw_bg():
    screen.blit(background_img, (0, 0))


def draw_panel():
    screen.blit(panel_img, (0, screen_height - bottom_panel))
    draw_text(f'{knight.name} HP: {knight.hp}', font, red, 100, screen_height - bottom_panel + 10)
    for count, i in enumerate(bandit_list):
        draw_text(f'{i.name} HP: {i.hp}', font, red, 550, (screen_height - bottom_panel + 10) + count * 60)


class Button:
    def __init__(self, surface, x, y, image, size_x, size_y):
        self.image = pygame.transform.scale(image, (size_x, size_y))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False
        self.surface = surface

    def draw(self):
        action = False
        pos1 = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos1) and pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
            action = True
            self.clicked = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        self.surface.blit(self.image, (self.rect.x, self.rect.y))
        return action


class Fighter:
    def __init__(self, x, y, name, max_hp, strength, potions):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.strength = strength
        self.start_potions = potions
        self.potions = potions
        self.alive = True
        self.animation_list = []
        self.frame_index = 0
        self.action = 0  # 0:idle, 1:attack, 2:hurt, 3:dead
        self.update_time = pygame.time.get_ticks()
        temp_list = []
        for i in range(8):
            img = pygame.image.load(f'img/{self.name}/Idle/{i}.png')
            temp_list.append(pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3)))
        self.animation_list.append(temp_list)
        temp_list = []
        for i in range(8):
            img = pygame.image.load(f'img/{self.name}/Attack/{i}.png')
            temp_list.append(pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3)))
        self.animation_list.append(temp_list)
        temp_list = []
        for i in range(3):
            img = pygame.image.load(f'img/{self.name}/Hurt/{i}.png')
            temp_list.append(pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3)))
        self.animation_list.append(temp_list)
        temp_list = []
        for i in range(10):
            img = pygame.image.load(f'img/{self.name}/Death/{i}.png')
            temp_list.append(pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3)))
        self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        animation_cooldown = 100
        self.image = self.animation_list[self.action][self.frame_index]

        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.idle()

    def idle(self):
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

    def hurt(self):
        self.frame_index = 0
        self.action = 2
        self.update_time = pygame.time.get_ticks()

    def death(self):
        self.frame_index = 0
        self.action = 3
        self.update_time = pygame.time.get_ticks()

    def attack(self, target):
        damage = self.strength + random.randint(-5, 5)
        target.hp -= damage
        target.hurt()
        if target.hp < 1:
            target.hp = 0
            target.alive = False
            target.death()
        damage_text = DamageText(target.rect.centerx, target.rect.y, str(damage), red)
        damage_text_group.add(damage_text)

        self.action = 1
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def reset(self):
        self.alive = True
        self.potions = self.start_potions
        self.hp = self.max_hp
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()


    def draw(self):
        screen.blit(self.image, self.rect)


class HealthBar:
    def __init__(self, x, y, hp, max_hp):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = max_hp

    def draw(self, hp):
        self.hp = hp
        ratio = self.hp / self.max_hp
        pygame.draw.rect(screen, red, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, green, (self.x, self.y, 150 * ratio, 20))


class DamageText(pygame.sprite.Sprite):
    def __init__(self, x, y, damage, colour):
        pygame.sprite.Sprite.__init__(self)
        self.image = font.render(damage, True, colour)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        self.rect.y -= 1
        self.counter += 1
        if self.counter > 60:
            self.kill()


damage_text_group = pygame.sprite.Group()


knight = Fighter(200, 260, 'Knight', 30, 10, 3)

bandit_list = [
    Fighter(550, 270, 'Bandit', 20, 6, 1),
    Fighter(700, 270, 'Bandit', 20, 6, 1)
]

knight_health_bar = HealthBar(100, screen_height - bottom_panel + 40, knight.hp, knight.max_hp)
bandit0_health_bar = HealthBar(550, screen_height - bottom_panel + 40, bandit_list[0].hp, bandit_list[0].max_hp)
bandit1_health_bar = HealthBar(550, screen_height - bottom_panel + 40 + 60, bandit_list[1].hp, bandit_list[1].max_hp)

potion_button = Button(screen, 100, screen_height-bottom_panel+70, potion_img, 64, 64)
restart_button = Button(screen, 330, 120, restart_img, 120, 30)

run = True
while run:

    clock.tick(fps)

    draw_bg()
    draw_panel()
    knight_health_bar.draw(knight.hp)
    bandit0_health_bar.draw(bandit_list[0].hp)
    bandit1_health_bar.draw(bandit_list[1].hp)

    knight.update()
    knight.draw()

    for bandit in bandit_list:
        bandit.update()
        bandit.draw()

    damage_text_group.update()
    damage_text_group.draw(screen)

    # control player actions
    attack = False
    potion = False
    target = None

    is_mouse_visible = True
    pos = pygame.mouse.get_pos()
    for count, bandit in enumerate(bandit_list):
        if bandit.rect.collidepoint(pos):
            is_mouse_visible = False
            screen.blit(sword_img, pos)
            if clicked and bandit.alive:
                attack = True
                target = bandit_list[count]
    pygame.mouse.set_visible(is_mouse_visible)

    if potion_button.draw():
        potion = True
    draw_text(str(knight.potions), font, red, 150, screen_height - bottom_panel + 70)

    if game_over == 0:
        # player action
        if knight.alive:
            if current_fighter == 1:
                action_cooldown += 1
                if action_cooldown >= action_wait_time:
                    if target and attack:
                        knight.attack(target)
                        current_fighter += 1
                        action_cooldown = 0
                    if potion and knight.potions > 0:
                        if knight.max_hp - knight.hp > potion_effect:
                            heal_amount = potion_effect
                        else:
                            heal_amount = knight.max_hp - knight.hp
                        knight.hp += heal_amount
                        knight.potions -= 1
                        damage_text = DamageText(knight.rect.centerx, knight.rect.y, str(heal_amount), green)
                        damage_text_group.add(damage_text)
                        current_fighter += 1
                        action_cooldown = 0
        else:
            game_over = -1

        # enemy action
        for count, bandit in enumerate(bandit_list):
            if current_fighter == 2 + count:
                if bandit.alive:
                    action_cooldown += 1
                    if action_cooldown >= action_wait_time:
                        if (bandit.hp / bandit.max_hp) < 0.5 and bandit.potions > 0:
                            if bandit.max_hp - bandit.hp > potion_effect:
                                heal_amount = potion_effect
                            else:
                                heal_amount = bandit.max_hp - bandit.hp
                            bandit.hp += heal_amount
                            bandit.potions -= 1
                            damage_text = DamageText(bandit.rect.centerx, bandit.rect.y, str(heal_amount), green)
                            damage_text_group.add(damage_text)
                            current_fighter += 1
                            action_cooldown = 0
                        else:
                            bandit.attack(knight)
                            current_fighter += 1
                            action_cooldown = 0
                else:
                    current_fighter += 1

        # if all fighters have had a turn then reset
        if current_fighter > total_fighters:
            current_fighter = 1

    # check if all bandits are dead
    alive_bandits = 0
    for bandit in bandit_list:
        if bandit.alive:
            alive_bandits += 1
    if alive_bandits == 0:
        game_over = 1

    if game_over:
        if game_over == 1:
            screen.blit(victory_img, (250, 50))
        if game_over == -1:
            screen.blit(defeat_img, (290, 50))
        if restart_button.draw():
            knight.reset()
            for bandit in bandit_list:
                bandit.reset()
            current_fighter = 1
            action_cooldown = 0
            game_over = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            clicked = True
        else:
            clicked = False

    pygame.display.update()

pygame.quit()
