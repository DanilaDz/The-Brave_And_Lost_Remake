import pygame
import math
import sys
import random

fps = pygame.time.Clock()

pygame.init()

pygame.display.set_caption('The Brave and Lost')
icon = pygame.image.load("game_images/game_icon.png")
icon.set_colorkey((0, 0, 0))
pygame.display.set_icon(icon)

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
display = pygame.Surface((300, 200))
surface = pygame.Surface((1200, 800))
# ==================Loading every image and variable needed===================== #
background = pygame.image.load("game_images/TBALbackground.png")
night_background = pygame.image.load("game_images/TBALnightbackground.png")
settings_icon = pygame.image.load('game_images/setting_icon.png')
settings_icon.set_colorkey((255, 255, 255))
settings_icon_hover = pygame.image.load('game_images/setting_icon - hover.png')
settings_icon_hover.set_colorkey((255, 255, 255))
grass_image = pygame.image.load('game_images/grass-tile.png')
dirt_image = pygame.image.load('game_images/dirt-tile.png')
grass_right_image = pygame.image.load('game_images/side-grass-tile-right.png')
grass_left_image = pygame.image.load('game_images/side-grass-tile-left.png')
gun_img = pygame.image.load("game_images/gun-img.png")
gun_img = gun_img.convert()
gun_img.set_colorkey((255, 255, 255))
heart_img = pygame.image.load('game_images/health.png')
heart_img.set_colorkey((0, 0, 0))
pointer_image = pygame.image.load("game_images/mouse.png")
pointer_image.set_colorkey((0, 0, 0))
# main_menu_music = pygame.mixer.Sound('other_stuff/MainMenuTBAL-Song.wav')
TILE_SIZE = grass_image.get_width()
true_scroll = [0, 0]
font = pygame.font.Font('other_stuff/font.ttf', 24)
sfont = pygame.font.Font('other_stuff/font.ttf', 8)
keys_font = pygame.font.Font('other_stuff/baby blocks.ttf', 16)


def load_map(path):
    with open(path + '.txt', 'r') as map_file:
        data = map_file.read()
    data = data.split("\n")
    game_map = []
    for row in data:
        game_map.append(list(row))
    return game_map


with open("other_stuff/played_before.txt") as played_before:
    played = played_before.read()

if played == "True":
    pass
else:
    game_map = load_map("game_levels_maps/tutorial_map")

animation_frames = {}


def load_animations(path, frame_durations):
    animation_name = path.split('/')[-1]
    animation_frame_data = []
    n = 0
    for frame in frame_durations:
        animation_frame_id = animation_name + '_' + str(n)
        img_loc = path + '/' + animation_frame_id + '.png'
        animation_image = pygame.image.load(img_loc).convert()
        animation_image.set_colorkey((0, 0, 0))
        animation_frames[animation_frame_id] = animation_image.copy()
        for i in range(frame):
            animation_frame_data.append(animation_frame_id)
        n += 1
    return animation_frame_data


def change_action(action_var, frame, new_value):
    if action_var != new_value:
        action_var = new_value
        frame = 0
    return action_var, frame


animation_database = {}

animation_database['run'] = load_animations('player_animations/run', [12, 12])
animation_database['idle'] = load_animations('player_animations/idle', [40, 40])
animation_database['lava'] = load_animations('lava_animations/lava', [2000, 2000])
animation_database['mouse'] = load_animations('mouse_animations/mouse', [60, 60])
animation_database['idlez'] = load_animations('zombie_animations/idlez', [500, 500])
animation_database['runz'] = load_animations('zombie_animations/runz', [100, 100])


def collision_test(rect, tiles):
    collision_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            collision_list.append(tile)
    return collision_list


def move(rect, movement, tiles):
    collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}
    rect.x += movement[0]
    collision_list = collision_test(rect, tiles)
    for tile in collision_list:
        if movement[0] > 0:
            rect.right = tile.left
            collision_types['right'] = True
        elif movement[0] < 0:
            rect.left = tile.right
            collision_types['left'] = True
    rect.y += movement[1]
    collision_list = collision_test(rect, tiles)
    for tile in collision_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_types['bottom'] = True
        elif movement[1] < 0:
            rect.top = tile.bottom
            collision_types['top'] = True
    return rect, collision_types


