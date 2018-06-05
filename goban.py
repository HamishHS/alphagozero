#GoBan.py Source: author: Aku Kotkavuo, version: 0.1, date: 2008

import pygame
import go
from alphagozero.model import load_best_model
from alphagozero.gtp import Engine
from sys import exit
from alphagozero.conf import conf
from datetime import datetime

BACKGROUND = 'images/ramin.jpg'
BOARD_SIZE = (820, 820)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GAME_SIZE = conf['SIZE']


class Stone(go.Stone):
    def __init__(self, board, point, color):
        """Create, initialize and draw a stone."""
        super(Stone, self).__init__(board, point, color)
        self.coords = (5 + self.point[0] * 40, 5 + self.point[1] * 40)
        self.draw()

    def draw(self):
        """Draw the stone as a circle."""
        pygame.draw.circle(screen, self.color, self.coords, 20, 0)
        pygame.display.update()

    def remove(self):
        """Remove the stone from board."""
        blit_coords = (self.coords[0] - 20, self.coords[1] - 20)
        area_rect = pygame.Rect(blit_coords, (40, 40))
        screen.blit(background, blit_coords, area_rect)
        pygame.display.update()
        super(Stone, self).remove()


class Board(go.Board):
    def __init__(self):
        """Create, initialize and draw an empty board."""
        super(Board, self).__init__()
        self.outline = pygame.Rect(45, 45, 720, 720)
        self.draw()

    def draw(self):
        """Draw the board to the background and blit it to the screen.

        The board is drawn by first drawing the outline, then the 19x19
        grid and finally by adding hoshi to the board. All these
        operations are done with pygame's draw functions.

        This method should only be called once, when initializing the
        board.

        """
        pygame.draw.rect(background, BLACK, self.outline, 3)
        # Outline is inflated here for future use as a collidebox for the mouse
        self.outline.inflate_ip(20, 20)
        for i in range(GAME_SIZE - 1):
            for j in range(GAME_SIZE - 1):
                rect = pygame.Rect(45 + (40 * i), 45 + (40 * j), 40, 40)
                pygame.draw.rect(background, BLACK, rect, 1)
        for i in range(3):
            for j in range(3):
                coords = (165 + (240 * i), 165 + (240 * j))
                pygame.draw.circle(background, BLACK, coords, 5, 0)
        screen.blit(background, (0,0))
        pygame.display.update()

    def update_liberties(self, added_stone=None):
        """Updates the liberties of the entire board, group by group.
        
        Usually a stone is added each turn. To allow killing by 'suicide',
        all the 'old' groups should be updated before the newly added one.
        
        """
        for group in self.groups:
            if added_stone:
                if group == added_stone.group:
                    continue
            group.update_liberties()
        if added_stone:
            added_stone.group.update_liberties()

#----------------------------Added to comunicated with alpha zero go-------------------------#
color_to_gtp_color = {WHITE: 'W', BLACK: 'B'}


def xy_to_gtp(x, y):
    xx = x
    if x >= 8:
        xx += 1  # I is a skipped letter
    return chr(64 + xx) + str(y)


def gtp_to_xy(crd):
    x = ord(crd[0]) - 64
    if x >= 9:
        x -= 1  # I is a skipped letter
    y = int(crd[1])
    return x, y


def add_stone(x, y):
    move_str = color_to_gtp_color[board.next] + " = " + xy_to_gtp(x, y)
    print(move_str)
    f.write(move_str + "\n")
    added_stone = Stone(board, (x, y), board.turn())
    board.update_liberties(added_stone)


def play_pass():
    move_str = color_to_gtp_color[board.next] + " = " + "pass"
    print(move_str)
    f.write(move_str + "\n")
    board.turn()


def move(x, y):
    gtp_color = color_to_gtp_color[board.next]
    add_stone(x, y)
    engine.play(gtp_color, xy_to_gtp(x, y)) # this is where NN learns your move

    gtp_color = color_to_gtp_color[board.next]
    nn_move = engine.genmove(gtp_color) # this is where NN produces its move
    nn_x, nn_y = gtp_to_xy(nn_move)
    if nn_x is 0 or nn_y is 0:
        play_pass()
    else:
        add_stone(nn_x, nn_y)
    f.flush()
#-----------------------------------end--------------------------------------#

def main():
    engine.clear_board()

    while True:
        pygame.time.wait(250)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and board.outline.collidepoint(event.pos):
                    x = int(round(((event.pos[0] - 5) / 40.0), 0))
                    y = int(round(((event.pos[1] - 5 ) / 40.0), 0))
                    stone = board.search(point=(x, y))
                    if not stone:
                        move(x, y)


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Goban')
    screen = pygame.display.set_mode(BOARD_SIZE, 0, 32)
    background = pygame.image.load(BACKGROUND).convert()
    board = Board()
    model = load_best_model() # alpha go specific
    engine = Engine(model) # alpha go specific
    # alpha go specific
    with open('logs/game_' + datetime.now().strftime("%Y_%M_%d_%h_%m") + '.log', 'w') as f:
        main()
