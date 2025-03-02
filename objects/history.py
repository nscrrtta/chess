from .board import Board
from pieces import Piece
import pygame


class History:

    def __init__(self, board: Board, pieces: list[Piece]):
        self.board = board
        self.pieces = pieces

    
    def reset(self):
        self.sound_history = []
        self.board_history = []
        self.piece_history = []

        self.index = -1
        self.depth = 0
        
    
    def save(self, sound_effect: str):
        self.sound_history.append(sound_effect)

        self.board_history.append(
        (self.board.prev_square, self.board.curr_square))

        self.piece_history.append([
        (piece.captured, piece.curr_square, piece.image)
        for piece in self.pieces])

        self.index += 1
        self.depth += 1


    def at_current_position(self) -> bool:
        return self.index == self.depth - 1
    

    def load_prev(self):
        if self.index == 0: return
        self.index -= 1
        self.load()

    
    def load_next(self):
        if self.at_current_position(): return
        self.index += 1
        self.load()

    
    def load_curr(self):
        if self.at_current_position(): return
        self.index = self.depth - 1
        self.load()

    
    def load_init(self):
        if self.index == 0: return
        self.index = 0
        self.load()

    
    def load(self):
        sound = self.sound_history[self.index]
        pygame.mixer.Sound(f'wavs/{sound}.wav').play()

        self.board.prev_square, self.board.curr_square = \
        self.board_history[self.index]

        piece_history = self.piece_history[self.index]

        for piece, (captured, curr_square, image) \
        in zip(self.pieces, piece_history):
            
            piece.captured = captured
            piece.set_image(image)
            piece.place(curr_square)
