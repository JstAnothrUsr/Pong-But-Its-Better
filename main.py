import random
import sys
import pygame
import time
import math
import json

pygame.init()
pygame.mixer.init()

# WINDOW
window_width = 1000
window_height = 600
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Pong But Its Better")
window_top = 0
window_bottom = window_height
window_left = 0
window_right = window_width

# BLACK HOLES
black_holes = []
teleports = 0

# GOING BLIND
vision_time_defined = False
blind_time_defined = False
sight_status = "Vision"
vision_time = 60
blind_time = 60
sight_cooldown = []

# TIMER
start_time = pygame.time.get_ticks()
total_time = 60000
timing = True
paused_at = 0
pause_duration = 0
total_paused_time = 0
overtime = False
clocks = []
clock_hits = 0

# LAG
input_list_p1 = []
input_list_p2 = []

# COLORS
white = (255, 255, 255)
black = (0, 0, 0)
grey = (200, 200, 200)
orange = (230, 138, 0)
red = (255, 0, 0)
blue = (51, 51, 255)
green = (0, 255, 0)

# UNLOCK DIFFICULTIES
difficulties_unlocked = 0

# PAUSE BUTTON
pause_button_rect = pygame.Rect(5, 5, 20, 20)
pause_button_clicked = False

# SOUND FX
Background_Music = pygame.mixer.Sound("BG Music 2.mp3")
Background_Music.play(loops=50000000)
Background_Music.set_volume(0.7)

# PADDLE DIMENSION
paddle_width = 14
paddle_height = 75

# PADDLE POSITIONS
player_x = 50
player_y = 263

comp_x = 950
comp_y = 263

# BALL
ball_x = 500
ball_y = 300
ball_stuck = 0

ball_x_speed = random.randint(-5, 5)
ball_y_speed = random.randint(-5, 5)
while -2 <= ball_x_speed <= 2:
    ball_x_speed = random.randint(-5, 5)

# GAME LOOP
playing = True
mid_game = False
clock = pygame.time.Clock()
fps = 60

# SETTINGS
selected_difficulty = 0
selected_points = 5
selected_players = 0
selected_mode = 0
modes = ["Normal", "Confused Keyboard", "Black Holes", "Mini Mode", "Going Blind?", "Enter the Matrix", "Light Lag", "McDonald's Lag", "Moon Lag", "Mars Lag", "Time Attack"]

# PADDLE MOVEMENT
player_move_up = False
player_move_down = False
player2_move_up = False
player2_move_down = False

player1_movement_speed = 5
player2_movement_speed = 5
comp_movement_speed = 3

# SCORE VARIABLES
player_score = 0
comp_score = 0
points_to_win = 21

# TIME WARP
time_warp_ready_p1 = False
time_warp_ready_p2 = False
time_warped_by_p1 = False
time_warped_by_p2 = False
time_warp_cooldown_p1 = []
time_warp_cooldown_p2 = []

# SCORE FONT
score_font = pygame.font.Font('Atari.TTF', 20)
tutorial_font = pygame.font.Font('Atari.TTF', 15)

# BALL RESPAWN TIMER
respawn_time = 1.5
ball_respawn_timer = None

# GAME OVER SCREEN
game_over = False

# TUTORIAL
tutorial = True

def save_game():
    data = {
        "difficulties_unlocked": int(difficulties_unlocked),
        "selected_difficulty": int(selected_difficulty),
        "selected_players": int(selected_players),
        "selected_points": int(selected_points),
        "selected_mode": int(selected_mode),
    }
    with open("game_progress.json", "w") as f:
        json.dump(data, f)

def load_game():
    global difficulties_unlocked, selected_difficulty, selected_players, selected_points, selected_mode
    try:
        with open("game_progress.json", "r") as f:
            loaded_data = json.load(f)
            difficulties_unlocked = int(loaded_data.get("difficulties_unlocked", 0))
            selected_difficulty = int(loaded_data.get("selected_difficulty", 0))
            selected_players = int(loaded_data.get("selected_players", 0))
            selected_points = int(loaded_data.get("selected_points", 0))
            selected_mode = int(loaded_data.get("selected_mode", 0))
    except FileNotFoundError:
        # If the file doesn't exist, set all variables to default values.
        difficulties_unlocked = 0
        selected_difficulty = 0
        selected_points = 5
        selected_players = 0
        selected_mode = 0

load_game()

def angle_from_collision(next_ball_x, next_ball_y):
    global ball_x_speed, ball_y_speed

    player_paddle_rect = pygame.Rect(player_x, player_y, paddle_width, paddle_height)
    collision = player_paddle_rect.collidepoint(next_ball_x, next_ball_y)

    if collision:
        ball_x_speed = -1 * (ball_x - (paddle_width + player_x))

    if ball_x_speed >= 8 or ball_y_speed >= 8:
        ball_x_speed = 0.9 * ball_x_speed
        ball_y_speed = 0.9 * ball_y_speed

    if collision:
        paddle_center_x = player_x
        paddle_center_y = player_y + paddle_height / 2
        dist_x = next_ball_x - paddle_center_x
        dist_y = next_ball_y - paddle_center_y
        ball_x_speed = dist_x * 0.25 + 5
        ball_y_speed = dist_y * 0.25

def angle_from_collision_computer(next_ball_x, next_ball_y):
    global ball_x_speed, ball_y_speed

    comp_paddle_rect = pygame.Rect(comp_x, comp_y, paddle_width, paddle_height)
    collision = comp_paddle_rect.collidepoint(next_ball_x, next_ball_y)

    if collision:
        ball_x_speed = comp_x - ball_x

    while ball_x_speed >= 8 or ball_y_speed >= 8:
        ball_x_speed = 0.9 * ball_x_speed
        ball_y_speed = 0.9 * ball_y_speed

    if collision:
        paddle_center_x = comp_x + paddle_width
        paddle_center_y = comp_y + paddle_height / 2
        dist_x = paddle_center_x - next_ball_x
        dist_y = next_ball_y - paddle_center_y
        ball_x_speed = dist_x * -0.25 - 5
        ball_y_speed = dist_y * 0.25

