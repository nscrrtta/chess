import functions as fnc
import pygame


pygame.init()
pygame.display.set_caption('Chess by Nick Sciarretta')


# Screen that everything is drawn onto
screen = pygame.display.set_mode((800, 800))

# Separate surface for transparent shapes
surface = pygame.Surface((800,800))
surface.set_colorkey((255,255,255))
surface.set_alpha(100)



class Game:

    def __init__(self):
        
        self.gui = GUI(self)
        self.new_game(True)


    def new_game(self, new_pos=False, fischer_random=False):

        # Create new starting position
        if new_pos or (self.fischer_random != fischer_random):
            self.start_pos = fnc.get_start_pos(fischer_random)
            self.fischer_random = fischer_random

        self.pos = [row[:] for row in self.start_pos]
        self.fmr = 0 # Fifty move rule counter
        self.wtm = True # White to move
        
        self.pawn_promoting = False
        self.sound_effect = 'nothing'

        self.history = []
        self.update()


    def make_move(self, sqr1: tuple, sqr2: tuple):

        pos = [row[:] for row in self.pos] # Make copy of position
        self.fmr += 0.5 # Half move was made
        self.sound_effect = 'move'
        
        f1,r1 = sqr1; p1 = pos[r1][f1] # Moving from
        f2,r2 = sqr2; p2 = pos[r2][f2] # Moving to
        
        # Clear old square
        pos[r1][f1] = '--'

        # Clear en passant square
        for f,r in fnc.sqrs:
            if pos[r][f] == '-e': pos[r][f] = '--'

        # Capture was made
        if p2 != '--': 
            self.sound_effect = 'capture'
            self.fmr = 0 # Reset fifty move rule counter

        # Pawn moved
        if p1 in ['P-', 'p-']:

            rank_behind = r2+1 if self.wtm else r2-1
            self.fmr = 0 # Reset fifty move rule counter
            
            # Captured en passant
            if p2 == '-e': pos[rank_behind][f2] = '--' 

            # Jumped two ranks
            elif abs(r2-r1) == 2: pos[rank_behind][f2] = '-e' 

            # Reached final rank
            elif r2 == {1:0,0:7}[self.wtm]: self.pawn_promoting = True

        # King made first move
        elif p1 in ['K+', 'k+']: 

            back_rank = 7 if self.wtm else 0
            rook = 'R+' if self.wtm else 'r+'
            
            # Castled short
            if sqr2 == (6,back_rank) and fnc.can_castle_short(self.wtm, self.pos):
                # Move king-side rook
                rook_file = pos[back_rank][f1:].index(rook)+f1
                pos[back_rank][rook_file] = '--' 
                pos[back_rank][5] = rook[0]+'-'
                self.sound_effect = 'castle'

            # Castled long
            elif sqr2 == (2,back_rank) and fnc.can_castle_long(self.wtm, self.pos): 
                # Move queen-side rook
                rook_file = pos[back_rank].index(rook)
                pos[back_rank][rook_file] = '--'
                pos[back_rank][3] = rook[0]+'-'
                self.sound_effect = 'castle'

        # Place moved piece on new square
        pos[r2][f2] = p1[0]+'-'

        self.pos = pos

        if self.pawn_promoting:
            self.gui.promo_file = sqr2[0]
        else:
            self.wtm = not self.wtm
            self.update()


    def promote_pawn(self, promotion: str, file: int):

        self.pos[0 if self.wtm else 7][file] = promotion+'-'
        self.pawn_promoting = False
        self.wtm = not self.wtm
        self.update()

    
    def update(self):

        # Update legal moves dictionary / Count minor pieces
        self.lmd = {}
        num_minor_pcs = num_other_pcs = 0

        for sqr in fnc.sqrs:

            f,r = sqr
            p = self.pos[r][f][0]

            if   p.upper() in ['B','N']: num_minor_pcs += 1
            elif p.upper() in ['P','R','Q']: num_other_pcs += 1

            if fnc.is_friend(self.wtm, sqr, self.pos):
                l = fnc.get_squares(sqr, self.pos)
                if l: self.lmd[sqr] = l

        # Save (copy of) current position+legal moves
        pos = [row[:] for row in self.pos]
        for f,r in fnc.sqrs: pos[r][f] = pos[r][f][0]
        self.history.append((pos,self.lmd.copy()))

        # Check if in check
        in_check = fnc.king_in_check(self.wtm, self.pos)
        if in_check: self.sound_effect = 'check'

        ######################## CHECK IF GAME OVER ########################
        self.game_over_id = 0

        # No legal moves
        if not self.lmd:
            if in_check: self.game_over_id = 1+self.wtm # Checkmate
            else: self.game_over_id = 3 # Stalemate

        # Insufficient material
        elif num_minor_pcs <= 1 and num_other_pcs == 0:
            self.game_over_id = 4 

        # Draw by fifty move rule
        elif self.fmr == 50:
            self.game_over_id = 5 

        # Draw by repitition
        # Same position has been reached 3 times with the same legal moves
        elif self.history.count((pos, self.lmd)) == 3:
            self.game_over_id = 6
        ####################################################################

        self.gui.save()



