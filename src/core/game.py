from __future__ import annotations

import asyncio

from .board import Board
from .piece import Piece, PieceType
from .player import Player, PlayerMove, PlayerType


class Game:
    PLAYER_TURN_TIMEOUT = 30

    def __init__(self, player1: Player, player2: Player) -> None:
        self.board = Board()
        self.board.pieces.extend((
            Piece(PieceType.socket, (3, 0), player1, is_on_board=True),
            Piece(PieceType.socket, (4, 0), player1, is_on_board=True),
            Piece(PieceType.socket, (3, 7), player2, is_on_board=True),
            Piece(PieceType.socket, (4, 7), player2, is_on_board=True),
        ))
        self.players: tuple[Player, Player] = (player1, player2)

    async def send_state(self) -> None:
        for player in self.players:
            await player.send_board_state(
                self.board.state(invert=player.on_board_type is PlayerType.top)
            )

    async def player_move(self, current_player: Player) -> PlayerMove | None:
        while True:
            move = await current_player.get_move()
            if validation_error := self.board.validate_move(move):
                await current_player.io_handler.send(validation_error)
            else:
                return move
        return None

    async def player_setup(self, player: Player) -> None:
        while True:
            setup = await player.get_setup()
            if validation_error := self.board.validate_setup(setup):
                await player.io_handler.send(validation_error)
            else:
                return self.board.setup(setup)

    async def setup(self) -> None:
        await asyncio.gather(*map(self.player_setup, self.players))

    async def main_loop(self) -> None:
        current_player = self.players[0]
        while True:
            await self.send_state()
            player_move = None
            async with asyncio.timeout(self.PLAYER_TURN_TIMEOUT):
                player_move = await self.player_move(current_player)

            if not player_move:
                break
            self.board.apply_move(player_move)
            if self.board.is_ended:
                break

            current_player = Player.switch(self.players, current_player)