def create_black_holes():
    global black_holes

    black_holes = []

    # Generate positions for two black holes without overlap
    for i in range(2):
        while True:
            x = random.randint(100, window_width - 100)
            y = random.randint(100, window_height - 100)
            radius = 75  # Adjust the range of radius as needed
            threshold = radius * 2  # Set the threshold based on the radius

            overlapping = False
            for black_hole in black_holes:
                distance = math.sqrt((black_hole['x'] - x) ** 2 + (black_hole['y'] - y) ** 2)
                if distance < 2 * black_hole['threshold']:  # Check if distance is less than twice the threshold
                    overlapping = True
                    break

            if not overlapping:
                black_hole = {
                    'x': x,
                    'y': y,
                    'mass': random.uniform(0.5, 2.0),
                    'threshold': threshold
                }
                black_holes.append(black_hole)
                break

def lines_intersect(line1_start, line1_end, line2_start, line2_end):
    x1, y1 = line1_start
    x2, y2 = line1_end
    x3, y3 = line2_start
    x4, y4 = line2_end

    # Calculate the cross products
    cross_product1 = (x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)
    cross_product2 = (x4 - x3) * (y2 - y3) - (y4 - y3) * (x2 - x3)
    cross_product3 = (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1)
    cross_product4 = (x2 - x1) * (y4 - y1) - (y2 - y1) * (x4 - x1)

    # Check if the lines intersect
    if cross_product1 * cross_product2 < 0 and cross_product3 * cross_product4 < 0:
        return True

    return False

def update_ball():
    global window_top, window_bottom, window_left, window_right, modes, selected_mode, teleports, overtime, ball_stuck, ball_x, ball_y, ball_x_speed, ball_y_speed, paddle_collisions, player_score, comp_score, ball_respawn_timer, game_over

    next_ball_x = ball_x + ball_x_speed  # Calculate next frame position of the ball
    next_ball_y = ball_y + ball_y_speed

    if modes[selected_mode] != "Mini Mode":
        window_top = 0
        window_bottom = window_height
        window_left = 0
        window_right = window_width
    if modes[selected_mode] == "Mini Mode":
        window_top = 135
        window_bottom = 465
        window_left = 135
        window_right = 865

    # PADDLE COLLISIONS
    angle_from_collision(next_ball_x, next_ball_y)
    angle_from_collision_computer(next_ball_x, next_ball_y)

    # WINDOW COLLISIONS
    if next_ball_y >= window_bottom - 5:
        ball_y_speed = -ball_y_speed
        ball_y = window_bottom * 2 - ball_y

    if next_ball_y <= window_top + 5:
        ball_y_speed = -ball_y_speed
        ball_y = abs(ball_y)

    if ball_x >= window_right:
        player_score += 1
        reset_ball()
        if overtime:
            player_score = points_to_win
            draw_game_over()

    elif ball_x <= window_left:
        comp_score += 1
        reset_ball()
        if overtime:
            comp_score = points_to_win
            draw_game_over()

    # BLACK HOLE INTERACTIONS
    for black_hole in black_holes:
        dist_x = black_hole['x'] - next_ball_x
        dist_y = black_hole['y'] - next_ball_y
        distance = max(1, (dist_x ** 2 + dist_y ** 2) ** 0.5)

        threshold = black_hole['threshold']
        strength = 500  # Default strength

        if distance <= threshold:
            ball_stuck += 1
            if ball_stuck >= 300:
                ball_x_speed *= 1.5  # Update ball speed
                ball_y_speed *= 1.5
                ball_stuck -= 60
            if distance <= 30:
                strength = 150
            if distance <= 5:
                strength = 50
            if distance > 30:
                strength = 500

            # Calculate the gravitational force based on the distance and strength
            force = black_hole['mass'] * strength * (1 / distance ** 2)
            force_x = force * (dist_x / distance)
            force_y = force * (dist_y / distance)
            ball_x_speed += force_x
            ball_y_speed += force_y

            # Apply teleportation logic
            teleport_threshold = 9
            if distance <= teleport_threshold and teleports <= 5:
                # Find the other black hole
                other_body = black_holes[1] if black_hole == black_holes[0] else black_holes[0]
                ball_x = other_body['x']
                ball_y = other_body['y']
                ball_stuck = 0  # Reset ball_stuck counter to prevent complete cancellation of black holes

            if distance > threshold:
                teleports = 0

    ball_x += ball_x_speed
    ball_y += ball_y_speed

    if player_score >= points_to_win or comp_score >= points_to_win:
        game_over = True

def create_clocks():
    global clocks

    clocks = []

    # Generate positions for two clocks without overlap
    for i in range(2):
        while True:
            x = random.randint(100, window_width - 100)
            y = random.randint(100, window_height - 100)
            radius = 20  # Adjust the range of radius as needed

            overlapping = False
            for clock in clocks:
                distance = math.sqrt((clock['x'] - x) ** 2 + (clock['y'] - y) ** 2)
                if distance < 2 * radius:  # Check if distance is less than twice the radius
                    overlapping = True
                    break

            if not overlapping:
                clock = {
                    'x': x,
                    'y': y,
                    'radius': radius
                }
                clocks.append(clock)
                break

