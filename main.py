# ------------------LIBRARIES USED FOR OUR GAME-----------------
import pygame
import sys
import random
from enum import Enum
from pygame.math import Vector2
# --------------------------------------------------------------

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()  # Initialize pygame to run the game
pygame.font.init()  # Initialize font to add our .ttf file
pygame.display.set_caption('Hungry Charlie')  # Name displayed to the top left of the window

CELL_SIZE = 40
CELL_NUMBER = 20
TEXT_FONT = pygame.font.Font("Fonts/ARCADE_R.TTF", 25)  # Set our own font to display text
# The window's size will be 800x800
SCREEN = pygame.display.set_mode((CELL_NUMBER * CELL_SIZE, CELL_NUMBER * CELL_SIZE))
CLOCK = pygame.time.Clock()
FRAMERATE = 60  # 60 frames per second (fps)
SCREEN_UPDATE = pygame.USEREVENT  # keep track of updates in our game
pygame.time.set_timer(SCREEN_UPDATE, 140)  # every update has 140 millisecond gap


# The Color class keeps all colors with their RGB values
# Used to easily keep track what colors we use in our code
class Color(Enum):
    GRASS = (110, 210, 100)
    SCORE = (60, 80, 15)
    SCREEN = (180, 210, 80)
    White = (255, 255, 255)
    Black = (0, 0, 0)


# The Fruit class represents the apple eaten by Charlie the Snake.
# When the snake eats the apple we add +1 to our total score and the snake grows larger
class Fruit:
    def __init__(self):
        self.pos = None  # Vector2 position of the fruit (randomized every time)
        self.y = None  # y position
        self.x = None  # x position
        self.image = pygame.image.load('Images/apple.png').convert_alpha()  # image used for the apple (40x40)
        self.randomize_position()  # at every initialization, we randomize the position of the next fruit

    def draw(self):  # How we draw the apple image to out object
        # We make sure the apple is drawn inside one of the screen's cells with exact integer coordinates
        fruit_rect = pygame.Rect(int(self.pos.x * CELL_SIZE), int(self.pos.y * CELL_SIZE), CELL_SIZE, CELL_SIZE)
        SCREEN.blit(self.image, fruit_rect)

    # When Charlie eats a fruit, the next one must be to another, random position
    def randomize_position(self):
        self.x = random.randint(0, CELL_NUMBER - 1)
        self.y = random.randint(0, CELL_NUMBER - 1)
        self.pos = Vector2(self.x, self.y)