class Button:
    def __init__(self, x, y, width, height, text=''):
        self.color = None
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    def draw(self, win, alpha_color=()):
        rect = (self.x, self.y, self.width, self.height)
        if alpha_color != ():
            self.color = alpha_color
        shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
        pygame.draw.rect(shape_surf, self.color, shape_surf.get_rect())
        win.blit(shape_surf, rect)
        # pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))

        if self.text != '':
            font = pygame.font.Font('other_stuff/font.ttf', 8)
            text = font.render(self.text, True, (255, 255, 255))
            win.blit(text, (
                self.x + (self.width / 2 - text.get_width() / 2), self.y + (self.height / 2 - text.get_height() / 2)))

    def isOver(self, pos):
        # Pos is the mouse position or a tuple of (x,y) coordinates
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True

        return False


# main menu buttons
play_button = Button(135, 80, 30, 13, 'Play')
option_button = Button(132, 100, 35, 13, 'Options')
exit_button = Button(135, 120, 30, 13, 'Quit')

# option menu buttons
video_settings_button = Button(135, 80, 30, 13, 'Info')
back_button = Button(135, 100, 30, 13, '< Back')

# pause menu buttons
continue_button = Button(136, 60, 40, 13, 'Continue')
main_menu_button = Button(135, 80, 45, 13, 'Main Menu')
quit_game_button = Button(140, 100, 30, 13, 'Quit')


def blit_gun(surf2, pos):
    x = int(surf2.get_width() / 2)
    y = int(surf2.get_height() / 2)
    display.blit(surf2, (pos[0] - x, pos[1] - y))


def flip_img(img, boolean, boolean_2):
    return pygame.transform.flip(img, boolean, boolean_2)


def collide(rect1, rect2):
    return rect1.colliderect(rect2)


u_w = pygame.display.Info().current_w
u_h = pygame.display.Info().current_h
dividendw = u_w / 300
dividendh = u_h / 200

pygame.mixer.music.set_volume(.3)
pygame.mixer.music.load("game_sounds/MMTBAL-Song.wav")
pygame.mixer.music.play(-1)


def main_menu():
    run = True
    move_b = False
    back_x, back_y = 0, 0
    pygame.mouse.set_visible(True)
    while run:
        display.fill((146, 244, 255))
        display.blit(background, [back_x, back_y])
        mpos = list(pygame.mouse.get_pos())
        mpos[0] = mpos[0] / dividendw
        mpos[1] = mpos[1] / dividendh
        draw_text = font.render('The Brave and Lost', True, (255, 255, 255))
        textRect = [25, 30]
        if not move_b:
            if play_button.isOver(mpos):
                play_button.draw(display, (47, 24, 63, 180))
            else:
                play_button.draw(display, (47, 24, 63, 0))
            if exit_button.isOver(mpos):
                exit_button.draw(display, (47, 24, 63, 180))
            else:
                exit_button.draw(display, (47, 24, 63, 0))
            if option_button.isOver(mpos):
                option_button.draw(display, (47, 24, 63, 180))
            else:
                option_button.draw(display, (47, 24, 63, 0))
            display.blit(draw_text, textRect)
        for event in pygame.event.get():  # event loop
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.isOver(mpos):
                    move_b = True
                if exit_button.isOver(mpos):
                    sys.exit()
                if option_button.isOver(mpos):
                    options()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSLASH:
                    game_over()

        # moves the background down making it seem like the title screen is leaving
        if move_b:
            pygame.mixer.music.fadeout(6400)
            back_y = round(back_y, 2)
            back_y -= 0.47
            if back_y == -195.99:
                move_b = False
                main_game()
        surf = pygame.transform.scale(display, screen.get_size())
        screen.blit(surf, (0, 0))
        pygame.display.update()
        fps.tick(60)


