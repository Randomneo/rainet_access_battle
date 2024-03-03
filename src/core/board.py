import dataclasses
from typing import Callable

from .exceptions import InternalError
from .piece import Piece, PieceType
from .player import Player, PlayerMove
from .utils import invert_pos


class Board:
    def __init__(self) -> None:
        self.pieces: list[Piece] = []
        self.is_ended: bool = False

    def state(self, invert=True) -> list[Piece]:
        if invert:
            return [dataclasses.replace(x, position=invert_pos(x.position)) for x in self.pieces]
        return list(map(dataclasses.replace, self.pieces))

    def apply_move(self, move: PlayerMove) -> None:
        # currently only moves are allowed
        assert move.pos_from and move.pos_to
        move_piece = None
        for piece in self.pieces:
            if move.pos_from == piece.position and move.player == piece.owner:
                move_piece = piece
        if not move_piece:
            raise InternalError('Got invalid PlayerMove')
        move_piece.position = move.pos_to

        for piece in self.pieces:
            if piece.position == move_piece.position and piece is not move_piece and piece.is_on_board:
                if piece.owner != move_piece.owner:
                    if piece.piece_type is PieceType.socket:
                        move_piece.is_on_board = False
                        move_piece.connected = True
                    else:
                        piece.is_on_board = False
                        piece.captured = True
                else:
                    raise InternalError('Got invalid PlayerMove')

    def count_connected(self, player: Player) -> int:
        count = 0
        for piece in self.pieces:
            if piece.connected and piece.owner == player:
                count += 1
        return count

    def count_captured(self, player: Player) -> int:
        count = 0
        for piece in self.pieces:
            if piece.captured and piece.owner == player:
                count += 1
        return count

    @staticmethod
    def get_piece_checker(player: Player) -> Callable[[Piece], bool]:
        def checker(piece: Piece) -> bool:
            return piece.owner == player
        return checker

    def validate_move(self, move: PlayerMove) -> str | None:
        assert move.pos_from and move.pos_to
        if not 0 <= move.pos_from[0] <= 7 or not 0 <= move.pos_from[1] <= 7:
            return 'invalid range pos_from'
        if not 0 <= move.pos_to[0] <= 7 or not 0 <= move.pos_to[1] <= 7:
            return 'invalid range pos_to'

        for piece in self.pieces:
            if piece.position == move.pos_from and piece.owner == move.player:
                break
        else:
            return 'invalid pos_from'

        for piece in self.pieces:
            if piece.position == move.pos_to and piece.owner == move.player:
                return 'invalid pos_to'

        if abs(move.pos_from[0] - move.pos_to[0]) + abs(move.pos_from[1] - move.pos_to[1]) > 1:
            return 'invalid pos_from + pos_to'

        return None
