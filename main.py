#    _       _                         _          _      _              _             _ 
#    | |_ ___| |_ ___   ____  _ _ ___ _(_)_ ____ _| |  __| |_  __ _ _ __| |_ ___ _ _  / |
#    |  _/ -_)  _/ _ \ (_-< || | '_\ V / \ V / _` | | / _| ' \/ _` | '_ \  _/ -_) '_| | |
#    \__\___|\__\___/ /__/\_,_|_|  \_/|_|\_/\__,_|_| \__|_||_\__,_| .__/\__\___|_|   |_|
#                                                                |_|                                                                              


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

VIRTUAL_WIDTH = screen_width
VIRTUAL_HEIGHT = screen_height
virtual_surface = pg.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))



# ----------- LOADING MUSIC ----------- #

# init mixer
# init mixer with error handling for environments without audio
audio_available = True
try:
    pg.mixer.init()
except pg.error:
    print("Audio device not available - running without sound")
    audio_available = False

# event for when current track ends
TRACK_END = pg.USEREVENT + 1
if audio_available:
    pg.mixer.music.set_endevent(TRACK_END)

def play_music():
    if audio_available and settings.get("music", True):
        play_next()
    else:
        if audio_available:
            pg.mixer.music.stop()

tracks = ["data/ochamekinou.mp3", "data/tetoterritory.mp3"]
r.shuffle(tracks)
track_iter = iter(tracks)

def play_next():
    if not audio_available:
        return
    global track_iter, tracks
    try:
        next_track = next(track_iter)
    except StopIteration:
        r.shuffle(tracks)
        track_iter = iter(tracks)
        next_track = next(track_iter)
    pg.mixer.music.load(next_track)
    pg.mixer.music.play()






# ----------- LOADING ASSETS ----------- #

# sprites loading

def load_sprite(imgname, filetype):
    sprite = pg.image.load("data/" + imgname + "." + filetype).convert_alpha()
    return sprite

teto_image = load_sprite("teto", "webp")
miku_image = load_sprite("miku", "webp")
neru_image = load_sprite("neru", "webp")
defoko_image = load_sprite("defoko", "png")
momone_image = load_sprite("momone", "png")
diva_image = load_sprite("diva", "png")
baguette_image = load_sprite("baguette", "webp")

""" # old img load
teto_image = pg.image.load("data/teto.webp").convert_alpha()
miku_image = pg.image.load("data/miku.webp").convert_alpha()
neru_image = pg.image.load("data/neru.webp").convert_alpha()
defoko_image = pg.image.load("data/defoko.png").convert_alpha()
momone_image = pg.image.load("data/momone.png").convert_alpha()
diva_image = pg.image.load("data/diva.png").convert_alpha()
baguette_image = pg.image.load("data/baguette.webp").convert_alpha()
"""

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

def complementary(x):
    highest = 255
    result = highest - x
    return result

a2 = complementary(a)
b2 = complementary(b)
c2 = complementary(c)


# ----------- STORY AND DIALOGUE SYSTEM ----------- #

# Story state
story_active = False
current_dialogue_index = 0
current_story_wave = 0
waiting_for_click = False