def update_paddles():
    global modes, comp_y, player_y, selected_mode, window_left, window_right, window_top, window_bottom, input_list_p1, input_list_p2, player2_movement_speed, player1_movement_speed

    if modes[selected_mode] == "Confused Keyboard":
        # Player 1
        if player_move_down and player_y - player1_movement_speed >= window_top:
            player_y -= player1_movement_speed
        elif player_move_down and player_y - player1_movement_speed <= window_top:
            player_y = window_top
        elif player_move_up and player_y + player1_movement_speed <= window_bottom - paddle_height:
            player_y += player1_movement_speed
        elif player_move_up and player_y + player1_movement_speed >= window_bottom - paddle_height:
            player_y += window_bottom - paddle_height - player_y

        # Player 2
        if player2_move_down and comp_y - player2_movement_speed >= window_top:
            comp_y -= player2_movement_speed
        elif player2_move_down and comp_y - player2_movement_speed <= window_top:
            comp_y = window_top
        elif player2_move_up and comp_y + player2_movement_speed <= window_bottom - paddle_height:
            comp_y += player2_movement_speed
        elif player2_move_up and comp_y + player2_movement_speed >= window_bottom - paddle_height:
            comp_y += window_bottom - paddle_height - comp_y

    elif modes[selected_mode] in ["Light Lag", "McDonald's Lag", "Moon Lag", "Mars Lag"]:
        global input_list_p1, input_list_p2

        if modes[selected_mode] == "Light Lag":
            lag_level = 20
        if modes[selected_mode] == "McDonald's Lag":
            lag_level = 30
        if modes[selected_mode] == "Moon Lag":
            lag_level = 45
        if modes[selected_mode] == "Mars Lag":
            lag_level = 60

        if len(input_list_p1) >= lag_level:
            oldest_input_p1 = input_list_p1.pop(0)

            # Use the oldest input and react appropriately for Player 1
            if oldest_input_p1 == "up":
                if player_y - player1_movement_speed >= window_top:
                    player_y -= player1_movement_speed
                elif player_y - player1_movement_speed <= window_top:
                    player_y = window_top
            elif oldest_input_p1 == "down":
                if player_y + player1_movement_speed <= window_bottom - paddle_height:
                    player_y += player1_movement_speed
                elif player_y + player1_movement_speed >= window_bottom - paddle_height:
                    player_y += window_bottom - paddle_height - player_y

        if len(input_list_p2) >= 30:
            oldest_input_p2 = input_list_p2.pop(0)

            # Use the oldest input and react appropriately for Player 2
            if oldest_input_p2 == "up":
                if comp_y - player2_movement_speed >= window_top:
                    comp_y -= player2_movement_speed
                elif comp_y - player2_movement_speed <= window_top:
                    comp_y = window_top
            elif oldest_input_p2 == "down":
                if comp_y + player2_movement_speed <= window_bottom - paddle_height:
                    comp_y += player2_movement_speed
                elif comp_y + player2_movement_speed >= window_bottom - paddle_height:
                    comp_y += window_bottom - paddle_height - comp_y

        # Append new inputs for both players
        if player_move_up:
            input_list_p1.append("up")
        elif player_move_down:
            input_list_p1.append("down")
        else:
            input_list_p1.append("none_detected")

        if player2_move_up:
            input_list_p2.append("up")
        elif player2_move_down:
            input_list_p2.append("down")
        else:
            input_list_p2.append("none_detected")

    else: # OTHER MODES
        # Player 1
        if player_move_up and player_y - player1_movement_speed >= window_top:
            player_y -= player1_movement_speed
        elif player_move_up and player_y - player1_movement_speed <= window_top:
            player_y = window_top
        elif player_move_down and player_y + player1_movement_speed <= window_bottom - paddle_height:
            player_y += player1_movement_speed
        elif player_move_down and player_y + player1_movement_speed >= window_bottom - paddle_height:
            player_y += window_bottom - paddle_height - player_y

        # Player 2
        if player2_move_up and comp_y - player2_movement_speed >= window_top:
            comp_y -= player2_movement_speed
        elif player2_move_up and comp_y - player2_movement_speed <= window_top:
            comp_y = window_top
        elif player2_move_down and comp_y + player2_movement_speed <= window_bottom - paddle_height:
            comp_y += player2_movement_speed
        elif player2_move_down and comp_y + player2_movement_speed >= window_bottom - paddle_height:
            comp_y += window_bottom - paddle_height - comp_y

