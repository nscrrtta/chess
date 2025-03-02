from pieces import Pawn, Knight, Bishop, Rook, Queen, King
from constants import SQUARE_SIZE, SCREEN_WIDTH
import pygame


class Player:

    def __init__(self, color: str):
        self.opponent: Player = None

        self.king = King(color)
        self.k_rook = Rook(color) # king-side rook
        self.q_rook = Rook(color) # queen-side rook

        self.pieces: list[Pawn | Knight | Bishop | Rook | Queen | King] = []
        self.pieces.extend([Pawn(color) for _ in range(8)])

        # Pieces on back rank from files a -> h
        self.pieces.extend([
            self.q_rook,
            Knight(color),
            Bishop(color),
            Queen (color),
            self.king,
            Bishop(color),
            Knight(color),
            self.k_rook])
        
        for file, piece in enumerate(self.pieces):
            piece.regular_file = file % 8

        self.promotions:list[Queen | Rook | Bishop | Knight] = ([
            Queen (color),
            Rook  (color),
            Bishop(color),
            Knight(color)])
        if color == 'black': self.promotions.reverse()

        self.score = 0.0
    
    
    def king_in_check(self) -> bool:
        return self.king.curr_square in self.opponent.guarded_squares


    def no_legal_moves(self) -> bool:
        for piece in self.pieces:
            if piece.captured: pass
            elif piece.allowed_squares: return False
        return True


    def insufficient_material(self) -> bool:
        # Count number of knights and bishops
        count = 0

        for piece in self.pieces:
            if piece.captured \
            or isinstance(piece, King): pass

            elif isinstance(piece, Knight) \
            or isinstance(piece, Bishop): count += 1

            elif isinstance(piece, Pawn) \
            and piece.promotion in [Knight, Bishop]: count += 1

            else: return False

        return count <= 1


    def set_guarded_squares(self):
        self.guarded_squares = []
        for piece in self.pieces:
            if piece.captured: continue
            self.guarded_squares.extend(piece.get_guarded_squares())

    
    def set_allowed_squares(self):
        for piece in self.pieces:
            if piece.captured: continue

            prev_square = piece.prev_square
            piece.allowed_squares.clear()

            for square in piece.get_allowed_squares():
                piece.move(square, temporary=True)

                for enemy in self.opponent.pieces:
                    if enemy.captured: pass
                    elif self.king.curr_square \
                    in enemy.get_guarded_squares(): break
                else: piece.allowed_squares.append(square)

                piece.undo_move(prev_square)
                if isinstance(piece, Pawn): piece.en_passant = False

        self.opponent.set_guarded_squares()

        self.king.check_can_castle_king_side(
        self.k_rook, self.opponent.guarded_squares)

        self.king.check_can_castle_queen_side(
        self.q_rook, self.opponent.guarded_squares)

    
    def castling_king_side(self) -> bool:
        x, y = pygame.mouse.get_pos()
        if self.king.rank != y // SQUARE_SIZE: return False

        if not self.king.flipped: return \
        x >= min((self.king.file + 2) * SQUARE_SIZE, SCREEN_WIDTH - 1)

        return x <= (self.king.file - 1) * SQUARE_SIZE
        

    def castling_queen_side(self) -> bool:
        x, y = pygame.mouse.get_pos()
        if self.king.rank != y // SQUARE_SIZE: return False
        
        if self.king.flipped: return \
        x >= min((self.king.file + 2) * SQUARE_SIZE, SCREEN_WIDTH - 1)
            
        return x <= (self.king.file - 1) * SQUARE_SIZE
    

    def castle_king_side(self):
        if self.king.flipped: f_file, g_file = 2, 1
        else: f_file, g_file = 5, 6

        self.king.move((g_file, self.king.rank))
        self.k_rook.move((f_file, self.k_rook.rank))


    def castle_queen_side(self):
        if self.king.flipped: c_file, d_file = 5, 4
        else: c_file, d_file = 2, 3

        self.king.move((c_file, self.king.rank))
        self.q_rook.move((d_file, self.q_rook.rank))
    

    def move_promotions(self, file: int, rank: int):
        if rank == 7: rank = 4
        for dr, piece in enumerate(self.promotions):
            piece.place((file, rank + dr))
    

    def flip(self):
        self.promotions.reverse()

        for piece in self.pieces:
            piece.flip()
            if isinstance(piece, Pawn) and piece.promoting:
                self.move_promotions(piece.file, piece.rank)
    
    
    def draw(self, screen: pygame.Surface, draw_promotions: bool):
        for piece in self.pieces:
            if piece.held or piece.captured: pass
            else: piece.draw(screen)

        if draw_promotions is False: return

        file, rank = self.promotions[0].curr_square

        rect = pygame.Rect(
            SQUARE_SIZE * file,
            SQUARE_SIZE * rank,
            SQUARE_SIZE * 1,
            SQUARE_SIZE * 4)

        pygame.draw.rect(
            surface=screen,
            color=(220, 220, 220),
            rect=rect, width=0,
            border_radius=15)

        pygame.draw.rect(
            surface=screen,
            color=(0, 0, 0),
            rect=rect, width=1,
            border_radius=15)

        for piece in self.promotions: piece.draw(screen)
    