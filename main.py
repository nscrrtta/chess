from game import Game
import threading
import pygame
import time


game = Game()
gui = game.gui
running = True

fade = False
speed = 0.1


def fade_thread():

    # Changes colour of dark squares on board
    # red -> yellow -> green -> turquoise -> blue -> purple (repeat)

    i = 0; j = 0; x = [180,70,70]
    l = [[0,1,0],[-1,0,0],[0,0,1],[0,-1,0],[1,0,0],[0,0,-1]]

    while running:

        time.sleep(0.1) # Wait for fade == True

        while running and fade:

            gui.colours = [(238,238,210),tuple(x)]
            x = [x[k] + l[i][k] for k in range(3)]

            if j == 110: i, j = (i+1)%len(l), 0
            else: j += 1

            time.sleep(speed)

threading.Thread(target=fade_thread).start()


# Main while loop
while running:

    x,y = pygame.mouse.get_pos()

    # Square size = 100 px
    file = x//100 if gui.white_pov else 7-x//100
    rank = y//100 if gui.white_pov else 7-y//100

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # Mouse click will move/select piece
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if gui.menu.active: gui.menu.click()
            elif not gui.move((file,rank)): gui.slct((file,rank))

        # Mouse release will move piece
        elif event.type == pygame.MOUSEBUTTONUP:
            if gui.menu.active: gui.menu.release()
            elif not gui.game.pawn_promoting: gui.move((file,rank))

        # Key press
        elif event.type == pygame.KEYDOWN:

            # Toggle menu
            if event.key == pygame.K_ESCAPE:
                gui.menu.active = not gui.menu.active

            ############# CHANGE COLOURS OF BOARD #############
            elif event.key == pygame.K_1: # Green (standard)
                gui.colours = [(238,238,210),(118,150,86)]
                fade = False

            elif event.key == pygame.K_2: # Blue
                gui.colours = [(238,238,210),(86,118,160)]
                fade = False

            elif event.key == pygame.K_3: # Red
                gui.colours = [(238,238,210),(180,80,80)]
                fade = False

            elif event.key == pygame.K_4: # Purple
                gui.colours = [(238,238,210),(150,86,150)]
                fade = False

            elif event.key == pygame.K_5: # Orange
                gui.colours = [(238,238,210),(205,153,97)]
                fade = False

            elif event.key == pygame.K_6: # Teal
                gui.colours = [(238,238,210),(95,190,135)]
                fade = False

            elif event.key == pygame.K_7: # Grey
                gui.colours = [(238,238,210),(150,150,150)]
                fade = False

            elif event.key == pygame.K_8: # Slow fade
                fade = True; speed = 0.1

            elif event.key == pygame.K_9: # Fast fade
                fade = True; speed = 0.005

            elif event.key == pygame.K_0: # Pause fade
                fade = not fade
            ###################################################


            ############# CHANGE SHAPE OF SQUARES #############
            elif event.key == pygame.K_MINUS:
                gui.border_radius = 0

            elif event.key == pygame.K_EQUALS:
                gui.border_radius = 8
            ###################################################


            ############### TOGGLE GUI VARIABLES ##############
            # Toggle white pov
            elif event.key == pygame.K_f:
                gui.white_pov = not gui.white_pov

            # Toggle show legal moves
            elif event.key == pygame.K_l:
                gui.show_legal_moves = not gui.show_legal_moves

            # Toggle show recent move / clicked square
            elif event.key == pygame.K_y:
                gui.show_yellow_sqrs = not gui.show_yellow_sqrs
            ###################################################


            ############# NAVIGATE BETWEEN MOVES ##############
            # Can't navigate while pawn is promoting
            if gui.game.pawn_promoting: pass

            elif event.key == pygame.K_UP:    gui.load('open')

            elif event.key == pygame.K_DOWN:  gui.load('curr')

            elif event.key == pygame.K_LEFT:  gui.load('prev')

            elif event.key == pygame.K_RIGHT: gui.load('next') 
            ###################################################

    gui.draw()
    pygame.display.update()


pygame.quit()