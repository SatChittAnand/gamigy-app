from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv

import pygame
import random
import os
import math

# --- Initialization ---
pygame.init()
pygame.mixer.init()

# --- Display Setup ---
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Temperature Control: Hypnotic Edition!")

# --- Colors & Fonts ---
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 150)
ORANGE = (255, 165, 0)
BLUE = (60, 120, 255)
RED = (255, 50, 50)
CYAN = (0, 200, 255)
BLACK = (0, 0, 0)
PINK = (255, 105, 180)
BG_COLOR = (10, 15, 30)
title_font = pygame.font.Font(None, 90)
main_font = pygame.font.Font(None, 40)
small_font = pygame.font.Font(None, 28)
HIGHSCORE_FILE = "highscore.txt"

# --- Blockchain Setup ---
load_dotenv()

RPC_URL = os.getenv("RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
SIGNER_ADDRESS = os.getenv("SIGNER_ADDRESS")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

# Web3 setup
web3 = Web3(Web3.HTTPProvider(RPC_URL))

# ABI of your deployed contract (replace with real ABI after deploy)
CONTRACT_ABI = [
    {
        "inputs": [{"internalType": "uint256", "name": "score", "type": "uint256"}],
        "name": "submitScore",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    }
]

# Fix addresses
contract = None
try:
    if CONTRACT_ADDRESS:
        CONTRACT_ADDRESS = web3.to_checksum_address(CONTRACT_ADDRESS)
        SIGNER_ADDRESS = web3.to_checksum_address(SIGNER_ADDRESS)
        contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
    else:
        print("⚠️ No contract address set, skipping on-chain score submission.")
except Exception as e:
    print(f"⚠️ Invalid address config: {e}")


# --- Asset Loading ---
try:
    original_ac_img = pygame.image.load("ac.png").convert_alpha()
    original_heater_img = pygame.image.load("heater.png").convert_alpha()
    original_fan_img = pygame.image.load("fan.png").convert_alpha()

    ac_img = pygame.transform.scale(original_ac_img, (60, 45))
    heater_img = pygame.transform.scale(original_heater_img, (70, 70))
    fast_heater_img = pygame.transform.scale(original_heater_img, (50, 50))
    fan_img = pygame.transform.scale(original_fan_img, (50, 50))

    coin_sound = pygame.mixer.Sound("collect.wav")
    hit_sound = pygame.mixer.Sound("lose.wav")
except Exception as e:
    print(f"Error loading assets: {e}. Make sure .png and .wav files are in the same folder as the script.")
    pygame.quit()
    exit()

# --- Particle & Background Classes ---
class Particle:
    def __init__(self, p_type, x, y):
        self.type = p_type
        self.x, self.y = x, y
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 6)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.color = random.choice([RED, ORANGE, YELLOW, WHITE])
        self.radius = random.randint(4, 7)
        self.life = 80
        self.gravity = 0.1

    def update_and_draw(self, surface):
        self.vy += self.gravity
        self.x += self.vx; self.y += self.vy; self.life -= 1
        self.radius -= 0.08
        if self.life > 0 and self.radius > 0:
            pygame.draw.circle(surface, self.color, (self.x, self.y), self.radius)
            return True
        return False