class GUI:

    def __init__(self, game: Game):

        # Playing pieces
        # Creating a Piece object loads an image
        # By using this dictionary, only 12 images need to be loaded
        self.piece_dict = {
            'K': Piece('white_king',   'K'), 'k': Piece('black_king',   'k'),
            'Q': Piece('white_queen',  'Q'), 'q': Piece('black_queen',  'q'),
            'R': Piece('white_rook',   'R'), 'r': Piece('black_rook',   'r'),
            'B': Piece('white_bishop', 'B'), 'b': Piece('black_bishop', 'b'),
            'N': Piece('white_knight', 'N'), 'n': Piece('black_knight', 'n'),
            'P': Piece('white_pawn',   'P'), 'p': Piece('black_pawn',   'p'),
        }

        # Promotion pieces
        self.promo_dict = {
            True: [ # White pieces
                self.piece_dict['Q'],
                self.piece_dict['R'],
                self.piece_dict['B'],
                self.piece_dict['N']
            ],
            False: [ # Black pieces
                self.piece_dict['q'],
                self.piece_dict['r'],
                self.piece_dict['b'],
                self.piece_dict['n']
            ]
        }

        # Font for labeling files and ranks
        self.font = pygame.font.Font(None, 32)

        # Colours of board
        self.colours = [(238,238,210), (118,150,86)]

        # Radius of squares
        self.border_radius = 0

        # If True: a1 square in bottom left corner
        self.white_pov = True

        self.show_legal_moves = True
        self.show_yellow_sqrs = True

        self.game = game
        self.menu = Menu(self)

        self.new_game()


    def new_game(self):

        self.history = []
        
        # Sqaures that get transparent yellow square
        self.recent_move = []
        self.clicked_sqr = []

        # Squares that get a transparent grey circle/ring
        self.legal_moves = []
        
        # File of pawn that is promoting
        self.promo_file: int

        # Play sound effect
        pygame.mixer.Sound(f'wavs/gamestart.wav').play()


    def move(self, sqr: tuple) -> bool:

        if self.game.pawn_promoting:

            for piece in self.promo_dict[self.game.wtm]:
                if piece.rect.collidepoint(pygame.mouse.get_pos()):
                    self.game.promote_pawn(piece.piece_id, self.promo_file)
                    return True

        if sqr in self.legal_moves:

            self.recent_move = [self.clicked_sqr[0], sqr]
            self.game.make_move(self.clicked_sqr.pop(0), sqr)
            return True
            
        return False


    def slct(self, sqr: tuple):

        file, rank = sqr

        self.clicked_sqr = []
        self.legal_moves = []
        
        piece = self.game.pos[rank][file][0]
        if piece != '-': self.clicked_sqr = [sqr]

        if (
        sqr in self.game.lmd
        and self.game.game_over_id == 0
        and not self.game.pawn_promoting
        and self.index == len(self.history)-1
        ): self.legal_moves = self.game.lmd[sqr]


    def save(self):

        self.clicked_sqr = []
        self.legal_moves = []

        self.history.append((
            [row[:] for row in self.game.pos],
            self.recent_move[:],
            self.game.sound_effect
        ))

        self.index = len(self.history)-1
        pygame.mixer.Sound(f'wavs/{self.game.sound_effect}.wav').play()

        if self.game.game_over_id == 0: return

        self.menu.active = True
        self.menu.update_scores()
        pygame.mixer.Sound('wavs/gameover.wav').play()


    def load(self, i):

        if i == 'prev':
            if self.index == 0: return
            else: self.index -= 1

        elif i == 'open':
            if self.index == 0: return
            else: self.index = 0

        elif i == 'next':
            if self.index == len(self.history)-1: return
            else: self.index += 1

        elif i == 'curr':
            if self.index == len(self.history)-1: return
            else: self.index = len(self.history)-1

        self.clicked_sqr = []
        self.legal_moves = []

        pos, recent_move, sound_effect = self.history[self.index]

        self.game.pos = [row[:] for row in pos]
        self.recent_move = recent_move[:]

        pygame.mixer.Sound(f'wavs/{sound_effect}.wav').play()


    def draw(self):


        def draw_board():

            # Draw squares
            for i,j in fnc.sqrs: pygame.draw.rect(
                screen, self.colours[(i+j)%2],
                pygame.Rect(i*100,j*100,100,100), 
                border_radius=self.border_radius
            )

            for i in range(8): 
                # Label ranks
                screen.blit(self.font.render(
                str(8-i if self.white_pov else i+1),
                True, self.colours[(i+1)%2]),
                (5, i*100+5))

                # Label files
                screen.blit(self.font.render(
                'abcdefgh'[i if self.white_pov else 7-i],
                True, self.colours[i%2]),
                (i*100+85, 775)
                )

        
        def draw_surface():

            # Clear surface of all transparent grey circles/rings and yellow squares
            surface.fill((255,255,255,0))

            # Draw yellow squares (pressed square / previous move)
            for i,j in self.recent_move + self.clicked_sqr:

                rank = j if self.white_pov else 7-j
                file = i if self.white_pov else 7-i

                if self.show_yellow_sqrs: pygame.draw.rect(
                    surface, (252,219,28), # Yellow
                    pygame.Rect(file*100,rank*100,100,100),
                    border_radius=self.border_radius
                )

            # Draw grey circles/rings (legal moves)
            for i,j in self.legal_moves:

                rank = j if self.white_pov else 7-j
                file = i if self.white_pov else 7-i

                # Small circle if square empty,
                # Large ring if square occupied
                empty = self.game.pos[j][i][0] == '-'

                if self.show_legal_moves: pygame.draw.circle(
                    surface, (90,90,90), # Grey
                    ((file+0.5)*100, (rank+0.5)*100),
                    15 if empty else 50, # Radius
                    0  if empty else 8   # Width
                )

            screen.blit(surface, (0,0))

        
        def draw_pieces():

            x = self.clicked_sqr and not self.menu.active and pygame.mouse.get_pressed()[0]

            # Draw static pieces
            for i,j in fnc.sqrs:

                # Skip square that was pressed
                if x and (i,j) in self.clicked_sqr: continue

                rank = j if self.white_pov else 7-j
                file = i if self.white_pov else 7-i

                piece = self.game.pos[j][i][0]
                if piece == '-': continue

                self.piece_dict[piece].draw((file,rank))

            # Draw held piece (if there is one)
            if not x: return

            i,j = self.clicked_sqr[0]
            piece = self.game.pos[j][i][0]

            self.piece_dict[piece].draw(held=True)


        def draw_promotions():

            f = self.promo_file if self.white_pov else 7-self.promo_file
            r,d = (4,-1) if self.white_pov != self.game.wtm else (0,1)

            # Draw grey rectangle + black border
            pygame.draw.rect(screen,(220,220,220),pygame.Rect(f*100,r*100,100,400),0,15)
            pygame.draw.rect(screen,(0,0,0),pygame.Rect(f*100,r*100,100,400),1,15)
    
            # Drawn promo pieces
            for i, piece in enumerate(self.promo_dict[self.game.wtm][::d]):
                piece.draw((f,i+r))


        screen.fill(self.colours[0])

        draw_board()
        draw_surface()
        draw_pieces()

        if self.game.pawn_promoting: draw_promotions()
        if self.menu.active: self.menu.draw()



