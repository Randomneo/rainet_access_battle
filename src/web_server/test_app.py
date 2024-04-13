import asyncio
from blacksheep import WebSocket
from blacksheep.testing import TestClient
from blacksheep.testing.websocket import TestWebSocket

from web_server.app import application


async def get_system_message(ws: TestWebSocket) -> str:
    async with asyncio.timeout(1):
        message = await ws.receive_json()
    assert message['message_type'] == 'system'
    return message['data']


async def get_game_message(ws: TestWebSocket) -> str:
    async with asyncio.timeout(1):
        message = await ws.receive_json()
    assert message['message_type'] == 'game'
    return message['data']


async def test_game_basic_flow():
    '''
    everything is starting and communication works as expected
    '''
    await application.start()
    client = TestClient(application)

    async with (
        client.websocket_connect('/game/1/aoe') as ws1,
        client.websocket_connect('/game/2/aoe') as ws2,
    ):
        # connect and board setup
        assert await get_system_message(ws1) == 'waiting for second player'
        assert await get_system_message(ws2) == 'waiting for second player'
        assert await get_game_message(ws1) == 'awaiting_board_setup'
        assert await get_game_message(ws2) == 'awaiting_board_setup'
        await ws1.send_text('virus;'*4 + 'link;'*3 + 'link')
        await ws2.send_text('virus;'*4 + 'link;'*3 + 'link')
        assert await get_game_message(ws1) == 'game_start'
        assert await get_game_message(ws2) == 'game_start'
        # game start
        await get_game_message(ws1) # read default board state
        await get_game_message(ws2) # read default board state
        assert await get_game_message(ws1) == 'awaiting_pos_from'
        await ws1.send_text('0 0')
        assert await get_game_message(ws1) == 'awaiting_pos_to'
        await ws1.send_text('0 1')

        field = await get_game_message(ws2)
        assert 'enemy,0,6' in field.split(';')
        assert await get_game_message(ws2) == 'awaiting_pos_from'
        await ws2.send_text('1 7')
        assert await get_game_message(ws2) == 'awaiting_pos_to'
        await ws2.send_text('1 6')
        assert await get_game_message(ws2) == 'invalid pos_from'
        assert await get_game_message(ws2) == 'awaiting_pos_from'
        await ws2.send_text('1 0')
        assert await get_game_message(ws2) == 'awaiting_pos_to'
        await ws2.send_text('1 1')

        field = await get_game_message(ws1)
        assert 'enemy,1,6' in field.split(';')
