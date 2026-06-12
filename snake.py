import pygame, sys, random, os, math
from pygame.math import Vector2
from typing import List

pygame.init()

score_font = pygame.font.Font(None, 40)
title_font = pygame.font.Font(None, 60)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 40, 40)
DARK_GRAY = (30, 30, 30)
LIGHT_GRAY = (100, 100, 100)

cell_size = 18
number_of_cells = 31

OFFSET = 35
GRID_PIXELS = cell_size * number_of_cells
SCREEN_SIZE = 2 * OFFSET + GRID_PIXELS

screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
game_canvas = pygame.Surface((SCREEN_SIZE, SCREEN_SIZE))

pygame.display.set_caption("Snek")

clock = pygame.time.Clock()

food_surfaces = []
food_names = []

if os.path.exists("Graphics/eten"):
    for file in os.listdir("Graphics/eten"):
        if file.endswith(".png"):
            surface = pygame.image.load(os.path.join("Graphics/eten", file)).convert_alpha()
            food_surfaces.append(surface)
            food_names.append(file)

SKINS_CONFIG = [
    {"id": "cowboy",  "name": "Cowboy Snek",   "color": (139, 69, 19)},
    {"id": "ushanka", "name": "Ushanka Snek",  "color": (173, 216, 230)},
    {"id": "bonnet",  "name": "Bonnet Snek",   "color": (255, 182, 193)},
    {"id": "tophat",  "name": "Top Hat Snek",  "color": (245, 245, 220)},
    {"id": "dandy",   "name": "Dandy Snek",    "color": (220, 220, 220)},
    {"id": "giraffe", "name": "Giraffe Snek",  "color": (255, 222, 173)}
]

skin_surfaces = {}

if os.path.exists("Graphics/skins"):
    for skin in SKINS_CONFIG:
        head_path = f"Graphics/skins/{skin['id']}_head.png"
        body_path = f"Graphics/skins/{skin['id']}_body.png"

        skin_surfaces[skin['id']] = {
            "head": pygame.image.load(head_path).convert_alpha() if os.path.exists(head_path) else None,
            "body": pygame.image.load(body_path).convert_alpha() if os.path.exists(body_path) else None
        }

class Food:
    def __init__(self, snake_body: List[Vector2]) -> None:
        self.food_surfaces = food_surfaces
        self.is_spaceship = False
        self.is_hammer = False
        self.v_direction = 1
        self.movement_counter = 0
        self.respawn(snake_body)

    def draw(self, surface_target: pygame.Surface) -> None:
        food_rect = pygame.Rect(
            OFFSET + self.position.x * cell_size,
            OFFSET + self.position.y * cell_size,
            cell_size,
            cell_size
        )
        if hasattr(self, 'food'):
            if self.is_spaceship and self.v_direction == 1:
                rotated_spaceship = pygame.transform.rotate(self.food, 180)
                surface_target.blit(rotated_spaceship, food_rect)
            else:
                surface_target.blit(self.food, food_rect)
        else:
            pygame.draw.rect(surface_target, RED, food_rect, 0, 4)

    def generate_random_cell(self) -> Vector2:
        return Vector2(
            random.randint(0, number_of_cells - 1),
            random.randint(0, number_of_cells - 1)
        )

    def generate_random_pos(self, snake_body: List[Vector2]) -> Vector2:
        position = self.generate_random_cell()
        while position in snake_body:
            position = self.generate_random_cell()
        return position

    def respawn(self, snake_body: List[Vector2]) -> None:
        self.position = self.generate_random_pos(snake_body)
        self.movement_counter = 0
        if self.food_surfaces:
            idx = random.randint(0, len(self.food_surfaces) - 1)
            self.food = self.food_surfaces[idx]
            current_name = food_names[idx]
            self.is_spaceship = (current_name == "ruimteschip.png")
            self.is_hammer = (current_name == "hamer.png")
            if self.is_spaceship:
                self.v_direction = random.choice([-1, 1])

    def update(self) -> None:
        if self.is_spaceship:
            self.movement_counter += 1
            if self.movement_counter % 2 == 0:
                self.position.y += self.v_direction
                if self.position.y >= number_of_cells - 1:
                    self.position.y = number_of_cells - 1
                    self.v_direction = -1
                elif self.position.y <= 0:
                    self.position.y = 0
                    self.v_direction = 1