# Story dialogue data
story_dialogue = {
    2: [
        "Neru: *ring ring*",
        "Neru: \"Teto! Can you hear me?\"",
        "Neru: \"Finally! Where have you been??\"",
        "Neru: \"You didn't answer any of my calls!\"",
        "Neru: \"...That's besides the point now, anyway. Have you seen Miku?\"",
        "Neru: \"I don't know what happened, but...\"",
        "Neru: \"She's acting a little odd right now. I think we should just give her some space...\"",
        "Neru: *beep*",
        "Miku: \"...\"",
        "Miku: \"..!\""
    ],
    10: [
        "Neru: *ring ring*",
        "Neru: \"Teto!!\"",
        "Neru: \"I think I left my baguette-shotgun back behind the concert hall!\"",
        "Neru: \"You're still there, right?\"",
        "Neru: \"Would you mind bringing it back to me?\"",
        "Neru: \"I don't mind if you use it if you need to!\"",
        "Neru: \"Press Q to switch weapons!\"",
        "Neru: \"Stay safe!!\""
        "Neru: *beep*",
    ],
    15: [
        "Neru: *beep*",
        "Neru: \"Hey Teto! Guess who's with me?\"",
        "Momo: \"Teto!!!\"",
        "Defoko: \"We're still here, Teto! Don't worry about us!\"",
        "Neru: \"I found Momo and Defoko! They're alright, they were just lost!\"",
        "Defoko: \"Are you nearly back, Teto? What's the hold up?\"",
        "Momo: *static*"
    ],
    20: [
        "Miku: \"...\"",
        "Miku: \"Te...\"",
        "Diva: \"Tet...\"",
        "Miku: \"...\"",
        "Diva: \"Teto.\""
    ],
    25: [
        "Teto: \"What is that feeling?\"",
        "Teto: \"Something's watching me...\""
    ],
    30: [
        "Neru: *ring ring*",
        "Neru: \"Teto! It's me again, Neru!\"",
        "Neru: \"Something's horribly wrong with Miku!\"",
        "Diva: \"...\"",
        "Neru: \"I... I don't know what happened, but stay away from her!\"",
        "Defoko: \"Did you guys hear that too?\"",
        "Momo: \"Hear what?\"",
        "Neru: \"Is that?!---\"",
        "Neru: *beeeeep*"
    ],
    35: [
        "Teto: \"...The Mikus wont stop coming....\"",
        "Teto: \"The air feels... suffocating. Even more so than that horde...\""
    ],
    40: [
        "Diva: *heavy breathing*",
        "Teto: \"!!!\""
    ]
}

# NPC sprite
current_npc_sprite = None

# ----------- WEAPON SYSTEM ----------- #

# Weapon types
WEAPON_SINGLE = "single"
WEAPON_SHOTGUN = "shotgun"

# Current weapon
current_weapon = WEAPON_SINGLE
weapon_unlocked_shotgun = True

# Weapon stats
weapon_stats = {
    WEAPON_SINGLE: {
        "projectile_count": 1,
        "spread_angle": 0,
        "cooldown": 1.0,
    },
    WEAPON_SHOTGUN: {
        "projectile_count": 5,
        "spread_angle": 0.3,
        "cooldown": 1.5,
    }
}

# ----------- BOSS SYSTEM ----------- #

boss_active = False
boss_data = None

# ----------- LOADING GAME VARIABLES ----------- #

# player settings
player_size = 80
player_x = VIRTUAL_WIDTH // 2 - player_size // 2
player_y = VIRTUAL_HEIGHT // 2 - player_size // 2
player_speed = 2
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
wave_count = 38
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



# ----------- STORY FUNCTIONS ----------- #

def start_story_sequence(wave):
    """Start a story dialogue sequence for the given wave."""
    global story_active, current_dialogue_index, current_story_wave, waiting_for_click, current_npc_sprite
    
    if wave in story_dialogue:
        story_active = True
        current_dialogue_index = 0
        current_story_wave = wave
        waiting_for_click = True
        
        # Set NPC sprite based on the speaker
        dialogue = story_dialogue[wave][0]
        if "Teto:" in dialogue:
            current_npc_sprite = teto_image
        elif "Miku:" in dialogue:
            current_npc_sprite = miku_image
        elif "Neru:" in dialogue:
            current_npc_sprite = neru_image
        elif "Momo:" in dialogue:
            current_npc_sprite = momone_image
        elif "Defoko:" in dialogue:
            current_npc_sprite = defoko_image
        elif "Diva:" in dialogue:
            current_npc_sprite = diva_image
        else:
            current_npc_sprite = neru_image