# Charlie is a hungry snake who likes to eat healthy :)
class Snake:
    def __init__(self):
        # The body of the snake is in total 3 vectors (head, body, tail) to specific locations
        self.body = [Vector2(5, 10), Vector2(4, 10), Vector2(3, 10)]
        self.direction = Vector2(1, 0)  # The snake has by default RIGHT direction
        self.new_block = False  # Does Charlie need to grow?
        self.skin = 0  # Skin selected from the menu (1, 2 or 3)

        # Images for all snake's vectors
        # The image's paths are found from the Images folder
        self.head = None
        self.tail = None
        self.head_up = None
        self.head_down = None
        self.head_right = None
        self.head_left = None

        self.tail_up = None
        self.tail_down = None
        self.tail_right = None
        self.tail_left = None

        self.body_vertical = None
        self.body_horizontal = None
        self.body_tr = None
        self.body_tl = None
        self.body_br = None
        self.body_bl = None

        self.crunch_sound = pygame.mixer.Sound('Sounds/crunch.wav')  # How Charlie eating sounds like?
        self.hit_sound = pygame.mixer.Sound('Sounds/hit.wav')  # How Charlie being hit sounds like?
        self.load_skin(1)  # Default skin of the snake is the first one

    def load_skin(self, skin_selection):  # Function to load the correct skin from the menu
        base_path = f"Images/Skin_{skin_selection}/"  # The images' names are the same
        # The only difference comes to the file located (Skin_1, Skin_2, Skin_3)

        self.head_up = pygame.image.load(base_path + "head_up.png").convert_alpha()
        self.head_down = pygame.image.load(base_path + "head_down.png").convert_alpha()
        self.head_right = pygame.image.load(base_path + "head_right.png").convert_alpha()
        self.head_left = pygame.image.load(base_path + "head_left.png").convert_alpha()

        self.tail_up = pygame.image.load(base_path + "tail_up.png").convert_alpha()
        self.tail_down = pygame.image.load(base_path + "tail_down.png").convert_alpha()
        self.tail_right = pygame.image.load(base_path + "tail_right.png").convert_alpha()
        self.tail_left = pygame.image.load(base_path + "tail_left.png").convert_alpha()

        self.body_vertical = pygame.image.load(base_path + "body_vertical.png").convert_alpha()
        self.body_horizontal = pygame.image.load(base_path + "body_horizontal.png").convert_alpha()

        self.body_tr = pygame.image.load(base_path + "body_tr.png").convert_alpha()
        self.body_tl = pygame.image.load(base_path + "body_tl.png").convert_alpha()
        self.body_br = pygame.image.load(base_path + "body_br.png").convert_alpha()
        self.body_bl = pygame.image.load(base_path + "body_bl.png").convert_alpha()

        self.head = self.head_up  # default value to avoid None value related errors
        self.tail = self.tail_up  # default value to avoid None value related errors

    def draw(self):
        self.update_head()  # keep track of the correct image of the head
        self.update_tail()  # keep track of the correct image of the tail

        # For each block in the snake's body we check which image is proper
        for index, block in enumerate(self.body):
            x_pos = int(block.x * CELL_SIZE)
            y_pos = int(block.y * CELL_SIZE)
            block_rect = pygame.Rect(x_pos, y_pos, CELL_SIZE, CELL_SIZE)

            if index == 0:  # The first block is the head
                SCREEN.blit(self.head, block_rect)
            elif index == len(self.body) - 1:  # The last one is the tail
                SCREEN.blit(self.tail, block_rect)
            else:  # In between, the rest of the body
                previous_block = self.body[index + 1] - block
                next_block = self.body[index - 1] - block

                # We make sure to keep track the direction of each block so that we can put the correct image
                if previous_block.x == next_block.x:
                    SCREEN.blit(self.body_vertical, block_rect)
                elif previous_block.y == next_block.y:
                    SCREEN.blit(self.body_horizontal, block_rect)
                else:
                    if previous_block.x == -1 and next_block.y == -1 or previous_block.y == -1 and next_block.x == -1:
                        SCREEN.blit(self.body_tl, block_rect)
                    if previous_block.x == -1 and next_block.y == 1 or previous_block.y == 1 and next_block.x == -1:
                        SCREEN.blit(self.body_bl, block_rect)
                    if previous_block.x == 1 and next_block.y == -1 or previous_block.y == -1 and next_block.x == 1:
                        SCREEN.blit(self.body_tr, block_rect)
                    if previous_block.x == 1 and next_block.y == 1 or previous_block.y == 1 and next_block.x == 1:
                        SCREEN.blit(self.body_br, block_rect)

    def update_head(self):  # How the head will look (based on direction)
        head_direction = self.body[1] - self.body[0]
        if head_direction == Vector2(1, 0):
            self.head = self.head_left  # LEFT
        elif head_direction == Vector2(-1, 0):
            self.head = self.head_right  # RIGHT
        elif head_direction == Vector2(0, 1):
            self.head = self.head_up  # UP
        elif head_direction == Vector2(0, -1):
            self.head = self.head_down  # DOWN

    def update_tail(self):  # How the tail will look (based on direction)
        tail_direction = self.body[-2] - self.body[-1]
        if tail_direction == Vector2(1, 0):
            self.tail = self.tail_left  # LEFT
        elif tail_direction == Vector2(-1, 0):
            self.tail = self.tail_right  # RIGHT
        elif tail_direction == Vector2(0, 1):
            self.tail = self.tail_up  # UP
        elif tail_direction == Vector2(0, -1):
            self.tail = self.tail_down  # DOWN

    def move(self):
        if self.new_block:  # If the snake requires a new block
            body_copy = self.body[:]
            body_copy.insert(0, body_copy[0] + self.direction)  # we add a new block
            self.body = body_copy[:]
            self.new_block = False
        else:  # The snake keeps moving we just adjust the Vector2 blocks
            body_copy = self.body[:-1]
            body_copy.insert(0, body_copy[0] + self.direction)
            self.body = body_copy[:]

    def add_block(self):  # Does the snake need a new block?
        self.new_block = True

    def crunch(self):  # Play the crunch sound when the snake eats fruit
        self.crunch_sound = pygame.mixer.Sound('Sounds/crunch.wav')
        self.crunch_sound.set_volume(1.0)
        self.crunch_sound.play()

    def hit(self):  # Play the hit sound when the snake bites itself or hits a wall
        self.hit_sound = pygame.mixer.Sound('Sounds/hit.wav')
        self.hit_sound.set_volume(1.0)
        self.hit_sound.play()

    def reset(self):
        self.body = [Vector2(5, 10), Vector2(4, 10), Vector2(3, 10)]


