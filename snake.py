import pygame,sys
pygame.init
screen = pygame.display.set_mode((500,500))
pygame.display.set_caption("snek")
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
