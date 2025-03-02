import pygame

SQUARE_SIZE = 100
SCREEN_WIDTH  = SQUARE_SIZE * 8
SCREEN_HEIGHT = SQUARE_SIZE * 8

COLORS = {
    pygame.K_1: (118, 150,  86), # Green
    pygame.K_2: ( 86, 118, 160), # Blue
    pygame.K_3: (180,  80,  80), # Red
    pygame.K_4: (150,  86, 150), # Purple
    pygame.K_5: (205, 153,  97), # Orange
    pygame.K_6: ( 95, 190, 135), # Teal
    pygame.K_7: (150, 150, 150), # Grey
}

pygame.init()
LABEL_FONT = pygame.font.Font(None, 32)
SMALL_FONT = pygame.font.Font(None, 45)
LARGE_FONT = pygame.font.Font(None, 90)
