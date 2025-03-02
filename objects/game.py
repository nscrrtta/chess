from .fischer import FischerRandom
from .history import History
from .player import Player
from .board import Board
from pieces import Pawn
import pygame


class Game:

    def __init__(self):
        self.white_player = Player('white')
        self.black_player = Player('black')

        self.pieces = self.white_player.pieces \
                    + self.black_player.pieces
        self.fischer_random = FischerRandom(self.pieces)
        
        self.board = Board(self.pieces)
        self.history = History(self.board, self.pieces)

        self.white_player.opponent = self.black_player
        self.black_player.opponent = self.white_player

        for piece in self.white_player.pieces:
            piece.friends = self.white_player.pieces
            piece.enemies = self.black_player.pieces

        for piece in self.black_player.pieces:
            piece.friends = self.black_player.pieces
            piece.enemies = self.white_player.pieces
        
        self.new_game(fischer_random=False)

    
    def new_game(self, fischer_random: bool):
        self.game_is_over = False
        self.selected_piece = None
        self.pawn_promoting = False

        # For menu
        self.large_text = 'Main Menu'
        self.small_text = ''

        for piece in self.pieces: piece.reset(fischer_random)
        self.history.reset()
        self.board.reset()

        self.active_player, self.inactive_player = \
        self.white_player, self.black_player

        self.active_player.set_allowed_squares()

        pygame.mixer.Sound('wavs/gamestart.wav').play()
        self.history.save(sound_effect='nothing')

    
    def next_turn(self):
        self.board.update()
        self.selected_piece = None

        self.active_player, self.inactive_player = \
        self.inactive_player, self.active_player

        for piece in self.active_player.pieces:
            if isinstance(piece, Pawn): piece.en_passant = False

        self.active_player.set_allowed_squares()
        in_check = self.active_player.king_in_check()

        if in_check: self.sound_effect = 'check'
        self.history.save(sound_effect=self.sound_effect)
        pygame.mixer.Sound(f'wavs/{self.sound_effect}.wav').play()

    
    def game_over(self) -> bool:
        in_check = self.active_player.king_in_check()
        no_moves = self.active_player.no_legal_moves()

        if in_check and no_moves:
            self.game_is_over = True

            self.inactive_player.score += 1.0

            self.large_text = {
                self.white_player: 'White Wins',
                self.black_player: 'Black Wins'
            }[self.inactive_player]
            self.small_text = 'By checkmate'

        elif not in_check and no_moves:
            self.game_is_over = True

            self.white_player.score += 0.5
            self.black_player.score += 0.5

            self.large_text, self.small_text = 'Draw', 'By stalemate'

        elif self.white_player.insufficient_material() \
        and self.black_player.insufficient_material():
            self.game_is_over = True

            self.white_player.score += 0.5
            self.black_player.score += 0.5

            self.large_text, self.small_text = 'Draw', 'By insufficient material'

        if self.game_is_over: pygame.mixer.Sound('wavs/gameover.wav').play()
        return self.game_is_over

    
    def select_promotion(self, file: int, rank: int) -> bool:
        for promotion in self.active_player.promotions:
            if promotion.curr_square == (file, rank): break
        else: return False

        for piece in self.active_player.pieces:
            if isinstance(piece, Pawn) and piece.promoting:
                piece.promote(promotion)
                break

        self.pawn_promoting = False
        self.next_turn()
        return True
    
    
    def select_piece(self, file: int, rank: int):
        self.selected_piece = \
        self.board.selected_piece = None
        
        for piece in self.pieces:
            if piece.captured: continue
            if piece.curr_square == (file, rank): break
        else: return

        self.selected_piece = piece
        self.selected_piece.held = True

        if self.game_is_over \
        or piece not in self.active_player.pieces \
        or self.history.at_current_position() is False: return

        self.board.selected_piece = piece

    
    def move_piece(self, file: int, rank: int) -> bool:
        piece = self.selected_piece

        if piece is None: return False

        elif self.history.at_current_position() is False:
            if piece.held: piece.place(piece.curr_square)
            return False
    
        elif piece == self.active_player.king \
        and self.active_player.castling_king_side() \
        and self.active_player.king.can_castle_king_side:
            
            self.active_player.castle_king_side()
            self.sound_effect = 'castle'
            self.next_turn()
            return True

        elif piece == self.active_player.king \
        and self.active_player.castling_queen_side() \
        and self.active_player.king.can_castle_queen_side:
            
            self.active_player.castle_queen_side()
            self.sound_effect = 'castle'
            self.next_turn()
            return True
        
        elif piece not in self.active_player.pieces:
            if piece.held: piece.place(piece.curr_square)
            return False
        
        elif (file, rank) not in piece.allowed_squares:
            if piece.held: piece.place(piece.curr_square)
            return False
        
        piece.move((file, rank))

        if piece.captured_piece is None: self.sound_effect = 'move'
        else: self.sound_effect = 'capture'

        if isinstance(piece, Pawn) \
        and piece.promotion is None \
        and rank == piece.final_rank:
            self.pawn_promoting = piece.promoting = True
            self.active_player.move_promotions(file, rank)
            return True
        
        self.next_turn()
        return True

    
    def flip(self):
        # Important to flip board AFTER flipping players
        self.fischer_random.flip()
        self.white_player.flip()
        self.black_player.flip()
        self.board.flip()

    
    def draw(self, screen: pygame.Surface):
        self.board.draw(screen)

        self.inactive_player.draw(screen, draw_promotions=False)
        self.active_player.draw(screen, draw_promotions=self.pawn_promoting)

        for piece in self.pieces:
            if piece.captured: pass
            elif piece.held: piece.draw(screen)
