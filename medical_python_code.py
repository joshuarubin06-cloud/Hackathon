import pygame

pygame.init()

# Window setup
WIDTH, HEIGHT = 600, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Body Health Viewer")

clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)

running = True

while running:
    clock.tick(60)
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.update()

pygame.quit()