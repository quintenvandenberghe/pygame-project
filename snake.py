import pygame, sys, random, os
from pygame.math import Vector2

pygame.init()

score_font = pygame.font.Font(None, 40)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

cell_size = 18
number_of_cells = 31

OFFSET = 35
screen = pygame.display.set_mode((2*OFFSET + cell_size*number_of_cells, 2*OFFSET + cell_size*number_of_cells))

pygame.display.set_caption("Snek")

clock = pygame.time.Clock()

# Inladen van alle beschikbare textures
food_surfaces = []
if os.path.exists("Graphics/eten"):
    for file in os.listdir("Graphics/eten"):
        if file.endswith(".png"):
            surface = pygame.image.load(
                os.path.join("Graphics/eten", file)
            ).convert_alpha()
            food_surfaces.append(surface)

class Food:
    def __init__(self, snake_body):
        self.food_surfaces = food_surfaces
        self.respawn(snake_body) # Gebruik direct de nieuwe methode bij initialisatie

    def draw(self):
        food_rect = pygame.Rect(OFFSET + self.position.x * cell_size, OFFSET + self.position.y * cell_size, 
            cell_size, cell_size)
        screen.blit(self.food, food_rect)

    def generate_random_cell(self):
        x = random.randint(0, number_of_cells-1)
        y = random.randint(0, number_of_cells-1)
        return Vector2(x, y)

    def generate_random_pos(self, snake_body):
        position = self.generate_random_cell()
        while position in snake_body:
            position = self.generate_random_cell()
        return position

    # Nieuwe methode om zowel positie als texture te vernieuwen
    def respawn(self, snake_body):
        self.position = self.generate_random_pos(snake_body)
        if self.food_surfaces: # Controleer of de lijst niet leeg is
            self.food = random.choice(self.food_surfaces)

class Snake:
    def __init__(self):
        self.body = [Vector2(6, 9), Vector2(5,9), Vector2(4,9)]
        self.direction = Vector2(1, 0)
        self.add_segment = False
        self.eat_sound = pygame.mixer.Sound("Sounds/eat.mp3")
        self.wall_hit_sound = pygame.mixer.Sound("Sounds/wall.mp3")

    def draw(self):
        for segment in self.body:
            segment_rect = (OFFSET + segment.x * cell_size, OFFSET+ segment.y * cell_size, cell_size, cell_size)
            pygame.draw.rect(screen, WHITE, segment_rect, 0, 7)

    def update(self):
        self.body.insert(0, self.body[0] + self.direction)
        if self.add_segment == True:
            self.add_segment = False
        else:
            self.body = self.body[:-1]

    def reset(self):
        self.body = [Vector2(6,9), Vector2(5,9), Vector2(4,9)]
        self.direction = Vector2(1, 0)

class Game:
    def __init__(self):
        self.snake = Snake()
        self.food = Food(self.snake.body)
        self.state = "RUNNING"
        self.score = 0

    def draw(self):
        self.food.draw()
        self.snake.draw()

    def update(self):
        if self.state == "RUNNING":
            self.snake.update()
            self.check_collision_with_food()
            self.check_collision_with_edges()
            self.check_collision_with_tail()

    def check_collision_with_food(self):
        if self.snake.body[0] == self.food.position:
            self.food.respawn(self.snake.body) # Aangepast: verandert nu ook de texture!
            self.snake.add_segment = True
            self.score += 1
            self.snake.eat_sound.play()

    def check_collision_with_edges(self):
        if self.snake.body[0].x == number_of_cells or self.snake.body[0].x == -1:
            self.game_over()
        if self.snake.body[0].y == number_of_cells or self.snake.body[0].y == -1:
            self.game_over()

    def game_over(self):
        self.snake.reset()
        self.food.respawn(self.snake.body) # Ook bij Game Over krijgt het eten een nieuwe plek + texture
        self.state = "STOPPED"
        self.score = 0
        self.snake.wall_hit_sound.play()

    def check_collision_with_tail(self):
        headless_body = self.snake.body[1:]
        if self.snake.body[0] in headless_body:
            self.game_over()


game = Game()

SNAKE_UPDATE = pygame.USEREVENT
pygame.time.set_timer(SNAKE_UPDATE, 200)    

while True:
    for event in pygame.event.get():
        if event.type == SNAKE_UPDATE:
            game.update()
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if game.state == "STOPPED":
                game.state = "RUNNING"
            if event.key == pygame.K_UP and game.snake.direction != Vector2(0, -1):
                game.snake.direction = Vector2(0, -1)
            if event.key == pygame.K_DOWN and game.snake.direction != Vector2(0, 1):
                game.snake.direction = Vector2(0, 1)
            if event.key == pygame.K_LEFT and game.snake.direction != Vector2(1, 0):
                game.snake.direction = Vector2(-1, 0)
            if event.key == pygame.K_RIGHT and game.snake.direction != Vector2(-1, 0):
                game.snake.direction = Vector2(1, 0)

    #Drawing
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, 
        (OFFSET-5, OFFSET-5, cell_size*number_of_cells+10, cell_size*number_of_cells+10), 5)
    game.draw()
    score_text = f"Score: {game.score}"
    score_surface = score_font.render(score_text, True, WHITE)
    screen.blit(score_surface, (OFFSET, OFFSET + cell_size * number_of_cells + 10))

    pygame.display.update()
    clock.tick(60)