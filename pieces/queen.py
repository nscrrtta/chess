from .piece import Piece


class Queen(Piece):

    def __init__(self, color: str):
        Piece.__init__(self, color, 'queen')

    
    def get_guarded_squares(self) -> list[tuple[int ,int]]:
        guarded_squares = []
        bounds = range(8)

        for df, dr in [(1,0), (0,1), (-1,0), (0,-1), (1,1), (-1,1), (-1,-1), (1,-1)]:
            for distance in range(1, 8):
                new_file = self.file + df * distance
                new_rank = self.rank + dr * distance

                if new_file in bounds and new_rank in bounds:
                    guarded_squares.append((new_file, new_rank))
                else: break
                
                if self.occupied((new_file, new_rank)): break

        return guarded_squares

    
    def get_allowed_squares(self) -> list[tuple[int, int]]:
        allowed_squares = []

        for file, rank in self.get_guarded_squares():
            if self.occupied_by_friend((file, rank)): pass
            else: allowed_squares.append((file, rank))

        return allowed_squares
