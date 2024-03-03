import asyncio

from core.game import Game
from core.io_handler import CliHandler
from core.player import Player, PlayerType


async def cli_game() -> None:
    game = Game(
        player1=Player(1, PlayerType.top, CliHandler()),
        player2=Player(2, PlayerType.bottom, CliHandler()),
    )
    await game.main_loop()


async def web_server() -> None:
    ...


if __name__ == '__main__':
    asyncio.run(cli_game())
