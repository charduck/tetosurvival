try:
    import sys
    import pygame as pg # type: ignore
    import random as r
    import math
    import time as t
    import json
except ImportError as ie:
    print(ie)

pg.init()
clock = pg.time.Clock()



# ----------- LOADING SETTINGS ----------- #


with open("data/settings.json", "r") as resfile:
    resdata = json.load(resfile)

resolution = resdata["resolution"]
screen_width, screen_height = resolution

# load settings from settings.json
def load_settings():
    try:
        with open("data/settings.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"music": True, "resolution": [1280, 720]} # defaults

# save settings to settings.json
def save_settings(settings):
    with open("data/settings.json", "w") as f:
        json.dump(settings, f)

settings = load_settings()

screen = pg.display.set_mode((screen_width, screen_height), pg.RESIZABLE)
running = True

VIRTUAL_WIDTH = 1280
VIRTUAL_HEIGHT = 720
virtual_surface = pg.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))



# ----------- LOADING MUSIC ----------- #

# init mixer
pg.mixer.init()

# event for when current track ends
TRACK_END = pg.USEREVENT + 1
pg.mixer.music.set_endevent(TRACK_END)

def play_music():
    if settings.get("music", True):
        play_next()
    else:
        pg.mixer.music.stop()

tracks = ["data/ochamekinou.mp3", "data/tetoterritory.mp3"]
r.shuffle(tracks)
track_iter = iter(tracks)

def play_next():
    global track_iter, tracks
    try:
        next_track = next(track_iter)
    except StopIteration:
        r.shuffle(tracks)
        track_iter = iter(tracks)
        next_track = next(track_iter)
    print(f"Now playing: {next_track}")
    pg.mixer.music.load(next_track)
    pg.mixer.music.play()






# ----------- LOADING ASSETS ----------- #

# sprites loading
teto_image = pg.image.load("data/teto.webp").convert_alpha()
miku_image = pg.image.load("data/miku.webp").convert_alpha()
neru_image = pg.image.load("data/neru.webp").convert_alpha()
baguette_image = pg.image.load("data/baguette.webp").convert_alpha()

# scale images for menu
miku_image_menu = pg.transform.scale(miku_image, (150, 150))
teto_image_menu = pg.transform.scale(teto_image, (150, 150))
neru_image_menu = pg.transform.scale(neru_image, (150, 150))

# set window icon + caption
pg.display.set_caption("Teto Survival")
pg.display.set_icon(teto_image)




# ----------- LOADING COLOUR VARIABLES ----------- #

# colours
black = (0, 0, 0)
white = (255, 255, 255)
green = (110, 194, 100)
gumigreen = (109,237,83)
blue = (101, 110, 195)
mikublue = (134, 206, 203)
red = (195, 101, 110)
tetored = (255,0,69)
yellow = (181, 195, 101)
neruyellow = (213, 157, 36)
# random colour selector
a = r.randint(1, 255)
b = r.randint(1, 255)
c = r.randint(1, 255)


# ----------- LOADING GAME VARIABLES ----------- #

# player settings
player_size = 80
player_x = VIRTUAL_WIDTH // 2 - player_size // 2
player_y = VIRTUAL_HEIGHT // 2 - player_size // 2
player_speed = 1
player_hp = 100

# baguette settings
baguette_length = 60
baguette_width = 8
proj_speed = 4
proj_lifetime = 60
last_throw_time = 0
throw_cooldown = 1

# game variables
enemies = []
thrown_baguettes = []
wave_count = 0
score = 0

# enemy settings
enemy_speed = player_speed / 2




# ----------- LOADING MAP ----------- #


# map offset
map_offset_x = 0
map_offset_y = 0

