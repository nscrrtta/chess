from constants import SQUARE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, LABEL_FONT
from pieces import Piece
import pygame


class Board:

    def __init__(self, pieces: list[Piece]):
        self.pieces = pieces

        # Surface for transparent shapes
        self.transparent = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.transparent.set_colorkey((255, 255, 255))
        self.transparent.set_alpha(100)

        self.light_color = (238, 238, 210)
        self.dark_color = (118, 150, 86)

        self.rank_labels = list('87654321')
        self.file_labels = list('abcdefgh')

        self.show_legal_moves = True

    
    def reset(self):
        self.prev_square = (-1, -1)
        self.curr_square = (-1, -1)
        self.selected_piece: Piece | None = None

        self.update_occupied_squares()
        

    def update(self):
        self.prev_square = self.selected_piece.prev_square
        self.curr_square = self.selected_piece.curr_square
        self.selected_piece = None

        self.update_occupied_squares()
        
    
    def update_occupied_squares(self):
        self.occupied_squares = [
            piece.curr_square for piece in self.pieces
            if piece.captured is False]


    def flip(self):
        self.update_occupied_squares()

        self.rank_labels.reverse()
        self.file_labels.reverse()

        file, rank = self.prev_square
        self.prev_square = (7-file, 7-rank)

        file, rank = self.curr_square
        self.curr_square = (7-file, 7-rank)
    

    def draw(self, screen: pygame.Surface):
        self.transparent.fill((255, 255, 255, 0))

        self.draw_board(screen)
        self.draw_labels(screen)
        self.highlight_yellow_squares()
        self.highlight_allowed_squares()

        screen.blit(self.transparent, (0, 0))

    
    def draw_board(self, screen: pygame.Surface):
        for rank in range(8):
            for file in range(8):
                color = self.dark_color if (rank + file) % 2 else self.light_color
                rect = pygame.Rect(
                    SQUARE_SIZE * file,
                    SQUARE_SIZE * rank,
                    SQUARE_SIZE,
                    SQUARE_SIZE)
                pygame.draw.rect(screen, color, rect)
    

    def draw_labels(self, screen: pygame.Surface):
        for rank, number in enumerate(self.rank_labels):
            color = self.light_color if rank % 2 else self.dark_color
            screen.blit(
                LABEL_FONT.render(number, True, color),
                (5, rank*SQUARE_SIZE + 5))

        for file, letter in enumerate(self.file_labels):
            color = self.dark_color if file % 2 else self.light_color
            screen.blit(
                LABEL_FONT.render(letter, True, color),
                (file*SQUARE_SIZE + 85, SCREEN_HEIGHT - 25))

    
    def highlight_yellow_squares(self):
        prev_move = [self.prev_square, self.curr_square]

        for file, rank in prev_move:
            pygame.draw.rect(
                surface=self.transparent,
                color=(252, 219, 28),
                rect = pygame.Rect(
                    SQUARE_SIZE * file,
                    SQUARE_SIZE * rank,
                    SQUARE_SIZE,
                    SQUARE_SIZE))
        
        if self.selected_piece is None \
        or self.selected_piece.curr_square in prev_move:
            return

        pygame.draw.rect(
            surface=self.transparent,
            color=(252, 219, 28),
            rect = pygame.Rect(
                SQUARE_SIZE * self.selected_piece.file,
                SQUARE_SIZE * self.selected_piece.rank,
                SQUARE_SIZE,
                SQUARE_SIZE))


    def highlight_allowed_squares(self):
        if self.show_legal_moves is False \
        or self.selected_piece is None: return
        
        for file, rank in self.selected_piece.allowed_squares:
            # If a square is occupied it gets a circle,
            # otherwise it gets a dot
            occupied = (file, rank) in self.occupied_squares

            pygame.draw.circle(
                surface=self.transparent,
                color=(90, 90, 90),
                center=((file + 0.5) * SQUARE_SIZE, (rank + 0.5) * SQUARE_SIZE),
                radius=50 if occupied else 15,
                width=8 if occupied else 0)
