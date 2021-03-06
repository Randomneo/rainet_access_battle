from ..ai import ai
from ..cards import Link
from ..cards import Pos
from ..cards import Virus
from ..models import Board


def test_ai_random_layout(user1, user2):
    board = Board.load(user1, user2, [[]])
    ai.random_layout(board)
    assert len(board.manager.board) == 8
    assert len([*filter(lambda x: isinstance(x, Link), board.manager.board)]) == 4
    assert len([*filter(lambda x: isinstance(x, Virus), board.manager.board)]) == 4
    ai.random_layout(board, invert=True)
    assert len(board.manager.board) == 16
    assert len([*filter(lambda x: isinstance(x, Link), board.manager.board)]) == 8
    assert len([*filter(lambda x: isinstance(x, Virus), board.manager.board)]) == 8


def test_ai_make_move(user1, user2, monkeypatch):
    board = Board.load(user1, user2, [['virus', 'link']])
    monkeypatch.setattr('rab.ai.choice', lambda x: x[0])
    f, t = ai.make_move(user2, board)

    assert Pos(0, 0) == f
    assert Pos(1, 0) == t


def test_ai_make_move_retry(user1, user2, monkeypatch):

    board = Board.load(user1, user2, [['virus', 'link'], ['virus']])
    monkeypatch.setattr('rab.ai.choice', lambda x: x[0])
    assert not ai.make_move(user2, board)
