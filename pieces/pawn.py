from .bishop import Bishop
from .knight import Knight
from .queen import Queen
from .rook import Rook
from .piece import Piece


class Pawn(Piece):

    def __init__(self, color: str):
        Piece.__init__(self, color, 'pawn')
        
        self.start_rank = {'white': 6, 'black': 1}[color]
        self.final_rank = {'white': 0, 'black': 7}[color]
        self.direction = {'white': -1, 'black': 1}[color]

        self.original_image = self.image
        self.en_passant = self.promoting = False
        self.promotion: Queen | Rook | Bishop | Knight | None = None

        
    def reset(self, _):
        if self.promotion is not None:
            self.set_image(self.original_image)

        self.en_passant = self.promoting = False
        self.promotion = None
        
        Piece.reset(self, fischer_random=False)

    
    def get_guarded_squares(self) -> list[tuple[int, int]]:
        if self.promotion == Queen:
            return Queen.get_guarded_squares(self)
        
        elif self.promotion == Rook:
            return Rook.get_guarded_squares(self)
        
        elif self.promotion == Bishop:
            return Bishop.get_guarded_squares(self)
        
        elif self.promotion == Knight:
            return Knight.get_guarded_squares(self)

        guarded_squares = []
        bounds = range(8)

        for df, dr in [(1, 1), (-1, 1)]:
            new_file = self.file + df
            new_rank = self.rank + dr * self.direction

            if new_file in bounds and new_rank in bounds:
                guarded_squares.append((new_file, new_rank))
        
        return guarded_squares


    def get_allowed_squares(self) -> list[tuple[int, int]]:
        if self.promotion == Queen:
            return Queen.get_allowed_squares(self)
        
        elif self.promotion == Rook:
            return Rook.get_allowed_squares(self)
        
        elif self.promotion == Bishop:
            return Bishop.get_allowed_squares(self)
        
        elif self.promotion == Knight:
            return Knight.get_allowed_squares(self)
        
        allowed_squares = []
        guarded_squares = self.get_guarded_squares()

        for file, rank in guarded_squares:
            if self.occupied_by_enemy((file, rank)):
                allowed_squares.append((file, rank))

        for dr in range(2 if self.rank == self.start_rank else 1):
            new_rank = self.rank + (dr + 1) * self.direction
            if self.occupied((self.file, new_rank)): break
            allowed_squares.append((self.file, new_rank))

        for piece in self.enemies:
            if isinstance(piece, Pawn) and piece.en_passant \
            and (piece.file, piece.rank - piece.direction) in guarded_squares:
                allowed_squares.append((piece.file, piece.rank - piece.direction))
                break

        return allowed_squares
    

    def promote(self, piece: Queen | Rook | Bishop | Knight):
        self.promotion = type(piece)
        self.promoting = False
        
        self.set_image(piece.image)
        self.place(self.curr_square)

    
    def move(self, square: tuple[int, int], temporary=False):
        file, rank = square
    
        for piece in self.enemies:
            if isinstance(piece, Pawn) and piece.en_passant \
            and piece.curr_square == (file, rank - self.direction):
                self.captured_piece = piece
                break
        else: self.captured_piece = self.get_captured_piece(square)

        if self.captured_piece is not None:
            self.captured_piece.captured = True

        elif abs(rank - self.rank) == 2:
            self.en_passant = True

        self.prev_square = self.curr_square
        self.curr_square = square

        if temporary: return
        self.has_moved = True
        self.place(square)

    
    def flip(self):
        self.final_rank = 7-self.final_rank
        self.direction *= -1
        Piece.flip(self)
