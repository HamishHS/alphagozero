#!/usr/bin/env python
import sys
from alphagozero.play import game_init
from alphagozero.engine import ModelEngine, COLOR_TO_PLAYER
import string
from alphagozero.conf import conf

SIZE = conf['SIZE']
MCTS_SIMULATIONS = conf['MCTS_SIMULATIONS']

class Engine(object):
    def __init__(self, model):
        self.board, self.player = game_init()
        self.start_engine(model)

    def start_engine(self, model):
        self.engine = ModelEngine(model, MCTS_SIMULATIONS, self.board)

    def name(self):
        return "AlphaGoZero Python - {} - {} simulations".format(self.engine.model.name, conf['MCTS_SIMULATIONS']) 

    def protocol_version(self):
        return "2"

    def list_commands(self):
        return ""

    def boardsize(self, size):
        size = int(size)
        if size != SIZE:
            raise Exception("The board size in configuration is {0}x{0} but GTP asked to play {1}x{1}".format(SIZE, size))
        return ""

    def komi(self, komi):
        # Don't check komi in GTP engine. The algorithm has learned with a specific
        # komi that we don't have any way to influence after learning.
        return ""

    def parse_move(self, move):

        if move.lower() == 'pass':
            x, y = 0, SIZE
            return x, y
        else:
            letter = move[0]
            number = move[1:]

            x = string.ascii_uppercase.index(letter)
            if x >= 9:
                x -= 1 # I is a skipped letter
            y = int(number) - 1

        x, y = x, SIZE - y - 1
        return x, y

    def print_move(self, x, y):
        x, y = x, SIZE - y - 1

        if x >= 8:
            x += 1 # I is a skipped letter

        move = string.ascii_uppercase[x] + str(y + 1)
        return move

    def play(self, color, move):
        announced_player = COLOR_TO_PLAYER[color]
        assert announced_player == self.player
        x, y = self.parse_move(move)
        self.board, self.player = self.engine.play(color, x, y)
        return ""

    def genmove(self, color):
        announced_player = COLOR_TO_PLAYER[color]
        assert announced_player == self.player

        x, y, policy_target, value, self.board, self.player = self.engine.genmove(color)
        self.player = self.board[0, 0, 0, -1]  # engine updates self.board already 
        move_string = self.print_move(x, y)
        result = move_string
        return result

    def clear_board(self):
        self.board, self.player = game_init()
        return ""

    def parse_command(self, line):
        tokens = line.strip().split(" ")
        command = tokens[0]
        args = tokens[1:]
        print(command)
        print(args)
        method = getattr(self, command)
        result = method(*args)
        print(result)
        if isinstance(result, str) and not result.strip():
            return "=\n\n"
        return "= " + str(result) + "\n\n"

# def main():
#     with open('logs/gtp.log', 'w') as f:
#         for line in sys.stdin:
#             f.write("<<<" + line)
#             result = engine.parse_command(line)
#
#             if result.strip():
#                 sys.stdout.write(result)
#                 sys.stdout.flush()
#                 f.write("'''" + str(engine.player) + '\n')
#                 f.write(">>>" + result)
#                 f.flush()
#
#
# if __name__ == "__main__":
#     main()