def handle_dialogue_click():
    """Handle left click during dialogue."""
    global current_dialogue_index, story_active, waiting_for_click, weapon_unlocked_shotgun, current_npc_sprite
    
    current_dialogue_index += 1
    
    # Check if we've shown all dialogue for this wave
    if current_dialogue_index >= len(story_dialogue[current_story_wave]):
        story_active = False
        waiting_for_click = False
        current_dialogue_index = 0
        
        # Special actions for specific waves
        if current_story_wave == 10:
            weapon_unlocked_shotgun = True
            
        return True  # Dialogue finished
    else:
        # Update NPC sprite for next dialogue
        dialogue = story_dialogue[current_story_wave][current_dialogue_index]
        if "Teto:" in dialogue:
            current_npc_sprite = teto_image
        elif "Miku:" in dialogue:
            current_npc_sprite = miku_image
        elif "Neru:" in dialogue:
            current_npc_sprite = neru_image
        elif "Momo:" in dialogue:
            current_npc_sprite = momone_image
        elif "Defoko:" in dialogue:
            current_npc_sprite = defoko_image
        elif "Diva:" in dialogue:
            current_npc_sprite = diva_image
        
        return False  # More dialogue to show

def draw_dialogue():
    """Draw the current dialogue and NPC sprite."""
    if not story_active:
        return
        
    # Draw dialogue box background
    dialogue_box = pg.Rect(20, VIRTUAL_HEIGHT - 150, VIRTUAL_WIDTH - 40, 130)
    pg.draw.rect(virtual_surface, black, dialogue_box)
    pg.draw.rect(virtual_surface, white, dialogue_box, 3)
    
    # Draw NPC sprite in bottom left
    if current_npc_sprite:
        npc_rect = pg.Rect(30, VIRTUAL_HEIGHT - 140, 100, 100)
        npc_scaled = pg.transform.scale(current_npc_sprite, (100, 100))
        virtual_surface.blit(npc_scaled, npc_rect)
    
    # Draw dialogue text
    dialogue_text = story_dialogue[current_story_wave][current_dialogue_index]
    font = pg.font.Font(None, 36)
    
    # Word wrap the text
    words = dialogue_text.split(' ')
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] < VIRTUAL_WIDTH - 180:  # Leave space for NPC sprite
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word + " "
    
    if current_line:
        lines.append(current_line)
    
    # Draw text lines
    y_offset = VIRTUAL_HEIGHT - 130
    for line in lines:
        text_surface = font.render(line.strip(), True, white)
        virtual_surface.blit(text_surface, (150, y_offset))
        y_offset += 30
    
    # Draw continue indicator
    continue_text = font.render("Click to continue...", True, (200, 200, 200))
    virtual_surface.blit(continue_text, (VIRTUAL_WIDTH - 200, VIRTUAL_HEIGHT - 30))

# ----------- WEAPON FUNCTIONS ----------- #

def switch_weapon():
    """Switch between available weapons."""
    global current_weapon
    
    if not weapon_unlocked_shotgun:
        return  # Can't switch if shotgun not unlocked
    
    if current_weapon == WEAPON_SINGLE:
        current_weapon = WEAPON_SHOTGUN
    else:
        current_weapon = WEAPON_SINGLE

def get_current_weapon_stats():
    """Get stats for the current weapon."""
    return weapon_stats[current_weapon]

def fire_weapon(angle, start_x, start_y):
    """Fire the current weapon and return projectiles to add."""
    stats = get_current_weapon_stats()
    projectiles = []

    count = stats["projectile_count"]
    spread = stats["spread_angle"]

    for i in range(count):
        if count == 1:
            # Single shot
            proj_angle = angle
        else:
            # Multiple shots with spread
            offset = (i - (count - 1) / 2) * spread
            proj_angle = angle + offset

        dx = math.cos(proj_angle) * proj_speed
        dy = math.sin(proj_angle) * proj_speed

        projectiles.append({
            "x": start_x,
            "y": start_y,
            "dx": dx,
            "dy": dy,
            "life": proj_lifetime
        })

    return projectiles

# ----------- BOSS FUNCTIONS ----------- #

