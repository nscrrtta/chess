from pieces import Piece
import random


class FischerRandom:

    def __init__(self, pieces: list[Piece]):
        # Remove pawns from list of pieces
        self.pieces = pieces[8:16] + pieces[24:32]
        self.flipped = False
        self.new_position()

    
    def new_position(self):
        empty_files = list(range(8))

        king_file = random.randint(1, 6)
        empty_files.remove(king_file)

        k_rook_file = random.randint(king_file + 1, 7)
        empty_files.remove(k_rook_file)

        q_rook_file = random.randint(0, king_file - 1)
        empty_files.remove(q_rook_file)

        if self.flipped: k_rook_file, q_rook_file = q_rook_file, k_rook_file

        bishop_1_file = random.choice(
        [file for file in empty_files if file % 2 == 0])
        empty_files.remove(bishop_1_file)

        bishop_2_file = random.choice(
        [file for file in empty_files if file % 2 == 1])
        empty_files.remove(bishop_2_file)

        knight_1_file = random.choice(empty_files)
        empty_files.remove(knight_1_file)

        knight_2_file = random.choice(empty_files)
        empty_files.remove(knight_2_file)

        queen_file = empty_files[0]

        files = [
            q_rook_file,
            knight_1_file,
            bishop_1_file,
            queen_file,
            king_file,
            bishop_2_file,
            knight_2_file,
            k_rook_file
        ] * 2

        for file, piece in zip(files, self.pieces):
            piece.fischer_file = file

    
    def flip(self):
        self.flipped = not self.flipped