class Piece:

    def __init__(self, png: str, piece_id: str):

        self.png = png
        self.piece_id = piece_id

        # Load image from 'pngs' directory
        self.image = pygame.image.load(f'pngs/{png}.png')
        self.rect  = self.image.get_rect()


    def draw(self, sqr=(0,0), held=False):

        i,j = sqr

        self.rect.center = (i+0.5)*100, (j+0.5)*100
        self.rect.bottom = (j+1.0)*100 - 8

        if held: self.rect.center = pygame.mouse.get_pos()

        screen.blit(self.image, self.rect)



class Menu:

    def __init__(self, gui: GUI):

        self.gui = gui
        self.active = False

        # Buttons
        self.new_game_btn = Button(400, 445, text='New Game')
        self.new_pos_btn  = Button(400, 595, text='New Position')
        self.new_pos_btn.colours = [(180,180,180), (110,110,110)]

        # Checkbox
        self.fr_checkbox = CheckBox(273, 523, 30, 30)
        self.fr_checkbox.load_image()

        # Large / small fonts
        self.large_font = pygame.font.Font(None, 100)
        self.small_font = pygame.font.Font(None, 44)

        # White pawn
        self.white_pawn = self.gui.piece_dict['P'].image
        self.white_pawn_rect = self.white_pawn.get_rect()
        self.white_pawn_rect.center = (300,340)

        # Black pawn
        self.black_pawn = self.gui.piece_dict['p'].image
        self.black_pawn_rect = self.black_pawn.get_rect()
        self.black_pawn_rect.center = (500,340)

        # Scores
        self.white_score = self.black_score = 0.0

        # Game over dictionary
        self.d = {
            0: (0.0, 0.0, 'Main Menu',   ''),
            1: (1.0, 0.0, 'White Wins!', 'By Checkmate'),
            2: (0.0, 1.0, 'Black Wins!', 'By Checkmate'),
            3: (0.5, 0.5, 'Draw!',       'By Stalemate'), 
            4: (0.5, 0.5, 'Draw!',       'By Insufficient Material'),
            5: (0.5, 0.5, 'Draw!',       'By Fifty-Move Rule'),
            6: (0.5, 0.5, 'Draw!',       'By Repetition')
        }


    def update_scores(self):

        self.white_score += self.d[self.gui.game.game_over_id][0]
        self.black_score += self.d[self.gui.game.game_over_id][1]


    def click(self):

        if self.new_game_btn.mouse_over():
            self.new_game_btn.pressed = True

        elif self.fr_checkbox.mouse_over():
            self.fr_checkbox.pressed = not self.fr_checkbox.pressed

        if self.fr_checkbox.pressed:
            self.new_pos_btn.colours = [(118,150,86), (76,105,51)]
        else:
            self.new_pos_btn.colours = [(180,180,180), (110,110,110)]
            return

        if self.new_pos_btn.mouse_over():
            self.new_pos_btn.pressed = True


    def release(self):

        fr = self.fr_checkbox.pressed

        for i, btn in enumerate([self.new_game_btn, self.new_pos_btn]):
            if btn.mouse_over() and btn.pressed:

                self.gui.new_game()
                self.gui.game.new_game(i, fr)
                self.active = btn.pressed = False

                break

    
    def draw(self):

        # Transparent background
        pygame.draw.rect(surface, (70,70,70), pygame.Rect(0,0,800,800))
        screen.blit(surface, (0,0))

        # Grey square + black border
        pygame.draw.rect(screen,(90,90,90),pygame.Rect(150,150,500,500),0,8)
        pygame.draw.rect(screen,(0,0,0),pygame.Rect(150,150,500,500),1,8)

        # Texts
        strings = [
            self.d[self.gui.game.game_over_id][2],
            self.d[self.gui.game.game_over_id][3],
            f'{self.white_score}  -  {self.black_score}',
            'Fischer Random'
        ]
        fonts = [
            self.large_font, 
            self.small_font, 
            self.small_font, 
            self.small_font]
        centers = [
            (400,200),
            (400,255),
            (400,340),
            (420,525)
        ]

        for string, font, center in zip(strings, fonts, centers):
            text = font.render(string, True, (250,250,250))
            rect = text.get_rect()
            rect.center = center
            screen.blit(text, rect)

        # Pieces
        screen.blit(self.white_pawn, self.white_pawn_rect)
        screen.blit(self.black_pawn, self.black_pawn_rect)
        
        # Buttons / checkbox
        self.new_game_btn.draw()
        self.new_pos_btn.draw()
        self.fr_checkbox.draw()
  


