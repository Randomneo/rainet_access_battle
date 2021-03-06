from logging import getLogger

from .cards import Card
from .cards import Link
from .cards import Pos
from .cards import Virus
from .cards import load_card
from .cards import load_cards
from .cards import save_cards

log = getLogger(__name__)


class NoWinner(Exception):
    ...


class BoardManager:
    def __init__(self, board):
        self.db_board = board
        self.board = load_cards(self.db_board.board)
        self.player1_stack = load_cards(self.db_board.player1_stack or [])
        self.player2_stack = load_cards(self.db_board.player2_stack or [])

    def save(self):
        self.db_board.board = save_cards(self.board)
        self.db_board.player1_stack = save_cards(self.player1_stack)
        self.db_board.player2_stack = save_cards(self.player2_stack)

    def get_by_pos(self, pos: Pos):
        try:
            return next(filter(lambda x: x.pos == pos, self.board))
        except StopIteration:
            return None

    def get_player_by_user(self, user):
        try:
            return {
                self.db_board.player1: 1,
                self.db_board.player2: 2,
            }[user]
        except KeyError:
            log.error(f'User ({user}) not assigned to board')
            raise

    def user_cards(self, user):
        return [*filter(lambda x: x.owner == self.get_player_by_user(user), self.board)]

    def move(self, pos_from: Pos, pos_to: Pos):
        card_from = self.get_by_pos(pos_from)
        card_to = self.get_by_pos(pos_to)
        card_from.pos = pos_to
        self.remove(card_to)
        return card_to

    def add(self, card: Card):
        self.board.append(card)
        self.save()
        return card

    def user_stack(self, user):
        try:
            return {
                self.db_board.player1: self.player1_stack,
                self.db_board.player2: self.player2_stack,
            }[user]
        except KeyError:
            log.error(f'user ({user}) not assigned to board')
            raise

    def add_stack(self, user, card):
        self.user_stack(user).append(card)
        self.save()

    def is_user_winner(self, user):
        stack = self.user_stack(user)
        viruses = sum(map(lambda card: isinstance(card, Virus), stack))
        links = sum(map(lambda card: isinstance(card, Link), stack))
        if viruses >= 4:
            return False
        elif links >= 4:
            return True
        return None

    def decide_winner(self):
        is_player1_winner = self.is_user_winner(self.db_board.player1)
        is_player2_winner = self.is_user_winner(self.db_board.player2)
        if is_player1_winner is None and is_player2_winner is None:
            raise NoWinner()

        if is_player1_winner is True:
            winner = self.db_board.player1
        elif is_player1_winner is False:
            winner = self.db_board.player2
        if is_player2_winner is True:
            winner = self.db_board.player2
        elif is_player2_winner is False:
            winner = self.db_board.player1

        self.db_board.set_winner(winner)
        return winner

    def remove(self, card: Card):
        self.board = [*filter(lambda x: x != card, self.board)]
        self.save()
        return self.board

    def exit_layout(self):
        '''Put on board exit cards for each player'''
        exits = {
            1: [
                [0, 3],
                [0, 4],
            ],
            2: [
                [7, 3],
                [7, 4],
            ],
        }
        for player, poses in exits.items():
            for pos in poses:
                self.add(load_card({
                    'type': 'exit',
                    'owner': player,
                    'x': pos[0],
                    'y': pos[1],
                }))

    def user_can_move_here(self, user, pos: Pos):
        return (
            (
                not self.get_by_pos(pos)
                or self.get_by_pos(pos).owner != self.get_player_by_user(user)
            )
            and pos.x >= 0 and pos.x < 8
            and pos.y >= 0 and pos.y < 8
        )

    @staticmethod
    def load(player1, player2, board: dict):
        resp = []
        for x, row in enumerate(board):
            for y, card in enumerate(row):
                owner = 1 if card.startswith('p1') else 2
                card = card[2:] if card.startswith('p1') else card
                if card in map(lambda x: x.__name__.lower(), Card.__subclasses__()):
                    resp.append({
                        'type': card,
                        'owner': owner,
                        'x': x,
                        'y': y,
                    })
        return resp

    def pprint(self, outstr=print):
        for i in range(8):
            outstr('-'*(3*8+1))
            outstr('|', end='')
            for j in range(8):
                card = self.get_by_pos(Pos(i, j))
                if not card:
                    outstr('  |', end='')
                else:
                    outstr('{}{}|'.format(card.owner, card.type[0]), end='')
            outstr()
        outstr('-'*(3*8+1))