def draw_objects():
    global time_warped_by_p2, time_warped_by_p1, time_warp_ready_p2, time_warp_ready_p1, vision_time_defined, blind_time_defined, vision_time, blind_time, sight_status, sight_cooldown, overtime, paddle_height, player_x, comp_x, player1_movement_speed, player2_movement_speed, modes, tutorial, selected_mode, player_score, comp_score, total_paused_time, overtime, clock_hits, ball_x_speed, ball_y_speed, ball_x, ball_y

    window.fill(black)
    if tutorial == True:
        tutorial_text = tutorial_font.render("W/S or Up/Down to move", True, red)
        tutorial_rect = tutorial_text.get_rect(center=(window_width / 4, 20))
        window.blit(tutorial_text, tutorial_rect)

    mouse_pos = pygame.mouse.get_pos()
    if pause_button_rect.collidepoint(mouse_pos):
        pause_color = grey
    else:
        pause_color = white

    # Draw pause lines
    pygame.draw.rect(window, pause_color, (10, 10, 2, 10))
    pygame.draw.rect(window, pause_color, (15, 10, 2, 10))

    # Draw black holes
    for black_hole in black_holes:
        black_hole_image = pygame.image.load("Black Hole.png")
        black_hole_image = pygame.transform.scale(black_hole_image, (int(black_hole['threshold']), int(black_hole['threshold'])))  # Resize the image based on the threshold
        black_hole_image.set_colorkey(black)
        black_hole_rect = black_hole_image.get_rect()
        black_hole_rect.center = (black_hole['x'], black_hole['y'])
        window.blit(black_hole_image, black_hole_rect)

    if modes[selected_mode] == "Going Blind?" and sight_status == "Vision" or modes[selected_mode] != "Going Blind?":
        pygame.draw.rect(window, white, (player_x, player_y, paddle_width, paddle_height), 2)  # Player's paddle
        pygame.draw.rect(window, white, (comp_x, comp_y, paddle_width, paddle_height), 2)  # Computer's paddle


        # Draw scores
        player_score_text = score_font.render(str(player_score), True, white)
        comp_score_text = score_font.render(str(comp_score), True, white)
        window.blit(player_score_text, (window_width // 2 - 47, 10))
        window.blit(comp_score_text, (window_width // 2 + 20, 10))

        if modes[selected_mode] == 'Time Attack':
            # Draw countdown timer
            time_remaining = max(0, (total_time - (pygame.time.get_ticks() - start_time) + total_paused_time + clock_hits * 5000) // 1000)
            timer_text = score_font.render(str(time_remaining), True, white)
            timer_rect = timer_text.get_rect(center=(window_width * 3 / 4, 20))
            if overtime:
                cover_up = pygame.draw.rect(window, black, timer_rect)
                timer_text = score_font.render("OVERTIME", True, white)  # Display "OVERTIME" instead of the timer text
            window.blit(timer_text, timer_rect)

            # Check if the timer has reached zero and the scores are equal
            if time_remaining <= 0 and player_score == comp_score:
                overtime = True

            # Check if the timer has reached zero
            if time_remaining == 0 and player_score != comp_score and modes[selected_mode] == 'Time Attack':
                game_over = True
                if player_score > comp_score:
                    player_score = points_to_win
                    draw_game_over()
                if comp_score > player_score:
                    comp_score = points_to_win
                    draw_game_over()
                if player_score == comp_score:
                    overtime = True

            # Draw clocks
            for clock in clocks:
                clock_image = pygame.image.load("clock.png")
                clock_image = pygame.transform.scale(clock_image, (2 * clock['radius'], 2 * clock['radius']))
                clock_rect = clock_image.get_rect()
                if abs(math.hypot(clock['x'] - ball_x, clock['y'] - ball_y)) <= 20:
                    clock['x'] = random.randint(100, window_width - 100)
                    clock['y'] = random.randint(100, window_height - 100)
                    clock_hits += 1
                clock_rect.center = (clock['x'], clock['y'])
                if not overtime:
                    window.blit(clock_image, clock_rect)

    if modes[selected_mode] == "Going Blind?" and sight_status == "Vision" or modes[selected_mode] != "Going Blind?":
        # Draw ball
        pygame.draw.circle(window, white, (ball_x, ball_y), 5)

        # Draw center line
        pygame.draw.line(window, white, (window_width // 2, 0), (window_width // 2, window_height), 1)

    if modes[selected_mode] == "Mini Mode":
        border = pygame.draw.rect(window, white, (125, 125, 750, 350), 10)
        cover_up1 = pygame.draw.line(window, black, (window_width // 2, 0), (window_width // 2, 124), 1)
        cover_up2 = pygame.draw.line(window, black, (window_width // 2, 475), (window_width // 2, window_height), 1)
        player_x = 160
        comp_x = 840
        player1_movement_speed = 3
        player2_movement_speed = 3
        paddle_height = 60
    if modes[selected_mode] != 'Mini Mode' and modes[selected_mode] != "Enter the Matrix":
        player_x = 50
        comp_x = 950
        player1_movement_speed = 5
        player2_movement_speed = 5
        paddle_height = 75

    if modes[selected_mode] == "Enter the Matrix":  # Check if the game mode is Time Warp

        # Left player's time warp status
        if time_warped_by_p1:
            warp_text = tutorial_font.render("WARPING TIME...", True, green)
        elif not time_warp_ready_p1:
            warp_text = tutorial_font.render("TIME WARP ON COOLDOWN...", True, green)
        else:
            warp_text = tutorial_font.render("LEFT SHIFT FOR TIME WARP", True, green)

        warp_text_rect = warp_text.get_rect(midtop=(window_width / 4, window_height - 20))
        window.blit(warp_text, warp_text_rect)

        # Right player's time warp status (2 player mode only)
        if selected_players == 1:
            if time_warped_by_p2:
                warp_text = tutorial_font.render("WARPING TIME...", True, white)
            elif not time_warp_ready_p2:
                warp_text = tutorial_font.render("TIME WARP ON COOLDOWN...", True, white)
            else:
                warp_text = tutorial_font.render("RIGHT SHIFT FOR TIME WARP", True, white)

            warp_text_rect = warp_text.get_rect(midtop=(window_width * 3 / 4, window_height - 20))
            window.blit(warp_text, warp_text_rect)

    if modes[selected_mode] == "Going Blind?":
        if sight_status == "Vision" and len(sight_cooldown) >= vision_time:
            vision_time_defined = False
            sight_status = "Blind"
            sight_cooldown.clear()
        if sight_status == "Blind" and len(sight_cooldown) >= blind_time:
            blind_time_defined = False
            sight_status = "Vision"
            sight_cooldown.clear()
        if not vision_time_defined:
            vision_time = random.randint(60, 300)
            vision_time_defined = True
        if not blind_time_defined:
            blind_time = random.randint(30, 60)
            blind_time_defined = True


    pygame.display.update()

def move_computer_paddle():
    global comp_y, window_top, window_bottom, selected_difficulty

    # Calculate predicted position of the ball
    if ball_x_speed != 0:
        predicted_y = ball_y + ((comp_x - ball_x) / ball_x_speed) * ball_y_speed

        # Calculate the margin for contact
        contact_margin = paddle_height * 0.3

        # Account for bounces off the top and bottom of the window only on Asian mode
        if selected_difficulty == 3:
            if predicted_y < 0:
                predicted_y = abs(predicted_y)
            elif predicted_y > window_height:
                predicted_y = 2 * window_height - predicted_y

        # Move the computer paddle towards the predicted position within the contact margin
        if predicted_y < comp_y + paddle_height / 2 - contact_margin and comp_y > window_top:
            comp_y -= comp_movement_speed
        elif predicted_y > comp_y + paddle_height / 2 + contact_margin and comp_y < window_bottom - paddle_height:
            comp_y += comp_movement_speed

def draw_game_over():
    global time_warp_ready_p1, time_warp_ready_p2, time_warp_cooldown_p2, time_warp_cooldown_p1, time_warped_by_p1, time_warped_by_p2, vision_time_defined, blind_time_defined, sight_cooldown, input_list_p1, input_list_p2, tutorial, subtitle_subtitle_text, selected_players, player_score, comp_score, start_time, total_time, black_holes, selected_mode, game_over, selected_difficulty, selected_points, difficulties_unlocked, subtitle_subtitle_text

    title_font = pygame.font.Font('Atari.TTF', 20)
    subtitle_font = pygame.font.Font('Atari.TTF', 11)
    tutorial = False
    subtitle_subtitle_text = subtitle_font.render("", True, blue)
    input_list_p1.clear()
    input_list_p2.clear()
    vision_time_defined = False
    blind_time_defined = False
    sight_cooldown.clear()
    time_warped_by_p1 = False
    time_warped_by_p2 = False
    time_warp_ready_p1 = False
    time_warp_ready_p2 = False
    time_warp_cooldown_p1.clear()
    time_warp_cooldown_p2.clear()


    if selected_players == 0:
        if player_score >= points_to_win:
            game_over_text = title_font.render("YOU WIN!", True, white)
            if selected_difficulty == 0:
                game_over_subtitle = subtitle_font.render("EZ win, but wait 'til you get to the last difficulty...", True, white)
                if difficulties_unlocked == 0:
                    difficulties_unlocked += 1
                    subtitle_subtitle_text = subtitle_font.render("Beat the Medium Difficulty. It's in your settings", True, blue)
            if selected_difficulty == 1:
                game_over_subtitle = subtitle_font.render("Not bad, I guess....", True, white)
                if difficulties_unlocked == 1:
                    difficulties_unlocked += 1
                    subtitle_subtitle_text = subtitle_font.render("Beat the Hard Difficulty", True, blue)
            if selected_difficulty == 2:
                game_over_subtitle = subtitle_font.render("Pretty good, but beat the final challenge now....", True, white)
                if difficulties_unlocked == 2:
                    difficulties_unlocked += 1
                    subtitle_subtitle_text = subtitle_font.render("BEAT ASIAN DIFFICULTY", True, blue)
            if selected_difficulty == 3:
                game_over_subtitle = subtitle_font.render("Is this the power of a god???", True, white)
        if comp_score >= points_to_win:
            game_over_text = title_font.render("GAME OVER", True, white)
            if selected_difficulty == 0:
                game_over_subtitle = subtitle_font.render("You LOST to EASY MODE?! I didn't know that was possible!", True, white)
            if selected_difficulty == 1:
                game_over_subtitle = subtitle_font.render("I expect more from you...", True, white)
            if selected_difficulty == 2:
                game_over_subtitle = subtitle_font.render("Ok, well this stage is supposed to be hard. But wait for the next one...", True, white)
            if selected_difficulty == 3:
                game_over_subtitle = subtitle_font.render("Expected.", True, white)

    if selected_players == 1:
        game_over_subtitle = score_font.render("", True, white)
        subtitle_subtitle_text = score_font.render("", True, white)
        if player_score >= points_to_win:
            game_over_text = title_font.render("Player 1 Wins!", True, white)
        if comp_score >= points_to_win:
            game_over_text = title_font.render("Player 2 Wins!", True, white)

    question_text = score_font.render("Play again?", True, white)
    yes_text = score_font.render("Yes", True, white)
    no_text = score_font.render("No", True, white)

    game_over_text_rect = game_over_text.get_rect(center=(window_width // 2, window_height // 2 - 100))
    question_text_rect = question_text.get_rect(center=(window_width // 2, window_height // 2))
    yes_text_rect = yes_text.get_rect(center=(window_width // 2 - 100, window_height // 2 + 50))
    no_text_rect = no_text.get_rect(center=(window_width // 2 + 100, window_height // 2 + 50))
    game_over_subtitle_rect = game_over_subtitle.get_rect(center=(window_width // 2, window_height // 2 - 60))
    subtitle_subtitle_rect = subtitle_subtitle_text.get_rect(center=(window_width // 2, window_height // 2 - 30))

    yes_rect = pygame.Rect(
        yes_text_rect.left - 5,
        yes_text_rect.top - 5,
        yes_text_rect.width + 10,
        yes_text_rect.height + 10
    )
    no_rect = pygame.Rect(
        no_text_rect.left - 5,
        no_text_rect.top - 5,
        no_text_rect.width + 10,
        no_text_rect.height + 10
    )

    while game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_game()
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if yes_rect.collidepoint(mouse_pos):
                    black_holes.clear()
                    clocks.clear()
                    if modes[selected_mode] == 'Black Holes':
                        create_black_holes()
                    if modes[selected_mode] == 'Time Attack':
                        create_clocks()
                        start_time = pygame.time.get_ticks()
                        total_time = 60000
                    window.fill(black)
                    reset_game()
                    reset_ball()

                elif no_rect.collidepoint(mouse_pos):
                    window.fill(black)
                    show_main_menu()
                    reset_ball()
                    reset_game()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    reset_game()

                elif event.key == pygame.K_n:
                    pygame.quit()
                    sys.exit()

        # Check if mouse hovers over "Yes" and "No" buttons
        mouse_pos = pygame.mouse.get_pos()
        yes_hover = yes_rect.collidepoint(mouse_pos)
        no_hover = no_rect.collidepoint(mouse_pos)

        # Update button colors based on hover state
        yes_color = grey if yes_hover else white
        no_color = grey if no_hover else white

        window.fill(black)
        window.blit(game_over_text, game_over_text_rect)
        window.blit(question_text, question_text_rect)
        pygame.draw.rect(window, black, yes_rect, 2)
        pygame.draw.rect(window, black, no_rect, 2)
        window.blit(yes_text, yes_text_rect)
        window.blit(no_text, no_text_rect)
        window.blit(game_over_subtitle, game_over_subtitle_rect)
        if player_score >= points_to_win:
            window.blit(subtitle_subtitle_text, subtitle_subtitle_rect)

        # Update button text colors based on hover state
        yes_text = score_font.render("Yes", True, yes_color)
        no_text = score_font.render("No", True, no_color)
        window.blit(yes_text, yes_text_rect)
        window.blit(no_text, no_text_rect)

        pygame.display.update()
        clock.tick(60)

def show_main_menu():
    global player_x, paddle_height, player1_movement_speed, player2_movement_speed, comp_x, black_holes, selected_mode, total_time, start_time, timing, modes

    menu_font = pygame.font.Font('Atari.TTF', 20)
    title_font = pygame.font.Font('Atari.TTF', 28)
    title_text = title_font.render("Welcome to Pong", True, white)
    start_text = menu_font.render("Start", True, white)
    settings_text = menu_font.render("Settings", True, white)
    quit_text = menu_font.render("End Game", True, white)

    title_rect = title_text.get_rect(center=(window_width // 2, window_height // 2 - 100))
    start_rect = start_text.get_rect(center=(window_width // 2, window_height // 2))
    settings_rect = settings_text.get_rect(center=(window_width // 2, window_height // 2 + 50))
    quit_rect = quit_text.get_rect(center=(window_width // 2, window_height // 2 + 100))

    start_button_rect = pygame.Rect(
        start_rect.left - 5,
        start_rect.top - 5,
        start_rect.width + 10,
        start_rect.height + 10
    )
    settings_button_rect = pygame.Rect(
        settings_rect.left - 5,
        settings_rect.top - 5,
        settings_rect.width + 10,
        settings_rect.height + 10
    )
    quit_button_rect = pygame.Rect(
        quit_rect.left - 5,
        quit_rect.top - 5,
        quit_rect.width + 10,
        quit_rect.height + 10
    )

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_game()
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if start_button_rect.collidepoint(mouse_pos):
                    black_holes.clear()
                    clocks.clear()
                    if modes[selected_mode] == 'Black Holes':
                        create_black_holes()
                    if modes[selected_mode] == 'Time Attack':
                        create_clocks()
                        start_time = pygame.time.get_ticks()
                        timing = False
                    return True

                if settings_button_rect.collidepoint(mouse_pos):
                    show_settings_menu()
                    if modes[selected_mode] == "Time Attack":
                        selected_points = 7

                if quit_button_rect.collidepoint(mouse_pos):
                    save_game()
                    pygame.quit()
                    sys.exit()

        # Check if mouse hovers over buttons
        mouse_pos = pygame.mouse.get_pos()
        start_hover = start_button_rect.collidepoint(mouse_pos)
        settings_hover = settings_button_rect.collidepoint(mouse_pos)
        quit_hover = quit_button_rect.collidepoint(mouse_pos)

        # Update button text color based on hover state
        start_color = grey if start_hover else white
        settings_color = grey if settings_hover else white
        quit_color = grey if quit_hover else white

        # Render button text with updated color
        start_text = menu_font.render("Start", True, start_color)
        settings_text = menu_font.render("Settings", True, settings_color)
        quit_text = menu_font.render("End Game", True, quit_color)

        window.fill(black)
        window.blit(title_text, title_rect)
        pygame.draw.rect(window, black, start_button_rect, 2)
        pygame.draw.rect(window, black, settings_button_rect, 2)
        pygame.draw.rect(window, black, quit_button_rect, 2)
        window.blit(start_text, start_rect)
        window.blit(settings_text, settings_rect)
        window.blit(quit_text, quit_rect)
        pygame.display.update()
        clock.tick(60)

def show_pause_menu():
    global time_warp_ready_p1, time_warp_ready_p2, time_warp_cooldown_p2, time_warp_cooldown_p1, time_warped_by_p1, time_warped_by_p2, vision_time_defined, blind_time_defined, sight_cooldown, tutorial, mid_game, total_paused_time, pause_button_clicked, playing, timing, start_time, total_time, paused_at, pause_duration, modes, selected_mode

    title_font = pygame.font.Font('Atari.TTF', 25)
    menu_font = pygame.font.Font('Atari.TTF', 20)
    title_text = title_font.render("Are you ready?", True, white)
    resume_text = menu_font.render("Play", True, white)
    quit_text = menu_font.render("Return to Menu", True, white)

    title_rect = title_text.get_rect(center=(window_width // 2, window_height // 2 - 100))
    resume_rect = resume_text.get_rect(center=(window_width // 2, window_height // 2))
    quit_rect = quit_text.get_rect(center=(window_width // 2, window_height // 2 + 50))

    resume_button_rect = pygame.Rect(
        resume_rect.left - 5,
        resume_rect.top - 5,
        resume_rect.width + 10,
        resume_rect.height + 10
    )
    quit_button_rect = pygame.Rect(
        quit_rect.left - 5,
        quit_rect.top - 5,
        quit_rect.width + 10,
        quit_rect.height + 10
    )

    while True:
        if modes[selected_mode] == 'Time Attack':
            pause_duration = pygame.time.get_ticks() - paused_at
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_game()
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if resume_button_rect.collidepoint(mouse_pos):
                    if not timing:
                        timing = True
                        total_time = 60000
                    if mid_game == True:
                        total_paused_time += pause_duration
                    mid_game = True
                    vision_time_defined = False
                    blind_time_defined = False
                    sight_cooldown.clear()
                    time_warped_by_p1 = False
                    time_warped_by_p2 = False
                    time_warp_ready_p1 = False
                    time_warp_ready_p2 = False
                    time_warp_cooldown_p1.clear()
                    time_warp_cooldown_p2.clear()
                    return  # Resume the game

                if quit_button_rect.collidepoint(mouse_pos):
                    mid_game = False
                    tutorial = False
                    show_main_menu()
                    reset_ball()
                    reset_game()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                show_main_menu()

        # Check if mouse hovers over buttons
        mouse_pos = pygame.mouse.get_pos()
        resume_hover = resume_button_rect.collidepoint(mouse_pos)
        quit_hover = quit_button_rect.collidepoint(mouse_pos)

        # Update button text color based on hover state
        resume_color = grey if resume_hover else white
        quit_color = grey if quit_hover else white

        # Render button text with updated color
        resume_text = menu_font.render("Play", True, resume_color)
        quit_text = menu_font.render("Return to Menu", True, quit_color)

        window.fill(black)
        window.blit(title_text, title_rect)
        pygame.draw.rect(window, black, resume_button_rect, 2)
        pygame.draw.rect(window, black, quit_button_rect, 2)
        window.blit(resume_text, resume_rect)
        window.blit(quit_text, quit_rect)

        pygame.display.update()
        clock.tick(60)

def show_settings_menu():
    global selected_players, modes, selected_mode, difficulties_unlocked, comp_movement_speed, points_to_win, player1_movement_speed, player2_movement_speed, selected_difficulty, selected_points

    difficulties = ["Easy"]
    if difficulties_unlocked == 1:
        difficulties.append("Medium")
    if difficulties_unlocked == 2:
        difficulties.append("Medium")
        difficulties.append("Hard")
    if difficulties_unlocked == 3:
        difficulties.append("Medium")
        difficulties.append("Hard")
        difficulties.append("Asian")

    points = [1, 3, 5, 7, 11, 21, 50, 100]
    players = [1, 2]

    title_font = pygame.font.Font('Atari.TTF', 25)
    menu_font = pygame.font.Font('Atari.TTF', 20)
    settings_title = title_font.render("Settings", True, white)
    difficulty_text = menu_font.render(f"Difficulty: {difficulties[selected_difficulty]}", True, white)
    points_text = menu_font.render(f"Points to Win: {points[selected_points]}", True, white)
    game_mode_text = menu_font.render(f"Game Mode: {modes[selected_mode]}", True, white)
    players_text = menu_font.render(f"Number of Players: {players[selected_players]}", True, white)
    save_text = menu_font.render("Press Enter to Save", True, red)

    difficulty_rect = difficulty_text.get_rect(topleft=(window_width // 2 - 165, window_height // 2 - 200))
    points_rect = points_text.get_rect(topleft=(window_width // 2 - 165, window_height // 2 - 100))
    game_mode_rect = game_mode_text.get_rect(topleft=(window_width // 2 - 165, window_height // 2))
    players_rect = players_text.get_rect(topleft=(window_width // 2 - 165, window_height // 2 + 100))
    save_rect = save_text.get_rect(center=(window_width // 2 + 8, window_height // 2 + 200))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_game()
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if difficulty_rect.collidepoint(mouse_pos):
                    selected_difficulty = (selected_difficulty + 1) % len(difficulties)

                if points_rect.collidepoint(mouse_pos):
                    selected_points = (selected_points + 1) % len(points)

                if game_mode_rect.collidepoint(mouse_pos):
                    if selected_mode == len(modes) - 2:
                        save_game()
                    if modes[selected_mode] == "Time Attack":
                        load_game()
                        selected_mode = (selected_mode + 1) % len(modes)
                    selected_mode = (selected_mode + 1) % len(modes)

                if players_rect.collidepoint(mouse_pos):
                    selected_players = (selected_players + 1) % len(players)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if selected_difficulty == 0:  # Easy
                        comp_movement_speed = 3
                    elif selected_difficulty == 1:  # Medium
                        comp_movement_speed = 5
                    elif selected_difficulty == 2:  # Hard
                        comp_movement_speed = 6
                    elif selected_difficulty == 3:
                        comp_movement_speed = 9
                    # Asian, which is mathematically impossible to beat (on normal mode).
                    # You're welcome :)

                    points_to_win = points[selected_points]
                    return

        mouse_pos = pygame.mouse.get_pos()
        difficulty_hover = difficulty_rect.collidepoint(mouse_pos)
        points_hover = points_rect.collidepoint(mouse_pos)
        game_mode_hover = game_mode_rect.collidepoint(mouse_pos)
        players_hover = players_rect.collidepoint(mouse_pos)

        # Update button text color based on hover state
        difficulty_color = grey if difficulty_hover else white
        points_color = grey if points_hover else white
        game_mode_color = grey if game_mode_hover else white
        players_color = grey if players_hover else white

        difficulty_text = menu_font.render(f"Difficulty: {difficulties[selected_difficulty]}", True, difficulty_color)
        if modes[selected_mode] != "Time Attack":
            points_text = menu_font.render(f"Points to Win: {points[selected_points]}", True, points_color)
        if modes[selected_mode] == "Time Attack":
            points_text = menu_font.render("Points to Win: INFINITE", True, points_color)
        game_mode_text = menu_font.render(f"Game Mode: {modes[selected_mode]}", True, game_mode_color)
        players_text = menu_font.render(f"Number of Players: {players[selected_players]}", True, players_color)

        # Draw the settings menu
        window.fill(black)
        window.blit(settings_title, (window_width // 2 - settings_title.get_width() // 2, 50))
        window.blit(difficulty_text, difficulty_rect)
        window.blit(points_text, points_rect)
        window.blit(game_mode_text, game_mode_rect)
        window.blit(players_text, players_rect)
        window.blit(save_text, save_rect)
        pygame.display.flip()

def reset_ball():
    global ball_x, ball_y, ball_x_speed, ball_y_speed, ball_respawn_timer

    ball_x = 500
    ball_y = 300
    # Ball must go towards comp on start to avoid startling the player
    # and giving the computer an unfair advantage, as the computer knows (and can react to)
    # where the ball is going as soon as the game starts but the player does not
    ball_x_speed = random.randint(3, 8)
    ball_y_speed = random.randint(-8, 8)
    while -2 <= ball_y_speed <= 2:
        ball_y_speed = random.randint(-8, 8)
    ball_respawn_timer = time.time()

def reset_game():
    global clock_hits, total_paused_time, player_score, comp_score, game_over, player_x, player_y, comp_x, comp_y, modes, selected_mode, overtime
    overtime = False
    player_score = 0
    comp_score = 0
    total_paused_time = 0
    game_over = False
    player_x = 50
    player_y = 263
    comp_x = 950
    comp_y = 263
    if modes[selected_mode] == 'Time Attack':
        total_time = 60000
        start_time = pygame.time.get_ticks()
        create_clocks()
        clock_hits = 0
    reset_ball()

show_main_menu()
show_pause_menu()
# Main game loop
while True:
    if modes[selected_mode] == "Going Blind?":
        sight_cooldown.append("+1")
    if modes[selected_mode] == 'Time Attack':
        selected_points = 7
        points_to_win = 100
    if modes[selected_mode] == "Enter the Matrix" and not time_warp_ready_p1:
        time_warp_cooldown_p1.append("+1")
    if modes[selected_mode] == "Enter the Matrix" and not time_warp_ready_p2:
        time_warp_cooldown_p2.append("+1")
    if len(time_warp_cooldown_p1) >= fps * 7 and not time_warp_ready_p1:
        time_warp_ready_p1 = True
        time_warp_cooldown_p1.clear()
    if len(time_warp_cooldown_p1) >= fps * 3 and time_warped_by_p1:
        time_warped_by_p1 = False
        time_warp_cooldown_p1.clear()
        player1_movement_speed = 5
    if len(time_warp_cooldown_p2) >= fps * 7 and not time_warp_ready_p2:
        time_warp_ready_p2 = True
        time_warp_cooldown_p2.clear()
    if len(time_warp_cooldown_p2) >= fps * 3 and time_warped_by_p2:
        time_warped_by_p2 = False
        time_warp_cooldown_p2.clear()

    if time_warped_by_p1:
        fps = 20
        player1_movement_speed = 15
    if time_warped_by_p2:
        fps = 20
        player2_movement_speed = 15
    if not time_warped_by_p1 and not time_warped_by_p2 and modes[selected_mode] != "Mini Mode":
        fps = 60
        player1_movement_speed = 5
        player2_movement_speed = 5

    if not playing:
        playing = show_main_menu()
        if not playing:
            break

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_game()
            pygame.quit()
            sys.exit()

        if selected_players == 0: # One player
            # Keydown events
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    player_move_up = True
                elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    player_move_down = True
                elif event.key == pygame.K_LSHIFT and time_warp_ready_p1:
                    time_warped_by_p1 = True
                    time_warp_ready_p1 = False

            # Keyup events
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    player_move_up = False
                elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    player_move_down = False

        if selected_players == 1: # 2 Players
            # P1 Keydown events
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    player_move_up = True
                elif event.key == pygame.K_s:
                    player_move_down = True
                elif event.key == pygame.K_LSHIFT and time_warp_ready_p1 and not time_warped_by_p2:
                    time_warped_by_p1 = True
                    time_warp_ready_p1 = False

            # P2 Keydown events
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    player2_move_up = True
                elif event.key == pygame.K_DOWN:
                    player2_move_down = True
                elif event.key == pygame.K_RSHIFT and time_warp_ready_p2 and not time_warped_by_p1:
                    time_warped_by_p2 = True
                    time_warp_ready_p2 = False

            # P1 Keyup events
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    player_move_up = False
                elif event.key == pygame.K_s:
                    player_move_down = False

            # P2 Keyup events
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    player2_move_up = False
                elif event.key == pygame.K_DOWN:
                    player2_move_down = False

        # Mouse click events
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            if pause_button_rect.collidepoint(mouse_pos):
                pause_button_clicked = True
                mid_game = True

    if pause_button_clicked:
        paused_at = pygame.time.get_ticks()
        show_pause_menu()
        pause_button_clicked = False
        player_move_up = False
        player_move_down = False

    if not game_over:
        if selected_players == 0:
            move_computer_paddle()
        update_paddles()
        draw_objects()
        update_ball()

    else:
        window.fill(black)
        draw_game_over()
        player_move_up = False
        player_move_down = False

    if ball_respawn_timer is not None and time.time() - ball_respawn_timer > respawn_time:
        ball_respawn_timer = None

    pygame.display.update()
    clock.tick(fps)

pygame.quit()
sys.exit()