class Button:

    def __init__(self, x_pos: int, y_pos: int, width=350, height=60, text=''):

        self.center = (x_pos, y_pos)
        self.width, self.height = width, height

        self.y_pos = y_pos - self.height/2
        self.x_pos = x_pos - self.width/2

        self.pressed = False

        self.font = pygame.font.Font(None, 53)
        self.text = self.font.render(text, True, (250,250,250))
        self.text_rect = self.text.get_rect()

        self.colours = [(118,150,86), (76,105,51)]


    def mouse_over(self) -> bool:

        x,y = pygame.mouse.get_pos()

        return (self.x_pos < x < self.x_pos+self.width
        and     self.y_pos < y < self.y_pos+self.height)


    def draw(self):

        if self.pressed and not self.mouse_over(): self.pressed = False

        # Accent colour
        rect = pygame.Rect(self.x_pos, self.y_pos+7, self.width, self.height)
        pygame.draw.rect(screen, self.colours[1], rect, 0, 10)

        # Normal colour
        rect = pygame.Rect(self.x_pos, self.y_pos+self.pressed*3, self.width, self.height)
        pygame.draw.rect(screen, self.colours[0], rect, 0, 10)

        # Text
        x,y = self.center
        y += self.pressed*3 + 3
        self.text_rect.center = (x,y)
        screen.blit(self.text, self.text_rect)



class CheckBox(Button):

    def load_image(self):

        self.image = pygame.image.load('pngs/checkmark.png')
        self.rect  = self.image.get_rect()
        self.rect.center = self.center

    
    def draw(self):

        rect = pygame.Rect(self.x_pos, self.y_pos, self.width, self.height)

        # Grey rectangle / black border
        pygame.draw.rect(screen, (180,180,180), rect, 0, 8)
        pygame.draw.rect(screen, (0,0,0), rect, 1, 8)

        # Checkmark
        if self.pressed: screen.blit(self.image, self.rect)