# map generation
def generate_map(num_objects, map_width, map_height, min_size=50, max_size=200):
    objects = []
    for _ in range(num_objects):
        width = r.randint(min_size, max_size)
        height = r.randint(min_size, max_size)
        x = r.randint(-map_width // 2, map_width // 2 - width)
        y = r.randint(-map_height // 2, map_height // 2 - height)
        objects.append(pg.Rect(x, y, width, height))
    return objects

# generate random map objects
map_objects = generate_map(num_objects=10000, map_width=30000, map_height=30000)



# ----------- LOADING UI ----------- #

def get_virtual_mouse_pos():
    mouse_x, mouse_y = pg.mouse.get_pos()
    scale_x = VIRTUAL_WIDTH / screen_width
    scale_y = VIRTUAL_HEIGHT / screen_height
    return int(mouse_x * scale_x), int(mouse_y * scale_y)



# credits screen
def credits_screen():
    """Display the credits screen."""
    credits_running = True
    font = pg.font.Font(None, 50)
    with open("data/credits.txt", "r") as f:
        credits_lines = f.readlines()

    while credits_running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                credits_running = False
            elif event.type == TRACK_END:
                play_next()
            elif event.type == pg.VIDEORESIZE:
                screen_width, screen_height = event.w, event.h
                screen = pg.display.set_mode((screen_width, screen_height), pg.RESIZABLE)
        scaled = pg.transform.scale(virtual_surface, (screen_width, screen_height))
        screen.blit(scaled, (0, 0))
        virtual_surface.fill(black)
        for i, line in enumerate(credits_lines):
            text_surface = font.render(line.strip(), True, white)
            virtual_surface.blit(text_surface, (50, 50 + i * 60))

        pg.display.flip()

# settings screen with visual indicators and dropdown for resolution
def settings_screen():
    """Display the settings screen."""
    settings_running = True
    font = pg.font.Font(None, 50)

    buttons = [
        {"text": "Toggle Music", "action": "toggle_music"},
        {"text": "Change Resolution", "action": "change_resolution"},
        {"text": "Back", "action": "back"}
    ]

    button_rects = []
    for i, button in enumerate(buttons):
        text_surface = font.render(button["text"], True, white)
        text_rect = text_surface.get_rect(center=(VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT // 2 - 100 + i * 100))
        button_rects.append((text_surface, text_rect, button["action"]))

    resolution_options = [[1280, 720], [1920, 1080]]
    resolution_index = resolution_options.index(settings.get("resolution", [1280, 720]))

    while settings_running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == TRACK_END:
                play_next()
            elif event.type == pg.VIDEORESIZE:
                screen_width, screen_height = event.w, event.h
                screen = pg.display.set_mode((screen_width, screen_height), pg.RESIZABLE)

            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_pos = get_virtual_mouse_pos()
                for text_surface, text_rect, action in button_rects:
                    if text_rect.collidepoint(mouse_pos):
                        if action == "toggle_music":
                            settings["music"] = not settings.get("music", True)
                            save_settings(settings)
                            play_music()
                        elif action == "change_resolution":
                            resolution_index = (resolution_index + 1) % len(resolution_options)
                            new_resolution = resolution_options[resolution_index]
                            settings["resolution"] = new_resolution
                            save_settings(settings)
                            global virtual_surface
                            screen_width, screen_height = new_resolution
                            screen = pg.display.set_mode((screen_width, screen_height), pg.RESIZABLE)
                            print("Resolution changed to", new_resolution)
                        elif action == "back":
                            settings_running = False

        scaled = pg.transform.scale(virtual_surface, (screen_width, screen_height))
        screen.blit(scaled, (0, 0))
        virtual_surface.fill(black)

        # draw buttons
        for text_surface, text_rect, _ in button_rects:
            virtual_surface.blit(text_surface, text_rect)

        # draw music status indicator
        music_status = "On" if settings.get("music", True) else "Off"
        music_status_text = font.render(f"Music: {music_status}", True, white)
        virtual_surface.blit(music_status_text, (VIRTUAL_WIDTH // 2 - 100, VIRTUAL_HEIGHT // 2 - 200))

        # draw resolution dropdown
        resolution_text = font.render(f"Resolution: {settings['resolution'][0]}x{settings['resolution'][1]}", True, white)
        virtual_surface.blit(resolution_text, (VIRTUAL_WIDTH // 2 - 100, VIRTUAL_HEIGHT // 2 - 150))

        pg.display.flip()




# ----------- MAIN MENU ----------- #

def main_menu():
    """Display the main menu screen."""
    menu_running = True
    font = pg.font.Font(None, 74)
    buttons = [
        {"text": "Play", "action": "play"},
        {"text": "Settings", "action": "settings"},
        {"text": "Credits", "action": "credits"},
        {"text": "Quit", "action": "quit"}
    ]

    button_rects = []
    for i, button in enumerate(buttons):
        text_surface = font.render(button["text"], True, white)
        text_rect = text_surface.get_rect(center=(VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT // 2 - 100 + i * 100))
        button_rects.append((text_surface, text_rect, button["action"]))

    while menu_running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == TRACK_END:
                play_next()
            elif event.type == pg.VIDEORESIZE:
                screen_width, screen_height = event.w, event.h
                screen = pg.display.set_mode((screen_width, screen_height), pg.RESIZABLE)

            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_pos = get_virtual_mouse_pos()
                for text_surface, text_rect, action in button_rects:
                    if text_rect.collidepoint(mouse_pos):
                        if action == "play":
                            menu_running = False
                        elif action == "settings":
                            settings_screen()
                        elif action == "credits":
                            credits_screen()
                        elif action == "quit":
                            pg.quit()
                            sys.exit()

        scaled = pg.transform.scale(virtual_surface, (screen_width, screen_height))
        screen.blit(scaled, (0, 0))

        # draw menu images
        virtual_surface.blit(miku_image_menu, (50, 50))
        virtual_surface.blit(neru_image_menu, (VIRTUAL_WIDTH - 200, 50))
        virtual_surface.blit(teto_image_menu, (VIRTUAL_WIDTH // 2 - 75, 50))

        # draw menu buttons
        for text_surface, text_rect, _ in button_rects:
            virtual_surface.blit(text_surface, text_rect)

        pg.display.flip()



# ----------- LOADING GAME LOGIC ----------- #

# Spawn enemies in waves
def spawn_wave():
    global wave_count
    wave_count += 1
    for _ in range(5 + wave_count):  # Increase enemy count with each wave
        x = r.randint(-1500, 1500)
        y = r.randint(-1500, 1500)
        enemies.append({"x": x, "y": y, "hp": 1})

# baguette collision

def check_collision(baguette, enemy):
    baguette_rect = pg.Rect(baguette["x"] - 40, baguette["y"] - 40, 80, 80)  # baguette hitbox
    enemy_rect = pg.Rect(enemy["x"] + map_offset_x, enemy["y"] + map_offset_y, 60, 60)  # enemy hitbox
    return baguette_rect.colliderect(enemy_rect)

# checl for collisions
def check_player_collision(player, enemy):
    player_rect = pg.Rect(player["x"], player["y"], player_size, player_size)
    enemy_rect = pg.Rect(enemy["x"] + map_offset_x, enemy["y"] + map_offset_y, 60, 60)
    return player_rect.colliderect(enemy_rect)

# end screen
def death_screen():
    font = pg.font.Font(None, 100)
    death_text = font.render("Teto Tragedy :'(", True, red)
    score_text = font.render(f"Final Score: {score}", True, white)
    wave_text = font.render(f"Waves Survived: {wave_count}", True, white)

    virtual_surface.fill(black)
    scaled = pg.transform.scale(virtual_surface, (screen_width, screen_height))
    screen.blit(scaled, (0, 0))
    virtual_surface.blit(death_text, (VIRTUAL_WIDTH // 2 - death_text.get_width() // 2, VIRTUAL_HEIGHT // 2 - 100))
    virtual_surface.blit(score_text, (VIRTUAL_WIDTH // 2 - score_text.get_width() // 2, VIRTUAL_HEIGHT // 2))
    virtual_surface.blit(wave_text, (VIRTUAL_WIDTH // 2 - wave_text.get_width() // 2, VIRTUAL_HEIGHT // 2 + 100))

    pg.display.flip()
    t.sleep(3)
    pg.quit()
    sys.exit()

def show_fps(x):
    x = int(fps)
    return x


# ----------- LOADING - SPLASH SCREEN ----------- #
splash_running = True
while splash_running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == TRACK_END:
                play_next()
            elif event.type == pg.VIDEORESIZE:
                screen_width, screen_height = event.w, event.h
                screen = pg.display.set_mode((screen_width, screen_height), pg.RESIZABLE)

        # load splash
        splash = pg.image.load("data/splash.png").convert_alpha()
        splash = pg.transform.scale(splash, (VIRTUAL_WIDTH, VIRTUAL_HEIGHT))

        # fade in
        for alpha in range(0, 256, 5):
            splash.set_alpha(alpha)
            virtual_surface.fill((0, 0, 0))  # black bg
            virtual_surface.blit(splash, (0, 0))
            scaled = pg.transform.scale(virtual_surface, (screen_width, screen_height))
            screen.blit(scaled, (0, 0))
            pg.display.flip()
            clock.tick(30)

        # 2 second hold
        t.sleep(2)

        # fade out
        for alpha in range(255, -1, -5):
            splash.set_alpha(alpha)
            virtual_surface.fill((0, 0, 0))
            virtual_surface.blit(splash, (0, 0))
            scaled = pg.transform.scale(virtual_surface, (screen_width, screen_height))
            screen.blit(scaled, (0, 0))
            pg.display.flip()
            clock.tick(30)
        
        splash_running = False



# ----------- INITIALIZING MENU/GAME ----------- #

play_music()
main_menu()

# transform sprites for game loop
teto_image = pg.transform.scale(teto_image, (player_size, player_size))
baguette_image = pg.transform.scale(baguette_image, (80, 80))
miku_image = pg.transform.scale(miku_image, (60, 60))



# Main loop
spawn_wave()
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:  # quit event
            running = False
        elif event.type == TRACK_END:
            play_next()
        elif event.type == pg.VIDEORESIZE:
            screen_width, screen_height = event.w, event.h
            screen = pg.display.set_mode((screen_width, screen_height), pg.RESIZABLE)

    clock.tick()
    fps = clock.get_fps()
    fps_count = show_fps(fps)

    keys = pg.key.get_pressed()  # wasd keypresses
    if keys[pg.K_a]:
        map_offset_x += player_speed
    if keys[pg.K_d]:
        map_offset_x -= player_speed
    if keys[pg.K_w]:
        map_offset_y += player_speed
    if keys[pg.K_s]:
        map_offset_y -= player_speed

    virtual_surface.fill(blue)  # screen bg

    # draw map
    for obj in map_objects:
        screen_x = obj.x + map_offset_x
        screen_y = obj.y + map_offset_y
        if -100 < screen_x < VIRTUAL_WIDTH + 100 and -100 < screen_y < VIRTUAL_HEIGHT + 100:  # Only draw visible objects
            pg.draw.rect(virtual_surface, (a, b, c), (screen_x, screen_y, obj.width, obj.height))

    # get mouse pos, calculate angle
    mouse_x, mouse_y = get_virtual_mouse_pos()
    dx = mouse_x - (player_x + player_size // 2)
    dy = mouse_y - (player_y + player_size // 2)
    angle = math.atan2(dy, dx)

    # draw baguette (if cooldown is over)
    if t.time() - last_throw_time >= throw_cooldown:
        end_x = player_x + player_size // 2 + math.cos(angle) * baguette_length
        end_y = player_y + player_size // 2 + math.sin(angle) * baguette_length
        rotated_baguette = pg.transform.rotate(baguette_image, -math.degrees(angle))
        virtual_surface.blit(rotated_baguette, (end_x - 40, end_y - 40))

    # throw baguette on m1
    if pg.mouse.get_pressed()[0]:
        current_time = t.time()
        if current_time - last_throw_time >= throw_cooldown:
            last_throw_time = current_time
            # baguette thrown as proj
            dx = math.cos(angle) * proj_speed
            dy = math.sin(angle) * proj_speed
            thrown_baguettes.append({
                "x": player_x + player_size // 2,
                "y": player_y + player_size // 2,
                "dx": dx,
                "dy": dy,
                "life": proj_lifetime
            })

    # draw thrown baguettes as proj
    for baguette in thrown_baguettes[:]:
        baguette["x"] += baguette["dx"]
        baguette["y"] += baguette["dy"]
        baguette["life"] -= 1
        if baguette["life"] <= 0:
            thrown_baguettes.remove(baguette)
        else:
            # determine which baguette to throw
            rotated_baguette = pg.transform.rotate(baguette_image, -math.degrees(angle))
            virtual_surface.blit(rotated_baguette, (baguette["x"] - 40, baguette["y"] - 40))

        # check for baguette collision
        for enemy in enemies[:]:
            if check_collision(baguette, enemy):
                if enemy in enemies:  # is enemy still in list?
                    enemies.remove(enemy)
                if baguette in thrown_baguettes:  # is baguette still in list?
                    thrown_baguettes.remove(baguette)
                score += 2

    # update enemy pos
    for enemy in enemies[:]:
        enemy_dx = player_x - enemy["x"] - map_offset_x
        enemy_dy = player_y - enemy["y"] - map_offset_y
        enemy_angle = math.atan2(enemy_dy, enemy_dx)
        enemy["x"] += math.cos(enemy_angle) * enemy_speed
        enemy["y"] += math.sin(enemy_angle) * enemy_speed

        # check if enemy collides with player
        if check_player_collision({"x": player_x, "y": player_y}, enemy):
            player_hp -= 10
            enemies.remove(enemy)
            if player_hp <= 0:
                death_screen()

        # draw enemies
        virtual_surface.blit(miku_image, (enemy["x"] + map_offset_x, enemy["y"] + map_offset_y))

    # when enemies all dead, spawn a new wave
    if not enemies:
        spawn_wave()

    # draw player
    virtual_surface.blit(teto_image, (player_x, player_y))

    # display player stats
    font = pg.font.Font(None, 50)
    hp_text = font.render(f"HP: {player_hp}", True, white)
    score_text = font.render(f"Score: {score}", True, white)
    wave_text = font.render(f"Wave: {wave_count}", True, white)
    fps_text = font.render(f"FPS: {fps_count}", True, white)
    virtual_surface.blit(hp_text, (10, 10))
    virtual_surface.blit(score_text, (10, 60))
    virtual_surface.blit(wave_text, (10, 110))
    virtual_surface.blit(fps_text, (10, 160))

    scaled_surface = pg.transform.scale(virtual_surface, (screen_width, screen_height))
    screen.blit(scaled_surface, (0, 0))
    pg.display.flip()


pg.quit()