def options():
    run = True
    back_x, back_y = 0, 0
    pygame.mouse.set_visible(True)
    while run:
        display.fill((146, 244, 255))
        display.blit(background, [back_x, back_y])
        dividendw = u_w / 300
        dividendh = u_h / 200
        mpos = list(pygame.mouse.get_pos())
        mpos[0] = mpos[0] / dividendw
        mpos[1] = mpos[1] / dividendh
        if video_settings_button.isOver(mpos):
            video_settings_button.draw(display, (47, 24, 63, 180))
        else:
            video_settings_button.draw(display, (47, 24, 63, 0))
        if back_button.isOver(mpos):
            back_button.draw(display, (47, 24, 63, 180))
        else:
            back_button.draw(display, (47, 24, 63, 0))
        draw_text = sfont.render('Options', True, (255, 255, 255))
        textsize = [133, 30]
        rect = (0, 27, 300, 15)
        shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
        pygame.draw.rect(shape_surf, (47, 24, 63, 180), shape_surf.get_rect())
        display.blit(shape_surf, rect)
        display.blit(draw_text, textsize)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.isOver(mpos):
                    run = False
                    main_menu()
                if video_settings_button.isOver(mpos):
                    info()
        surf = pygame.transform.scale(display, screen.get_size())
        screen.blit(surf, (0, 0))
        pygame.display.update()
        fps.tick(60)


def info():
    run = True
    back_x, back_y = 0, 0
    pygame.mouse.set_visible(True)
    while run:
        display.fill((146, 244, 255))
        display.blit(background, [back_x, back_y])
        dividendw = u_w / 300
        dividendh = u_h / 200
        mpos = list(pygame.mouse.get_pos())
        mpos[0] = mpos[0] / dividendw
        mpos[1] = mpos[1] / dividendh
        if back_button.isOver(mpos):
            back_button.draw(display, (47, 24, 63, 180))
        else:
            back_button.draw(display, (47, 24, 63, 0))
        draw_text = sfont.render('Info', True, (255, 255, 255))
        textsize = [140, 30]
        rect = (0, 27, 300, 15)
        shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
        pygame.draw.rect(shape_surf, (47, 24, 63, 180), shape_surf.get_rect())
        display.blit(shape_surf, rect)
        display.blit(draw_text, textsize)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.isOver(mpos):
                    run = False
                    options()
        surf = pygame.transform.scale(display, screen.get_size())
        screen.blit(surf, (0, 0))
        pygame.display.update()
        fps.tick(60)


