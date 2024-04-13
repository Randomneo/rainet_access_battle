from __future__ import annotations

import dataclasses
import enum
from typing import Sequence

from .io_handler import IOHandler
from .piece import Piece, PieceType
from .utils import invert_pos


class PlayerType(enum.StrEnum):
    top = enum.auto()
    bottom = enum.auto()


@dataclasses.dataclass
class PlayerMove:
    player: Player
    pos_from: tuple[int, int] | None
    pos_to: tuple[int, int] | None
    action: None = dataclasses.field(default=None)


@dataclasses.dataclass
class PlayerSetup:
    pieces: tuple[Piece, ...]


class Player():
    def __init__(
            self,
            user_id: int,
            on_board_type: PlayerType,
            io_handler: IOHandler,
    ) -> None:
        self.user_id = user_id
        self.on_board_type = on_board_type
        self.io_handler = io_handler

    def __hash__(self):
        return hash(self.user_id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Player):
            raise NotImplementedError()
        return self.user_id == other.user_id

    @staticmethod
    def switch(
            players_pool: tuple[Player, Player],
            current_player: Player,
    ) -> Player:
        return {*players_pool}.difference({current_player}).pop()

    async def get_move(self) -> PlayerMove:
        await self.io_handler.send('awaiting_pos_from')
        pos = await self.io_handler.read()
        pos_from = tuple(map(int, pos.split()))
        await self.io_handler.send('awaiting_pos_to')
        pos = await self.io_handler.read()
        pos_to = tuple(map(int, pos.split()))
        pos_from = (pos_from[0], pos_from[1])
        pos_to = (pos_to[0], pos_to[1])
        if self.on_board_type is PlayerType.bottom:
            pos_from = invert_pos(pos_from)
            pos_to = invert_pos(pos_to)
        return PlayerMove(self, pos_from, pos_to)

    async def get_setup(self) -> PlayerSetup:
        await self.io_handler.send('awaiting_board_setup')
        pieces = await self.io_handler.read()
        setup = []
        preset_pos_list = [
            (0, 0),
            (1, 0),
            (2, 0),
            (3, 1),
            (4, 1),
            (5, 0),
            (6, 0),
            (7, 0),
        ]
        for pos, piece in zip(preset_pos_list, pieces.split(';')):
            if self.on_board_type is PlayerType.bottom:
                pos = invert_pos(pos)
            setup.append(Piece(PieceType(piece), pos, self, is_on_board=True))

        return PlayerSetup(pieces=tuple(setup))

    async def send_board_state(self, pieces: Sequence[Piece]) -> None:
        board_state = []
        for piece in pieces:
            if piece.is_on_board:
                if piece.owner == self or piece.piece_type is PieceType.socket:
                    piece_type = piece.piece_type.value
                else:
                    piece_type = PieceType.enemy.value
                board_state.append(','.join((
                    piece_type,
                    *map(str, piece.position),
                )))

        await self.io_handler.send_board(';'.join(board_state))