class Snake:
    def __init__(self) -> None:
        self.body = [Vector2(6, 9), Vector2(5, 9), Vector2(4, 9)]
        self.direction = Vector2(1, 0)
        self.add_segment = False
        self.current_skin_id = "cowboy"

        try:
            self.eat_sound = pygame.mixer.Sound("Sounds/eat.mp3")
            self.wall_hit_sound = pygame.mixer.Sound("Sounds/wall.mp3")
        except:
            self.eat_sound = None
            self.wall_hit_sound = None

    def draw(self, surface_target: pygame.Surface) -> None:
        skin_assets = skin_surfaces.get(self.current_skin_id, {"head": None, "body": None})
        skin_color = next(
            (s["color"] for s in SKINS_CONFIG if s["id"] == self.current_skin_id),
            WHITE
        )

        for i, segment in enumerate(self.body):
            segment_rect = (
                OFFSET + segment.x * cell_size,
                OFFSET + segment.y * cell_size,
                cell_size,
                cell_size
            )

            if i == 0:
                if skin_assets["head"]:
                    angle = 0
                    if self.direction == Vector2(0, -1):
                        angle = 0
                    elif self.direction == Vector2(0, 1):
                        angle = 180
                    elif self.direction == Vector2(-1, 0):
                        angle = 90
                    elif self.direction == Vector2(1, 0):
                        angle = -90
                    rotated_head = pygame.transform.rotate(skin_assets["head"], angle)
                    surface_target.blit(rotated_head, segment_rect)
                else:
                    pygame.draw.rect(surface_target, skin_color, segment_rect, 0, 4)
            else:
                if skin_assets["body"]:
                    previous_segment = self.body[i - 1]
                    segment_direction = previous_segment - segment
                    if segment_direction.x != 0:
                        rotated_body = pygame.transform.rotate(skin_assets["body"], 90)
                    else:
                        rotated_body = skin_assets["body"]
                    surface_target.blit(rotated_body, segment_rect)
                else:
                    pygame.draw.rect(surface_target, skin_color, segment_rect, 0, 7)

    def update(self) -> None:
        self.body.insert(0, self.body[0] + self.direction)
        if self.add_segment:
            self.add_segment = False
        else:
            self.body = self.body[:-1]

    def reset(self) -> None:
        self.body = [Vector2(6, 9), Vector2(5, 9), Vector2(4, 9)]
        self.direction = Vector2(1, 0)

