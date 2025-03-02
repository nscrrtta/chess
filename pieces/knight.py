from .piece import Piece


class Knight(Piece):

    def __init__(self, color: str):
        Piece.__init__(self, color, 'knight')


    def get_guarded_squares(self) -> list[tuple[int, int]]:
        guarded_squares = []
        bounds = range(8)

        for df, dr in [(2,1), (1,2), (-1,2), (-2,1), (-2,-1), (-1,-2), (1,-2), (2,-1)]:
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
