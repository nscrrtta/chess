from constants import SQUARE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, SMALL_FONT, LARGE_FONT
from .game import Game
import pygame


class Menu:

    def __init__(self, game: Game):
        self.game = game
        self.active = False

        self.transparent = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.transparent.set_colorkey((255, 255, 255))
        self.transparent.set_alpha(100)

        self.white_pawn = pygame.image.load(f'pngs/white_pawn.png')
        self.white_pawn_rect = self.white_pawn.get_rect()
        self.white_pawn_rect.center = (300, 340)

        self.black_pawn = pygame.image.load(f'pngs/black_pawn.png')
        self.black_pawn_rect = self.black_pawn.get_rect()
        self.black_pawn_rect.center = (500, 340)

        self.checkmark = pygame.image.load('pngs/checkmark.png')
        self.checkmark_rect = self.checkmark.get_rect()
        self.checkmark_rect.center = (273, 523)

        self.new_game_button = Button(
            center=(400, 445), text='New Game')
        self.new_position_button = Button(
            center=(400, 595), text='New Position')
        self.checkbox = Checkbox(
            center=(273, 523), height=30, width=30)
        self.new_position_button.enabled = False

        self.fr_text = SMALL_FONT.render(
            'Fischer Random', True, (250, 250, 250))
        self.fr_text_rect = self.fr_text.get_rect()
        self.fr_text_rect.center = (420, 525)

        self.update_text()

    
    def mouse_button_down(self):
        if self.new_game_button.mouse_over():
            self.new_game_button.pressed = True

        elif self.new_position_button.mouse_over():
            self.new_position_button.pressed = True

        elif self.checkbox.mouse_over():
            self.checkbox.pressed = \
            not self.checkbox.pressed

            self.new_position_button.enabled = \
            self.checkbox.pressed


    def mouse_button_up(self):
        if self.new_game_button.pressed:
            self.game.new_game(fischer_random=\
            self.checkbox.pressed)
            self.update_text()
            self.toggle()

        elif self.new_position_button.pressed:
            self.game.fischer_random.new_position()
            self.game.new_game(fischer_random=True)
            self.update_text()
            self.toggle()

    
    def toggle(self):
        self.active = not self.active
        if self.active is False:
            self.new_game_button.pressed = \
            self.new_position_button.pressed = False

    
    def update_text(self):
        self.large_text = LARGE_FONT.render(
        self.game.large_text, True, (250, 250, 250))

        self.large_text_rect = self.large_text.get_rect()
        self.large_text_rect.center = (400, 200)

        self.small_text = SMALL_FONT.render(
        self.game.small_text, True, (250, 250, 250))

        self.small_text_rect = self.small_text.get_rect()
        self.small_text_rect.center = (400, 255)

        self.score_text = SMALL_FONT.render(
        f'{self.game.white_player.score}  -  {self.game.black_player.score}',
        True, (250, 250,250))

        self.score_text_rect = self.score_text.get_rect()
        self.score_text_rect.center = (400, 340)


    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(
            surface=self.transparent, color=(70, 70, 70),
            rect=pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        
        screen.blit(self.transparent, (0, 0))

        rect = pygame.Rect(
            SQUARE_SIZE * 1.5,
            SQUARE_SIZE * 1.5,
            SQUARE_SIZE * 5,
            SQUARE_SIZE * 5
        )

        pygame.draw.rect(
            surface=screen, color=(100, 100, 100),
            rect=rect, width=0, border_radius=8
        )
        pygame.draw.rect(
            surface=screen, color=(0, 0, 0),
            rect=rect, width=1, border_radius=8
        )

        screen.blit(self.large_text, self.large_text_rect)
        screen.blit(self.small_text, self.small_text_rect)
        screen.blit(self.score_text, self.score_text_rect)

        screen.blit(self.white_pawn, self.white_pawn_rect)
        screen.blit(self.black_pawn, self.black_pawn_rect)

        self.new_game_button.draw(screen)
        self.new_position_button.draw(screen)

        self.checkbox.draw(screen)
        if self.checkbox.pressed: screen.blit(self.checkmark, self.checkmark_rect)

        screen.blit(self.fr_text, self.fr_text_rect)




class Button:

    def __init__(self, **kwargs):
        x, y = self.center = kwargs['center']

        self.height = kwargs.get('height', 60)
        self.width = kwargs.get('width', 350)
        
        self.y_pos = y - self.height / 2
        self.x_pos = x - self.width / 2

        self.color = (118, 150, 86)

        self.pressed = False
        self.enabled = True

        text = kwargs.get('text', None)
        if text is None: return

        font = pygame.font.Font(None, 45)
        self.text = font.render(text, True, (250, 250, 250))
        self.text_rect = self.text.get_rect()
    

    def mouse_over(self) -> bool:
        x, y = pygame.mouse.get_pos()
        return self.enabled \
        and self.x_pos < x < self.x_pos + self.width \
        and self.y_pos < y < self.y_pos + self.height \
    

    def draw(self, screen: pygame.Surface):
        self.pressed = self.pressed and self.mouse_over()

        top_color = self.color if self.enabled else (150, 150, 150)
        bot_color = tuple([max(0, i-60) for i in top_color])

        rect = pygame.Rect(self.x_pos, self.y_pos + 7, self.width, self.height)
        pygame.draw.rect(
            surface=screen, color=bot_color,
            rect=rect, width=0, border_radius=10)

        rect = pygame.Rect(self.x_pos, self.y_pos + self.pressed * 3, self.width, self.height)
        pygame.draw.rect(
            surface=screen, color=top_color,
            rect=rect, width=0, border_radius=10)

        x, y = self.center
        y += 3 * (self.pressed + 1)

        self.text_rect.center = (x, y)
        screen.blit(self.text, self.text_rect)




class Checkbox(Button):

    def draw(self, screen: pygame.Surface):
        rect = pygame.Rect(self.x_pos, self.y_pos, self.width, self.height)

        pygame.draw.rect(
            surface=screen, color=(180, 180, 180),
            rect=rect, width=0, border_radius=8)
        
        pygame.draw.rect(
            surface=screen, color=(0, 0, 0),
            rect=rect, width=1, border_radius=8)