def spawn_boss():
    """Spawn a boss enemy."""
    global boss_active, boss_data
    
    boss_active = True
    boss_data = {
        "x": r.randint(-1000, 1000),
        "y": r.randint(-1000, 1000),
        "hp": 50,
        "max_hp": 50,
        "size": 120,  # Larger than normal enemies
        "speed": enemy_speed * 0.7,  # Slower but tankier
        "last_attack_time": 0,
        "attack_cooldown": 3.0,
        "last_player_hit_time": 0,
        "player_hit_cooldown": 2.0
    }

def update_boss():
    """Update boss behavior."""
    if not boss_active or not boss_data:
        return
    
    # Move toward player
    boss_dx = player_x - boss_data["x"] - map_offset_x
    boss_dy = player_y - boss_data["y"] - map_offset_y
    boss_angle = math.atan2(boss_dy, boss_dx)
    
    boss_data["x"] += math.cos(boss_angle) * boss_data["speed"]
    boss_data["y"] += math.sin(boss_angle) * boss_data["speed"]
    
    # Boss special attack (spawn additional enemies periodically)
    current_time = t.time()
    if current_time - boss_data["last_attack_time"] >= boss_data["attack_cooldown"]:
        boss_data["last_attack_time"] = current_time
        # Spawn 3 additional enemies around the boss
        for _ in range(3):
            angle = r.uniform(0, 2 * math.pi)
            distance = 200
            enemy_x = boss_data["x"] + math.cos(angle) * distance
            enemy_y = boss_data["y"] + math.sin(angle) * distance
            enemies.append({"x": enemy_x, "y": enemy_y, "hp": 1})

def draw_boss():
    """Draw the boss enemy."""
    if not boss_active or not boss_data:
        return
    
    # Draw boss (scaled up miku sprite)
    boss_sprite = pg.transform.scale(diva_image, (boss_data["size"], boss_data["size"]))
    boss_x = boss_data["x"] + map_offset_x
    boss_y = boss_data["y"] + map_offset_y
    virtual_surface.blit(boss_sprite, (boss_x, boss_y))
    
    # Draw boss health bar
    bar_width = 300
    bar_height = 20
    bar_x = (VIRTUAL_WIDTH - bar_width) // 2
    bar_y = 50
    
    # Background
    pg.draw.rect(virtual_surface, red, (bar_x, bar_y, bar_width, bar_height))
    
    # Health
    health_ratio = boss_data["hp"] / boss_data["max_hp"]
    health_width = int(bar_width * health_ratio)
    pg.draw.rect(virtual_surface, green, (bar_x, bar_y, health_width, bar_height))
    
    # Border
    pg.draw.rect(virtual_surface, white, (bar_x, bar_y, bar_width, bar_height), 2)
    
    # Boss name
    font = pg.font.Font(None, 36)
    boss_text = font.render("DIVA MIKU", True, white)
    text_x = (VIRTUAL_WIDTH - boss_text.get_width()) // 2
    virtual_surface.blit(boss_text, (text_x, bar_y - 30))

def check_boss_collision(projectile):
    """Check if projectile hits the boss."""
    global boss_active
    if not boss_active or not boss_data:
        return False
    
    proj_rect = pg.Rect(
        projectile["x"] + map_offset_x - 40,
        projectile["y"] + map_offset_y - 40, 
        80, 
        80
        )
    boss_rect = pg.Rect(
        boss_data["x"] + map_offset_x,
        boss_data["y"] + map_offset_y,
        boss_data["size"],
        boss_data["size"]
    )

    
    if proj_rect.colliderect(boss_rect):
        boss_data["hp"] -= 5  # Bosses take more hits
        if boss_data["hp"] <= 0:
            handle_boss_death()
            return True
        return True
    return False

def check_boss_player_collision():
    """Check if boss collides with player."""

    if not boss_active or not boss_data:
        return False
    
    player_rect = pg.Rect(player_x, player_y, player_size, player_size)
    boss_rect = pg.Rect(
        boss_data["x"] + map_offset_x, 
        boss_data["y"] + map_offset_y, 
        boss_data["size"], 
        boss_data["size"]
    )
    
    return player_rect.colliderect(boss_rect)

