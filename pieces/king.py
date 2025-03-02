from .piece import Piece


class King(Piece):

    def __init__(self, color: str):
        Piece.__init__(self, color, 'king')
        self.flipped = False

        self.can_castle_king_side = \
        self.can_castle_queen_side = False
        
    
    def get_guarded_squares(self) -> list[tuple[int ,int]]:
        guarded_squares = []
        bounds = range(8)

        for df, dr in [(1,0), (0,1), (-1,0), (0,-1), (1,1), (-1,1), (-1,-1), (1,-1)]:
            new_file = self.file + df
            new_rank = self.rank + dr

            if new_file in bounds and new_rank in bounds:
                guarded_squares.append((new_file, new_rank))

        return guarded_squares

    
    def get_allowed_squares(self) -> list[tuple[int, int]]:
        allowed_squares = []

        for file, rank in self.get_guarded_squares():
            if self.occupied_by_friend((file, rank)): pass
            else: allowed_squares.append((file, rank))

        return allowed_squares
    

    def check_can_castle_king_side(self, rook: Piece, 
    guarded_squares: list[tuple[int, int]]):
        self.can_castle_king_side = False

        # King and rook have not moved
        if self.has_moved or rook.has_moved: return

        if self.flipped: f_file, g_file = 2, 1
        else: f_file, g_file = 5, 6

        # Squares king / rook will move to are unoccupied
        for file in [f_file, g_file]:
            if self.file != file and rook.file != file \
            and self.occupied((file, self.rank)): return
        
        # No pieces between king and rook
        files = range(min(self.file, rook.file) + 1,
                      max(self.file, rook.file))
        
        for file in files:
            if self.occupied((file, self.rank)): return
        
        # King not in check or castling through check
        files = range(min(self.file, g_file),
                      max(self.file, g_file) + 1)
        
        for file in files:
            if (file, self.rank) in guarded_squares: return
            
        self.can_castle_king_side = True

        if self.file == g_file: pass
        else: self.allowed_squares.append((g_file, self.rank))


    def check_can_castle_queen_side(self, rook: Piece, 
    guarded_squares: list[tuple[int, int]]) -> bool:
        self.can_castle_queen_side = False

        # King and rook have not moved
        if self.has_moved or rook.has_moved: return

        if self.flipped: c_file, d_file = 5, 4
        else: c_file, d_file = 2, 3

        # Squares king / rook will move to are unoccupied
        for file in [c_file, d_file]:
            if self.file != file and rook.file != file \
            and self.occupied((file, self.rank)): return
                
        # No pieces between king and rook
        files = range(min(self.file, rook.file) + 1,
                      max(self.file, rook.file))
        
        for file in files:
            if self.occupied((file, self.rank)): return
            
        # King not in check or castling through check
        files = range(min(self.file, c_file),
                      max(self.file, c_file) + 1)
        
        for file in files:
            if (file, self.rank) in guarded_squares: return
            
        self.can_castle_queen_side = True

        if self.file == c_file: pass
        else: self.allowed_squares.append((c_file, self.rank))
        

    def flip(self):
        self.flipped = not self.flipped
        Piece.flip(self)