def main_game():
    run = True
    player_rect = pygame.Rect(200, 50, 11, 19)

    moving_right = False
    moving_left = False
    flip = False

    player_momentum = 0
    air_timer = 0

    player_action = 'idle'
    player_frame = 0
    lava_action = 'lava'
    lava_frame = 0
    mouse_action = 'mouse'
    mouse_frame = 0
    enemy_action = 'idlez'
    enemy_frame = 0

    back_x, back_y = 0, -195.99

    gamestate = 'game'
    pygame.mixer.music.set_volume(.4)
    pygame.mixer.music.load("game_sounds/night ambience.mp3")
    pygame.mixer.music.play(-1)

    run_sound = pygame.mixer.Sound('game_sounds/sfx_step_grass_l.flac')
    run_sound.set_volume(0.3)
    run_sound_timer = 0

    shoot_sound = pygame.mixer.Sound('game_sounds/shot.wav')

    move_font = keys_font.render("A   D", True, (255, 255, 255))
    move_font_arrows = sfont.render("<--     -->", True, (255, 255, 255))
    move_text = sfont.render("Movement", True, (255, 255, 255))
    jump_font = keys_font.render("W", True, (255, 255, 255))
    jump_font_arrow = sfont.render("^", True, (255, 255, 255))
    jump_text = sfont.render("Jumping", True, (255, 255, 255))
    jump_font_arrow_line = sfont.render("|", True, (255, 255, 255))
    shoot_text = sfont.render("Shooting", True, (255, 255, 255))
    text = "Objective: Kill all zombies"

    bullets = []
    enemies = []
    particles = []

    lava_hit = False
    floor_hit = False

    enemy_momentum = 0
    flipz = False
    enemy_hit = False
    amount_enemies = 2
    for i in range(amount_enemies):
        random_x = random.randrange(900, 1100, 30)
        enemies.append([pygame.Rect(random_x, 95, 11, 17), 10])

    dmgtimer = 1
    dt = 1
    dmgspace = 60
    player_hp = 10

    while run:
        if gamestate == 'game':
            display.fill((146, 244, 255))
            display.blit(background, [back_x, back_y])
            surface.fill((0, 0, 0))
            surface.set_colorkey((0, 0, 0))

            pygame.mouse.set_visible(False)

            true_scroll[0] += 1
            true_scroll[0] += (player_rect.x - true_scroll[0] - 159) / 20
            true_scroll[1] += (player_rect.y - true_scroll[1] - 124) / 20
            scroll = true_scroll.copy()
            scroll[0] = int(scroll[0])
            scroll[1] = int(scroll[1])

            if player_rect.x < 350:
                display.blit(move_font, (150, 50))
                display.blit(move_font_arrows, (152, 70))
                display.blit(move_text, (154, 40))
            if 350 < player_rect.x < 550:
                display.blit(jump_font, (165, 50))
                display.blit(jump_font_arrow, (174, 37))
                display.blit(jump_font_arrow_line, (175, 40))
                display.blit(jump_text, (157, 70))
            if 550 <= player_rect.x < 750:
                display.blit(shoot_text, (165, 52))
                mouse_action, mouse_frame = change_action(mouse_action, mouse_frame, 'mouse')
                mouse_frame += 1
                if mouse_frame >= len(animation_database[mouse_action]):
                    mouse_frame = 0
                mouse_img_id = animation_database[mouse_action][mouse_frame]
                mouse_image = animation_frames[mouse_img_id]
                display.blit(mouse_image, (150, 50))
            if 750 <= player_rect.x < 800:
                finish_game_letter = sfont.render(text, True, (255, 255, 255))
                display.blit(finish_game_letter, (150, 50))

            if run_sound_timer > 0:
                run_sound_timer -= 1

            tile_rects = []
            y = 0
            for row in game_map:
                x = 0
                for tile in row:
                    if tile == '1':
                        display.blit(dirt_image, (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))
                    if tile == '2':
                        display.blit(grass_image, (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))
                    if tile == '3':
                        display.blit(grass_right_image, (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))
                    if tile == '4':
                        display.blit(grass_left_image, (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))
                    if tile == 'L':
                        lava_action, lava_frame = change_action(lava_action, lava_frame, 'lava')
                        lava_frame += 1
                        if lava_frame >= len(animation_database[lava_action]):
                            lava_frame = 0
                        lava_img_id = animation_database[lava_action][lava_frame]
                        lava_image = animation_frames[lava_img_id]
                        display.blit(lava_image, (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))
                    if tile != '0':
                        tile_rects.append(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                    x += 1
                y += 1

            player_movement = [0, 0]
            if moving_right:
                player_movement[0] += 2
            if moving_left:
                player_movement[0] -= 2
            player_movement[1] += player_momentum
            player_momentum += 0.2
            if player_momentum > 3:
                player_momentum = 3

            if moving_left and not flip:
                player_movement[0] += 1
            if moving_right and flip:
                player_movement[0] -= 1

            if player_rect.y > 124:
                player_rect.y = 50
                player_rect.x = 200
                back_x = 0

            if player_movement[0] > 0:
                player_action, player_frame = change_action(player_action, player_frame, 'run')
            if player_movement[0] == 0:
                player_action, player_frame = change_action(player_action, player_frame, 'idle')
            if player_movement[0] < 0:
                player_action, player_frame = change_action(player_action, player_frame, 'run')

            player_rect, collisions = move(player_rect, player_movement, tile_rects)

            if collisions['bottom']:
                player_momentum = 0
                air_timer = 0
                if player_movement[0] != 0:
                    if run_sound_timer == 0:
                        run_sound_timer = 20
                        run_sound.play()
            else:
                air_timer += 1

            dividendw = u_w / 300
            dividendh = u_h / 200
            mx, my = pygame.mouse.get_pos()
            mx = mx / dividendw
            my = my / dividendh

            display.blit(pointer_image, (mx, my))
            display.blit(settings_icon, (5, 5))

            if mx > player_rect.x - scroll[0]:
                flip = False
            else:
                flip = True

            player_frame += 1
            if player_frame >= len(animation_database[player_action]):
                player_frame = 0
            player_img_id = animation_database[player_action][player_frame]
            player_image = animation_frames[player_img_id]
            display.blit(flip_img(player_image, flip, False), (player_rect.x - scroll[0], player_rect.y - scroll[1]))

            heartx = 210
            for heart in range(player_hp):
                display.blit(heart_img, (heartx, 5))
                heartx = heartx + 8

            x = player_rect.x + 14
            y = player_rect.y + 8
            rot = -math.degrees(math.atan2(my - (int(y) - scroll[1]), mx - (int(x) - scroll[0])))
            blit_gun(pygame.transform.rotate(flip_img(gun_img, False, flip), rot),
                     [(player_rect.x + 6) - scroll[0], (player_rect.y + 12) - scroll[1]])

            if my > 5 and my < 15 and mx > 5 and mx < 15:
                display.blit(settings_icon_hover, (5, 5))
                display.blit(pointer_image, (mx, my))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    gamestate = 'pause'
                if event.type == pygame.MOUSEBUTTONDOWN:
                    nmx, nmy = pygame.mouse.get_pos()
                    nmx, nmy = nmx / dividendw, nmy / dividendh
                    distance_x = nmx - (player_rect.x - scroll[0] + 5)
                    distance_y = nmy - (player_rect.y - scroll[1] + 12)
                    angle = math.atan2(distance_y, distance_x)
                    speed_x = 3 * math.cos(angle)
                    speed_y = 3 * math.sin(angle)
                    bullets.append([player_rect.x - scroll[0] + 6, player_rect.y - scroll[1] + 13, speed_x, speed_y])
                    shoot_sound.play(0)
                    if my > 5 and my < 15 and mx > 5 and mx < 15:
                        gamestate = 'pause'
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_d:
                        moving_right = True
                    if event.key == pygame.K_a:
                        moving_left = True
                    if event.key == pygame.K_w:
                        if air_timer < 6:
                            player_momentum = -2.5
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_d:
                        moving_right = False
                    if event.key == pygame.K_a:
                        moving_left = False
            floor_rect = pygame.Rect(0 - scroll[0], 113 - scroll[1], 433, 55)
            floor_rect2 = pygame.Rect(480 - scroll[0], 113 - scroll[1], 433, 55)
            lava_rect = pygame.Rect(430 - scroll[0], 145 - scroll[1], 50, 50)
            left_mountain_rect1 = pygame.Rect(145 - scroll[0], 80 - scroll[1], 32, 32)
            left_mountain_rect2 = pygame.Rect(80 - scroll[0], 32 - scroll[1], 32, 32)
            right_mountain_rect1 = pygame.Rect(1183 - scroll[0], 80 - scroll[1], 32, 32)
            right_mountain_rect2 = pygame.Rect(1248 - scroll[0], 32 - scroll[1], 32, 32)
            for bullet in bullets:
                bullet[0] += bullet[2]
                bullet[1] += bullet[3]
            for bullet in bullets:
                bullet_rect = pygame.Rect(bullet[0], bullet[1], 1, 1)
                if bullet[0] > display.get_size()[0] or bullet[1] > display.get_size()[1]:
                    bullets.remove(bullet)
                if bullet_rect.colliderect(floor_rect) or bullet_rect.colliderect(
                        floor_rect2) or bullet_rect.colliderect(left_mountain_rect1) or bullet_rect.colliderect(
                    left_mountain_rect2) or bullet_rect.colliderect(right_mountain_rect1) or bullet_rect.colliderect(
                    right_mountain_rect2):
                    bullets.remove(bullet)
                    lava_hit = False
                    enemy_hit = False
                    floor_hit = True
                    particles.append(
                        [[bullet[0] * 4, bullet[1] * 4], [random.randint(0, 20) / 10 - 1, -2], random.randint(3, 4)])
                    particles.append(
                        [[bullet[0] * 4, bullet[1] * 4], [random.randint(0, 20) / 10 - 1, -2], random.randint(3, 4)])
                    particles.append(
                        [[bullet[0] * 4, bullet[1] * 4], [random.randint(0, 20) / 10 - 1, -2], random.randint(3, 4)])
                if bullet_rect.colliderect(lava_rect):
                    bullets.remove(bullet)
                    lava_hit = True
                    enemy_hit = False
                    floor_hit = False
                    particles.append(
                        [[bullet[0] * 4, bullet[1] * 4], [random.randint(0, 20) / 10 - 1, -2], random.randint(3, 4)])
                    particles.append(
                        [[bullet[0] * 4, bullet[1] * 4], [random.randint(0, 20) / 10 - 1, -2], random.randint(3, 4)])
                    particles.append(
                        [[bullet[0] * 4, bullet[1] * 4], [random.randint(0, 20) / 10 - 1, -2], random.randint(3, 4)])
                for enemy in enemies:
                    if collide(pygame.Rect(enemy[0].x - scroll[0], enemy[0].y - scroll[1], 11, 17), bullet_rect):
                        lava_hit = False
                        enemy_hit = True
                        floor_hit = False
                        bullets.remove(bullet)
                        enemy[1] = enemy[1] - 5
                        if enemy[1] == 0:
                            enemies.remove(enemy)
                            amount_enemies = amount_enemies - 1
                        particles.append(
                            [[bullet[0] * 4, bullet[1] * 4], [random.randint(0, 20) / 10 - 1, -2],
                             random.randint(3, 4)])
                        particles.append(
                            [[bullet[0] * 4, bullet[1] * 4], [random.randint(0, 20) / 10 - 1, -2],
                             random.randint(3, 4)])
                        particles.append(
                            [[bullet[0] * 4, bullet[1] * 4], [random.randint(0, 20) / 10 - 1, -2],
                             random.randint(3, 4)])
                pygame.draw.rect(display, (0, 255, 0), bullet_rect)

            for enemy, health in enemies:
                enemy_frame += 1
                if enemy_frame >= len(animation_database[enemy_action]):
                    enemy_frame = 0
                enemy_img_id = animation_database[enemy_action][enemy_frame]
                enemy_image = animation_frames[enemy_img_id]
                enemy_air_timer = 0
                enemy_movement = [0, 0]
                enemy_momentum += 0.2
                enemy_movement[1] += enemy_momentum
                if enemy_momentum > 3:
                    enemy_momentum = 3
                if enemy.x - player_rect.x <= 120:
                    if enemy.x > player_rect.x:
                        enemy_movement[0] -= 1
                        flipz = True
                        enemy_action, enemy_frame = change_action(enemy_action, enemy_frame, 'runz')
                    if enemy.x < player_rect.x:
                        enemy_movement[0] += 1
                        flipz = False
                        enemy_action, enemy_frame = change_action(enemy_action, enemy_frame, 'runz')
                    enemy, collisions = move(enemy, enemy_movement, tile_rects)
                else:
                    enemy_action, enemy_frame = change_action(enemy_action, enemy_frame, 'idlez')
                if collisions['bottom']:
                    enemy_momentum = 0
                    enemy_air_timer = 0
                else:
                    enemy_air_timer += 1
                if enemy.colliderect(player_rect):
                    dmgtimer += dt
                    if dmgtimer >= dmgspace:
                        player_hp = player_hp - 2
                        dmgtimer = 0
                        if player_hp == 0:
                            player_rect.x = 200
                display.blit(flip_img(enemy_image, flipz, False), (enemy.x - scroll[0], enemy.y - scroll[1]))

            if amount_enemies == 0:
                game_over()

            for particle in particles:
                particle[0][0] += particle[1][0]
                particle[0][1] += particle[1][1]
                particle[2] -= 0.06
                particle[1][1] += 0.1
                if lava_hit:
                    pygame.draw.circle(surface, (194, 46, 33), [int(particle[0][0]), int(particle[0][1])],
                                       int(particle[2]))
                if enemy_hit:
                    pygame.draw.circle(surface, (136, 0, 23), [int(particle[0][0]), int(particle[0][1])],
                                       int(particle[2]))
                if floor_hit:
                    pygame.draw.circle(surface, (100, 21, 77), [int(particle[0][0]), int(particle[0][1])],
                                       int(particle[2]))
                if particle[2] <= 0:
                    particles.remove(particle)

            surf = pygame.transform.scale(display, screen.get_size())
            screen.blit(surf, (0, 0))
            surf1 = pygame.transform.scale(surface, screen.get_size())
            screen.blit(surf1, (0, 0))
            pygame.display.update()
            fps.tick(60)
        if gamestate == 'pause':
            pygame.mouse.set_visible(True)
            display.fill((146, 244, 255))
            display.blit(night_background, (back_x, back_y))
            dividendw = u_w / 300
            dividendh = u_h / 200
            mpos = list(pygame.mouse.get_pos())
            mpos[0] = mpos[0] / dividendw
            mpos[1] = mpos[1] / dividendh
            if continue_button.isOver(mpos):
                continue_button.draw(display, (47, 24, 63, 180))
            else:
                continue_button.draw(display, (47, 24, 63, 0))
            if main_menu_button.isOver(mpos):
                main_menu_button.draw(display, (47, 24, 63, 180))
            else:
                main_menu_button.draw(display, (47, 24, 63, 0))
            if quit_game_button.isOver(mpos):
                quit_game_button.draw(display, (47, 24, 63, 180))
            else:
                quit_game_button.draw(display, (47, 24, 63, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    gamestate = 'game'
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if quit_game_button.isOver(mpos):
                        sys.exit()
                    if continue_button.isOver(mpos):
                        gamestate = 'game'
                    if main_menu_button.isOver(mpos):
                        back_y, back_x = 0, 0
                        main_menu()
            surf = pygame.transform.scale(display, screen.get_size())
            screen.blit(surf, (0, 0))
            pygame.display.update()  # update display
            fps.tick(60)


def game_over():
    run = True

    font_x, font_y = 50, 0
    go_0_font = font.render("Congratulations!", True, (255, 255, 255))
    go_1_font = font.render("You have completed", True, (255, 255, 255))
    go_2_font = font.render("the tutorial!", True, (255, 255, 255))
    go_3_font = font.render("That is it for the game", True, (255, 255, 255))
    go_4_font = font.render("More will come", True, (255, 255, 255))
    go_5_font = font.render("or not...", True, (255, 255, 255))
    pygame.mixer.music.set_volume(0)

    while run:
        display.fill((0, 0, 0))

        font_y -= 0.5
        display.blit(go_0_font, (font_x, font_y + 200))
        display.blit(go_1_font, (font_x - 25, font_y + 300))
        display.blit(go_2_font, (font_x + 20, font_y + 350))
        display.blit(go_3_font, (font_x - 47, font_y + 450))
        display.blit(go_4_font, (font_x + 17, font_y + 550))
        display.blit(go_5_font, (font_x + 50, font_y + 650))

        if font_y == -650:
            sys.exit()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                sys.exit()

        surf = pygame.transform.scale(display, screen.get_size())
        screen.blit(surf, (0, 0))
        pygame.display.update()  # update display
        fps.tick(60)


# the thing that will run the whole game
main_menu()
