from constants import SQUARE_SIZE
import pygame


class Piece:

    def __init__(self, color: str, png: str):
        self.start_rank = {'white': 7, 'black': 0}[color]
        
        image = pygame.image.load(f'pngs/{color}_{png}.png')
        self.set_image(image)
        
        self.friends: list[Piece] = []
        self.enemies: list[Piece] = []

        self.allowed_squares: list[tuple[int, int]] = []
        self.captured_piece: Piece | None = None

        self.regular_file = -1
        self.fischer_file = -1

    
    def set_image(self, image: pygame.Surface):
        self.image = image
        self.rect = image.get_rect()
        

    def reset(self, fischer_random: bool):
        self.has_moved = \
        self.captured = \
        self.held = False
        
        file = self.fischer_file if fischer_random else self.regular_file
        self.place((file, self.start_rank))
        self.prev_square = (-1, -1)

    
    def occupied(self, square: tuple[int, int]) -> bool:
        return self.occupied_by_friend(square) \
            or self.occupied_by_enemy(square)
    

    def occupied_by_friend(self, square: tuple[int, int]) -> bool:
        for piece in self.friends:
            if piece.captured: pass
            elif piece.curr_square == square: return True
        return False
    

    def occupied_by_enemy(self, square: tuple[int, int]) -> bool:
        for piece in self.enemies:
            if piece.captured: pass
            elif piece.curr_square == square: return True
        return False
    
    
    def place(self, square: tuple[int, int]):
        self.file, self.rank = self.curr_square = square
        self.rect.center = (self.file + 0.5) * SQUARE_SIZE, \
                           (self.rank + 0.5) * SQUARE_SIZE
        self.rect.bottom = (self.rank + 1.0) * SQUARE_SIZE - 8
        self.held = False

    
    def move(self, square: tuple[int, int], temporary=False):
        self.captured_piece = self.get_captured_piece(square)

        if self.captured_piece is not None:
            self.captured_piece.captured = True

        self.prev_square = self.curr_square
        self.curr_square = square

        if temporary: return
        self.has_moved = True
        self.place(square)

    
    def undo_move(self, square: tuple[int, int]):
        if self.captured_piece is not None:
            self.captured_piece.captured = False
            self.captured_piece = None

        self.curr_square = self.prev_square
        self.prev_square = square

    
    def get_captured_piece(self, square: tuple[int, int]):
        for piece in self.enemies:
            if piece.captured: pass
            elif piece.curr_square == square: return piece
        return None
    
    
    def flip(self):
        # Flip starting squares
        self.start_rank = 7-self.start_rank
        self.regular_file = 7-self.regular_file
        self.fischer_file = 7-self.fischer_file

        # Flip current square
        self.place((7-self.file, 7-self.rank))

        # Flip allowed squares
        for i, (file, rank) in enumerate(self.allowed_squares):
            self.allowed_squares[i] = (7-file, 7-rank)
    

    def draw(self, screen: pygame.Surface):
        if self.held: self.rect.center = pygame.mouse.get_pos()
        screen.blit(self.image, self.rect)
