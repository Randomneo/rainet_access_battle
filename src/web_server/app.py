from __future__ import annotations

import asyncio
import dataclasses
import secrets
from enum import StrEnum, auto
from typing import Any

from blacksheep import (Application, WebSocket, WebSocketDisconnectError, get,
                        ws)
from core.game import Game, Player, PlayerType
from core.io_handler import IOHandler

application = Application()
games = []


class WaitingRoom():
    _waiting_rooms: dict[str, WaitingRoom] = {}

    def __init__(self, game_id: str):
        self.game_id = game_id
        self.players: list[Player] = []
        self.game: asyncio.Future[Game] = asyncio.get_running_loop().create_future()

    def join(self, player: Player):
        self.players.append(player)
        if len(self.players) >= 2:
            self.players[0].on_board_type = PlayerType.top
            self.players[1].on_board_type = PlayerType.bottom
            game = Game(*self.players)
            games.append(asyncio.create_task(game.run()))
            self.game.set_result(game)

    @classmethod
    def get(cls, game_id: str) -> WaitingRoom:
        room = cls._waiting_rooms.get(game_id)
        if room:
            return room
        cls._waiting_rooms[game_id] = WaitingRoom(game_id)
        return cls._waiting_rooms[game_id]


class WsMessageType(StrEnum):
    system = auto()
    game = auto()


@dataclasses.dataclass
class WsMessage:
    message_type: WsMessageType
    data: dict[str, Any] | str

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


class WebSocketHandler(IOHandler):
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket

    async def send_json(self, ws_message: WsMessage) -> None:
        await self.websocket.send_json(ws_message.to_dict())

    async def send_system_message(self, message: str) -> None:
        await self.send_json(
            WsMessage(
                message_type=WsMessageType.system,
                data=message,
            ),
        )

    async def send_game_message(self, message: str) -> None:
        await self.send_json(
            WsMessage(
                message_type=WsMessageType.game,
                data=message,
            ),
        )
    send = send_game_message

    async def send_board(self, board_state: str) -> None:
        return await self.send(board_state)

    async def read(self) -> str:
        return await self.websocket.receive_text()


@get('/echo/{user_id}')
async def echo(user_id: int):
    return f'ok {user_id}'


@get('/game/create')
async def game_create():
    game_id = secrets.token_urlsafe(8)
    return game_id


@ws('/game/{player_id}/{game_id}')
async def game(websocket: WebSocket, player_id: int, game_id: str) -> None:
    await websocket.accept()
    websocket_handler = WebSocketHandler(websocket)
    player = Player(player_id, PlayerType.top, websocket_handler)
    room = WaitingRoom.get(game_id)
    room.join(player)
    try:
        await websocket_handler.send_system_message('waiting for second player')
        game = await room.game
        await game.end
    except WebSocketDisconnectError:
        ...
