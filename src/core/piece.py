from __future__ import annotations

import dataclasses
import enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .player import Player


class PieceType(enum.StrEnum):
    link = enum.auto()
    virus = enum.auto()
    enemy = enum.auto()
    socket = enum.auto()


@dataclasses.dataclass
class Piece:
    piece_type: PieceType
    position: tuple[int, int]
    owner: Player
    is_on_board: bool = dataclasses.field(default=False)
    connected: bool = dataclasses.field(default=False)
    captured: bool = dataclasses.field(default=False)