def close_game():  # Close the game (the program)
    pygame.quit()
    sys.exit()


def draw_level():  # Draw the game screen
    grass_color = Color.GRASS.value
    for row in range(CELL_NUMBER):
        if row % 2 == 0:
            for column in range(CELL_NUMBER):
                if column % 2 == 0:
                    grass_rect = pygame.Rect(column * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(SCREEN, grass_color, grass_rect)
        else:
            for column in range(CELL_NUMBER):
                if column % 2 != 0:
                    grass_rect = pygame.Rect(column * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(SCREEN, grass_color, grass_rect)


# The Game class represents the game we play
class Game:
    def __init__(self):
        self.Fruit = None
        self.Snake = None
        self.score = None
        self.reset(skin_selected=1)

    def play_movements(self):
        hit_or_bit = False  # check if the player loses
        for game_event in pygame.event.get():

            if game_event.type == pygame.QUIT:  # If we press X on the window
                close_game()  # the game closes

            if game_event.type == pygame.KEYDOWN:  # If the user presses a key
                if game_event.key == pygame.K_UP:  # PRESS UP ARROW
                    if main_Game.Snake.direction.y != 1:
                        main_Game.Snake.direction = Vector2(0, -1)
                if game_event.key == pygame.K_DOWN:  # PRESS DOWN ARROW
                    if main_Game.Snake.direction.y != -1:
                        main_Game.Snake.direction = Vector2(0, 1)
                if game_event.key == pygame.K_RIGHT:  # PRESS RIGHT ARROW
                    if main_Game.Snake.direction.x != -1:
                        main_Game.Snake.direction = Vector2(1, 0)
                if game_event.key == pygame.K_LEFT:  # PRESS LEFT ARROW
                    if main_Game.Snake.direction.x != 1:
                        main_Game.Snake.direction = Vector2(-1, 0)

            # Gameplay Updates
            if game_event.type == SCREEN_UPDATE:
                self.Snake.move()
                self.eat_fruit()

                if self.check_failure():  # If we hit the wall or the snakes bites itself
                    hit_or_bit = True
                    return hit_or_bit, self.score

        return hit_or_bit, self.score

    def draw(self):
        draw_level()
        self.Fruit.draw()
        self.Snake.draw()
        self.draw_score()

    def eat_fruit(self):
        if self.Fruit.pos == self.Snake.body[0]:  # If the snake bites the fruit
            self.Fruit.randomize_position()  # new fruit
            self.Snake.add_block()  # snake grows
            self.Snake.crunch()  # play the crunch sound
            self.score += 1
            # print("Current Score: ", self.score)

        # We make sure the new position of the fruit is not at any of the snake's blocks
        for block in self.Snake.body[1:]:
            if block == self.Fruit.pos:
                self.Fruit.randomize_position()  # Randomize again

    def check_failure(self):
        snake_head = self.Snake.body[0]
        right_left_wall_bounds = (0 <= snake_head.x <= CELL_NUMBER)
        up_down_wall_bounds = (0 <= snake_head.y <= CELL_NUMBER)

        # The snake hits the wall
        if not right_left_wall_bounds or not up_down_wall_bounds:
            print("Charlie hit the wall!")
            self.Snake.hit()
            return True

        # The snake eats itself
        for block in self.Snake.body[1:]:
            if block == self.Snake.body[0]:
                print("Charlie bit himself!")
                self.Snake.hit()
                return True
        return False

    def reset(self, skin_selected):  # When the user restarts the game we must be careful
        # The selected skin must remain the same (otherwise it becomes default again)
        self.Snake = Snake()
        self.Snake.load_skin(skin_selected)  # Pass selected_skin to load_skin
        self.Fruit = Fruit()
        self.score = 0

    def draw_score(self):  # Display how many apples Charlie ate
        my_score = str(len(self.Snake.body) - 3)
        score_surface = TEXT_FONT.render(my_score, True, Color.SCORE.value)
        score_x = int(CELL_SIZE * CELL_NUMBER - 60)
        score_y = int(CELL_SIZE * CELL_NUMBER - 40)
        score_rect = score_surface.get_rect(center=(score_x, score_y))
        apple_rect = self.Fruit.image.get_rect(midright=(score_rect.left, score_rect.centery))
        SCREEN.blit(score_surface, score_rect)
        SCREEN.blit(self.Fruit.image, apple_rect)


# Menu screen: The user has 3 options:
# Start game: It starts the snake game
# Customization: The user can select the snake's skin (Orange, Blue, Pink)
class Menu:
    def __init__(self):
        self.options = ["Start Game", "Costume:Skin 1", "Exit"]
        self.selected_option = 0
        self.skins = ["Skin 1", "Skin 2", "Skin 3"]
        self.selected_skin = 1  # Default skin is 1
        self.selection_icon = pygame.image.load('Images/apple.png').convert_alpha()

        self.title_font = pygame.font.Font("Fonts/ARCADE_R.TTF", 50)
        self.option_font = pygame.font.Font("Fonts/ARCADE_R.TTF", 30)
        self.notes_font = pygame.font.Font("Fonts/ARCADE_R.TTF", 15)

    def draw(self):
        SCREEN.fill(Color.Black.value)

        # Center coordinates
        screen_center_x = CELL_NUMBER * CELL_SIZE // 2
        screen_center_y = CELL_NUMBER * CELL_SIZE // 2

        # Draw title
        title_surface = self.title_font.render("Hungry Charlie", True, Color.White.value)
        title_rect = title_surface.get_rect(center=(screen_center_x, screen_center_y - CELL_SIZE * 4))
        SCREEN.blit(title_surface, title_rect)

        # Draw menu options
        for i, option in enumerate(self.options):
            option_surface = self.option_font.render(option, True, Color.White.value)
            option_rect = option_surface.get_rect(
                center=(screen_center_x, screen_center_y + CELL_SIZE * (i - 1))
            )
            SCREEN.blit(option_surface, option_rect)

            if i == self.selected_option:
                apple_rect = self.selection_icon.get_rect(
                    midleft=(option_rect.right + 10, option_rect.centery)
                )
                SCREEN.blit(self.selection_icon, apple_rect)

        # Draw notes at the bottom with smaller font
        notes_text = "Press Enter or Space to select"
        notes_surface = self.notes_font.render(notes_text, True, Color.White.value)
        notes_rect = notes_surface.get_rect(
            center=(screen_center_x, CELL_NUMBER * CELL_SIZE - CELL_SIZE // 2)
        )
        SCREEN.blit(notes_surface, notes_rect)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                close_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.options)
                if event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.options)
                if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                    if self.selected_option == 1:
                        self.selected_skin = (self.selected_skin % len(self.skins)) + 1
                        self.options[1] = f"Costume:{self.skins[self.selected_skin - 1]}"
                    else:
                        return self.selected_option
        return None


def menu_screen(main_menu):
    while True:
        selected_option = main_menu.handle_input()
        main_menu.draw()
        pygame.display.update()
        CLOCK.tick(FRAMERATE)

        if selected_option == 0:  # Play
            return
        elif selected_option == 1:  # Skin Selection
            continue
        elif selected_option == 2:  # Quit
            close_game()


def game_screen(game):
    while True:
        game_over, score = main_Game.play_movements()

        if game_over:
            print('Final Score: ', score)

            # Show game over screen and ask if the player wants to try again
            result = game_over_screen()

            if result == "Yes":
                game.reset(main_Menu.selected_skin)
            elif result == "No":
                close_game()

        SCREEN.fill(Color.SCREEN.value)
        game.draw()
        pygame.display.update()
        CLOCK.tick(FRAMERATE)


# Game Over screen: Basically, the game screen freezes (we can make it black if we wanted to)
# Then some texts pop up
# The user selects either to continue playing or close the game
def game_over_screen():

    game_over_font = pygame.font.Font("Fonts/ARCADE_R.TTF", 45)
    try_again_font = pygame.font.Font("Fonts/ARCADE_R.TTF", 40)
    options_font = pygame.font.Font("Fonts/ARCADE_R.TTF", 30)

    # Center coordinates for the game-over screen
    go_screen_x = CELL_NUMBER * CELL_SIZE // 2
    go_screen_y = (CELL_NUMBER * CELL_SIZE // 2) - 20

    # Display Game Over text (size 60)
    game_over_text = game_over_font.render("Game Over", True, Color.Black.value)
    game_over_rect = game_over_text.get_rect(center=(go_screen_x, go_screen_y - CELL_SIZE * 2))
    SCREEN.blit(game_over_text, game_over_rect)

    # Display Try Again text (size 45)
    try_again_text = try_again_font.render("Try again?", True, Color.Black.value)
    try_again_rect = try_again_text.get_rect(center=(go_screen_x, go_screen_y))
    SCREEN.blit(try_again_text, try_again_rect)

    # Display Yes and No options (size 30)
    yes_option_text = options_font.render("Yes", True, Color.Black.value)
    yes_option_rect = yes_option_text.get_rect(center=(go_screen_x, go_screen_y + 1.5 * CELL_SIZE))

    no_option_text = options_font.render("No", True, Color.Black.value)
    no_option_rect = no_option_text.get_rect(center=(go_screen_x, go_screen_y + 3 * CELL_SIZE))

    selected_option_index = 0  # Default selected option is "Yes"

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                close_game()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    selected_option_index = (selected_option_index + 1) % 2

                elif event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                    return "Yes" if selected_option_index == 0 else "No"

        if selected_option_index == 0:
            yes_option_text = options_font.render("Yes", True, Color.White.value)
            no_option_text = options_font.render("No", True, Color.Black.value)
        elif selected_option_index == 1:
            yes_option_text = options_font.render("Yes", True, Color.Black.value)
            no_option_text = options_font.render("No", True, Color.White.value)

        SCREEN.blit(yes_option_text, yes_option_rect)
        SCREEN.blit(no_option_text, no_option_rect)

        pygame.display.update()


if __name__ == "__main__":
    main_Menu = Menu()  # First screen: Menu
    main_Game = Game()  # Second screen: Game
    menu_screen(main_Menu)  # Show menu to user
    main_Game.Snake.skin = main_Menu.selected_skin  # Which skin the user selected
    main_Game.Snake.load_skin(main_Game.Snake.skin)  # Whatever skin they selected, we put the correct skin images
    game_screen(main_Game)  # Game start! Enjoy Playing <3