class Cloud:
    def __init__(self, speed, size, color):
        self.x, self.y, self.speed = random.randint(-200, screen_width), random.randint(0, screen_height), speed
        self.surface = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.circle(self.surface, color, (size[0] // 2, size[1] // 2), size[0] // 2)

    def update_and_draw(self, surface):
        self.x += self.speed
        if self.x > screen_width: self.x, self.y = -200, random.randint(0, screen_height)
        surface.blit(self.surface, (self.x, self.y))

# --- Vortex Background Setup ---
vortex_surface = pygame.Surface((screen_width * 2, screen_height * 2))
for i in range(40, 0, -1):
    color = (random.randint(10, 30), random.randint(15, 40), random.randint(20, 50))
    pygame.draw.circle(vortex_surface, color, vortex_surface.get_rect().center, i * 30)

# --- Game Settings & Variables ---
player_base_speed = 9
clock = pygame.time.Clock()
game_state = "title_screen"
fan_rotation_angle, pulse_timer, vortex_rotation_angle = 0, 0, 0
player_wobble = {'x': 1.0, 'y': 1.0, 'timer': 0}
collected_fans, game_over_particles = [], []
clouds = [Cloud(0.5, (200, 200), (20, 25, 50, 80)), Cloud(0.8, (150, 150), (25, 35, 60, 90)), Cloud(1.2, (100, 100), (30, 45, 70, 100))]

# --- High Score & Game Functions ---
def load_highscore():
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, "r") as f: return int(f.read())
        except (ValueError, TypeError): return 0
    return 0
def save_highscore(new_highscore):
    # Save locally
    with open(HIGHSCORE_FILE, "w") as f:
        f.write(str(new_highscore))

    # Try to submit on-chain
    try:
        nonce = web3.eth.get_transaction_count(SIGNER_ADDRESS)
        txn = contract.functions.submitScore(new_highscore).build_transaction({
            "from": SIGNER_ADDRESS,
            "nonce": nonce,
            "gas": 200000,
            "gasPrice": web3.to_wei("1", "gwei"),
        })
        signed_txn = web3.eth.account.sign_transaction(txn, PRIVATE_KEY)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
        print(f"✅ Submitted score {new_highscore}, tx hash: {tx_hash.hex()}")
    except Exception as e:
        print(f"⚠️ On-chain score submission failed: {e}")

high_score = load_highscore()

def reset_game():
    global ac_rect, heaters, fan_rect, score, new_high_score_achieved, lives, invincible, invincible_timer, screen_shake, blast_cooldown_timer, blast_ready, fan_rotation_angle, pulse_timer, powerup, powerup_active, powerup_type, powerup_timer, collected_fans, powerup_spawn_timer, fan_collect_count, game_over_particles, life_fan_collect_count
    ac_rect = ac_img.get_rect(center=(screen_width/2, screen_height/2))
    heaters, score, collected_fans, game_over_particles = [], 0, [], []
    spawn_heater()
    fan_rect = fan_img.get_rect(center=(random.randint(50, screen_width-50), random.randint(50, screen_height-50)))
    new_high_score_achieved, lives = False, 3
    invincible, invincible_timer, screen_shake = False, 0, 0
    blast_cooldown_timer, blast_ready = 0, True
    fan_rotation_angle, pulse_timer = 0, 0
    powerup, powerup_active, powerup_type, powerup_timer = None, False, "", 0
    powerup_spawn_timer = pygame.time.get_ticks() + random.randint(15000, 20000)
    fan_collect_count, life_fan_collect_count = 0, 0

def spawn_heater():
    heater_type = random.choice(["normal", "normal", "fast"])
    start_pos = (random.randint(0, screen_width), random.choice([-50, screen_height + 50]))
    speed = (1.5 if heater_type == "normal" else 2.5) + (score / 150)
    img = heater_img if heater_type == "normal" else fast_heater_img
    heaters.append({"rect": img.get_rect(center=start_pos), "img": img, "speed": speed, "frozen": False, "frozen_timer": 0})

def spawn_powerup(p_type):
    global powerup, powerup_spawn_timer
    if powerup is None:
        powerup = {"rect": pygame.Rect(random.randint(50, screen_width-50), random.randint(50, screen_height-50), 35, 35), "type": p_type}
        if p_type != "life" and p_type != "score_boost":
            powerup_spawn_timer = pygame.time.get_ticks() + random.randint(15000, 20000)

def draw_text(text, font, color, surface, x, y, align="center"):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    if align == "center": text_rect.center = (x, y)
    elif align == "topleft": text_rect.topleft = (x, y)
    elif align == "topright": text_rect.topright = (x, y)
    elif align == "bottomleft": text_rect.bottomleft = (x, y)
    elif align == "bottomright": text_rect.bottomright = (x, y)
    surface.blit(text_obj, text_rect)

def draw_powerup(surface, powerup_data):
    rect = powerup_data["rect"]
    ptype = powerup_data["type"]
    pygame.draw.rect(surface, BLACK, rect, border_radius=5)
    if ptype == "score_boost":
        pygame.draw.polygon(surface, YELLOW, [(rect.centerx, rect.top+5), (rect.right-7, rect.bottom-7), (rect.left+7, rect.bottom-7)])
        pygame.draw.polygon(surface, YELLOW, [(rect.centerx, rect.bottom-5), (rect.left+7, rect.top+12), (rect.right-7, rect.top+12)])
    elif ptype == "shield":
        pygame.draw.rect(surface, CYAN, rect, border_radius=5)
        pygame.draw.rect(surface, WHITE, (rect.left+5, rect.top+5, rect.width-10, rect.height-10), 4)
    elif ptype == "life":
        pygame.draw.rect(surface, PINK, rect, border_radius=5)
        pygame.draw.circle(surface, RED, (rect.centerx - 8, rect.top + 12), 8)
        pygame.draw.circle(surface, RED, (rect.centerx + 8, rect.top + 12), 8)

# --- Initialize ---
reset_game()

# --- Main Game Loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN:
            if game_state == "playing":
                if event.key == pygame.K_p: game_state = "paused"
                if (event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT) and blast_ready:
                    blast_ready, blast_cooldown_timer = False, pygame.time.get_ticks() + 10000
                    for heater in heaters: heater["frozen"], heater["frozen_timer"] = True, pygame.time.get_ticks() + 3000
            elif game_state == "paused" and event.key == pygame.K_p: game_state = "playing"
            elif game_state == "title_screen" and event.key == pygame.K_SPACE: game_state = "playing"; reset_game()
            elif game_state == "game_over" and event.key == pygame.K_r: game_state = "playing"; reset_game()

    # --- Background ---
    screen.fill(BG_COLOR)
    vortex_rotation_angle = (vortex_rotation_angle + 0.2) % 360
    rotated_vortex = pygame.transform.rotate(vortex_surface, vortex_rotation_angle)
    screen.blit(rotated_vortex, rotated_vortex.get_rect(center=screen.get_rect().center))
    for cloud in clouds: cloud.update_and_draw(screen)

    # --- Animations & Screen Shake ---
    if game_state == 'playing':
        fan_rotation_angle = (fan_rotation_angle + 5) % 360; pulse_timer += 0.1
        if player_wobble['timer'] > 0:
            player_wobble['timer'] -= 1; player_wobble['x'] += (1.0 - player_wobble['x']) * 0.1; player_wobble['y'] += (1.0 - player_wobble['y']) * 0.1
    render_offset = [0, 0]
    if screen_shake > 0: screen_shake -= 1; render_offset = [random.randint(-8, 8), random.randint(-8, 8)]

    # --- Game Logic ---
    if game_state == 'playing':
        moved_x, moved_y = False, False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and ac_rect.left > 0: ac_rect.x -= player_base_speed; moved_x = True
        if keys[pygame.K_RIGHT] and ac_rect.right < screen_width: ac_rect.x += player_base_speed; moved_x = True
        if keys[pygame.K_UP] and ac_rect.top > 0: ac_rect.y -= player_base_speed; moved_y = True
        if keys[pygame.K_DOWN] and ac_rect.bottom < screen_height: ac_rect.y += player_base_speed; moved_y = True
        if moved_x: player_wobble = {'x': 1.3, 'y': 0.7, 'timer': 15}
        elif moved_y: player_wobble = {'x': 0.7, 'y': 1.3, 'timer': 15}

        is_invincible = (invincible and pygame.time.get_ticks() < invincible_timer) or (powerup_active and powerup_type == 'shield')

        for heater in heaters:
            if heater["frozen"] and pygame.time.get_ticks() > heater["frozen_timer"]: heater["frozen"] = False
            if not heater["frozen"]:
                if ac_rect.centerx > heater["rect"].centerx: heater["rect"].x += heater["speed"]
                else: heater["rect"].x -= heater["speed"]
                if ac_rect.centery > heater["rect"].centery: heater["rect"].y += heater["speed"]
                else: heater["rect"].y -= heater["speed"]
            if ac_rect.colliderect(heater["rect"]) and not is_invincible:
                hit_sound.play(); lives -= 1; invincible = True
                invincible_timer = pygame.time.get_ticks() + 2000; screen_shake = 20
                if lives <= 0:
                    save_highscore(high_score); game_state = "game_over"
                    for _ in range(100): game_over_particles.append(Particle('firework', x=ac_rect.centerx, y=ac_rect.centery))

        if invincible and pygame.time.get_ticks() > invincible_timer: invincible = False
        if not blast_ready and pygame.time.get_ticks() > blast_cooldown_timer: blast_ready = True
        if powerup_active and pygame.time.get_ticks() > powerup_timer: powerup_active = False
        if powerup is None and pygame.time.get_ticks() > powerup_spawn_timer: spawn_powerup("shield")

        if ac_rect.colliderect(fan_rect):
            fan_collect_count += 1; life_fan_collect_count += 1
            points = 30 if powerup_active and powerup_type == 'score_boost' else 10
            score += points; coin_sound.play()
            collected_fans.append({'rect': fan_rect.copy(), 'alpha': 255, 'scale': 1.0})
            if score > high_score: high_score = score; new_high_score_achieved = True
            if score > 0 and score % 70 == 0: spawn_heater()
            if fan_collect_count >= 6: spawn_powerup("score_boost"); fan_collect_count = 0
            if life_fan_collect_count >= 10 and lives < 3: spawn_powerup("life"); life_fan_collect_count = 0
            fan_rect.center = (random.randint(50, screen_width-50), random.randint(50, screen_height-50))

        if powerup and ac_rect.colliderect(powerup["rect"]):
            if powerup["type"] == "life":
                if lives < 3: lives += 1
            else:
                powerup_active, powerup_type, powerup_timer = True, powerup["type"], pygame.time.get_ticks() + 6000
            powerup = None

        # --- Drawing Gameplay ---
        for collected in collected_fans[:]:
            collected['scale'] += 0.1; collected['alpha'] -= 15
            if collected['alpha'] <= 0: collected_fans.remove(collected)
            else:
                pop_img = pygame.transform.scale(fan_img, (int(fan_img.get_width()*collected['scale']), int(fan_img.get_height()*collected['scale'])))
                pop_img.set_alpha(collected['alpha']); screen.blit(pop_img, pop_img.get_rect(center=collected['rect'].center))
        rotated_fan = pygame.transform.rotate(fan_img, fan_rotation_angle)
        screen.blit(rotated_fan, rotated_fan.get_rect(center=fan_rect.center))
        if powerup: draw_powerup(screen, powerup)
        for heater in heaters:
            pulse_scale = 1.0 + math.sin(pulse_timer) * 0.1
            pulsed_img = pygame.transform.scale(heater["img"], (int(heater["rect"].width*pulse_scale), int(heater["rect"].height*pulse_scale)))
            img = pulsed_img.copy()
            if heater["frozen"]: img.fill((0, 100, 200, 150), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(img, img.get_rect(center=heater["rect"].center))
        wobbled_ac = pygame.transform.scale(ac_img, (int(ac_img.get_width()*player_wobble['x']), int(ac_img.get_height()*player_wobble['y'])))
        if not (invincible and (pygame.time.get_ticks() // 150) % 2 == 0):
            screen.blit(wobbled_ac, wobbled_ac.get_rect(center=ac_rect.center))
        if powerup_active and powerup_type == 'shield':
            shield_surf = pygame.Surface((ac_rect.width + 20, ac_rect.height + 20), pygame.SRCALPHA)
            pygame.draw.circle(shield_surf, (CYAN[0], CYAN[1], CYAN[2], 100), shield_surf.get_rect().center, shield_surf.get_width()//2)
            screen.blit(shield_surf, shield_surf.get_rect(center=ac_rect.center))

    # --- Drawing Menus ---
    elif game_state == 'title_screen':
        draw_text("Temperature Control!", title_font, BLUE, screen, screen_width/2, screen_height/3)
        draw_text(f"High Score: {high_score}", main_font, YELLOW, screen, screen_width/2, screen_height/2)
        draw_text("Press SPACE to Start", main_font, WHITE, screen, screen_width/2, screen_height/2 + 60)
    elif game_state == 'paused':
        draw_text("PAUSED", title_font, ORANGE, screen, screen_width/2, screen_height/2 - 50)
        draw_text("Press 'P' to Resume", main_font, WHITE, screen, screen_width/2, screen_height/2 + 40)
    elif game_state == 'game_over':
        game_over_particles = [p for p in game_over_particles if p.update_and_draw(screen)]
        if not game_over_particles:
            draw_text("GAME OVER", title_font, RED, screen, screen_width/2, screen_height/3)
            if new_high_score_achieved: draw_text("New High Score!", main_font, GREEN, screen, screen_width/2, screen_height/2 - 50)
            draw_text(f"Your Score: {score}", main_font, WHITE, screen, screen_width/2, screen_height/2)
            draw_text("Press 'R' to Restart", main_font, WHITE, screen, screen_width/2, screen_height/2 + 100)

    # --- UI in Corners ---
    if game_state == 'playing':
        draw_text(f"SCORE: {score}", main_font, WHITE, screen, 10, 10, align="topleft")
        draw_text(f"HIGH SCORE: {high_score}", main_font, YELLOW, screen, screen_width - 10, 10, align="topright")
        for i in range(lives): screen.blit(pygame.transform.scale(ac_img, (35,25)), (10 + i * 40, screen_height - 40))
        if not blast_ready:
            remaining_cd = (blast_cooldown_timer - pygame.time.get_ticks()) // 1000
            draw_text(f"Blast: {remaining_cd+1}s", small_font, RED, screen, screen_width - 10, screen_height - 10, align="bottomright")
        else:
            draw_text("Blast: READY", small_font, CYAN, screen, screen_width - 10, screen_height - 10, align="bottomright")
        if powerup_active:
            p_color = YELLOW if powerup_type == 'score_boost' else (CYAN if powerup_type == 'shield' else BLUE)
            draw_text(f"{powerup_type.replace('_',' ').upper()}!", small_font, p_color, screen, screen_width/2, 10)
        if lives < 3:
            draw_text(f"Fans for Life: {life_fan_collect_count}/10", small_font, PINK, screen, 10, screen_height - 70, align="bottomleft")

    pygame.display.flip()
    clock.tick(60)

pygame.quit()