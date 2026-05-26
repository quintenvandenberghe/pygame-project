import pygame
import sys
import random

# --- CONSTANTEN ---
BREEDTE, HOOGTE = 500, 500
FPS = 15
GRID = 20

# --- KLEUREN ---
ZWART = (0, 0, 0)
GROEN = (0, 255, 0)
ROOD = (255, 0, 0)
WIT = (255, 255, 255)

class Snake:
    def __init__(self):
        self.lichaam = [(100, 100), (80, 100), (60, 100)]
        self.richting = (GRID, 0)
        self.groei = False

    def bewegen(self):
        hoofd = (self.lichaam[0][0] + self.richting[0], self.lichaam[0][1] + self.richting[1])
        self.lichaam.insert(0, hoofd)
        if not self.groei:
            self.lichaam.pop()
        else:
            self.groei = False

    def botsing(self):
        hoofd = self.lichaam[0]
        # Botsing met zichzelf
        if hoofd in self.lichaam[1:]:
            return True
        # Botsing met muur
        x, y = hoofd
        if x < 0 or x >= BREEDTE or y < 0 or y >= HOOGTE:
            return True
        return False

    def verander_richting(self, richting):
        # Voorkom omkeren
        if (richting[0] * -1, richting[1] * -1) != self.richting:
            self.richting = richting

class Apple:
    def __init__(self):
        self.pos = self.nieuwe_positie()

    def nieuwe_positie(self):
        return (random.randrange(0, BREEDTE, GRID), random.randrange(0, HOOGTE, GRID))

    def tekenen(self, scherm):
        pygame.draw.rect(scherm, ROOD, (*self.pos, GRID, GRID))

class Game:
    def __init__(self):
        pygame.init()
        self.scherm = pygame.display.set_mode((BREEDTE, HOOGTE))
        pygame.display.set_caption("Snake")
        self.klok = pygame.time.Clock()
        self.snake = Snake()
        self.apple = Apple()
        self.score = 0

    def reset(self):
        self.snake = Snake()
        self.apple = Apple()
        self.score = 0

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.snake.verander_richting((0, -GRID))
                    elif event.key == pygame.K_DOWN:
                        self.snake.verander_richting((0, GRID))
                    elif event.key == pygame.K_LEFT:
                        self.snake.verander_richting((-GRID, 0))
                    elif event.key == pygame.K_RIGHT:
                        self.snake.verander_richting((GRID, 0))

            self.snake.bewegen()

            # Check appel
            if self.snake.lichaam[0] == self.apple.pos:
                self.snake.groei = True
                self.apple.pos = self.apple.nieuwe_positie()
                self.score += 1

            # Check botsing
            if self.snake.botsing():
                self.reset()

            # Teken alles
            self.scherm.fill(ZWART)
            for blok in self.snake.lichaam:
                pygame.draw.rect(self.scherm, GROEN, (*blok, GRID, GRID))
            self.apple.tekenen(self.scherm)

            # Score tonen
            font = pygame.font.SysFont(None, 36)
            score_img = font.render(f"Score: {self.score}", True, WIT)
            self.scherm.blit(score_img, (10, 10))

            pygame.display.flip()
            self.klok.tick(FPS)

if __name__ == "__main__":
    Game().run()