def handle_boss_death():
    global boss_active
    boss_active = False
    victory_screen()


# ----------- LOADING UI ----------- #

def get_virtual_mouse_pos():
    mouse_x, mouse_y = pg.mouse.get_pos()
    scale_x = VIRTUAL_WIDTH / screen_width
    scale_y = VIRTUAL_HEIGHT / screen_height
    return int(mouse_x * scale_x), int(mouse_y * scale_y)



# credits screen
def credits_screen():
    """Display the credits screen."""
    global screen_width, screen_height, screen
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
    global screen_width, screen_height, screen
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
    global screen_width, screen_height, screen
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

def continue_after_dialogue():
    """Continue with wave spawning after dialogue finishes."""
    global wave_count

    wave_count += 1
    
    # Now spawn the actual wave
    if wave_count >= 40 and wave_count % 10 == 0 and not boss_active:
        spawn_boss()
    else:
        enemy_count = 5 + wave_count
        for _ in range(enemy_count):
            x = r.randint(-1500, 1500)
            y = r.randint(-1500, 1500)
            enemies.append({"x": x, "y": y, "hp": 1})

def end_after_boss():
    if wave_count > 40 and boss_active == False:
        victory_screen()
    else:
        pass

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
    virtual_surface.blit(death_text, (VIRTUAL_WIDTH // 2 - death_text.get_width() // 2, VIRTUAL_HEIGHT // 2 - 100))
    virtual_surface.blit(score_text, (VIRTUAL_WIDTH // 2 - score_text.get_width() // 2, VIRTUAL_HEIGHT // 2))
    virtual_surface.blit(wave_text, (VIRTUAL_WIDTH // 2 - wave_text.get_width() // 2, VIRTUAL_HEIGHT // 2 + 100))
    scaled = pg.transform.scale(virtual_surface, (screen_width, screen_height))
    screen.blit(scaled, (0, 0))

    pg.display.flip()
    t.sleep(3)
    pg.quit()
    sys.exit()

def victory_screen():
    font = pg.font.Font(None, 100)
    win_text = font.render("Teto Survived the Diva Attack!", True, green)
    score_text = font.render(f"Final Score: {score}", True, white)
    wave_text = font.render(f"Waves Survived: {wave_count}", True, white)

    virtual_surface.fill(black)
    virtual_surface.blit(win_text, (VIRTUAL_WIDTH // 2 - win_text.get_width() // 2, VIRTUAL_HEIGHT // 2 - 100))
    virtual_surface.blit(score_text, (VIRTUAL_WIDTH // 2 - score_text.get_width() // 2, VIRTUAL_HEIGHT // 2))
    virtual_surface.blit(wave_text, (VIRTUAL_WIDTH // 2 - wave_text.get_width() // 2, VIRTUAL_HEIGHT // 2 + 100))
    scaled = pg.transform.scale(virtual_surface, (screen_width, screen_height))
    screen.blit(scaled, (0, 0))

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


    # prepare splash text
    font = pg.font.Font(None, 200)
    text_trip = font.render("Trip", True, neruyellow).convert_alpha()
    text_leNe = font.render("le Ne", True, mikublue).convert_alpha()
    text_wgen = font.render("wgen", True, tetored).convert_alpha()

    # calculate total width and starting x position
    total_width = text_trip.get_width() + text_leNe.get_width() + text_wgen.get_width()
    start_x = VIRTUAL_WIDTH // 2 - total_width // 2
    text_y = VIRTUAL_HEIGHT // 2 + 200



    # fade in
    for alpha in range(0, 256, 5):
        splash.set_alpha(alpha)
        text_trip.set_alpha(alpha)
        text_leNe.set_alpha(alpha)
        text_wgen.set_alpha(alpha)

        virtual_surface.fill((0, 0, 0))
        virtual_surface.blit(splash, (0, 0))
        virtual_surface.blit(text_trip, (start_x, text_y))
        virtual_surface.blit(text_leNe, (start_x + text_trip.get_width(), text_y))
        virtual_surface.blit(text_wgen, (start_x + text_trip.get_width() + text_leNe.get_width(), text_y))

        scaled = pg.transform.scale(virtual_surface, (screen_width, screen_height))
        screen.blit(scaled, (0, 0))
        pg.display.flip()
        clock.tick(30)

    # 2 second hold
    t.sleep(2)

    # fade out
    for alpha in range(255, -1, -5):
        splash.set_alpha(alpha)
        text_trip.set_alpha(alpha)
        text_leNe.set_alpha(alpha)
        text_wgen.set_alpha(alpha)

        virtual_surface.fill((0, 0, 0))
        virtual_surface.blit(splash, (0, 0))
        virtual_surface.blit(text_trip, (start_x, text_y))
        virtual_surface.blit(text_leNe, (start_x + text_trip.get_width(), text_y))
        virtual_surface.blit(text_wgen, (start_x + text_trip.get_width() + text_leNe.get_width(), text_y))

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
        elif event.type == pg.MOUSEBUTTONDOWN and story_active:
            finished = handle_dialogue_click()
            if finished:
                continue_after_dialogue()
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_q:
                switch_weapon()

    clock.tick()
    fps = clock.get_fps()
    fps_count = show_fps(fps)

    if not story_active:
        keys = pg.key.get_pressed()  # wasd keypresses
        if keys[pg.K_a]:
            map_offset_x += player_speed
        if keys[pg.K_d]:
            map_offset_x -= player_speed
        if keys[pg.K_w]:
            map_offset_y += player_speed
        if keys[pg.K_s]:
            map_offset_y -= player_speed

    virtual_surface.fill((a2, b2, c2))  # screen bg -- complementary colours to abc

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
        stats = get_current_weapon_stats()
        if current_time - last_throw_time >= stats["cooldown"]:
            last_throw_time = current_time
            new_projectiles = fire_weapon(angle, player_x + player_size // 2, player_y + player_size // 2)
            thrown_baguettes.extend(new_projectiles)

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

        

    if not story_active:
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
    if not enemies and not story_active and not boss_active:
        next_wave = wave_count + 1
        if next_wave in story_dialogue:
            start_story_sequence(next_wave)
        else:
            spawn_wave()

    # draw player
    virtual_surface.blit(teto_image, (player_x, player_y))

    if boss_active:
        update_boss()
        draw_boss()
        print("Active")
        if check_boss_player_collision():
            current_time = t.time()
            if current_time - boss_data["last_player_hit_time"] >= boss_data["player_hit_cooldown"]:
                boss_data["last_player_hit_time"] = current_time
                player_hp -= 20
                if player_hp <= 0:
                    death_screen()
        if check_boss_collision(baguette) == True:
            print("Hit")
            if baguette in thrown_baguettes:
                thrown_baguettes.remove(baguette)
            score += 10

    end_after_boss()


    # display player stats
    font = pg.font.Font(None, 50)
    hp_text = font.render(f"HP: {player_hp}", True, white).convert_alpha()
    score_text = font.render(f"Score: {score}", True, white).convert_alpha()
    wave_text = font.render(f"Wave: {wave_count}", True, white).convert_alpha()
    fps_text = font.render(f"FPS: {fps_count}", True, white).convert_alpha()
    weapon_text = font.render(f"Weapon: {current_weapon.upper()}", True, white).convert_alpha()
    virtual_surface.blit(hp_text, (10, 10))
    virtual_surface.blit(score_text, (10, 60))
    virtual_surface.blit(wave_text, (10, 110))
    virtual_surface.blit(fps_text, (10, 160))
    if weapon_unlocked_shotgun == False:
        pass
    else:
        virtual_surface.blit(weapon_text, (10, 210))


    if story_active:
        draw_dialogue()
    scaled_surface = pg.transform.scale(virtual_surface, (screen_width, screen_height))
    screen.blit(scaled_surface, (0, 0))
    pg.display.flip()




pg.quit()
