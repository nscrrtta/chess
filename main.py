from constants import SQUARE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, COLORS
from objects import Game, Menu
import pygame


pygame.display.set_caption('Chess by Nick Sciarretta')
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

game = Game()
menu = Menu(game)
running = True

while running:
    piece_moved = False

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            file = x // SQUARE_SIZE
            rank = y // SQUARE_SIZE

            if menu.active:
                menu.mouse_button_down()

            elif game.pawn_promoting \
            and game.select_promotion(file, rank):
                piece_moved = True

            elif game.move_piece(file, rank):
                piece_moved = True

            else: game.select_piece(file, rank)

        elif event.type == pygame.MOUSEBUTTONUP:
            x, y = pygame.mouse.get_pos()
            file = x // SQUARE_SIZE
            rank = y // SQUARE_SIZE

            if menu.active:
                menu.mouse_button_up()

            elif game.pawn_promoting:
                pass

            elif game.move_piece(file, rank):
                piece_moved = True

        elif event.type == pygame.KEYDOWN:
            
            if event.key == pygame.K_ESCAPE:
                menu.toggle()

            elif event.key == pygame.K_f:
                game.flip()

            elif event.key == pygame.K_l:
                game.board.show_legal_moves = \
                not game.board.show_legal_moves

            elif event.key == pygame.K_LEFT:
                game.history.load_prev()

            elif event.key == pygame.K_RIGHT:
                game.history.load_next()

            elif event.key == pygame.K_UP:
                game.history.load_init()

            elif event.key == pygame.K_DOWN:
                game.history.load_curr()

            # Number keys 0 -> 9
            elif event.key in range(48, 58):
                game.board.dark_color = \
                menu.new_game_button.color = \
                menu.new_position_button.color = \
                COLORS.get(event.key, game.board.dark_color)

    if piece_moved and game.game_over():
        menu.update_text()
        menu.active = True

    game.draw(screen)
    if menu.active: menu.draw(screen)

    pygame.display.update()

pygame.quit()