class Game:
    def __init__(self) -> None:
        self.snake = Snake()
        self.food = Food(self.snake.body)
        self.state = "MENU"
        self.score = 0
        self.wobble_timer = 0
        self.selected_skin_index = 0

    def draw(self, surface_target: pygame.Surface) -> None:
        if self.state == "MENU":
            self.draw_menu_screen(surface_target)
        else:
            self.food.draw(surface_target)
            self.snake.draw(surface_target)
            if self.state == "STOPPED":
                self.draw_game_over_screen(surface_target)

    def update(self) -> None:
        if self.state == "RUNNING":
            self.snake.update()
            self.food.update()
            self.check_collision_with_food()
            self.check_collision_with_edges()
            self.check_collision_with_tail()

    def check_collision_with_food(self) -> None:
        if self.snake.body[0] == self.food.position:
            if self.food.is_hammer:
                self.wobble_timer = 120
            self.food.respawn(self.snake.body)
            self.snake.add_segment = True
            self.score += 1
            if self.snake.eat_sound:
                self.snake.eat_sound.play()

    def check_collision_with_edges(self) -> None:
        if (
            self.snake.body[0].x in [number_of_cells, -1]
            or self.snake.body[0].y in [number_of_cells, -1]
        ):
            self.game_over()

    def game_over(self) -> None:
        self.state = "STOPPED"
        if self.snake.wall_hit_sound:
            self.snake.wall_hit_sound.play()

    def reset_game(self) -> None:
        self.snake.reset()
        self.food.respawn(self.snake.body)
        self.score = 0
        self.wobble_timer = 0
        self.state = "RUNNING"

    def check_collision_with_tail(self) -> None:
        if self.snake.body[0] in self.snake.body[1:]:
            self.game_over()

    def draw_menu_screen(self, surface_target: pygame.Surface) -> None:
        center_x = SCREEN_SIZE // 2

        title_surf = title_font.render("SNEK SKIN SELECTION", True, WHITE)
        title_rect = title_surf.get_rect(center=(center_x, OFFSET + 40))
        surface_target.blit(title_surf, title_rect)

        current_skin = SKINS_CONFIG[self.selected_skin_index]

        card_rect = pygame.Rect(0, 0, 400, 250)
        card_rect.center = (center_x, SCREEN_SIZE // 2 - 20)
        pygame.draw.rect(surface_target, DARK_GRAY, card_rect, 0, 12)
        pygame.draw.rect(surface_target, RED, card_rect, 4, 12)

        name_surf = title_font.render(current_skin["name"], True, WHITE)
        name_rect = name_surf.get_rect(center=(center_x, SCREEN_SIZE // 2 - 80))
        surface_target.blit(name_surf, name_rect)

        preview_rect = pygame.Rect(0, 0, 60, 60)
        preview_rect.center = (center_x, SCREEN_SIZE // 2 + 10)

        assets = skin_surfaces.get(current_skin["id"], {"head": None})
        if assets["head"]:
            scaled_head = pygame.transform.scale(assets["head"], (60, 60))
            surface_target.blit(scaled_head, preview_rect)
        else:
            pygame.draw.circle(
                surface_target,
                current_skin["color"],
                preview_rect.center,
                30
            )

        nav_surf = score_font.render("< Gebruik Pijltjestoetsen >", True, LIGHT_GRAY)
        nav_rect = nav_surf.get_rect(center=(center_x, SCREEN_SIZE // 2 + 80))
        surface_target.blit(nav_surf, nav_rect)

        start_surf = score_font.render(
            "Druk op [ SPATIE ] om te starten",
            True,
            WHITE
        )
        start_rect = start_surf.get_rect(center=(center_x, SCREEN_SIZE - OFFSET - 60))
        surface_target.blit(start_surf, start_rect)

    def draw_game_over_screen(self, surface_target: pygame.Surface) -> None:
        center_x = SCREEN_SIZE // 2
        center_y = SCREEN_SIZE // 2

        menu_rect = pygame.Rect(0, 0, 420, 220)
        menu_rect.center = (center_x, center_y)
        pygame.draw.rect(surface_target, DARK_GRAY, menu_rect, 0, 12)
        pygame.draw.rect(surface_target, RED, menu_rect, 3, 12)

        over_surface = title_font.render("GAME OVER", True, RED)
        over_rect = over_surface.get_rect(center=(center_x, center_y - 50))

        score_surface = score_font.render(
            f"Final Score: {self.score}",
            True,
            WHITE
        )
        score_rect = score_surface.get_rect(center=(center_x, center_y + 5))

        retry_surface = score_font.render(
            "Press [ SPACE ] to Retry",
            True,
            WHITE
        )
        retry_rect = retry_surface.get_rect(center=(center_x, center_y + 55))

        surface_target.blit(over_surface, over_rect)
        surface_target.blit(score_surface, score_rect)
        surface_target.blit(retry_surface, retry_rect)

game = Game()

SNAKE_UPDATE = pygame.USEREVENT
pygame.time.set_timer(SNAKE_UPDATE, 200)

wobble_frame = 0

while True:
    for event in pygame.event.get():
        if event.type == SNAKE_UPDATE:
            game.update()
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if game.state == "MENU":
                if event.key == pygame.K_LEFT:
                    game.selected_skin_index = (
                        game.selected_skin_index - 1
                    ) % len(SKINS_CONFIG)
                elif event.key == pygame.K_RIGHT:
                    game.selected_skin_index = (
                        game.selected_skin_index + 1
                    ) % len(SKINS_CONFIG)
                elif event.key == pygame.K_SPACE:
                    game.snake.current_skin_id = SKINS_CONFIG[
                        game.selected_skin_index
                    ]["id"]
                    game.reset_game()
                continue

            if game.state == "STOPPED":
                if event.key == pygame.K_SPACE:
                    game.state = "MENU"
                continue

            if event.key == pygame.K_UP and game.snake.direction != Vector2(0, 1):
                game.snake.direction = Vector2(0, -1)
            elif event.key == pygame.K_DOWN and game.snake.direction != Vector2(0, -1):
                game.snake.direction = Vector2(0, 1)
            elif event.key == pygame.K_LEFT and game.snake.direction != Vector2(1, 0):
                game.snake.direction = Vector2(-1, 0)
            elif event.key == pygame.K_RIGHT and game.snake.direction != Vector2(-1, 0):
                game.snake.direction = Vector2(1, 0)

    if game.state == "RUNNING" and game.wobble_timer > 0:
        game.wobble_timer -= 1

    game_canvas.fill(BLACK)

    if game.state != "MENU":
        pygame.draw.rect(
            game_canvas,
            WHITE,
            (
                OFFSET - 5,
                OFFSET - 5,
                cell_size * number_of_cells + 10,
                cell_size * number_of_cells + 10
            ),
            5
        )

    game.draw(game_canvas)

    if game.state == "RUNNING":
        score_surface = score_font.render(
            f"Score: {game.score}",
            True,
            WHITE
        )
        game_canvas.blit(
            score_surface,
            (OFFSET, OFFSET + cell_size * number_of_cells + 10)
        )

    screen.fill(BLACK)

    if game.state == "RUNNING" and game.wobble_timer > 0:
        wobble_frame += 1
        for y in range(SCREEN_SIZE):
            offset_x = int(
                math.sin((y + wobble_frame * 5) * 0.05) * 8
            )
            screen.blit(
                game_canvas,
                (offset_x, y),
                (0, y, SCREEN_SIZE, 1)
            )
    else:
        screen.blit(game_canvas, (0, 0))

    pygame.display.update()
    clock.tick(60)